// State
let currentResults = null;

// Theme handling
const themeToggle = document.getElementById('themeToggle');

function setTheme(theme) {
    if (theme === 'dark') {
        document.documentElement.classList.add('dark');
        localStorage.theme = 'dark';
    } else {
        document.documentElement.classList.remove('dark');
        localStorage.theme = 'light';
    }
}

if (themeToggle) {
    themeToggle.addEventListener('click', () => {
        if (document.documentElement.classList.contains('dark')) {
            setTheme('light');
        } else {
            setTheme('dark');
        }
    });
}

// DOM Elements
const uploadForm = document.getElementById('uploadForm');
const fileInput = document.getElementById('fileInput');
const dropZone = document.getElementById('dropZone');
const fileName = document.getElementById('fileName');
const uploadSection = document.getElementById('uploadSection');
const processingStatus = document.getElementById('processingStatus');
const resultsSection = document.getElementById('resultsSection');
const newAnalysisBtn = document.getElementById('newAnalysisBtn');
const homeBtn = document.getElementById('homeBtn');
const copyJsonBtn = document.getElementById('copyJsonBtn');

// Load existing chapters
async function loadExistingChapters() {
    try {
        const response = await fetch('/chapters/list');
        const data = await response.json();
        const container = document.getElementById('existingChapters');

        if (data.chapters && data.chapters.length > 0) {
            container.innerHTML = data.chapters.map(chapter => `
                <div class="group relative w-full">
                    <button onclick="loadChapter('${chapter.filename}')" class="w-full text-left px-4 py-3 bg-gray-50 dark:bg-gray-700 hover:bg-gray-100 dark:hover:bg-gray-600 rounded-lg border border-gray-200 dark:border-gray-600 transition-colors">
                        <div class="font-semibold text-sm text-gray-900 dark:text-white">${chapter.chapter_id || 'Unknown'}</div>
                        <div class="text-xs text-gray-500 dark:text-gray-400 mt-1">${chapter.source_text || 'No source'} • v${chapter.version || 'N/A'}</div>
                    </button>
                    <button onclick="event.stopPropagation(); deleteChapter('${chapter.filename}')" class="absolute top-1/2 -translate-y-1/2 right-2 opacity-0 group-hover:opacity-100 p-2 text-gray-400 hover:text-red-500 dark:text-gray-500 dark:hover:text-red-400 rounded-lg transition-all hover:bg-gray-200 dark:hover:bg-gray-600" title="Delete this analysis">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                        </svg>
                    </button>
                </div>
            `).join('');
        } else {
            container.innerHTML = '<p class="text-sm text-gray-500 dark:text-gray-400 text-center py-4">No analyses yet</p>';
        }
    } catch (error) {
        console.error('Error loading chapters:', error);
    }
}

// Delete chapter
window.deleteChapter = async function(filename) {
    if (!confirm('Are you sure you want to delete this analysis? This action cannot be undone.')) {
        return;
    }

    try {
        const response = await fetch(`/chapters/${filename}`, {
            method: 'DELETE'
        });

        if (!response.ok) {
            throw new Error('Failed to delete chapter');
        }

        // Reload the list
        await loadExistingChapters();

        // Show success message
        alert('Analysis deleted successfully!');
    } catch (error) {
        alert(`Error deleting chapter: ${error.message}`);
        console.error('Delete error:', error);
    }
};

// Load specific chapter
window.loadChapter = async function(filename) {
    try {
        const response = await fetch(`/chapters/${filename}`);
        if (!response.ok) throw new Error('Failed to load chapter');

        const data = await response.json();
        currentResults = data;
        showResults(data);
    } catch (error) {
        alert(`Error loading chapter: ${error.message}`);
    }
};

// File upload handling
// Click handler to trigger file input
dropZone.addEventListener('click', (e) => {
    e.preventDefault();
    e.stopPropagation();
    fileInput.click();
});

dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    e.stopPropagation();
    dropZone.classList.add('border-blue-500', 'bg-blue-50', 'dark:bg-gray-700');
});

dropZone.addEventListener('dragleave', (e) => {
    e.preventDefault();
    e.stopPropagation();
    dropZone.classList.remove('border-blue-500', 'bg-blue-50', 'dark:bg-gray-700');
});

dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    e.stopPropagation();
    dropZone.classList.remove('border-blue-500', 'bg-blue-50', 'dark:bg-gray-700');

    const files = e.dataTransfer.files;
    if (files.length > 0) {
        fileInput.files = files;
        updateFileName(files[0].name);
    }
});

fileInput.addEventListener('change', (e) => {
    console.log('File input change event triggered');
    if (e.target.files && e.target.files.length > 0) {
        console.log('File selected:', e.target.files[0].name);
        updateFileName(e.target.files[0].name);
    } else {
        console.log('No file selected');
    }
});

function updateFileName(name) {
    console.log('updateFileName called with:', name);
    if (fileName) {
        fileName.textContent = `✓ Selected: ${name}`;
        fileName.classList.remove('hidden');
        fileName.style.display = 'block';
        console.log('File name displayed successfully');
    } else {
        console.error('fileName element not found');
    }
}

// Form submission with real-time SSE progress tracking
uploadForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    const formData = new FormData();
    formData.append('file', fileInput.files[0]);
    formData.append('chapter_id', document.getElementById('chapterId').value);
    formData.append('version', document.getElementById('version').value);
    formData.append('source_text', document.getElementById('sourceText').value || '');
    formData.append('author_or_editor', document.getElementById('author').value || '');

    // Show processing
    uploadForm.classList.add('hidden');
    processingStatus.classList.remove('hidden');

    // Reset progress UI
    updateProgress('initialization', 'Starting analysis...', 0);

    let eventSource = null;

    try {
        // Submit the form and get job_id
        const response = await fetch('/chapters/digest', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Analysis failed');
        }

        const data = await response.json();
        const jobId = data.job_id;

        if (!jobId) {
            throw new Error('No job ID returned from server');
        }

        console.log('Analysis started with job ID:', jobId);

        // Connect to SSE endpoint for real-time progress
        eventSource = new EventSource(`/chapters/progress/${jobId}`);

        eventSource.onmessage = (event) => {
            try {
                const update = JSON.parse(event.data);
                console.log('Progress update:', update);

                if (update.status === 'timeout') {
                    eventSource.close();
                    console.log('SSE stream timed out, checking if analysis completed...');

                    // Manually check for completion since timeout doesn't trigger onerror
                    setTimeout(async () => {
                        try {
                            const listResponse = await fetch('/chapters/list');
                            const listData = await listResponse.json();

                            if (listData.chapters && listData.chapters.length > 0) {
                                const latestChapter = listData.chapters[listData.chapters.length - 1];
                                const createdTime = new Date(latestChapter.created_at);
                                const now = new Date();
                                const diffMinutes = (now - createdTime) / 1000 / 60;

                                if (diffMinutes < 5) {
                                    console.log('Analysis completed! Loading results...');
                                    updateProgress('completed', 'Analysis complete!', 100);
                                    await loadChapter(latestChapter.filename);
                                    return;
                                }
                            }

                            showErrorState('Stream timed out. Please refresh to check if analysis completed.');
                        } catch (checkError) {
                            console.error('Error checking for completion:', checkError);
                            showErrorState('Stream timed out. Please refresh the page.');
                        }
                    }, 1000);
                    return;
                }

                // Update UI with real progress
                updateProgress(update.phase, update.message);

                // Check if completed
                if (update.status === 'completed') {
                    eventSource.close();

                    // Final progress update
                    updateProgress('completed', 'Analysis complete!', 100);

                    // Load the results
                    setTimeout(async () => {
                        try {
                            // Fetch updated chapter list
                            const listResponse = await fetch('/chapters/list');
                            const listData = await listResponse.json();

                            // Find the most recent chapter (should be our new one)
                            if (listData.chapters && listData.chapters.length > 0) {
                                const latestChapter = listData.chapters[listData.chapters.length - 1];
                                await loadChapter(latestChapter.filename);
                            } else {
                                throw new Error('No chapters found after analysis');
                            }
                        } catch (loadError) {
                            console.error('Error loading results:', loadError);
                            alert('Analysis completed but failed to load results. Please refresh the page.');
                            uploadForm.classList.remove('hidden');
                            processingStatus.classList.add('hidden');
                        }
                    }, 500);
                }

                // Check if error
                if (update.status === 'error') {
                    eventSource.close();
                    // Show persistent error message
                    showErrorState(update.message || 'Analysis failed');
                    return;
                }

            } catch (parseError) {
                console.error('Error parsing progress update:', parseError);
            }
        };

        eventSource.onerror = async (error) => {
            console.error('SSE error:', error);
            eventSource.close();

            // Check if analysis actually completed by fetching the chapter list
            console.log('Lost connection to progress stream, checking if analysis completed...');

            try {
                await new Promise(resolve => setTimeout(resolve, 1000)); // Wait 1 second
                const listResponse = await fetch('/chapters/list');
                const listData = await listResponse.json();

                // Find the most recent chapter (should be our new one if completed)
                if (listData.chapters && listData.chapters.length > 0) {
                    const latestChapter = listData.chapters[listData.chapters.length - 1];

                    // Check if it was created in the last 5 minutes
                    const createdTime = new Date(latestChapter.created_at);
                    const now = new Date();
                    const diffMinutes = (now - createdTime) / 1000 / 60;

                    if (diffMinutes < 5) {
                        // Analysis completed! Load the results
                        console.log('Analysis completed! Loading results...');
                        updateProgress('completed', 'Analysis complete!', 100);
                        await loadChapter(latestChapter.filename);
                        return;
                    }
                }

                // If we get here, analysis might still be running or failed
                console.warn('Could not confirm completion. Analysis may still be running or may have failed.');
                showErrorState('Connection lost. Please refresh the page to check if analysis completed.');
            } catch (checkError) {
                console.error('Error checking for completion:', checkError);
                showErrorState('Connection lost and unable to verify completion. Please refresh the page.');
            }
        };

    } catch (error) {
        console.error('Error:', error);

        if (eventSource) {
            eventSource.close();
        }

        // Show persistent error state instead of auto-hiding
        showErrorState(error.message || 'An unexpected error occurred');
    }
});

