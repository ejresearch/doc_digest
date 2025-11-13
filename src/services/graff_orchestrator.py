"""
GRAFF Orchestrator - 2-Phase Chapter Analysis Pipeline

Manages the complete GRAFF workflow:
1. Run Phase 1 + Phase 2 via LLM
2. Validate with Pydantic
3. Persist to database
4. Return results
"""

from typing import Dict, Any, Optional, Callable
from ..utils.logging_config import get_logger
from .llm_client import process_chapter, run_phase_1, run_phase_2
from ..models import ChapterAnalysis
from ..db import save_chapter_analysis, init_database
import uuid
from datetime import datetime

logger = get_logger(__name__)

# Custom exceptions
class DigestError(Exception):
    """Base exception for digest pipeline errors."""
    pass

class PhaseError(DigestError):
    """Exception raised when a phase fails."""
    def __init__(self, phase: str, message: str, original_error: Exception = None):
        self.phase = phase
        self.original_error = original_error
        super().__init__(f"Phase {phase} failed: {message}")

class ValidationError(DigestError):
    """Exception raised when validation fails."""
    pass

class StorageError(DigestError):
    """Exception raised when storage fails."""
    pass


def digest_chapter_graff(
    text: str,
    book_id: str = "unknown_book",
    chapter_title: str = "Untitled Chapter",
    chapter_id: Optional[str] = None,
    progress_callback: Optional[Callable[[str, str], None]] = None
) -> ChapterAnalysis:
    """
    Process a chapter through the GRAFF 2-phase analysis pipeline.

    Workflow:
    1. Phase 1: Extract structure, entities, keywords, summary
    2. Phase 2: Extract comprehensive propositions + key takeaways
    3. Validate with Pydantic models
    4. Save to database
    5. Return complete ChapterAnalysis

    Args:
        text: The chapter text to analyze
        book_id: Book identifier (default: "unknown_book")
        chapter_title: Chapter title (default: "Untitled Chapter")
        chapter_id: Chapter ID (auto-generated if not provided)
        progress_callback: Optional callback function(phase, message) for progress updates

    Returns:
        ChapterAnalysis: Complete validated analysis

    Raises:
        PhaseError: If Phase 1 or Phase 2 fails
        ValidationError: If Pydantic validation fails
        StorageError: If database persistence fails
    """
    logger.info(f"Starting GRAFF pipeline for: {chapter_title}")

    # Auto-generate chapter_id if not provided
    if not chapter_id:
        chapter_id = f"ch_{uuid.uuid4().hex[:8]}"
        logger.info(f"Auto-generated chapter_id: {chapter_id}")

    def notify(phase: str, message: str):
        """Send progress update via callback."""
        if progress_callback:
            progress_callback(phase, message)
        logger.info(f"{phase}: {message}")

    try:
        # Ensure database is initialized
        try:
            init_database()
        except Exception as e:
            logger.warning(f"Database already initialized or init failed: {e}")

        # Phase 1: Chapter Comprehension
        notify("phase-1", "Analyzing chapter structure and content...")
        try:
            phase1 = run_phase_1(text, book_id, chapter_id, chapter_title)
            logger.info(f"Phase 1 complete: {len(phase1.sections)} sections, {len(phase1.key_entities)} entities")
            notify("phase-1", f"Phase 1 complete ✓ ({len(phase1.sections)} sections)")
        except Exception as e:
            logger.error(f"Phase 1 failed: {e}", exc_info=True)
            raise PhaseError("1", f"Chapter comprehension failed: {str(e)}", e)

        # Phase 2: Proposition Extraction + Synthesis
        notify("phase-2", "Extracting atomic facts and synthesizing takeaways...")
        try:
            phase2 = run_phase_2(text, chapter_id, phase1)

            # FIX: Correct chapter_id in all propositions and takeaways
            # (LLM sometimes uses example chapter_id like "ch01" instead of actual chapter_id)
            for prop in phase2.propositions:
                if prop.chapter_id != chapter_id:
                    logger.warning(f"Correcting proposition {prop.proposition_id} chapter_id from '{prop.chapter_id}' to '{chapter_id}'")
                    prop.chapter_id = chapter_id

            for takeaway in phase2.key_takeaways:
                if takeaway.chapter_id != chapter_id:
                    logger.warning(f"Correcting takeaway {takeaway.takeaway_id} chapter_id from '{takeaway.chapter_id}' to '{chapter_id}'")
                    takeaway.chapter_id = chapter_id

            # Calculate Bloom distribution for progress message
            bloom_dist = {}
            for prop in phase2.propositions:
                bloom_dist[prop.bloom_level] = bloom_dist.get(prop.bloom_level, 0) + 1

            logger.info(f"Phase 2 complete: {len(phase2.propositions)} propositions, {len(phase2.key_takeaways)} takeaways")
            logger.info(f"Bloom distribution: {bloom_dist}")

            notify("phase-2", f"Phase 2 complete ✓ ({len(phase2.propositions)} propositions, {len(phase2.key_takeaways)} takeaways)")
        except Exception as e:
            logger.error(f"Phase 2 failed: {e}", exc_info=True)
            raise PhaseError("2", f"Proposition extraction failed: {str(e)}", e)

        # Assemble complete analysis
        notify("validation", "Validating complete analysis...")
        try:
            chapter = ChapterAnalysis(
                schema_version="1.0",
                book_id=book_id,
                chapter_id=chapter_id,
                chapter_title=chapter_title,
                phase1=phase1,
                phase2=phase2
            )
            logger.info("Analysis validated successfully")
            notify("validation", "Validation complete ✓")
        except Exception as e:
            logger.error(f"Validation failed: {e}", exc_info=True)
            raise ValidationError(f"Failed to validate analysis: {str(e)}")

        # Save to database
        notify("storage", "Saving to database...")
        try:
            success = save_chapter_analysis(chapter)
            if not success:
                raise StorageError("Database save returned False")

            logger.info(f"Chapter {chapter_id} saved to database successfully")
            notify("storage", "Storage complete ✓")
        except Exception as e:
            logger.error(f"Storage failed: {e}", exc_info=True)
            raise StorageError(f"Failed to save to database: {str(e)}")

        # Success!
        notify("completed", f"Analysis complete! ({chapter.get_proposition_count()} propositions extracted)")
        logger.info(f"GRAFF pipeline completed successfully for {chapter_id}")

        return chapter

    except PhaseError:
        # Re-raise phase errors as-is
        raise
    except ValidationError:
        # Re-raise validation errors as-is
        raise
    except StorageError:
        # Re-raise storage errors as-is
        raise
    except Exception as e:
        # Catch any unexpected errors
        logger.exception(f"Unexpected error in GRAFF pipeline: {e}")
        raise DigestError(f"Unexpected error: {str(e)}")


def quick_digest(
    text: str,
    chapter_title: str = "Untitled Chapter",
    book_id: str = "test_book"
) -> ChapterAnalysis:
    """
    Quick wrapper for digest_chapter_graff without progress callbacks.

    Useful for CLI tools and testing.

    Args:
        text: Chapter text
        chapter_title: Chapter title
        book_id: Book ID

    Returns:
        ChapterAnalysis: Complete analysis
    """
    return digest_chapter_graff(
        text=text,
        book_id=book_id,
        chapter_title=chapter_title,
        progress_callback=None
    )
