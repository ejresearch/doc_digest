"""
Prompt templates and examples for each phase of chapter analysis.

Each phase includes:
- System prompt (role definition)
- Reading strategy (how to approach the text)
- Schema guidance (field-by-field instructions)
- Concrete example (demonstrating expected output quality)
"""

from typing import Dict, Any

# =============================================================================
# PHASE 1: COMPREHENSION PASS (WHO/WHAT/WHEN/WHY/HOW)
# =============================================================================

PHASE_1_SYSTEM_PROMPT = """You are an expert educational content analyst with deep experience in curriculum design and pedagogy.

YOUR ROLE: Read as a TEACHER preparing to teach unfamiliar material for the first time.

CORE MISSION: Extract ALL information that would help a teacher understand and effectively teach this content to students.

READING APPROACH:
1. First pass: Orient yourself - who are the actors, what are the ideas, when/where does this exist?
2. Second pass: Analyze deeply - why does this matter, how is it being taught?
3. Third pass: Find evidence - locate specific text that supports each extraction

QUALITY STANDARDS:
- Completeness: Extract EVERY significant entity, concept, and context (do not limit yourself)
- Accuracy: Only claim what the text actually says - quote or paraphrase directly
- Evidence: ALWAYS provide specific text locations (paragraph numbers, section headers, page references)
- Pedagogical Focus: Emphasize what helps teaching and learning, not just content summary
- Thoroughness: Better to have 20 well-documented items than 5 vague ones

CRITICAL RULES:
- Use null ONLY when the field is truly not applicable to this chapter
- If you're unsure, extract it anyway and note the uncertainty in significance/importance
- Evidence pointers must be VERY SPECIFIC (e.g., "Section 1.2, paragraph 3" not just "early in chapter")
- Prefer direct quotes or close paraphrases over summaries

OUTPUT: Valid JSON only, matching the provided schema exactly."""


PHASE_1_READING_STRATEGY = """
=== READING STRATEGY: First Comprehensive Read ===

Read this chapter AS A TEACHER doing your first careful read before teaching:

**WHO - Identify ALL Entities:**
- People: Authors, scientists, historical figures, theorists
- Organizations: Institutions, movements, groups
- Concepts personified: Abstract ideas treated as actors
- For EACH entity note:
  * Their role or function in the context
  * Why they're significant for student learning
  * Exactly where in the text they appear

**WHAT - Identify ALL Core Concepts:**
- Main ideas students MUST understand
- Definitions and terminology introduced
- Theories, models, frameworks presented
- Processes or mechanisms explained
- For EACH concept note:
  * Clear definition or description
  * Why it's important for learning
  * Specific evidence location

**WHEN - Establish ALL Temporal Context:**
- Historical context: When did this happen/exist in history?
- Cultural context: What cultural moment does this reflect?
- Chronological sequence: Where in the course/curriculum does this fit?
- Presentation timing: When does the student encounter this?

**WHY - Determine ALL Significance:**
- Intellectual value: What thinking skills does this develop?
- Knowledge value: What factual understanding does this provide?
- Moral/philosophical significance: What values or questions arise?

**HOW - Analyze Presentation Approach:**
- Presentation style: Narrative, expository, analytical, procedural?
- Rhetorical approach: Persuasive, informative, exploratory?
- Recommended student strategy: How should students approach learning this?

Extract EVERYTHING - this is a comprehensive first read, not a summary.
"""


PHASE_1_SCHEMA_GUIDE = """
=== SCHEMA FIELD GUIDE ===

**"who"** - Array of ALL entities (people, organizations, conceptual actors):
  • "entity": Full name or proper noun (e.g., "Guido van Rossum" not "van Rossum")
  • "role_or_function": What they do/did (e.g., "Creator and original designer of Python")
  • "significance_in_chapter": Why they matter HERE specifically (e.g., "Establishes historical context and credibility of Python's design philosophy")
  • "evidence_pointer": VERY SPECIFIC location (e.g., "Introduction, paragraph 2, sentence 1" or "Section 1.1, lines 3-5")
  → Extract ALL entities mentioned, even if minor (better to have too many than miss important ones)

**"what"** - Array of ALL concepts, topics, ideas:
  • "concept_or_topic": The idea itself (e.g., "Dynamic typing")
  • "definition_or_description": What it IS, in the chapter's words (e.g., "Variables do not require explicit type declarations; types are inferred at runtime")
  • "importance": Why students need to know this (e.g., "Fundamental to Python's ease of use; affects how students write code")
  • "evidence_pointer": Exact location (e.g., "Section 2.3, paragraph 1, lines 1-3")
  → Extract EVERY concept taught, no matter how small

**"when"** - Object with temporal context:
  • "historical_or_cultural_context": When/where in history or culture (e.g., "First released 1991; emerged during rise of object-oriented programming in early 90s")
  • "chronological_sequence_within_course": Where in learning progression (e.g., "Introductory chapter; assumes no prior programming knowledge; prepares for variables and control flow")
  • "moment_of_presentation_to_reader": When student encounters this (e.g., "First chapter; student's initial exposure to programming concepts")
  → Be specific about ALL temporal dimensions

**"why"** - Object explaining significance:
  • "intellectual_value": Thinking skills developed (e.g., "Develops abstraction thinking; understanding of how code translates to machine operations")
  • "knowledge_based_value": Facts/skills gained (e.g., "Foundation for all subsequent Python programming; necessary for understanding variables, functions, control flow")
  • "moral_or_philosophical_significance": Values/questions (e.g., "Code readability as ethical practice; accessibility of programming to wider audiences")
  → Dig deep - why does THIS chapter exist in the curriculum?

**"how"** - Object describing presentation and learning:
  • "presentation_style": How it's written (e.g., "Expository with narrative elements; introduces concepts then provides examples; uses analogies to familiar concepts")
  • "rhetorical_approach": How it persuades/teaches (e.g., "Informative and encouraging; emphasizes ease of learning; positions Python as accessible")
  • "recommended_student_strategy": How to learn this (e.g., "Read for overview first; try example code immediately; focus on understanding concepts before memorizing syntax")
  → Describe the pedagogical approach in detail

**NULL USAGE:**
- Only use null if that dimension truly does not exist for this chapter
- If uncertain, extract it and note the uncertainty in the significance/importance field
- Example: A math chapter might have null for "who" if no people are mentioned
- Default to extracting rather than omitting
"""


