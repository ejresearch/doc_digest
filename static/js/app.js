// State
let currentResults = null;

// DOM Elements
const uploadForm = document.getElementById('uploadForm');
const fileInput = document.getElementById('fileInput');
const dropZone = document.getElementById('dropZone');
const fileName = document.getElementById('fileName');
const uploadSection = document.getElementById('uploadSection');
const processingStatus = document.getElementById('processingStatus');
const resultsSection = document.getElementById('resultsSection');
const newAnalysisBtn = document.getElementById('newAnalysisBtn');
const copyJsonBtn = document.getElementById('copyJsonBtn');

// Load existing chapters on page load
async function loadExistingChapters() {
    try {
        const response = await fetch('/chapters/list');
        const data = await response.json();
        const container = document.getElementById('existingChapters');

        if (data.chapters && data.chapters.length > 0) {
            container.innerHTML = data.chapters.map(chapter => `
                <div style="padding: 16px; background: var(--gray-50); border-radius: 8px; border: 1px solid var(--gray-200); cursor: pointer; transition: all 0.2s ease;"
                     onclick="loadChapter('${chapter.filename}')"
                     onmouseover="this.style.background='white'; this.style.borderColor='var(--primary)'"
                     onmouseout="this.style.background='var(--gray-50)'; this.style.borderColor='var(--gray-200)'">
                    <div style="display: flex; justify-content: space-between; align-items: start;">
                        <div>
                            <strong style="color: var(--primary);">${chapter.chapter_id || 'Unknown'}</strong>
                            <p style="font-size: 14px; color: var(--gray-600); margin-top: 4px;">${chapter.source_text || 'No source'}</p>
                            <p style="font-size: 12px; color: var(--gray-600); margin-top: 4px;">Version: ${chapter.version || 'N/A'}</p>
                        </div>
                        <span style="background: var(--primary); color: white; padding: 4px 12px; border-radius: 12px; font-size: 12px; font-weight: 600;">View</span>
                    </div>
                </div>
            `).join('');
        } else {
            container.innerHTML = '<p style="color: var(--gray-600); text-align: center; padding: 24px;">No existing analyses found</p>';
        }
    } catch (error) {
        console.error('Error loading chapters:', error);
        document.getElementById('existingChapters').innerHTML = '<p style="color: var(--danger); text-align: center;">Failed to load existing chapters</p>';
    }
}

// Load a specific chapter by filename
async function loadChapter(filename) {
    try {
        const response = await fetch(`/chapters/${filename}`);
        if (!response.ok) {
            throw new Error('Failed to load chapter');
        }
        const data = await response.json();
        currentResults = data;
        showResults(data);
    } catch (error) {
        alert(`Error loading chapter: ${error.message}`);
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    loadExistingChapters();
});

// File Upload Handling
dropZone.addEventListener('click', () => fileInput.click());

dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.style.borderColor = 'var(--primary)';
    dropZone.style.background = 'white';
});

dropZone.addEventListener('dragleave', () => {
    dropZone.style.borderColor = 'var(--gray-300)';
    dropZone.style.background = 'var(--gray-50)';
});

dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.style.borderColor = 'var(--gray-300)';
    dropZone.style.background = 'var(--gray-50)';

    const files = e.dataTransfer.files;
    if (files.length > 0) {
        fileInput.files = files;
        updateFileName(files[0].name);
    }
});

fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        updateFileName(e.target.files[0].name);
    }
});

function updateFileName(name) {
    fileName.textContent = `Selected: ${name}`;
    fileName.classList.add('show');
}

// Form Submission
uploadForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    const formData = new FormData();
    formData.append('file', fileInput.files[0]);
    formData.append('chapter_id', document.getElementById('chapterId').value);
    formData.append('version', document.getElementById('version').value);
    formData.append('source_text', document.getElementById('sourceText').value || '');
    formData.append('author_or_editor', document.getElementById('author').value || '');

    // Show processing status
    uploadForm.style.display = 'none';
    processingStatus.classList.remove('hidden');

    try {
        const response = await fetch('/chapters/digest', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Analysis failed');
        }

        const results = await response.json();
        currentResults = results;

        // Show results
        showResults(results);

    } catch (error) {
        alert(`Error: ${error.message}`);
        uploadForm.style.display = 'block';
        processingStatus.classList.add('hidden');
    }
});

