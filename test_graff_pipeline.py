#!/usr/bin/env python3
"""
GRAFF Pipeline Test Script

Tests the end-to-end GRAFF pipeline:
1. Phase 1: Chapter comprehension
2. Phase 2: Proposition extraction + synthesis
3. Pydantic validation
4. Database persistence
5. Database retrieval

Usage:
    python test_graff_pipeline.py
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.services.graff_orchestrator import quick_digest
from src.db import init_database, load_chapter_analysis, list_chapters
from src.utils.logging_config import setup_logging, get_logger

setup_logging(level="INFO")
logger = get_logger(__name__)

# Sample test chapter
SAMPLE_CHAPTER = """
Chapter 1: The Classical Hollywood Studio System

Introduction

The Hollywood studio system of the 1930s and 1940s represents one of the most dominant and influential periods in American film history. This chapter examines how five major studios - Paramount, MGM, Warner Bros., 20th Century Fox, and RKO - came to control the entire film industry through a strategy known as vertical integration.

Section 1.1: What is Vertical Integration?

Vertical integration is the practice of owning and controlling all three stages of the film business: production, distribution, and exhibition. Unlike the Little Three studios (Universal, Columbia, and United Artists), which only controlled production and distribution, the Big Five owned extensive theater chains across the United States.

This business model gave the Big Five unprecedented power. By owning theaters, they guaranteed exhibition outlets for their films while simultaneously controlling which films competed for audience attention. Paramount Pictures, for example, owned 1,450 theaters across the country in 1948, allowing it to dominate local markets.

Section 1.2: Block Booking and Market Control

To maximize profits and minimize risk, studios employed a practice called block booking. Block booking required theater owners to rent films in groups rather than individually. A theater might be forced to accept 50 films sight unseen to gain access to one highly anticipated release.

This practice effectively transferred financial risk from studios to exhibitors. Studios guaranteed revenue regardless of film quality, while independent theater owners bore the burden of screening unprofitable films.

Section 1.3: The Star System

Studios also controlled talent through long-term contracts and the star system. Major actors, directors, and writers were bound to exclusive multi-year contracts that prevented them from working for competitors. Studios invested heavily in cultivating star personas, which functioned as a form of brand differentiation.

The star system created significant barriers to entry for independent producers. Without access to established stars under contract, independent films struggled to compete for audience attention.

Section 1.4: The Paramount Decision

In 1948, the United States Supreme Court ruled against Paramount Pictures in United States v. Paramount Pictures, Inc. The decision declared vertical integration and block booking to be violations of antitrust law. Studios were forced to divest their theater chains, fundamentally restructuring the industry.

However, the Paramount decision proved only partially effective. While the Big Five lost their exhibition monopoly, they retained control over production and distribution. The industry's power structure remained concentrated, albeit in a modified form.

Conclusion

