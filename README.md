# Doc Digester

Four-phase chapter analysis service with comprehensive error handling, logging, and JSON file persistence.

## Features

- **4-Phase Analysis Pipeline**: Comprehension → Structural Outline → Propositional Extraction → Analytical Metadata
- **Comprehensive Error Handling**: Detailed error messages at every layer with proper exception types
- **Structured Logging**: Full observability with INFO-level logging to console
- **Phase-by-Phase Validation**: Pydantic validation after each phase + final JSON Schema validation
- **JSON File Persistence**: Documents automatically saved to `data/chapters/` with timestamps
- **File Size Protection**: 10MB upload limit with chunked reading
- **Health Check Endpoint**: `/health` for monitoring

## Run

```bash
uvicorn src.app:app --reload
```

## Endpoints

### POST /chapters/digest

Process a chapter through the 4-phase analysis pipeline.

**Request** (multipart/form-data):
- `file`: Text file (required, max 10MB)
- `chapter_id`: Optional custom chapter ID
- `file_name`: Optional filename override
- `author_or_editor`: Optional author information
- `version`: Version string (default: "v1")
- `created_at`: ISO-8601 timestamp (auto-generated if not provided)
- `source_text`: Optional source description

**Response** (200 OK):
```json
{
  "chapter_id": "ch-a1b2c3d4e5f6g7h8",
  "status": "ok",
  "file_path": "/path/to/data/chapters/ch-xxx_20231015_143022.json",
  "timestamp": "2023-10-15T14:30:22Z"
}
```

**Error Responses**:
- `400 Bad Request`: Empty file, file too short (<100 chars), or encoding error
- `413 Request Entity Too Large`: File exceeds 10MB
- `422 Unprocessable Entity`: Validation failed (with detailed error messages)
- `500 Internal Server Error`: Pipeline or storage failure

### GET /health

Health check endpoint.

**Response** (200 OK):
```json
{
  "status": "healthy",
  "service": "doc-digester"
}
```

## Example Usage

```bash
# Basic usage
curl -X POST http://localhost:8000/chapters/digest \
  -F file=@test_sample.txt

# With metadata
curl -X POST http://localhost:8000/chapters/digest \
  -F file=@examples/sample.txt \
  -F chapter_id=ch-001 \
  -F version=v25 \
  -F source_text="DMC v25"

# Health check
curl http://localhost:8000/health
```

## Project Structure

```
doc_digester/
├─ .gitignore
├─ pyproject.toml
├─ README.md
├─ src/
│  ├─ app.py                    # FastAPI application with error handling
│  ├─ models.py                 # Pydantic models for all phases
│  ├─ schemas/
│  │  └─ chapter-analysis.schema.json  # JSON Schema (Draft 2020-12)
│  ├─ services/
│  │  ├─ orchestrator.py        # Pipeline orchestration with validation
│  │  ├─ llm_client.py          # LLM API client (stubbed, ready for integration)
│  │  └─ storage.py             # JSON file persistence
│  └─ utils/
│     ├─ logging_config.py      # Logging setup
│     └─ validation.py          # JSON Schema validation with error formatting
├─ data/
│  └─ chapters/                 # Persisted analysis results (auto-created)
└─ examples/
   ├─ sample_system_metadata.json
   ├─ sample_comprehension_pass.json
   ├─ sample_structural_outline.json
   ├─ sample_propositional_extraction.json
   └─ sample_analytical_metadata.json
```

## How It Works - Data Flow

```
User Upload (chapter.txt)
  │
  ├─ Validates: size (<10MB), encoding (UTF-8), length (>100 chars)
  │
  ▼
┌─────────────────────────────────────┐
│ FastAPI App (app.py)                │
│ • File validation & decoding        │
│ • Build system metadata             │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│ Orchestrator (orchestrator.py)      │
│ • Coordinates 4-phase pipeline      │
│ • Validates after each phase        │
└────────────┬────────────────────────┘
             │
    ┌────────┴────────┐
    ▼                 ▼
┌─────────┐      ┌──────────────┐
│ Phase 1 │──────▶│ OpenAI API   │
│ Compre- │      │ (gpt-4o)     │
│ hension │◀──────│ Temp: 0.15   │
└────┬────┘      │ + Retry      │
     │           └──────────────┘
     │ validate with Pydantic
     ▼
┌─────────┐
│ Phase 2 │──────▶ OpenAI API (Temp: 0.20)
│ Outline │◀────── + Context from Phase 1
└────┬────┘       + Retry logic
     │
     │ validate with Pydantic
     ▼
┌─────────┐
│ Phase 3 │──────▶ OpenAI API (Temp: 0.20)
│  Props  │◀────── + Context from Phases 1+2
└────┬────┘       + Retry logic
     │
     │ validate with Pydantic
     ▼
┌─────────┐
│ Phase 4 │──────▶ OpenAI API (Temp: 0.25)
│Metadata │◀────── + Context from Phases 1+2+3
└────┬────┘       + Retry logic
     │
     │ validate with Pydantic
     ▼
┌─────────────────────────────────────┐
│ Assemble Complete Document          │
│ • Merge all 4 phases                │
│ • Add system metadata               │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│ Final Validation                    │
│ • JSON Schema validation            │
│ • Pydantic ChapterAnalysis check    │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│ Storage (storage.py)                │
│ • Generate/extract chapter_id       │
│ • Add timestamp                     │
│ • Write to data/chapters/*.json     │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│ Response                            │
│ {chapter_id, status, file_path,     │
│  timestamp}                         │
└─────────────────────────────────────┘
```

