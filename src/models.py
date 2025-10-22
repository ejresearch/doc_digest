from typing import List, Literal, Optional
from pydantic import BaseModel

# -------- System Metadata (backend header) --------
class SystemMetadata(BaseModel):
    chapter_id: Optional[str] = None
    file_name: Optional[str] = None
    author_or_editor: Optional[str] = None
    version: Optional[str] = None
    created_at: Optional[str] = None  # ISO-8601
    source_text: Optional[str] = None

# -------- Comprehension Pass --------
class WhoItem(BaseModel):
    entity: str
    role_or_function: Optional[str] = ""
    significance_in_chapter: Optional[str] = ""
    evidence_pointer: Optional[str] = None

class WhatItem(BaseModel):
    concept_or_topic: str
    definition_or_description: Optional[str] = ""
    importance: Optional[str] = ""
    evidence_pointer: Optional[str] = None

class WhenBlock(BaseModel):
    historical_or_cultural_context: Optional[str] = ""
    chronological_sequence_within_course: Optional[str] = ""
    moment_of_presentation_to_reader: Optional[str] = ""

class WhyBlock(BaseModel):
    intellectual_value: Optional[str] = ""
    knowledge_based_value: Optional[str] = ""
    moral_or_philosophical_significance: Optional[str] = ""

class HowBlock(BaseModel):
    presentation_style: Optional[str] = ""
    rhetorical_approach: Optional[str] = ""
    recommended_student_strategy: Optional[str] = ""

class ComprehensionPass(BaseModel):
    who: List[WhoItem]
    what: List[WhatItem]
    when: WhenBlock
    why: WhyBlock
    how: HowBlock

# -------- Structural Outline --------
class SubSubtopic(BaseModel):
    title: str
    details: Optional[str] = ""
    visual_or_media_support: Optional[str] = ""

class Subtopic(BaseModel):
    subtopic_title: str
    key_concepts: List[str] = []
    supporting_examples: List[str] = []
    student_discussion_prompts: List[str] = []
    notes_on_instructional_sequence: Optional[str] = ""
    sub_subtopics: List[SubSubtopic] = []

class Section(BaseModel):
    section_title: str
    section_summary: Optional[str] = ""
    pedagogical_purpose: Optional[str] = ""
    rhetorical_mode: Optional[Literal["expository","narrative","analytical","reflective","procedural"]] = None
    subtopics: List[Subtopic] = []

class StructuralOutline(BaseModel):
    chapter_title: str
    guiding_context_questions: List[str] = []
    outline: List[Section]

# -------- Propositional Extraction --------
class Proposition(BaseModel):
    id: Optional[str] = None
    truth_type: Optional[Literal["descriptive","analytical","normative"]] = None
    statement: str
    evidence_from_text: Optional[str] = ""
    implication_for_learning: Optional[str] = ""
    connections_to_other_chapters: List[str] = []
    potential_student_reflection_question: Optional[str] = ""
    evidence_pointer: Optional[str] = None

class PropositionalExtraction(BaseModel):
    definition: Optional[str] = None
    guiding_prompts: List[str] = []
    propositions: List[Proposition]

# -------- Analytical Metadata (derived) --------
class AnalyticalMetadata(BaseModel):
    subject_domain: Optional[str] = None
    curriculum_unit: Optional[str] = None
    disciplinary_lens: Optional[str] = None
    related_chapters: List[str] = []
    grade_level_or_audience: Optional[str] = None
    spiral_position: Optional[str] = None

# -------- Pedagogical Mapping --------
class StudentActivity(BaseModel):
    activity_type: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None

class AssessmentQuestion(BaseModel):
    question: Optional[str] = None
    question_type: Optional[str] = None
    location: Optional[str] = None

class ReviewSection(BaseModel):
    content: Optional[str] = None
    location: Optional[str] = None

class VisualMediaReference(BaseModel):
    reference: Optional[str] = None
    description: Optional[str] = None
    pedagogical_purpose: Optional[str] = None

class HistoricalExample(BaseModel):
    example: Optional[str] = None
    time_period: Optional[str] = None
    still_relevant: Optional[bool] = None

class ContemporaryExample(BaseModel):
    example: Optional[str] = None
    current_as_of: Optional[str] = None
    update_priority: Optional[Literal["low", "medium", "high"]] = None

class TemporalAnalysis(BaseModel):
    historical_examples: List[HistoricalExample] = []
    contemporary_examples: List[ContemporaryExample] = []
    temporal_range: Optional[str] = None

class PedagogicalMapping(BaseModel):
    learning_objectives: List[str] = []
    student_activities: List[StudentActivity] = []
    assessment_questions: List[AssessmentQuestion] = []
    chapter_summary: Optional[str] = None
    review_sections: List[ReviewSection] = []
    visual_media_references: List[VisualMediaReference] = []
    temporal_analysis: Optional[TemporalAnalysis] = None
    potential_discussion_questions: List[str] = []

# -------- Master Document --------
class ChapterAnalysis(BaseModel):
    system_metadata: Optional[SystemMetadata] = None
    comprehension_pass: ComprehensionPass
    structural_outline: StructuralOutline
    propositional_extraction: PropositionalExtraction
    analytical_metadata: Optional[AnalyticalMetadata] = None
    pedagogical_mapping: Optional[PedagogicalMapping] = None
