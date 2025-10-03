class VoiceInput {
    constructor() {
        this.recognition = null;
        this.isRecording = false;
        this.setupSpeechRecognition();
        this.bindEvents();
    }
    
    setupSpeechRecognition() {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        
        if (!SpeechRecognition) {
            console.error("Speech recognition not supported");
            document.getElementById('voiceBtn').disabled = true;
            document.getElementById('voiceStatus').textContent = 
                "Voice input not supported in your browser";
            return;
        }
        
        this.recognition = new SpeechRecognition();
        this.recognition.continuous = false;
        this.recognition.interimResults = true;
        this.recognition.lang = localStorage.getItem('preferredLanguage') === 'hi' ? 'hi-IN' : 'en-IN';
        
        this.recognition.onstart = () => {
            this.isRecording = true;
            this.updateUI('recording');
        };
        
        this.recognition.onresult = (event) => {
            const transcript = Array.from(event.results)
                .map(result => result[0].transcript)
                .join('');
            
            document.getElementById('symptomsText').value = transcript;
        };
        
        this.recognition.onend = () => {
            this.isRecording = false;
            this.updateUI('stopped');
        };
        
        this.recognition.onerror = (event) => {
            console.error("Speech recognition error:", event.error);
            this.isRecording = false;
            this.updateUI('error', event.error);
        };
    }
    
    bindEvents() {
        document.getElementById('voiceBtn').addEventListener('click', () => {
            if (this.isRecording) {
                this.stopRecording();
            } else {
                this.startRecording();
            }
        });
    }
    
    startRecording() {
        if (this.recognition) {
            try {
                this.recognition.start();
            } catch (error) {
                console.error("Error starting recognition:", error);
            }
        }
    }
    
    stopRecording() {
        if (this.recognition && this.isRecording) {
            this.recognition.stop();
        }
    }
    
    updateUI(state, error = '') {
        const voiceBtn = document.getElementById('voiceBtn');
        const voiceStatus = document.getElementById('voiceStatus');
        
        switch (state) {
            case 'recording':
                voiceBtn.innerHTML = '⏹️ Stop Recording';
                voiceBtn.style.background = '#e74c3c';
                voiceStatus.textContent = 'Listening... Speak now';
                voiceStatus.style.color = '#3498db';
                break;
            case 'stopped':
                voiceBtn.innerHTML = '🎤 Record Voice Description';
                voiceBtn.style.background = '';
                voiceStatus.textContent = 'Recording stopped';
                voiceStatus.style.color = '#27ae60';
                break;
            case 'error':
                voiceBtn.innerHTML = '🎤 Record Voice Description';
                voiceBtn.style.background = '';
                voiceStatus.textContent = `Error: ${error}. Please try again.`;
                voiceStatus.style.color = '#e74c3c';
                break;
        }
    }
}

// Initialize voice input when page loads
document.addEventListener('DOMContentLoaded', () => {
    new VoiceInput();
});