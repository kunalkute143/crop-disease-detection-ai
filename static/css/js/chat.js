// Chat Assistant JavaScript

class ChatAssistant {
    constructor() {
        this.messagesContainer = document.getElementById('chatMessages');
        this.inputField = document.getElementById('messageInput');
        this.sendButton = document.getElementById('sendBtn');
        this.voiceButton = document.getElementById('voiceBtn');
        this.suggestionsContainer = document.getElementById('suggestions');
        this.language = document.documentElement.lang || 'en';
        
        this.voiceAssistant = new VoiceAssistant();
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.loadSuggestions();
        this.scrollToBottom();
    }
    
    setupEventListeners() {
        // Send message on button click
        if (this.sendButton) {
            this.sendButton.addEventListener('click', () => this.sendMessage());
        }
        
        // Send message on Enter key
        if (this.inputField) {
            this.inputField.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    this.sendMessage();
                }
            });
        }
        
        // Voice input
        if (this.voiceButton) {
            this.voiceButton.addEventListener('click', () => this.toggleVoiceInput());
        }
        
        // Suggestion chips
        if (this.suggestionsContainer) {
            this.suggestionsContainer.addEventListener('click', (e) => {
                if (e.target.classList.contains('suggestion-chip')) {
                    this.inputField.value = e.target.textContent;
                    this.sendMessage();
                }
            });
        }
    }
    
    async sendMessage() {
        const message = this.inputField.value.trim();
        if (!message) return;
        
        // Add user message to chat
        this.addMessage(message, 'user');
        this.inputField.value = '';
        
        // Show typing indicator
        this.showTypingIndicator();
        
        try {
            const response = await fetch('/chat/api/message', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    language: this.language
                })
            });
            
            const data = await response.json();
            this.removeTypingIndicator();
            
            if (data.status === 'success') {
                this.addMessage(data.response, 'bot');
                
                // Optional: Speak the response
                if (this.voiceAssistant && confirm('🔊 Hear response?')) {
                    this.voiceAssistant.speak(data.response, this.language);
                }
            } else {
                this.addMessage('Error: ' + data.response, 'bot');
            }
        } catch (error) {
            this.removeTypingIndicator();
            this.addMessage('Network error. Please try again.', 'bot');
            console.error('Chat error:', error);
        }
    }
    
    addMessage(text, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender} animate-slide-up`;
        
        const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        
        if (sender === 'user') {
            messageDiv.innerHTML = `
                <div class="message-content user">
                    <p>${this.escapeHtml(text)}</p>
                    <span class="message-time">${time}</span>
                </div>
                <div class="message-avatar user">
                    <i class="fas fa-user"></i>
                </div>
            `;
        } else {
            messageDiv.innerHTML = `
                <div class="message-avatar bot">
                    <i class="fas fa-robot"></i>
                </div>
                <div class="message-content bot">
                    <p>${this.escapeHtml(text)}</p>
                    <span class="message-time">${time}</span>
                </div>
            `;
        }
        
        this.messagesContainer.appendChild(messageDiv);
        this.scrollToBottom();
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    showTypingIndicator() {
        const indicator = document.createElement('div');
        indicator.className = 'message bot typing-indicator-container';
        indicator.id = 'typingIndicator';
        indicator.innerHTML = `
            <div class="message-avatar bot">
                <i class="fas fa-robot"></i>
            </div>
            <div class="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
            </div>
        `;
        
        this.messagesContainer.appendChild(indicator);
        this.scrollToBottom();
    }
    
    removeTypingIndicator() {
        const indicator = document.getElementById('typingIndicator');
        if (indicator) {
            indicator.remove();
        }
    }
    
    scrollToBottom() {
        this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
    }
    
    toggleVoiceInput() {
        if (this.voiceAssistant.isListening) {
            this.voiceAssistant.stopListening();
            this.voiceButton.classList.remove('listening');
        } else {
            this.voiceAssistant.setLanguage(this.language);
            this.voiceAssistant.startListening();
            this.voiceButton.classList.add('listening');
        }
    }
    
    async loadSuggestions() {
        try {
            const response = await fetch('/chat/api/suggestions');
            const data = await response.json();
            
            if (data.status === 'success' && this.suggestionsContainer) {
                this.suggestionsContainer.innerHTML = '';
                data.suggestions.forEach(suggestion => {
                    const chip = document.createElement('button');
                    chip.className = 'suggestion-chip';
                    chip.textContent = suggestion;
                    this.suggestionsContainer.appendChild(chip);
                });
            }
        } catch (error) {
            console.error('Failed to load suggestions:', error);
        }
    }
}

// Voice Assistant Class
class VoiceAssistant {
    constructor() {
        this.recognition = null;
        this.synthesis = window.speechSynthesis;
        this.isListening = false;
        this.onVoiceInput = null;
        this.onStatusChange = null;
        
        this.initRecognition();
    }
    
    initRecognition() {
        if ('webkitSpeechRecognition' in window) {
            this.recognition = new webkitSpeechRecognition();
            this.setupRecognition();
        } else if ('SpeechRecognition' in window) {
            this.recognition = new SpeechRecognition();
            this.setupRecognition();
        } else {
            console.warn('Speech recognition not supported');
        }
    }
    
    setupRecognition() {
        this.recognition.continuous = false;
        this.recognition.interimResults = false;
        this.recognition.maxAlternatives = 1;
        
        this.recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            if (this.onVoiceInput) {
                this.onVoiceInput(transcript);
            }
        };
        
        this.recognition.onerror = (event) => {
            console.error('Speech recognition error:', event.error);
            this.isListening = false;
            if (this.onStatusChange) {
                this.onStatusChange(false);
            }
        };
        
        this.recognition.onend = () => {
            this.isListening = false;
            if (this.onStatusChange) {
                this.onStatusChange(false);
            }
        };
    }
    
    setLanguage(lang) {
        if (this.recognition) {
            this.recognition.lang = lang === 'mr' ? 'mr-IN' : 'en-US';
        }
    }
    
    startListening() {
        if (this.recognition && !this.isListening) {
            this.isListening = true;
            this.recognition.start();
            if (this.onStatusChange) {
                this.onStatusChange(true);
            }
        }
    }
    
    stopListening() {
        if (this.recognition && this.isListening) {
            this.recognition.stop();
            this.isListening = false;
            if (this.onStatusChange) {
                this.onStatusChange(false);
            }
        }
    }
    
    speak(text, lang = 'en') {
        this.synthesis.cancel();
        
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = lang === 'mr' ? 'mr-IN' : 'en-US';
        utterance.rate = 0.9;
        utterance.pitch = 1;
        utterance.volume = 1;
        
        this.synthesis.speak(utterance);
    }
}

// Initialize chat when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('chatMessages')) {
        window.chatAssistant = new ChatAssistant();
    }
});