// Show persistent error state
function showErrorState(errorMessage) {
    const progressPhase = document.getElementById('progressPhase');
    const progressMessage = document.getElementById('progressMessage');
    const progressBar = document.getElementById('progressBar');
    const progressPercent = document.getElementById('progressPercent');
    const progressETA = document.getElementById('progressETA');

    // Update UI to show error
    if (progressPhase) {
        progressPhase.textContent = 'Error';
        progressPhase.className = 'text-xl font-bold text-red-600 dark:text-red-400';
    }
    if (progressMessage) {
        progressMessage.textContent = errorMessage;
        progressMessage.className = 'text-gray-700 dark:text-gray-300 mt-2 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg';
    }
    if (progressBar) {
        progressBar.style.width = '100%';
        progressBar.className = 'h-full bg-red-500 rounded-full transition-all duration-500';
    }
    if (progressPercent) {
        progressPercent.textContent = 'Failed';
    }
    if (progressETA) {
        progressETA.textContent = '';
    }

    // Add retry button
    const processingContent = document.querySelector('#processingStatus > div');
    if (processingContent && !document.getElementById('retryButton')) {
        const retryButton = document.createElement('button');
        retryButton.id = 'retryButton';
        retryButton.textContent = 'Try Again';
        retryButton.className = 'mt-6 px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg shadow-lg transition-colors';
        retryButton.onclick = () => {
            document.getElementById('retryButton')?.remove();
            uploadForm.classList.remove('hidden');
            processingStatus.classList.add('hidden');
            uploadForm.reset();
            fileName.classList.add('hidden');
        };
        processingContent.appendChild(retryButton);
    }
}

