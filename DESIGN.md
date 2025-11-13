# GRAFF v0.3.0 Design Document

**Content-to-Cognition Pipeline: Textbook Chapters → Searchable Knowledge Database**

## Table of Contents
- [Overview](#overview)
- [Architecture](#architecture)
- [Database Schema](#database-schema)
- [Phase Specifications](#phase-specifications)
- [Data Flow](#data-flow)
- [Implementation Progress](#implementation-progress)

---

## Overview

### Purpose
GRAFF v0.3.0 transforms textbook chapters into a **searchable knowledge database** optimized for LLM-powered tutoring systems and human learners.

### Core Value Proposition
**Input:** Textbook chapter (raw text, .docx, or .pdf)
**Process:** 6-phase extraction pipeline
**Output:** Structured database organized by Bloom's Taxonomy
**Use:** LLM tutors query by cognitive level, topic, and unit for adaptive instruction

### Key Design Decisions (Phase 0)
- **Comprehensive extraction:** 30-50 propositions per section (500-1000 per chapter)
- **Bloom-centric organization:** All content tagged by cognitive demand level
- **Auto-tagging:** Topic tags (economic, technological, social, etc.) for multi-dimensional queries
- **Full-text search:** FTS5 indexing for semantic queries
- **Source tracking:** explicit/paraphrased/inferred/synthesized classification
- **Database-first:** Output maps directly to SQL tables (no transformation needed)

---

## Architecture

### Pipeline Flow

```
📚 TEXTBOOK CHAPTER (Input)
│
├─────────────────────────────────────────────────────────────┐
│                                                             │
▼                                                             ▼
┌─────────────────────────────────────────┐    ┌──────────────────────────────────┐
│  PHASE 1: Outline & Unit Extraction     │    │  PHASE 4: Analytical Metadata    │
│  (Structural mapping)                   │    │  (Classification & Tagging)      │
└─────────────────────────────────────────┘    └──────────────────────────────────┘
│                                                             │
│ Extracts:                                                   │ Derives:
│ • Chapter/section hierarchy                                 │ • Subject domain
│ • Text chunks by section                                    │ • Grade level
│ • Keywords per unit                                         │ • Prerequisites
│ • Sequence order                                            │ • Curriculum position
│                                                             │
▼                                                             ▼
DATABASE: content_units                          DATABASE: metadata fields
├─ unit_id                                      ├─ project_id
├─ chapter, section                             ├─ domain
├─ text_snippet                                 ├─ grade_level
├─ keywords                                     └─ related_chapters
├─ sequence_order
└─ depth_level
         │
         │
         ├──────────────────────────────────┐
         │                                  │
         ▼                                  ▼
┌────────────────────────────────┐  ┌─────────────────────────────────┐
│ PHASE 2: Bloom-Tagged          │  │ PHASE 5: Learning Objectives    │
│ Proposition Generation         │  │ & Assessment Elements           │
│ (Multi-level cognitive content)│  │ (Pedagogical scaffolding)       │
└────────────────────────────────┘  └─────────────────────────────────┘
│                                                  │
│ For EACH unit, generates propositions at:        │ Extracts:
│ • REMEMBER (facts, definitions)                  │ • Learning objectives
│ • UNDERSTAND (explanations)                      │ • Assessment questions
│ • APPLY (applications, examples)                 │ • Student activities
│ • ANALYZE (comparisons, causes)                  │ • Discussion prompts
│ • EVALUATE (judgments, critiques)                │
│ • CREATE (novel applications)                    │
│                                                  │
▼                                                  ▼
DATABASE: propositions                DATABASE: learning_objectives
├─ proposition_id                    ├─ objective_id
├─ unit_id (FK)                      ├─ objective_text
├─ proposition_text                  ├─ bloom_level ★
├─ bloom_level ★                     └─ related_units
├─ bloom_verb
└─ evidence_location                 DATABASE: tasks (seed data)
         │                           ├─ task_id
         │                           ├─ unit_id (FK)
         ▼                           ├─ bloom_level ★
┌────────────────────────────────┐   ├─ generated_text
│ PHASE 3: Examples &            │   └─ status
│ Relationships                  │
│ (Supporting content)           │
└────────────────────────────────┘
│
│ Extracts:
│ • Concrete examples
│ • Case studies
│ • Code samples
│ • Concept relationships
│
▼
DATABASE: examples
├─ example_id
├─ unit_id (FK)
├─ example_text
├─ example_type
└─ illustrates_proposition

DATABASE: concept_relationships
├─ parent_unit_id
├─ child_unit_id
└─ relationship_type
    (prerequisite, elaborates, contrasts)

════════════════════════════════════════════════════════════════

ALL PHASES COMPLETE → DATABASE POPULATED
│
├─ content_units (structure)
├─ propositions (Bloom-tagged content) ★
├─ examples (illustrations)
├─ concept_relationships (dependencies)
├─ learning_objectives (goals)
└─ Metadata (domain, grade_level, etc.)

════════════════════════════════════════════════════════════════

                              ↓
┌────────────────────────────────────────────────────────────────┐
│ PHASE 6: Synthesize Navigation Outline                        │
│ (Human-readable chapter guide)                                 │
│                                                                │
│ Input: ALL extracted data from phases 1-5                     │
│ Output: JSON detailed outline with:                           │
│ • Chapter title, headings, subheadings                        │
│ • Section overviews and summaries                             │
│ • Key concepts per section                                    │
│ • Learning path recommendations                               │
│ • Prerequisites and dependencies                              │
│                                                                │
│ Purpose: "Here's how to navigate this chapter as a human"     │
└────────────────────────────────────────────────────────────────┘

════════════════════════════════════════════════════════════════

DOWNSTREAM PROCESSES
│
├─────────────────────┬──────────────────────┬─────────────────────┐
│                     │                      │                     │
▼                     ▼                      ▼                     ▼
TASK GENERATION   LEARNER PATHING    ADAPTIVE TUTORING    COVERAGE TRACKING
│                     │                      │                     │
Uses:                 Uses:                  Uses:                 Monitors:
• propositions        • outline position     • learner_tasks       • Which sections
  + bloom_level       • bloom_level          • bloom_level           have propositions
• prompt_templates    • prerequisites        • performance         • Which Bloom levels
  (by domain)                                  scores                covered per unit
• bloom_verbs        Guides:                                      • Gaps in higher-
                     "Finished Apply         Adapts:                order thinking
Generates:            tasks in 3.2?          "Student failing
• Study questions     → Move to Analyze       Understand?          Flags:
• Practice prompts     tasks in 3.3"          → Drop to            "Section 3.4 has
• Scenarios                                    Remember level"      no Evaluate tasks"
│                     │                      │                     │
▼                     ▼                      ▼                     ▼
DATABASE: tasks   LEARNING PATH UI    🤖 LLM TUTOR          ANALYTICS DASHBOARD
                                      │
                                      Queries by:
                                      • "Get all 'understand'
                                         propositions for Ch 3"
                                      • "Get examples for
                                         unit_3.2"
                                      • "Get prerequisites
                                         for this concept"
                                      │
                                      Uses to:
                                      • Answer questions
                                      • Generate explanations
                                      • Scaffold learning
                                      • Check understanding
                                      • Adapt difficulty

════════════════════════════════════════════════════════════════

LEARNER INTERACTION LOOP
│
Student asks question about Ch 3.2
        ▼
LLM queries: propositions WHERE unit_id='unit_3.2' AND bloom_level='understand'
        ▼
LLM retrieves: examples WHERE unit_id='unit_3.2'
        ▼
LLM generates explanation using proposition + example
        ▼
Student demonstrates understanding
        ▼
LLM queries: tasks WHERE unit_id='unit_3.2' AND bloom_level='apply'
        ▼
LLM presents practice scenario
        ▼
Student completes task → logged to learner_tasks
        ▼
System evaluates: ready for 'analyze' level? → repeat
```

### Key Pipeline Insights

1. **Phases 1, 3, 5** extract content → populate core database tables
2. **Phase 4** classifies and tags → enables smart filtering and querying
3. **Phase 2** is the cognitive core → generates Bloom-tagged propositions at multiple cognitive levels
4. **Phase 6** synthesizes → creates human-readable navigation guide
5. **★ Bloom's Taxonomy** flows through the entire pipeline as the organizing principle
6. **LLM Tutor** queries the database by Bloom level + unit + domain for adaptive instruction
7. **Learner progression** is guided by Bloom hierarchy combined with outline position

---

## Database Schema

### Core Tables

**See `schema.sql` for complete definitions.**

Key tables and their purpose:

#### Reference Data
- **bloom_verbs**: 70+ verbs with definitions and example question stems
  - Enables automatic verb selection and question generation

#### Content Structure
- **content_units**: Hierarchical chapter organization
  - Enables navigation and unit-based queries
  - Foreign key anchor for all other content

#### Knowledge Atoms
- **propositions**: Bloom-tagged factual statements
  - Core knowledge extraction (500-1000 per chapter)
  - Full-text search enabled (FTS5)
  - Multi-dimensional tagging (Bloom + topic)

#### Supporting Content
- **examples**: Concrete illustrations linked to propositions
- **concept_relationships**: Prerequisites, elaborations, contrasts
- **learning_objectives**: Bloom-tagged learning goals
- **prompt_templates**: Task generation templates by Bloom level + domain
- **tasks**: Generated questions/prompts

#### Metadata
- **content_metadata**: Domain, grade level, curriculum positioning

#### Learner Tracking (Future)
- **learner_tasks**: Performance tracking for adaptive tutoring

### Database Design Principles

1. **Bloom-first**: Cognitive level is a first-class dimension
2. **Searchable**: Full-text indexes on propositions
3. **Queryable**: Multi-dimensional (Bloom × topic × unit × domain)
4. **Relational**: Foreign keys maintain data integrity
5. **Database-ready**: JSON output maps directly to SQL

---

## Phase Specifications

### Phase 0: Foundation (COMPLETED ✅)

**Purpose:** Design database schema and establish reference data

**Deliverables:**
- `schema.sql`: Complete database schema (10+ tables, indexes, triggers)
- `seed_bloom_verbs.sql`: 70+ Bloom verbs with definitions
- Design decisions documented (comprehensive extraction, auto-tagging, source tracking)

**Status:** Pushed to GitHub (tag: `v0.3.0-phase0`)

---

### Phase 1: Outline & Unit Extraction (COMPLETED ✅)

**Purpose:** Map chapter hierarchical structure and create queryable content units

**Input:** Chapter text (raw, .docx, or .pdf)

**Output:** `content_units` array
```json
{
  "content_units": [
    {
      "unit_id": "unit_1_2",
      "chapter": "1",
      "section": "1.2",
      "parent_unit_id": "unit_1",
      "depth_level": 1,
      "sequence_order": 2,
      "text_snippet": "THE IMPORTANCE OF COMMUNICATION IN OUR LIVES...",
      "keywords": ["communication", "television", "media addiction", "leisure time"],
      "unit_type": "section"
    }
  ]
}
```

**Prompts:**
- System Prompt: Defines role as "content structuralist"
- Reading Strategy: 5-step process (structure → hierarchy → snippets → keywords → classification)
- Schema Guide: Field-by-field specifications with examples
- Example Output: 9 content units from film industry chapter

**Test Results:**
- Tested on Chapter 1 "YOUR FOUR WORLDS" (DMC v25)
- Successfully extracted 9 content units (1 chapter + 8 sections)
- Keywords extracted: "media addiction", "four worlds", "communication models"
- Output is database-ready (maps directly to content_units table)

**Status:** Pushed to GitHub (tag: `v0.3.0-phase1`)

**Files:**
- `src/services/prompts.py`: PHASE_1 prompts redesigned
- `test_phase1.py`: Standalone test script
- `test_phase1_output.json`: Test results on actual chapter

---

### Phase 2: Bloom-Tagged Proposition Generation (DESIGNED, NOT IMPLEMENTED)

**Purpose:** Extract comprehensive factual statements tagged by Bloom's Taxonomy cognitive levels

**Input:**
- Chapter text
- Phase 1 output (content_units with unit_ids)

**Output:** `propositions` array
```json
{
  "propositions": [
    {
      "proposition_id": "prop_1_2_1",
      "unit_id": "unit_1_2",
      "proposition_text": "Americans spend about 5 hours per day on leisure activities according to the U.S. Bureau of Labor Statistics",
      "bloom_level": "remember",
      "bloom_verb": "recall",
      "evidence_location": "Section 1.2, paragraph 4",
      "source_type": "explicit",
      "tags": ["leisure time", "statistics", "media consumption", "demographics"]
    }
  ]
}
```

**Extraction Target:** 30-50 propositions per section (comprehensive but not redundant)

**Expected Distribution per Section:**
- Remember: 20-25% (pure facts, definitions, statistics)
- Understand: 30-35% (explanations, descriptions)
- Apply: 10-15% (examples, applications)
- Analyze: 20-25% (comparisons, relationships, causes)
- Evaluate: 10-15% (judgments, assessments)
- Create: 5-10% (novel applications, often inferred/synthesized)

#### Implementation Plan

**1. System Prompt (15-20 min)**

Components:
- Identity & Role: "Expert knowledge extractor specializing in Bloom's Taxonomy"
- What is a Proposition: Definition and examples (good vs bad)
- Extraction Philosophy: Comprehensive, not redundant, multi-level, evidence-based
- Bloom's Taxonomy Framework: Overview of all 6 levels
- Quality Standards: Completeness, precision, cognitive accuracy, topic relevance
- Critical Rules: 7 operational rules
- Anti-Patterns: What NOT to do (redundancy, combining facts, vagueness, hallucination)

**2. Reading Strategy (30-40 min)** ← BIGGEST COMPONENT

Structure:
- **Step 1:** Read for comprehension first
- **Step 2:** Extract by Bloom level
  - **2A: REMEMBER** (facts, dates, statistics, definitions)
    - What to scan for
    - Question prompts
    - 4 examples
    - Bloom verbs
    - Common mistakes to avoid
  - **2B: UNDERSTAND** (explanations, descriptions)
    - What to scan for
    - Question prompts
    - 4 examples
    - Bloom verbs
    - Common mistakes to avoid
  - **2C: APPLY** (applications, examples in action)
    - What to scan for
    - Question prompts
    - 4 examples
    - Bloom verbs
    - Common mistakes to avoid
  - **2D: ANALYZE** (comparisons, causes, relationships)
    - What to scan for
    - Question prompts
    - 4 examples
    - Bloom verbs
    - Common mistakes to avoid
  - **2E: EVALUATE** (judgments, critiques, assessments)
    - What to scan for
    - Question prompts
    - 4 examples
    - Bloom verbs
    - Common mistakes to avoid
  - **2F: CREATE** (novel applications, hypotheticals)
    - What to scan for
    - Question prompts
    - 4 examples
    - Bloom verbs
    - Source type notice (often synthesized/inferred)
    - Common mistakes to avoid
- **Step 3:** Assign Bloom verb (select appropriate action word)
- **Step 4:** Assign topic tags (2-5 domain-specific tags)
- **Step 5:** Determine source type (explicit/paraphrased/inferred/synthesized)
- **Step 6:** Link evidence (exact text location)
- Extraction checklist

**3. Schema Guide (20-30 min)**

Field definitions with examples:
- `proposition_id`: Format, examples, constraints
- `unit_id`: Foreign key to content_units
- `proposition_text`: Complete statement, examples of good/bad
- `bloom_level`: Enum validation, lowercase only
- `bloom_verb`: Must match bloom_level
- `evidence_location`: Specific format requirements
- `source_type`: Definitions of each type
- `tags`: 2-5 specific domain tags, not generic

Completeness expectations:
- 30-50 propositions per section
- Bloom level distribution guidance
- Validation rules checklist
- Common data errors to avoid

**4. Example Output (30-45 min)**

15-20 sample propositions demonstrating:
- All 6 Bloom levels represented
- Different source types (mostly explicit, some inferred/synthesized)
- Good proposition text (complete, clear, testable)
- Appropriate Bloom verbs matched to levels
- Relevant topic tags
- Proper evidence linking

**5. Negative Prompts (18-27 min)**

Anti-patterns to avoid:
- Creating redundant propositions
- Combining multiple facts
- Being too vague or too granular
- Hallucinating facts
- Using generic tags
- Misclassifying Bloom levels
- Providing vague evidence locations
- Wrong data types/formats

**6. Helper Function (10-15 min)**

```python
def get_phase_2_prompts(chapter_text: str, phase_1_output: Dict[str, Any]) -> Dict[str, str]:
    """
    Get system and user prompts for Phase 2.
    Includes content_units from Phase 1 for unit_id reference.
    """
```

**7. Test & Validate (15-20 min)**

Create `test_phase2.py`:
- Run Phase 1 first to get content_units
- Run Phase 2 with Phase 1 context
- Validate: ~30-50 propositions per section, all Bloom levels present, unit_ids match

**Total Estimated Time:** 1.5-2 hours

**Status:** Fully planned, ready to implement

---

### Phase 3: Examples & Relationships (TO BE DESIGNED)

**Purpose:** Extract concrete examples and map concept relationships

**Planned Output:**
- `examples` array: Concrete illustrations linked to propositions/units
- `concept_relationships` array: Prerequisites, elaborations, contrasts

**Status:** Not yet designed

---

### Phase 4: Analytical Metadata (TO BE UPDATED)

**Purpose:** Classify and tag content for filtering and curriculum positioning

**Planned Output:**
- Subject domain
- Grade level
- Prerequisites
- Curriculum unit
- Related chapters

**Status:** Needs updating for new schema

---

### Phase 5: Learning Objectives & Assessment (TO BE REDESIGNED)

**Purpose:** Extract pedagogical scaffolding with Bloom tagging

**Planned Output:**
- Learning objectives (Bloom-tagged)
- Assessment questions (Bloom-tagged)
- Student activities
- Discussion prompts

**Status:** Needs redesign for Bloom-centric approach

---

### Phase 6: Navigation Outline Synthesis (IDENTIFIED FOR LATER)

**Purpose:** Create human-readable comprehensive chapter outline using ALL extracted data

**When:** AFTER phases 1-5 complete (synthesis phase)

**Input:**
- content_units (Phase 1)
- propositions grouped by unit and Bloom level (Phase 2)
- examples (Phase 3)
- metadata (Phase 4)
- learning_objectives (Phase 5)

**Output:** JSON detailed outline with:
- Chapter title and structure
- Section headings and subheadings
- Section overviews and content summaries
- Key concepts per section (from propositions)
- Examples referenced
- Learning path recommendations
- Prerequisites and dependencies
- Bloom-level distribution per section

**Format:** JSON (structured, programmatically usable)

**Purpose Statement:** "Here's how to navigate this chapter as a human"

**Status:** Identified, will design when we reach it

---

## Data Flow

### JSON → Database Mapping

**Phase 1 Output → content_units table:**
```json
{"unit_id": "unit_1_2", "chapter": "1", "section": "1.2", ...}
↓
INSERT INTO content_units (unit_id, chapter, section, ...) VALUES (...)
```

**Phase 2 Output → propositions table:**
```json
{"proposition_id": "prop_1_2_1", "unit_id": "unit_1_2", "bloom_level": "remember", ...}
↓
INSERT INTO propositions (proposition_id, unit_id, bloom_level, ...) VALUES (...)
```

### Database Query Examples

**Example 1: Get all 'analyze' propositions for Section 1.2**
```sql
SELECT p.proposition_text, p.tags, p.evidence_location
FROM propositions p
JOIN content_units c ON p.unit_id = c.unit_id
WHERE c.section = '1.2' AND p.bloom_level = 'analyze';
```

**Example 2: Get propositions about "media addiction" at understand level**
```sql
SELECT proposition_text, evidence_location
FROM propositions_fts
WHERE propositions_fts MATCH 'media addiction'
AND bloom_level = 'understand';
```

**Example 3: Get learning path for Chapter 1 (ordered by sequence)**
```sql
SELECT unit_id, section, text_snippet
FROM content_units
WHERE chapter = '1'
ORDER BY depth_level, sequence_order;
```

**Example 4: Get all content for a unit (propositions + examples)**
```sql
SELECT
  p.proposition_text,
  p.bloom_level,
  e.example_text
FROM propositions p
LEFT JOIN examples e ON p.proposition_id = e.proposition_id
WHERE p.unit_id = 'unit_1_2';
```

---

## Implementation Progress

### Completed ✅

- [x] **Phase 0:** Database schema design
  - schema.sql created
  - seed_bloom_verbs.sql created
  - Pushed to GitHub (v0.3.0-phase0)

- [x] **Phase 1:** Outline & Unit Extraction
  - Prompts redesigned (system, strategy, schema, example)
  - Test script created (test_phase1.py)
  - Tested on actual chapter (9 units extracted)
  - Pushed to GitHub (v0.3.0-phase1)

### In Progress ⏳

- [ ] **Phase 2:** Bloom-Tagged Proposition Generation
  - [x] Fully planned (detailed implementation outline)
  - [ ] System prompt
  - [ ] Reading strategy
  - [ ] Schema guide
  - [ ] Example output
  - [ ] Negative prompts
  - [ ] Helper function
  - [ ] Test script

### Pending 📋

- [ ] **Phase 3:** Examples & Relationships extraction
- [ ] **Phase 4:** Analytical Metadata updates
- [ ] **Phase 5:** Learning Objectives & Assessment redesign
- [ ] **Phase 6:** Navigation Outline Synthesis
- [ ] **Pydantic Models:** Update for new schema structures
- [ ] **Database Implementation:** Execute schema.sql, create database
- [ ] **Parser:** Build JSON → database insertion logic
- [ ] **End-to-End Testing:** Full pipeline validation

### Next Steps

1. **Immediate:** Implement Phase 2 prompts (~1.5-2 hours)
2. **Then:** Test Phase 2 on actual chapter
3. **Then:** Design Phases 3-5
4. **Then:** Update Pydantic models
5. **Then:** Build database and parser
6. **Finally:** End-to-end testing and Phase 6 synthesis

---

## Document History

- **Created:** 2025-01-08
- **Last Updated:** 2025-01-08
- **Version:** v0.3.0-draft
- **Status:** Design specification (implementation in progress)

---

**Next Review:** After Phase 2 implementation complete
