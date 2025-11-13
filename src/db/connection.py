"""
GRAFF Database Connection and Persistence Layer

Handles all database operations for storing and retrieving chapter analysis results.
"""

import sqlite3
import os
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime

from src.models import ChapterAnalysis, Phase1Comprehension, Phase2Output, Section, Entity, Proposition, KeyTakeaway

logger = logging.getLogger(__name__)

# Database file path
DB_PATH = Path(__file__).parent.parent.parent / "graff.db"
SCHEMA_PATH = Path(__file__).parent / "schema.sql"


def get_connection() -> sqlite3.Connection:
    """
    Get a connection to the GRAFF database.

    Returns:
        sqlite3.Connection: Database connection with row factory enabled
    """
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row  # Enable column access by name
    conn.execute("PRAGMA foreign_keys = ON")  # Enable foreign key constraints
    return conn


def init_database() -> None:
    """
    Initialize the database by creating all tables from schema.sql.
    Safe to call multiple times (uses IF NOT EXISTS).
    """
    if not SCHEMA_PATH.exists():
        raise FileNotFoundError(f"Schema file not found: {SCHEMA_PATH}")

    with open(SCHEMA_PATH, 'r') as f:
        schema_sql = f.read()

    conn = get_connection()
    try:
        conn.executescript(schema_sql)
        conn.commit()
        logger.info(f"Database initialized at {DB_PATH}")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise
    finally:
        conn.close()


