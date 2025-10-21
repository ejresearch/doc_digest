# Quick Start - Get Running in 5 Minutes

## Step 1: Create Your `.env` File (30 seconds)

```bash
cd /Users/elle_jansick/doc_digester

# Create .env from template
cp .env.example .env

# Edit it with your API key
nano .env
```

**In the `.env` file, set:**
```bash
# IMPORTANT: Set this to true to use OpenAI
USE_ACTUAL_LLM=true

# Add your NEW API key (the one you just created after revoking the old one)
OPENAI_API_KEY=sk-proj-YOUR-NEW-KEY-HERE

# Use GPT-4o (best quality/price ratio)
OPENAI_MODEL=gpt-4o
```

Save and exit (Ctrl+X, then Y, then Enter).

## Step 2: Install Dependencies (1 minute)

```bash
# Install main dependencies
pip install -e .

# Optional: Install dev dependencies for testing
pip install -e ".[dev]"
```

## Step 3: Start the Server (5 seconds)

```bash
uvicorn src.app:app --reload
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Doc Digester API starting up
```

## Step 4: Test It! (2 minutes)

### Option A: Quick Test with Sample File

Open a new terminal and run:

```bash
cd /Users/elle_jansick/doc_digester

# Test the health endpoint
curl http://localhost:8000/health

# Process the sample chapter (this will take 60-120 seconds)
curl -X POST http://localhost:8000/chapters/digest \
  -F file=@test_sample.txt \
  -F chapter_id=my-first-chapter
```

### Option B: Use the Interactive API Docs

1. Open your browser to: http://localhost:8000/docs
2. Click on **POST /chapters/digest**
3. Click "Try it out"
4. Click "Choose File" and select `test_sample.txt`
5. Fill in chapter_id: `my-first-chapter`
6. Click "Execute"
7. Wait ~60-120 seconds for the analysis to complete

## Step 5: View the Results (10 seconds)

```bash
# List the saved chapters
ls -la data/chapters/

# View the JSON output (install jq if you don't have it: brew install jq)
cat data/chapters/my-first-chapter_*.json | jq .

# Or without jq:
cat data/chapters/my-first-chapter_*.json
```

## What You Should See

The analysis will have 4 main sections:

1. **comprehension_pass** - WHO/WHAT/WHEN/WHY/HOW framework
2. **structural_outline** - Hierarchical chapter structure
3. **propositional_extraction** - Truth statements with evidence
4. **analytical_metadata** - Curriculum context

Example output:
```json
{
  "comprehension_pass": {
    "who": [
      {
        "entity": "Guido van Rossum",
        "role_or_function": "Creator of Python",
        ...
      }
    ],
    "what": [
      {
        "concept_or_topic": "Python Programming",
        "definition_or_description": "High-level interpreted language",
        ...
      }
    ],
    ...
  },
  "structural_outline": {
    "chapter_title": "Introduction to Python Programming",
    "outline": [ ... ]
  },
  ...
}
```

---

## Troubleshooting

### "OPENAI_API_KEY not found in environment"

**Fix:** Make sure your `.env` file exists and has the API key:
```bash
cat .env
# Should show: OPENAI_API_KEY=sk-proj-...
```

### "Invalid API key"

**Fix:** Your API key might be wrong or revoked. Get a new one:
1. Go to https://platform.openai.com/api-keys
2. Click "Create new secret key"
3. Copy it
4. Update `.env` with the new key

### "Module not found" errors

**Fix:** Install the package:
```bash
pip install -e .
```

### Request takes forever / times out

**Fix:** Increase timeout in `.env`:
```bash
OPENAI_TIMEOUT=120
```

### "Rate limit exceeded"

**Fix:** The retry logic will handle this automatically. If it keeps happening:
- Wait a few minutes between requests
- Check your OpenAI usage limits
- Consider upgrading your OpenAI plan

---

## Next Steps

### Process Your Own Chapters

```bash
curl -X POST http://localhost:8000/chapters/digest \
  -F file=@/path/to/your/chapter.txt \
  -F chapter_id=chapter-1 \
  -F author_or_editor="Your Name" \
  -F version=v1
```

### Run in Stub Mode (For Testing Without Costs)

Edit `.env`:
```bash
USE_ACTUAL_LLM=false
```

Restart the server. Now it returns stub data instantly with no OpenAI costs.

### Run Tests

```bash
# Install dev dependencies first
pip install -e ".[dev]"

# Run tests
pytest

# With coverage
pytest --cov=src
```

### Check Logs

The server logs show exactly what's happening:
```
INFO - Received digest request for file: test_sample.txt
INFO - Processing chapter with 1234 characters
INFO - Running Phase 1: Comprehension Pass
INFO - Phase 1 completed successfully
INFO - Running Phase 2: Structural Outline
...
```

Set log level to DEBUG for more detail:
```bash
# In .env
LOG_LEVEL=DEBUG
```

---

## Cost Estimation

With GPT-4o:
- Short chapter (1-2 pages): $0.01-0.02
- Medium chapter (5-10 pages): $0.05-0.10
- Long chapter (20+ pages): $0.20-0.50

Monitor your usage at: https://platform.openai.com/usage

---

## Tips

1. **Start small:** Test with the provided `test_sample.txt` first
2. **Use stub mode** for development to avoid costs
3. **Check logs** if something goes wrong
4. **Monitor costs** on OpenAI platform
5. **Save results:** All analyses are saved to `data/chapters/`

---

## Quick Reference

| Task | Command |
|------|---------|
| Start server | `uvicorn src.app:app --reload` |
| Health check | `curl http://localhost:8000/health` |
| Process chapter | `curl -X POST http://localhost:8000/chapters/digest -F file=@chapter.txt` |
| View docs | http://localhost:8000/docs |
| Run tests | `pytest` |
| Check types | `mypy src/` |
| View results | `cat data/chapters/*.json \| jq .` |

---

## You're Ready!

Your Doc Digester is now running and ready to analyze educational chapters with GPT-4o.

**Questions?** Check:
- SETUP.md (detailed setup)
- README.md (full documentation)
- IMPLEMENTATION_SUMMARY.md (technical details)
- http://localhost:8000/docs (interactive API docs)
