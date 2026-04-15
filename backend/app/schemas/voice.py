from pydantic import BaseModel, Field
from typing import List, Dict, Any

class VoiceParameters(BaseModel):
    pitch_multiplier: float = Field(..., ge=0.5, le=2.0)
    rate_multiplier: float = Field(..., ge=0.5, le=2.0)
    volume_db_offset: float = Field(..., ge=-20.0, le=10.0)
    prosody_markers: List[str] = []
    recommended_voice_traits: Dict[str, str] = {}
    ssml_markup: str = ""

class MappingMetadata(BaseModel):
    emotion: str
    intensity: float
    mapped_at: str