def save_chapter_analysis(chapter: ChapterAnalysis) -> bool:
    """
    Save a complete ChapterAnalysis to the database.

    This is the main persistence function that:
    1. Inserts chapter metadata
    2. Inserts Phase 1 data (sections, entities, keywords)
    3. Inserts Phase 2 data (propositions, takeaways)

    Args:
        chapter: ChapterAnalysis object to persist

    Returns:
        bool: True if successful, False otherwise
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()

        # Validate unit_ids exist in Phase 1 sections
        valid_unit_ids = {section.unit_id for section in chapter.phase1.sections}
        logger.info(f"Valid unit_ids from Phase 1: {sorted(valid_unit_ids)}")

        # Check propositions
        for prop in chapter.phase2.propositions:
            if prop.unit_id not in valid_unit_ids:
                logger.error(f"Proposition {prop.proposition_id} references invalid unit_id: {prop.unit_id}")
                logger.error(f"Valid unit_ids: {sorted(valid_unit_ids)}")
                raise ValueError(f"Proposition references non-existent unit_id: {prop.unit_id}")

        # Check takeaways
        for takeaway in chapter.phase2.key_takeaways:
            if takeaway.unit_id and takeaway.unit_id not in valid_unit_ids:
                logger.error(f"Takeaway {takeaway.takeaway_id} references invalid unit_id: {takeaway.unit_id}")
                logger.error(f"Valid unit_ids: {sorted(valid_unit_ids)}")
                raise ValueError(f"Takeaway references non-existent unit_id: {takeaway.unit_id}")

        # Validate proposition_ids in takeaways
        valid_prop_ids = {prop.proposition_id for prop in chapter.phase2.propositions}
        for takeaway in chapter.phase2.key_takeaways:
            invalid_refs = [pid for pid in takeaway.proposition_ids if pid not in valid_prop_ids]
            if invalid_refs:
                logger.error(f"Takeaway {takeaway.takeaway_id} references invalid proposition IDs: {invalid_refs}")
                logger.error(f"Valid proposition IDs: {sorted(valid_prop_ids)}")
                raise ValueError(f"Takeaway references non-existent propositions: {invalid_refs}")

        # Check if chapter already exists
        cursor.execute("SELECT id FROM chapters WHERE chapter_id = ?", (chapter.chapter_id,))
        existing = cursor.fetchone()

        if existing:
            logger.warning(f"Chapter {chapter.chapter_id} already exists, deleting old version")
            delete_chapter(chapter.chapter_id, conn)

        # Insert chapter metadata
        cursor.execute("""
            INSERT INTO chapters (book_id, chapter_id, chapter_title, summary, schema_version)
            VALUES (?, ?, ?, ?, ?)
        """, (
            chapter.book_id,
            chapter.chapter_id,
            chapter.chapter_title,
            chapter.phase1.summary,
            chapter.schema_version
        ))

        # Insert sections
        for section in chapter.phase1.sections:
            cursor.execute("""
                INSERT INTO sections (chapter_id, unit_id, title, level, parent_unit_id, start_location, end_location)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                chapter.chapter_id,
                section.unit_id,
                section.title,
                section.level,
                section.parent_unit_id,
                section.start_location,
                section.end_location
            ))

        # Insert entities
        for entity in chapter.phase1.key_entities:
            cursor.execute("""
                INSERT INTO entities (chapter_id, name, type)
                VALUES (?, ?, ?)
            """, (chapter.chapter_id, entity.name, entity.type))

        # Insert keywords
        for keyword in chapter.phase1.keywords:
            cursor.execute("""
                INSERT INTO keywords (chapter_id, keyword)
                VALUES (?, ?)
            """, (chapter.chapter_id, keyword))

        # Insert propositions
        logger.info(f"Chapter ID being used: {chapter.chapter_id}")
        for i, prop in enumerate(chapter.phase2.propositions):
            if i == 0:
                logger.info(f"First proposition chapter_id: {prop.chapter_id}")
            if prop.chapter_id != chapter.chapter_id:
                logger.error(f"MISMATCH: Proposition {prop.proposition_id} has chapter_id={prop.chapter_id}, but chapter.chapter_id={chapter.chapter_id}")
            cursor.execute("""
                INSERT INTO propositions (id, chapter_id, unit_id, proposition_text, bloom_level, bloom_verb, evidence_location, source_type)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                prop.proposition_id,
                prop.chapter_id,
                prop.unit_id,
                prop.proposition_text,
                prop.bloom_level,
                prop.bloom_verb,
                prop.evidence_location,
                prop.source_type
            ))

            # Insert proposition tags
            for tag in prop.tags:
                cursor.execute("""
                    INSERT INTO proposition_tags (proposition_id, tag)
                    VALUES (?, ?)
                """, (prop.proposition_id, tag))

        # Insert key takeaways
        for takeaway in chapter.phase2.key_takeaways:
            cursor.execute("""
                INSERT INTO key_takeaways (id, chapter_id, unit_id, text, dominant_bloom_level)
                VALUES (?, ?, ?, ?, ?)
            """, (
                takeaway.takeaway_id,
                takeaway.chapter_id,
                takeaway.unit_id,
                takeaway.text,
                takeaway.dominant_bloom_level
            ))

            # Insert takeaway-proposition links
            for prop_id in takeaway.proposition_ids:
                cursor.execute("""
                    INSERT INTO takeaway_propositions (takeaway_id, proposition_id)
                    VALUES (?, ?)
                """, (takeaway.takeaway_id, prop_id))

            # Insert takeaway tags
            for tag in takeaway.tags:
                cursor.execute("""
                    INSERT INTO takeaway_tags (takeaway_id, tag)
                    VALUES (?, ?)
                """, (takeaway.takeaway_id, tag))

        conn.commit()
        logger.info(f"Successfully saved chapter {chapter.chapter_id} ({chapter.get_proposition_count()} propositions)")
        return True

    except Exception as e:
        conn.rollback()
        logger.error(f"Failed to save chapter {chapter.chapter_id}: {e}")
        logger.error(f"Error type: {type(e).__name__}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False
    finally:
        conn.close()


def load_chapter_analysis(chapter_id: str) -> Optional[ChapterAnalysis]:
    """
    Load a complete ChapterAnalysis from the database.

    Args:
        chapter_id: Unique chapter identifier

    Returns:
        ChapterAnalysis object if found, None otherwise
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()

        # Load chapter metadata
        cursor.execute("SELECT * FROM chapters WHERE chapter_id = ?", (chapter_id,))
        chapter_row = cursor.fetchone()

        if not chapter_row:
            logger.warning(f"Chapter {chapter_id} not found")
            return None

        # Load sections
        cursor.execute("SELECT * FROM sections WHERE chapter_id = ? ORDER BY level, unit_id", (chapter_id,))
        sections = [
            Section(
                unit_id=row['unit_id'],
                title=row['title'],
                level=row['level'],
                parent_unit_id=row['parent_unit_id'],
                start_location=row['start_location'],
                end_location=row['end_location']
            )
            for row in cursor.fetchall()
        ]

        # Load entities
        cursor.execute("SELECT * FROM entities WHERE chapter_id = ?", (chapter_id,))
        entities = [
            Entity(name=row['name'], type=row['type'])
            for row in cursor.fetchall()
        ]

        # Load keywords
        cursor.execute("SELECT keyword FROM keywords WHERE chapter_id = ?", (chapter_id,))
        keywords = [row['keyword'] for row in cursor.fetchall()]

        # Load propositions with tags
        cursor.execute("SELECT * FROM propositions WHERE chapter_id = ? ORDER BY id", (chapter_id,))
        propositions = []
        for row in cursor.fetchall():
            # Get tags for this proposition
            cursor.execute("SELECT tag FROM proposition_tags WHERE proposition_id = ?", (row['id'],))
            tags = [tag_row['tag'] for tag_row in cursor.fetchall()]

            propositions.append(Proposition(
                proposition_id=row['id'],
                chapter_id=row['chapter_id'],
                unit_id=row['unit_id'],
                proposition_text=row['proposition_text'],
                bloom_level=row['bloom_level'],
                bloom_verb=row['bloom_verb'],
                evidence_location=row['evidence_location'],
                source_type=row['source_type'],
                tags=tags
            ))

        # Load key takeaways with proposition links and tags
        cursor.execute("SELECT * FROM key_takeaways WHERE chapter_id = ? ORDER BY id", (chapter_id,))
        takeaways = []
        for row in cursor.fetchall():
            # Get linked proposition IDs
            cursor.execute("""
                SELECT proposition_id FROM takeaway_propositions WHERE takeaway_id = ?
            """, (row['id'],))
            proposition_ids = [p_row['proposition_id'] for p_row in cursor.fetchall()]

            # Get tags
            cursor.execute("SELECT tag FROM takeaway_tags WHERE takeaway_id = ?", (row['id'],))
            tags = [tag_row['tag'] for tag_row in cursor.fetchall()]

            takeaways.append(KeyTakeaway(
                takeaway_id=row['id'],
                chapter_id=row['chapter_id'],
                unit_id=row['unit_id'],
                text=row['text'],
                proposition_ids=proposition_ids,
                dominant_bloom_level=row['dominant_bloom_level'],
                tags=tags
            ))

        # Construct ChapterAnalysis object
        chapter = ChapterAnalysis(
            schema_version=chapter_row['schema_version'],
            book_id=chapter_row['book_id'],
            chapter_id=chapter_row['chapter_id'],
            chapter_title=chapter_row['chapter_title'],
            phase1=Phase1Comprehension(
                summary=chapter_row['summary'],
                sections=sections,
                key_entities=entities,
                keywords=keywords
            ),
            phase2=Phase2Output(
                propositions=propositions,
                key_takeaways=takeaways
            )
        )

        logger.info(f"Successfully loaded chapter {chapter_id}")
        return chapter

    except Exception as e:
        logger.error(f"Failed to load chapter {chapter_id}: {e}")
        return None
    finally:
        conn.close()


def list_chapters() -> List[Dict[str, Any]]:
    """
    Get a list of all chapters in the database.

    Returns:
        List of dictionaries containing chapter metadata
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                chapter_id,
                chapter_title,
                book_id,
                created_at,
                (SELECT COUNT(*) FROM propositions WHERE chapter_id = chapters.chapter_id) as proposition_count,
                (SELECT COUNT(*) FROM key_takeaways WHERE chapter_id = chapters.chapter_id) as takeaway_count
            FROM chapters
            ORDER BY created_at DESC
        """)

        chapters = []
        for row in cursor.fetchall():
            chapters.append({
                'chapter_id': row['chapter_id'],
                'chapter_title': row['chapter_title'],
                'book_id': row['book_id'],
                'created_at': row['created_at'],
                'proposition_count': row['proposition_count'],
                'takeaway_count': row['takeaway_count']
            })

        return chapters

    finally:
        conn.close()


