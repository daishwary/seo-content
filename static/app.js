const form = document.getElementById('generateForm');
const submitBtn = document.getElementById('submitBtn');
const btnText = document.getElementById('btnText');
const btnSpinner = document.getElementById('btnSpinner');

const statusSection = document.getElementById('statusSection');
const statusBadge = document.getElementById('statusBadge');
const progressBar = document.getElementById('progressBar');
const statusMessage = document.getElementById('statusMessage');

const resultsSection = document.getElementById('resultsSection');
const errorSection = document.getElementById('errorSection');

let currentJobId = null;
let pollInterval = null;

// Tab Logic
document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
        
        btn.classList.add('active');
        document.getElementById(btn.dataset.tab + 'Tab').classList.add('active');
    });
});

form.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const payload = {
        topic: document.getElementById('topic').value,
        word_count: parseInt(document.getElementById('wordCount').value),
        language: document.getElementById('language').value
    };

    try {
        setLoadingState(true);
        resultsSection.classList.add('hidden');
        errorSection.classList.add('hidden');
        
        const response = await fetch('/api/jobs', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (!response.ok) throw new Error("Failed to start job");
        
        const data = await response.json();
        currentJobId = data.id;
        
        statusSection.classList.remove('hidden');
        updateStatusUI(data.status);
        
        // Start polling
        pollInterval = setInterval(pollJobStatus, 2000);
        
    } catch (err) {
        showError(err.message);
        setLoadingState(false);
    }
});

async function pollJobStatus() {
    if (!currentJobId) return;
    
    try {
        const response = await fetch(`/api/jobs/${currentJobId}`);
        const data = await response.json();
        
        updateStatusUI(data.status);
        
        if (data.status === 'completed') {
            clearInterval(pollInterval);
            renderResults(data.result);
            setLoadingState(false);
            statusSection.classList.add('hidden');
        } else if (data.status === 'failed') {
            clearInterval(pollInterval);
            showError(data.error_message || "Agent process failed.");
            setLoadingState(false);
        }
    } catch (err) {
        console.error("Polling error:", err);
    }
}

function updateStatusUI(status) {
    statusBadge.textContent = status.replace('_', ' ');
    statusBadge.className = `badge ${status}`;
    
    const messages = {
        'pending': 'Initializing agent environment...',
        'running': 'Analyzing SERP data & generating outline and draft content...',
        'scored_revising': 'Editor agent reviewing quality. Making revisions...',
        'completed': 'Content generation complete!',
        'failed': 'Process encountered a critical error.'
    };
    
    const progress = {
        'pending': '10%',
        'running': '50%',
        'scored_revising': '85%',
        'completed': '100%',
        'failed': '100%'
    };
    
    statusMessage.textContent = messages[status] || 'Processing...';
    progressBar.style.width = progress[status] || '0%';
}

function renderResults(result) {
    resultsSection.classList.remove('hidden');
    
    // 1. Preview
    document.getElementById('articleTitle').textContent = result.title;
    document.getElementById('articleContent').innerHTML = marked.parse(result.content_markdown);
    
    // 2. SEO
    document.getElementById('seoTitle').textContent = result.metadata.title_tag;
    document.getElementById('seoDesc').textContent = result.metadata.meta_description;
    document.getElementById('primaryKw').textContent = result.metadata.primary_keyword;
    
    const secKwContainer = document.getElementById('secondaryKwContainer');
    secKwContainer.innerHTML = '<strong>Secondary:</strong>';
    result.metadata.secondary_keywords.forEach(kw => {
        secKwContainer.innerHTML += `<span class="tag">${kw}</span>`;
    });
    
    // 3. Links
    const intLinks = document.getElementById('internalLinks');
    intLinks.innerHTML = '';
    result.internal_links.forEach(l => {
        intLinks.innerHTML += `<li>
            <strong>Anchor:</strong> <span>${l.anchor_text}</span> <br/>
            <strong>Target:</strong> <span>${l.target_topic_or_url}</span>
            <div class="context">${l.context}</div>
        </li>`;
    });
    
    const extLinks = document.getElementById('externalLinks');
    extLinks.innerHTML = '';
    result.external_links.forEach(l => {
        extLinks.innerHTML += `<li>
            <strong>Anchor:</strong> <span>${l.anchor_text}</span> <br/>
            <strong>Target:</strong> <span>${l.target_topic_or_url}</span>
            <div class="context">${l.context}</div>
        </li>`;
    });
    
    // 4. FAQ
    const faqCont = document.getElementById('faqContainer');
    faqCont.innerHTML = '';
    result.faq.forEach(f => {
        faqCont.innerHTML += `<div class="faq-item">
            <div class="faq-question">Q: ${f.question}</div>
            <div class="faq-answer">A: ${f.answer}</div>
        </div>`;
    });
    
    // 5. Schema
    let schemaObj = result.structured_data_schema;
    if (typeof schemaObj === 'string') {
        try { schemaObj = JSON.parse(schemaObj); } catch(e) {}
    }
    document.getElementById('schemaCode').textContent = JSON.stringify(schemaObj, null, 2);
}

function showError(msg) {
    errorSection.classList.remove('hidden');
    document.getElementById('errorMsg').textContent = msg;
    statusSection.classList.add('hidden');
}

function setLoadingState(isLoading) {
    submitBtn.disabled = isLoading;
    if (isLoading) {
        btnText.classList.add('hidden');
        btnSpinner.classList.remove('hidden');
    } else {
        btnText.classList.remove('hidden');
        btnSpinner.classList.add('hidden');
    }
}
