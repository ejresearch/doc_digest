-- GRAFF v0.3.0 Database Schema
-- Content-to-Cognition Pipeline: Textbook chapters → Searchable knowledge database
-- Organized around Bloom's Taxonomy for LLM-powered tutoring and prompt engineering

-- ============================================================================
-- REFERENCE TABLES
-- ============================================================================

-- Bloom's Taxonomy verbs with definitions (reference data)
CREATE TABLE bloom_verbs (
    verb_id INTEGER PRIMARY KEY AUTOINCREMENT,
    bloom_level TEXT NOT NULL CHECK(bloom_level IN ('remember', 'understand', 'apply', 'analyze', 'evaluate', 'create')),
    verb TEXT NOT NULL,
    definition TEXT NOT NULL,
    example_question_stem TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(bloom_level, verb)
);

-- Create index for fast lookup by level
CREATE INDEX idx_bloom_verbs_level ON bloom_verbs(bloom_level);

-- ============================================================================
-- CONTENT STRUCTURE TABLES
-- ============================================================================

-- Content units: structural chunks of textbook content
CREATE TABLE content_units (
    unit_id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    chapter TEXT,
    section TEXT,
    parent_unit_id TEXT REFERENCES content_units(unit_id),
    depth_level INTEGER,  -- 0=chapter, 1=section, 2=subsection, etc.
    sequence_order INTEGER,  -- Order within parent
    text_snippet TEXT NOT NULL,
    keywords TEXT,  -- JSON array: ["vertical integration", "block booking"]
    unit_type TEXT CHECK(unit_type IN ('chapter', 'section', 'subsection', 'concept', 'activity')),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_content_units_project ON content_units(project_id);
CREATE INDEX idx_content_units_chapter ON content_units(chapter);
CREATE INDEX idx_content_units_parent ON content_units(parent_unit_id);

-- ============================================================================
-- PROPOSITIONS (Core Knowledge Atoms)
-- ============================================================================

-- Propositions: comprehensive factual statements tagged by Bloom level
CREATE TABLE propositions (
    proposition_id TEXT PRIMARY KEY,
    unit_id TEXT NOT NULL REFERENCES content_units(unit_id),
    proposition_text TEXT NOT NULL,
    bloom_level TEXT NOT NULL CHECK(bloom_level IN ('remember', 'understand', 'apply', 'analyze', 'evaluate', 'create')),
    bloom_verb TEXT NOT NULL,
    evidence_location TEXT,  -- "Section 3.2, paragraph 4"
    source_type TEXT DEFAULT 'explicit' CHECK(source_type IN ('explicit', 'paraphrased', 'inferred', 'synthesized')),
    -- explicit: directly quoted or stated
    -- paraphrased: restated from clear textual evidence
    -- inferred: derived from strong textual evidence
    -- synthesized: created by connecting multiple sources or extrapolating patterns
    tags TEXT,  -- JSON array: ["economic", "technological", "regulatory"]
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_propositions_unit ON propositions(unit_id);
CREATE INDEX idx_propositions_bloom ON propositions(bloom_level);
CREATE INDEX idx_propositions_unit_bloom ON propositions(unit_id, bloom_level);

-- Full-text search for propositions (enables semantic querying)
CREATE VIRTUAL TABLE propositions_fts USING fts5(
    proposition_id UNINDEXED,
    proposition_text,
    tags,
    content='propositions'
);

-- Trigger to keep FTS index in sync
CREATE TRIGGER propositions_ai AFTER INSERT ON propositions BEGIN
  INSERT INTO propositions_fts(proposition_id, proposition_text, tags)
  VALUES (new.proposition_id, new.proposition_text, new.tags);
END;

CREATE TRIGGER propositions_ad AFTER DELETE ON propositions BEGIN
  DELETE FROM propositions_fts WHERE proposition_id = old.proposition_id;
END;

CREATE TRIGGER propositions_au AFTER UPDATE ON propositions BEGIN
  UPDATE propositions_fts
  SET proposition_text = new.proposition_text, tags = new.tags
  WHERE proposition_id = old.proposition_id;
END;

-- ============================================================================
-- SUPPORTING CONTENT
-- ============================================================================

-- Examples that illustrate propositions/concepts
CREATE TABLE examples (
    example_id TEXT PRIMARY KEY,
    unit_id TEXT NOT NULL REFERENCES content_units(unit_id),
    proposition_id TEXT REFERENCES propositions(proposition_id),
    example_text TEXT NOT NULL,
    example_type TEXT CHECK(example_type IN ('historical_case', 'code_sample', 'analogy', 'case_study', 'scenario', 'diagram_reference', 'data_point')),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_examples_unit ON examples(unit_id);
CREATE INDEX idx_examples_proposition ON examples(proposition_id);

-- Relationships between concepts/units (prerequisite chains, elaborations)
CREATE TABLE concept_relationships (
    relationship_id INTEGER PRIMARY KEY AUTOINCREMENT,
    parent_unit_id TEXT NOT NULL REFERENCES content_units(unit_id),
    child_unit_id TEXT NOT NULL REFERENCES content_units(unit_id),
    relationship_type TEXT NOT NULL CHECK(relationship_type IN ('prerequisite', 'elaborates', 'contrasts', 'applies', 'exemplifies')),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(parent_unit_id, child_unit_id, relationship_type)
);

CREATE INDEX idx_relationships_parent ON concept_relationships(parent_unit_id);
CREATE INDEX idx_relationships_child ON concept_relationships(child_unit_id);

-- ============================================================================
-- PEDAGOGICAL SCAFFOLDING
-- ============================================================================

-- Learning objectives with Bloom tagging
CREATE TABLE learning_objectives (
    objective_id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    chapter TEXT,
    objective_text TEXT NOT NULL,
    bloom_level TEXT NOT NULL CHECK(bloom_level IN ('remember', 'understand', 'apply', 'analyze', 'evaluate', 'create')),
    related_units TEXT,  -- JSON array of unit_ids
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_objectives_project ON learning_objectives(project_id);
CREATE INDEX idx_objectives_chapter ON learning_objectives(chapter);
CREATE INDEX idx_objectives_bloom ON learning_objectives(bloom_level);

-- Prompt templates for task generation (keyed by Bloom level and domain)
CREATE TABLE prompt_templates (
    template_id INTEGER PRIMARY KEY AUTOINCREMENT,
    bloom_level TEXT NOT NULL CHECK(bloom_level IN ('remember', 'understand', 'apply', 'analyze', 'evaluate', 'create')),
    domain TEXT,  -- "FilmHistory", "PythonProgramming", etc.
    prompt_template TEXT NOT NULL,  -- "Using {concept}, how would you {action} in {scenario}?"
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_templates_bloom ON prompt_templates(bloom_level);
CREATE INDEX idx_templates_domain ON prompt_templates(domain);
CREATE INDEX idx_templates_bloom_domain ON prompt_templates(bloom_level, domain);

-- Tasks generated for learners (seed data from GRAFF, expanded by tutoring system)
CREATE TABLE tasks (
    task_id TEXT PRIMARY KEY,
    unit_id TEXT REFERENCES content_units(unit_id),
    proposition_id TEXT REFERENCES propositions(proposition_id),
    bloom_level TEXT NOT NULL CHECK(bloom_level IN ('remember', 'understand', 'apply', 'analyze', 'evaluate', 'create')),
    prompt_template_id INTEGER REFERENCES prompt_templates(template_id),
    generated_text TEXT,
    status TEXT DEFAULT 'pending' CHECK(status IN ('pending', 'reviewed', 'live', 'archived')),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_tasks_unit ON tasks(unit_id);
CREATE INDEX idx_tasks_bloom ON tasks(bloom_level);
CREATE INDEX idx_tasks_status ON tasks(status);

-- ============================================================================
-- METADATA (Classification & Tagging)
-- ============================================================================

-- Content metadata (output from Phase 4: Analytical Metadata)
CREATE TABLE content_metadata (
    metadata_id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id TEXT NOT NULL UNIQUE,
    chapter TEXT,
    subject_domain TEXT,  -- "Computer Science - Programming - Python"
    curriculum_unit TEXT,  -- "Unit 1: Introduction to Programming"
    grade_level TEXT,  -- "Undergraduate - Introductory"
    prerequisite_chapters TEXT,  -- JSON array
    related_chapters TEXT,  -- JSON array
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_metadata_project ON content_metadata(project_id);

-- ============================================================================
-- LEARNER TRACKING (Future use - adaptive tutoring)
-- ============================================================================

-- Learner performance tracking
CREATE TABLE learner_tasks (
    learner_task_id INTEGER PRIMARY KEY AUTOINCREMENT,
    learner_id TEXT NOT NULL,
    task_id TEXT NOT NULL REFERENCES tasks(task_id),
    attempt_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    result TEXT CHECK(result IN ('completed', 'failed', 'skipped', 'partial')),
    score REAL,  -- 0.0 to 1.0 or NULL
    bloom_level TEXT NOT NULL,
    notes TEXT,  -- Optional feedback or explanation
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_learner_tasks_learner ON learner_tasks(learner_id);
CREATE INDEX idx_learner_tasks_task ON learner_tasks(task_id);
CREATE INDEX idx_learner_tasks_bloom ON learner_tasks(bloom_level);
CREATE INDEX idx_learner_tasks_result ON learner_tasks(result);

-- ============================================================================
-- VERSIONING & AUDIT
-- ============================================================================

-- Version tracking for content updates
CREATE TABLE content_versions (
    version_id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id TEXT NOT NULL,
    version_number INTEGER NOT NULL,
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(project_id, version_number)
);

CREATE INDEX idx_versions_project ON content_versions(project_id);
