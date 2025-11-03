-- GRAFF v0.3.0: Bloom's Taxonomy Verb Reference Data
-- Populates the bloom_verbs table with comprehensive verb lists and definitions

-- ============================================================================
-- REMEMBER LEVEL
-- Definition: Retrieve relevant knowledge from long-term memory
-- ============================================================================

INSERT INTO bloom_verbs (bloom_level, verb, definition, example_question_stem) VALUES
('remember', 'recall', 'Retrieve specific information from memory without prompting', 'What is...?'),
('remember', 'list', 'Enumerate items, names, or elements from memory', 'List the...'),
('remember', 'define', 'State the precise meaning of a term or concept', 'Define...'),
('remember', 'identify', 'Recognize and name a specific item or concept', 'Identify the...'),
('remember', 'name', 'Provide the label or title for something', 'Name the...'),
('remember', 'state', 'Express information in words clearly and explicitly', 'State the...'),
('remember', 'recognize', 'Identify something from a set of alternatives', 'Which of these is...?'),
('remember', 'match', 'Pair related items or concepts correctly', 'Match the following...'),
('remember', 'select', 'Choose the correct item from alternatives', 'Select the...'),
('remember', 'describe', 'Give an account of characteristics or features (factual)', 'Describe what...');

-- ============================================================================
-- UNDERSTAND LEVEL
-- Definition: Construct meaning from instructional messages; demonstrate comprehension
-- ============================================================================

INSERT INTO bloom_verbs (bloom_level, verb, definition, example_question_stem) VALUES
('understand', 'explain', 'Provide a clear description of how or why something works', 'Explain why...'),
('understand', 'describe', 'Give a detailed account of characteristics or processes', 'Describe how...'),
('understand', 'summarize', 'Condense information to essential points', 'Summarize the main...'),
('understand', 'interpret', 'Translate or explain the meaning of information', 'What does this mean...?'),
('understand', 'classify', 'Group items according to shared characteristics', 'Classify these into...'),
('understand', 'compare', 'Identify similarities between two or more things', 'How are these similar...?'),
('understand', 'infer', 'Draw logical conclusions from evidence or reasoning', 'What can you infer...?'),
('understand', 'paraphrase', 'Restate information using different words', 'Put this in your own words...'),
('understand', 'exemplify', 'Provide an example or illustration of a concept', 'Give an example of...'),
('understand', 'illustrate', 'Show or demonstrate through examples or visuals', 'Illustrate how...'),
('understand', 'translate', 'Convert from one form to another (verbal, symbolic, visual)', 'Translate this into...'),
('understand', 'predict', 'Forecast what will happen based on understanding', 'What would happen if...?');

-- ============================================================================
-- APPLY LEVEL
-- Definition: Carry out or use a procedure in a given situation
-- ============================================================================

INSERT INTO bloom_verbs (bloom_level, verb, definition, example_question_stem) VALUES
('apply', 'apply', 'Use knowledge or skills in a new or concrete situation', 'How would you apply...?'),
('apply', 'execute', 'Carry out a procedure or process', 'Execute the following...'),
('apply', 'implement', 'Put a plan, decision, or procedure into action', 'Implement a solution to...'),
('apply', 'use', 'Employ knowledge or tools for a specific purpose', 'Use this concept to...'),
('apply', 'demonstrate', 'Show how something works through action', 'Demonstrate how...'),
('apply', 'solve', 'Find a solution to a problem using learned methods', 'Solve this problem...'),
('apply', 'calculate', 'Compute numerical results using procedures', 'Calculate the...'),
('apply', 'operate', 'Make something work or function', 'How would you operate...?'),
('apply', 'construct', 'Build or create using established procedures', 'Construct a...'),
('apply', 'modify', 'Change or adapt something for a new purpose', 'Modify this to...'),
('apply', 'prepare', 'Make ready for use by applying learned procedures', 'Prepare a...'),
('apply', 'produce', 'Generate an output using learned techniques', 'Produce a...');

-- ============================================================================
-- ANALYZE LEVEL
-- Definition: Break material into parts; determine how parts relate to one another
-- ============================================================================