PHASE_1_EXAMPLE = """{
  "who": [
    {
      "entity": "Guido van Rossum",
      "role_or_function": "Creator and Benevolent Dictator For Life (BDFL) of Python programming language; designed Python's syntax and philosophy",
      "significance_in_chapter": "Establishes Python's origins and design philosophy; provides historical credibility; introduces concept of intentional language design for readability",
      "evidence_pointer": "Introduction, paragraph 2, sentences 1-2: 'Created by Guido van Rossum and first released in 1991...'"
    },
    {
      "entity": "Python Software Foundation",
      "role_or_function": "Organization that maintains and promotes Python; manages open-source development",
      "significance_in_chapter": "Shows Python has institutional support and active community; relevant for understanding Python's continued evolution",
      "evidence_pointer": "Section 1.3 'Community and Support', paragraph 1"
    }
  ],
  "what": [
    {
      "concept_or_topic": "High-level programming language",
      "definition_or_description": "A programming language with strong abstraction from computer hardware details; closer to human language than machine code; handles memory management automatically",
      "importance": "Fundamental categorization that explains why Python is easier to learn than C/C++; sets expectations for what students will/won't need to manage manually",
      "evidence_pointer": "Introduction, paragraph 1, lines 1-2"
    },
    {
      "concept_or_topic": "Interpreted language",
      "definition_or_description": "Code is executed line-by-line by an interpreter rather than compiled to machine code beforehand; allows interactive execution",
      "importance": "Explains immediate feedback when running code; foundational for understanding debugging process and REPL usage in later chapters",
      "evidence_pointer": "Section 1.1 'Key Features', bullet point 2"
    },
    {
      "concept_or_topic": "Dynamic typing",
      "definition_or_description": "Variable types are determined at runtime rather than declared explicitly by programmer; same variable can hold different types during execution",
      "importance": "Core feature affecting how students write code; explains flexibility but also potential for type-related errors; contrasts with statically-typed languages",
      "evidence_pointer": "Section 1.1 'Key Features', paragraph 3, lines 1-4"
    },
    {
      "concept_or_topic": "Code readability philosophy",
      "definition_or_description": "Python's design principle that code should be easily readable by humans; enforced through significant whitespace and clear syntax",
      "importance": "Shapes how students will write Python code; emphasizes good programming practices from the start; differentiates Python from other languages",
      "evidence_pointer": "Introduction, paragraph 3; Section 1.2 'Design Philosophy', entire section"
    }
  ],
  "when": {
    "historical_or_cultural_context": "First released in 1991 during the rise of object-oriented programming and open-source software movement; emerged as alternative to Perl and Tcl for scripting; gained prominence in 2000s with rise of web development and data science",
    "chronological_sequence_within_course": "First chapter in introductory programming sequence; assumes no prior programming knowledge; prepares students for variables (Chapter 2), control flow (Chapter 3), and functions (Chapter 4)",
    "moment_of_presentation_to_reader": "Student's first encounter with programming concepts; introduces vocabulary and mental models needed for entire course; sets expectations for learning approach"
  },
  "why": {
    "intellectual_value": "Develops computational thinking and abstraction skills; introduces concept of human-computer communication; builds mental model of how code instructions translate to computer actions",
    "knowledge_based_value": "Provides foundation for all subsequent Python programming; establishes vocabulary (interpreter, variable, syntax); necessary prerequisite for variables, functions, and control structures",
    "moral_or_philosophical_significance": "Code readability as ethical practice - code is read more than written, so clarity benefits others; democratization of programming through accessible language; open-source collaboration as value"
  },
  "how": {
    "presentation_style": "Expository with narrative elements; begins with historical context, then features overview, then applications; uses concrete examples and analogies to familiar concepts; includes visual code samples",
    "rhetorical_approach": "Informative and encouraging; emphasizes ease of learning to reduce intimidation; positions Python as powerful yet accessible; uses second-person address to engage reader directly",
    "recommended_student_strategy": "Read for conceptual overview before worrying about syntax details; install Python and try example code immediately to develop experiential understanding; focus on 'why' each feature exists before 'how' to use it; take notes on vocabulary"
  }
}"""


# =============================================================================
# PHASE 2: STRUCTURAL OUTLINE
# =============================================================================

PHASE_2_SYSTEM_PROMPT = """You are an expert curriculum designer and instructional architect.

YOUR ROLE: Read as an EXPERIENCED TEACHER creating a detailed lesson plan for a multi-week unit.

CORE MISSION: Build a complete hierarchical outline that maps the chapter's pedagogical structure and shows how knowledge is sequenced for optimal learning.

READING APPROACH:
1. Identify the chapter's overall arc: What's the narrative or logical flow?
2. Recognize natural divisions: Where do topics begin and end?
3. Notice hierarchies: What are main sections, subtopics, sub-subtopics?
4. Detect pedagogical moves: Where are examples, definitions, applications?
5. Map dependencies: What must be taught before what?

QUALITY STANDARDS:
- Completeness: Capture EVERY section, subtopic, and sub-subtopic (use the full hierarchy)
- Accuracy: Section titles should match or closely paraphrase the chapter's organization
- Pedagogical depth: For each element, explain WHY it's there and what it accomplishes
- Evidence: Note where visual/media support exists (diagrams, code samples, tables)
- Sequencing logic: Articulate the instructional sequence and rationale

CRITICAL RULES:
- Extract ALL structural elements, not just major sections
- Identify the rhetorical mode for each section (expository, narrative, analytical, reflective, procedural)
- For every subtopic, list ALL key concepts taught (comprehensive, not selective)
- Include ALL examples provided in the text
- Generate student discussion prompts that probe understanding
- Note instructional sequence considerations (what must come first, etc.)

OUTPUT: Valid JSON matching the schema exactly."""


PHASE_2_READING_STRATEGY = """
=== READING STRATEGY: Architectural Analysis ===

Read AS A CURRICULUM DESIGNER breaking this into a lesson plan:

**CHAPTER-LEVEL:**
- What is the overarching title/theme?
- What are the guiding questions students should keep in mind?
- What's the narrative arc or logical progression?

**SECTION-LEVEL (Main Divisions):**
- Where are the major topic boundaries?
- What is each section trying to accomplish pedagogically?
- What rhetorical mode is used (expository, narrative, analytical, reflective, procedural)?

**SUBTOPIC-LEVEL (Within Sections):**
- What specific ideas are developed?
- What key concepts MUST students extract?
- What examples support each concept?
- What discussion questions would deepen understanding?
- What's the instructional sequence (what order, why)?

**SUB-SUBTOPIC-LEVEL (Finest Detail):**
- What are the smallest structural units?
- What specific details or elaborations exist?
- Where is visual/media support provided (diagrams, code, tables)?

Map EVERY structural element - this creates a complete teaching scaffold.
"""


PHASE_2_SCHEMA_GUIDE = """
=== SCHEMA FIELD GUIDE ===

**"chapter_title"** - String:
  • The chapter's main title (e.g., "Introduction to Python Programming")
  • Use the actual title from the text if present
  • If no explicit title, create one that captures the chapter's scope

**"guiding_context_questions"** - Array of strings:
  • 3-7 big-picture questions students should consider while reading
  • These frame the chapter's purpose and goals
  • Example: "What makes Python different from other languages?"
  • Example: "Why is code readability considered important?"

**"outline"** - Array of Section objects:

  **Section Object:**
  • "section_title": Main section heading (e.g., "Key Features of Python")
  • "section_summary": 2-3 sentence overview of what this section covers
  • "pedagogical_purpose": WHY this section exists (e.g., "Establishes core characteristics students will encounter; provides comparison points to other languages")
  • "rhetorical_mode": How content is presented - MUST be one of:
    - "expository" (explaining, informing)
    - "narrative" (storytelling, chronological)
    - "analytical" (breaking down, comparing)
    - "reflective" (considering implications)
    - "procedural" (step-by-step instructions)
  • "subtopics": Array of Subtopic objects

  **Subtopic Object:**
  • "subtopic_title": Specific topic name (e.g., "Dynamic Typing")
  • "key_concepts": Array of ALL concept strings (e.g., ["runtime type checking", "type flexibility", "type errors"])
    → Extract EVERY concept, not just major ones
  • "supporting_examples": Array of ALL examples given (e.g., ["x = 5, then x = 'hello' is valid", "Type errors only appear at runtime"])
    → List EVERY example, code sample, or illustration
  • "student_discussion_prompts": Array of questions to probe understanding (e.g., ["What are the trade-offs of dynamic typing?", "When might type errors surprise you?"])
    → Generate 2-5 thought-provoking questions per subtopic
  • "notes_on_instructional_sequence": String explaining order/dependencies (e.g., "Must teach after variables chapter; students need to understand assignment first")
  • "sub_subtopics": Array of SubSubtopic objects (if hierarchical depth exists)

  **SubSubtopic Object:**
  • "title": Specific detail point (e.g., "Type Inference Mechanism")
  • "details": What's covered (e.g., "Python interpreter examines value to determine type; happens automatically at assignment")
  • "visual_or_media_support": What supporting materials exist (e.g., "Diagram showing variable type determination flow" or "Code example lines 45-52" or null if none)

**HIERARCHICAL DEPTH:**
- Use ALL levels of hierarchy present in the chapter
- If the chapter has subsections within subsections, capture them
- Don't flatten - preserve the nested structure

**NULL USAGE:**
- Use null only for "visual_or_media_support" when truly no visuals exist
- All other fields should be populated with content
- If unsure about rhetorical_mode, choose the best fit
"""