def delete_chapter(chapter_id: str, conn: Optional[sqlite3.Connection] = None) -> bool:
    """
    Delete a chapter and all associated data from the database.

    Args:
        chapter_id: Chapter to delete
        conn: Optional existing connection (for use within transactions)

    Returns:
        bool: True if successful, False otherwise
    """
    should_close = conn is None
    if conn is None:
        conn = get_connection()

    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM chapters WHERE chapter_id = ?", (chapter_id,))

        if should_close:
            conn.commit()

        logger.info(f"Deleted chapter {chapter_id}")
        return True

    except Exception as e:
        if should_close:
            conn.rollback()
        logger.error(f"Failed to delete chapter {chapter_id}: {e}")
        return False
    finally:
        if should_close:
            conn.close()


def get_propositions_by_bloom(chapter_id: str, bloom_level: str) -> List[Proposition]:
    """
    Get all propositions for a chapter filtered by Bloom level.

    Args:
        chapter_id: Chapter identifier
        bloom_level: Bloom level filter (remember, understand, apply, analyze)

    Returns:
        List of Proposition objects
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM propositions
            WHERE chapter_id = ? AND bloom_level = ?
            ORDER BY unit_id, id
        """, (chapter_id, bloom_level))

        propositions = []
        for row in cursor.fetchall():
            # Get tags
            cursor.execute("SELECT tag FROM proposition_tags WHERE proposition_id = ?", (row['id'],))
            tags = [tag_row['tag'] for tag_row in cursor.fetchall()]

            propositions.append(Proposition(
                proposition_id=row['id'],
                chapter_id=row['chapter_id'],
                unit_id=row['unit_id'],
                proposition_text=row['proposition_text'],
                bloom_level=row['bloom_level'],
                bloom_verb=row['bloom_verb'],
                evidence_location=row['evidence_location'],
                source_type=row['source_type'],
                tags=tags
            ))

        return propositions

    finally:
        conn.close()