INSERT INTO bloom_verbs (bloom_level, verb, definition, example_question_stem) VALUES
('analyze', 'differentiate', 'Distinguish between different parts or elements', 'What is the difference between...?'),
('analyze', 'organize', 'Arrange elements into categories or structures', 'Organize these elements by...'),
('analyze', 'attribute', 'Determine point of view, values, or intent behind material', 'What is the author''s perspective...?'),
('analyze', 'compare', 'Identify both similarities and differences systematically', 'Compare and contrast...'),
('analyze', 'contrast', 'Identify and explain differences between items', 'How does X differ from Y...?'),
('analyze', 'deconstruct', 'Break complex material down into component parts', 'Break this down into...'),
('analyze', 'examine', 'Inspect or investigate closely and methodically', 'Examine the relationship between...'),
('analyze', 'categorize', 'Sort items into defined groups or classes', 'Categorize these by...'),
('analyze', 'investigate', 'Conduct a systematic inquiry into causes or patterns', 'Investigate why...'),
('analyze', 'distinguish', 'Recognize differences between similar items', 'Distinguish between...'),
('analyze', 'separate', 'Divide into constituent parts', 'Separate the components of...'),
('analyze', 'integrate', 'Combine parts to see relationships', 'How do these parts integrate...?');

-- ============================================================================
-- EVALUATE LEVEL
-- Definition: Make judgments based on criteria and standards
-- ============================================================================

INSERT INTO bloom_verbs (bloom_level, verb, definition, example_question_stem) VALUES
('evaluate', 'critique', 'Analyze and judge strengths and weaknesses', 'Critique this approach...'),
('evaluate', 'judge', 'Form an opinion or conclusion based on criteria', 'Judge the effectiveness of...'),
('evaluate', 'assess', 'Determine the value, quality, or importance of something', 'Assess whether...'),
('evaluate', 'evaluate', 'Make judgments about value based on standards', 'Evaluate the success of...'),
('evaluate', 'justify', 'Provide sound reasons or evidence for a decision', 'Justify your position on...'),
('evaluate', 'argue', 'Present a logical case for or against a position', 'Argue for or against...'),
('evaluate', 'defend', 'Support a position with reasoned arguments', 'Defend your choice of...'),
('evaluate', 'appraise', 'Estimate the value or quality of something', 'What is your assessment of...?'),
('evaluate', 'prioritize', 'Rank in order of importance based on criteria', 'Prioritize these factors...'),
('evaluate', 'recommend', 'Suggest a course of action based on evaluation', 'What would you recommend...?'),
('evaluate', 'conclude', 'Reach a reasoned judgment or decision', 'What can you conclude about...?'),
('evaluate', 'support', 'Provide evidence or arguments in favor of a position', 'Support or refute the claim that...');

-- ============================================================================
-- CREATE LEVEL
-- Definition: Put elements together to form a novel, coherent whole; reorganize into a new pattern
-- ============================================================================

INSERT INTO bloom_verbs (bloom_level, verb, definition, example_question_stem) VALUES
('create', 'design', 'Plan and construct something new to meet specifications', 'Design a solution that...'),
('create', 'construct', 'Build or assemble into a new whole', 'Construct a model of...'),
('create', 'plan', 'Develop a detailed method or strategy for a task', 'Plan an approach to...'),
('create', 'produce', 'Generate a novel output or product', 'Produce a new...'),
('create', 'invent', 'Create something entirely new and original', 'Invent a way to...'),
('create', 'devise', 'Think up or contrive a new method or solution', 'Devise a strategy for...'),
('create', 'formulate', 'Express precisely or develop systematically', 'Formulate a hypothesis about...'),
('create', 'compose', 'Create by putting parts together in original ways', 'Compose a solution using...'),
('create', 'generate', 'Produce new ideas, alternatives, or hypotheses', 'Generate alternatives for...'),
('create', 'hypothesize', 'Propose an explanation or prediction to be tested', 'Hypothesize what would happen if...'),
('create', 'propose', 'Put forward a plan or idea for consideration', 'Propose a model that...'),
('create', 'synthesize', 'Combine elements to form a coherent new pattern', 'Synthesize these concepts into...');
