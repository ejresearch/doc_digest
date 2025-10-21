from fastapi import FastAPI, UploadFile, File, Form, HTTPException, status
from fastapi.responses import JSONResponse
from .services.orchestrator import digest_chapter, DigestError, ValidationError, StorageError
from .utils.logging_config import setup_logging, get_logger

# Initialize logging
setup_logging(level="INFO")
logger = get_logger(__name__)

app = FastAPI(title="Doc Digester", version="0.1.0")

# Maximum file size: 10MB
MAX_FILE_SIZE = 10 * 1024 * 1024

@app.on_event("startup")
async def startup_event():
    logger.info("Doc Digester API starting up")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Doc Digester API shutting down")

@app.post("/chapters/digest")
async def chapters_digest(
    file: UploadFile = File(...),
    chapter_id: str | None = Form(default=None),
    file_name: str | None = Form(default=None),
    author_or_editor: str | None = Form(default=None),
    version: str | None = Form(default="v1"),
    created_at: str | None = Form(default=None),
    source_text: str | None = Form(default=None),
):
    """
    Process a chapter document through the 4-phase analysis pipeline.

    Returns the chapter_id and status on success, or error details on failure.
    """
    logger.info(f"Received digest request for file: {file.filename}")

    try:
        # Read file content with size validation
        content = b""
        chunk_size = 1024 * 1024  # 1MB chunks
        total_size = 0

        while chunk := await file.read(chunk_size):
            total_size += len(chunk)
            if total_size > MAX_FILE_SIZE:
                logger.warning(f"File too large: {total_size} bytes (max: {MAX_FILE_SIZE})")
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail=f"File size exceeds maximum allowed size of {MAX_FILE_SIZE / (1024*1024)}MB"
                )
            content += chunk

        if not content:
            logger.warning("Empty file uploaded")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File is empty"
            )

        # Decode content
        try:
            text = content.decode('utf-8')
        except UnicodeDecodeError:
            logger.warning("UTF-8 decode failed, attempting with latin-1")
            try:
                text = content.decode('latin-1')
            except UnicodeDecodeError as e:
                logger.error(f"Failed to decode file: {e}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Unable to decode file. Please ensure it's a valid text file."
                )

        if len(text.strip()) < 100:
            logger.warning(f"Text too short: {len(text)} characters")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Text content is too short for analysis (minimum 100 characters)"
            )

        # Build system metadata
        from datetime import datetime, timezone
        sys_meta = {
            "chapter_id": chapter_id,
            "file_name": file_name or file.filename,
            "author_or_editor": author_or_editor or "Unknown",
            "version": version,
            "created_at": created_at or datetime.now(timezone.utc).isoformat(),
            "source_text": source_text or ""
        }

        logger.info(f"Processing chapter with {len(text)} characters")

        # Process through pipeline
        result = digest_chapter(text, sys_meta)

        logger.info(f"Successfully processed chapter: {result.get('chapter_id')}")
        return result

    except ValidationError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Validation failed: {str(e)}"
        )

    except StorageError as e:
        logger.error(f"Storage error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to store analysis results: {str(e)}"
        )

    except DigestError as e:
        logger.error(f"Digest error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis pipeline failed: {str(e)}"
        )

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise

    except Exception as e:
        logger.exception(f"Unexpected error processing chapter: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during processing"
        )

@app.get("/health")
async def health_check():
    """Simple health check endpoint."""
    return {"status": "healthy", "service": "doc-digester"}
