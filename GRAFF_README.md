# GRAFF - Chapter Analysis Pipeline

**G**ranular **R**etrieval **A**nd **F**actual **F**ramework for educational content analysis

## Overview

GRAFF is a 2-phase AI-powered pipeline that transforms textbook chapters into a searchable knowledge database organized by Bloom's Taxonomy cognitive levels.

**What it does:**
- Extracts ALL atomic facts (propositions) from textbook chapters
- Tags each fact with appropriate Bloom cognitive level
- Synthesizes higher-order learning insights (key takeaways)
- Stores everything in a queryable SQLite database

**Why it matters:**
- Enables adaptive tutoring systems to retrieve facts by cognitive level
- Supports learner progression through Bloom's hierarchy
- Creates comprehensive, searchable knowledge bases from textbooks
- Enforces pedagogically sound categorization of learning content

---

## Architecture

### 2-Phase Pipeline

```
┌─────────────────────────────────────────┐
│  INPUT: Chapter Text (.txt/.docx/.pdf) │
└──────────────────┬──────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────┐
│  PHASE 1: Chapter Comprehension        │
│  ────────────────────────────────────  │
│  Extracts:                              │
│  • Summary (1 paragraph)                │
│  • Sections (hierarchical structure)    │
│  • Entities (people, orgs, concepts)    │
│  • Keywords (domain-specific terms)     │
└──────────────────┬──────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────┐
│  PHASE 2: Proposition Extraction        │
│  ────────────────────────────────────  │
│  Extracts:                              │
│  • ALL atomic facts (comprehensive)     │
│  • Bloom tags (remember/understand/     │
│    apply/analyze)                       │
│  • Evidence locations                   │
│  • Domain tags                          │
│                                         │
│  Synthesizes:                           │
│  • Key takeaways (analyze/evaluate)     │
│  • Links to source propositions         │
└──────────────────┬──────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────┐
│  VALIDATION: Pydantic Schema            │
│  • Bloom constraints enforced           │
│  • Data types validated                 │
│  • Referential integrity checked        │
└──────────────────┬──────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────┐
│  STORAGE: SQLite Database (graff.db)    │
│  • 9 tables with FTS5 search            │
│  • Bloom-indexed queries                │
│  • Full-text proposition search         │
└─────────────────────────────────────────┘
```

---

## Bloom's Taxonomy Mapping

GRAFF uses Bloom's Taxonomy as the organizing principle for ALL extracted content.

### Propositions (Micro Layer)

**Allowed Bloom Levels:** `remember`, `understand`, `apply`, `analyze`

Propositions are atomic facts extracted FROM the text. They represent what the text SAYS, not what learners should DO.

| Bloom Level | Definition | Example Proposition |
|-------------|------------|---------------------|
| **Remember** | Recall facts, terms, definitions | "Vertical integration refers to studio ownership of production, distribution, and exhibition." |
| **Understand** | Explain concepts, describe relationships | "Vertical integration allowed studios to control the entire film supply chain, eliminating dependency on third parties." |
| **Apply** | Use concepts in concrete examples | "Paramount demonstrated vertical integration by owning production facilities, a distribution network, and 1,450 theaters." |
| **Analyze** | Compare, contrast, examine causes | "Unlike the Little Three studios, the Big Five's theater ownership gave them guaranteed exhibition outlets and greater market leverage." |

**NOT ALLOWED:** `evaluate`, `create` - These represent learner cognition, not textbook content.

### Key Takeaways (Meso Layer)

**Allowed Bloom Levels:** `analyze`, `evaluate`

Takeaways are synthesized insights derived BY combining multiple propositions.

| Bloom Level | Definition | Example Takeaway |
|-------------|------------|------------------|
| **Analyze** | Examine relationships, patterns, structures | "Vertical integration created a self-reinforcing advantage: theater ownership guaranteed distribution, which generated revenue to fund more production." |
| **Evaluate** | Judge significance, assess effectiveness | "The Paramount decision proved only partially effective, as studios retained control over production and distribution even after divesting their theaters." |

