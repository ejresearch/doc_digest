# Doc Digester v0.2.0

AI-powered educational chapter analysis system with 5-phase processing pipeline, comprehensive pedagogical extraction, and modern web interface.

## Features

- **5-Phase Analysis Pipeline**: Comprehension → Structural Outline → Propositional Extraction → Analytical Metadata → Pedagogical Mapping
- **Pedagogical Intelligence**: Extracts learning objectives, student activities, assessment questions, visual media references, and temporal analysis
- **Modern Web Interface**: Drag-and-drop file upload with tabbed results visualization
- **Temporal Analysis**: Identifies historical vs contemporary examples and flags content needing updates
- **File Format Support**: Both `.txt` and `.docx` files with proper text extraction
- **GPT-4o Powered**: Uses OpenAI's GPT-4o with structured JSON output and automatic retry logic
- **Comprehensive Error Handling**: Detailed error messages at every layer with proper exception types
- **Structured Logging**: Full observability with INFO-level logging to console
- **Phase-by-Phase Validation**: Pydantic validation after each phase + final JSON Schema validation
- **JSON File Persistence**: Documents automatically saved to `data/chapters/` with timestamps
- **File Size Protection**: 10MB upload limit with chunked reading
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

- **Drag & Drop Upload**: Upload `.txt` or `.docx` files
- **Live Processing Status**: See progress through all 5 phases with animated indicators
- **Tabbed Results**:
  - **Overview**: Chapter info, quick stats, and key concepts
  - **Pedagogical**: Learning objectives, activities, assessments, discussion questions
  - **Structure**: Hierarchical chapter outline
  - **Propositions**: Truth claims with evidence
  - **Temporal Analysis**: Historical/contemporary examples with update priorities
  - **Raw JSON**: Copy-to-clipboard JSON output

## API Endpoints

### POST /chapters/digest

Process a chapter through the 5-phase analysis pipeline.

**Request** (multipart/form-data):
- `file`: Text or Word file (required, max 10MB)
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
  "file_path": "/path/to/data/chapters/ch-xxx_20251022_143022.json",
  "timestamp": "2025-10-22T14:30:22Z",
  "system_metadata": { ... },
  "comprehension_pass": { ... },
  "structural_outline": { ... },
  "propositional_extraction": { ... },
  "analytical_metadata": { ... },
  "pedagogical_mapping": { ... }
}
```

**Error Responses**:
- `400 Bad Request`: Empty file, file too short (<100 chars), encoding error, or invalid .docx
- `413 Request Entity Too Large`: File exceeds 10MB
- `422 Unprocessable Entity`: Validation failed (with detailed error messages)
- `500 Internal Server Error`: Pipeline or storage failure

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

**File Size Limits**:
- Max upload: 10MB
- Recommended: Keep chapters under 200KB of actual text (~50K tokens)
- Files exceeding GPT-4o's 128K context window will fail

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

## Changes from v0.1.0

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