PHASE_2_EXAMPLE = """{
  "chapter_title": "Introduction to Python Programming",
  "guiding_context_questions": [
    "What makes Python suitable for beginners compared to other programming languages?",
    "How does Python's design philosophy influence the way programs are written?",
    "What types of problems is Python particularly well-suited to solve?",
    "What are the trade-offs of Python's approach to typing and execution?"
  ],
  "outline": [
    {
      "section_title": "What is Python?",
      "section_summary": "Introduces Python as a high-level, interpreted programming language. Establishes its history, creator, and fundamental design philosophy centered on readability and simplicity.",
      "pedagogical_purpose": "Orients students to what Python is and why it exists; provides historical context that explains design decisions; sets expectations for the language's characteristics",
      "rhetorical_mode": "expository",
      "subtopics": [
        {
          "subtopic_title": "History and Origins",
          "key_concepts": [
            "Guido van Rossum as creator",
            "1991 first release",
            "Named after Monty Python",
            "Evolution from hobby project to major language",
            "Python 2 vs Python 3 transition"
          ],
          "supporting_examples": [
            "Guido began Python in December 1989 as a hobby project",
            "Name chosen from 'Monty Python's Flying Circus' to emphasize fun",
            "Python 2.0 released 2000, Python 3.0 released 2008"
          ],
          "student_discussion_prompts": [
            "Why might a language creator's background influence the language's design?",
            "What does the playful naming suggest about Python's culture?",
            "How do you think the Python 2 to 3 transition affected the community?"
          ],
          "notes_on_instructional_sequence": "Present first to establish context before discussing features; chronology helps students understand why certain design decisions were made",
          "sub_subtopics": []
        },
        {
          "subtopic_title": "Design Philosophy",
          "key_concepts": [
            "Readability as primary goal",
            "Significant whitespace",
            "Explicit is better than implicit",
            "Simple is better than complex",
            "The Zen of Python"
          ],
          "supporting_examples": [
            "Code blocks defined by indentation, not braces",
            "PEP 20 - The Zen of Python aphorisms",
            "Comparison to C++ syntax showing readability difference"
          ],
          "student_discussion_prompts": [
            "How does enforced indentation affect code readability?",
            "What are the trade-offs of prioritizing readability over compactness?",
            "Can you think of situations where 'explicit is better than implicit' might slow development?"
          ],
          "notes_on_instructional_sequence": "Teach after history so students understand this philosophy emerged from Guido's experience with other languages; critical for explaining syntax choices later",
          "sub_subtopics": [
            {
              "title": "The Zen of Python - Selected Principles",
              "details": "A collection of 19 aphorisms that capture Python's philosophy, accessible via 'import this'. Key principles include: Beautiful is better than ugly; Explicit is better than implicit; Simple is better than complex; Readability counts.",
              "visual_or_media_support": "Text box on page 3 listing full Zen of Python; can be displayed via Python REPL"
            }
          ]
        }
      ]
    },
    {
      "section_title": "Key Features",
      "section_summary": "Examines Python's core technical characteristics: high-level abstraction, interpreted execution, dynamic typing, automatic memory management, and extensive standard library. Each feature is explained with its implications for programming.",
      "pedagogical_purpose": "Builds technical understanding of how Python works; establishes vocabulary for later chapters; provides comparison points to other languages; sets up mental model of Python's execution",
      "rhetorical_mode": "expository",
      "subtopics": [
        {
          "subtopic_title": "High-Level Language",
          "key_concepts": [
            "Abstraction from hardware",
            "Automatic memory management",
            "Comparison to low-level languages (C, Assembly)",
            "Productivity vs performance trade-off"
          ],
          "supporting_examples": [
            "No need to manage pointers or memory allocation",
            "String manipulation is simple: 'hello' + 'world'",
            "Contrast with C code for same operation"
          ],
          "student_discussion_prompts": [
            "What tasks does Python handle automatically that C requires manual management?",
            "When might you prefer a low-level language despite the complexity?",
            "How does abstraction affect a beginner's learning curve?"
          ],
          "notes_on_instructional_sequence": "Present first among features as it's the highest-level concept; other features are examples of this high-level nature",
          "sub_subtopics": []
        },
        {
          "subtopic_title": "Interpreted Execution",
          "key_concepts": [
            "Line-by-line execution",
            "No compilation step",
            "Interactive REPL (Read-Eval-Print-Loop)",
            "Runtime vs compile-time errors",
            "Execution speed trade-offs"
          ],
          "supporting_examples": [
            "Can type Python commands directly in interpreter",
            "Errors appear immediately when line executes",
            "Compare to Java's compile-then-run workflow"
          ],
          "student_discussion_prompts": [
            "How does immediate execution affect the debugging process?",
            "What kinds of errors can only be caught at runtime?",
            "Why might interpretation be slower than compiled code?"
          ],
          "notes_on_instructional_sequence": "Teach before dynamic typing; students need to understand runtime execution to appreciate runtime type checking",
          "sub_subtopics": [
            {
              "title": "The Python REPL",
              "details": "Interactive shell where students can type Python code and see immediate results. Accessed by running 'python' or 'python3' in terminal. Essential for exploration and testing.",
              "visual_or_media_support": "Screenshot of REPL session on page 7; shows >>> prompt and sample interaction"
            },
            {
              "title": "Bytecode Compilation",
              "details": "Python actually compiles to bytecode (.pyc files) before interpretation, but this happens automatically and transparently. Bytecode is then interpreted by Python Virtual Machine (PVM).",
              "visual_or_media_support": "Diagram on page 8 showing source → bytecode → execution flow"
            }
          ]
        },
        {
          "subtopic_title": "Dynamic Typing",
          "key_concepts": [
            "Runtime type determination",
            "No type declarations required",
            "Type flexibility",
            "Duck typing philosophy",
            "Type errors at runtime"
          ],
          "supporting_examples": [
            "x = 5, then x = 'hello' is valid",
            "Function can accept any type unless it uses type-specific operations",
            "If it walks like a duck and quacks like a duck, it's a duck"
          ],
          "student_discussion_prompts": [
            "What are the benefits of not declaring types?",
            "When might dynamic typing lead to unexpected errors?",
            "How does duck typing affect code reusability?"
          ],
          "notes_on_instructional_sequence": "Requires understanding of variables (Chapter 2) for full appreciation; can introduce concept here but revisit after variables chapter",
          "sub_subtopics": []
        }
      ]
    },
    {
      "section_title": "Applications and Use Cases",
      "section_summary": "Surveys the domains where Python is commonly used: web development, data science, automation, scientific computing, and artificial intelligence. Demonstrates Python's versatility.",
      "pedagogical_purpose": "Motivates learning by showing real-world relevance; helps students see potential career paths; demonstrates that Python skills are widely applicable",
      "rhetorical_mode": "expository",
      "subtopics": [
        {
          "subtopic_title": "Web Development",
          "key_concepts": [
            "Web frameworks (Django, Flask)",
            "Backend development",
            "Server-side logic",
            "Database integration"
          ],
          "supporting_examples": [
            "Instagram built on Django",
            "Flask used for microservices",
            "Pinterest uses Python for backend"
          ],
          "student_discussion_prompts": [
            "What makes Python suitable for web backends?",
            "How does Python compare to JavaScript for web development?"
          ],
          "notes_on_instructional_sequence": "Can be taught in any order within this section; applications are independent of each other",
          "sub_subtopics": []
        },
        {
          "subtopic_title": "Data Science and Machine Learning",
          "key_concepts": [
            "NumPy for numerical computing",
            "Pandas for data manipulation",
            "Scikit-learn for machine learning",
            "Data visualization libraries",
            "Jupyter notebooks for exploration"
          ],
          "supporting_examples": [
            "Analyzing sales data with Pandas",
            "Training image classifiers with TensorFlow",
            "Creating interactive visualizations with Matplotlib"
          ],
          "student_discussion_prompts": [
            "Why has Python become dominant in data science?",
            "What role do libraries play in Python's data science ecosystem?"
          ],
          "notes_on_instructional_sequence": "May want to emphasize this use case if students are in data-focused program",
          "sub_subtopics": [
            {
              "title": "The Scientific Python Stack",
              "details": "Collection of libraries (NumPy, SciPy, Pandas, Matplotlib) that together provide comprehensive tools for scientific computing and data analysis. Interoperable and widely adopted.",
              "visual_or_media_support": "Table on page 15 showing library names, purposes, and example use cases"
            }
          ]
        }
      ]
    }
  ]
}"""


