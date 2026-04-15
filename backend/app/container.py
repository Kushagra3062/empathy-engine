import os
from typing import Dict, Any, Protocol, List
from .models.emotion_detector import EmotionDetector
from .models.voice_mapper import ScientificVoiceParameterMapper
from .services.tts_service import TTSService
from .database import get_db
from sqlalchemy.orm import Session

class ServiceContainer:
    """
    Central registry for all services.
    Enables dependency injection and swapping implementations.
    """
    
    def __init__(self):
        self._services = {}
        # Initialized on demand or at startup
        self._initialize_core_services()

    def _initialize_core_services(self):
        # Layer 3: Ensemble Emotion Detector
        self._services['emotion_detector'] = EmotionDetector()
        
        # Layer 4: Scientific Voice Mapper
        self._services['voice_mapper'] = ScientificVoiceParameterMapper()
        
        # Layer 5: TTS Service
        self._services['tts_service'] = TTSService()

    def get_emotion_detector(self) -> EmotionDetector:
        return self._services['emotion_detector']

    def get_voice_mapper(self) -> ScientificVoiceParameterMapper:
        return self._services['voice_mapper']

    def get_tts_service(self) -> TTSService:
        return self._services['tts_service']

# Global container instance
container = ServiceContainer()