// Update progress display
function updateProgress(phase, message, percent) {
    const progressPhase = document.getElementById('progressPhase');
    const progressMessage = document.getElementById('progressMessage');
    const progressBar = document.getElementById('progressBar');
    const progressPercent = document.getElementById('progressPercent');
    const progressETA = document.getElementById('progressETA');

    // Map phase to user-friendly text and percentage
    const phaseMap = {
        'initialization': { label: 'Initializing', percent: 5 },
        'phase-1': { label: 'Phase 1 of 5: Comprehension', percent: 20 },
        'phase-2': { label: 'Phase 2 of 5: Structure', percent: 40 },
        'phase-3': { label: 'Phase 3 of 5: Propositions', percent: 60 },
        'phase-4': { label: 'Phase 4 of 5: Analytics', percent: 75 },
        'phase-5': { label: 'Phase 5 of 5: Pedagogy', percent: 90 },
        'validation': { label: 'Finalizing', percent: 95 },
        'completed': { label: 'Complete!', percent: 100 },
        'error': { label: 'Error', percent: 0 }
    };

    const phaseInfo = phaseMap[phase] || { label: 'Processing', percent: percent || 0 };

    // Update text
    if (progressPhase) {
        progressPhase.textContent = phaseInfo.label;
    }
    if (progressMessage) {
        progressMessage.textContent = message;
    }

    // Update progress bar
    const targetPercent = percent !== undefined ? percent : phaseInfo.percent;
    if (progressBar) {
        progressBar.style.width = `${targetPercent}%`;
    }
    if (progressPercent) {
        progressPercent.textContent = `${Math.round(targetPercent)}%`;
    }

    // Update phase indicators
    for (let i = 1; i <= 5; i++) {
        const indicator = document.getElementById(`phase-${i}-indicator`);
        if (indicator) {
            if (phase === 'error') {
                // Error state - show red for all phases
                indicator.className = 'flex items-center gap-1 px-3 py-1 rounded-full text-xs bg-red-500 text-white';
            } else {
                const phaseNum = phase.match(/phase-(\d)/)?.[1];
                if (phaseNum && parseInt(phaseNum) === i) {
                    // Current phase
                    indicator.className = 'flex items-center gap-1 px-3 py-1 rounded-full text-xs bg-blue-600 text-white animate-pulse';
                } else if (phaseNum && parseInt(phaseNum) > i) {
                    // Completed phase
                    indicator.className = 'flex items-center gap-1 px-3 py-1 rounded-full text-xs bg-green-600 text-white';
                } else {
                    // Pending phase
                    indicator.className = 'flex items-center gap-1 px-3 py-1 rounded-full text-xs bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400';
                }
            }
        }
    }

    // Estimate time remaining
    if (progressETA && phase !== 'completed' && phase !== 'error') {
        const remainingPercent = 100 - targetPercent;
        const estimatedMinutes = Math.ceil((remainingPercent / 100) * 12); // Rough estimate
        progressETA.textContent = `~${estimatedMinutes} min remaining`;
    } else if (progressETA && phase === 'completed') {
        progressETA.textContent = 'Done!';
    }
}

// Show results
function showResults(data) {
    uploadSection.classList.add('hidden');
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
    renderTemporal(data);
    renderRawJson(data);
}

