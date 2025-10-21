"""Tests for validation module."""
import pytest
from src.utils.validation import (
    validate_master,
    validate_section,
    validate_required_fields,
    ValidationError
)


def test_validate_section_exists(valid_chapter_analysis):
    """Test that validate_section passes when section exists."""
    validate_section(valid_chapter_analysis, "comprehension_pass")
    validate_section(valid_chapter_analysis, "structural_outline")


def test_validate_section_missing():
    """Test that validate_section raises when section is missing."""
    doc = {"foo": "bar"}
    with pytest.raises(ValidationError, match="Required section 'comprehension_pass' is missing"):
        validate_section(doc, "comprehension_pass")


def test_validate_section_invalid_data():
    """Test that validate_section raises when data is not a dict."""
    with pytest.raises(ValidationError, match="Data must be a dictionary"):
        validate_section("not a dict", "foo")  # type: ignore


def test_validate_required_fields_success(valid_chapter_analysis):
    """Test validate_required_fields with all fields present."""
    required = ["comprehension_pass", "structural_outline", "propositional_extraction"]
    validate_required_fields(valid_chapter_analysis, required)


def test_validate_required_fields_missing():
    """Test validate_required_fields with missing fields."""
    doc = {"comprehension_pass": {}}
    required = ["comprehension_pass", "structural_outline"]

    with pytest.raises(ValidationError, match="Missing required sections: structural_outline"):
        validate_required_fields(doc, required)


def test_validate_master_with_valid_document(valid_chapter_analysis):
    """Test that validate_master passes with a valid document."""
    # Should not raise
    validate_master(valid_chapter_analysis)


def test_validate_master_with_invalid_document():
    """Test that validate_master raises with an invalid document."""
    invalid_doc = {
        "system_metadata": {},
        # Missing required sections
    }

    with pytest.raises(ValidationError):
        validate_master(invalid_doc)


def test_validate_master_not_a_dict():
    """Test that validate_master raises when document is not a dict."""
    with pytest.raises(ValidationError, match="Document must be a dictionary"):
        validate_master("not a dict")  # type: ignore


def test_validate_master_with_partial_data(valid_comprehension_pass):
    """Test validation with partially complete data."""
    partial_doc = {
        "comprehension_pass": valid_comprehension_pass,
        "structural_outline": {
            "chapter_title": "",
            "guiding_context_questions": [],
            "outline": []
        }
        # Missing propositional_extraction and analytical_metadata
    }

    with pytest.raises(ValidationError):
        validate_master(partial_doc)
