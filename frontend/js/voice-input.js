class VoiceInput {
    constructor() {
        this.recognition = null;
        this.isRecording = false;
        this.finalTranscript = '';
        this.setupSpeechRecognition();
        this.bindEvents();
    }
    
    setupSpeechRecognition() {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        
        if (!SpeechRecognition) {
            console.error("Speech recognition not supported");
            this.showNotSupported();
            return;
        }
        
        this.recognition = new SpeechRecognition();
        this.recognition.continuous = false;
        this.recognition.interimResults = true;
        
        // Set language based on user preference
        const language = localStorage.getItem('preferredLanguage') || 'en';
        this.recognition.lang = language === 'hi' ? 'hi-IN' : 'en-IN';
        
        this.recognition.onstart = () => {
            this.isRecording = true;
            this.finalTranscript = '';
            this.updateUI('recording');
        };
        
        this.recognition.onresult = (event) => {
            let interimTranscript = '';
            
            for (let i = event.resultIndex; i < event.results.length; ++i) {
                if (event.results[i].isFinal) {
                    this.finalTranscript += event.results[i][0].transcript;
                } else {
                    interimTranscript += event.results[i][0].transcript;
                }
            }
            
            // Update textarea with both final and interim results
            document.getElementById('symptomsText').value = this.finalTranscript + interimTranscript;
            
            // Update status with interim results
            if (interimTranscript) {
                document.getElementById('voiceStatus').textContent = `Listening: ${interimTranscript}`;
            }
        };
        
        this.recognition.onend = () => {
            this.isRecording = false;
            this.updateUI('stopped');
            if (this.finalTranscript) {
                document.getElementById('voiceStatus').textContent = 'Recording completed!';
            }
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
                this.updateUI('error', 'Cannot start recording');
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
                voiceBtn.classList.add('recording');
                voiceStatus.textContent = 'Listening... Speak now';
                voiceStatus.style.color = '#3498db';
                break;
            case 'stopped':
                voiceBtn.innerHTML = '🎤 Record Voice Description';
                voiceBtn.classList.remove('recording');
                voiceStatus.style.color = '#27ae60';
                break;
            case 'error':
                voiceBtn.innerHTML = '🎤 Record Voice Description';
                voiceBtn.classList.remove('recording');
                voiceStatus.textContent = `Error: ${error}. Please try again.`;
                voiceStatus.style.color = '#e74c3c';
                break;
        }
    }
    
    showNotSupported() {
        document.getElementById('voiceBtn').disabled = true;
        document.getElementById('voiceBtn').innerHTML = '🎤 Voice Not Supported';
        document.getElementById('voiceStatus').textContent = 
            "Voice input not supported in your browser. Please use Chrome or Edge.";
        document.getElementById('voiceStatus').style.color = '#e74c3c';
    }
}
// Check if microphone access is possible
async function checkMicrophonePermission() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        // Permission granted
        stream.getTracks().forEach(track => track.stop());
        return true;
    } catch (error) {
        console.error('Microphone permission denied:', error);
        document.getElementById('voiceStatus').textContent = 
            'Microphone access denied. Please allow microphone access to use voice input.';
        document.getElementById('voiceStatus').style.color = '#e74c3c';
        return false;
    }
}
// Initialize voice input when page loads
document.addEventListener('DOMContentLoaded', () => {
    new VoiceInput();
});