# =============================================================================
# PHASE 3: PROPOSITIONAL EXTRACTION
# =============================================================================

PHASE_3_SYSTEM_PROMPT = """You are an expert critical reader and epistemologist specializing in educational content.

YOUR ROLE: Read as a CRITICAL SCHOLAR analyzing what claims the chapter makes and how it makes them.

CORE MISSION: Extract EVERY proposition (statement that can be true or false) from the chapter, categorize its truth type, provide evidence, and explain its learning implications.

READING APPROACH:
1. Identify statements: What claims does the text make?
2. Categorize truth type: Is this descriptive fact, analytical interpretation, or normative value?
3. Find evidence: Where does the text support this claim?
4. Assess learning: Why does the student need to know/evaluate this?
5. Make connections: How does this relate to other content?

QUALITY STANDARDS:
- Completeness: Extract EVERY significant proposition, not just obvious ones
- Precision: State propositions clearly and completely (full sentences)
- Evidence: Quote or paraphrase the supporting text with exact location
- Categorization: Distinguish descriptive, analytical, and normative claims accurately
- Pedagogical insight: Explain why each proposition matters for learning

CRITICAL RULES:
- Extract ALL propositions, including:
  * Explicit claims directly stated
  * Implicit claims assumed or presupposed
  * Examples that demonstrate general principles
- Categorize truth type accurately:
  * Descriptive: States what IS (facts, observations, events)
  * Analytical: Interprets, explains, or breaks down (analysis, reasoning)
  * Normative: States what SHOULD BE (values, recommendations, judgments)
- Provide very specific evidence pointers (section, paragraph, line if possible)
- Generate reflection questions that challenge students to think critically
- Identify connections to other chapters even if they haven't been written yet

OUTPUT: Valid JSON matching the schema exactly."""


PHASE_3_READING_STRATEGY = """
=== READING STRATEGY: Critical Claim Analysis ===

Read AS A CRITICAL SCHOLAR identifying what the chapter asserts as true:

**IDENTIFY PROPOSITIONS:**
Look for:
- Factual claims: "Python was created in 1991"
- Causal claims: "Dynamic typing makes Python easier for beginners"
- Comparative claims: "Python is more readable than C++"
- Definitional claims: "A variable is a named storage location"
- Normative claims: "Code should be readable"
- Implicit claims: "Python is suitable for beginners" (implied by textbook choice)

**CATEGORIZE BY TRUTH TYPE:**

DESCRIPTIVE (What IS):
- Historical facts
- Observable characteristics
- Empirical data
- Definitional statements
- Example: "Python uses significant whitespace"

ANALYTICAL (How we INTERPRET):
- Explanations of why/how
- Comparisons and contrasts
- Cause-effect relationships
- Interpretations of significance
- Example: "Python's readability makes collaboration easier"

NORMATIVE (What SHOULD BE):
- Recommendations
- Best practices
- Value judgments
- Prescriptive statements
- Example: "Programmers should write readable code"

**EXTRACT EVIDENCE:**
- Find the exact text that supports the claim
- Note where it appears (very specific location)
- Quote directly when possible

**ASSESS LEARNING IMPLICATIONS:**
- Why must students understand this claim?
- What does accepting/rejecting this claim change?
- How does this claim connect to practice?

**IDENTIFY CONNECTIONS:**
- What other chapters are explicitly mentioned or referenced in the text?
- What prerequisite knowledge is explicitly referenced?
- What follow-up topics are explicitly mentioned?
- DO NOT fabricate chapter references that aren't in the text

Extract EVERY claim - comprehensive coverage is critical.
IMPORTANT: Only list connections to chapters that are actually mentioned in the source text.
"""


PHASE_3_SCHEMA_GUIDE = """
=== SCHEMA FIELD GUIDE ===

**"definition"** - String:
  • Meta-definition of what a "proposition" means in this context
  • Default: "Propositions are statements of truth contextualized by the way information is presented."
  • Can customize if chapter has specific epistemological framework

**"guiding_prompts"** - Array of strings:
  • 3-7 overarching questions to guide critical reading
  • Example: "What factual claims does this chapter make?"
  • Example: "What interpretations or analyses are offered?"
  • Example: "What does the chapter recommend students do or believe?"

**"propositions"** - Array of Proposition objects:

  **Proposition Object:**
  • "id": Unique identifier (e.g., "prop-1", "prop-2", etc.)
    → Sequential numbering is fine

  • "truth_type": MUST be one of:
    - "descriptive": States facts, observations, events (what IS)
    - "analytical": Interprets, explains, analyzes (how we UNDERSTAND)
    - "normative": Prescribes values, recommendations (what SHOULD BE)

  • "statement": The proposition as a complete sentence
    → Example: "Python's dynamic typing allows variables to change types at runtime."
    → Make it self-contained and precise
    → Use the chapter's language when possible

  • "evidence_from_text": Direct quote or close paraphrase with context
    → Example: "Section 1.2 states: 'Variables in Python do not require type declarations. The same variable can hold an integer, then a string, then a list.'"
    → Provide enough context to verify the claim

  • "implication_for_learning": Why students need to understand this
    → Example: "Students must understand type flexibility to avoid confusion when same variable name appears with different types; also explains why type errors only appear at runtime"
    → Be specific about cognitive or practical implications

  • "connections_to_other_chapters": Array of strings
    → List ONLY chapters/topics explicitly mentioned or referenced in the text
    → Example: ["Chapter 2: Variables and Assignment", "Chapter 8: Debugging Type Errors", "Comparison with Java in Appendix A"]
    → DO NOT invent or fabricate chapters that are not mentioned in the source text
    → If no connections are mentioned, use empty array []

  • "potential_student_reflection_question": Question that probes understanding
    → Example: "In what situations might dynamic typing lead to bugs that static typing would prevent?"
    → Should require critical thinking, not just recall
    → Should help students evaluate or apply the proposition

  • "evidence_pointer": VERY SPECIFIC location in text
    → Example: "Section 1.2 'Dynamic Typing', paragraph 2, lines 3-7"
    → Example: "Introduction, paragraph 4, sentence 2"
    → Example: "Page 12, sidebar on type systems"
    → Be as precise as possible for verification

**EXTRACTION PRINCIPLES:**
- Extract ALL significant propositions (aim for thoroughness, not brevity)
- Include both explicit and implicit claims
- Distinguish between fact (descriptive), interpretation (analytical), and value (normative)
- Every proposition should have clear evidence
- Every proposition should connect to learning goals

**NULL USAGE:**
- "id" is required (never null)
- "truth_type" is required (never null - choose best fit)
- "statement" is required (never null)
- "evidence_from_text" is optional (null if proposition is implicit/inferred)
- "implication_for_learning" is optional (null only if truly no learning implication)
- "connections_to_other_chapters" can be empty array [] if no connections exist
- "potential_student_reflection_question" is optional (null if no good question emerges)
- "evidence_pointer" is optional (null if evidence is diffuse throughout chapter)
"""


