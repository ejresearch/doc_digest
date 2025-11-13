"""
GRAFF LLM Client - 2-Phase Chapter Analysis Pipeline

This module orchestrates the GRAFF pipeline:
- Phase 1: Chapter Comprehension (structure, entities, keywords, summary)
- Phase 2: Proposition Extraction + Key Takeaway Synthesis
"""

from typing import Dict, Optional, Any
import json
from pathlib import Path
from ..utils.logging_config import get_logger
from .openai_client import call_openai_structured, LLMConfigurationError, LLMAPIError
from ..models import (
    ChapterAnalysis,
    Phase1Comprehension,
    Phase2Output,
    Proposition,
    KeyTakeaway
)

logger = get_logger(__name__)

# LLM configuration
PHASE_1_TEMPERATURE = 0.15  # Deterministic for structural analysis
PHASE_2_TEMPERATURE = 0.2   # Slightly more flexible for extraction

# Prompt file paths
PROMPT_DIR = Path(__file__).parent.parent.parent / "prompts"
PHASE_1_PROMPT_PATH = PROMPT_DIR / "phase1_system.txt"
PHASE_2_PROMPT_PATH = PROMPT_DIR / "phase2_system.txt"

# Environment variable to enable/disable actual LLM calls
import os
USE_ACTUAL_LLM = os.getenv("USE_ACTUAL_LLM", "true").lower() == "true"

def _load_prompt(prompt_path: Path) -> str:
    """Load system prompt from file."""
    if not prompt_path.exists():
        raise FileNotFoundError(f"Prompt file not found: {prompt_path}")

    with open(prompt_path, 'r', encoding='utf-8') as f:
        return f.read()


def run_phase_1(text: str, book_id: str, chapter_id: str, chapter_title: str) -> Phase1Comprehension:
    """
    GRAFF Phase 1: Chapter Comprehension and Structural Mapping.

    Extracts:
    - One-paragraph chapter summary
    - Hierarchical section structure
    - Key entities (people, organizations, concepts)
    - Domain-specific keywords

    Args:
        text: The chapter text to analyze
        book_id: Identifier for the book (e.g., "film_industry_vol1")
        chapter_id: Unique chapter identifier (e.g., "ch01")
        chapter_title: Chapter title for context

    Returns:
        Phase1Comprehension: Validated Pydantic model with structural analysis

    Raises:
        LLMConfigurationError: If OpenAI API is not configured
        LLMAPIError: If API call fails
    """
    logger.info(f"Phase 1 starting: {chapter_id} - {chapter_title} (text length: {len(text)} chars)")

    try:
        # Load system prompt from file
        system_prompt = _load_prompt(PHASE_1_PROMPT_PATH)

        # Construct user prompt with chapter text
        user_prompt = f"""Chapter Title: {chapter_title}
Book ID: {book_id}
Chapter ID: {chapter_id}

Chapter Text:
{text}

Please analyze this chapter and respond with the Phase 1 JSON output."""

        # Call LLM with structured output
        response_dict = call_openai_structured(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=PHASE_1_TEMPERATURE,
            json_schema=Phase1Comprehension.model_json_schema()
        )

        # Validate with Pydantic
        phase1 = Phase1Comprehension.model_validate(response_dict)

        logger.info(f"Phase 1 completed: {len(phase1.sections)} sections, {len(phase1.key_entities)} entities, {len(phase1.keywords)} keywords")
        return phase1

    except Exception as e:
        logger.error(f"Phase 1 failed for {chapter_id}: {e}")
        raise