// Show Results
function showResults(data) {
    uploadSection.style.display = 'none';
    resultsSection.classList.remove('hidden');

    renderOverview(data);
    renderMetadata(data);
    renderComprehension(data);
    renderOutline(data);
    renderPropositions(data);
    renderAnalytics(data);
    renderPedagogy(data);
    renderActivities(data);
    renderQuestions(data);
    renderReview(data);
    renderVisual(data);
    renderTemporal(data);
    renderHistorical(data);
    renderContemporary(data);
    renderRawJson(data);
}

// Render Overview Tab
function renderOverview(data) {
    // Chapter Info
    const chapterInfo = document.getElementById('chapterInfo');
    chapterInfo.innerHTML = `
        <p><strong>Chapter ID:</strong> ${data.system_metadata?.chapter_id || 'N/A'}</p>
        <p><strong>Version:</strong> ${data.system_metadata?.version || 'N/A'}</p>
        <p><strong>Source:</strong> ${data.system_metadata?.source_text || 'N/A'}</p>
        <p><strong>Author:</strong> ${data.system_metadata?.author_or_editor || 'Unknown'}</p>
    `;

    // Quick Stats
    const quickStats = document.getElementById('quickStats');
    const propCount = data.propositional_extraction?.propositions?.length || 0;
    const objectiveCount = data.pedagogical_mapping?.learning_objectives?.length || 0;
    const activityCount = data.pedagogical_mapping?.student_activities?.length || 0;

    quickStats.innerHTML = `
        <p><strong>Learning Objectives:</strong> ${objectiveCount}</p>
        <p><strong>Student Activities:</strong> ${activityCount}</p>
        <p><strong>Propositions:</strong> ${propCount}</p>
        <p><strong>Subject:</strong> ${data.analytical_metadata?.subject_domain || 'N/A'}</p>
    `;

    // Key Concepts
    const keyConcepts = document.getElementById('keyConcepts');
    const concepts = data.comprehension_pass?.what || [];
    if (concepts.length > 0) {
        keyConcepts.innerHTML = concepts.slice(0, 5).map(concept => `
            <div class="list-item">
                <strong>${concept.concept_or_topic}</strong>
                <p style="margin-top: 4px; font-size: 14px; color: var(--gray-600);">${concept.definition_or_description || ''}</p>
            </div>
        `).join('');
    } else {
        keyConcepts.innerHTML = '<p>No concepts extracted</p>';
    }
}

// Render Metadata Tab
function renderMetadata(data) {
    const metadata = document.getElementById('metadataContent');
    const meta = data.system_metadata || {};

    metadata.innerHTML = `
        <div style="display: grid; gap: 16px;">
            <div class="list-item">
                <strong>Chapter ID:</strong>
                <p style="margin-top: 4px;">${meta.chapter_id || 'N/A'}</p>
            </div>
            <div class="list-item">
                <strong>File Name:</strong>
                <p style="margin-top: 4px;">${meta.file_name || 'N/A'}</p>
            </div>
            <div class="list-item">
                <strong>Author/Editor:</strong>
                <p style="margin-top: 4px;">${meta.author_or_editor || 'Unknown'}</p>
            </div>
            <div class="list-item">
                <strong>Version:</strong>
                <p style="margin-top: 4px;">${meta.version || 'N/A'}</p>
            </div>
            <div class="list-item">
                <strong>Created At:</strong>
                <p style="margin-top: 4px;">${meta.created_at || 'N/A'}</p>
            </div>
            <div class="list-item">
                <strong>Source Text:</strong>
                <p style="margin-top: 4px;">${meta.source_text || 'N/A'}</p>
            </div>
        </div>
    `;
}

