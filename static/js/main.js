/**
 * ResumeFit - ATS Resume Analyzer Client Controller
 */

document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements - Inputs & Dropzone
    const form = document.getElementById('analyzer-form');
    const fileInput = document.getElementById('resume-file-input');
    const dropzone = document.getElementById('pdf-dropzone');
    const dropzoneDefault = document.getElementById('dropzone-default');
    const dropzoneFileInfo = document.getElementById('dropzone-file-info');
    const selectedFileName = document.getElementById('selected-file-name');
    const selectedFileSize = document.getElementById('selected-file-size');
    const removeFileBtn = document.getElementById('remove-file-btn');
    const browseBtn = document.getElementById('browse-btn');
    
    // Sample Helpers
    const useSampleResumeBtn = document.getElementById('use-sample-resume-btn');
    const sampleResumeTextInput = document.getElementById('sample-resume-text');
    const loadSampleJdBtn = document.getElementById('load-sample-jd-btn');
    const jdInput = document.getElementById('job-description-input');
    const jdWordCount = document.getElementById('jd-word-count');
    const clearJdBtn = document.getElementById('clear-jd-btn');

    // Action & Status
    const analyzeBtn = document.getElementById('analyze-btn');
    const analyzeSpinner = document.getElementById('analyze-spinner');
    const errorBanner = document.getElementById('error-banner');
    const errorMessage = document.getElementById('error-message');
    const closeErrorBtn = document.getElementById('close-error-btn');

    // Results Elements
    const resultsSection = document.getElementById('results-section');
    const reanalyzeBtn = document.getElementById('reanalyze-btn');
    const atsScoreDisplay = document.getElementById('ats-score-display');
    const gaugeProgressCircle = document.getElementById('gauge-progress-circle');
    const matchLevelBadge = document.getElementById('match-level-badge');
    const scoreVerdictTitle = document.getElementById('score-verdict-title');
    const scoreVerdictDesc = document.getElementById('score-verdict-desc');

    // Stat elements
    const statMatchedKeywords = document.getElementById('stat-matched-keywords');
    const statMissingKeywords = document.getElementById('stat-missing-keywords');
    const statWordCount = document.getElementById('stat-word-count');
    const statWordStatus = document.getElementById('stat-word-status');
    const statActionVerbs = document.getElementById('stat-action-verbs');

    // Subscores progress bars
    const barValKeywords = document.getElementById('bar-val-keywords');
    const barFillKeywords = document.getElementById('bar-fill-keywords');
    const barValTech = document.getElementById('bar-val-tech');
    const barFillTech = document.getElementById('bar-fill-tech');
    const barValStructure = document.getElementById('bar-val-structure');
    const barFillStructure = document.getElementById('bar-fill-structure');
    const barValImpact = document.getElementById('bar-val-impact');
    const barFillImpact = document.getElementById('bar-fill-impact');

    // Keyword chips containers & filters
    const matchedChipsContainer = document.getElementById('matched-chips-container');
    const missingChipsContainer = document.getElementById('missing-chips-container');
    const pillCountMatched = document.getElementById('pill-count-matched');
    const pillCountMissing = document.getElementById('pill-count-missing');
    const filterBtns = document.querySelectorAll('.filter-btn');
    const groupMatched = document.getElementById('group-matched');
    const groupMissing = document.getElementById('group-missing');

    // Improvements & Sections checklist
    const improvementsListContainer = document.getElementById('improvements-list-container');
    const sectionChecksGrid = document.getElementById('section-checks-grid');

    // State Variables
    let selectedFile = null;
    let sampleResumeData = null;
    let sampleJdData = null;

    // =========================================================================
    // File Upload & Drag-and-Drop Handlers
    // =========================================================================

    browseBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        fileInput.click();
    });

    dropzone.addEventListener('click', () => {
        if (!selectedFile && !sampleResumeTextInput.value) {
            fileInput.click();
        }
    });

    ['dragenter', 'dragover'].forEach(eventName => {
        dropzone.addEventListener(eventName, (e) => {
            e.preventDefault();
            e.stopPropagation();
            dropzone.classList.add('drag-active');
        }, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropzone.addEventListener(eventName, (e) => {
            e.preventDefault();
            e.stopPropagation();
            dropzone.classList.remove('drag-active');
        }, false);
    });

    dropzone.addEventListener('drop', (e) => {
        const dt = e.dataTransfer;
        const files = dt.files;
        if (files && files.length > 0) {
            handleFileSelection(files[0]);
        }
    });

    fileInput.addEventListener('change', (e) => {
        if (e.target.files && e.target.files.length > 0) {
            handleFileSelection(e.target.files[0]);
        }
    });

    function handleFileSelection(file) {
        hideError();
        if (!file.name.toLowerCase().endsWith('.pdf')) {
            showError("Invalid File Format", "Please upload a valid PDF document (.pdf).");
            return;
        }

        selectedFile = file;
        sampleResumeTextInput.value = ''; // Clear sample text if file uploaded

        // Update UI
        selectedFileName.textContent = file.name;
        selectedFileSize.textContent = formatBytes(file.size);
        dropzoneDefault.classList.add('hidden');
        dropzoneFileInfo.classList.remove('hidden');
    }

    removeFileBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        resetFileInput();
    });

    function resetFileInput() {
        selectedFile = null;
        fileInput.value = '';
        sampleResumeTextInput.value = '';
        dropzoneFileInfo.classList.add('hidden');
        dropzoneDefault.classList.remove('hidden');
    }

    function formatBytes(bytes, decimals = 1) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const dm = decimals < 0 ? 0 : decimals;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
    }

    // =========================================================================
    // Job Description Live Counter & Samples
    // =========================================================================

    jdInput.addEventListener('input', updateJdWordCount);

    function updateJdWordCount() {
        const text = jdInput.value.trim();
        const count = text ? text.split(/\s+/).length : 0;
        jdWordCount.innerHTML = `<i class="fa-solid fa-font"></i> ${count} words`;
    }

    clearJdBtn.addEventListener('click', () => {
        jdInput.value = '';
        updateJdWordCount();
        hideError();
    });

    // Fetch sample data on demand
    async function fetchSampleData() {
        if (sampleResumeData && sampleJdData) return;
        try {
            const res = await fetch('/api/sample');
            const data = await res.json();
            sampleJdData = data.sample_jd;
            sampleResumeData = data.sample_resume;
        } catch (err) {
            console.error("Failed to load sample data", err);
        }
    }

    loadSampleJdBtn.addEventListener('click', async () => {
        await fetchSampleData();
        if (sampleJdData) {
            jdInput.value = sampleJdData;
            updateJdWordCount();
            hideError();
        }
    });

    useSampleResumeBtn.addEventListener('click', async () => {
        await fetchSampleData();
        if (sampleResumeData) {
            selectedFile = null;
            fileInput.value = '';
            sampleResumeTextInput.value = sampleResumeData;

            // Update UI preview for sample resume
            selectedFileName.textContent = "Alex_Morgan_Resume_Sample.pdf (Sample Data)";
            selectedFileSize.textContent = "Standard Software Engineer Resume";
            dropzoneDefault.classList.add('hidden');
            dropzoneFileInfo.classList.remove('hidden');
            hideError();
        }
    });

    // =========================================================================
    // Error Handling
    // =========================================================================

    function showError(title, msg) {
        document.getElementById('error-title').textContent = title;
        errorMessage.textContent = msg;
        errorBanner.classList.remove('hidden');
        errorBanner.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }

    function hideError() {
        errorBanner.classList.add('hidden');
    }

    closeErrorBtn.addEventListener('click', hideError);

    // =========================================================================
    // Form Submission & Analysis
    // =========================================================================

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        hideError();

        const jobDescription = jdInput.value.trim();

        // Validation
        if (!selectedFile && !sampleResumeTextInput.value.trim()) {
            showError("Resume Required", "Please upload a PDF resume or click 'Load Sample Resume'.");
            return;
        }

        if (!jobDescription) {
            showError("Job Description Required", "Please paste the target job description to match against.");
            return;
        }

        // Set Loading State
        setLoading(true);

        // Prepare FormData
        const formData = new FormData();
        formData.append('job_description', jobDescription);

        if (selectedFile) {
            formData.append('resume_file', selectedFile);
        } else if (sampleResumeTextInput.value) {
            formData.append('resume_text', sampleResumeTextInput.value);
        }

        try {
            const response = await fetch('/api/analyze', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();

            if (!response.ok || !result.success) {
                throw new Error(result.error || "Failed to analyze resume.");
            }

            renderResults(result.data);

        } catch (err) {
            showError("Analysis Error", err.message);
        } finally {
            setLoading(false);
        }
    });

    function setLoading(isLoading) {
        if (isLoading) {
            analyzeBtn.disabled = true;
            analyzeSpinner.classList.remove('hidden');
            analyzeBtn.querySelector('.btn-text-content').style.opacity = '0.7';
        } else {
            analyzeBtn.disabled = false;
            analyzeSpinner.classList.add('hidden');
            analyzeBtn.querySelector('.btn-text-content').style.opacity = '1';
        }
    }

    // =========================================================================
    // Render Results Dashboard
    // =========================================================================

    function renderResults(data) {
        resultsSection.classList.remove('hidden');

        // 1. Overall Score & Gauge Animation
        animateScoreGauge(data.score, data.match_color);

        // 2. Verdict & Level
        matchLevelBadge.textContent = data.match_level;
        matchLevelBadge.className = `score-status-badge badge-${data.match_color}`;
        scoreVerdictTitle.textContent = `${data.match_level} (${data.score}/100)`;
        scoreVerdictDesc.textContent = data.summary_verdict;

        // 3. Stats Overview
        statMatchedKeywords.textContent = data.statistics.matched_keywords_count;
        statMissingKeywords.textContent = data.statistics.missing_keywords_count;
        statWordCount.textContent = data.statistics.word_count;
        statWordStatus.textContent = data.statistics.word_count_status;
        statActionVerbs.textContent = `${data.statistics.action_verbs_count} verbs / ${data.statistics.metrics_count} metrics`;

        // 4. Sub-scores Progress Bars
        barValKeywords.textContent = `${data.sub_scores.keyword_match}%`;
        barFillKeywords.style.width = `${data.sub_scores.keyword_match}%`;

        barValTech.textContent = `${data.sub_scores.tech_skills_match}%`;
        barFillTech.style.width = `${data.sub_scores.tech_skills_match}%`;

        barValStructure.textContent = `${data.sub_scores.structure_score}%`;
        barFillStructure.style.width = `${data.sub_scores.structure_score}%`;

        barValImpact.textContent = `${data.sub_scores.impact_score}%`;
        barFillImpact.style.width = `${data.sub_scores.impact_score}%`;

        // 5. Matched & Missing Keywords Chips
        renderKeywordChips(data.matched_keywords, data.missing_keywords);

        // 6. Areas for Improvement
        renderImprovements(data.improvements);

        // 7. ATS Section Detection
        renderSectionsChecklist(data.sections_detected);

        // Smooth scroll to results
        setTimeout(() => {
            resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }, 100);
    }

    // Animate Circular SVG Gauge
    function animateScoreGauge(targetScore, colorClass) {
        const circumference = 2 * Math.PI * 68; // ~427.26
        const offset = circumference - (targetScore / 100) * circumference;
        
        // Gauge color mapping
        const colorMap = {
            success: '#10b981',
            primary: '#4f46e5',
            warning: '#f59e0b',
            danger: '#ef4444'
        };
        
        gaugeProgressCircle.style.stroke = colorMap[colorClass] || '#4f46e5';
        gaugeProgressCircle.style.strokeDashoffset = offset;

        // Countup animation for number
        let current = 0;
        const duration = 1000;
        const stepTime = 20;
        const steps = duration / stepTime;
        const increment = targetScore / steps;

        const timer = setInterval(() => {
            current += increment;
            if (current >= targetScore) {
                atsScoreDisplay.textContent = targetScore;
                clearInterval(timer);
            } else {
                atsScoreDisplay.textContent = Math.round(current);
            }
        }, stepTime);
    }

    // Render Keyword Badges
    function renderKeywordChips(matchedList, missingList) {
        pillCountMatched.textContent = matchedList.length;
        pillCountMissing.textContent = missingList.length;

        // Matched
        matchedChipsContainer.innerHTML = '';
        if (matchedList.length > 0) {
            matchedList.forEach(kw => {
                const chip = document.createElement('span');
                chip.className = 'chip chip-matched';
                chip.innerHTML = `<i class="fa-solid fa-check"></i> ${escapeHtml(kw)}`;
                matchedChipsContainer.appendChild(chip);
            });
        } else {
            matchedChipsContainer.innerHTML = '<span class="empty-chips-msg">No target keywords directly matched in resume.</span>';
        }

        // Missing
        missingChipsContainer.innerHTML = '';
        if (missingList.length > 0) {
            missingList.forEach(kw => {
                const chip = document.createElement('span');
                chip.className = 'chip chip-missing';
                chip.innerHTML = `<i class="fa-solid fa-plus"></i> ${escapeHtml(kw)}`;
                missingChipsContainer.appendChild(chip);
            });
        } else {
            missingChipsContainer.innerHTML = '<span class="empty-chips-msg">Great job! All target keywords from the JD are present.</span>';
        }
    }

    // Filter Chips Event Listeners
    filterBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            filterBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            const filter = btn.getAttribute('data-filter');

            if (filter === 'all') {
                groupMatched.style.display = 'block';
                groupMissing.style.display = 'block';
            } else if (filter === 'matched') {
                groupMatched.style.display = 'block';
                groupMissing.style.display = 'none';
            } else if (filter === 'missing') {
                groupMatched.style.display = 'none';
                groupMissing.style.display = 'block';
            }
        });
    });

    // Render Actionable Improvement Areas
    function renderImprovements(improvements) {
        improvementsListContainer.innerHTML = '';
        
        if (!improvements || improvements.length === 0) {
            improvementsListContainer.innerHTML = '<p class="text-success">No immediate improvements needed. Resume is highly optimized!</p>';
            return;
        }

        improvements.forEach(item => {
            const priorityClass = `priority-${item.priority.toLowerCase()}`;
            const iconMap = {
                'Missing Hard Skills': 'fa-solid fa-code',
                'Keyword Optimization': 'fa-solid fa-key',
                'Resume Structure': 'fa-solid fa-table-list',
                'Measurable Impact': 'fa-solid fa-chart-line',
                'Content & Phrasing': 'fa-solid fa-pen-nib',
                'Resume Length': 'fa-solid fa-ruler',
                'Optimization': 'fa-solid fa-circle-check'
            };
            const iconClass = iconMap[item.category] || 'fa-solid fa-lightbulb';

            const itemEl = document.createElement('div');
            itemEl.className = 'improvement-item';
            itemEl.innerHTML = `
                <div class="improvement-icon ${priorityClass}-icon">
                    <i class="${iconClass}"></i>
                </div>
                <div class="improvement-content">
                    <div class="improvement-meta">
                        <span class="priority-badge ${priorityClass}">${item.priority} Priority</span>
                        <span class="category-tag">${escapeHtml(item.category)}</span>
                    </div>
                    <h4 class="improvement-title">${escapeHtml(item.title)}</h4>
                    <p class="improvement-desc">${escapeHtml(item.description)}</p>
                </div>
            `;
            improvementsListContainer.appendChild(itemEl);
        });
    }

    // Render Detected Sections
    function renderSectionsChecklist(sections) {
        sectionChecksGrid.innerHTML = '';
        const standardLabels = [
            { key: 'contact', label: 'Contact Info (Email & Phone)' },
            { key: 'experience', label: 'Work Experience' },
            { key: 'skills', label: 'Skills & Technologies' },
            { key: 'education', label: 'Education & Degrees' },
            { key: 'summary', label: 'Professional Summary' },
            { key: 'projects', label: 'Projects / Portfolio' }
        ];

        standardLabels.forEach(sec => {
            const isFound = !!sections[sec.key];
            const div = document.createElement('div');
            div.className = `section-check-item ${isFound ? 'detected' : 'missing'}`;
            div.innerHTML = `
                <i class="${isFound ? 'fa-solid fa-circle-check' : 'fa-regular fa-circle-xmark'}"></i>
                <span>${sec.label}</span>
            `;
            sectionChecksGrid.appendChild(div);
        });
    }

    // Re-analyze / Reset scroll
    reanalyzeBtn.addEventListener('click', () => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });

    // Helper: Escape HTML
    function escapeHtml(str) {
        if (!str) return '';
        return String(str)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
    }
});
