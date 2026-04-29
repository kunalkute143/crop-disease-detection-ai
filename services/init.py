# services/__init__.py
from .ml_service import CropDiseaseDetector, init_detector, get_detector
from .chatbot_service import FarmingChatbot, init_chatbot, get_chatbot
from .voice_service import VoiceService

__all__ = [
    'CropDiseaseDetector', 'init_detector', 'get_detector',
    'FarmingChatbot', 'init_chatbot', 'get_chatbot',
    'VoiceService'
]