**NOT ALLOWED:** `remember`, `understand`, `apply` (too low-level), `create` (reserved for future activity generation)

---

## Database Schema

**File:** `src/db/schema.sql`

### Core Tables

| Table | Purpose | Key Fields |
|-------|---------|------------|
| `chapters` | Chapter metadata | `chapter_id`, `book_id`, `chapter_title`, `summary` |
| `sections` | Hierarchical structure | `unit_id`, `title`, `level`, `parent_unit_id` |
| `entities` | Key people/concepts | `name`, `type` (person, concept, org, etc.) |
| `keywords` | Domain-specific terms | `keyword` |
| **`propositions`** | **Atomic facts** | **`proposition_text`, `bloom_level`, `bloom_verb`, `evidence_location`, `tags`** |
| `proposition_tags` | Proposition tagging | `proposition_id`, `tag` |
| **`key_takeaways`** | **Synthesized insights** | **`text`, `proposition_ids`, `dominant_bloom_level`** |
| `takeaway_propositions` | Links takeaways → propositions | `takeaway_id`, `proposition_id` |
| `takeaway_tags` | Takeaway tagging | `takeaway_id`, `tag` |

### Full-Text Search

```sql
-- FTS5 virtual table for proposition search
CREATE VIRTUAL TABLE propositions_fts USING fts5(
  proposition_id UNINDEXED,
  proposition_text
);

-- Example: Search propositions about "vertical integration"
SELECT * FROM propositions_fts WHERE propositions_fts MATCH 'vertical integration';
```

### Query Examples

**Get all "analyze" level propositions for a chapter:**
```sql
SELECT proposition_text, evidence_location, tags
FROM propositions
WHERE chapter_id = 'ch01' AND bloom_level = 'analyze';
```

**Get key takeaways with their source propositions:**
```sql
SELECT
  kt.text,
  GROUP_CONCAT(p.proposition_text, ' | ') as supporting_facts
FROM key_takeaways kt
JOIN takeaway_propositions tp ON kt.id = tp.takeaway_id
JOIN propositions p ON tp.proposition_id = p.id
WHERE kt.chapter_id = 'ch01'
GROUP BY kt.id;
```

**Get Bloom distribution for a chapter:**
```sql
SELECT bloom_level, COUNT(*) as count
FROM propositions
WHERE chapter_id = 'ch01'
GROUP BY bloom_level;
```

---

## API Endpoints

**Base URL:** `http://localhost:8000`

### Upload & Process

**`POST /chapters/digest`**
- Upload chapter file (.txt, .docx, or .pdf)
- Returns `job_id` for progress tracking
- Runs GRAFF 2-phase pipeline asynchronously

**`GET /chapters/progress/{job_id}`**
- Server-Sent Events (SSE) stream
- Real-time progress updates for Phase 1 and Phase 2

### Retrieve Data

**`GET /chapters/list`**
- List all processed chapters
- Returns: `chapter_id`, `chapter_title`, `proposition_count`, `takeaway_count`, `created_at`

**`GET /chapters/{chapter_id}`**
- Get complete chapter analysis
- Returns full ChapterAnalysis object (Phase 1 + Phase 2)

**`GET /chapters/{chapter_id}/propositions?bloom_level=analyze`**
- Get propositions for a chapter
- Optional Bloom filter: `?bloom_level=remember|understand|apply|analyze`
- Returns propositions with Bloom distribution stats

**`DELETE /chapters/{chapter_id}`**
- Delete a chapter and all associated data

---

## Installation & Setup

### Prerequisites
- Python 3.10+
- OpenAI API key (for GPT-4)

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Set OpenAI API Key
```bash
export OPENAI_API_KEY="your-api-key-here"
```

### Initialize Database
```bash
python -c "from src.db import init_database; init_database()"
```

---

## Usage

### 1. CLI Test (Quick Start)

Run the test script to validate the pipeline:

```bash
python test_graff_pipeline.py
```