// Render Comprehension Tab
function renderComprehension(data) {
    const comp = data.comprehension_pass || {};

    // Who
    const who = document.getElementById('comprehensionWho');
    if (comp.who && comp.who.length > 0) {
        who.innerHTML = comp.who.map(item => `
            <div class="list-item" style="margin-bottom: 12px;">
                <strong>${item.entity}</strong>
                ${item.role_or_function ? `<p style="margin-top: 4px;"><em>Role:</em> ${item.role_or_function}</p>` : ''}
                ${item.significance_in_chapter ? `<p style="margin-top: 4px;"><em>Significance:</em> ${item.significance_in_chapter}</p>` : ''}
                ${item.evidence_pointer ? `<p style="margin-top: 4px; font-size: 13px; color: var(--gray-600);">📍 ${item.evidence_pointer}</p>` : ''}
            </div>
        `).join('');
    } else {
        who.innerHTML = '<p style="color: var(--gray-600);">No entities found</p>';
    }

    // What
    const what = document.getElementById('comprehensionWhat');
    if (comp.what && comp.what.length > 0) {
        what.innerHTML = comp.what.map(item => `
            <div class="list-item" style="margin-bottom: 12px;">
                <strong>${item.concept_or_topic}</strong>
                ${item.definition_or_description ? `<p style="margin-top: 4px;">${item.definition_or_description}</p>` : ''}
                ${item.importance ? `<p style="margin-top: 4px;"><em>Importance:</em> ${item.importance}</p>` : ''}
                ${item.evidence_pointer ? `<p style="margin-top: 4px; font-size: 13px; color: var(--gray-600);">📍 ${item.evidence_pointer}</p>` : ''}
            </div>
        `).join('');
    } else {
        what.innerHTML = '<p style="color: var(--gray-600);">No concepts found</p>';
    }

    // When
    const when = document.getElementById('comprehensionWhen');
    const whenBlock = comp.when || {};
    when.innerHTML = `
        <div class="list-item" style="margin-bottom: 12px;">
            <strong>Historical/Cultural Context:</strong>
            <p style="margin-top: 4px;">${whenBlock.historical_or_cultural_context || 'N/A'}</p>
        </div>
        <div class="list-item" style="margin-bottom: 12px;">
            <strong>Chronological Sequence:</strong>
            <p style="margin-top: 4px;">${whenBlock.chronological_sequence_within_course || 'N/A'}</p>
        </div>
        <div class="list-item">
            <strong>Moment of Presentation:</strong>
            <p style="margin-top: 4px;">${whenBlock.moment_of_presentation_to_reader || 'N/A'}</p>
        </div>
    `;

    // Why
    const why = document.getElementById('comprehensionWhy');
    const whyBlock = comp.why || {};
    why.innerHTML = `
        <div class="list-item" style="margin-bottom: 12px;">
            <strong>Intellectual Value:</strong>
            <p style="margin-top: 4px;">${whyBlock.intellectual_value || 'N/A'}</p>
        </div>
        <div class="list-item" style="margin-bottom: 12px;">
            <strong>Knowledge-Based Value:</strong>
            <p style="margin-top: 4px;">${whyBlock.knowledge_based_value || 'N/A'}</p>
        </div>
        <div class="list-item">
            <strong>Moral/Philosophical Significance:</strong>
            <p style="margin-top: 4px;">${whyBlock.moral_or_philosophical_significance || 'N/A'}</p>
        </div>
    `;

    // How
    const how = document.getElementById('comprehensionHow');
    const howBlock = comp.how || {};
    how.innerHTML = `
        <div class="list-item" style="margin-bottom: 12px;">
            <strong>Presentation Style:</strong>
            <p style="margin-top: 4px;">${howBlock.presentation_style || 'N/A'}</p>
        </div>
        <div class="list-item" style="margin-bottom: 12px;">
            <strong>Rhetorical Approach:</strong>
            <p style="margin-top: 4px;">${howBlock.rhetorical_approach || 'N/A'}</p>
        </div>
        <div class="list-item">
            <strong>Recommended Student Strategy:</strong>
            <p style="margin-top: 4px;">${howBlock.recommended_student_strategy || 'N/A'}</p>
        </div>
    `;
}

