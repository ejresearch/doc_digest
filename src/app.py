from fastapi import FastAPI, UploadFile, File, Form, HTTPException, status
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from docx import Document
import io
from .services.orchestrator import digest_chapter, DigestError, ValidationError, StorageError
from .utils.logging_config import setup_logging, get_logger

# Initialize logging
setup_logging(level="INFO")
logger = get_logger(__name__)

app = FastAPI(title="Doc Digester", version="0.2.0")

# Mount static files
static_path = Path(__file__).parent.parent / "static"
if static_path.exists():
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

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

        # Extract text based on file type
        filename_lower = file.filename.lower() if file.filename else ""

        if filename_lower.endswith('.docx'):
            # Handle .docx files using python-docx
            logger.info("Processing .docx file")
            try:
                doc = Document(io.BytesIO(content))
                paragraphs = [para.text for para in doc.paragraphs if para.text.strip()]
                text = '\n'.join(paragraphs)
                logger.info(f"Extracted {len(paragraphs)} paragraphs from .docx")
            except Exception as e:
                logger.error(f"Failed to extract text from .docx: {e}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Unable to process .docx file. Please ensure it's a valid Word document."
                )
        else:
            # Handle plain text files
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

@app.get("/")
async def root():
    """Serve the web interface."""
    index_path = Path(__file__).parent.parent / "static" / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path))
    return {"message": "Doc Digester API", "version": "0.2.0"}

@app.get("/health")
async def health_check():
    """Simple health check endpoint."""
    return {"status": "healthy", "service": "doc-digester"}

@app.get("/chapters/list")
async def list_chapters():
    """List all available chapter analyses."""
    from pathlib import Path
    import json

    data_dir = Path(__file__).parent.parent / "data" / "chapters"
    chapters = []

    if data_dir.exists():
        for file in data_dir.glob("*.json"):
            try:
                with open(file, 'r') as f:
                    data = json.load(f)
                    meta = data.get('system_metadata', {})
                    chapters.append({
                        'filename': file.name,
                        'chapter_id': meta.get('chapter_id'),
                        'version': meta.get('version'),
                        'source_text': meta.get('source_text'),
                        'created_at': meta.get('created_at')
                    })
            except Exception:
                continue

    return {"chapters": chapters}

@app.get("/chapters/{filename}")
async def get_chapter(filename: str):
    """Get a specific chapter analysis by filename."""
    from pathlib import Path
    import json

    data_dir = Path(__file__).parent.parent / "data" / "chapters"
    file_path = data_dir / filename

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Chapter not found")

    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load chapter: {str(e)}")
