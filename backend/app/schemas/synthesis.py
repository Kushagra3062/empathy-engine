from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any, Literal
from uuid import uuid4
from datetime import datetime

class SynthesisRequest(BaseModel):
    """
    The API contract for emotion synthesis requests.
    Explicit input validation at the boundary.
    """
    text: str = Field(..., description="Text to synthesize", min_length=1, max_length=5000)
    
    emotion: Optional[Literal[
        "HAPPY", "ANGRY", "FRUSTRATED", 
        "CALM", "SAD", "SURPRISED", 
        "CONCERNED", "NEUTRAL"
    ]] = Field(None, description="Manual emotion override")
    
    intensity: Optional[float] = Field(None, ge=0.0, le=1.0, description="Emotional intensity scaling (0-1)")
    
    target_voice_gender: Literal["male", "female", "neutral"] = "neutral"
    
    output_format: Literal["wav", "mp3"] = "wav"
    sample_rate: int = Field(24000, le=48000)

    @field_validator('text')
    @classmethod
    def text_must_not_be_empty_or_too_long(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Text must not be empty")
        if len(v) > 5000:
            raise ValueError("Text is too long (max 5000 characters)")
        return v

class VoiceParameter(BaseModel):
    value: float
    unit: str
    description: str

class VoiceParametersApplied(BaseModel):
    pitch_shift: VoiceParameter
    speech_rate: VoiceParameter
    volume_shift: VoiceParameter
    breathiness: Optional[VoiceParameter] = None
    harshness: Optional[VoiceParameter] = None
    articulation_clarity: Optional[float] = None
    pause_duration_ms: Optional[int] = None

class SynthesisResponse(BaseModel):
    """Response contract with full metadata"""
    request_id: str = Field(default_factory=lambda: str(uuid4()))
    audio_url: str
    detected_emotion: str
    detected_intensity: float
    confidence: float
    voice_parameters_applied: VoiceParametersApplied
    processing_time_ms: int
    created_at: datetime = Field(default_factory=datetime.utcnow)
    quality_metrics: Optional[Dict[str, float]] = None