// Render Outline Tab
function renderOutline(data) {
    const outline = document.getElementById('outlineContent');
    const struct = data.structural_outline || {};
    const sections = struct.outline || [];

    if (sections.length > 0) {
        outline.innerHTML = `
            <h4 style="margin-bottom: 16px; font-size: 20px;">${struct.chapter_title || 'Chapter'}</h4>
            ${struct.guiding_context_questions && struct.guiding_context_questions.length > 0 ? `
                <div class="list-item" style="margin-bottom: 24px;">
                    <strong>Guiding Questions:</strong>
                    <ul style="margin-top: 8px; padding-left: 20px;">
                        ${struct.guiding_context_questions.map(q => `<li style="margin-bottom: 4px;">${q}</li>`).join('')}
                    </ul>
                </div>
            ` : ''}
            ${sections.map((section, i) => `
                <div style="margin-bottom: 24px; padding: 16px; background: white; border-radius: 8px; border-left: 4px solid var(--primary);">
                    <h5 style="margin-bottom: 8px; font-size: 18px;">${i + 1}. ${section.section_title}</h5>
                    ${section.section_summary ? `<p style="font-size: 14px; color: var(--gray-600); margin-bottom: 8px;">${section.section_summary}</p>` : ''}
                    ${section.pedagogical_purpose ? `<p style="font-size: 14px; margin-bottom: 8px;"><strong>Purpose:</strong> ${section.pedagogical_purpose}</p>` : ''}
                    ${section.rhetorical_mode ? `<p style="font-size: 13px; color: var(--gray-600); margin-bottom: 8px;"><em>Mode: ${section.rhetorical_mode}</em></p>` : ''}
                    ${section.subtopics && section.subtopics.length > 0 ? `
                        <div style="margin-top: 12px;">
                            <strong style="font-size: 14px;">Subtopics:</strong>
                            ${section.subtopics.map(sub => `
                                <div style="margin: 8px 0 8px 16px; padding: 8px; background: var(--gray-50); border-radius: 6px;">
                                    <div style="font-weight: 600;">${sub.subtopic_title}</div>
                                    ${sub.key_concepts && sub.key_concepts.length > 0 ? `
                                        <div style="margin-top: 4px; font-size: 13px;">
                                            <em>Key concepts:</em> ${sub.key_concepts.join(', ')}
                                        </div>
                                    ` : ''}
                                    ${sub.supporting_examples && sub.supporting_examples.length > 0 ? `
                                        <div style="margin-top: 4px; font-size: 13px;">
                                            <em>Examples:</em> ${sub.supporting_examples.join(', ')}
                                        </div>
                                    ` : ''}
                                </div>
                            `).join('')}
                        </div>
                    ` : ''}
                </div>
            `).join('')}
        `;
    } else {
        outline.innerHTML = '<p style="color: var(--gray-600);">No outline available</p>';
    }
}

// Render Analytics Tab
function renderAnalytics(data) {
    const analytics = document.getElementById('analyticsContent');
    const meta = data.analytical_metadata || {};

    analytics.innerHTML = `
        <div style="display: grid; gap: 16px;">
            <div class="list-item">
                <strong>Subject Domain:</strong>
                <p style="margin-top: 4px;">${meta.subject_domain || 'N/A'}</p>
            </div>
            <div class="list-item">
                <strong>Curriculum Unit:</strong>
                <p style="margin-top: 4px;">${meta.curriculum_unit || 'N/A'}</p>
            </div>
            <div class="list-item">
                <strong>Disciplinary Lens:</strong>
                <p style="margin-top: 4px;">${meta.disciplinary_lens || 'N/A'}</p>
            </div>
            <div class="list-item">
                <strong>Grade Level/Audience:</strong>
                <p style="margin-top: 4px;">${meta.grade_level_or_audience || 'N/A'}</p>
            </div>
            <div class="list-item">
                <strong>Spiral Position:</strong>
                <p style="margin-top: 4px;">${meta.spiral_position || 'N/A'}</p>
            </div>
            ${meta.related_chapters && meta.related_chapters.length > 0 ? `
                <div class="list-item">
                    <strong>Related Chapters:</strong>
                    <ul style="margin-top: 8px; padding-left: 20px;">
                        ${meta.related_chapters.map(ch => `<li>${ch}</li>`).join('')}
                    </ul>
                </div>
            ` : ''}
        </div>
    `;
}

