// Scoped Snowflake Logic
function initScopedSnow() {
    const container = document.getElementById('snow-container');
    if (!container) return;

    const chars = ['❄', '❅', '❆'];
    const snowflakes = [];
    const count = 15;

    for (let i = 0; i < count; i++) {
        const s = document.createElement('div');
        s.className = 'snowflake';
        s.innerHTML = chars[Math.floor(Math.random() * chars.length)];
        const left = Math.random() * 100;
        s.style.left = left + '%';
        s.style.animationDuration = (Math.random() * 3 + 4) + 's'; // Faster fall
        s.style.animationDelay = (Math.random() * 5) + 's';
        container.appendChild(s);
        snowflakes.push({ el: s, x: left });
    }

    const section = document.getElementById('upload-section');
    section.addEventListener('mousemove', (e) => {
        const rect = section.getBoundingClientRect();
        const mouseX = ((e.clientX - rect.left) / rect.width) * 100;
        const mouseY = ((e.clientY - rect.top) / rect.height) * 100;

        snowflakes.forEach(snow => {
            const sRect = snow.el.getBoundingClientRect();
            const sX = ((sRect.left + sRect.width/2 - rect.left) / rect.width) * 100;
            const sY = ((sRect.top + sRect.height/2 - rect.top) / rect.height) * 100;

            const dx = sX - mouseX;
            const dy = sY - mouseY;
            const dist = Math.sqrt(dx*dx + dy*dy);

            if (dist < 15) {
                const force = (15 - dist) / 15;
                snow.el.style.transform = `translate(${dx * force * 2}px, ${dy * force * 2}px)`;
            } else {
                snow.el.style.transform = 'translate(0,0)';
            }
        });
    });
}

document.addEventListener('DOMContentLoaded', function() {
    initScopedSnow();
    const themeToggle = document.getElementById('themeToggle');
    const body = document.body;
    const uploadArea = document.getElementById('uploadArea');
    const fileInput = document.getElementById('fileInput');
    const processing = document.getElementById('processing');
    const result = document.getElementById('result');
    const error = document.getElementById('error');
    const resultFilename = document.getElementById('resultFilename');
    const downloadBtn = document.getElementById('downloadBtn');
    const feedbackText = document.getElementById('feedbackText');
    const submitFeedback = document.getElementById('submitFeedback');
    const feedbackSuccess = document.getElementById('feedbackSuccess');

    let generatedContent = '';
    let generatedFilename = '';

    const savedTheme = localStorage.getItem('theme') || 'dark';
    body.className = savedTheme + '-mode';
    updateThemeIcon();

    themeToggle.addEventListener('click', function() {
        if (body.classList.contains('dark-mode')) {
            body.classList.remove('dark-mode');
            body.classList.add('light-mode');
            localStorage.setItem('theme', 'light');
        } else {
            body.classList.remove('light-mode');
            body.classList.add('dark-mode');
            localStorage.setItem('theme', 'dark');
        }
        updateThemeIcon();
    });

    function updateThemeIcon() {
        const icon = themeToggle.querySelector('i');
        if (body.classList.contains('dark-mode')) {
            icon.className = 'fas fa-moon';
        } else {
            icon.className = 'fas fa-sun';
        }
    }

    uploadArea.addEventListener('click', function() {
        fileInput.click();
    });

    uploadArea.addEventListener('dragover', function(e) {
        e.preventDefault();
        uploadArea.classList.add('dragover');
    });

    uploadArea.addEventListener('dragleave', function(e) {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
    });

    uploadArea.addEventListener('drop', function(e) {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFile(files[0]);
        }
    });

    fileInput.addEventListener('change', function() {
        if (fileInput.files.length > 0) {
            handleFile(fileInput.files[0]);
        }
    });

    function handleFile(file) {
        if (!file.name.endsWith('.pkg')) {
            showError('Please upload a .pkg file');
            return;
        }

        uploadArea.style.display = 'none';
        result.style.display = 'none';
        error.style.display = 'none';
        processing.style.display = 'block';

        const formData = new FormData();
        formData.append('file', file);

        fetch('/upload', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            processing.style.display = 'none';

            if (data.error) {
                showError(data.error);
                uploadArea.style.display = 'block';
                return;
            }

            generatedContent = data.content;
            generatedFilename = data.filename;
            resultFilename.textContent = data.filename;
            result.style.display = 'block';
        })
        .catch(err => {
            processing.style.display = 'none';
            showError('An error occurred while processing the file');
            uploadArea.style.display = 'block';
            console.error(err);
        });
    }

    function showError(message) {
        const errorMessage = document.getElementById('errorMessage');
        errorMessage.textContent = message;
        error.style.display = 'flex';
    }

    downloadBtn.addEventListener('click', function() {
        const blob = new Blob([generatedContent], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = generatedFilename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        // Show validation message for 5 seconds after download
        const validationMessage = document.getElementById('validationMessage');
        if (validationMessage) {
            validationMessage.style.display = 'flex';
            setTimeout(() => {
                validationMessage.style.display = 'none';
            }, 5000);
        }
    });

    submitFeedback.addEventListener('click', function() {
        const feedback = feedbackText.value.trim();
        
        if (!feedback) {
            return;
        }

        submitFeedback.disabled = true;
        submitFeedback.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Submitting...';

        fetch('/feedback', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ feedback: feedback })
        })
        .then(response => response.json())
        .then(data => {
            submitFeedback.disabled = false;
            submitFeedback.innerHTML = '<i class="fas fa-paper-plane"></i> Submit Feedback';

            if (data.success) {
                feedbackText.value = '';
                feedbackSuccess.style.display = 'flex';
                setTimeout(() => {
                    feedbackSuccess.style.display = 'none';
                }, 3000);
            }
        })
        .catch(err => {
            submitFeedback.disabled = false;
            submitFeedback.innerHTML = '<i class="fas fa-paper-plane"></i> Submit Feedback';
            console.error(err);
        });
    });

    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
});
