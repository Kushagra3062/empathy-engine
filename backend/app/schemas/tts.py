from pydantic import BaseModel
from typing import Optional, Dict, Any
from app.schemas.emotion import EmotionResult
from app.models.voice_mapper import VoiceParameters

class AudioOutput(BaseModel):
    audio_bytes: Optional[bytes] = None
    audio_path: Optional[str] = None
    format: str  # mp3, wav
    duration_ms: int
    sample_rate: int
    provider_used: str
    processing_time_ms: int
    ssml_used: bool

class SynthesizeRequest(BaseModel):
    text: str
    provider: Optional[str] = "pyttsx3-local"
    voice_id: Optional[str] = None

class SynthesizeResponse(BaseModel):
    text: str
    emotion: EmotionResult
    voice_parameters: VoiceParameters
    audio_url: str
    audio_metadata: Dict[str, Any]
