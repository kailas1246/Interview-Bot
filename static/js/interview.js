class InterviewBot {
    constructor() {
        this.sessionId = null;
        this.currentQuestionNumber = 0;
        this.totalQuestions = 0;
        this.isListening = false;
        this.recognition = null;
        this.synthesis = window.speechSynthesis;
        
        this.initializeElements();
        this.initializeSpeechRecognition();
        this.bindEvents();
    }

    initializeElements() {
        // Role selection elements
        this.roleSelect = document.getElementById('roleSelect');
        this.startInterviewBtn = document.getElementById('startInterview');
        this.roleSelection = document.getElementById('roleSelection');
        
        // Interview interface elements
        this.interviewInterface = document.getElementById('interviewInterface');
        this.progressBar = document.getElementById('progressBar');
        this.progressText = document.getElementById('progressText');
        this.questionText = document.getElementById('questionText');
        this.listenBtn = document.getElementById('listenBtn');
        this.listenText = document.getElementById('listenText');
        this.speakQuestionBtn = document.getElementById('speakQuestionBtn');
        this.exitInterviewBtn = document.getElementById('exitInterviewBtn');
        this.voiceStatus = document.getElementById('voiceStatus');
        this.statusText = document.getElementById('statusText');
        this.answerText = document.getElementById('answerText');
        this.submitAnswerBtn = document.getElementById('submitAnswer');
        this.feedbackCard = document.getElementById('feedbackCard');
        this.feedbackContent = document.getElementById('feedbackContent');
        
        // Summary interface elements
        this.summaryInterface = document.getElementById('summaryInterface');
        this.finalScore = document.getElementById('finalScore');
        this.overallFeedbackText = document.getElementById('overallFeedbackText');
        this.detailedResults = document.getElementById('detailedResults');
        this.restartBtn = document.getElementById('restartBtn');
        
        // Error elements
        this.errorAlert = document.getElementById('errorAlert');
        this.errorText = document.getElementById('errorText');
    }

    initializeSpeechRecognition() {
        if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
            this.showError('Speech recognition is not supported in this browser. Please use Chrome or Edge.');
            return;
        }

        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        this.recognition = new SpeechRecognition();
        
        this.recognition.continuous = true;
        this.recognition.interimResults = true;
        this.recognition.lang = 'en-US';

        this.recognition.onstart = () => {
            this.isListening = true;
            this.updateListenButton();
            this.showVoiceStatus('Listening... Speak now!');
        };

        this.recognition.onresult = (event) => {
            let finalTranscript = '';
            let interimTranscript = '';

            for (let i = event.resultIndex; i < event.results.length; i++) {
                const transcript = event.results[i][0].transcript;
                if (event.results[i].isFinal) {
                    finalTranscript += transcript;
                } else {
                    interimTranscript += transcript;
                }
            }

            this.answerText.value = finalTranscript + interimTranscript;
            
            if (finalTranscript) {
                this.submitAnswerBtn.disabled = false;
            }
        };

        this.recognition.onerror = (event) => {
            this.isListening = false;
            this.updateListenButton();
            this.hideVoiceStatus();
            
            let errorMessage = 'Speech recognition error: ';
            switch(event.error) {
                case 'no-speech':
                    errorMessage += 'No speech detected. Please try again.';
                    break;
                case 'audio-capture':
                    errorMessage += 'No microphone found. Please check your microphone.';
                    break;
                case 'not-allowed':
                    errorMessage += 'Microphone access denied. Please allow microphone access.';
                    break;
                default:
                    errorMessage += event.error;
            }
            this.showError(errorMessage);
        };

        this.recognition.onend = () => {
            this.isListening = false;
            this.updateListenButton();
            this.hideVoiceStatus();
        };
    }

    bindEvents() {
        this.roleSelect.addEventListener('change', () => {
            this.startInterviewBtn.disabled = !this.roleSelect.value;
        });

        this.startInterviewBtn.addEventListener('click', () => {
            this.startInterview();
        });

        this.listenBtn.addEventListener('click', () => {
            this.toggleListening();
        });

        this.speakQuestionBtn.addEventListener('click', () => {
            this.speakQuestion();
        });

        this.exitInterviewBtn.addEventListener('click', () => {
            this.exitInterview();
        });

        this.submitAnswerBtn.addEventListener('click', () => {
            this.submitAnswer();
        });

        this.restartBtn.addEventListener('click', () => {
            this.restart();
        });

        // Allow manual text input
        this.answerText.addEventListener('input', () => {
            this.submitAnswerBtn.disabled = !this.answerText.value.trim();
        });

        // Add keyboard shortcut for exit (Escape key)
        document.addEventListener('keydown', (event) => {
            if (event.key === 'Escape' && this.sessionId && this.interviewInterface.classList.contains('d-none') === false) {
                this.exitInterview();
            }
        });
    }

    async startInterview() {
        const selectedRole = this.roleSelect.value;
        if (!selectedRole) {
            this.showError('Please select a role first.');
            return;
        }

        try {
            const response = await fetch('/api/start-interview', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ role: selectedRole })
            });

            if (!response.ok) {
                throw new Error('Failed to start interview');
            }

            const data = await response.json();
            this.sessionId = data.session_id;
            this.totalQuestions = data.total_questions;
            this.currentQuestionNumber = 1;

            this.showInterviewInterface();
            this.displayQuestion(data.first_question);
            this.updateProgress();
            this.hideError();

            // Automatically speak the first question
            setTimeout(() => {
                this.speakQuestion();
            }, 1000);

        } catch (error) {
            this.showError('Failed to start interview: ' + error.message);
        }
    }

    showInterviewInterface() {
        this.roleSelection.classList.add('d-none');
        this.interviewInterface.classList.remove('d-none');
        this.summaryInterface.classList.add('d-none');
    }

    displayQuestion(question) {
        this.questionText.textContent = question;
        this.answerText.value = '';
        this.submitAnswerBtn.disabled = true;
        this.feedbackCard.classList.add('d-none');
    }

    updateProgress() {
        const progress = (this.currentQuestionNumber / this.totalQuestions) * 100;
        this.progressBar.style.width = progress + '%';
        this.progressText.textContent = `Question ${this.currentQuestionNumber} of ${this.totalQuestions}`;
    }

    toggleListening() {
        if (this.isListening) {
            this.recognition.stop();
        } else {
            this.recognition.start();
        }
    }

    updateListenButton() {
        if (this.isListening) {
            this.listenBtn.className = 'btn btn-danger btn-lg';
            this.listenBtn.innerHTML = '<i class="fas fa-stop me-2"></i><span>Stop Listening</span>';
        } else {
            this.listenBtn.className = 'btn btn-success btn-lg';
            this.listenBtn.innerHTML = '<i class="fas fa-microphone me-2"></i><span>Start Speaking</span>';
        }
    }

    speakQuestion() {
        if (this.synthesis.speaking) {
            this.synthesis.cancel();
        }

        const utterance = new SpeechSynthesisUtterance(this.questionText.textContent);
        utterance.rate = 0.8;
        utterance.pitch = 1;
        utterance.volume = 1;

        this.synthesis.speak(utterance);
    }

    showVoiceStatus(message) {
        this.statusText.textContent = message;
        this.voiceStatus.classList.remove('d-none');
    }

    hideVoiceStatus() {
        this.voiceStatus.classList.add('d-none');
    }

    async submitAnswer() {
        const answer = this.answerText.value.trim();
        if (!answer) {
            this.showError('Please provide an answer before submitting.');
            return;
        }

        try {
            this.submitAnswerBtn.disabled = true;
            this.submitAnswerBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Submitting...';

            const response = await fetch('/api/submit-answer', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    session_id: this.sessionId,
                    answer: answer
                })
            });

            if (!response.ok) {
                throw new Error('Failed to submit answer');
            }

            const data = await response.json();
            this.displayFeedback(data.feedback, data.score, data.is_satisfactory, data.specific_issues, data.improvement_suggestions);

            if (data.interview_complete) {
                setTimeout(() => {
                    this.showSummary();
                }, 3000);
            } else if (data.repeat_question) {
                // Answer was not satisfactory, repeat question
                setTimeout(() => {
                    this.displayRetryMessage(data.retry_message);
                    this.speakRetryMessage(data.retry_message);
                }, 3000);
            } else {
                // Move to next question
                this.currentQuestionNumber = data.question_number;
                this.updateProgress();
                
                setTimeout(() => {
                    this.displayQuestion(data.next_question);
                    this.speakQuestion();
                }, 3000);
            }

        } catch (error) {
            this.showError('Failed to submit answer: ' + error.message);
        } finally {
            this.submitAnswerBtn.innerHTML = '<i class="fas fa-paper-plane me-2"></i>Submit Answer';
        }
    }

    displayFeedback(feedback, score, isSatisfactory, issues, suggestions) {
        const scoreClass = score >= 8 ? 'text-success' : score >= 6 ? 'text-warning' : 'text-danger';
        const satisfactoryClass = isSatisfactory ? 'alert-success' : 'alert-warning';
        const satisfactoryIcon = isSatisfactory ? 'fa-check-circle' : 'fa-exclamation-triangle';
        
        let issuesHTML = '';
        if (issues && issues.length > 0) {
            issuesHTML = `
                <div class="mt-3">
                    <h6 class="text-danger"><i class="fas fa-times-circle me-2"></i>Issues Found:</h6>
                    <ul class="mb-0">
                        ${issues.map(issue => `<li>${issue}</li>`).join('')}
                    </ul>
                </div>
            `;
        }
        
        let suggestionsHTML = '';
        if (suggestions && suggestions.length > 0) {
            suggestionsHTML = `
                <div class="mt-3">
                    <h6 class="text-info"><i class="fas fa-lightbulb me-2"></i>Suggestions:</h6>
                    <ul class="mb-0">
                        ${suggestions.map(suggestion => `<li>${suggestion}</li>`).join('')}
                    </ul>
                </div>
            `;
        }
        
        this.feedbackContent.innerHTML = `
            <div class="alert ${satisfactoryClass} mb-3">
                <i class="fas ${satisfactoryIcon} me-2"></i>
                <strong>${isSatisfactory ? 'Answer Accepted' : 'Answer Needs Improvement'}</strong>
            </div>
            <div class="d-flex justify-content-between align-items-center mb-2">
                <strong>Score:</strong>
                <span class="${scoreClass} fs-5">${score}/10</span>
            </div>
            <p class="mb-0">${feedback}</p>
            ${issuesHTML}
            ${suggestionsHTML}
        `;
        
        this.feedbackCard.classList.remove('d-none');
        
        // Speak the feedback
        const speakText = isSatisfactory ? 
            `Good answer! Score: ${score} out of 10. ${feedback}` :
            `Your answer needs improvement. Score: ${score} out of 10. ${feedback}`;
        
        const utterance = new SpeechSynthesisUtterance(speakText);
        utterance.rate = 0.8;
        this.synthesis.speak(utterance);
    }

    displayRetryMessage(message) {
        // Clear previous answer
        this.answerText.value = '';
        this.submitAnswerBtn.disabled = true;
        
        // Show retry message
        const retryHTML = `
            <div class="alert alert-info mb-3">
                <i class="fas fa-redo me-2"></i>
                <strong>Please Try Again:</strong> ${message}
            </div>
        `;
        
        // Add retry message to feedback
        this.feedbackContent.innerHTML += retryHTML;
        
        // Keep the same question displayed
        // No need to change the question text since it's the same question
    }

    speakRetryMessage(message) {
        const utterance = new SpeechSynthesisUtterance(message + " " + this.questionText.textContent);
        utterance.rate = 0.8;
        this.synthesis.speak(utterance);
    }

    async exitInterview() {
        // Stop any ongoing speech
        if (this.synthesis.speaking) {
            this.synthesis.cancel();
        }
        
        // Stop speech recognition if active
        if (this.isListening) {
            this.recognition.stop();
        }

        // Show confirmation dialog
        const confirmExit = confirm("Are you sure you want to exit the interview? Your progress will be lost.");
        
        if (confirmExit) {
            // Cancel the interview session on the backend
            if (this.sessionId) {
                try {
                    await fetch('/api/cancel-interview', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({ session_id: this.sessionId })
                    });
                } catch (error) {
                    console.log('Error cancelling interview:', error);
                }
            }
            
            // Speak exit message
            const exitMessage = "Interview ended. Thank you for practicing with us!";
            const utterance = new SpeechSynthesisUtterance(exitMessage);
            utterance.rate = 0.8;
            this.synthesis.speak(utterance);
            
            // Reset to initial state
            this.restart();
        }
    }

    async showSummary() {
        try {
            const response = await fetch('/api/get-summary', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ session_id: this.sessionId })
            });

            if (!response.ok) {
                throw new Error('Failed to get summary');
            }

            const data = await response.json();
            this.displaySummary(data);

        } catch (error) {
            this.showError('Failed to load summary: ' + error.message);
        }
    }

    displaySummary(summaryData) {
        this.interviewInterface.classList.add('d-none');
        this.summaryInterface.classList.remove('d-none');

        this.finalScore.textContent = summaryData.final_score;
        this.overallFeedbackText.textContent = summaryData.overall_feedback;

        // Display detailed results
        let detailedHTML = '';
        summaryData.detailed_results.forEach((result, index) => {
            const scoreClass = result.score >= 8 ? 'text-success' : result.score >= 6 ? 'text-warning' : 'text-danger';
            detailedHTML += `
                <div class="card mb-3">
                    <div class="card-body">
                        <div class="d-flex justify-content-between align-items-start mb-2">
                            <h6 class="card-title mb-0">Question ${index + 1}</h6>
                            <span class="${scoreClass} fw-bold">${result.score}/10</span>
                        </div>
                        <p class="text-muted mb-2">${result.question}</p>
                        <p class="mb-2"><strong>Your Answer:</strong> ${result.answer}</p>
                        <p class="mb-0"><strong>Feedback:</strong> ${result.feedback}</p>
                    </div>
                </div>
            `;
        });

        this.detailedResults.innerHTML = detailedHTML;

        // Speak the final feedback
        const finalMessage = `Interview complete! Your final score is ${summaryData.final_score} out of 10. ${summaryData.overall_feedback}`;
        const utterance = new SpeechSynthesisUtterance(finalMessage);
        utterance.rate = 0.8;
        this.synthesis.speak(utterance);
    }

    restart() {
        this.sessionId = null;
        this.currentQuestionNumber = 0;
        this.totalQuestions = 0;
        
        this.roleSelection.classList.remove('d-none');
        this.interviewInterface.classList.add('d-none');
        this.summaryInterface.classList.add('d-none');
        
        this.roleSelect.value = '';
        this.startInterviewBtn.disabled = true;
        this.hideError();
        
        if (this.synthesis.speaking) {
            this.synthesis.cancel();
        }
        
        if (this.isListening) {
            this.recognition.stop();
        }
    }

    showError(message) {
        this.errorText.textContent = message;
        this.errorAlert.classList.remove('d-none');
    }

    hideError() {
        this.errorAlert.classList.add('d-none');
    }
}

// Initialize the interview bot when the page loads
document.addEventListener('DOMContentLoaded', () => {
    new InterviewBot();
});
