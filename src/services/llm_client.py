from typing import Dict, Optional, Any
from ..utils.logging_config import get_logger
from .openai_client import call_openai_structured, LLMConfigurationError, LLMAPIError
from ..models import ComprehensionPass, StructuralOutline, PropositionalExtraction, AnalyticalMetadata
from .prompts import (
    get_phase_1_prompts,
    get_phase_2_prompts,
    get_phase_3_prompts,
    get_phase_4_prompts
)

logger = get_logger(__name__)

# LLM configuration
DEFAULT_TEMPERATURE = 0.2
PHASE_1_TEMPERATURE = 0.15  # More deterministic for comprehension
PHASE_2_TEMPERATURE = 0.2   # Structured outline
PHASE_3_TEMPERATURE = 0.2   # Propositional extraction
PHASE_4_TEMPERATURE = 0.25  # Slightly more creative for metadata

# Environment variable to enable/disable actual LLM calls
import os
USE_ACTUAL_LLM = os.getenv("USE_ACTUAL_LLM", "false").lower() == "true"

def extract_comprehension_pass(text: str) -> Dict[str, Any]:
    """
    Phase 1: Extract comprehension pass using WHO/WHAT/WHEN/WHY/HOW framework.

    Args:
        text: The chapter text to analyze

    Returns:
        Dictionary with 'comprehension_pass' key containing the analysis

    Raises:
        LLMConfigurationError: If OpenAI API is not configured
        LLMAPIError: If API call fails
    """
    logger.info(f"Phase 1: Extracting comprehension pass (text length: {len(text)} chars)")

    if not USE_ACTUAL_LLM:
        logger.warning("USE_ACTUAL_LLM=false - returning stub data")
        return _stub_comprehension_pass()

    # Get comprehensive prompts from prompts module
    prompts = get_phase_1_prompts(text)

    try:
        response = call_openai_structured(
            system_prompt=prompts["system_prompt"],
            user_prompt=prompts["user_prompt"],
            temperature=PHASE_1_TEMPERATURE,
            json_schema=ComprehensionPass.model_json_schema()
        )
        logger.info("Phase 1 completed successfully")
        return {"comprehension_pass": response}

    except (LLMConfigurationError, LLMAPIError) as e:
        logger.error(f"Phase 1 failed: {e}")
        raise


def _stub_comprehension_pass() -> Dict[str, Any]:
    """Return stub data for testing without LLM."""
    return {
        "comprehension_pass": {
            "who": [],
            "what": [],
            "when": {
                "historical_or_cultural_context": "",
                "chronological_sequence_within_course": "",
                "moment_of_presentation_to_reader": ""
            },
            "why": {
                "intellectual_value": "",
                "knowledge_based_value": "",
                "moral_or_philosophical_significance": ""
            },
            "how": {
                "presentation_style": "",
                "rhetorical_approach": "",
                "recommended_student_strategy": ""
            }
        }
    }

def build_structural_outline(text: str, comp: Dict[str, Any]) -> Dict[str, Any]:
    """
    Phase 2: Build hierarchical structural outline of the chapter.

    Args:
        text: The chapter text to analyze
        comp: Output from Phase 1 (comprehension pass)

    Returns:
        Dictionary with 'structural_outline' key containing the outline

    Raises:
        LLMConfigurationError: If OpenAI API is not configured
        LLMAPIError: If API call fails
    """
    logger.info(f"Phase 2: Building structural outline")

    if not USE_ACTUAL_LLM:
        logger.warning("USE_ACTUAL_LLM=false - returning stub data")
        return _stub_structural_outline()

    # Get comprehensive prompts from prompts module
    prompts = get_phase_2_prompts(text, comp)

    try:
        response = call_openai_structured(
            system_prompt=prompts["system_prompt"],
            user_prompt=prompts["user_prompt"],
            temperature=PHASE_2_TEMPERATURE,
            json_schema=StructuralOutline.model_json_schema()
        )
        logger.info("Phase 2 completed successfully")
        return {"structural_outline": response}

    except (LLMConfigurationError, LLMAPIError) as e:
        logger.error(f"Phase 2 failed: {e}")
        raise