// Render Pedagogy Tab
function renderPedagogy(data) {
    const ped = data.pedagogical_mapping || {};

    // Learning Objectives
    const objectives = document.getElementById('pedagogyObjectives');
    if (ped.learning_objectives && ped.learning_objectives.length > 0) {
        objectives.innerHTML = '<ol style="padding-left: 20px;">' +
            ped.learning_objectives.map(obj => `<li style="margin-bottom: 8px;">${obj}</li>`).join('') +
            '</ol>';
    } else {
        objectives.innerHTML = '<p style="color: var(--gray-600);">No learning objectives found</p>';
    }

    // Chapter Summary
    const summary = document.getElementById('pedagogySummary');
    if (ped.chapter_summary) {
        summary.innerHTML = `<p>${ped.chapter_summary}</p>`;
    } else {
        summary.innerHTML = '<p style="color: var(--gray-600);">No chapter summary available</p>';
    }

    // Discussion Questions
    const discussion = document.getElementById('pedagogyDiscussion');
    if (ped.potential_discussion_questions && ped.potential_discussion_questions.length > 0) {
        discussion.innerHTML = '<ol style="padding-left: 20px;">' +
            ped.potential_discussion_questions.map(q => `<li style="margin-bottom: 8px;">${q}</li>`).join('') +
            '</ol>';
    } else {
        discussion.innerHTML = '<p style="color: var(--gray-600);">No discussion questions generated</p>';
    }
}

// Render Activities Tab
function renderActivities(data) {
    const activities = document.getElementById('activitiesContent');
    const acts = data.pedagogical_mapping?.student_activities || [];

    if (acts.length > 0) {
        activities.innerHTML = acts.map(activity => `
            <div class="activity-item">
                <span class="item-badge">${activity.activity_type || 'Activity'}</span>
                <p>${activity.description || ''}</p>
                ${activity.location ? `<p class="item-location">📍 ${activity.location}</p>` : ''}
            </div>
        `).join('');
    } else {
        activities.innerHTML = '<p style="color: var(--gray-600);">No student activities found</p>';
    }
}

// Render Questions Tab
function renderQuestions(data) {
    const questions = document.getElementById('questionsContent');
    const qs = data.pedagogical_mapping?.assessment_questions || [];

    if (qs.length > 0) {
        questions.innerHTML = qs.map(q => `
            <div class="question-item">
                <span class="item-badge">${q.question_type || 'Question'}</span>
                <p><strong>Q:</strong> ${q.question || ''}</p>
                ${q.location ? `<p class="item-location">📍 ${q.location}</p>` : ''}
            </div>
        `).join('');
    } else {
        questions.innerHTML = '<p style="color: var(--gray-600);">No assessment questions found</p>';
    }
}

// Render Review Tab
function renderReview(data) {
    const review = document.getElementById('reviewContent');
    const reviews = data.pedagogical_mapping?.review_sections || [];

    if (reviews.length > 0) {
        review.innerHTML = reviews.map(r => `
            <div class="list-item" style="margin-bottom: 12px;">
                <p>${r.content || ''}</p>
                ${r.location ? `<p class="item-location">📍 ${r.location}</p>` : ''}
            </div>
        `).join('');
    } else {
        review.innerHTML = '<p style="color: var(--gray-600);">No review sections found</p>';
    }
}

// Render Visual Media Tab
function renderVisual(data) {
    const visual = document.getElementById('visualContent');
    const media = data.pedagogical_mapping?.visual_media_references || [];

    if (media.length > 0) {
        visual.innerHTML = media.map(v => `
            <div class="list-item" style="margin-bottom: 12px;">
                <strong>${v.reference || 'Visual'}</strong>
                <p style="margin-top: 4px; font-size: 14px;">${v.description || ''}</p>
                ${v.pedagogical_purpose ? `<p style="margin-top: 4px; font-size: 13px; color: var(--gray-600);"><em>Purpose: ${v.pedagogical_purpose}</em></p>` : ''}
            </div>
        `).join('');
    } else {
        visual.innerHTML = '<p style="color: var(--gray-600);">No visual media references found</p>';
    }
}

// Render Propositions Tab
function renderPropositions(data) {
    const propositions = document.getElementById('propositionsList');
    const props = data.propositional_extraction?.propositions || [];

    if (props.length > 0) {
        propositions.innerHTML = props.map((prop, i) => `
            <div class="list-item" style="margin-bottom: 16px;">
                <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
                    <span style="background: var(--primary); color: white; padding: 2px 8px; border-radius: 4px; font-size: 12px; font-weight: 600;">#${i + 1}</span>
                    ${prop.truth_type ? `<span style="background: var(--gray-200); padding: 2px 8px; border-radius: 4px; font-size: 12px;">${prop.truth_type}</span>` : ''}
                </div>
                <p><strong>${prop.statement}</strong></p>
                ${prop.evidence_from_text ? `<p style="margin-top: 8px; font-size: 14px; color: var(--gray-600);">${prop.evidence_from_text}</p>` : ''}
                ${prop.implication_for_learning ? `<p style="margin-top: 8px; font-size: 14px; font-style: italic;">💡 ${prop.implication_for_learning}</p>` : ''}
            </div>
        `).join('');
    } else {
        propositions.innerHTML = '<p style="color: var(--gray-600);">No propositions extracted</p>';
    }
}