This will:
1. Initialize the database
2. Process a sample chapter
3. Extract propositions and takeaways
4. Validate Bloom constraints
5. Test database persistence and retrieval

### 2. API Server

Start the FastAPI server:

```bash
python -m uvicorn src.app:app --reload
```

Visit: `http://localhost:8000` for the web interface

### 3. Programmatic Usage

```python
from src.services.graff_orchestrator import quick_digest

# Process a chapter
chapter = quick_digest(
    text="Your chapter text here...",
    chapter_title="Introduction to Film History",
    book_id="film101"
)

# Access results
print(f"Propositions: {len(chapter.phase2.propositions)}")
print(f"Takeaways: {len(chapter.phase2.key_takeaways)}")
print(f"Bloom distribution: {chapter.get_bloom_distribution()}")

# Get specific Bloom level
remember_facts = [p for p in chapter.phase2.propositions if p.bloom_level == "remember"]
```

---

## File Structure

```
doc_digester/
├── src/
│   ├── models.py                  # Pydantic models (ChapterAnalysis, Proposition, etc.)
│   ├── app.py                     # FastAPI web server
│   ├── db/
│   │   ├── schema.sql            # SQLite database schema
│   │   ├── connection.py         # Database connection & persistence
│   │   └── __init__.py
│   └── services/
│       ├── llm_client.py         # LLM integration (run_phase_1, run_phase_2)
│       ├── graff_orchestrator.py # Pipeline orchestration
│       └── openai_client.py      # OpenAI API wrapper
├── prompts/
│   ├── phase1_system.txt         # Phase 1 system prompt (20KB)
│   └── phase2_system.txt         # Phase 2 system prompt (30KB)
├── static/
│   ├── index.html                # Web interface
│   └── js/app.js                 # Frontend JavaScript
├── test_graff_pipeline.py        # End-to-end test script
├── graff.db                      # SQLite database (created on first run)
└── README.md                     # This file
```

---

## Prompt Engineering

GRAFF uses extensive, detailed prompts to ensure high-quality extraction.

### Phase 1 Prompt (`prompts/phase1_system.txt`)
- **Purpose:** Extract chapter structure and comprehension
- **Length:** ~20KB (very detailed instructions)
- **Key sections:**
  - Output format specification
  - Field-by-field requirements
  - Reading strategy (3-pass approach)
  - Quality standards
  - Examples

### Phase 2 Prompt (`prompts/phase2_system.txt`)
- **Purpose:** Extract comprehensive propositions + synthesize takeaways
- **Length:** ~30KB (most detailed)
- **Key sections:**
  - Bloom taxonomy constraints (critical!)
  - Proposition vs. Takeaway definitions
  - Extraction philosophy (comprehensive, not selective)
  - Bloom level guide for each level (remember through analyze)
  - Synthesis strategy for takeaways
  - Anti-patterns to avoid
  - Quality checklist

---

## Data Flow Example

**Input:** Film history chapter (10,000 words)

**Phase 1 Output:**
```json
{
  "summary": "This chapter examines the classical Hollywood studio system...",
  "sections": [
    {"unit_id": "1.1", "title": "Introduction", "level": 1},
    {"unit_id": "1.2", "title": "Vertical Integration", "level": 1},
    {"unit_id": "1.2.1", "title": "Production Control", "level": 2, "parent_unit_id": "1.2"}
  ],
  "key_entities": [
    {"name": "Paramount Pictures", "type": "organization"},
    {"name": "vertical integration", "type": "concept"}
  ],
  "keywords": ["studio system", "vertical integration", "block booking"]
}
```