def _stub_structural_outline() -> Dict[str, Any]:
    """Return stub data for testing without LLM."""
    return {
        "structural_outline": {
            "chapter_title": "",
            "guiding_context_questions": [],
            "outline": []
        }
    }

def extract_propositions(text: str, comp: Dict[str, Any], outline: Dict[str, Any]) -> Dict[str, Any]:
    """
    Phase 3: Extract truth propositions from the chapter.

    Args:
        text: The chapter text to analyze
        comp: Output from Phase 1 (comprehension pass)
        outline: Output from Phase 2 (structural outline)

    Returns:
        Dictionary with 'propositional_extraction' key containing propositions

    Raises:
        LLMConfigurationError: If OpenAI API is not configured
        LLMAPIError: If API call fails
    """
    logger.info(f"Phase 3: Extracting propositions")

    if not USE_ACTUAL_LLM:
        logger.warning("USE_ACTUAL_LLM=false - returning stub data")
        return _stub_propositions()

    # Get comprehensive prompts from prompts module
    prompts = get_phase_3_prompts(text, comp, outline)

    try:
        response = call_openai_structured(
            system_prompt=prompts["system_prompt"],
            user_prompt=prompts["user_prompt"],
            temperature=PHASE_3_TEMPERATURE,
            json_schema=PropositionalExtraction.model_json_schema()
        )
        logger.info("Phase 3 completed successfully")
        return {"propositional_extraction": response}

    except (LLMConfigurationError, LLMAPIError) as e:
        logger.error(f"Phase 3 failed: {e}")
        raise


def _stub_propositions() -> Dict[str, Any]:
    """Return stub data for testing without LLM."""
    return {
        "propositional_extraction": {
            "definition": "Propositions are statements of truth contextualized by the way information is presented.",
            "guiding_prompts": [],
            "propositions": []
        }
    }

def derive_analytical_metadata(
    comp: Dict[str, Any],
    outline: Dict[str, Any],
    props: Dict[str, Any],
    hints: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Phase 4: Derive analytical metadata about curriculum context.

    Args:
        comp: Output from Phase 1 (comprehension pass)
        outline: Output from Phase 2 (structural outline)
        props: Output from Phase 3 (propositional extraction)
        hints: Optional hints for metadata derivation

    Returns:
        Dictionary with 'analytical_metadata' key containing metadata

    Raises:
        LLMConfigurationError: If OpenAI API is not configured
        LLMAPIError: If API call fails
    """
    logger.info(f"Phase 4: Deriving analytical metadata")

    if not USE_ACTUAL_LLM:
        logger.warning("USE_ACTUAL_LLM=false - returning stub data")
        return _stub_analytical_metadata()

    # Get comprehensive prompts from prompts module
    prompts = get_phase_4_prompts(comp, outline, props)

    try:
        response = call_openai_structured(
            system_prompt=prompts["system_prompt"],
            user_prompt=prompts["user_prompt"],
            temperature=PHASE_4_TEMPERATURE,
            json_schema=AnalyticalMetadata.model_json_schema()
        )
        logger.info("Phase 4 completed successfully")
        return {"analytical_metadata": response}

    except (LLMConfigurationError, LLMAPIError) as e:
        logger.error(f"Phase 4 failed: {e}")
        raise


def _stub_analytical_metadata() -> Dict[str, Any]:
    """Return stub data for testing without LLM."""
    return {
        "analytical_metadata": {
            "subject_domain": None,
            "curriculum_unit": None,
            "disciplinary_lens": None,
            "related_chapters": [],
            "grade_level_or_audience": None,
            "spiral_position": None
        }
    }
