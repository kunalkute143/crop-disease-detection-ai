// Voice Assistant JavaScript

class VoiceService {
    constructor() {
        this.synthesis = window.speechSynthesis;
        this.recognition = null;
        this.isSupported = this.checkSupport();
        this.voices = [];
        this.selectedVoice = null;
        
        if (this.isSupported) {
            this.loadVoices();
            this.initRecognition();
        }
    }
    
    checkSupport() {
        const hasSpeechSynthesis = 'speechSynthesis' in window;
        const hasSpeechRecognition = 'webkitSpeechRecognition' in window || 'SpeechRecognition' in window;
        
        if (!hasSpeechSynthesis) {
            console.warn('Speech synthesis not supported');
        }
        if (!hasSpeechRecognition) {
            console.warn('Speech recognition not supported');
        }
        
        return hasSpeechSynthesis && hasSpeechRecognition;
    }
    
    loadVoices() {
        this.voices = this.synthesis.getVoices();
        
        // Set default voices for English and Marathi
        this.voices.forEach(voice => {
            if (voice.lang === 'en-US' || voice.lang === 'en-GB') {
                if (!this.selectedVoice) this.selectedVoice = voice;
            }
            if (voice.lang === 'mr-IN') {
                this.marathiVoice = voice;
            }
        });
        
        // If voices not loaded yet, wait for them
        if (this.voices.length === 0) {
            this.synthesis.addEventListener('voiceschanged', () => {
                this.voices = this.synthesis.getVoices();
            });
        }
    }
    
    initRecognition() {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (SpeechRecognition) {
            this.recognition = new SpeechRecognition();
            this.recognition.continuous = false;
            this.recognition.interimResults = false;
            this.recognition.maxAlternatives = 1;
        }
    }
    
    speak(text, language = 'en', options = {}) {
        return new Promise((resolve, reject) => {
            if (!this.synthesis) {
                reject('Speech synthesis not supported');
                return;
            }
            
            const utterance = new SpeechSynthesisUtterance(text);
            
            // Set language
            utterance.lang = language === 'mr' ? 'mr-IN' : 'en-US';
            
            // Set voice
            if (language === 'mr' && this.marathiVoice) {
                utterance.voice = this.marathiVoice;
            } else if (this.selectedVoice) {
                utterance.voice = this.selectedVoice;
            }
            
            // Set options
            utterance.rate = options.rate || 0.9;
            utterance.pitch = options.pitch || 1;
            utterance.volume = options.volume || 1;
            
            utterance.onend = () => resolve();
            utterance.onerror = (error) => reject(error);
            
            this.synthesis.speak(utterance);
        });
    }
    
    listen(language = 'en', options = {}) {
        return new Promise((resolve, reject) => {
            if (!this.recognition) {
                reject('Speech recognition not supported');
                return;
            }
            
            this.recognition.lang = language === 'mr' ? 'mr-IN' : 'en-US';
            this.recognition.continuous = options.continuous || false;
            this.recognition.interimResults = options.interimResults || false;
            
            this.recognition.onresult = (event) => {
                const transcript = event.results[0][0].transcript;
                const confidence = event.results[0][0].confidence;
                resolve({ text: transcript, confidence });
            };
            
            this.recognition.onerror = (event) => {
                reject(event.error);
            };
            
            this.recognition.onend = () => {
                // Recognition ended
            };
            
            this.recognition.start();
        });
    }
    
    stopListening() {
        if (this.recognition) {
            this.recognition.stop();
        }
    }
    
    stopSpeaking() {
        if (this.synthesis) {
            this.synthesis.cancel();
        }
    }
    
    getVoicesByLanguage(language) {
        return this.voices.filter(voice => voice.lang.startsWith(language));
    }
    
    isSpeaking() {
        return this.synthesis && this.synthesis.speaking;
    }
    
    isPaused() {
        return this.synthesis && this.synthesis.paused;
    }
    
    pause() {
        if (this.synthesis && this.synthesis.speaking) {
            this.synthesis.pause();
        }
    }
    
    resume() {
        if (this.synthesis && this.synthesis.paused) {
            this.synthesis.resume();
        }
    }
}

// Voice Commands for Farming
class FarmingVoiceCommands {
    constructor(voiceService) {
        this.voice = voiceService;
        this.commands = {
            'upload': ['upload', 'photo', 'picture', 'अपलोड', 'फोटो'],
            'chat': ['chat', 'ask', 'question', 'चॅट', 'विचारा'],
            'dashboard': ['dashboard', 'history', 'डॅशबोर्ड', 'इतिहास'],
            'help': ['help', 'मदत'],
            'home': ['home', 'मुख्यपृष्ठ']
        };
    }
    
    async processCommand(text) {
        text = text.toLowerCase();
        
        for (const [command, keywords] of Object.entries(this.commands)) {
            if (keywords.some(keyword => text.includes(keyword))) {
                return command;
            }
        }
        
        return null;
    }
    
    async listenForCommand() {
        try {
            const result = await this.voice.listen();
            const command = await this.processCommand(result.text);
            
            if (command) {
                return { command, text: result.text };
            } else {
                return { command: 'unknown', text: result.text };
            }
        } catch (error) {
            console.error('Voice command error:', error);
            return null;
        }
    }
    
    executeCommand(command, data) {
        switch(command) {
            case 'upload':
                window.location.href = '/crop/upload';
                break;
            case 'chat':
                window.location.href = '/chat/assistant';
                break;
            case 'dashboard':
                window.location.href = '/dashboard';
                break;
            case 'help':
                this.voice.speak('How can I help you? You can say upload, chat, or dashboard');
                break;
            case 'home':
                window.location.href = '/';
                break;
            default:
                this.voice.speak('Command not recognized. Please try again.');
        }
    }
}

// Initialize voice service
document.addEventListener('DOMContentLoaded', () => {
    window.voiceService = new VoiceService();
    window.voiceCommands = new FarmingVoiceCommands(window.voiceService);
});