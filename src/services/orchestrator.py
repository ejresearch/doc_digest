from typing import Dict, Any, Optional, Callable
from ..utils.validation import validate_master, ValidationError
from ..utils.logging_config import get_logger
from .llm_client import (
    extract_comprehension_pass,
    build_structural_outline,
    extract_propositions,
    derive_analytical_metadata,
    extract_pedagogical_mapping
)
from .storage import persist_document, StorageError
from ..models import (
    ComprehensionPass,
    StructuralOutline,
    PropositionalExtraction,
    AnalyticalMetadata,
    PedagogicalMapping,
    ChapterAnalysis
)

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

def digest_chapter(
    text: str,
    system_metadata: Optional[Dict[str, Any]] = None,
    progress_callback: Optional[Callable[[str, str], None]] = None
) -> Dict[str, str]:
    """
    Process a chapter through the 5-phase analysis pipeline.

    Args:
        text: The chapter text to analyze
        system_metadata: Optional metadata about the chapter
        progress_callback: Optional callback function(phase, message) for progress updates

    Returns:
        Dictionary with chapter_id and status

    Raises:
        DigestError: If any phase fails
        ValidationError: If validation fails at any stage
        StorageError: If persistence fails
    """
    logger.info("Starting digest pipeline")

    def notify(phase: str, message: str):
        if progress_callback:
            progress_callback(phase, message)

    try:
        # Phase 1: Comprehension Pass
        logger.info("Running Phase 1: Comprehension Pass")
        notify("phase-1", "Analyzing chapter comprehension...")
        try:
            comp = extract_comprehension_pass(text)
            # Validate Phase 1 output
            ComprehensionPass(**comp["comprehension_pass"])
            logger.info("Phase 1 completed and validated")
            notify("phase-1", "Phase 1 complete ✓")
        except Exception as e:
            logger.error(f"Phase 1 failed: {e}")
            raise PhaseError("1", "Comprehension pass extraction failed", e)

        # Phase 2: Structural Outline
        logger.info("Running Phase 2: Structural Outline")
        notify("phase-2", "Building structural outline...")
        try:
            outline = build_structural_outline(text, comp)
            # Validate Phase 2 output
            StructuralOutline(**outline["structural_outline"])
            logger.info("Phase 2 completed and validated")
            notify("phase-2", "Phase 2 complete ✓")
        except Exception as e:
            logger.error(f"Phase 2 failed: {e}")
            raise PhaseError("2", "Structural outline building failed", e)

        # Phase 3: Propositional Extraction
        logger.info("Running Phase 3: Propositional Extraction")
        notify("phase-3", "Extracting propositions...")
        try:
            props = extract_propositions(text, comp, outline)
            # Validate Phase 3 output
            PropositionalExtraction(**props["propositional_extraction"])
            logger.info("Phase 3 completed and validated")
            notify("phase-3", "Phase 3 complete ✓")
        except Exception as e:
            logger.error(f"Phase 3 failed: {e}")
            raise PhaseError("3", "Propositional extraction failed", e)

        # Phase 4: Analytical Metadata
        logger.info("Running Phase 4: Analytical Metadata")
        notify("phase-4", "Deriving analytical metadata...")
        try:
            analytical = derive_analytical_metadata(comp, outline, props)
            # Validate Phase 4 output
            if analytical.get("analytical_metadata"):
                AnalyticalMetadata(**analytical["analytical_metadata"])
            logger.info("Phase 4 completed and validated")
            notify("phase-4", "Phase 4 complete ✓")
        except Exception as e:
            logger.error(f"Phase 4 failed: {e}")
            raise PhaseError("4", "Analytical metadata derivation failed", e)

        # Phase 5: Pedagogical Mapping
        logger.info("Running Phase 5: Pedagogical Mapping")
        notify("phase-5", "Mapping pedagogical elements...")
        try:
            pedagogical = extract_pedagogical_mapping(text)
            # Validate Phase 5 output
            if pedagogical.get("pedagogical_mapping"):
                PedagogicalMapping(**pedagogical["pedagogical_mapping"])
            logger.info("Phase 5 completed and validated")
            notify("phase-5", "Phase 5 complete ✓")
        except Exception as e:
            logger.error(f"Phase 5 failed: {e}")
            raise PhaseError("5", "Pedagogical mapping extraction failed", e)

        # Assemble complete document
        logger.info("Assembling final document")
        notify("validation", "Validating and saving...")
        doc = {
            "system_metadata": system_metadata,
            **comp,
            **outline,
            **props,
            **analytical,
            **pedagogical
        }

        # Master validation using JSON Schema
        logger.info("Performing master document validation")
        try:
            validate_master(doc)
            logger.info("Master validation passed")
        except Exception as e:
            logger.error(f"Master validation failed: {e}")
            raise ValidationError(f"Final document validation failed: {str(e)}")

        # Validate with full Pydantic model as final check
        try:
            ChapterAnalysis(**doc)
            logger.info("Pydantic model validation passed")
        except Exception as e:
            logger.error(f"Pydantic validation failed: {e}")
            raise ValidationError(f"Pydantic validation failed: {str(e)}")

        # Persist document
        logger.info("Persisting document to storage")
        try:
            result = persist_document(doc)
            logger.info(f"Document persisted successfully: {result.get('chapter_id')}")
            return result
        except Exception as e:
            logger.error(f"Storage failed: {e}")
            raise StorageError(f"Failed to persist document: {str(e)}")

    except (DigestError, ValidationError, StorageError):
        # Re-raise our custom exceptions
        raise
    except Exception as e:
        # Catch any unexpected errors
        logger.exception(f"Unexpected error in digest pipeline: {e}")
        raise DigestError(f"Unexpected pipeline error: {str(e)}")
