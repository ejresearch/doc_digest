# GRAFF (Granular Retrieval And Factual Framework) v0.3.0

AI-powered educational chapter analysis system that transforms textbook chapters into structured, queryable knowledge databases for adaptive tutoring systems.

## What It Does

GRAFF extracts a complete knowledge representation from textbook chapters:

```
Chapter Text → Structure → Propositions → Key Takeaways
```

- **Structure**: Hierarchical sections, summary, entities, keywords
- **Propositions**: Atomic facts tagged with Bloom's Taxonomy levels
- **Key Takeaways**: Higher-order insights synthesizing across propositions

## Three-Pass Architecture

GRAFF uses a three-pass pipeline where each pass builds on the previous:

```
Pass 1: STRUCTURE
────────────────────────────────────────────────────────
Input:  Chapter text
Output: Sections, summary, entities, keywords
        │
        ▼ (feeds into)

Pass 2: PROPOSITIONS
────────────────────────────────────────────────────────
Input:  Chapter text + structure from Pass 1
Output: All atomic facts, tagged with unit_ids
        │
        ▼ (feeds into)

Pass 3: KEY TAKEAWAYS
────────────────────────────────────────────────────────
Input:  Structure + ALL propositions
Output: Synthesized insights linking proposition_ids
```

**Why three passes?**
- Pass 2 needs structure to tag propositions with section IDs
- Pass 3 needs ALL propositions to synthesize cross-section takeaways
- Each pass is focused, producing higher quality output

## Features

- **Three-Pass Analysis**: Structure → Propositions → Takeaways
- **Bloom's Taxonomy Tagging**: Propositions tagged as remember/understand/apply/analyze
- **Cross-Section Synthesis**: Takeaways can bridge across multiple sections
- **Real-Time Progress**: Server-Sent Events (SSE) for live updates
- **Modern Web Interface**: Drag-and-drop upload, dark/light mode, tabbed results
- **File Format Support**: `.txt`, `.docx`, `.pdf`
- **GPT-5.2 Powered**: Uses OpenAI's latest model via `responses.create()` API

## Quick Start

```bash
# Install dependencies
pip install -e .

# Set up OpenAI API key
export OPENAI_API_KEY="your-api-key-here"

# Run the server
uvicorn src.app:app --reload --port 8000

# Open in browser
open http://localhost:8000
```

## Output Structure

GRAFF produces a `ChapterAnalysis` with three connected layers:

```json
{
  "chapter_id": "ch_abc123",
  "chapter_title": "The Studio System",

  "phase1": {
    "summary": "One-paragraph overview...",
    "sections": [
      {"unit_id": "1.1", "title": "Introduction", "level": 1},
      {"unit_id": "1.2", "title": "Vertical Integration", "level": 1},
      {"unit_id": "1.2.1", "title": "Production Control", "level": 2, "parent_unit_id": "1.2"}
    ],
    "key_entities": [
      {"name": "Paramount Pictures", "type": "organization"},
      {"name": "vertical integration", "type": "concept"}
    ],
    "keywords": ["studio system", "block booking", "exhibition"]
  },

  "phase2": {
    "propositions": [
      {
        "proposition_id": "ch_abc123_1.2_p001",
        "unit_id": "1.2",
        "proposition_text": "Vertical integration refers to studio ownership of production, distribution, and exhibition.",
        "bloom_level": "remember",
        "bloom_verb": "define",
        "evidence_location": "1.2:¶002"
      }
    ],
    "key_takeaways": [
      {
        "takeaway_id": "ch_abc123_t001",
        "text": "Vertical integration allowed studios to dominate by controlling the entire supply chain.",
        "proposition_ids": ["ch_abc123_1.2_p001", "ch_abc123_1.2_p003", "ch_abc123_1.3_p002"],
        "dominant_bloom_level": "analyze"
      }
    ]
  }
}
```

## Bloom's Taxonomy Levels

### Propositions (atomic facts)
| Level | Description | Example |
|-------|-------------|---------|
| `remember` | Definitions, dates, facts | "Block booking was banned in 1948." |
| `understand` | Explanations, cause-effect | "Vertical integration eliminated dependency on third parties." |
| `apply` | Concrete examples | "Paramount owned 1,450 theaters by 1948." |
| `analyze` | Comparisons, relationships | "The Big Five owned theaters while the Little Three did not." |

