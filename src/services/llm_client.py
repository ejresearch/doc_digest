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


def _extract_section_text(full_text: str, section_title: str, next_section_title: Optional[str] = None) -> str:
    """
    Extract approximate text for a section by finding title boundaries.

    Args:
        full_text: The complete chapter text
        section_title: Title of the section to extract
        next_section_title: Title of the next section (to mark end boundary)

    Returns:
        Extracted section text (approximate)
    """
    # Find section start
    start_idx = full_text.find(section_title)
    if start_idx == -1:
        # Try case-insensitive
        start_idx = full_text.lower().find(section_title.lower())

    if start_idx == -1:
        logger.warning(f"Could not find section title '{section_title}' in text, using full text")
        return full_text

    # Find section end (next section title or end of text)
    if next_section_title:
        end_idx = full_text.find(next_section_title, start_idx + len(section_title))
        if end_idx == -1:
            end_idx = full_text.lower().find(next_section_title.lower(), start_idx + len(section_title))
        if end_idx == -1:
            end_idx = len(full_text)
    else:
        end_idx = len(full_text)

    return full_text[start_idx:end_idx]


def run_phase_2(text: str, chapter_id: str, phase1: Phase1Comprehension) -> Phase2Output:
    """
    GRAFF Phase 2: Comprehensive Proposition Extraction + Key Takeaway Synthesis.

    Uses SECTION-BY-SECTION extraction strategy:
    - Processes each section individually with explicit targets
    - Prevents LLM from being selective by forcing granular focus
    - Aggregates propositions, then synthesizes takeaways

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
    logger.info(f"Phase 2 starting: {chapter_id} (section-by-section extraction)")

    try:
        # Load system prompt from file
        system_prompt = _load_prompt(PHASE_2_PROMPT_PATH)

        all_propositions = []
        total_word_count = len(text.split())

        # STEP 1: Extract propositions section-by-section
        logger.info(f"Extracting propositions from {len(phase1.sections)} sections")

        for i, section in enumerate(phase1.sections):
            # Get next section title for text boundary
            next_section_title = phase1.sections[i+1].title if i+1 < len(phase1.sections) else None

            # Extract section text (approximate)
            section_text = _extract_section_text(text, section.title, next_section_title)
            section_word_count = len(section_text.split())

            # Calculate section-specific targets
            min_props = max(3, int(section_word_count / 150))  # At least 3 propositions per section
            max_props = max(5, int(section_word_count / 100))

            logger.info(f"Processing section {section.unit_id} '{section.title}' ({section_word_count} words, target: {min_props}-{max_props} props)")

            # Section-specific prompt
            user_prompt = f"""Chapter ID: {chapter_id}
Section: {section.unit_id} - {section.title}

**TASK: Extract ALL facts from THIS SECTION ONLY**

Section Text ({section_word_count:,} words):
{section_text}

**QUANTITATIVE REQUIREMENT FOR THIS SECTION:**
This section has {section_word_count:,} words.
You MUST extract at least {min_props}-{max_props} propositions from this section.
Extract EVERY fact - definitions, names, dates, descriptions, examples, comparisons, etc.

Respond with a JSON object containing ONLY a "propositions" array.
Each proposition must have:
- proposition_id: "{chapter_id}_{section.unit_id}_pXXX" (e.g., "1_1.2_p001")
- chapter_id: "{chapter_id}"
- unit_id: "{section.unit_id}"
- All other required fields

Do NOT include key_takeaways (those will be generated separately)."""

            # Simplified schema for section extraction (propositions only)
            section_schema = {
                "type": "object",
                "properties": {
                    "propositions": {
                        "type": "array",
                        "items": Proposition.model_json_schema()
                    }
                },
                "required": ["propositions"]
            }

            # Extract propositions for this section
            response_dict = call_openai_structured(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=PHASE_2_TEMPERATURE,
                json_schema=section_schema,
                max_tokens=8000
            )

            # Validate and collect propositions
            section_props = [Proposition.model_validate(p) for p in response_dict.get("propositions", [])]
            all_propositions.extend(section_props)

            logger.info(f"Section {section.unit_id}: extracted {len(section_props)} propositions")

        logger.info(f"Total propositions extracted: {len(all_propositions)}")

        # STEP 2: Synthesize takeaways across all propositions
        logger.info("Synthesizing key takeaways...")

        # Create summary of all propositions for takeaway synthesis
        props_summary = "\n".join([
            f"- [{p.proposition_id}] {p.proposition_text} (Bloom: {p.bloom_level}, Unit: {p.unit_id})"
            for p in all_propositions
        ])

        takeaway_prompt = f"""Chapter ID: {chapter_id}

**TASK: Synthesize key takeaways from the propositions below**

Phase 1 Sections:
{phase1.model_dump_json(indent=2)}

All Extracted Propositions ({len(all_propositions)} total):
{props_summary}

**REQUIREMENTS:**
- Generate 8-20 key takeaways that synthesize groups of related propositions
- Use multi-pass approach: section-level → cross-section patterns → chapter-level insights
- Each takeaway must link to 2+ proposition IDs
- Use Bloom levels: analyze or evaluate

Respond with a JSON object containing ONLY a "key_takeaways" array.
Each takeaway must have:
- takeaway_id: "{chapter_id}_tXXX"
- chapter_id: "{chapter_id}"
- unit_id: primary section (or null for chapter-level)
- text: one-sentence synthesis
- proposition_ids: array of related proposition IDs
- dominant_bloom_level: "analyze" or "evaluate"
- tags: thematic tags"""

        takeaway_schema = {
            "type": "object",
            "properties": {
                "key_takeaways": {
                    "type": "array",
                    "items": KeyTakeaway.model_json_schema()
                }
            },
            "required": ["key_takeaways"]
        }

        # Extract takeaways
        takeaway_response = call_openai_structured(
            system_prompt=system_prompt,
            user_prompt=takeaway_prompt,
            temperature=PHASE_2_TEMPERATURE,
            json_schema=takeaway_schema,
            max_tokens=8000
        )

        # Validate takeaways
        takeaways = [KeyTakeaway.model_validate(t) for t in takeaway_response.get("key_takeaways", [])]

        logger.info(f"Synthesized {len(takeaways)} key takeaways")

        # Assemble Phase 2 output
        phase2 = Phase2Output(
            propositions=all_propositions,
            key_takeaways=takeaways
        )

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
