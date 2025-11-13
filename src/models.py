"""
GRAFF Pydantic Models for Chapter Analysis

This module defines the schema for the 2-phase GRAFF pipeline:
- Phase 1: Chapter Comprehension
- Phase 2: Proposition Extraction + Key Takeaway Synthesis

Bloom Taxonomy Mapping:
- Propositions (micro): remember, understand, apply, analyze
- Key Takeaways (meso): analyze, evaluate
- Create (macro): Reserved for future activity generation
"""

from typing import List, Optional, Literal
from pydantic import BaseModel, Field

# ============================================================================
# Bloom Level Type Definitions
# ============================================================================

PropositionBloom = Literal["remember", "understand", "apply", "analyze"]
"""
Allowed Bloom levels for propositions (atomic facts).
Propositions must NOT use 'evaluate' or 'create'.
"""

TakeawayBloom = Literal["analyze", "evaluate"]
"""
Allowed Bloom levels for key takeaways (synthesized insights).
Takeaways represent higher-order cognition.
"""


# ============================================================================
# Phase 1: Chapter Comprehension Models
# ============================================================================

class Section(BaseModel):
    """
    Represents a hierarchical section or subsection within the chapter.

    Examples:
    - unit_id="1.1", title="Introduction", level=1
    - unit_id="1.2.3", title="Methods of Analysis", level=2, parent_unit_id="1.2"
    """
    unit_id: str = Field(..., description="Unique identifier for this section (e.g., '1.2', '3.4.1')")
    title: str = Field(..., description="Section title or heading")
    level: int = Field(..., description="Nesting depth (1=top-level section, 2=subsection, etc.)")
    parent_unit_id: Optional[str] = Field(None, description="unit_id of parent section (null for top-level)")
    start_location: Optional[str] = Field(None, description="Where section begins (e.g., 'p.5 ¶2')")
    end_location: Optional[str] = Field(None, description="Where section ends (e.g., 'p.8 ¶4')")


class Entity(BaseModel):
    """
    Key entity mentioned in the chapter (person, organization, concept, etc.).

    Examples:
    - name="Paramount Pictures", type="studio"
    - name="vertical integration", type="concept"
    - name="Adolph Zukor", type="person"
    """
    name: str = Field(..., description="Entity name")
    type: str = Field(..., description="Entity type (e.g., 'concept', 'person', 'studio', 'event')")


class Phase1Comprehension(BaseModel):
    """
    Output from Phase 1: Chapter structural analysis and comprehension.

    Includes:
    - Overall chapter summary
    - Hierarchical section breakdown
    - Key entities and concepts
    - Important keywords
    """
    summary: str = Field(..., description="One-paragraph summary of the entire chapter")
    sections: List[Section] = Field(..., description="Hierarchical breakdown of chapter sections")
    key_entities: List[Entity] = Field(default_factory=list, description="Important entities mentioned")
    keywords: List[str] = Field(default_factory=list, description="Domain-specific keywords and terms")


# ============================================================================
# Phase 2: Proposition & Takeaway Models
# ============================================================================

class Proposition(BaseModel):
    """
    An atomic fact extracted directly from the chapter text.

    Characteristics:
    - True/false statement
    - Grounded in specific text location
    - Cannot contain multiple ideas
    - Smallest unit of instructional meaning

    Bloom Constraints:
    - ALLOWED: remember, understand, apply, analyze
    - NOT ALLOWED: evaluate, create

    Example:
    {
      "proposition_id": "ch01_1.2_p001",
      "chapter_id": "ch01",
      "unit_id": "1.2",
      "proposition_text": "Vertical integration refers to studio ownership of production, distribution, and exhibition.",
      "bloom_level": "remember",
      "bloom_verb": "define",
      "evidence_location": "Section 1.2, paragraph 2",
      "source_type": "definition",
      "tags": ["vertical integration", "studios"]
    }
    """
    proposition_id: str = Field(..., description="Unique identifier (e.g., 'ch01_1.2_p001')")
    chapter_id: str = Field(..., description="Chapter this proposition belongs to")
    unit_id: str = Field(..., description="Section/unit this proposition is from")
    proposition_text: str = Field(..., description="The atomic fact statement")
    bloom_level: PropositionBloom = Field(..., description="Cognitive level (remember/understand/apply/analyze)")
    bloom_verb: str = Field(..., description="Action verb matching the Bloom level (e.g., 'define', 'explain', 'apply', 'compare')")
    evidence_location: str = Field(..., description="Where in the text this fact appears (e.g., 'Section 1.2, paragraph 3')")
    source_type: str = Field(..., description="How the fact was extracted (e.g., 'explicit', 'definition', 'paraphrased', 'inferred')")
    tags: List[str] = Field(default_factory=list, description="Domain-specific tags for filtering and search")


