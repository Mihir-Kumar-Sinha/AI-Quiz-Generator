document.addEventListener('DOMContentLoaded', () => {
    // Tab switching
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');
    
    let currentInputMode = 'text';
    let uploadedFile = null;
    let extractedText = '';

    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            tabBtns.forEach(b => b.classList.remove('active'));
            tabContents.forEach(c => c.classList.remove('active'));
            
            btn.classList.add('active');
            const targetId = btn.getAttribute('data-tab') + '-tab';
            document.getElementById(targetId).classList.add('active');
            currentInputMode = btn.getAttribute('data-tab');
        });
    });

    // Option per question visibility logic based on question type
    const qTypeRadios = document.querySelectorAll('input[name="qType"]');
    const optsGroup = document.getElementById('opts-group');
    
    qTypeRadios.forEach(radio => {
        radio.addEventListener('change', (e) => {
            if(e.target.value === 'MCQ') {
                optsGroup.classList.remove('hidden');
            } else {
                optsGroup.classList.add('hidden');
            }
        });
    });

    // File upload handling
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const fileStatus = document.getElementById('file-status');

    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('dragover');
    });

    dropZone.addEventListener('dragleave', () => {
        dropZone.classList.remove('dragover');
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('dragover');
        if (e.dataTransfer.files.length) {
            handleFile(e.dataTransfer.files[0]);
        }
    });

    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length) {
            handleFile(e.target.files[0]);
        }
    });

    function handleFile(file) {
        const allowedTypes = ['.txt', '.pdf', '.docx'];
        const isValid = allowedTypes.some(ext => file.name.toLowerCase().endsWith(ext));
        
        if (!isValid) {
            fileStatus.innerHTML = '<span style="color: var(--error);">Invalid file type. Only PDF, DOCX, and TXT are supported.</span>';
            uploadedFile = null;
            return;
        }

        uploadedFile = file;
        fileStatus.innerHTML = `File ready: <strong>${file.name}</strong> (${(file.size / 1024).toFixed(1)} KB)`;
    }

    // Generate Button
    const generateBtn = document.getElementById('generate-btn');
    const btnText = generateBtn.querySelector('.btn-text');
    const loader = generateBtn.querySelector('.loader');
    const errorBanner = document.getElementById('error-message');
    const resultsSection = document.getElementById('results-section');
    const quizContainer = document.getElementById('quiz-container');

    generateBtn.addEventListener('click', async () => {
        // Reset Error
        errorBanner.classList.add('hidden');
        errorBanner.innerText = '';
        
        // Loader State
        btnText.classList.add('hidden');
        loader.classList.remove('hidden');
        generateBtn.disabled = true;

        try {
            await runPipeline();
        } catch (err) {
            errorBanner.innerText = err.message || 'An error occurred during generation.';
            errorBanner.classList.remove('hidden');
        } finally {
            btnText.classList.remove('hidden');
            loader.classList.add('hidden');
            generateBtn.disabled = false;
        }
    });

    async function runPipeline() {
        // Step 1: Get Text
        let textToProcess = '';

        if (currentInputMode === 'text') {
            textToProcess = document.getElementById('text-input').value.trim();
            if (!textToProcess) {
                throw new Error("Please enter some text.");
            }
        } else if (currentInputMode === 'file') {
            if (!uploadedFile) {
                throw new Error("Please upload a file.");
            }
            // Need to upload and extract first
            textToProcess = await extractTextFromFile(uploadedFile);
        }

        if (!textToProcess || textToProcess.length < 50) {
            throw new Error("Input text is too short. Please provide meaningful content.");
        }

        // Step 2: Get configuration
        const selectedRadio = document.querySelector('input[name="qType"]:checked');
        if (!selectedRadio) throw new Error("Please select a Question Type (MCQ or Q/A).");
        
        const qType = selectedRadio.value;
        const config = {
            numQs: parseInt(document.getElementById('num-qs').value),
            qType: qType,
            numOpts: qType === 'MCQ' ? parseInt(document.getElementById('num-opts').value) : 0,
            incAns: document.getElementById('inc-ans').checked,
            incExp: document.getElementById('inc-exp').checked
        };

        // Step 3: Call generation API
        const quizData = await generateQuiz(textToProcess, config);
        
        // Step 4: Render Quiz
        renderQuiz(quizData, config);
        
        // Show results, hide form if needed (we'll just scroll)
        resultsSection.classList.remove('hidden');
        resultsSection.scrollIntoView({ behavior: 'smooth' });
    }

    async function extractTextFromFile(file) {
        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch('/api/process-input', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || "Failed to process file.");
        }
        
        return data.text;
    }

    async function generateQuiz(text, config) {
        const response = await fetch('/api/generate-quiz', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                text: text,
                ...config
            })
        });

        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || "Failed to generate quiz.");
        }
        
        return data;
    }

    // Render Logic
    function renderQuiz(quizData, config) {
        quizContainer.innerHTML = ''; // clear previous
        
        if (!quizData.questions || quizData.questions.length === 0) {
            quizContainer.innerHTML = '<p class="text-muted">No questions could be generated from the provided text.</p>';
            return;
        }

        quizData.questions.forEach((q, index) => {
            const card = document.createElement('div');
            card.className = 'quiz-card';
            
            let cardHtml = `
                <div class="quiz-question">${index + 1}. ${escapeHTML(q.question)}</div>
            `;

            // Setup options for MCQ
            if (config.qType === 'MCQ' && q.options) {
                cardHtml += `<div class="quiz-options">`;
                q.options.forEach((opt, optIndex) => {
                    cardHtml += `<button class="option-btn" data-val="${escapeHTML(opt)}">${String.fromCharCode(65 + optIndex)}. ${escapeHTML(opt)}</button>`;
                });
                cardHtml += `</div>`;
            } else {
                // Setup short answer section
                cardHtml += `
                    <div class="qa-input-wrapper">
                        <textarea class="qa-input" placeholder="Type your answer here..."></textarea>
                    </div>
                `;
            }

            // Answer Reveal logic
            if (config.incAns && q.answer) {
                cardHtml += `
                    <button class="reveal-btn">Show Answer</button>
                    <div class="answer-section hidden">
                        <div class="answer-label">Correct Answer:</div>
                        <div class="actual-answer">${escapeHTML(q.answer)}</div>
                        ${config.incExp && q.explanation ? `<div class="explanation">${escapeHTML(q.explanation)}</div>` : ''}
                    </div>
                `;
            }

            card.innerHTML = cardHtml;
            
            // Add interaction logic
            if (config.qType === 'MCQ') {
                const optBtns = card.querySelectorAll('.option-btn');
                optBtns.forEach(btn => {
                    btn.addEventListener('click', () => {
                        // Deselect others
                        optBtns.forEach(b => b.classList.remove('selected'));
                        btn.classList.add('selected');
                        // if answers are included and shown, we could immediately highlight right/wrong
                        // but let's keep it simple: just mark selection. Right/wrong visually handled if reveal is clicked format?
                        // If user wants interactive grading
                    });
                });
            }

            const revealBtn = card.querySelector('.reveal-btn');
            if (revealBtn) {
                revealBtn.addEventListener('click', () => {
                    const ansSec = card.querySelector('.answer-section');
                    if (ansSec.classList.contains('hidden')) {
                        ansSec.classList.remove('hidden');
                        revealBtn.innerText = 'Hide Answer';
                        
                        // If MCQ verify selected
                        if (config.qType === 'MCQ') {
                            const optBtns = card.querySelectorAll('.option-btn');
                            const correctAnsStr = String(q.answer).toLowerCase();
                            optBtns.forEach(btn => {
                                const btnVal = btn.getAttribute('data-val').toLowerCase();
                                if (btnVal === correctAnsStr || correctAnsStr.includes(btnVal)) {
                                    btn.classList.add('correct');
                                } else if (btn.classList.contains('selected')) {
                                    btn.classList.add('wrong');
                                }
                            });
                        }
                    } else {
                        ansSec.classList.add('hidden');
                        revealBtn.innerText = 'Show Answer';
                    }
                });
            }

            quizContainer.appendChild(card);
        });
    }

    // Reset flow
    const resetBtn = document.getElementById('reset-btn');
    resetBtn.addEventListener('click', () => {
        resultsSection.classList.add('hidden');
        quizContainer.innerHTML = '';
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });

    // Utility
    function escapeHTML(str) {
        if (!str) return '';
        return str.replace(/[&<>'"]/g, 
            tag => ({
                '&': '&amp;',
                '<': '&lt;',
                '>': '&gt;',
                "'": '&#39;',
                '"': '&quot;'
            }[tag] || tag)
        );
    }
});
