/**
 * NoHate - Frontend JavaScript
 * Handles API calls, dynamic result rendering, charts, and animations.
 */

// ─── State ──────────────────────────────────────────────────────────────────
const API_BASE = '';
let analysisHistory = JSON.parse(localStorage.getItem('nohate_history') || '[]');

// ─── Sample Texts ───────────────────────────────────────────────────────────
const SAMPLES = {
    hate: "I hate all those people, they are disgusting trash and should die. They are subhuman and worthless scum.",
    offensive: "You are so stupid and dumb, what an idiot loser. Shut up you moron, nobody cares about your pathetic opinion.",
    clean: "I really enjoyed the seminar on artificial intelligence today. The speaker discussed fascinating advances in machine learning and natural language processing."
};

// ─── Initialize ─────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    const textInput = document.getElementById('text-input');
    
    // Character count
    textInput.addEventListener('input', () => {
        const count = textInput.value.length;
        document.getElementById('char-count').textContent = `${count} / 5000`;
    });

    // Enter key shortcut (Ctrl+Enter)
    textInput.addEventListener('keydown', (e) => {
        if (e.ctrlKey && e.key === 'Enter') {
            analyzeText();
        }
    });

    // Load model info
    loadModelInfo();

    // Render history
    renderHistory();
});

// ─── Load Sample Text ───────────────────────────────────────────────────────
function loadSample(type) {
    const textInput = document.getElementById('text-input');
    textInput.value = SAMPLES[type] || '';
    textInput.dispatchEvent(new Event('input'));
    textInput.focus();
}

// ─── Analyze Text ───────────────────────────────────────────────────────────
async function analyzeText() {
    const textInput = document.getElementById('text-input');
    const text = textInput.value.trim();
    
    if (!text) {
        showToast('Please enter some text to analyze.', true);
        return;
    }

    const btn = document.getElementById('analyze-btn');
    const btnContent = btn.querySelector('.btn-content');
    const btnLoading = btn.querySelector('.btn-loading');

    // Show loading state
    btn.disabled = true;
    btnContent.style.display = 'none';
    btnLoading.style.display = 'flex';

    try {
        const response = await fetch(`${API_BASE}/api/analyze`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text })
        });

        if (!response.ok) {
            throw new Error('Analysis failed. Please try again.');
        }

        const result = await response.json();
        
        if (result.error) {
            throw new Error(result.error);
        }

        // Add to history
        addToHistory(result);

        // Render results
        renderResults(result);

    } catch (error) {
        showToast(error.message || 'An error occurred. Please try again.', true);
    } finally {
        btn.disabled = false;
        btnContent.style.display = 'flex';
        btnLoading.style.display = 'none';
    }
}

// ─── Render Results ─────────────────────────────────────────────────────────
function renderResults(result) {
    const section = document.getElementById('results-section');
    section.style.display = 'block';

    // Smooth scroll to results
    setTimeout(() => {
        section.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }, 100);

    // ─── Classification Badge ──────────────────────────────────────────
    const headerCard = document.getElementById('result-header');
    headerCard.className = 'glass-card result-header-card';
    
    const classIcons = { 'Hate Speech': '🚨', 'Offensive Language': '⚠️', 'Clean': '🛡️' };
    const classColors = { 'Hate Speech': 'class-hate', 'Offensive Language': 'class-offensive', 'Clean': 'class-clean' };
    
    document.getElementById('class-icon').textContent = classIcons[result.classification] || '🔍';
    document.getElementById('class-label').textContent = result.classification;
    document.getElementById('class-confidence').textContent = `${result.confidence}% confidence`;
    
    const badge = document.getElementById('class-badge');
    badge.className = `class-badge ${classColors[result.classification] || ''}`;

    // ─── Confidence Ring ───────────────────────────────────────────────
    drawConfidenceRing(result.confidence, result.classification);

    // ─── Stats Cards ───────────────────────────────────────────────────
    const stats = result.stats || {};
    animateValue('stat-hate-pct', 0, stats.hate_percentage || 0, '%');
    animateValue('stat-clean-pct', 0, stats.clean_percentage || 100, '%');
    document.getElementById('stat-total-words').textContent = stats.total_words || 0;
    document.getElementById('stat-flagged-words').textContent = stats.hateful_words || 0;

    // Animate bars
    setTimeout(() => {
        document.getElementById('hate-bar').style.width = `${stats.hate_percentage || 0}%`;
        document.getElementById('clean-bar').style.width = `${stats.clean_percentage || 100}%`;
    }, 200);

    // ─── Probability Chart ─────────────────────────────────────────────
    drawProbabilityChart(result.probabilities);

    // ─── Highlighted Text ──────────────────────────────────────────────
    renderHighlightedText(result);

    // ─── Flagged Words List ────────────────────────────────────────────
    renderFlaggedWords(result.flagged_words || []);

    // ─── Improved Text ─────────────────────────────────────────────────
    document.getElementById('improved-text').textContent = result.improved_text || result.original_text;

    // ─── Suggestions ───────────────────────────────────────────────────
    const sugList = document.getElementById('suggestions-list');
    sugList.innerHTML = '';
    (result.suggestions || []).forEach(s => {
        const li = document.createElement('li');
        li.textContent = s;
        sugList.appendChild(li);
    });

    // ─── Preprocessed Text ─────────────────────────────────────────────
    document.getElementById('preprocessed-text').textContent = result.preprocessed_text || '';
}