**Processing Time:**
- **Stub Mode** (USE_ACTUAL_LLM=false): <1 second
- **LLM Mode** (USE_ACTUAL_LLM=true): 60-120 seconds

**Cost per Chapter** (with gpt-4o):
- Short (1-2 pages): $0.01-0.02
- Medium (5-10 pages): $0.05-0.10
- Long (20+ pages): $0.20-0.50

## Pipeline Phases

1. **Phase 1: Comprehension Pass** (WHO/WHAT/WHEN/WHY/HOW framework)
   - Validated with `ComprehensionPass` Pydantic model
   - Temperature: 0.15 (deterministic)
   - Extracts: Entities, concepts, context, significance, teaching approach

2. **Phase 2: Structural Outline** (Hierarchical chapter structure)
   - Validated with `StructuralOutline` Pydantic model
   - Temperature: 0.2
   - Builds: Sections → Subtopics → Sub-subtopics with pedagogical metadata

3. **Phase 3: Propositional Extraction** (Truth statements with evidence)
   - Validated with `PropositionalExtraction` Pydantic model
   - Temperature: 0.2
   - Identifies: Descriptive, analytical, and normative claims with evidence

4. **Phase 4: Analytical Metadata** (Curriculum context)
   - Validated with `AnalyticalMetadata` Pydantic model
   - Temperature: 0.25 (slightly more creative)
   - Derives: Subject domain, curriculum unit, grade level, spiral position

Each phase:
- Builds on previous phase results
- Validates immediately (fail fast)
- Retries automatically on transient API failures
- Logs progress and errors

Final document validated against both:
- Pydantic `ChapterAnalysis` model
- JSON Schema (Draft 2020-12)

## Error Handling

The system includes comprehensive error handling with custom exceptions:

- **DigestError**: Base exception for pipeline failures
- **PhaseError**: Specific phase failures (includes phase number and original error)
- **ValidationError**: Schema/model validation failures (with detailed path information)
- **StorageError**: Persistence failures

All errors are logged with full context and returned to the client with appropriate HTTP status codes.

## Installation

```bash
pip install -e .
```

## Storage

Documents are automatically persisted to `data/chapters/` as JSON files with the format:
```
{chapter_id}_{timestamp}.json
```

Example: `ch-a1b2c3d4e5f6g7h8_20231015_143022.json`

## Development

### LLM Integration

The LLM client in `src/services/llm_client.py` is currently stubbed. To integrate with an actual LLM:

1. Replace stub implementations in each phase function
2. Use the configured temperature constants for each phase
3. Return responses that match the Pydantic model schemas
4. Consider using `.model_json_schema()` for structured output

Example structure:
```python
response = llm_api.call(
    prompt=build_comprehension_prompt(text),
    temperature=PHASE_1_TEMPERATURE,
    schema=ComprehensionPass.model_json_schema()
)
return {"comprehension_pass": response}
```

### Logging

Logging is configured at the INFO level by default. To change:
```python
setup_logging(level="DEBUG")  # in src/app.py
```

Logs include:
- Phase execution progress
- Validation results
- Storage operations
- Error details with stack traces

## Changes from v0.1.0

- ✅ Comprehensive error handling at all layers
- ✅ Structured logging throughout the application
- ✅ Phase-by-phase Pydantic validation (fail fast)
- ✅ Actual JSON file persistence (no longer stubbed)
- ✅ Removed redundant `phases.py` layer (direct LLM client calls)
- ✅ File upload size limits and chunked reading
- ✅ Better error messages with validation path details
- ✅ Health check endpoint
- ✅ .gitignore file
