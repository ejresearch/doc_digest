// State
let currentResults = null;
let logViewerOpen = false;
let logEntries = [];

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

// Welcome Modal handling
function showWelcomeModal() {
    const modal = document.getElementById('welcomeModal');
    if (modal) {
        modal.classList.remove('hidden');
    }
}

function hideWelcomeModal() {
    const modal = document.getElementById('welcomeModal');
    const dontShowAgain = document.getElementById('dontShowAgain');

    if (modal) {
        modal.classList.add('hidden');
    }

    if (dontShowAgain && dontShowAgain.checked) {
        localStorage.setItem('graffModalSeen', 'true');
    }
}

// Show modal on first visit
document.addEventListener('DOMContentLoaded', () => {
    const hasSeenModal = localStorage.getItem('graffModalSeen');
    if (!hasSeenModal) {
        setTimeout(showWelcomeModal, 500);
    }

    // Modal close handlers
    const closeModal = document.getElementById('closeModal');
    const getStartedBtn = document.getElementById('getStartedBtn');
    const welcomeModal = document.getElementById('welcomeModal');

    if (closeModal) {
        closeModal.addEventListener('click', hideWelcomeModal);
    }

    if (getStartedBtn) {
        getStartedBtn.addEventListener('click', hideWelcomeModal);
    }

    // Close on background click
    if (welcomeModal) {
        welcomeModal.addEventListener('click', (e) => {
            if (e.target === welcomeModal) {
                hideWelcomeModal();
            }
        });
    }

    // Sample Data toggle
    const toggleSampleData = document.getElementById('toggleSampleData');
    const sampleDataContent = document.getElementById('sampleDataContent');
    const sampleChevron = document.getElementById('sampleChevron');

    if (toggleSampleData && sampleDataContent) {
        toggleSampleData.addEventListener('click', () => {
            const isHidden = sampleDataContent.classList.contains('hidden');
            if (isHidden) {
                sampleDataContent.classList.remove('hidden');
                sampleChevron.classList.add('rotate-90');
            } else {
                sampleDataContent.classList.add('hidden');
                sampleChevron.classList.remove('rotate-90');
            }
        });
    }
});

// Real-time Log Viewer Functions
function toggleLogViewer() {
    logViewerOpen = !logViewerOpen;
    const logViewer = document.getElementById('logViewer');
    const logChevron = document.getElementById('logChevron');

    if (logViewerOpen) {
        logViewer.classList.remove('hidden');
        logChevron.classList.add('rotate-180');
    } else {
        logViewer.classList.add('hidden');
        logChevron.classList.remove('rotate-180');
    }
}

function addLogEntry(message, phase) {
    const logContent = document.getElementById('logContent');
    const logCount = document.getElementById('logCount');

    if (!logContent) return;

    // Determine log color based on content
    let color = 'text-gray-300';
    if (message.includes('✅') || message.includes('✓')) {
        color = 'text-green-400';
    } else if (message.includes('📖')) {
        color = 'text-blue-400';
    } else if (message.includes('⚙️')) {
        color = 'text-yellow-400';
    } else if (message.includes('🔗') || message.includes('✨')) {
        color = 'text-purple-400';
    } else if (message.includes('🎯')) {
        color = 'text-cyan-400';
    }

    // Add timestamp
    const timestamp = new Date().toLocaleTimeString();

    // Create log entry
    const entry = document.createElement('div');
    entry.className = `${color} leading-relaxed`;
    entry.innerHTML = `<span class="text-gray-500">[${timestamp}]</span> ${escapeHtml(message)}`;

    logContent.appendChild(entry);
    logEntries.push(message);

    // Update count
    if (logCount) {
        logCount.textContent = logEntries.length;
    }

    // Auto-scroll to bottom
    logContent.scrollTop = logContent.scrollHeight;

    // Auto-open on first log entry
    if (logEntries.length === 1 && !logViewerOpen) {
        toggleLogViewer();
    }
}

