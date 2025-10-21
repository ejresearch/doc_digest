"""Tests for storage module."""
import pytest
import json
from pathlib import Path
from src.services.storage import (
    persist_document,
    load_document,
    generate_chapter_id,
    stable_id,
    StorageError,
    STORAGE_DIR
)


def test_stable_id():
    """Test stable ID generation from bytes."""
    content = b"test content"
    id1 = stable_id(content, "v1")
    id2 = stable_id(content, "v1")

    assert id1 == id2  # Should be deterministic
    assert id1.startswith("ch-")
    assert len(id1) == 19  # "ch-" + 16 hex chars


def test_stable_id_different_versions():
    """Test that different versions produce different IDs."""
    content = b"test content"
    id_v1 = stable_id(content, "v1")
    id_v2 = stable_id(content, "v2")

    assert id_v1 != id_v2


def test_generate_chapter_id_with_metadata(valid_chapter_analysis):
    """Test generate_chapter_id when chapter_id exists in metadata."""
    chapter_id = generate_chapter_id(valid_chapter_analysis)
    assert chapter_id == "test-ch-001"


def test_generate_chapter_id_without_metadata():
    """Test generate_chapter_id generates ID from content hash."""
    doc = {"foo": "bar"}
    chapter_id = generate_chapter_id(doc)

    assert chapter_id.startswith("ch-")
    assert len(chapter_id) == 19


def test_persist_document_success(valid_chapter_analysis, tmp_path, monkeypatch):
    """Test successful document persistence."""
    # Use temp directory for testing
    test_storage = tmp_path / "test_chapters"
    monkeypatch.setattr("src.services.storage.STORAGE_DIR", test_storage)

    result = persist_document(valid_chapter_analysis)

    assert result["status"] == "ok"
    assert result["chapter_id"] == "test-ch-001"
    assert "file_path" in result
    assert "timestamp" in result

    # Verify file was actually created
    file_path = Path(result["file_path"])
    assert file_path.exists()

    # Verify content
    with open(file_path) as f:
        saved_doc = json.load(f)
    assert saved_doc["system_metadata"]["chapter_id"] == "test-ch-001"


def test_persist_document_generates_chapter_id(tmp_path, monkeypatch):
    """Test that persist_document generates chapter_id if missing."""
    test_storage = tmp_path / "test_chapters"
    monkeypatch.setattr("src.services.storage.STORAGE_DIR", test_storage)

    doc = {
        "comprehension_pass": {},
        "structural_outline": {},
        "propositional_extraction": {},
        "analytical_metadata": {}
    }

    result = persist_document(doc)

    assert result["status"] == "ok"
    assert result["chapter_id"].startswith("ch-")


def test_persist_document_adds_timestamp(tmp_path, monkeypatch):
    """Test that persist_document adds timestamp if missing."""
    test_storage = tmp_path / "test_chapters"
    monkeypatch.setattr("src.services.storage.STORAGE_DIR", test_storage)

    doc = {
        "system_metadata": {"chapter_id": "test-123"},
        "comprehension_pass": {},
        "structural_outline": {},
        "propositional_extraction": {},
        "analytical_metadata": {}
    }

    result = persist_document(doc)

    # Load the file and check timestamp was added
    file_path = Path(result["file_path"])
    with open(file_path) as f:
        saved_doc = json.load(f)

    assert "created_at" in saved_doc["system_metadata"]
    assert saved_doc["system_metadata"]["created_at"].endswith("Z")


def test_load_document_success(valid_chapter_analysis, tmp_path, monkeypatch):
    """Test successful document loading."""
    test_storage = tmp_path / "test_chapters"
    monkeypatch.setattr("src.services.storage.STORAGE_DIR", test_storage)

    # First persist a document
    result = persist_document(valid_chapter_analysis)
    chapter_id = result["chapter_id"]

    # Then load it
    loaded_doc = load_document(chapter_id)

    assert loaded_doc["system_metadata"]["chapter_id"] == chapter_id
    assert loaded_doc["comprehension_pass"] == valid_chapter_analysis["comprehension_pass"]


def test_load_document_not_found(tmp_path, monkeypatch):
    """Test load_document raises when document doesn't exist."""
    test_storage = tmp_path / "test_chapters"
    monkeypatch.setattr("src.services.storage.STORAGE_DIR", test_storage)
    test_storage.mkdir(parents=True, exist_ok=True)

    with pytest.raises(StorageError, match="No document found"):
        load_document("nonexistent-id")


def test_persist_multiple_versions(valid_chapter_analysis, tmp_path, monkeypatch):
    """Test that multiple versions of same chapter are saved."""
    test_storage = tmp_path / "test_chapters"
    monkeypatch.setattr("src.services.storage.STORAGE_DIR", test_storage)

    # Persist same document twice
    result1 = persist_document(valid_chapter_analysis)
    result2 = persist_document(valid_chapter_analysis)

    # Should have different file paths (different timestamps)
    assert result1["file_path"] != result2["file_path"]

    # Both files should exist
    assert Path(result1["file_path"]).exists()
    assert Path(result2["file_path"]).exists()