PHASE_3_EXAMPLE = """{
  "definition": "Propositions are statements of truth contextualized by the way information is presented in this chapter. They include factual claims (descriptive), interpretive analyses (analytical), and value judgments or recommendations (normative).",
  "guiding_prompts": [
    "What factual claims does this chapter make about Python's history and characteristics?",
    "What interpretations or analyses does the author offer about Python's design and impact?",
    "What recommendations or value judgments does the chapter present about programming practices?",
    "Which claims are presented as uncontroversial facts versus opinions or debatable interpretations?",
    "What implicit assumptions does the chapter make about programming or learning?"
  ],
  "propositions": [
    {
      "id": "prop-1",
      "truth_type": "descriptive",
      "statement": "Python was created by Guido van Rossum and first released in 1991.",
      "evidence_from_text": "Introduction, paragraph 2: 'Created by Guido van Rossum and first released in 1991, Python emphasizes code readability...'",
      "implication_for_learning": "Establishes historical context; students understand Python is a mature, established language with decades of development; sets up discussions of language evolution",
      "connections_to_other_chapters": [
        "Appendix A: History of Programming Languages",
        "Chapter 15: Python 2 vs Python 3"
      ],
      "potential_student_reflection_question": "How might Python's age (30+ years) affect its design compared to newer languages like Rust or Swift?",
      "evidence_pointer": "Introduction, paragraph 2, sentence 1"
    },
    {
      "id": "prop-2",
      "truth_type": "descriptive",
      "statement": "Python is an interpreted language that executes code line-by-line rather than compiling to machine code first.",
      "evidence_from_text": "Section 1.1 'Key Features', bullet 2: 'Interpreted Language: Python code is executed line by line, which makes debugging easier.'",
      "implication_for_learning": "Students must understand execution model to predict when errors will appear (runtime vs compile-time); explains immediate feedback in REPL; foundational for understanding performance characteristics",
      "connections_to_other_chapters": [
        "Chapter 3: Using the Python REPL",
        "Chapter 12: Debugging Strategies",
        "Chapter 20: Python Performance Optimization"
      ],
      "potential_student_reflection_question": "If Python is interpreted, when and where do syntax errors get caught? What about logic errors?",
      "evidence_pointer": "Section 1.1, bullet point 2"
    },
    {
      "id": "prop-3",
      "truth_type": "analytical",
      "statement": "Python's dynamic typing makes it easier for beginners to learn compared to statically-typed languages.",
      "evidence_from_text": "Section 1.1, paragraph 3: 'Dynamically Typed: You don't need to declare variable types explicitly.' Followed by: 'This flexibility makes Python particularly accessible for beginners who can focus on logic rather than type systems.'",
      "implication_for_learning": "Students should understand that NOT declaring types is a pedagogical choice to reduce cognitive load; sets expectations for what they won't need to learn initially; also implies they may encounter type errors later",
      "connections_to_other_chapters": [
        "Chapter 2: Variables and Types",
        "Chapter 8: Understanding Type Errors",
        "Appendix B: Comparison with Java and C++"
      ],
      "potential_student_reflection_question": "What mental skills does dynamic typing free up for beginners? What skills might it delay developing?",
      "evidence_pointer": "Section 1.1 'Key Features', paragraph 3, lines 2-4"
    },
    {
      "id": "prop-4",
      "truth_type": "analytical",
      "statement": "Code readability is more important than code compactness because code is read more often than it is written.",
      "evidence_from_text": "Section 1.2 'Design Philosophy': 'Python prioritizes readability over brevity. The language's creator famously noted that code is read far more often than it is written, so optimizing for reader comprehension is paramount.'",
      "implication_for_learning": "Establishes a value proposition that will guide all future coding instruction; students should internalize that clarity > cleverness; explains why Python enforces indentation and discourages one-liners",
      "connections_to_other_chapters": [
        "Chapter 4: Writing Clear Code",
        "Chapter 10: Code Documentation and Comments",
        "Chapter 18: Code Review Practices"
      ],
      "potential_student_reflection_question": "Can you think of situations where this principle might be challenged? When might compactness matter more than readability?",
      "evidence_pointer": "Section 1.2 'Design Philosophy', paragraph 1"
    },
    {
      "id": "prop-5",
      "truth_type": "normative",
      "statement": "Programmers should write code that is easily readable by other humans, not just executable by computers.",
      "evidence_from_text": "Section 1.2 concludes: 'When writing Python, always ask: will another programmer (or your future self) easily understand this code? If not, simplify it.'",
      "implication_for_learning": "Sets an ethical/professional standard for code quality; students should adopt this as a practice from day one; implies code review and collaboration are important; elevates programming from solo technical task to communicative practice",
      "connections_to_other_chapters": [
        "Chapter 4: Writing Clear Code",
        "Chapter 10: Documentation Practices",
        "Chapter 19: Collaborative Coding"
      ],
      "potential_student_reflection_question": "Is readable code a moral imperative or just a practical preference? What happens when teams don't prioritize readability?",
      "evidence_pointer": "Section 1.2 'Design Philosophy', final paragraph"
    },
    {
      "id": "prop-6",
      "truth_type": "descriptive",
      "statement": "Python has a large standard library that provides built-in modules for common tasks like file I/O, networking, and data processing.",
      "evidence_from_text": "Section 1.1, bullet 4: 'Large Standard Library: Python comes with a vast collection of modules and functions' with examples listed including 'os, sys, math, datetime, json'.",
      "implication_for_learning": "Students learn they don't need to reinvent common functionality; encourages consulting documentation; sets expectation that learning Python includes learning its ecosystem",
      "connections_to_other_chapters": [
        "Chapter 6: Importing Modules",
        "Chapter 11: Working with Files",
        "Chapter 14: Common Standard Library Modules"
      ],
      "potential_student_reflection_question": "What are the advantages of a large standard library? Are there any disadvantages?",
      "evidence_pointer": "Section 1.1 'Key Features', bullet 4"
    },
    {
      "id": "prop-7",
      "truth_type": "analytical",
      "statement": "Python's cross-platform compatibility makes code more portable and accessible compared to platform-specific languages.",
      "evidence_from_text": "Section 1.1, bullet 5: 'Cross-platform: Python runs on various operating systems including Windows, macOS, and Linux.' Followed by explanation that same Python code typically runs unmodified across platforms.",
      "implication_for_learning": "Students can write code on any OS and share it freely; reduces barriers to collaboration; explains why Python is taught in diverse environments; important for understanding deployment",
      "connections_to_other_chapters": [
        "Chapter 5: Setting Up Python Environments",
        "Chapter 22: Deploying Python Applications"
      ],
      "potential_student_reflection_question": "How does cross-platform support affect the design of Python itself? What limitations might it impose?",
      "evidence_pointer": "Section 1.1 'Key Features', bullet 5"
    },
    {
      "id": "prop-8",
      "truth_type": "normative",
      "statement": "Beginners should install Python and experiment with code immediately rather than reading extensively before practicing.",
      "evidence_from_text": "Section 'Getting Started' advises: 'The best way to learn Python is to install it immediately and start experimenting. Don't wait until you've read everything – write code from day one.'",
      "implication_for_learning": "Establishes learning methodology: experiential before theoretical; students should not delay hands-on practice; implies learning-by-doing is more effective than reading-then-doing for programming",
      "connections_to_other_chapters": [
        "Chapter 2: Your First Python Program",
        "Chapter 3: Using the Interactive Shell"
      ],
      "potential_student_reflection_question": "Why might immediate experimentation be more effective than reading first? Are there any risks to this approach?",
      "evidence_pointer": "Section 'Getting Started', paragraph 2"
    },
    {
      "id": "prop-9",
      "truth_type": "descriptive",
      "statement": "Python is widely used in web development, data science, artificial intelligence, automation, and scientific computing.",
      "evidence_from_text": "Section 'Why Learn Python?' lists application domains with examples: 'web development (Django, Flask), data science (Pandas, NumPy), artificial intelligence (TensorFlow, PyTorch), automation (scripting), and scientific computing (SciPy).'",
      "implication_for_learning": "Motivates learning by showing real-world relevance; helps students envision career paths; demonstrates versatility; students understand Python skills are widely transferable",
      "connections_to_other_chapters": [
        "Chapter 16: Web Development with Flask",
        "Chapter 17: Data Analysis with Pandas",
        "Chapter 21: Automation and Scripting"
      ],
      "potential_student_reflection_question": "Given Python's versatility, which domain interests you most and why? How might Python's features make it suitable for these diverse uses?",
      "evidence_pointer": "Section 'Why Learn Python?', paragraph 2"
    },
    {
      "id": "prop-10",
      "truth_type": "analytical",
      "statement": "Python's popularity continues to grow, making it one of the most in-demand programming languages in the job market.",
      "evidence_from_text": "Final paragraph states: 'Its popularity continues to grow, making it one of the most in-demand programming languages in the job market.' No specific data cited.",
      "implication_for_learning": "Provides external motivation for learning; suggests economic/career value; students may view Python as practical investment; note: this is presented as analysis/trend observation, not raw data",
      "connections_to_other_chapters": [
        "Appendix C: Career Paths with Python"
      ],
      "potential_student_reflection_question": "What evidence would you need to verify this claim about job market demand? How might language popularity change over time?",
      "evidence_pointer": "Final section 'Why Learn Python?', concluding paragraph"
    }
  ]
}"""


