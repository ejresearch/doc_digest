# Setup Guide

## Quick Start

### 1. Install Dependencies

```bash
# Install main dependencies
pip install -e .

# Install dev dependencies (for testing)
pip install -e ".[dev]"
```

### 2. Configure Environment Variables

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your OpenAI API key
nano .env
```

**Important:** Set these values in `.env`:
```bash
# Enable actual LLM calls
USE_ACTUAL_LLM=true

# Add your OpenAI API key (get it from https://platform.openai.com/api-keys)
OPENAI_API_KEY=sk-proj-your-actual-key-here

# Choose your model (gpt-4o recommended)
OPENAI_MODEL=gpt-4o
```

### 3. Run the Server

```bash
uvicorn src.app:app --reload
```

The API will be available at `http://localhost:8000`

### 4. Test the API

```bash
# Health check
curl http://localhost:8000/health

# Process a chapter (with stub data - no API key needed)
curl -X POST http://localhost:8000/chapters/digest \
  -F file=@test_sample.txt

# With actual LLM (requires API key and USE_ACTUAL_LLM=true)
curl -X POST http://localhost:8000/chapters/digest \
  -F file=@test_sample.txt \
  -F chapter_id=ch-001
```

## Configuration Options

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `USE_ACTUAL_LLM` | `false` | Set to `true` to enable OpenAI API calls |
| `OPENAI_API_KEY` | - | Your OpenAI API key (required if `USE_ACTUAL_LLM=true`) |
| `OPENAI_MODEL` | `gpt-4o` | Model to use (gpt-4o, gpt-4-turbo, gpt-4, gpt-3.5-turbo) |
| `OPENAI_MAX_TOKENS` | `4000` | Maximum tokens in LLM response |
| `OPENAI_TIMEOUT` | `60` | API call timeout in seconds |
| `OPENAI_MAX_RETRIES` | `3` | Number of retry attempts for transient failures |
| `OPENAI_RETRY_MIN_WAIT` | `4` | Minimum wait time between retries (seconds) |
| `OPENAI_RETRY_MAX_WAIT` | `10` | Maximum wait time between retries (seconds) |
| `LOG_LEVEL` | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL) |

### Stub Mode vs. LLM Mode

**Stub Mode** (`USE_ACTUAL_LLM=false`):
- No API key required
- Returns empty/minimal data structures
- Fast testing and development
- No costs

**LLM Mode** (`USE_ACTUAL_LLM=true`):
- Requires valid OpenAI API key
- Performs actual chapter analysis
- Slower (60-120 seconds per chapter)
- Costs $0.01-0.50 per chapter (depending on chapter length and model)

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_validation.py

# Run with verbose output
pytest -v

# Run only fast tests (skip slow integration tests)
pytest -m "not slow"
```

After running with coverage, open `htmlcov/index.html` in your browser to see the coverage report.

## Type Checking

```bash
# Run mypy type checker
mypy src/

# Run on specific file
mypy src/services/llm_client.py
```

## Development Workflow

### 1. Testing Without LLM (Recommended for Development)

```bash
# Set USE_ACTUAL_LLM=false in .env
USE_ACTUAL_LLM=false

# Run tests (fast, no API calls)
pytest

# Start server and test endpoints
uvicorn src.app:app --reload
```

### 2. Testing With LLM (For Integration Testing)

```bash
# Set USE_ACTUAL_LLM=true in .env
USE_ACTUAL_LLM=true
OPENAI_API_KEY=your-key-here

# Run full pipeline test
curl -X POST http://localhost:8000/chapters/digest \
  -F file=@test_sample.txt \
  -F chapter_id=test-001
```

### 3. Check Results

```bash
# View stored chapter
ls -la data/chapters/

# Read JSON output
cat data/chapters/test-001_*.json | jq .
```

## Common Issues

### Issue: "OPENAI_API_KEY not found"

**Solution:** Create a `.env` file based on `.env.example` and add your API key:
```bash
cp .env.example .env
# Edit .env and add your key
```

### Issue: "Module not found" errors

**Solution:** Install the package in development mode:
```bash
pip install -e .
```

### Issue: Tests failing with import errors

**Solution:** Install dev dependencies:
```bash
pip install -e ".[dev]"
```

### Issue: "File too large" (413 error)

**Solution:** The max file size is 10MB. Split large documents or adjust `MAX_FILE_SIZE` in `src/app.py`.

### Issue: LLM calls timing out

**Solution:** Increase `OPENAI_TIMEOUT` in `.env`:
```bash
OPENAI_TIMEOUT=120  # 2 minutes
```

### Issue: Rate limit errors from OpenAI

**Solution:** The retry logic will automatically handle rate limits with exponential backoff. If it persists, you may need to:
- Reduce concurrent requests
- Upgrade your OpenAI account tier
- Increase `OPENAI_RETRY_MAX_WAIT`

## API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

## Directory Structure

```
doc_digester/
├── .env                    # Your environment variables (git-ignored)
├── .env.example            # Template for environment variables
├── .gitignore              # Git ignore rules
├── pyproject.toml          # Project dependencies and config
├── README.md               # Project documentation
├── SETUP.md                # This file
├── CHANGES.md              # Changelog
├── test_sample.txt         # Sample chapter for testing
├── src/
│   ├── app.py              # FastAPI application
│   ├── models.py           # Pydantic models
│   ├── services/
│   │   ├── openai_client.py    # OpenAI API client with retry logic
│   │   ├── llm_client.py       # Phase implementations
│   │   ├── orchestrator.py     # Pipeline orchestration
│   │   └── storage.py          # JSON file persistence
│   ├── utils/
│   │   ├── logging_config.py   # Logging setup
│   │   └── validation.py       # Schema validation
│   └── schemas/
│       └── chapter-analysis.schema.json  # JSON Schema
├── data/
│   └── chapters/           # Stored analysis results (auto-created)
└── tests/
    ├── conftest.py         # Pytest fixtures
    ├── test_validation.py  # Validation tests
    ├── test_storage.py     # Storage tests
    └── test_api.py         # API endpoint tests
```

## Next Steps

1. **Get an OpenAI API key** from https://platform.openai.com/api-keys
2. **Add it to `.env`** file
3. **Set `USE_ACTUAL_LLM=true`** to enable real analysis
4. **Process your first chapter**
5. **Check the results** in `data/chapters/`

## Cost Estimation

Rough cost estimates per chapter (using gpt-4o):

| Chapter Length | Tokens | Cost |
|---------------|--------|------|
| Short (1-2 pages) | ~2K | $0.01-0.02 |
| Medium (5-10 pages) | ~8K | $0.05-0.10 |
| Long (20+ pages) | ~20K | $0.20-0.50 |

**Note:** These are estimates. Actual costs depend on:
- Input chapter length
- Output analysis detail
- Model used (gpt-4o vs gpt-4 vs gpt-3.5-turbo)
- Number of retries

Monitor your usage at https://platform.openai.com/usage