// ─── Draw Confidence Ring (Canvas) ──────────────────────────────────────────
function drawConfidenceRing(confidence, classification) {
    const canvas = document.getElementById('confidence-canvas');
    const ctx = canvas.getContext('2d');
    const size = 120;
    const center = size / 2;
    const radius = 48;
    const lineWidth = 8;

    ctx.clearRect(0, 0, size, size);

    // Background ring
    ctx.beginPath();
    ctx.arc(center, center, radius, 0, Math.PI * 2);
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.06)';
    ctx.lineWidth = lineWidth;
    ctx.stroke();

    // Confidence arc
    const colors = {
        'Hate Speech': '#f87171',
        'Offensive Language': '#fb923c',
        'Clean': '#34d399'
    };
    const color = colors[classification] || '#818cf8';
    const endAngle = (confidence / 100) * Math.PI * 2 - Math.PI / 2;

    // Animated drawing
    let currentAngle = -Math.PI / 2;
    const step = (endAngle + Math.PI / 2) / 60;
    let frame = 0;

    function animate() {
        if (frame >= 60) return;
        frame++;
        currentAngle += step;

        ctx.clearRect(0, 0, size, size);

        // Background ring
        ctx.beginPath();
        ctx.arc(center, center, radius, 0, Math.PI * 2);
        ctx.strokeStyle = 'rgba(255, 255, 255, 0.06)';
        ctx.lineWidth = lineWidth;
        ctx.stroke();

        // Gradient arc
        const gradient = ctx.createLinearGradient(0, 0, size, size);
        gradient.addColorStop(0, color);
        gradient.addColorStop(1, color + '80');
        
        ctx.beginPath();
        ctx.arc(center, center, radius, -Math.PI / 2, currentAngle);
        ctx.strokeStyle = gradient;
        ctx.lineWidth = lineWidth;
        ctx.lineCap = 'round';
        ctx.stroke();

        // Glow effect
        ctx.beginPath();
        ctx.arc(center, center, radius, -Math.PI / 2, currentAngle);
        ctx.strokeStyle = color + '30';
        ctx.lineWidth = lineWidth + 6;
        ctx.stroke();

        requestAnimationFrame(animate);
    }

    animate();

    // Update value
    const valueEl = document.getElementById('confidence-value');
    valueEl.textContent = `${confidence}%`;
    valueEl.style.color = color;
}

// ─── Draw Probability Donut Chart ───────────────────────────────────────────
function drawProbabilityChart(probabilities) {
    const canvas = document.getElementById('prob-chart');
    const ctx = canvas.getContext('2d');
    const size = 240;
    const center = size / 2;
    const outerRadius = 100;
    const innerRadius = 65;

    ctx.clearRect(0, 0, size, size);

    const data = [
        { label: 'Hate Speech', value: probabilities['Hate Speech'] || 0, color: '#f87171' },
        { label: 'Offensive', value: probabilities['Offensive Language'] || 0, color: '#fb923c' },
        { label: 'Clean', value: probabilities['Clean'] || 0, color: '#34d399' }
    ];

    const total = data.reduce((sum, d) => sum + d.value, 0) || 1;
    let startAngle = -Math.PI / 2;

    data.forEach(item => {
        const sliceAngle = (item.value / total) * Math.PI * 2;
        
        // Draw slice
        ctx.beginPath();
        ctx.arc(center, center, outerRadius, startAngle, startAngle + sliceAngle);
        ctx.arc(center, center, innerRadius, startAngle + sliceAngle, startAngle, true);
        ctx.closePath();
        ctx.fillStyle = item.color;
        ctx.fill();

        // Add slight gap
        ctx.beginPath();
        ctx.arc(center, center, outerRadius, startAngle, startAngle + sliceAngle);
        ctx.arc(center, center, innerRadius, startAngle + sliceAngle, startAngle, true);
        ctx.closePath();
        ctx.strokeStyle = 'rgba(10, 10, 26, 0.8)';
        ctx.lineWidth = 2;
        ctx.stroke();

        startAngle += sliceAngle;
    });

    // Center text
    ctx.fillStyle = '#e2e8f0';
    ctx.font = '700 14px Inter';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText('Distribution', center, center);

    // Legend
    const legendEl = document.getElementById('chart-legend');
    legendEl.innerHTML = data.map(item => `
        <div class="legend-item">
            <span class="legend-color" style="background:${item.color}"></span>
            <span class="legend-label">${item.label}:</span>
            <span class="legend-value">${item.value.toFixed(1)}%</span>
        </div>
    `).join('');
}

