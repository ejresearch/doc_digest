-- GRAFF Database Schema
-- SQLite database for storing chapter analysis results
-- Schema version: 1.0

-- ============================================================================
-- chapters: Core chapter metadata
-- ============================================================================
CREATE TABLE IF NOT EXISTS chapters (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  book_id TEXT NOT NULL,
  chapter_id TEXT NOT NULL UNIQUE,
  chapter_title TEXT NOT NULL,
  summary TEXT,
  schema_version TEXT DEFAULT '1.0',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_chapters_book_id ON chapters(book_id);
CREATE INDEX IF NOT EXISTS idx_chapters_chapter_id ON chapters(chapter_id);

-- ============================================================================
-- sections: Hierarchical chapter structure
-- ============================================================================
CREATE TABLE IF NOT EXISTS sections (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  chapter_id TEXT NOT NULL,
  unit_id TEXT NOT NULL,
  title TEXT NOT NULL,
  level INTEGER NOT NULL,
  parent_unit_id TEXT,
  start_location TEXT,
  end_location TEXT,
  FOREIGN KEY (chapter_id) REFERENCES chapters(chapter_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_sections_chapter_id ON sections(chapter_id);
CREATE INDEX IF NOT EXISTS idx_sections_unit_id ON sections(unit_id);
CREATE INDEX IF NOT EXISTS idx_sections_parent_unit_id ON sections(parent_unit_id);

-- ============================================================================
-- entities: Key entities mentioned in chapter
-- ============================================================================
CREATE TABLE IF NOT EXISTS entities (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  chapter_id TEXT NOT NULL,
  name TEXT NOT NULL,
  type TEXT NOT NULL,
  FOREIGN KEY (chapter_id) REFERENCES chapters(chapter_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_entities_chapter_id ON entities(chapter_id);
CREATE INDEX IF NOT EXISTS idx_entities_type ON entities(type);

-- ============================================================================
-- keywords: Chapter keywords for search
-- ============================================================================
CREATE TABLE IF NOT EXISTS keywords (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  chapter_id TEXT NOT NULL,
  keyword TEXT NOT NULL,
  FOREIGN KEY (chapter_id) REFERENCES chapters(chapter_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_keywords_chapter_id ON keywords(chapter_id);
CREATE INDEX IF NOT EXISTS idx_keywords_keyword ON keywords(keyword);

-- ============================================================================
-- propositions: Atomic facts extracted from chapter
-- ============================================================================
CREATE TABLE IF NOT EXISTS propositions (
  id TEXT PRIMARY KEY,
  chapter_id TEXT NOT NULL,
  unit_id TEXT NOT NULL,
  proposition_text TEXT NOT NULL,
  bloom_level TEXT NOT NULL CHECK (bloom_level IN ('remember', 'understand', 'apply', 'analyze')),
  bloom_verb TEXT NOT NULL,
  evidence_location TEXT NOT NULL,
  source_type TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (chapter_id) REFERENCES chapters(chapter_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_propositions_chapter_id ON propositions(chapter_id);
CREATE INDEX IF NOT EXISTS idx_propositions_unit_id ON propositions(unit_id);
CREATE INDEX IF NOT EXISTS idx_propositions_bloom_level ON propositions(bloom_level);

-- Full-text search on proposition text
CREATE VIRTUAL TABLE IF NOT EXISTS propositions_fts USING fts5(
  proposition_id UNINDEXED,
  proposition_text,
  content=propositions,
  content_rowid=rowid
);

-- Triggers to keep FTS index in sync
CREATE TRIGGER IF NOT EXISTS propositions_ai AFTER INSERT ON propositions BEGIN
  INSERT INTO propositions_fts(rowid, proposition_id, proposition_text)
  VALUES (new.rowid, new.id, new.proposition_text);
END;

CREATE TRIGGER IF NOT EXISTS propositions_ad AFTER DELETE ON propositions BEGIN
  DELETE FROM propositions_fts WHERE rowid = old.rowid;
END;

CREATE TRIGGER IF NOT EXISTS propositions_au AFTER UPDATE ON propositions BEGIN
  DELETE FROM propositions_fts WHERE rowid = old.rowid;
  INSERT INTO propositions_fts(rowid, proposition_id, proposition_text)
  VALUES (new.rowid, new.id, new.proposition_text);
END;

-- ============================================================================
-- proposition_tags: Many-to-many relationship for proposition tags
-- ============================================================================
CREATE TABLE IF NOT EXISTS proposition_tags (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  proposition_id TEXT NOT NULL,
  tag TEXT NOT NULL,
  FOREIGN KEY (proposition_id) REFERENCES propositions(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_proposition_tags_proposition_id ON proposition_tags(proposition_id);
CREATE INDEX IF NOT EXISTS idx_proposition_tags_tag ON proposition_tags(tag);

-- ============================================================================
-- key_takeaways: Synthesized learning points
-- ============================================================================
CREATE TABLE IF NOT EXISTS key_takeaways (
  id TEXT PRIMARY KEY,
  chapter_id TEXT NOT NULL,
  unit_id TEXT,
  text TEXT NOT NULL,
  dominant_bloom_level TEXT CHECK (dominant_bloom_level IN ('analyze', 'evaluate') OR dominant_bloom_level IS NULL),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (chapter_id) REFERENCES chapters(chapter_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_key_takeaways_chapter_id ON key_takeaways(chapter_id);
CREATE INDEX IF NOT EXISTS idx_key_takeaways_unit_id ON key_takeaways(unit_id);
CREATE INDEX IF NOT EXISTS idx_key_takeaways_bloom_level ON key_takeaways(dominant_bloom_level);

-- ============================================================================
-- takeaway_propositions: Links takeaways to their source propositions
-- ============================================================================
CREATE TABLE IF NOT EXISTS takeaway_propositions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  takeaway_id TEXT NOT NULL,
  proposition_id TEXT NOT NULL,
  FOREIGN KEY (takeaway_id) REFERENCES key_takeaways(id) ON DELETE CASCADE,
  FOREIGN KEY (proposition_id) REFERENCES propositions(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_takeaway_propositions_takeaway_id ON takeaway_propositions(takeaway_id);
CREATE INDEX IF NOT EXISTS idx_takeaway_propositions_proposition_id ON takeaway_propositions(proposition_id);

-- ============================================================================
-- takeaway_tags: Many-to-many relationship for takeaway tags
-- ============================================================================
CREATE TABLE IF NOT EXISTS takeaway_tags (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  takeaway_id TEXT NOT NULL,
  tag TEXT NOT NULL,
  FOREIGN KEY (takeaway_id) REFERENCES key_takeaways(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_takeaway_tags_takeaway_id ON takeaway_tags(takeaway_id);
CREATE INDEX IF NOT EXISTS idx_takeaway_tags_tag ON takeaway_tags(tag);

-- ============================================================================
-- Views for common queries
-- ============================================================================

-- View: Proposition count by Bloom level per chapter
CREATE VIEW IF NOT EXISTS v_proposition_bloom_distribution AS
SELECT
  chapter_id,
  bloom_level,
  COUNT(*) as count
FROM propositions
GROUP BY chapter_id, bloom_level;

-- View: Takeaway count by Bloom level per chapter
CREATE VIEW IF NOT EXISTS v_takeaway_bloom_distribution AS
SELECT
  chapter_id,
  dominant_bloom_level,
  COUNT(*) as count
FROM key_takeaways
GROUP BY chapter_id, dominant_bloom_level;

-- View: Complete chapter statistics
CREATE VIEW IF NOT EXISTS v_chapter_stats AS
SELECT
  c.chapter_id,
  c.chapter_title,
  c.book_id,
  COUNT(DISTINCT s.id) as section_count,
  COUNT(DISTINCT e.id) as entity_count,
  COUNT(DISTINCT k.id) as keyword_count,
  COUNT(DISTINCT p.id) as proposition_count,
  COUNT(DISTINCT kt.id) as takeaway_count,
  c.created_at
FROM chapters c
LEFT JOIN sections s ON c.chapter_id = s.chapter_id
LEFT JOIN entities e ON c.chapter_id = e.chapter_id
LEFT JOIN keywords k ON c.chapter_id = k.chapter_id
LEFT JOIN propositions p ON c.chapter_id = p.chapter_id
LEFT JOIN key_takeaways kt ON c.chapter_id = kt.chapter_id
GROUP BY c.chapter_id;
