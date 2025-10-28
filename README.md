# GRAFF (Educational Chapter Analysis) v0.2.1

AI-powered educational chapter analysis system with 5-phase processing pipeline, comprehensive pedagogical extraction, real-time progress tracking, and modern web interface.

## Features

- **5-Phase Analysis Pipeline**: Comprehension → Structural Outline → Propositional Extraction → Analytical Metadata → Pedagogical Mapping
- **Real-Time Progress Tracking**: Server-Sent Events (SSE) stream for live phase-by-phase updates
- **Background Processing**: Non-blocking async analysis with immediate job_id response
- **Pedagogical Intelligence**: Extracts learning objectives, student activities, assessment questions, visual media references, and temporal analysis
- **Modern Web Interface**:
  - Drag-and-drop file upload with tabbed results visualization
  - Dark/light mode toggle with persistent preference
  - Interactive progress bar with phase indicators
  - Delete saved analyses with hover-to-reveal buttons
  - Gradient animations and smooth transitions
- **Temporal Analysis**: Identifies historical vs contemporary examples and flags content needing updates
- **File Format Support**: `.txt`, `.docx`, and `.pdf` files with proper text extraction
- **Large File Optimization**: Smart text truncation for 50K+ character documents to prevent timeouts
- **GPT-4o Powered**: Uses OpenAI's GPT-4o with structured JSON output and automatic retry logic
- **Comprehensive Error Handling**: Detailed error messages at every layer with proper exception types
- **Structured Logging**: Full observability with INFO-level logging to console
- **Phase-by-Phase Validation**: Pydantic validation after each phase + final JSON Schema validation
- **JSON File Persistence**: Documents automatically saved to `data/chapters/` with timestamps
- **File Size Protection**: 100MB upload limit with chunked reading
- **Health Check Endpoint**: `/health` for monitoring

## Quick Start

```bash
# Install dependencies
pip install -e .

# Set up OpenAI API key
export OPENAI_API_KEY="your-api-key-here"
export USE_ACTUAL_LLM="true"

# Run the server
uvicorn src.app:app --reload --port 8000

# Open in browser
open http://localhost:8000
```

## Web Interface

The web interface provides a modern, user-friendly way to analyze educational chapters:

- **Drag & Drop Upload**: Upload `.txt`, `.docx`, or `.pdf` files (up to 100MB)
- **Real-Time Progress Tracking**: Live SSE stream showing actual phase progress
  - Animated gradient progress bar with percentage
  - 5 phase indicators (gray → blue pulsing → green)
  - Time estimates and status messages
  - Automatic result loading on completion
- **Dark/Light Mode**: Toggle with persistent localStorage preference
- **Manage Analyses**:
  - View all saved chapter analyses
  - Delete with hover-to-reveal buttons
  - Load any previous analysis instantly
- **Tabbed Results**:
  - **Overview**: Chapter info, quick stats, and key concepts
  - **Pedagogical**: Learning objectives, activities, assessments, discussion questions
  - **Structure**: Hierarchical chapter outline
  - **Propositions**: Truth claims with evidence
  - **Temporal Analysis**: Historical/contemporary examples with update priorities
  - **Raw JSON**: Copy-to-clipboard JSON output

## API Endpoints

### POST /chapters/digest

Start background processing of a chapter through the 5-phase analysis pipeline. Returns immediately with a job_id for progress tracking.

**Request** (multipart/form-data):
- `file`: Text, Word, or PDF file (required, max 100MB)
- `chapter_id`: Optional custom chapter ID
- `file_name`: Optional filename override
- `author_or_editor`: Optional author information
- `version`: Version string (default: "v1")
- `created_at`: ISO-8601 timestamp (auto-generated if not provided)
- `source_text`: Optional source description

**Response** (200 OK):
```json
{
  "job_id": "c41becf1-43c3-4e69-abb7-fac29f480bc8",
  "status": "processing",
  "message": "Analysis started. Use the job_id to track progress."
}
```

**Error Responses**:
- `400 Bad Request`: Empty file, file too short (<100 chars), encoding error, invalid .docx/.pdf
- `413 Request Entity Too Large`: File exceeds 100MB
- `500 Internal Server Error`: Unexpected error during file processing

### GET /chapters/progress/{job_id}

Stream real-time progress updates via Server-Sent Events (SSE).