### Key Takeaways (synthesis)
| Level | Description | Example |
|-------|-------------|---------|
| `analyze` | Patterns, relationships | "Theater ownership created a self-reinforcing market advantage." |
| `evaluate` | Judgments, significance | "The Paramount decision proved only partially effective." |

## Project Structure

```
GRAFF/
├── src/
│   ├── app.py                      # FastAPI server
│   ├── models.py                   # Pydantic models
│   └── services/
│       ├── openai_client.py        # GPT-5.2 via responses.create()
│       ├── llm_client.py           # Three-pass analysis functions
│       └── graff_orchestrator.py   # Pipeline orchestration
├── prompts/
│   ├── pass1_structure.txt         # Pass 1 prompt
│   ├── pass2_propositions.txt      # Pass 2 prompt
│   └── pass3_takeaways.txt         # Pass 3 prompt
├── static/
│   ├── index.html                  # Web interface
│   └── js/app.js                   # Client-side logic
└── data/
    └── chapters/                   # Saved analyses
```

## API Endpoints

### POST /chapters/digest
Start analysis of a chapter. Returns immediately with job_id.

```bash
curl -X POST http://localhost:8000/chapters/digest \
  -F file=@chapter.txt \
  -F chapter_id=ch-001
```

### GET /chapters/progress/{job_id}
Stream real-time progress via SSE.

```
data: {"phase":"pass-1","message":"Extracting structure..."}
data: {"phase":"pass-2","message":"Extracting propositions..."}
data: {"phase":"pass-3","message":"Synthesizing takeaways..."}
data: {"phase":"completed","message":"Done! 85 propositions, 12 takeaways"}
```

### GET /chapters/list
List all saved analyses.

### GET /chapters/{filename}
Retrieve a specific analysis.

### DELETE /chapters/{filename}
Delete a saved analysis.

## Processing Pipeline

```
┌─────────────────────────────────────────┐
│         User uploads file               │
└────────────────────┬────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────┐
│    Pass 1: Structure (4K tokens)        │
│    → sections, summary, entities        │
└────────────────────┬────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────┐
│    Pass 2: Propositions (16K tokens)    │
│    → atomic facts with Bloom levels     │
└────────────────────┬────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────┐
│    Pass 3: Takeaways (8K tokens)        │
│    → cross-section synthesis            │
└────────────────────┬────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────┐
│    Save to SQLite + JSON                │
└─────────────────────────────────────────┘
```

## Configuration

```bash
# Required
export OPENAI_API_KEY="sk-..."

# Optional (with defaults)
export OPENAI_MODEL="gpt-5.2"
export OPENAI_MAX_TOKENS="16000"
export OPENAI_TIMEOUT="300"
```

## File Format Support

| Format | Library | Notes |
|--------|---------|-------|
| `.txt` | Built-in | UTF-8 or Latin-1 |
| `.docx` | python-docx | Extracts paragraph text |
| `.pdf` | PyPDF2 | Text-based PDFs only |

**Limits**: 100MB max upload, recommended <50K tokens of text.

## Changes in v0.3.0

### Architecture Overhaul
- **Three-pass pipeline** replaces 5-phase system
- **GPT-5.2** via new `responses.create()` API
- **Cross-section takeaways**: Pass 3 sees ALL propositions for true synthesis

### New Files
- `prompts/pass1_structure.txt` - Structure extraction prompt
- `prompts/pass2_propositions.txt` - Proposition extraction prompt
- `prompts/pass3_takeaways.txt` - Takeaway synthesis prompt

### Removed
- Old phase prompts (phase1_system.txt, phase2_system.txt)
- Section-by-section chunking in proposition extraction
- Separate takeaway generation per section

## Use Cases

GRAFF powers downstream systems:

- **Adaptive Tutoring**: Query propositions by Bloom level for scaffolded learning
- **Knowledge Graphs**: Takeaways link propositions into semantic networks
- **Assessment Generation**: Generate questions from propositions at target cognitive levels
- **Content Gap Analysis**: Identify sections lacking higher-order (analyze/evaluate) content

## License

Proprietary - All rights reserved