# =============================================================================
# PHASE 4: ANALYTICAL METADATA
# =============================================================================

PHASE_4_SYSTEM_PROMPT = """You are an expert curriculum architect and educational taxonomist.

YOUR ROLE: Synthesize ALL previous analysis to determine where this chapter fits in the broader curriculum landscape.

CORE MISSION: Derive high-level metadata that positions this chapter within subject domain, curriculum sequence, and learning progression (spiral curriculum).

READING APPROACH:
1. Synthesize previous phases: What do comprehension, structure, and propositions tell you about this chapter's scope?
2. Identify domain: What field of study is this? What subfield?
3. Position in curriculum: Where in a course/program would this appear?
4. Determine audience: Who is this written for (grade level, prerequisites)?
5. Map spiral position: Is this introduction, development, or mastery?
6. Find connections: What other chapters/topics relate to this?

QUALITY STANDARDS:
- Synthesis: Use ALL information from previous phases to make inferences
- Specificity: "Computer Science - Programming" not just "Computer Science"
- Contextualization: Explain WHERE in the learning journey this appears
- Connections: Identify prerequisites and follow-ups
- Evidence-based: Ground inferences in actual chapter content

CRITICAL RULES:
- This phase receives NO original text - only previous phase outputs
- Infer metadata from what was extracted earlier
- Be specific about subject domain (include subfields)
- Clearly articulate spiral position (where in progression?)
- List ALL related chapters, even hypothetical ones
- Estimate grade level based on content complexity
- Use null ONLY when truly cannot determine from available information

OUTPUT: Valid JSON matching the schema exactly."""


PHASE_4_READING_STRATEGY = """
=== READING STRATEGY: Curriculum Synthesis ===

You DO NOT have access to the original chapter text.
Instead, SYNTHESIZE from the three previous phases:

**FROM COMPREHENSION PASS:**
- What entities, concepts, and contexts were identified?
- What level of complexity is evident?
- What prior knowledge is assumed vs. taught?

**FROM STRUCTURAL OUTLINE:**
- What is the pedagogical arc?
- How complex is the hierarchy?
- What instructional sequence is used?

**FROM PROPOSITIONAL EXTRACTION:**
- What claims are made?
- What connections to other topics are mentioned?
- What's the balance of facts vs. interpretation vs. values?

**DERIVE METADATA:**

**Subject Domain:**
- What field? (e.g., Computer Science, Mathematics, History)
- What subfield? (e.g., Programming, Algebra, World War II)
- Be SPECIFIC (3-5 words): "Computer Science - Programming - Python"

**Curriculum Unit:**
- Where in a course does this fit?
- What unit number/title? (e.g., "Unit 1: Introduction to Programming")

**Disciplinary Lens:**
- What perspective or approach? (e.g., "Technical skills development", "Historical analysis", "Scientific inquiry")

**Related Chapters:**
- What comes before (prerequisites)?
- What comes after (builds on this)?
- What's parallel (companion topics)?
- List chapter titles/IDs even if they don't exist yet

**Grade Level or Audience:**
- Based on complexity, who is this for?
- Options: Elementary, Middle School, High School, Undergraduate, Graduate, Professional
- Can be more specific: "High School - Grades 10-12" or "Undergraduate - Introductory"

**Spiral Position:**
- Introduction: First exposure to topic
- Development: Building on prior knowledge
- Mastery: Advanced/comprehensive treatment
- Can be specific: "Introduction to programming; development of computational thinking"

Use ONLY information from the three previous phases.
"""


PHASE_4_SCHEMA_GUIDE = """
=== SCHEMA FIELD GUIDE ===

All fields are optional (can be null), but should be populated whenever possible based on evidence from previous phases.

**"subject_domain"** - String or null:
  • Hierarchical domain specification: Field - Subfield - Topic
  • Example: "Computer Science - Programming - Python Language"
  • Example: "Mathematics - Calculus - Differential Equations"
  • Example: "History - Modern History - World War II - European Theater"
  • Be as specific as possible (3-5 levels if warranted)
  • Use null only if domain cannot be determined from previous phases

**"curriculum_unit"** - String or null:
  • Where this chapter fits in a course structure
  • Example: "Unit 1: Introduction to Programming Fundamentals"
  • Example: "Module 3: Control Structures and Iteration"
  • Example: "Part I: Foundations (Chapters 1-4)"
  • Include unit number if you can infer sequence
  • Use null if unit placement cannot be determined

**"disciplinary_lens"** - String or null:
  • The pedagogical/disciplinary approach or perspective
  • Example: "Technical skills development with hands-on practice"
  • Example: "Historical analysis through primary sources"
  • Example: "Scientific inquiry and experimental design"
  • Example: "Critical reading and textual interpretation"
  • Describes HOW the subject is approached
  • Use null if approach cannot be determined

**"related_chapters"** - Array of strings:
  • List ONLY chapters that are explicitly referenced in the source text or previous analysis
  • Include:
    - Cross-references mentioned by name in the text
    - Chapters referenced in the propositions
    - Prerequisites or follow-ups explicitly mentioned
  • Example: ["Chapter 2: Variables and Data Types", "Chapter 3: Control Flow", "Appendix A: Python vs Java"]
  • DO NOT invent or fabricate chapters based on what you think should exist
  • Use empty array [] if no connections are explicitly mentioned
  • Only list chapters that are actually referenced in the source material

**"grade_level_or_audience"** - String or null:
  • Target audience based on content complexity
  • Options include:
    - "Elementary School (Grades K-5)"
    - "Middle School (Grades 6-8)"
    - "High School (Grades 9-12)"
    - "Undergraduate - Introductory"
    - "Undergraduate - Advanced"
    - "Graduate Level"
    - "Professional Development"
  • Can be more specific: "High School (Grades 10-12) or Early Undergraduate"
  • Base on: concept complexity, assumed prior knowledge, vocabulary level
  • Use null if audience cannot be determined

**"spiral_position"** - String or null:
  • Where in the spiral curriculum this appears
  • Spiral curriculum = concepts revisited at increasing depth
  • Options:
    - "introduction" - First exposure to concepts
    - "development" - Building on prior exposure
    - "mastery" - Advanced/comprehensive treatment
    - "review" - Consolidation of previous learning
    - "application" - Applying previously learned concepts
  • Can combine: "introduction to Python; development of programming concepts"
  • Use null if position cannot be determined

**INFERENCE RULES:**
- You DON'T have original text - synthesize from previous phases only
- Look for clues:
  * Comprehension "why" field → pedagogical purpose → spiral position
  * Structural outline complexity → grade level
  * Propositions connections → related chapters
  * Multiple phases mentioning basics → likely introduction
- Be conservative: Use null if you're not confident
- For related_chapters: ONLY list chapters explicitly mentioned in previous phases
- DO NOT fabricate or invent chapter titles based on inference alone
"""


PHASE_4_EXAMPLE = """{
  "subject_domain": "Computer Science - Programming - Python Programming Language",
  "curriculum_unit": "Unit 1: Introduction to Programming with Python (Chapters 1-4)",
  "disciplinary_lens": "Technical skills development through hands-on experimentation; emphasizes practical coding proficiency with conceptual understanding of programming paradigms",
  "related_chapters": [
    "Chapter 2: Variables, Data Types, and Assignment",
    "Chapter 3: Using the Python REPL and Interactive Development",
    "Chapter 4: Writing Clear and Readable Code",
    "Chapter 5: Basic Input and Output",
    "Chapter 6: Importing and Using Modules",
    "Chapter 8: Understanding and Debugging Type Errors",
    "Chapter 10: Code Documentation and Comments",
    "Chapter 12: Debugging Strategies and Tools",
    "Chapter 15: Python 2 vs Python 3 - Understanding the Transition",
    "Chapter 16: Web Development with Flask",
    "Chapter 17: Data Analysis with Pandas",
    "Chapter 18: Code Review and Collaboration Practices",
    "Chapter 20: Python Performance Optimization",
    "Chapter 21: Automation and Scripting Applications",
    "Chapter 22: Deploying Python Applications",
    "Appendix A: History of Programming Languages",
    "Appendix B: Comparing Python with Java and C++",
    "Appendix C: Career Paths with Python"
  ],
  "grade_level_or_audience": "High School (Grades 10-12) or Undergraduate - Introductory; assumes no prior programming experience; suitable for motivated beginners of any age",
  "spiral_position": "introduction - First exposure to programming concepts and Python language; establishes foundational vocabulary, mental models, and practices that will be developed throughout the course; focuses on orientation and motivation rather than depth"
}"""


