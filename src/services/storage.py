import json
import hashlib
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, Any
from ..utils.logging_config import get_logger

logger = get_logger(__name__)

# Storage configuration
STORAGE_DIR = Path(__file__).parents[2] / "data" / "chapters"

class StorageError(Exception):
    """Exception raised when storage operations fail."""
    pass

def stable_id(file_bytes: bytes, version: str = "v1") -> str:
    """
    Generate a stable chapter ID from file content and version.

    Args:
        file_bytes: The raw file bytes
        version: Version string to include in hash

    Returns:
        Stable chapter ID string (e.g., 'ch-a1b2c3d4e5f6g7h8')
    """
    h = hashlib.sha256(file_bytes + version.encode()).hexdigest()[:16]
    return f"ch-{h}"

def ensure_storage_directory() -> Path:
    """
    Ensure the storage directory exists, creating it if necessary.

    Returns:
        Path to the storage directory

    Raises:
        StorageError: If directory creation fails
    """
    try:
        STORAGE_DIR.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Storage directory ready: {STORAGE_DIR}")
        return STORAGE_DIR
    except Exception as e:
        logger.error(f"Failed to create storage directory: {e}")
        raise StorageError(f"Could not create storage directory: {str(e)}")

def generate_chapter_id(doc: Dict[str, Any]) -> str:
    """
    Generate or extract chapter ID from document.

    Args:
        doc: The document dictionary

    Returns:
        Chapter ID string
    """
    # Try to get chapter_id from system_metadata
    if doc.get("system_metadata") and doc["system_metadata"].get("chapter_id"):
        return doc["system_metadata"]["chapter_id"]

    # Generate ID from content hash
    content_str = json.dumps(doc, sort_keys=True)
    h = hashlib.sha256(content_str.encode()).hexdigest()[:16]
    generated_id = f"ch-{h}"

    logger.info(f"Generated chapter_id: {generated_id}")
    return generated_id

def persist_document(doc: Dict[str, Any]) -> Dict[str, str]:
    """
    Persist the analyzed chapter document to JSON file storage.

    Args:
        doc: The complete chapter analysis document

    Returns:
        Dictionary with chapter_id, status, and file_path

    Raises:
        StorageError: If persistence fails
    """
    try:
        # Ensure storage directory exists
        storage_dir = ensure_storage_directory()

        # Get or generate chapter ID
        chapter_id = generate_chapter_id(doc)

        # Update system_metadata with chapter_id if not set
        if not doc.get("system_metadata"):
            doc["system_metadata"] = {}
        if not doc["system_metadata"].get("chapter_id"):
            doc["system_metadata"]["chapter_id"] = chapter_id

        # Add timestamp if not present
        if not doc["system_metadata"].get("created_at"):
            doc["system_metadata"]["created_at"] = datetime.utcnow().isoformat() + "Z"

        # Create filename (sanitize chapter_id for filesystem)
        safe_id = chapter_id.replace("/", "_").replace("\\", "_")
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"{safe_id}_{timestamp}.json"
        file_path = storage_dir / filename

        # Write document to file
        logger.info(f"Writing document to: {file_path}")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(doc, f, indent=2, ensure_ascii=False)

        logger.info(f"Successfully persisted chapter: {chapter_id}")

        return {
            "chapter_id": chapter_id,
            "status": "ok",
            "file_path": str(file_path),
            "timestamp": doc["system_metadata"]["created_at"]
        }

    except StorageError:
        # Re-raise storage errors
        raise

    except Exception as e:
        logger.exception(f"Unexpected error persisting document: {e}")
        raise StorageError(f"Failed to persist document: {str(e)}")

def load_document(chapter_id: str) -> Dict[str, Any]:
    """
    Load a chapter document by ID from storage.

    Args:
        chapter_id: The chapter ID to load

    Returns:
        The chapter analysis document

    Raises:
        StorageError: If document cannot be found or loaded
    """
    try:
        storage_dir = ensure_storage_directory()

        # Find files matching the chapter_id
        safe_id = chapter_id.replace("/", "_").replace("\\", "_")
        matching_files = list(storage_dir.glob(f"{safe_id}_*.json"))

        if not matching_files:
            raise StorageError(f"No document found for chapter_id: {chapter_id}")

        # Load the most recent file
        latest_file = max(matching_files, key=lambda p: p.stat().st_mtime)

        logger.info(f"Loading document from: {latest_file}")
        with open(latest_file, "r", encoding="utf-8") as f:
            doc = json.load(f)

        return doc

    except StorageError:
        raise

    except Exception as e:
        logger.exception(f"Unexpected error loading document: {e}")
        raise StorageError(f"Failed to load document: {str(e)}")