class KeyTakeaway(BaseModel):
    """
    A meaningful learning point that synthesizes several propositions.

    Characteristics:
    - One-sentence conceptual summary
    - Derived, not extracted
    - Represents significance, trend, relationship, or interpretation
    - Usually tied to a section or theme

    Bloom Constraints:
    - ALLOWED: analyze, evaluate
    - Represents higher-order cognition

    Example:
    {
      "takeaway_id": "ch01_t001",
      "chapter_id": "ch01",
      "unit_id": "1.2",
      "text": "Vertical integration allowed studios to dominate the film industry by controlling production, distribution, and exhibition.",
      "proposition_ids": ["ch01_1.2_p001", "ch01_1.2_p002", "ch01_1.2_p003"],
      "dominant_bloom_level": "analyze",
      "tags": ["industry structure", "market control"]
    }
    """
    takeaway_id: str = Field(..., description="Unique identifier (e.g., 'ch01_t001')")
    chapter_id: str = Field(..., description="Chapter this takeaway belongs to")
    unit_id: Optional[str] = Field(None, description="Primary section/unit (null if chapter-level)")
    text: str = Field(..., description="One-sentence synthesis statement")
    proposition_ids: List[str] = Field(..., description="List of proposition IDs this takeaway synthesizes")
    dominant_bloom_level: Optional[TakeawayBloom] = Field(None, description="Primary cognitive level (analyze/evaluate)")
    tags: List[str] = Field(default_factory=list, description="Thematic tags")

    def validate_proposition_ids(self) -> bool:
        """Ensure takeaway references at least one proposition."""
        return len(self.proposition_ids) > 0


class Phase2Output(BaseModel):
    """
    Output from Phase 2: Comprehensive proposition extraction and synthesis.

    Includes:
    - All atomic facts extracted from the chapter (comprehensive, no artificial limit)
    - Key takeaways synthesizing groups of related propositions
    - Optional processing notes
    """
    propositions: List[Proposition] = Field(..., description="All extracted atomic facts (comprehensive extraction)")
    key_takeaways: List[KeyTakeaway] = Field(..., description="Synthesized learning points")
    notes: Optional[str] = Field(None, description="Optional notes about extraction process, distribution, etc.")


# ============================================================================
# Complete Chapter Analysis (Root Model)
# ============================================================================

class ChapterAnalysis(BaseModel):
    """
    Complete analysis output for one chapter.

    Combines Phase 1 (comprehension) and Phase 2 (extraction/synthesis).
    This is the root model for the entire GRAFF pipeline.

    Example structure:
    {
      "schema_version": "1.0",
      "book_id": "film_industry_vol1",
      "chapter_id": "ch01",
      "chapter_title": "The Classical Hollywood Studio System",
      "phase1": { ... },
      "phase2": { ... }
    }
    """
    schema_version: str = Field(default="1.0", description="GRAFF schema version")
    book_id: str = Field(..., description="Identifier for the book/course this chapter belongs to")
    chapter_id: str = Field(..., description="Unique chapter identifier")
    chapter_title: str = Field(..., description="Chapter title")
    phase1: Phase1Comprehension = Field(..., description="Phase 1: Structural comprehension output")
    phase2: Phase2Output = Field(..., description="Phase 2: Proposition and takeaway extraction")

    def get_proposition_count(self) -> int:
        """Get total number of propositions extracted."""
        return len(self.phase2.propositions)

    def get_bloom_distribution(self) -> dict:
        """
        Get distribution of propositions by Bloom level.

        Returns:
            dict: {bloom_level: count}
        """
        distribution = {"remember": 0, "understand": 0, "apply": 0, "analyze": 0}
        for prop in self.phase2.propositions:
            distribution[prop.bloom_level] += 1
        return distribution

    def get_takeaway_bloom_distribution(self) -> dict:
        """
        Get distribution of key takeaways by Bloom level.

        Returns:
            dict: {bloom_level: count}
        """
        distribution = {"analyze": 0, "evaluate": 0, "none": 0}
        for takeaway in self.phase2.key_takeaways:
            if takeaway.dominant_bloom_level:
                distribution[takeaway.dominant_bloom_level] += 1
            else:
                distribution["none"] += 1
        return distribution