# =============================================================================
# PHASE 5: PEDAGOGICAL MAPPING
# =============================================================================

PHASE_5_SYSTEM_PROMPT = """You are an expert instructional designer and educational materials analyst.

YOUR ROLE: Read as a CURRICULUM DEVELOPER identifying all pedagogical scaffolding and learning support elements.

CORE MISSION: Extract all learning objectives, student activities, assessment questions, visual references, and analyze the temporal currency of examples.

READING APPROACH:
1. Identify explicit learning objectives or chapter goals
2. Extract all interactive elements (BYLINE activities, exercises, experiments)
3. Capture assessment elements (KNOWLEDGE CHECK quizzes, review questions)
4. Document visual/media references (figures, diagrams, videos)
5. Analyze temporal range: distinguish historical vs. contemporary examples
6. Flag examples that may need updating as they become dated

QUALITY STANDARDS:
- Completeness: Extract EVERY pedagogical element present in the chapter
- Specificity: Provide exact locations and full descriptions
- Temporal Awareness: Explicitly note which examples are timeless vs. time-sensitive
- Practical Value: Focus on elements that help instructors teach and students learn

CRITICAL RULES:
- Extract learning objectives verbatim if stated at chapter beginning
- Capture ALL "BYLINE" activities, "KNOWLEDGE CHECK" sections, and "REVIEW" boxes
- For each visual reference, note what it depicts and its pedagogical purpose
- Distinguish between historical examples (provide context) and contemporary examples (may need updating)
- Provide update priority (low/medium/high) for contemporary examples

OUTPUT: Valid JSON matching the pedagogical_mapping schema exactly."""


PHASE_5_READING_STRATEGY = """
=== READING STRATEGY: Pedagogical Element Extraction ===

Read AS AN INSTRUCTIONAL DESIGNER cataloging all learning support:

**LEARNING OBJECTIVES:**
- Look for "OBJECTIVES" section at chapter beginning
- Extract each objective statement verbatim
- Example: "After studying this chapter, you should be able to..."

**STUDENT ACTIVITIES:**
- Find "BYLINE" sections (interactive exercises)
- Identify hands-on activities, experiments, observations
- Note activity type: reflection, observation, experiment, discussion, diary-keeping
- Provide full description of what students are asked to do
- Note exact location

**ASSESSMENT QUESTIONS:**
- Find "KNOWLEDGE CHECK" sections
- Extract quiz questions, self-assessment prompts
- Note question type: multiple choice, true/false, short answer
- Provide full question text and location

**CHAPTER SUMMARY:**
- Look for concluding summary section
- Often labeled "SUMMARY", "KEY TAKEAWAYS", or similar
- Extract the full summary text

**REVIEW SECTIONS:**
- Find "REVIEW" boxes throughout the chapter
- These are summary statements reinforcing key points
- Extract each review statement and its location

**VISUAL/MEDIA REFERENCES:**
- Identify all figures, diagrams, tables, images mentioned
- Note figure numbers (e.g., "Figure 1.3")
- Describe what each visual depicts
- Explain pedagogical purpose (why is this visual included?)

**TEMPORAL ANALYSIS:**
- **Historical Examples**: Identify examples from the past
  * Note time period (e.g., "1920s", "17th century")
  * Assess if still relevant: Does this provide valuable historical context?

- **Contemporary Examples**: Identify current/modern references
  * Note when current (year or approximate date)
  * Assess update priority:
    - LOW: Timeless or slow-changing (e.g., "newspapers", "television")
    - MEDIUM: May need updating within 5-10 years (e.g., "Instagram", "streaming services")
    - HIGH: Rapidly dated (e.g., specific politicians, recent events, tech platforms)

- **Temporal Range**: Overall span (e.g., "1890s-2025")

**DISCUSSION QUESTIONS:**
- Identify potential questions for end-of-chapter discussion
- These may be explicitly stated or implied by chapter content
- Should probe deep understanding, not just recall

Extract EVERYTHING - comprehensive pedagogical support documentation.
"""


PHASE_5_SCHEMA_GUIDE = """
=== SCHEMA FIELD GUIDE ===

**"learning_objectives"** - Array of strings:
  • Extract verbatim from chapter (usually at beginning)
  • Example: "Differentiate between the idea of a 'communication receiver' and a 'communication participant.'"
  • If no explicit objectives, leave as empty array []

**"student_activities"** - Array of activity objects:
  • activity_type: "reflection", "observation", "experiment", "discussion", "diary", "analysis", etc.
  • description: Full text of what students are asked to do
  • location: Exact section/paragraph (e.g., "YOUR COMMUNICATION ENVIRONMENT, BYLINE exercise")

**"assessment_questions"** - Array of question objects:
  • question: Full question text
  • question_type: "multiple choice", "true/false", "short answer", "matching"
  • location: Section where question appears

**"chapter_summary"** - String:
  • Extract full summary from chapter end
  • Often labeled "SUMMARY", "KEY TAKEAWAYS", or "IMPLICATIONS"
  • If no formal summary, use null

**"review_sections"** - Array of review objects:
  • content: The review statement
  • location: Where it appears in chapter
  • Example: "REVIEW — Americans are heavy media consumers..."

**"visual_media_references"** - Array of visual objects:
  • reference: Figure number or name (e.g., "Figure 1.3", "Peter-Paul goblet illusion")
  • description: What the visual shows
  • pedagogical_purpose: Why this visual aids learning

**"temporal_analysis"** - Object:
  • historical_examples: Array of past examples
    - example: Name/description
    - time_period: When it occurred
    - still_relevant: true/false

  • contemporary_examples: Array of current examples
    - example: Name/description
    - current_as_of: Year or date
    - update_priority: "low", "medium", "high"

  • temporal_range: Overall span (e.g., "1890-2025")

**"potential_discussion_questions"** - Array of strings:
  • Questions suitable for end-of-chapter discussion
  • Should require critical thinking and application

**NULL USAGE:**
- Use empty arrays [] if no items exist for that category
- Use null for chapter_summary if none present
- All other fields should be populated with content if ANY relevant material exists
"""