def get_takeaways_for_unit(chapter_id: str, unit_id: str) -> List[KeyTakeaway]:
    """
    Get all key takeaways for a specific unit/section.

    Args:
        chapter_id: Chapter identifier
        unit_id: Unit/section identifier

    Returns:
        List of KeyTakeaway objects
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM key_takeaways
            WHERE chapter_id = ? AND unit_id = ?
            ORDER BY id
        """, (chapter_id, unit_id))

        takeaways = []
        for row in cursor.fetchall():
            # Get linked propositions
            cursor.execute("""
                SELECT proposition_id FROM takeaway_propositions WHERE takeaway_id = ?
            """, (row['id'],))
            proposition_ids = [p_row['proposition_id'] for p_row in cursor.fetchall()]

            # Get tags
            cursor.execute("SELECT tag FROM takeaway_tags WHERE takeaway_id = ?", (row['id'],))
            tags = [tag_row['tag'] for tag_row in cursor.fetchall()]

            takeaways.append(KeyTakeaway(
                takeaway_id=row['id'],
                chapter_id=row['chapter_id'],
                unit_id=row['unit_id'],
                text=row['text'],
                proposition_ids=proposition_ids,
                dominant_bloom_level=row['dominant_bloom_level'],
                tags=tags
            ))

        return takeaways

    finally:
        conn.close()