// Render functions
function renderOverview(data) {
    document.getElementById('chapterInfo').innerHTML = `
        <p><strong>Chapter ID:</strong> ${data.system_metadata?.chapter_id || 'N/A'}</p>
        <p><strong>Version:</strong> ${data.system_metadata?.version || 'N/A'}</p>
        <p><strong>Source:</strong> ${data.system_metadata?.source_text || 'N/A'}</p>
        <p><strong>Author:</strong> ${data.system_metadata?.author_or_editor || 'Unknown'}</p>
    `;

    document.getElementById('quickStats').innerHTML = `
        <p><strong>Learning Objectives:</strong> ${data.pedagogical_mapping?.learning_objectives?.length || 0}</p>
        <p><strong>Activities:</strong> ${data.pedagogical_mapping?.student_activities?.length || 0}</p>
        <p><strong>Propositions:</strong> ${data.propositional_extraction?.propositions?.length || 0}</p>
        <p><strong>Subject:</strong> ${data.analytical_metadata?.subject_domain || 'N/A'}</p>
    `;

    const concepts = data.comprehension_pass?.what || [];
    document.getElementById('keyConcepts').innerHTML = concepts.slice(0, 5).map(c => `
        <div class="mb-3 pb-3 border-b border-gray-200 dark:border-gray-600 last:border-0">
            <p class="font-semibold text-sm text-gray-900 dark:text-white">${c.concept_or_topic}</p>
            <p class="text-xs text-gray-600 dark:text-gray-400 mt-1">${c.definition_or_description || ''}</p>
        </div>
    `).join('') || '<p class="text-sm text-gray-500 dark:text-gray-400">No concepts found</p>';
}

function renderMetadata(data) {
    const meta = data.system_metadata || {};
    document.getElementById('metadataContent').innerHTML = `
        <p><strong>Chapter ID:</strong> ${meta.chapter_id || 'N/A'}</p>
        <p><strong>File Name:</strong> ${meta.file_name || 'N/A'}</p>
        <p><strong>Author/Editor:</strong> ${meta.author_or_editor || 'Unknown'}</p>
        <p><strong>Version:</strong> ${meta.version || 'N/A'}</p>
        <p><strong>Created:</strong> ${meta.created_at || 'N/A'}</p>
        <p><strong>Source:</strong> ${meta.source_text || 'N/A'}</p>
    `;
}

function renderComprehension(data) {
    const comp = data.comprehension_pass || {};

    // Who
    const who = comp.who || [];
    document.getElementById('comprehensionWho').innerHTML = who.map(item => `
        <div class="mb-3 p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
            <p class="font-semibold text-sm text-gray-900 dark:text-white">${item.entity}</p>
            ${item.role_or_function ? `<p class="text-xs text-gray-600 dark:text-gray-400 mt-1">Role: ${item.role_or_function}</p>` : ''}
            ${item.significance_in_chapter ? `<p class="text-xs text-gray-600 dark:text-gray-400 mt-1">Significance: ${item.significance_in_chapter}</p>` : ''}
        </div>
    `).join('') || '<p class="text-sm text-gray-500 dark:text-gray-400">No entities found</p>';

    // What
    const what = comp.what || [];
    document.getElementById('comprehensionWhat').innerHTML = what.map(item => `
        <div class="mb-3 p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
            <p class="font-semibold text-sm text-gray-900 dark:text-white">${item.concept_or_topic}</p>
            ${item.definition_or_description ? `<p class="text-xs text-gray-600 dark:text-gray-400 mt-1">${item.definition_or_description}</p>` : ''}
        </div>
    `).join('') || '<p class="text-sm text-gray-500 dark:text-gray-400">No concepts found</p>';

    // When/Why/How
    const when = comp.when || {};
    document.getElementById('comprehensionWhen').innerHTML = `
        <div class="space-y-2 text-sm">
            <p><strong>Historical Context:</strong> ${when.historical_or_cultural_context || 'N/A'}</p>
            <p><strong>Chronological Sequence:</strong> ${when.chronological_sequence_within_course || 'N/A'}</p>
        </div>
    `;

    const why = comp.why || {};
    document.getElementById('comprehensionWhy').innerHTML = `
        <div class="space-y-2 text-sm">
            <p><strong>Intellectual Value:</strong> ${why.intellectual_value || 'N/A'}</p>
            <p><strong>Knowledge Value:</strong> ${why.knowledge_based_value || 'N/A'}</p>
        </div>
    `;

    const how = comp.how || {};
    document.getElementById('comprehensionHow').innerHTML = `
        <div class="space-y-2 text-sm">
            <p><strong>Presentation Style:</strong> ${how.presentation_style || 'N/A'}</p>
            <p><strong>Rhetorical Approach:</strong> ${how.rhetorical_approach || 'N/A'}</p>
        </div>
    `;
}

