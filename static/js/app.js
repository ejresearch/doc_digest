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
    renderPedagogical(data);
    renderStructure(data);
    renderPropositions(data);
    renderTemporal(data);
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

// Render Pedagogical Tab
function renderPedagogical(data) {
    const ped = data.pedagogical_mapping || {};

    // Learning Objectives
    const objectives = document.getElementById('learningObjectives');
    if (ped.learning_objectives && ped.learning_objectives.length > 0) {
        objectives.innerHTML = '<ol style="padding-left: 20px;">' +
            ped.learning_objectives.map(obj => `<li style="margin-bottom: 8px;">${obj}</li>`).join('') +
            '</ol>';
    } else {
        objectives.innerHTML = '<p style="color: var(--gray-600);">No learning objectives found</p>';
    }

    // Student Activities
    const activities = document.getElementById('studentActivities');
    if (ped.student_activities && ped.student_activities.length > 0) {
        activities.innerHTML = ped.student_activities.map(activity => `
            <div class="activity-item">
                <span class="item-badge">${activity.activity_type || 'Activity'}</span>
                <p>${activity.description || ''}</p>
                ${activity.location ? `<p class="item-location">📍 ${activity.location}</p>` : ''}
            </div>
        `).join('');
    } else {
        activities.innerHTML = '<p style="color: var(--gray-600);">No student activities found</p>';
    }

    // Assessment Questions
    const assessments = document.getElementById('assessmentQuestions');
    if (ped.assessment_questions && ped.assessment_questions.length > 0) {
        assessments.innerHTML = ped.assessment_questions.map(q => `
            <div class="question-item">
                <span class="item-badge">${q.question_type || 'Question'}</span>
                <p><strong>Q:</strong> ${q.question || ''}</p>
                ${q.location ? `<p class="item-location">📍 ${q.location}</p>` : ''}
            </div>
        `).join('');
    } else {
        assessments.innerHTML = '<p style="color: var(--gray-600);">No assessment questions found</p>';
    }

    // Visual Media
    const visual = document.getElementById('visualMedia');
    if (ped.visual_media_references && ped.visual_media_references.length > 0) {
        visual.innerHTML = ped.visual_media_references.map(v => `
            <div class="list-item">
                <strong>${v.reference || 'Visual'}</strong>
                <p style="margin-top: 4px; font-size: 14px;">${v.description || ''}</p>
                ${v.pedagogical_purpose ? `<p style="margin-top: 4px; font-size: 13px; color: var(--gray-600);"><em>Purpose: ${v.pedagogical_purpose}</em></p>` : ''}
            </div>
        `).join('');
    } else {
        visual.innerHTML = '<p style="color: var(--gray-600);">No visual media references found</p>';
    }

    // Discussion Questions
    const discussion = document.getElementById('discussionQuestions');
    if (ped.potential_discussion_questions && ped.potential_discussion_questions.length > 0) {
        discussion.innerHTML = '<ol style="padding-left: 20px;">' +
            ped.potential_discussion_questions.map(q => `<li style="margin-bottom: 8px;">${q}</li>`).join('') +
            '</ol>';
    } else {
        discussion.innerHTML = '<p style="color: var(--gray-600);">No discussion questions generated</p>';
    }
}

// Render Structure Tab
function renderStructure(data) {
    const structure = document.getElementById('structureOutline');
    const outline = data.structural_outline?.outline || [];

    if (outline.length > 0) {
        structure.innerHTML = `
            <h4 style="margin-bottom: 16px;">${data.structural_outline?.chapter_title || 'Chapter'}</h4>
            ${outline.map((section, i) => `
                <div style="margin-bottom: 24px; padding-left: 16px; border-left: 3px solid var(--primary);">
                    <h5 style="margin-bottom: 8px;">${i + 1}. ${section.section_title}</h5>
                    <p style="font-size: 14px; color: var(--gray-600); margin-bottom: 8px;">${section.section_summary || ''}</p>
                    ${section.subtopics && section.subtopics.length > 0 ? `
                        <ul style="margin-left: 20px; font-size: 14px;">
                            ${section.subtopics.map(sub => `<li>${sub.subtopic_title}</li>`).join('')}
                        </ul>
                    ` : ''}
                </div>
            `).join('')}
        `;
    } else {
        structure.innerHTML = '<p style="color: var(--gray-600);">No structural outline available</p>';
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

// Render Temporal Analysis Tab
function renderTemporal(data) {
    const temporal = data.pedagogical_mapping?.temporal_analysis || {};

    // Historical Examples
    const historical = document.getElementById('historicalExamples');
    if (temporal.historical_examples && temporal.historical_examples.length > 0) {
        historical.innerHTML = temporal.historical_examples.map(ex => `
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

    // Contemporary Examples
    const contemporary = document.getElementById('contemporaryExamples');
    if (temporal.contemporary_examples && temporal.contemporary_examples.length > 0) {
        contemporary.innerHTML = temporal.contemporary_examples.map(ex => `
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

    // Temporal Range
    const range = document.getElementById('temporalRange');
    if (temporal.temporal_range) {
        range.innerHTML = `
            <p style="font-size: 18px; font-weight: 600; color: var(--primary);">
                ${temporal.temporal_range}
            </p>
            <p style="font-size: 14px; color: var(--gray-600); margin-top: 8px;">
                This chapter spans content from ${temporal.temporal_range}
            </p>
        `;
    } else {
        range.innerHTML = '<p style="color: var(--gray-600);">No temporal range information</p>';
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
