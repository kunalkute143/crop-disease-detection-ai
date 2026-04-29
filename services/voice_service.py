# services/voice_service.py
import base64
import json

class VoiceService:
    """Service for voice processing (Web Speech API wrapper)"""
    
    def __init__(self):
        self.supported_languages = {
            'en': 'en-US',
            'mr': 'mr-IN'
        }
    
    def text_to_speech(self, text, language='en'):
        """
        Convert text to speech
        Note: Actual TTS is handled by browser's Web Speech API
        This method prepares the text for client-side TTS
        """
        if not text:
            return None
        
        # Return the text to be spoken by browser
        return {
            'text': text,
            'lang': self.supported_languages.get(language, 'en-US'),
            'rate': 0.9,  # Slightly slower for clarity
            'pitch': 1.0
        }
    
    def speech_to_text(self, audio_data, language='en'):
        """
        Convert speech to text
        Note: Actual STT is handled by browser's Web Speech API
        This method would process audio if using server-side STT
        """
        # In production, integrate with Google Speech-to-Text or similar
        # For now, return placeholder
        return {
            'text': '',
            'confidence': 0,
            'language': language
        }
    
    def get_voice_config(self, language='en'):
        """Get voice configuration for client"""
        return {
            'language': self.supported_languages.get(language, 'en-US'),
            'continuous': False,
            'interimResults': False,
            'maxAlternatives': 1
        }