function renderOutline(data) {
    const struct = data.structural_outline || {};
    const sections = struct.outline || [];

    document.getElementById('outlineContent').innerHTML = `
        <h4 class="text-lg font-semibold text-gray-900 mb-4">${struct.chapter_title || 'Chapter'}</h4>
        ${sections.map((s, i) => `
            <div class="mb-4 p-4 bg-gray-50 rounded-lg">
                <p class="font-semibold text-sm">${i+1}. ${s.section_title}</p>
                ${s.section_summary ? `<p class="text-xs text-gray-600 mt-2">${s.section_summary}</p>` : ''}
            </div>
        `).join('')}
    ` || '<p class="text-sm text-gray-500">No outline available</p>';
}

function renderPropositions(data) {
    const props = data.propositional_extraction?.propositions || [];

    document.getElementById('propositionsList').innerHTML = props.map((p, i) => `
        <div class="mb-4 p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
            <div class="flex items-center gap-2 mb-2">
                <span class="px-2 py-1 bg-blue-600 dark:bg-blue-500 text-white text-xs font-semibold rounded">#${i+1}</span>
                ${p.truth_type ? `<span class="text-xs text-gray-600 dark:text-gray-400">${p.truth_type}</span>` : ''}
            </div>
            <p class="text-sm font-medium text-gray-900 dark:text-white">${p.statement}</p>
            ${p.evidence_from_text ? `<p class="text-xs text-gray-600 dark:text-gray-400 mt-2">${p.evidence_from_text}</p>` : ''}
        </div>
    `).join('') || '<p class="text-sm text-gray-500 dark:text-gray-400">No propositions found</p>';
}

function renderAnalytics(data) {
    const meta = data.analytical_metadata || {};
    document.getElementById('analyticsContent').innerHTML = `
        <p><strong>Subject Domain:</strong> ${meta.subject_domain || 'N/A'}</p>
        <p><strong>Curriculum Unit:</strong> ${meta.curriculum_unit || 'N/A'}</p>
        <p><strong>Disciplinary Lens:</strong> ${meta.disciplinary_lens || 'N/A'}</p>
        <p><strong>Grade Level:</strong> ${meta.grade_level_or_audience || 'N/A'}</p>
    `;
}

function renderPedagogy(data) {
    const ped = data.pedagogical_mapping || {};

    document.getElementById('pedagogyObjectives').innerHTML = (ped.learning_objectives || []).map(obj => `
        <li class="text-sm text-gray-700 mb-2">${obj}</li>
    `).join('') ? `<ol class="list-decimal list-inside">${(ped.learning_objectives || []).map(obj => `<li class="text-sm text-gray-700 mb-2">${obj}</li>`).join('')}</ol>` : '<p class="text-sm text-gray-500">No objectives found</p>';

    document.getElementById('pedagogySummary').innerHTML = `<p class="text-sm text-gray-700">${ped.chapter_summary || 'No summary available'}</p>`;

    document.getElementById('pedagogyDiscussion').innerHTML = (ped.potential_discussion_questions || []).map(q => `
        <li class="text-sm text-gray-700 mb-2">${q}</li>
    `).join('') ? `<ol class="list-decimal list-inside">${(ped.potential_discussion_questions || []).map(q => `<li class="text-sm text-gray-700 mb-2">${q}</li>`).join('')}</ol>` : '<p class="text-sm text-gray-500">No questions found</p>';
}