**Phase 2 Output:**
```json
{
  "propositions": [
    {
      "proposition_id": "ch01_1.2_p001",
      "unit_id": "1.2",
      "proposition_text": "Vertical integration refers to studio ownership of production, distribution, and exhibition.",
      "bloom_level": "remember",
      "bloom_verb": "define",
      "evidence_location": "Section 1.2, paragraph 2",
      "source_type": "explicit",
      "tags": ["vertical integration", "studio system"]
    },
    {
      "proposition_id": "ch01_1.2_p002",
      "proposition_text": "Unlike the Little Three, the Big Five's theater ownership gave them guaranteed exhibition outlets.",
      "bloom_level": "analyze",
      "bloom_verb": "contrast",
      "evidence_location": "Section 1.2, paragraph 5",
      "source_type": "paraphrased",
      "tags": ["Big Five", "market power", "comparison"]
    }
  ],
  "key_takeaways": [
    {
      "takeaway_id": "ch01_t001",
      "text": "Vertical integration allowed the Big Five to dominate the industry by creating insurmountable barriers for independent producers.",
      "proposition_ids": ["ch01_1.2_p001", "ch01_1.2_p002", "ch01_1.2_p005"],
      "dominant_bloom_level": "analyze",
      "tags": ["industry structure", "market dominance"]
    }
  ]
}
```

**Database:** Stored in `graff.db` with full-text search and Bloom indexing

---

## Validation & Quality Control

### Automatic Validation (Pydantic)
- All outputs validated against strict schema
- Bloom level constraints enforced
- Required fields checked
- Data types verified

### Bloom Constraint Enforcement
- **Propositions:** MUST be `remember`, `understand`, `apply`, or `analyze`
- **Takeaways:** MUST be `analyze` or `evaluate` (or null)
- Invalid Bloom levels cause validation failure

### Referential Integrity
- All `unit_id` references must exist in Phase 1 sections
- All `proposition_ids` in takeaways must reference valid propositions
- Foreign key constraints enforced in database

---

## Performance

**Typical Processing Time:**
- Phase 1: 10-20 seconds (chapter comprehension)
- Phase 2: 30-120 seconds (proposition extraction - depends on chapter length)
- **Total:** ~1-2 minutes for 5,000-word chapter

**Extraction Capacity:**
- No artificial limits on proposition count
- Typical output: 100-500 propositions per dense chapter
- Key takeaways: 10-30 per chapter

**Cost (OpenAI API):**
- Phase 1: ~$0.10-0.20 per chapter
- Phase 2: ~$0.30-0.60 per chapter (higher due to comprehensive extraction)
- **Total:** ~$0.40-0.80 per chapter using GPT-4

---

## Troubleshooting

**Issue:** "OpenAI API key not found"
```bash
export OPENAI_API_KEY="your-key-here"
```

**Issue:** "Database not initialized"
```bash
python -c "from src.db import init_database; init_database()"
```

**Issue:** "Validation error: Invalid Bloom level"
- Check Phase 2 prompt constraints
- Ensure propositions only use: remember, understand, apply, analyze
- Ensure takeaways only use: analyze, evaluate

**Issue:** "Too few propositions extracted"
- Check Phase 2 prompt emphasizes "comprehensive extraction"
- Increase max_tokens in `llm_client.py` (currently 16000)
- Review chapter text quality

---

## Future Enhancements

### Planned Features
- [ ] Multi-chapter knowledge graphs
- [ ] Cross-chapter proposition linking
- [ ] Learner progression tracking
- [ ] Adaptive task generation (Create level)
- [ ] True/False question generation
- [ ] Multiple-choice question generation
- [ ] Frontend UI updates for GRAFF display

### Research Directions
- Automatic prerequisite detection
- Concept difficulty scoring
- Optimal learning path recommendation
- Knowledge gap identification

---

## Credits

**Architecture:** GRAFF 2-phase pipeline with Bloom's Taxonomy constraints

**Technology Stack:**
- FastAPI (web framework)
- Pydantic (schema validation)
- SQLite with FTS5 (database + full-text search)
- OpenAI GPT-4 (LLM extraction)

**Design Principles:**
- Comprehensive extraction (not selective)
- Bloom-first organization
- Database-ready output
- Pedagogically sound categorization

---

## License

[Your license here]

## Support

For issues or questions, please open an issue on the GitHub repository.

---

**Last Updated:** 2025-01-13
**Version:** GRAFF 1.0