**Response** (text/event-stream):
```
data: {"phase":"phase-1","message":"Analyzing chapter comprehension...","status":"in_progress","timestamp":"2025-10-28T16:22:01Z"}

data: {"phase":"phase-1","message":"Phase 1 complete ✓","status":"in_progress","timestamp":"2025-10-28T16:22:21Z"}

data: {"phase":"phase-2","message":"Building structural outline...","status":"in_progress","timestamp":"2025-10-28T16:22:21Z"}

...

data: {"phase":"completed","message":"Analysis complete!","status":"completed","timestamp":"2025-10-28T16:30:15Z"}
```

Stream automatically closes after 2 minutes or when status becomes "completed" or "error".

### GET /chapters/list

List all saved chapter analyses.

**Response** (200 OK):
```json
{
  "chapters": [
    {
      "filename": "ch-001_20251028_143022.json",
      "chapter_id": "ch-001",
      "version": "v25",
      "source_text": "Introduction to Communication",
      "created_at": "2025-10-28T14:30:22Z"
    }
  ]
}
```

### GET /chapters/{filename}

Retrieve a specific chapter analysis.

**Response** (200 OK):
```json
{
  "system_metadata": { ... },
  "comprehension_pass": { ... },
  "structural_outline": { ... },
  "propositional_extraction": { ... },
  "analytical_metadata": { ... },
  "pedagogical_mapping": { ... }
}
```

**Error Responses**:
- `404 Not Found`: Chapter file doesn't exist
- `500 Internal Server Error`: Failed to load chapter

### DELETE /chapters/{filename}

Delete a saved chapter analysis.

**Response** (200 OK):
```json
{
  "message": "Chapter deleted successfully",
  "filename": "ch-001_20251028_143022.json"
}
```

**Error Responses**:
- `400 Bad Request`: Invalid filename (path traversal attempt)
- `404 Not Found`: Chapter file doesn't exist
- `500 Internal Server Error`: Failed to delete chapter

### GET /

Serves the web interface.

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
# Upload via web interface
open http://localhost:8000

# Or use curl for .txt files
curl -X POST http://localhost:8000/chapters/digest \
  -F file=@chapter.txt \
  -F chapter_id=ch-001 \
  -F version=v25 \
  -F source_text="Introduction to Communication"

# Or use curl for .docx files
curl -X POST http://localhost:8000/chapters/digest \
  -F file=@chapter.docx \
  -F chapter_id=ch-002 \
  -F version=v25

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
│  ├─ app.py                    # FastAPI app with .docx support
│  ├─ models.py                 # Pydantic models (including Phase 5)
│  ├─ schemas/
│  │  └─ chapter-analysis.schema.json  # JSON Schema with pedagogical_mapping
│  ├─ services/
│  │  ├─ orchestrator.py        # 5-phase pipeline orchestration
│  │  ├─ llm_client.py          # GPT-4o integration with retry logic
│  │  ├─ openai_client.py       # OpenAI API wrapper with structured output
│  │  ├─ prompts.py             # All 5 phase prompts
│  │  └─ storage.py             # JSON file persistence
│  └─ utils/
│     ├─ logging_config.py      # Logging setup
│     └─ validation.py          # JSON Schema validation
├─ static/
│  ├─ index.html                # Web interface
│  ├─ css/
│  │  └─ style.css              # Modern gradient styling
│  └─ js/
│     └─ app.js                 # Client-side app logic
├─ data/
│  └─ chapters/                 # Persisted analysis results (auto-created)
└─ examples/
   └─ sample_*.json             # Example outputs for each phase
