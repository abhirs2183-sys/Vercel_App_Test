// Snowflake generation
function createSnowflakes() {
    const snowContainer = document.getElementById('snow');
    if (!snowContainer) return;
    
    const snowflakeChars = ['❄', '❅', '❆', '✻', '✼'];
    const count = 30;
    const snowflakes = [];
    
    for (let i = 0; i < count; i++) {
        const snowflake = document.createElement('div');
        snowflake.className = 'snowflake';
        snowflake.innerHTML = snowflakeChars[Math.floor(Math.random() * snowflakeChars.length)];
        const left = Math.random() * 100;
        snowflake.style.left = left + 'vw';
        snowflake.style.animationDuration = (Math.random() * 10 + 10) + 's';
        snowflake.style.animationDelay = (Math.random() * 20) + 's';
        snowflake.style.fontSize = (Math.random() * 1 + 0.5) + 'em';
        snowContainer.appendChild(snowflake);
        snowflakes.push({ element: snowflake, originalLeft: left });
    }

    // Mouse reaction: Point 4 - "Bust out" effect
    document.addEventListener('mousemove', (e) => {
        const mouseX = e.clientX;
        const mouseY = e.clientY;
        
        snowflakes.forEach(s => {
            const rect = s.element.getBoundingClientRect();
            const snowX = rect.left + rect.width / 2;
            const snowY = rect.top + rect.height / 2;
            
            const diffX = snowX - mouseX;
            const diffY = snowY - mouseY;
            const distance = Math.sqrt(diffX * diffX + diffY * diffY);
            
            // Interaction radius: 150px
            if (distance < 150) {
                const power = (150 - distance) / 150;
                const forceX = (diffX / distance) * power * 50; // Push intensity
                const forceY = (diffY / distance) * power * 50;
                
                s.element.style.transition = 'transform 0.3s ease-out';
                s.element.style.transform = `translate(${forceX}px, ${forceY}px)`;
            } else {
                s.element.style.transform = 'translate(0, 0)';
            }
        });
    });
}

// Modal handling: Point 5
function showNewYearModal() {
    if (localStorage.getItem('newYearGreetingShown')) return;

    const modal = document.createElement('div');
    modal.className = 'modal-overlay';
    modal.innerHTML = `
        <div class="greeting-modal">
            <h2>Happy New Year!</h2>
            <p>Goodbye 2025, Hello 2026! We wish you a prosperous and productive year ahead. Thank you for being a part of yDatafix.</p>
            <button class="close-modal">Get Started</button>
        </div>
    `;
    document.body.appendChild(modal);

    setTimeout(() => modal.classList.add('active'), 100);

    modal.querySelector('.close-modal').addEventListener('click', () => {
        modal.classList.remove('active');
        setTimeout(() => modal.remove(), 300);
        localStorage.setItem('newYearGreetingShown', 'true');
    });
}

document.addEventListener('DOMContentLoaded', function() {
    createSnowflakes();
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