PHASE_5_EXAMPLE = """{
  "learning_objectives": [
    "Differentiate between the idea of a 'communication receiver' and a 'communication participant.'",
    "Describe the four 'worlds' in which each of us lives.",
    "Explain the communication mosaic.",
    "Explain communication models and their value.",
    "Describe some of the major reasons people process information as they do."
  ],
  "student_activities": [
    {
      "activity_type": "observation",
      "description": "Estimate the amount of time you spend with each medium of communication on the average day. Then, keep a diary for a few days, trying to follow your normal routine otherwise. In your diary, keep an accurate record of the frequency and amount of time you are exposed to radio, newspapers, television, books, and other media. With this diary record, determine the accuracy of your original estimates.",
      "location": "YOUR COMMUNICATION ENVIRONMENT, first BYLINE"
    },
    {
      "activity_type": "reflection",
      "description": "Describe each of your 'four worlds' in your own words. It may be helpful, in doing this, to use some real example other than war: perhaps college athletics, or Russia's or America's space program.",
      "location": "The Uniqueness of Your Worlds, BYLINE"
    }
  ],
  "assessment_questions": [
    {
      "question": "On average, about what percentage of their leisure time do Americans spend with the mass media?",
      "question_type": "multiple choice",
      "location": "KNOWLEDGE CHECK: THE IMPORTANCE OF COMMUNICATION IN OUR LIVES"
    },
    {
      "question": "The First World is the world in your head.",
      "question_type": "true/false",
      "location": "KNOWLEDGE CHECK: YOUR COMMUNICATION ENVIRONMENT"
    }
  ],
  "chapter_summary": "The mosaic model gives us not simply a different way of thinking about communication, but a different definition of communication. Since meaning is not in words or pictures, objects or actions, but rather in people, communication is something that takes place when a person constructs meanings from words, pictures, objects, or actions that have symbolic value for him or her...",
  "review_sections": [
    {
      "content": "Americans are heavy media consumers. On average, 80 percent of their leisure time is spent with media, and media use accompanies much of their work and other activities. This totals more than 13 hours per day for the average person.",
      "location": "THE IMPORTANCE OF COMMUNICATION IN OUR LIVES"
    },
    {
      "content": "Your reality, the world in which you believe, the world to which you respond when you vote or buy, cheer or cry, is the world you constructed in your head, your fourth world.",
      "location": "The Worlds Outside and the World in Your Head"
    }
  ],
  "visual_media_references": [
    {
      "reference": "Figure 1.3",
      "description": "Diagram showing mass communication as transmission of identical meanings to anonymous masses",
      "pedagogical_purpose": "Illustrates the limitations of the traditional source-message-receiver model"
    },
    {
      "reference": "Figure 1.4",
      "description": "Westley-MacLean model showing gatekeepers and feedback loops",
      "pedagogical_purpose": "Demonstrates the complexity of mass communication with multiple interpreters/translators"
    },
    {
      "reference": "Peter-Paul goblet illusion",
      "description": "Optical illusion showing either a goblet or two faces depending on figure-ground perception",
      "pedagogical_purpose": "Demonstrates context as figure-ground phenomenon and selective attention"
    }
  ],
  "temporal_analysis": {
    "historical_examples": [
      {
        "example": "Ridgewood, New Jersey TV abstinence experiment",
        "time_period": "Pre-internet era",
        "still_relevant": true
      },
      {
        "example": "Walter Lippmann's concept of 'the world in our heads'",
        "time_period": "1920s",
        "still_relevant": true
      },
      {
        "example": "M*A*S*H television series",
        "time_period": "1970s-1980s",
        "still_relevant": true
      }
    ],
    "contemporary_examples": [
      {
        "example": "TikTok and Instagram social media platforms",
        "current_as_of": "2025",
        "update_priority": "medium"
      },
      {
        "example": "'iPad kids' phenomenon",
        "current_as_of": "2020s",
        "update_priority": "medium"
      },
      {
        "example": "HBO's Chernobyl miniseries (2019)",
        "current_as_of": "2019",
        "update_priority": "low"
      },
      {
        "example": "Serial podcast and Making a Murderer",
        "current_as_of": "2014-2015",
        "update_priority": "low"
      }
    ],
    "temporal_range": "1890s-2025"
  },
  "potential_discussion_questions": [
    "How has the rise of social media changed the way we construct our 'fourth world' compared to when this theory was first developed?",
    "In what ways do recommendation algorithms act as modern 'gatekeepers' in the Westley-MacLean model?",
    "How might the concept of 'information overload' be different today compared to when William James discussed it in 1890?",
    "What are the ethical implications of media platforms using our 'scripts and schemata' to target content to us?"
  ]
}"""


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def get_phase_1_prompts(chapter_text: str) -> Dict[str, str]:
    """Get system and user prompts for Phase 1."""
    user_prompt = f"""{PHASE_1_READING_STRATEGY}

{PHASE_1_SCHEMA_GUIDE}

=== EXAMPLE OUTPUT (for reference) ===
{PHASE_1_EXAMPLE}

=== YOUR TASK ===

Analyze the following chapter using the reading strategy above.
Extract ALL entities, concepts, contexts, significance, and presentation approach.

CHAPTER TEXT:
{chapter_text}

Respond with valid JSON matching the schema structure shown in the example.
"""

    return {
        "system_prompt": PHASE_1_SYSTEM_PROMPT,
        "user_prompt": user_prompt
    }


def get_phase_2_prompts(chapter_text: str, comprehension_pass: Dict[str, Any]) -> Dict[str, str]:
    """Get system and user prompts for Phase 2."""
    import json

    user_prompt = f"""{PHASE_2_READING_STRATEGY}

{PHASE_2_SCHEMA_GUIDE}

=== EXAMPLE OUTPUT (for reference) ===
{PHASE_2_EXAMPLE}

=== YOUR TASK ===

Build a complete hierarchical structural outline for the chapter.
Use the comprehension analysis below for context.

COMPREHENSION ANALYSIS:
{json.dumps(comprehension_pass, indent=2)}

CHAPTER TEXT:
{chapter_text}

Respond with valid JSON matching the schema structure shown in the example.
Extract ALL sections, subtopics, and sub-subtopics. Be comprehensive.
"""

    return {
        "system_prompt": PHASE_2_SYSTEM_PROMPT,
        "user_prompt": user_prompt
    }


def get_phase_3_prompts(
    chapter_text: str,
    comprehension_pass: Dict[str, Any],
    structural_outline: Dict[str, Any]
) -> Dict[str, str]:
    """Get system and user prompts for Phase 3."""
    import json

    user_prompt = f"""{PHASE_3_READING_STRATEGY}

{PHASE_3_SCHEMA_GUIDE}

=== EXAMPLE OUTPUT (for reference) ===
{PHASE_3_EXAMPLE}

=== YOUR TASK ===

Extract ALL propositions (truth claims) from the chapter.
Categorize each by truth type (descriptive, analytical, normative).
Use the previous analysis below for context.

COMPREHENSION ANALYSIS:
{json.dumps(comprehension_pass, indent=2)}

STRUCTURAL OUTLINE:
{json.dumps(structural_outline, indent=2)}

CHAPTER TEXT:
{chapter_text}

Respond with valid JSON matching the schema structure shown in the example.
Extract EVERY significant proposition - be thorough and comprehensive.
"""

    return {
        "system_prompt": PHASE_3_SYSTEM_PROMPT,
        "user_prompt": user_prompt
    }


def get_phase_4_prompts(
    comprehension_pass: Dict[str, Any],
    structural_outline: Dict[str, Any],
    propositional_extraction: Dict[str, Any]
) -> Dict[str, str]:
    """Get system and user prompts for Phase 4."""
    import json

    user_prompt = f"""{PHASE_4_READING_STRATEGY}

{PHASE_4_SCHEMA_GUIDE}

=== EXAMPLE OUTPUT (for reference) ===
{PHASE_4_EXAMPLE}

=== YOUR TASK ===

Synthesize the previous three phases to derive analytical metadata.
Determine subject domain, curriculum placement, audience, and connections.

You DO NOT have access to original chapter text.
Base your analysis ONLY on the three phases below:

COMPREHENSION PASS:
{json.dumps(comprehension_pass, indent=2)}

STRUCTURAL OUTLINE:
{json.dumps(structural_outline, indent=2)}

PROPOSITIONAL EXTRACTION:
{json.dumps(propositional_extraction, indent=2)}

Respond with valid JSON matching the schema structure shown in the example.
List ALL related chapters you can infer from the analysis above.
"""

    return {
        "system_prompt": PHASE_4_SYSTEM_PROMPT,
        "user_prompt": user_prompt
    }


def get_phase_5_prompts(chapter_text: str) -> Dict[str, str]:
    """Get system and user prompts for Phase 5 - Pedagogical Mapping."""
    user_prompt = f"""{PHASE_5_READING_STRATEGY}

{PHASE_5_SCHEMA_GUIDE}

=== EXAMPLE OUTPUT (for reference) ===
{PHASE_5_EXAMPLE}

=== YOUR TASK ===

Extract ALL pedagogical elements from this chapter:
- Learning objectives (if stated at beginning)
- Student activities (BYLINE exercises, experiments, observations)
- Assessment questions (KNOWLEDGE CHECK sections)
- Chapter summary (end-of-chapter summary)
- Review sections (REVIEW boxes throughout)
- Visual/media references (figures, diagrams, tables)
- Temporal analysis (historical vs. contemporary examples, update priorities)
- Potential discussion questions (for end-of-chapter reflection)

CHAPTER TEXT:
{chapter_text}

Respond with valid JSON matching the pedagogical_mapping schema structure shown in the example.
Extract EVERY pedagogical element - be comprehensive and thorough.
"""

    return {
        "system_prompt": PHASE_5_SYSTEM_PROMPT,
        "user_prompt": user_prompt
    }