function clearLogs() {
    const logContent = document.getElementById('logContent');
    const logCount = document.getElementById('logCount');

    if (logContent) logContent.innerHTML = '';
    if (logCount) logCount.textContent = '0';
    logEntries = [];
    logViewerOpen = false;

    const logViewer = document.getElementById('logViewer');
    const logChevron = document.getElementById('logChevron');
    if (logViewer) logViewer.classList.add('hidden');
    if (logChevron) logChevron.classList.remove('rotate-180');
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
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
                    <button onclick="loadChapter('${chapter.chapter_id}')" class="w-full text-left px-4 py-3 bg-gray-50 dark:bg-gray-700 hover:bg-gray-100 dark:hover:bg-gray-600 rounded-lg border border-gray-200 dark:border-gray-600 transition-colors">
                        <div class="font-semibold text-sm text-gray-900 dark:text-white">${chapter.chapter_title || chapter.chapter_id || 'Unknown'}</div>
                        <div class="text-xs text-gray-500 dark:text-gray-400 mt-1">
                            <span class="inline-block mr-2">📝 ${chapter.proposition_count || 0} propositions</span>
                            <span class="inline-block mr-2">💡 ${chapter.takeaway_count || 0} takeaways</span>
                        </div>
                        <div class="text-xs text-gray-400 dark:text-gray-500 mt-1">ID: ${chapter.chapter_id} • ${chapter.book_id || 'Unknown book'}</div>
                    </button>
                    <button onclick="event.stopPropagation(); deleteChapter('${chapter.chapter_id}')" class="absolute top-1/2 -translate-y-1/2 right-2 opacity-0 group-hover:opacity-100 p-2 text-gray-400 hover:text-red-500 dark:text-gray-500 dark:hover:text-red-400 rounded-lg transition-all hover:bg-gray-200 dark:hover:bg-gray-600" title="Delete this analysis">
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
window.deleteChapter = async function(chapter_id) {
    if (!confirm('Are you sure you want to delete this analysis? This action cannot be undone.')) {
        return;
    }

    try {
        const response = await fetch(`/chapters/${chapter_id}`, {
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
window.loadChapter = async function(chapter_id) {
    try {
        const response = await fetch(`/chapters/${chapter_id}`);
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

    // Clear previous logs
    clearLogs();

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
                    updateProgress('validation', 'Checking if analysis completed...', 95);

                    // Poll for completion since the stream timed out but analysis might still be running
                    let pollAttempts = 0;

                    const pollForCompletion = async () => {
                        try {
                            const listResponse = await fetch('/chapters/list');
                            const listData = await listResponse.json();

                            if (listData.chapters && listData.chapters.length > 0) {
                                const latestChapter = listData.chapters[listData.chapters.length - 1];
                                const createdTime = new Date(latestChapter.created_at);
                                const now = new Date();
                                const diffMinutes = (now - createdTime) / 1000 / 60;

                                if (diffMinutes < 60) { // Consider chapters from last hour as potentially ours
                                    console.log('Analysis completed! Loading results...');
                                    updateProgress('completed', 'Analysis complete!', 100);
                                    await loadChapter(latestChapter.chapter_id);
                                    return;
                                }
                            }

                            // Continue polling indefinitely
                            pollAttempts++;
                            const elapsedMinutes = Math.floor(pollAttempts * 10 / 60);
                            console.log(`Polling attempt ${pollAttempts} (${elapsedMinutes} min elapsed)...`);
                            updateProgress('validation', `Still processing... (${elapsedMinutes} minutes elapsed)`, 95);
                            setTimeout(pollForCompletion, 10000); // Poll every 10 seconds
                        } catch (checkError) {
                            console.error('Error checking for completion:', checkError);
                            pollAttempts++;
                            // Continue polling even on errors - they might be temporary network issues
                            setTimeout(pollForCompletion, 10000);
                        }
                    };

                    // Start polling after 2 seconds
                    setTimeout(pollForCompletion, 2000);
                    return;
                }

                // Update UI with real progress
                updateProgress(update.phase, update.message);

                // Add to log viewer
                addLogEntry(update.message, update.phase);

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
                                await loadChapter(latestChapter.chapter_id);
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
            updateProgress('validation', 'Connection lost, checking for results...', 95);

            // Poll for completion since the connection was lost but analysis might still be running
            let pollAttempts = 0;

            const pollForCompletion = async () => {
                try {
                    const listResponse = await fetch('/chapters/list');
                    const listData = await listResponse.json();

                    if (listData.chapters && listData.chapters.length > 0) {
                        const latestChapter = listData.chapters[listData.chapters.length - 1];
                        const createdTime = new Date(latestChapter.created_at);
                        const now = new Date();
                        const diffMinutes = (now - createdTime) / 1000 / 60;

                        if (diffMinutes < 60) { // Consider chapters from last hour as potentially ours
                            // Analysis completed! Load the results
                            console.log('Analysis completed! Loading results...');
                            updateProgress('completed', 'Analysis complete!', 100);
                            await loadChapter(latestChapter.chapter_id);
                            return;
                        }
                    }

                    // Continue polling indefinitely
                    pollAttempts++;
                    const elapsedMinutes = Math.floor(pollAttempts * 10 / 60);
                    console.log(`Polling attempt ${pollAttempts} (${elapsedMinutes} min elapsed)...`);
                    updateProgress('validation', `Checking for results... (${elapsedMinutes} minutes elapsed)`, 95);
                    setTimeout(pollForCompletion, 10000); // Poll every 10 seconds
                } catch (checkError) {
                    console.error('Error checking for completion:', checkError);
                    pollAttempts++;
                    // Continue polling even on errors - they might be temporary network issues
                    setTimeout(pollForCompletion, 10000);
                }
            };

            // Start polling after 1 second
            setTimeout(pollForCompletion, 1000);
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

    // Map phase to user-friendly text and base percentage
    const phaseMap = {
        'initialization': { label: 'Initializing', percent: 5 },
        'phase-1': { label: 'Phase 1 of 2: Structure Analysis', percent: 30 },
        'phase-2': { label: 'Phase 2 of 2: Content Extraction', percent: 70 },  // fallback
        'validation': { label: 'Validating', percent: 90 },
        'storage': { label: 'Saving', percent: 95 },
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

    // Calculate actual progress percentage
    let targetPercent = percent !== undefined ? percent : phaseInfo.percent;

    // For phase-2, parse actual progress from message (e.g., "6% done", "13% done")
    if (phase === 'phase-2' && message) {
        const progressMatch = message.match(/(\d+)% done/);
        if (progressMatch) {
            const phase2Progress = parseInt(progressMatch[1]);
            // Map phase-2 progress (0-100%) to overall progress (30-90%)
            targetPercent = 30 + (phase2Progress * 0.6);
        }
    }

    // Update progress bar
    if (progressBar) {
        progressBar.style.width = `${targetPercent}%`;
    }
    if (progressPercent) {
        progressPercent.textContent = `${Math.round(targetPercent)}%`;
    }

    // Update phase indicators (GRAFF has 2 phases)
    for (let i = 1; i <= 2; i++) {
        const indicator = document.getElementById(`phase-${i}-indicator`);
        if (indicator) {
            if (phase === 'error') {
                // Error state - show red for all phases
                indicator.className = 'flex items-center gap-2 px-4 py-2 rounded-full text-sm bg-red-500 text-white font-medium';
            } else {
                const phaseNum = phase.match(/phase-(\d)/)?.[1];
                if (phaseNum && parseInt(phaseNum) === i) {
                    // Current phase - blue with pulse animation
                    indicator.className = 'flex items-center gap-2 px-4 py-2 rounded-full text-sm bg-blue-600 text-white animate-pulse font-medium';
                } else if (phaseNum && parseInt(phaseNum) > i) {
                    // Completed phase - green checkmark
                    indicator.className = 'flex items-center gap-2 px-4 py-2 rounded-full text-sm bg-green-600 text-white font-medium';
                } else if (phase === 'completed' || phase === 'validation' || phase === 'storage') {
                    // All phases complete - green
                    indicator.className = 'flex items-center gap-2 px-4 py-2 rounded-full text-sm bg-green-600 text-white font-medium';
                } else {
                    // Pending phase - gray
                    indicator.className = 'flex items-center gap-2 px-4 py-2 rounded-full text-sm bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400 font-medium';
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

// Global state for Bloom filtering
let currentBloomFilter = 'all';

// Show results - GRAFF 2-phase structure
function showResults(data) {
    uploadSection.classList.add('hidden');
    resultsSection.classList.remove('hidden');

    // GRAFF render functions
    renderGraffOverview(data);
    renderPhase1Summary(data);
    renderPhase1Sections(data);
    renderPhase1Entities(data);
    renderPhase1Keywords(data);
    renderPhase2Propositions(data);
    renderPhase2Takeaways(data);
    renderBloomDistribution(data);
    renderRawJson(data);
}

// ============================================================================
// GRAFF Render Functions
// ============================================================================

// Helper: Calculate Bloom distribution
function calculateBloomDistribution(propositions) {
    const dist = {remember: 0, understand: 0, apply: 0, analyze: 0};
    propositions.forEach(p => {
        if (dist.hasOwnProperty(p.bloom_level)) {
            dist[p.bloom_level]++;
        }
    });
    return dist;
}

// Helper: Get Bloom color class
function getBloomColorClass(level) {
    const colors = {
        remember: 'bg-blue-500',
        understand: 'bg-green-500',
        apply: 'bg-yellow-500',
        analyze: 'bg-purple-500',
        evaluate: 'bg-red-500'
    };
    return colors[level] || 'bg-gray-500';
}

// Render GRAFF Overview
function renderGraffOverview(data) {
    const overviewEl = document.getElementById('graffOverview');
    if (!overviewEl) return;

    const propositions = data.phase2?.propositions || [];
    const takeaways = data.phase2?.key_takeaways || [];
    const sections = data.phase1?.sections || [];
    const entities = data.phase1?.key_entities || [];
    const keywords = data.phase1?.keywords || [];
    const summary = data.phase1?.summary || '';

    const bloomDist = calculateBloomDistribution(propositions);
    const totalProps = propositions.length;

    overviewEl.innerHTML = `
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <!-- Chapter Info -->
            <div class="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
                <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Chapter Information</h3>
                <div class="space-y-2 text-sm">
                    <p><strong>Title:</strong> <span class="text-gray-700 dark:text-gray-300">${data.chapter_title || 'N/A'}</span></p>
                    <p><strong>Book ID:</strong> <span class="text-gray-700 dark:text-gray-300">${data.book_id || 'N/A'}</span></p>
                    <p><strong>Chapter ID:</strong> <span class="text-gray-700 dark:text-gray-300">${data.chapter_id || 'N/A'}</span></p>
                    <p><strong>Schema:</strong> <span class="text-gray-700 dark:text-gray-300">GRAFF v${data.schema_version || '1.0'}</span></p>
                </div>
            </div>

            <!-- Quick Stats -->
            <div class="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
                <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Quick Stats</h3>
                <div class="space-y-2 text-sm">
                    <p><strong>Summary:</strong> <span class="text-gray-700 dark:text-gray-300">${summary.length} characters</span></p>
                    <p><strong>Sections:</strong> <span class="text-gray-700 dark:text-gray-300">${sections.length}</span></p>
                    <p><strong>Entities:</strong> <span class="text-gray-700 dark:text-gray-300">${entities.length}</span></p>
                    <p><strong>Keywords:</strong> <span class="text-gray-700 dark:text-gray-300">${keywords.length}</span></p>
                    <p><strong>📝 Propositions:</strong> <span class="text-blue-600 dark:text-blue-400 font-semibold">${totalProps}</span></p>
                    <p><strong>💡 Key Takeaways:</strong> <span class="text-purple-600 dark:text-purple-400 font-semibold">${takeaways.length}</span></p>
                </div>
            </div>

            <!-- Bloom Distribution Preview -->
            <div class="bg-white dark:bg-gray-800 p-6 rounded-lg shadow md:col-span-2">
                <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Bloom Distribution Preview</h3>
                <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                    ${Object.entries(bloomDist).map(([level, count]) => {
                        const percentage = totalProps > 0 ? ((count / totalProps) * 100).toFixed(1) : '0.0';
                        return `
                            <div class="text-center p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                                <div class="text-xs uppercase font-semibold text-gray-600 dark:text-gray-400 mb-1">${level}</div>
                                <div class="text-2xl font-bold text-gray-900 dark:text-white">${count}</div>
                                <div class="text-xs text-gray-500 dark:text-gray-400">${percentage}%</div>
                            </div>
                        `;
                    }).join('')}
                </div>
            </div>
        </div>
    `;
}

// Render Phase 1: Summary
function renderPhase1Summary(data) {
    const el = document.getElementById('summaryContent');
    if (!el) return;

    const summary = data.phase1?.summary || 'No summary available';
    el.innerHTML = `
        <p class="text-gray-700 dark:text-gray-300 leading-relaxed">${summary}</p>
    `;
}

// Render Phase 1: Sections
function renderPhase1Sections(data) {
    const el = document.getElementById('sectionsTree');
    if (!el) return;

    const sections = data.phase1?.sections || [];
    if (sections.length === 0) {
        el.innerHTML = '<p class="text-sm text-gray-500 dark:text-gray-400">No sections found</p>';
        return;
    }

    el.innerHTML = sections.map(s => {
        const indent = (s.level - 1) * 24;
        return `
            <div class="mb-3 p-4 bg-gray-50 dark:bg-gray-700 rounded-lg" style="margin-left: ${indent}px;">
                <div class="flex items-center gap-2 mb-1">
                    <span class="px-2 py-1 bg-gray-200 dark:bg-gray-600 text-gray-700 dark:text-gray-300 text-xs font-mono rounded">${s.unit_id}</span>
                    <span class="text-xs text-gray-500 dark:text-gray-400">Level ${s.level}</span>
                </div>
                <p class="font-semibold text-sm text-gray-900 dark:text-white">${s.title}</p>
                ${s.start_location ? `<p class="text-xs text-gray-500 dark:text-gray-400 mt-1">📍 ${s.start_location}</p>` : ''}
            </div>
        `;
    }).join('');
}

// Render Phase 1: Entities
function renderPhase1Entities(data) {
    const el = document.getElementById('entitiesContent');
    if (!el) return;

    const entities = data.phase1?.key_entities || [];
    if (entities.length === 0) {
        el.innerHTML = '<p class="text-sm text-gray-500 dark:text-gray-400">No entities found</p>';
        return;
    }

    // Group by type
    const grouped = {};
    entities.forEach(e => {
        if (!grouped[e.type]) grouped[e.type] = [];
        grouped[e.type].push(e.name);
    });

    const typeIcons = {
        person: '👤',
        organization: '🏢',
        concept: '💡',
        event: '📅',
        place: '📍',
        technology: '🔧'
    };

    el.innerHTML = Object.entries(grouped).map(([type, names]) => `
        <div class="mb-4">
            <h4 class="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                ${typeIcons[type] || '•'} ${type.charAt(0).toUpperCase() + type.slice(1)} (${names.length})
            </h4>
            <div class="flex flex-wrap gap-2">
                ${names.map(name => `
                    <span class="px-3 py-1 bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300 text-xs rounded-full">${name}</span>
                `).join('')}
            </div>
        </div>
    `).join('');
}

// Render Phase 1: Keywords
function renderPhase1Keywords(data) {
    const el = document.getElementById('keywordsContent');
    if (!el) return;

    const keywords = data.phase1?.keywords || [];
    if (keywords.length === 0) {
        el.innerHTML = '<p class="text-sm text-gray-500 dark:text-gray-400">No keywords found</p>';
        return;
    }

    el.innerHTML = `
        <div class="flex flex-wrap gap-2">
            ${keywords.map(kw => `
                <span class="px-3 py-1 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 text-sm rounded-full border border-gray-300 dark:border-gray-600">${kw}</span>
            `).join('')}
        </div>
        <p class="text-xs text-gray-500 dark:text-gray-400 mt-4">${keywords.length} keywords total</p>
    `;
}

// Render Phase 2: Propositions (with Bloom filter)
function renderPhase2Propositions(data) {
    const propositions = data.phase2?.propositions || [];

    // Render filter buttons
    renderBloomFilter(propositions);

    // Render propositions list
    renderPropositionsList(propositions);
}

function renderBloomFilter(propositions) {
    const el = document.getElementById('bloomFilter');
    if (!el) return;

    const bloomDist = calculateBloomDistribution(propositions);
    const total = propositions.length;

    const bloomLevels = [
        {key: 'all', label: 'All', count: total},
        {key: 'remember', label: 'Remember', count: bloomDist.remember},
        {key: 'understand', label: 'Understand', count: bloomDist.understand},
        {key: 'apply', label: 'Apply', count: bloomDist.apply},
        {key: 'analyze', label: 'Analyze', count: bloomDist.analyze}
    ];

    el.innerHTML = `
        <div class="mb-6 p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
            <p class="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">Filter by Bloom Level:</p>
            <div class="flex flex-wrap gap-2">
                ${bloomLevels.map(level => `
                    <button
                        onclick="filterPropositions('${level.key}')"
                        class="bloom-filter-btn px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                            currentBloomFilter === level.key
                                ? 'bg-blue-600 text-white shadow-md'
                                : 'bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-300 border border-gray-300 dark:border-gray-600 hover:bg-gray-100 dark:hover:bg-gray-600'
                        }">
                        ${level.label} (${level.count})
                    </button>
                `).join('')}
            </div>
        </div>
    `;
}

function renderPropositionsList(propositions) {
    const el = document.getElementById('propositionsList');
    if (!el) return;

    // Filter propositions
    const filtered = currentBloomFilter === 'all'
        ? propositions
        : propositions.filter(p => p.bloom_level === currentBloomFilter);

    if (filtered.length === 0) {
        el.innerHTML = '<p class="text-sm text-gray-500 dark:text-gray-400">No propositions found for this filter</p>';
        return;
    }

    el.innerHTML = filtered.map((p, i) => {
        const bloomColor = getBloomColorClass(p.bloom_level);
        return `
            <div class="mb-4 p-4 bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700">
                <div class="flex items-center gap-2 mb-3">
                    <span class="px-2 py-1 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 text-xs font-semibold rounded">#${i+1}</span>
                    <span class="px-3 py-1 ${bloomColor} text-white text-xs font-semibold uppercase rounded-full">${p.bloom_level}</span>
                    <span class="px-2 py-1 bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400 text-xs rounded">${p.bloom_verb}</span>
                </div>
                <p class="text-sm font-medium text-gray-900 dark:text-white mb-3">${p.proposition_text}</p>
                <div class="space-y-2 text-xs text-gray-600 dark:text-gray-400">
                    <p><strong>📍 Evidence:</strong> ${p.evidence_location}</p>
                    <p><strong>📂 Unit:</strong> ${p.unit_id}</p>
                    <p><strong>📝 Source:</strong> ${p.source_type}</p>
                    ${p.tags && p.tags.length > 0 ? `
                        <div class="flex items-center gap-2 flex-wrap mt-2">
                            <strong>🏷️ Tags:</strong>
                            ${p.tags.map(tag => `<span class="px-2 py-1 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded">${tag}</span>`).join('')}
                        </div>
                    ` : ''}
                </div>
            </div>
        `;
    }).join('');

    // Update count
    const countEl = document.getElementById('propositionsCount');
    if (countEl) {
        countEl.textContent = `Showing ${filtered.length} of ${propositions.length} propositions`;
    }
}

// Global function for filter buttons
window.filterPropositions = function(bloomLevel) {
    currentBloomFilter = bloomLevel;
    renderPhase2Propositions(currentResults);
};

// Render Phase 2: Key Takeaways
function renderPhase2Takeaways(data) {
    const el = document.getElementById('takeawaysList');
    if (!el) return;

    const takeaways = data.phase2?.key_takeaways || [];
    if (takeaways.length === 0) {
        el.innerHTML = '<p class="text-sm text-gray-500 dark:text-gray-400">No key takeaways found</p>';
        return;
    }

    el.innerHTML = takeaways.map((t, i) => {
        const bloomColor = t.dominant_bloom_level ? getBloomColorClass(t.dominant_bloom_level) : 'bg-gray-500';
        return `
            <div class="mb-4 p-5 bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700">
                <div class="flex items-center gap-2 mb-3">
                    <span class="px-2 py-1 bg-purple-100 dark:bg-purple-900 text-purple-700 dark:text-purple-300 text-xs font-semibold rounded">#${i+1}</span>
                    ${t.dominant_bloom_level ? `<span class="px-3 py-1 ${bloomColor} text-white text-xs font-semibold uppercase rounded-full">${t.dominant_bloom_level}</span>` : ''}
                </div>
                <p class="text-base font-medium text-gray-900 dark:text-white mb-4 leading-relaxed">${t.text}</p>
                <div class="space-y-2 text-xs text-gray-600 dark:text-gray-400">
                    ${t.unit_id ? `<p><strong>📂 Unit:</strong> ${t.unit_id}</p>` : ''}
                    <p><strong>🔗 Based on ${t.proposition_ids.length} proposition(s):</strong></p>
                    <div class="flex flex-wrap gap-1 ml-4">
                        ${t.proposition_ids.map(pid => `
                            <span class="px-2 py-1 bg-blue-50 dark:bg-blue-900 text-blue-700 dark:text-blue-300 rounded text-xs font-mono">${pid}</span>
                        `).join('')}
                    </div>
                    ${t.tags && t.tags.length > 0 ? `
                        <div class="flex items-center gap-2 flex-wrap mt-2">
                            <strong>🏷️ Tags:</strong>
                            ${t.tags.map(tag => `<span class="px-2 py-1 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded">${tag}</span>`).join('')}
                        </div>
                    ` : ''}
                </div>
            </div>
        `;
    }).join('');
}

// Render Bloom Distribution Charts
function renderBloomDistribution(data) {
    const el = document.getElementById('bloomCharts');
    if (!el) return;

    const propositions = data.phase2?.propositions || [];
    const takeaways = data.phase2?.key_takeaways || [];

    const propDist = calculateBloomDistribution(propositions);
    const totalProps = propositions.length;

    // Calculate takeaway distribution
    const takeawayDist = {analyze: 0, evaluate: 0};
    takeaways.forEach(t => {
        if (t.dominant_bloom_level && takeawayDist.hasOwnProperty(t.dominant_bloom_level)) {
            takeawayDist[t.dominant_bloom_level]++;
        }
    });
    const totalTakeaways = takeaways.length;

    // Target ranges for validation
    const targets = {
        remember: {min: 20, max: 30},
        understand: {min: 30, max: 40},
        apply: {min: 10, max: 15},
        analyze: {min: 20, max: 25}
    };

    el.innerHTML = `
        <div class="space-y-8">
            <!-- Propositions Distribution -->
            <div class="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
                <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Proposition Distribution by Bloom Level</h3>
                <p class="text-sm text-gray-600 dark:text-gray-400 mb-4">Total: ${totalProps} propositions</p>
                <div class="space-y-3">
                    ${Object.entries(propDist).map(([level, count]) => {
                        const percentage = totalProps > 0 ? ((count / totalProps) * 100).toFixed(1) : '0.0';
                        const target = targets[level];
                        const inRange = totalProps > 0 && parseFloat(percentage) >= target.min && parseFloat(percentage) <= target.max;
                        const bloomColor = getBloomColorClass(level);
                        return `
                            <div>
                                <div class="flex justify-between items-center mb-1">
                                    <span class="text-sm font-medium text-gray-700 dark:text-gray-300 capitalize">${level}</span>
                                    <span class="text-sm text-gray-600 dark:text-gray-400">
                                        ${count} (${percentage}%)
                                        ${inRange ? '✓' : ''}
                                        <span class="text-xs text-gray-500">Target: ${target.min}-${target.max}%</span>
                                    </span>
                                </div>
                                <div class="h-6 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                                    <div class="${bloomColor} h-full transition-all duration-500" style="width: ${percentage}%"></div>
                                </div>
                            </div>
                        `;
                    }).join('')}
                </div>
            </div>

            <!-- Takeaways Distribution -->
            <div class="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
                <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Key Takeaway Distribution by Bloom Level</h3>
                <p class="text-sm text-gray-600 dark:text-gray-400 mb-4">Total: ${totalTakeaways} takeaways</p>
                <div class="space-y-3">
                    ${Object.entries(takeawayDist).map(([level, count]) => {
                        const percentage = totalTakeaways > 0 ? ((count / totalTakeaways) * 100).toFixed(1) : '0.0';
                        const bloomColor = getBloomColorClass(level);
                        return `
                            <div>
                                <div class="flex justify-between items-center mb-1">
                                    <span class="text-sm font-medium text-gray-700 dark:text-gray-300 capitalize">${level}</span>
                                    <span class="text-sm text-gray-600 dark:text-gray-400">${count} (${percentage}%)</span>
                                </div>
                                <div class="h-6 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                                    <div class="${bloomColor} h-full transition-all duration-500" style="width: ${percentage}%"></div>
                                </div>
                            </div>
                        `;
                    }).join('')}
                </div>
            </div>
        </div>
    `;
}

function renderRawJson(data) {
    const el = document.getElementById('rawJson');
    if (el) {
        el.textContent = JSON.stringify(data, null, 2);
    }
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

// Reset processing status to initial state
function resetProcessingStatus() {
    // Hide processing status
    processingStatus.classList.add('hidden');

    // Clear logs
    clearLogs();

    // Reset progress elements
    const progressPhase = document.getElementById('progressPhase');
    const progressMessage = document.getElementById('progressMessage');
    const progressBar = document.getElementById('progressBar');
    const progressPercent = document.getElementById('progressPercent');
    const progressETA = document.getElementById('progressETA');

    if (progressPhase) {
        progressPhase.textContent = 'Processing chapter...';
        progressPhase.className = 'text-sm font-semibold text-gray-700 dark:text-gray-300';
    }
    if (progressMessage) {
        progressMessage.textContent = 'Starting analysis...';
        progressMessage.className = 'text-xs text-gray-500 dark:text-gray-400 mt-1';
    }
    if (progressBar) {
        progressBar.style.width = '0%';
        progressBar.className = 'bg-gradient-to-r from-blue-600 to-purple-600 h-2 rounded-full transition-all duration-500 ease-out';
    }
    if (progressPercent) {
        progressPercent.textContent = '0%';
    }
    if (progressETA) {
        progressETA.textContent = 'Estimating time...';
    }

    // Remove retry button if it exists
    const retryButton = document.getElementById('retryButton');
    if (retryButton) {
        retryButton.remove();
    }

    // Reset phase indicators
    ['phase-1-indicator', 'phase-2-indicator'].forEach(id => {
        const indicator = document.getElementById(id);
        if (indicator) {
            indicator.className = 'flex items-center gap-2 px-4 py-2 rounded-full text-sm bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400 font-medium';
        }
    });
}

// New analysis buttons
[newAnalysisBtn, homeBtn].forEach(btn => {
    if (btn) {
        btn.addEventListener('click', () => {
            resultsSection.classList.add('hidden');
            uploadSection.classList.remove('hidden');
            uploadForm.classList.remove('hidden');
            resetProcessingStatus();
            uploadForm.reset();
            fileName.classList.add('hidden');

            // Refresh the chapter list to show any new chapters
            loadExistingChapters();
        });
    }
});

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadExistingChapters();
});