// Render Temporal Tab
function renderTemporal(data) {
    const temporal = document.getElementById('temporalContent');
    const temp = data.pedagogical_mapping?.temporal_analysis || {};

    if (temp.temporal_range) {
        temporal.innerHTML = `
            <div class="list-item">
                <p style="font-size: 18px; font-weight: 600; color: var(--primary);">
                    ${temp.temporal_range}
                </p>
                <p style="font-size: 14px; color: var(--gray-600); margin-top: 8px;">
                    This chapter spans content from ${temp.temporal_range}
                </p>
            </div>
        `;
    } else {
        temporal.innerHTML = '<p style="color: var(--gray-600);">No temporal range information available</p>';
    }
}

// Render Historical Tab
function renderHistorical(data) {
    const historical = document.getElementById('historicalContent');
    const examples = data.pedagogical_mapping?.temporal_analysis?.historical_examples || [];

    if (examples.length > 0) {
        historical.innerHTML = examples.map(ex => `
            <div class="example-item">
                <p><strong>${ex.example}</strong></p>
                <p style="font-size: 14px; color: var(--gray-600); margin-top: 4px;">📅 ${ex.time_period || 'Unknown period'}</p>
                ${ex.still_relevant !== undefined ? `
                    <p style="font-size: 13px; margin-top: 4px;">
                        ${ex.still_relevant ? '✅ Still relevant' : '⚠️ May be outdated'}
                    </p>
                ` : ''}
            </div>
        `).join('');
    } else {
        historical.innerHTML = '<p style="color: var(--gray-600);">No historical examples found</p>';
    }
}

// Render Contemporary Tab
function renderContemporary(data) {
    const contemporary = document.getElementById('contemporaryContent');
    const examples = data.pedagogical_mapping?.temporal_analysis?.contemporary_examples || [];

    if (examples.length > 0) {
        contemporary.innerHTML = examples.map(ex => `
            <div class="example-item">
                <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 8px;">
                    <p><strong>${ex.example}</strong></p>
                    ${ex.update_priority ? `
                        <span class="item-badge priority-${ex.update_priority}">
                            ${ex.update_priority.toUpperCase()} PRIORITY
                        </span>
                    ` : ''}
                </div>
                <p style="font-size: 14px; color: var(--gray-600);">📅 Current as of: ${ex.current_as_of || 'Unknown'}</p>
            </div>
        `).join('');
    } else {
        contemporary.innerHTML = '<p style="color: var(--gray-600);">No contemporary examples found</p>';
    }
}

// Render Raw JSON Tab
function renderRawJson(data) {
    const rawJson = document.getElementById('rawJson');
    rawJson.textContent = JSON.stringify(data, null, 2);
}

// Tab Switching
document.querySelectorAll('.tab').forEach(tab => {
    tab.addEventListener('click', () => {
        const target = tab.dataset.tab;

        // Update active tab
        document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
        tab.classList.add('active');

        // Update active panel
        document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
        document.getElementById(target).classList.add('active');
    });
});

// Copy JSON Button
copyJsonBtn.addEventListener('click', () => {
    const text = document.getElementById('rawJson').textContent;
    navigator.clipboard.writeText(text).then(() => {
        const originalText = copyJsonBtn.textContent;
        copyJsonBtn.textContent = 'Copied!';
        setTimeout(() => {
            copyJsonBtn.textContent = originalText;
        }, 2000);
    });
});

// New Analysis Button
newAnalysisBtn.addEventListener('click', () => {
    resultsSection.classList.add('hidden');
    uploadSection.style.display = 'block';
    uploadForm.style.display = 'block';
    processingStatus.classList.add('hidden');
    uploadForm.reset();
    fileName.classList.remove('show');
});