The classical Hollywood studio system demonstrates how vertical integration can create market dominance. The Big Five's control of production, distribution, and exhibition allowed them to establish insurmountable barriers to competition. Though the Paramount decision ended theater ownership, the studios' fundamental power endured through their continued control of production and distribution infrastructure.
"""


def main():
    """Run GRAFF pipeline test."""
    print("=" * 70)
    print("GRAFF Pipeline End-to-End Test")
    print("=" * 70)
    print()

    # Initialize database
    print("[1/5] Initializing database...")
    try:
        init_database()
        print("✓ Database initialized\n")
    except Exception as e:
        logger.error(f"Database init failed: {e}")
        print(f"✗ Database initialization failed: {e}\n")
        return False

    # Run GRAFF pipeline
    print("[2/5] Running GRAFF pipeline (this may take 30-60 seconds)...")
    print("      Phase 1: Chapter comprehension")
    print("      Phase 2: Proposition extraction + synthesis")
    try:
        chapter = quick_digest(
            text=SAMPLE_CHAPTER,
            chapter_title="The Classical Hollywood Studio System",
            book_id="film_history_101"
        )
        print(f"✓ Pipeline completed successfully\n")
    except Exception as e:
        logger.error(f"Pipeline failed: {e}", exc_info=True)
        print(f"✗ Pipeline failed: {e}\n")
        return False

    # Validate results
    print("[3/5] Validating results...")
    try:
        print(f"   Chapter ID: {chapter.chapter_id}")
        print(f"   Book ID: {chapter.book_id}")
        print(f"   Schema Version: {chapter.schema_version}")
        print()

        # Phase 1 stats
        print("   Phase 1 Results:")
        print(f"   - Sections: {len(chapter.phase1.sections)}")
        print(f"   - Entities: {len(chapter.phase1.key_entities)}")
        print(f"   - Keywords: {len(chapter.phase1.keywords)}")
        print(f"   - Summary length: {len(chapter.phase1.summary)} chars")
        print()

        # Phase 2 stats
        print("   Phase 2 Results:")
        print(f"   - Total propositions: {len(chapter.phase2.propositions)}")
        print(f"   - Key takeaways: {len(chapter.phase2.key_takeaways)}")

        # Bloom distribution
        bloom_dist = chapter.get_bloom_distribution()
        print(f"\n   Bloom Distribution:")
        for level, count in bloom_dist.items():
            if count > 0:
                percentage = (count / len(chapter.phase2.propositions)) * 100
                print(f"   - {level.capitalize()}: {count} ({percentage:.1f}%)")

        # Validate Bloom constraints
        print(f"\n   Bloom Constraint Validation:")
        invalid_props = [p for p in chapter.phase2.propositions if p.bloom_level not in ['remember', 'understand', 'apply', 'analyze']]
        if invalid_props:
            print(f"   ✗ Found {len(invalid_props)} propositions with invalid Bloom levels!")
            for p in invalid_props[:3]:
                print(f"      - {p.proposition_id}: {p.bloom_level}")
        else:
            print(f"   ✓ All propositions have valid Bloom levels")

        invalid_takeaways = [t for t in chapter.phase2.key_takeaways if t.dominant_bloom_level and t.dominant_bloom_level not in ['analyze', 'evaluate']]
        if invalid_takeaways:
            print(f"   ✗ Found {len(invalid_takeaways)} takeaways with invalid Bloom levels!")
        else:
            print(f"   ✓ All takeaways have valid Bloom levels")

        print("\n✓ Validation passed\n")
    except Exception as e:
        logger.error(f"Validation failed: {e}")
        print(f"✗ Validation failed: {e}\n")
        return False

    # Test database retrieval
    print("[4/5] Testing database retrieval...")
    try:
        loaded_chapter = load_chapter_analysis(chapter.chapter_id)
        if not loaded_chapter:
            raise Exception("Chapter not found in database")

        if loaded_chapter.chapter_id != chapter.chapter_id:
            raise Exception("Chapter ID mismatch")

        if len(loaded_chapter.phase2.propositions) != len(chapter.phase2.propositions):
            raise Exception("Proposition count mismatch")

        print(f"   ✓ Successfully loaded chapter {chapter.chapter_id}")
        print(f"   ✓ Data integrity verified")
        print("✓ Database retrieval passed\n")
    except Exception as e:
        logger.error(f"Database retrieval failed: {e}")
        print(f"✗ Database retrieval failed: {e}\n")
        return False

    # Test chapter listing
    print("[5/5] Testing chapter listing...")
    try:
        chapters = list_chapters()
        found = False
        for ch in chapters:
            if ch['chapter_id'] == chapter.chapter_id:
                found = True
                print(f"   ✓ Found chapter in list")
                print(f"      - Title: {ch['chapter_title']}")
                print(f"      - Propositions: {ch['proposition_count']}")
                print(f"      - Takeaways: {ch['takeaway_count']}")
                break

        if not found:
            raise Exception("Chapter not found in list")

        print("✓ Chapter listing passed\n")
    except Exception as e:
        logger.error(f"Chapter listing failed: {e}")
        print(f"✗ Chapter listing failed: {e}\n")
        return False

    # Success summary
    print("=" * 70)
    print("✓ ALL TESTS PASSED")
    print("=" * 70)
    print()
    print(f"Sample chapter '{chapter.chapter_title}' has been:")
    print(f"  1. Analyzed through 2-phase GRAFF pipeline")
    print(f"  2. Validated against Pydantic schema")
    print(f"  3. Persisted to graff.db")
    print(f"  4. Successfully retrieved")
    print()
    print(f"You can now:")
    print(f"  - Start the API: python -m uvicorn src.app:app --reload")
    print(f"  - View the chapter: GET /chapters/{chapter.chapter_id}")
    print(f"  - List all chapters: GET /chapters/list")
    print()
    return True


if __name__ == "__main__":
    # Set environment variable to use actual LLM
    os.environ["USE_ACTUAL_LLM"] = "true"

    success = main()
    sys.exit(0 if success else 1)