function renderActivities(data) {
    const acts = data.pedagogical_mapping?.student_activities || [];
    document.getElementById('activitiesContent').innerHTML = acts.map(a => `
        <div class="mb-3 p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
            <span class="px-2 py-1 bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300 text-xs font-semibold rounded">${a.activity_type || 'Activity'}</span>
            <p class="text-sm text-gray-700 dark:text-gray-300 mt-2">${a.description || ''}</p>
        </div>
    `).join('') || '<p class="text-sm text-gray-500 dark:text-gray-400">No activities found</p>';
}

function renderQuestions(data) {
    const qs = data.pedagogical_mapping?.assessment_questions || [];
    document.getElementById('questionsContent').innerHTML = qs.map(q => `
        <div class="mb-3 p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
            <span class="px-2 py-1 bg-green-100 dark:bg-green-900 text-green-700 dark:text-green-300 text-xs font-semibold rounded">${q.question_type || 'Question'}</span>
            <p class="text-sm text-gray-700 dark:text-gray-300 mt-2"><strong>Q:</strong> ${q.question || ''}</p>
        </div>
    `).join('') || '<p class="text-sm text-gray-500 dark:text-gray-400">No questions found</p>';
}

function renderTemporal(data) {
    const temp = data.pedagogical_mapping?.temporal_analysis || {};
    document.getElementById('temporalContent').innerHTML = `
        <p class="text-lg font-semibold text-blue-600 dark:text-blue-400">${temp.temporal_range || 'N/A'}</p>
        <p class="text-sm text-gray-600 dark:text-gray-400 mt-2">Content spans from ${temp.temporal_range || 'unknown period'}</p>
    `;
}

function renderRawJson(data) {
    document.getElementById('rawJson').textContent = JSON.stringify(data, null, 2);
}

// Tab switching
document.querySelectorAll('.tab').forEach(tab => {
    tab.addEventListener('click', () => {
        const target = tab.dataset.tab;

        // Update tabs
        document.querySelectorAll('.tab').forEach(t => {
            t.classList.remove('bg-gradient-to-r', 'from-blue-600', 'to-purple-600', 'dark:from-blue-500', 'dark:to-purple-500', 'text-white', 'shadow-lg');
            t.classList.add('text-gray-600', 'dark:text-gray-400');
        });
        tab.classList.add('bg-gradient-to-r', 'from-blue-600', 'to-purple-600', 'dark:from-blue-500', 'dark:to-purple-500', 'text-white', 'shadow-lg');
        tab.classList.remove('text-gray-600', 'dark:text-gray-400');

        // Update panels
        document.querySelectorAll('.tab-panel').forEach(p => p.classList.add('hidden'));
        document.getElementById(target).classList.remove('hidden');
    });
});

// Copy JSON
if (copyJsonBtn) {
    copyJsonBtn.addEventListener('click', () => {
        const text = document.getElementById('rawJson').textContent;
        navigator.clipboard.writeText(text).then(() => {
            const original = copyJsonBtn.textContent;
            copyJsonBtn.textContent = 'Copied!';
            setTimeout(() => copyJsonBtn.textContent = original, 2000);
        });
    });
}

// New analysis buttons
[newAnalysisBtn, homeBtn].forEach(btn => {
    if (btn) {
        btn.addEventListener('click', () => {
            resultsSection.classList.add('hidden');
            uploadSection.classList.remove('hidden');
            uploadForm.classList.remove('hidden');
            processingStatus.classList.add('hidden');
            uploadForm.reset();
            fileName.classList.add('hidden');
        });
    }
});

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadExistingChapters();
});