```

## Pipeline Phases

### Phase 1: Comprehension Pass
- **Framework**: WHO/WHAT/WHEN/WHY/HOW
- **Temperature**: 0.15 (deterministic)
- **Model**: `ComprehensionPass`
- **Extracts**: Entities, concepts, temporal context, significance, teaching approach

### Phase 2: Structural Outline
- **Purpose**: Hierarchical chapter structure
- **Temperature**: 0.2
- **Model**: `StructuralOutline`
- **Builds**: Sections → Subtopics → Sub-subtopics with pedagogical metadata

### Phase 3: Propositional Extraction
- **Purpose**: Truth statements with evidence
- **Temperature**: 0.2
- **Model**: `PropositionalExtraction`
- **Identifies**: Descriptive, analytical, and normative claims with textual evidence

### Phase 4: Analytical Metadata
- **Purpose**: Curriculum context
- **Temperature**: 0.25
- **Model**: `AnalyticalMetadata`
- **Derives**: Subject domain, curriculum unit, grade level, related chapters (explicitly mentioned only)

### Phase 5: Pedagogical Mapping (NEW in v0.2.0)
- **Purpose**: Learning support elements and temporal analysis
- **Temperature**: 0.15
- **Model**: `PedagogicalMapping`
- **Max Tokens**: 16,000 (4x default for comprehensive extraction)
- **Extracts**:
  - Learning objectives
  - Student activities (BYLINE exercises, reflections, observations)
  - Assessment questions (KNOWLEDGE CHECK quizzes with types)
  - Chapter summaries and review sections
  - Visual media references with pedagogical purpose
  - Temporal analysis:
    - Historical examples (with relevance flags)
    - Contemporary examples (with update priority: low/medium/high)
    - Temporal range (e.g., "1890s-2025")
  - Potential discussion questions

Each phase:
- Builds on previous phase results
- Validates immediately with Pydantic (fail fast)
- Retries automatically on transient API failures (exponential backoff)
- Logs progress and errors

Final document validated against:
- Pydantic `ChapterAnalysis` model
- JSON Schema (Draft 2020-12)

## Temporal Analysis

Phase 5 includes sophisticated temporal tracking:

**Historical Examples**:
- Automatically identifies dated examples (e.g., "M*A*S*H series (1970s)")
- Flags whether they're still relevant for teaching

**Contemporary Examples**:
- Identifies current references (e.g., "TikTok", "iPad kids")
- Assigns update priority (low/medium/high) based on volatility
- Records "current as of" date for future maintenance

**Temporal Range**:
- Captures the overall time span of content (e.g., "1890s-2025")
- Helps identify chapters that may need updating

## Processing Time & Cost

**Processing Time** (varies by chapter length and API load):
- Phase 1 (Comprehension): 20-60 seconds
- Phase 2 (Structure): 60-120 seconds
- Phase 3 (Propositions): 120-240 seconds (largest phase)
- Phase 4 (Metadata): 10-30 seconds
- Phase 5 (Pedagogical): 300-600 seconds (comprehensive extraction)
- **Total**: 10-20 minutes for a typical textbook chapter

**Cost per Chapter** (with gpt-4o at $2.50/1M input, $10/1M output):
- Short chapter (5-10 pages): $0.10-0.25
- Medium chapter (15-25 pages): $0.30-0.60
- Long chapter (30+ pages): $0.75-1.50

## File Format Support

### Plain Text (.txt)
- UTF-8 or Latin-1 encoding
- Direct text extraction

### Microsoft Word (.docx)
- Automatically extracts paragraph text using `python-docx`
- Strips Word formatting and metadata
- Reduces file size significantly (944KB .docx → 220KB text)
- **Note**: Tables, images, and complex formatting are not preserved

### PDF (.pdf)
- Automatically extracts text using `PyPDF2`
- Processes all pages and combines text
- Works with standard text-based PDFs
- **Note**: Scanned PDFs without OCR will extract poorly

**File Size Limits**:
- Max upload: 100MB
- Recommended: Keep chapters under 200KB of actual text (~50K tokens)
- Large documents (>50K characters) automatically use smart truncation:
  - Phase 1: Full text (comprehension analysis needs complete content)
  - Phase 2: First 50K characters + comprehension results
  - Phase 3: First 50K characters + comprehension + structure
  - Phase 5: First 30K + last 20K characters (captures objectives + summaries)

This intelligent truncation prevents timeouts while maintaining analysis quality by leveraging previously extracted structured data.

## Error Handling

Custom exceptions with detailed error messages:

- **DigestError**: Base exception for pipeline failures
- **PhaseError**: Specific phase failures (includes phase number and original error)
- **ValidationError**: Schema/model validation failures (with detailed path information)
- **StorageError**: Persistence failures
- **LLMConfigurationError**: Missing OpenAI API key
- **LLMAPIError**: OpenAI API failures (with retry logic)

All errors are logged with full context and returned to the client with appropriate HTTP status codes.

## Fabrication Prevention

The system has been carefully tuned to prevent AI hallucination:

**Phase 3 & 4 - Related Chapters**:
- Prompts explicitly instruct: "DO NOT invent or fabricate chapters"
- Only extracts chapter references that are explicitly mentioned in the source text
- Returns empty array if no connections are mentioned

**Phase 5 - Pedagogical Elements**:
- Extracts only elements that are actually present in the chapter
- Uses location markers to tie extractions to specific sections
- High precision mode to avoid inferring activities that don't exist

## Changes from v0.2.0 to v0.2.1

### Major Features
- ✅ **Real-Time Progress Tracking** - Server-Sent Events (SSE) for live phase updates
- ✅ **Background Processing** - Non-blocking async analysis with immediate job_id response
- ✅ **PDF Support** - Extract text from PDF files using PyPDF2
- ✅ **Dark/Light Mode** - Theme toggle with persistent localStorage preference
- ✅ **Delete Functionality** - Remove saved analyses with hover-to-reveal buttons
- ✅ **Smart Text Truncation** - Prevent timeouts on large documents (>50K characters)
- ✅ **100MB File Limit** - Increased from 10MB to support larger documents

### Technical Improvements
- ✅ Background task processing with `asyncio.create_task()`
- ✅ SSE streaming endpoint `/chapters/progress/{job_id}`
- ✅ Intelligent text truncation per phase (50K chars for phases 2-3, 30K+20K for phase 5)
- ✅ CRUD endpoints: GET/DELETE `/chapters/{filename}`, GET `/chapters/list`
- ✅ Enhanced progress UI with animated gradient bar and phase indicators
- ✅ Tailwind CSS migration with gradient animations
- ✅ EventSource integration for real-time frontend updates
- ✅ Path traversal protection in delete endpoint

### Bug Fixes
- ✅ Fixed Phase 2/3/5 timeouts on large documents (218K+ characters)
- ✅ Fixed file selection display issues (click-to-browse not working)
- ✅ Fixed progress tracking showing fake simulated data
- ✅ Increased timeout from 60s to 180s and retries from 3 to 5

## Changes from v0.1.0 to v0.2.0

### Major Features
- ✅ **Phase 5: Pedagogical Mapping** - New comprehensive learning support extraction
- ✅ **Temporal Analysis** - Historical vs contemporary example tracking with update priorities
- ✅ **Web Interface** - Modern drag-and-drop UI with tabbed results visualization
- ✅ **Word Document Support** - Proper `.docx` text extraction (not just binary decoding)
- ✅ **OpenAI Integration** - Full GPT-4o integration with structured JSON output
- ✅ **Fabrication Prevention** - Strict prompts to prevent hallucinated chapter references

### Technical Improvements
- ✅ Higher token limits for Phase 5 (16K tokens for comprehensive extraction)
- ✅ Static file serving for web interface
- ✅ Improved error handling for file format issues
- ✅ Better logging with phase-specific progress tracking
- ✅ Enhanced Pydantic models with 8 new classes for Phase 5

### Bug Fixes
- ✅ Fixed .docx files being decoded as binary (was causing 8x token overflow)
- ✅ Fixed Phase 5 JSON truncation issues
- ✅ Fixed UTF-8 decoding fallback logic
- ✅ Removed fabricated chapter references from prompts

## Development

### Environment Variables

```bash
# Required for LLM mode
export OPENAI_API_KEY="sk-..."
export USE_ACTUAL_LLM="true"

# Optional
export OPENAI_MODEL="gpt-4o"  # Default model
```

### Logging

Logging is configured at the INFO level by default. To change:
```python
setup_logging(level="DEBUG")  # in src/app.py
```

Logs include:
- Phase execution progress with timing
- .docx paragraph extraction counts
- Validation results
- Storage operations
- OpenAI API retries and errors
- Full error stack traces

### Customizing Prompts

All prompts are in `src/services/prompts.py`:
- `get_phase_1_prompts()` - Comprehension (WHO/WHAT/WHEN/WHY/HOW)
- `get_phase_2_prompts()` - Structural outline
- `get_phase_3_prompts()` - Propositional extraction
- `get_phase_4_prompts()` - Analytical metadata
- `get_phase_5_prompts()` - Pedagogical mapping (260+ lines)

Each prompt function returns a dict with `system_prompt` and `user_prompt` keys.

## License

Proprietary - All rights reserved
