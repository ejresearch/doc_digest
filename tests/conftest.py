"""Pytest configuration and fixtures."""
import pytest
import json
from pathlib import Path
from typing import Dict, Any

# Test data directory
FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def sample_chapter_text() -> str:
    """Sample chapter text for testing."""
    return """Chapter 1: Introduction to Python Programming

Python is a high-level, interpreted programming language known for its clear syntax and readability.
Created by Guido van Rossum and first released in 1991, Python emphasizes code readability and allows
programmers to express concepts in fewer lines of code than would be possible in languages such as C++ or Java.

Key Features of Python:
1. Easy to Learn and Use: Python has a simple syntax that mimics natural language.
2. Interpreted Language: Python code is executed line by line.
3. Dynamically Typed: You don't need to declare variable types explicitly.
4. Large Standard Library: Python comes with a vast collection of modules.
5. Cross-platform: Python runs on various operating systems.

Why Learn Python?
Python is versatile and used in web development, data science, AI, automation, and scientific computing."""


@pytest.fixture
def valid_comprehension_pass() -> Dict[str, Any]:
    """Valid comprehension pass data."""
    return {
        "who": [
            {
                "entity": "Guido van Rossum",
                "role_or_function": "Creator of Python",
                "significance_in_chapter": "Historical context",
                "evidence_pointer": "line 3"
            }
        ],
        "what": [
            {
                "concept_or_topic": "Python Programming Language",
                "definition_or_description": "High-level interpreted language",
                "importance": "Foundation for the chapter",
                "evidence_pointer": "line 1-2"
            }
        ],
        "when": {
            "historical_or_cultural_context": "First released in 1991",
            "chronological_sequence_within_course": "Introduction chapter",
            "moment_of_presentation_to_reader": "Beginning of course"
        },
        "why": {
            "intellectual_value": "Understanding programming fundamentals",
            "knowledge_based_value": "Practical programming skills",
            "moral_or_philosophical_significance": "Code readability and clarity"
        },
        "how": {
            "presentation_style": "Expository with examples",
            "rhetorical_approach": "Informative and accessible",
            "recommended_student_strategy": "Read and experiment with code"
        }
    }


@pytest.fixture
def valid_structural_outline() -> Dict[str, Any]:
    """Valid structural outline data."""
    return {
        "chapter_title": "Introduction to Python Programming",
        "guiding_context_questions": [
            "What makes Python unique?",
            "Why should I learn Python?"
        ],
        "outline": [
            {
                "section_title": "Python Overview",
                "section_summary": "Introduction to Python language",
                "pedagogical_purpose": "Introduce core concepts",
                "rhetorical_mode": "expository",
                "subtopics": [
                    {
                        "subtopic_title": "Key Features",
                        "key_concepts": ["Readability", "Interpreted"],
                        "supporting_examples": ["Simple syntax example"],
                        "student_discussion_prompts": ["Why is readability important?"],
                        "notes_on_instructional_sequence": "Start with basics",
                        "sub_subtopics": []
                    }
                ]
            }
        ]
    }


@pytest.fixture
def valid_chapter_analysis(
    valid_comprehension_pass: Dict[str, Any],
    valid_structural_outline: Dict[str, Any]
) -> Dict[str, Any]:
    """Complete valid chapter analysis document."""
    return {
        "system_metadata": {
            "chapter_id": "test-ch-001",
            "file_name": "test_chapter.txt",
            "author_or_editor": "Test Author",
            "version": "v1",
            "created_at": "2023-10-15T14:30:00Z",
            "source_text": "Test Source"
        },
        "comprehension_pass": valid_comprehension_pass,
        "structural_outline": valid_structural_outline,
        "propositional_extraction": {
            "definition": "Propositions are statements of truth.",
            "guiding_prompts": ["What claims are made?"],
            "propositions": [
                {
                    "id": "prop-1",
                    "truth_type": "descriptive",
                    "statement": "Python is interpreted",
                    "evidence_from_text": "Line 2",
                    "implication_for_learning": "Understanding execution model",
                    "connections_to_other_chapters": [],
                    "potential_student_reflection_question": "How does this affect debugging?",
                    "evidence_pointer": "line 2"
                }
            ]
        },
        "analytical_metadata": {
            "subject_domain": "Computer Science - Programming",
            "curriculum_unit": "Unit 1: Introduction",
            "disciplinary_lens": "Technical skills",
            "related_chapters": [],
            "grade_level_or_audience": "Beginner",
            "spiral_position": "introduction"
        }
    }