// ─── Render Highlighted Text ────────────────────────────────────────────────
function renderHighlightedText(result) {
    const container = document.getElementById('highlighted-text');
    const flaggedSet = new Set((result.flagged_words || []).map(f => f.word.toLowerCase()));
    const words = result.original_text.split(/\s+/);

    container.innerHTML = words.map(word => {
        const cleanWord = word.toLowerCase().replace(/[^\w]/g, '');
        if (flaggedSet.has(cleanWord)) {
            const flagData = result.flagged_words.find(f => f.word.toLowerCase() === cleanWord);
            const replacement = flagData ? flagData.replacement : '';
            return `<span class="word-flagged">${escapeHtml(word)}<span class="tooltip">⚠️ Suggest: "${replacement}"</span></span>`;
        }
        return `<span class="word-safe">${escapeHtml(word)} </span>`;
    }).join(' ');
}

// ─── Render Flagged Words List ──────────────────────────────────────────────
function renderFlaggedWords(flaggedWords) {
    const container = document.getElementById('flagged-list');
    
    if (flaggedWords.length === 0) {
        container.innerHTML = '<p style="color: var(--accent-green); font-size: 0.85rem; padding: 10px;">✅ No hateful or offensive words detected!</p>';
        return;
    }

    container.innerHTML = flaggedWords.map(item => `
        <div class="flagged-item">
            <span class="flagged-word">"${escapeHtml(item.word)}"</span>
            <span class="flagged-arrow">→</span>
            <span class="flagged-replacement">"${escapeHtml(item.replacement)}"</span>
            <span class="flagged-reason">${item.severity === 'high' ? '🔴 High' : '🟡 Medium'}</span>
        </div>
    `).join('');
}

// ─── Animated Counter ───────────────────────────────────────────────────────
function animateValue(elementId, start, end, suffix = '') {
    const el = document.getElementById(elementId);
    const duration = 1000;
    const startTime = performance.now();

    function update(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        const eased = 1 - Math.pow(1 - progress, 3); // easeOutCubic
        const current = Math.round(start + (end - start) * eased * 10) / 10;
        
        el.textContent = `${current}${suffix}`;
        
        if (progress < 1) {
            requestAnimationFrame(update);
        } else {
            el.textContent = `${end}${suffix}`;
        }
    }

    requestAnimationFrame(update);
}

// ─── Load Model Info ────────────────────────────────────────────────────────
async function loadModelInfo() {
    try {
        const response = await fetch(`${API_BASE}/api/model-info`);
        const info = await response.json();

        if (info.accuracy) {
            document.getElementById('model-accuracy').textContent = `${info.accuracy}%`;
            document.getElementById('model-samples').textContent = (info.training_samples || 0).toLocaleString();
            document.getElementById('model-features').textContent = (info.features || 0).toLocaleString();
            document.getElementById('model-test').textContent = (info.test_samples || 0).toLocaleString();
        }
    } catch (error) {
        // Model info not available yet (server might be starting)
        console.log('Model info not available yet.');
    }
}

// ─── History Management ─────────────────────────────────────────────────────
function addToHistory(result) {
    const entry = {
        text: result.original_text,
        classification: result.classification,
        confidence: result.confidence,
        timestamp: new Date().toISOString()
    };

    analysisHistory.unshift(entry);
    if (analysisHistory.length > 20) analysisHistory.pop();
    
    localStorage.setItem('nohate_history', JSON.stringify(analysisHistory));
    renderHistory();
}

function renderHistory() {
    const section = document.getElementById('history-section');
    const list = document.getElementById('history-list');

    if (analysisHistory.length === 0) {
        section.style.display = 'none';
        return;
    }

    section.style.display = 'block';

    const classMap = {
        'Hate Speech': { indicator: 'indicator-hate', badge: 'history-class-hate' },
        'Offensive Language': { indicator: 'indicator-offensive', badge: 'history-class-offensive' },
        'Clean': { indicator: 'indicator-clean', badge: 'history-class-clean' }
    };

    list.innerHTML = analysisHistory.map((entry, idx) => {
        const cls = classMap[entry.classification] || classMap['Clean'];
        const truncText = entry.text.length > 60 ? entry.text.substring(0, 60) + '...' : entry.text;
        return `
            <div class="history-item" onclick="reanalyze(${idx})">
                <span class="history-indicator ${cls.indicator}"></span>
                <span class="history-text">${escapeHtml(truncText)}</span>
                <span class="history-class ${cls.badge}">${entry.classification}</span>
            </div>
        `;
    }).join('');
}

function reanalyze(index) {
    const entry = analysisHistory[index];
    if (entry) {
        document.getElementById('text-input').value = entry.text;
        document.getElementById('text-input').dispatchEvent(new Event('input'));
        document.getElementById('input-section').scrollIntoView({ behavior: 'smooth' });
    }
}

function clearHistory() {
    analysisHistory = [];
    localStorage.removeItem('nohate_history');
    renderHistory();
}

// ─── Utility Functions ──────────────────────────────────────────────────────
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function showToast(message, isError = false) {
    const existing = document.querySelector('.toast');
    if (existing) existing.remove();

    const toast = document.createElement('div');
    toast.className = `toast ${isError ? 'toast-error' : ''}`;
    toast.textContent = message;
    document.body.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(30px)';
        toast.style.transition = 'all 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}
