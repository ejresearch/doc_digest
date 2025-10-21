import json
import pathlib
from typing import Dict, List, Any, Optional
from jsonschema import validate, Draft202012Validator, ValidationError as JsonSchemaValidationError
from .logging_config import get_logger

logger = get_logger(__name__)

# Custom exception
class ValidationError(Exception):
    """Custom exception for validation failures."""
    pass

# Load schema at module level
SCHEMA_PATH = pathlib.Path(__file__).parents[1] / "schemas" / "chapter-analysis.schema.json"

try:
    MASTER_SCHEMA = json.loads(SCHEMA_PATH.read_text())
    logger.info(f"Loaded JSON Schema from: {SCHEMA_PATH}")
except FileNotFoundError:
    logger.error(f"Schema file not found at: {SCHEMA_PATH}")
    raise ValidationError(f"Schema file not found: {SCHEMA_PATH}")
except json.JSONDecodeError as e:
    logger.error(f"Invalid JSON in schema file: {e}")
    raise ValidationError(f"Invalid JSON in schema file: {str(e)}")

def format_validation_error(error: JsonSchemaValidationError) -> str:
    """
    Format a JSON Schema validation error into a human-readable message.

    Args:
        error: The validation error from jsonschema

    Returns:
        Formatted error message
    """
    path = " -> ".join(str(p) for p in error.path) if error.path else "root"
    return f"Validation error at '{path}': {error.message}"

def validate_section(data: Dict[str, Any], pointer: str) -> None:
    """
    Validate that a specific section exists in the data.

    Args:
        data: The data dictionary to validate
        pointer: The section key to check for (e.g., "comprehension_pass")

    Raises:
        ValidationError: If the section is missing
    """
    logger.debug(f"Validating section presence: {pointer}")

    if not isinstance(data, dict):
        raise ValidationError(f"Data must be a dictionary, got {type(data).__name__}")

    if pointer not in data:
        logger.error(f"Section '{pointer}' missing in payload")
        raise ValidationError(f"Required section '{pointer}' is missing from the document")

    logger.debug(f"Section '{pointer}' present")

def validate_master(doc: Dict[str, Any]) -> None:
    """
    Validate the complete chapter analysis document against the master JSON Schema.

    Args:
        doc: The complete chapter analysis document

    Raises:
        ValidationError: If validation fails with details about the error
    """
    logger.info("Starting master document validation")

    if not isinstance(doc, dict):
        raise ValidationError(f"Document must be a dictionary, got {type(doc).__name__}")

    try:
        # Create validator
        validator = Draft202012Validator(MASTER_SCHEMA)

        # Validate
        validator.validate(doc)

        logger.info("Master document validation passed")

    except JsonSchemaValidationError as e:
        # Format the error for better readability
        error_msg = format_validation_error(e)
        logger.error(f"Schema validation failed: {error_msg}")

        # Collect all validation errors (not just the first one)
        all_errors = list(validator.iter_errors(doc))
        if len(all_errors) > 1:
            logger.error(f"Total validation errors: {len(all_errors)}")
            error_details = "\n".join(
                f"  - {format_validation_error(err)}"
                for err in all_errors[:5]  # Show first 5 errors
            )
            if len(all_errors) > 5:
                error_details += f"\n  ... and {len(all_errors) - 5} more errors"

            raise ValidationError(
                f"Document validation failed with {len(all_errors)} errors:\n{error_details}"
            )
        else:
            raise ValidationError(error_msg)

    except Exception as e:
        logger.exception(f"Unexpected error during validation: {e}")
        raise ValidationError(f"Validation failed unexpectedly: {str(e)}")

def validate_required_fields(doc: Dict[str, Any], required_sections: List[str]) -> None:
    """
    Validate that all required top-level sections are present.

    Args:
        doc: The document to validate
        required_sections: List of required section names

    Raises:
        ValidationError: If any required section is missing
    """
    logger.debug(f"Validating required sections: {required_sections}")

    missing_sections = [section for section in required_sections if section not in doc]

    if missing_sections:
        error_msg = f"Missing required sections: {', '.join(missing_sections)}"
        logger.error(error_msg)
        raise ValidationError(error_msg)

    logger.debug("All required sections present")
