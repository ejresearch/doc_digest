"""Tests for FastAPI endpoints."""
import pytest
from fastapi.testclient import TestClient
from pathlib import Path
import io


@pytest.fixture
def client():
    """Create test client."""
    from src.app import app
    return TestClient(app)


@pytest.fixture
def sample_file(sample_chapter_text):
    """Create a sample file for upload."""
    return ("test_chapter.txt", io.BytesIO(sample_chapter_text.encode()), "text/plain")


def test_health_endpoint(client):
    """Test the health check endpoint."""
    response = client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "doc-digester"


def test_digest_endpoint_with_file(client, sample_file, tmp_path, monkeypatch):
    """Test the digest endpoint with a valid file."""
    # Use temp directory for storage
    test_storage = tmp_path / "test_chapters"
    monkeypatch.setattr("src.services.storage.STORAGE_DIR", test_storage)

    response = client.post(
        "/chapters/digest",
        files={"file": sample_file},
        data={"chapter_id": "test-api-001"}
    )

    assert response.status_code == 200
    data = response.json()

    assert "chapter_id" in data
    assert data["status"] == "ok"
    assert "file_path" in data
    assert "timestamp" in data


def test_digest_endpoint_empty_file(client):
    """Test digest endpoint with an empty file."""
    empty_file = ("empty.txt", io.BytesIO(b""), "text/plain")

    response = client.post(
        "/chapters/digest",
        files={"file": empty_file}
    )

    assert response.status_code == 400
    assert "empty" in response.json()["detail"].lower()


def test_digest_endpoint_short_file(client):
    """Test digest endpoint with file that's too short."""
    short_file = ("short.txt", io.BytesIO(b"Too short"), "text/plain")

    response = client.post(
        "/chapters/digest",
        files={"file": short_file}
    )

    assert response.status_code == 400
    assert "too short" in response.json()["detail"].lower()


def test_digest_endpoint_with_metadata(client, sample_file, tmp_path, monkeypatch):
    """Test digest endpoint with all metadata fields."""
    test_storage = tmp_path / "test_chapters"
    monkeypatch.setattr("src.services.storage.STORAGE_DIR", test_storage)

    response = client.post(
        "/chapters/digest",
        files={"file": sample_file},
        data={
            "chapter_id": "test-metadata-001",
            "file_name": "test.txt",
            "author_or_editor": "Test Author",
            "version": "v2",
            "source_text": "Test Source"
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert data["chapter_id"] == "test-metadata-001"


def test_digest_endpoint_large_file(client, tmp_path, monkeypatch):
    """Test that very large files are rejected."""
    test_storage = tmp_path / "test_chapters"
    monkeypatch.setattr("src.services.storage.STORAGE_DIR", test_storage)

    # Create a file larger than 10MB
    large_content = b"x" * (11 * 1024 * 1024)  # 11MB
    large_file = ("large.txt", io.BytesIO(large_content), "text/plain")

    response = client.post(
        "/chapters/digest",
        files={"file": large_file}
    )

    assert response.status_code == 413
    assert "exceeds maximum" in response.json()["detail"].lower()


def test_digest_endpoint_invalid_encoding(client):
    """Test digest endpoint with invalid UTF-8 encoding."""
    # Create file with invalid UTF-8 but valid latin-1
    invalid_utf8 = b"Valid text \xff\xfe invalid utf-8"
    invalid_file = ("invalid.txt", io.BytesIO(invalid_utf8), "text/plain")

    # Should still work with latin-1 fallback, but need minimum length
    padded_content = invalid_utf8 + b" " * 100
    padded_file = ("invalid.txt", io.BytesIO(padded_content), "text/plain")

    response = client.post(
        "/chapters/digest",
        files={"file": padded_file}
    )

    # Should either succeed with latin-1 fallback or fail gracefully
    assert response.status_code in [200, 400]


def test_openapi_schema(client):
    """Test that OpenAPI schema is accessible."""
    response = client.get("/openapi.json")
    assert response.status_code == 200

    schema = response.json()
    assert "openapi" in schema
    assert "/chapters/digest" in schema["paths"]
    assert "/health" in schema["paths"]