def run_phase_2(text: str, chapter_id: str, phase1: Phase1Comprehension) -> Phase2Output:
    """
    GRAFF Phase 2: Comprehensive Proposition Extraction + Key Takeaway Synthesis.

    Extracts:
    - ALL atomic facts (propositions) from the chapter (comprehensive, no limits)
    - Each proposition tagged with Bloom level (remember, understand, apply, analyze)
    - Key takeaways synthesizing groups of propositions (analyze, evaluate)

    Args:
        text: The chapter text to analyze
        chapter_id: Chapter identifier for proposition IDs
        phase1: Phase 1 output (used for section unit_ids)

    Returns:
        Phase2Output: Validated Pydantic model with propositions and takeaways

    Raises:
        LLMConfigurationError: If OpenAI API is not configured
        LLMAPIError: If API call fails
    """
    logger.info(f"Phase 2 starting: {chapter_id} (will extract comprehensive propositions)")

    try:
        # Load system prompt from file
        system_prompt = _load_prompt(PHASE_2_PROMPT_PATH)

        # Construct user prompt with chapter text and Phase 1 context
        phase1_json = phase1.model_dump_json(indent=2)

        user_prompt = f"""Chapter ID: {chapter_id}

Phase 1 Output (for section unit_ids reference):
{phase1_json}

Chapter Text:
{text}

Please perform comprehensive Phase 2 extraction:
1. Extract ALL atomic facts as propositions (no artificial limits)
2. Tag each with appropriate Bloom level (remember/understand/apply/analyze)
3. Synthesize key takeaways linking related propositions

Respond with the Phase 2 JSON output."""

        # Call LLM with structured output (higher max_tokens for comprehensive extraction)
        response_dict = call_openai_structured(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=PHASE_2_TEMPERATURE,
            json_schema=Phase2Output.model_json_schema(),
            max_tokens=16000  # Allow for comprehensive extraction (100-500+ propositions)
        )

        # Validate with Pydantic
        phase2 = Phase2Output.model_validate(response_dict)

        # Log extraction statistics
        bloom_dist = {}
        for prop in phase2.propositions:
            bloom_dist[prop.bloom_level] = bloom_dist.get(prop.bloom_level, 0) + 1

        logger.info(f"Phase 2 completed: {len(phase2.propositions)} propositions, {len(phase2.key_takeaways)} takeaways")
        logger.info(f"Bloom distribution: {bloom_dist}")

        return phase2

    except Exception as e:
        logger.error(f"Phase 2 failed for {chapter_id}: {e}")
        raise


def process_chapter(
    text: str,
    book_id: str,
    chapter_id: str,
    chapter_title: str
) -> ChapterAnalysis:
    """
    Run the complete GRAFF 2-phase pipeline on a chapter.

    This is the main orchestration function that:
    1. Runs Phase 1 (structural comprehension)
    2. Runs Phase 2 (proposition extraction + synthesis)
    3. Assembles the complete ChapterAnalysis object

    Args:
        text: The chapter text to analyze
        book_id: Book identifier (e.g., "film_industry_vol1")
        chapter_id: Chapter identifier (e.g., "ch01")
        chapter_title: Chapter title

    Returns:
        ChapterAnalysis: Complete validated analysis ready for database storage

    Raises:
        LLMConfigurationError: If OpenAI API is not configured
        LLMAPIError: If API call fails
        ValidationError: If output doesn't match schema
    """
    logger.info(f"Starting GRAFF pipeline for {chapter_id}: {chapter_title}")

    # Run Phase 1
    phase1 = run_phase_1(text, book_id, chapter_id, chapter_title)

    # Run Phase 2
    phase2 = run_phase_2(text, chapter_id, phase1)

    # Assemble complete analysis
    chapter = ChapterAnalysis(
        schema_version="1.0",
        book_id=book_id,
        chapter_id=chapter_id,
        chapter_title=chapter_title,
        phase1=phase1,
        phase2=phase2
    )

    # Log final statistics
    logger.info(f"GRAFF pipeline completed for {chapter_id}")
    logger.info(f"  Propositions: {chapter.get_proposition_count()}")
    logger.info(f"  Bloom distribution: {chapter.get_bloom_distribution()}")
    logger.info(f"  Key takeaways: {len(chapter.phase2.key_takeaways)}")

    return chapter
