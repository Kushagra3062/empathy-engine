from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional

class EmotionResult(BaseModel):
    primary_emotion: str  # HAPPY, ANGRY, etc.
    confidence: float = Field(..., ge=0.0, le=1.0)
    intensity: float = Field(..., ge=0.0, le=1.0)
    intensity_level: str  # "minimal", "light", "medium", "strong", "maximum"
    all_emotions: Dict[str, float]  # All 8 emotions with scores
    model_scores: Dict[str, float]  # Individual model confidences
    linguistic_cues: Dict[str, Any]  # Debug info: caps, punctuation, etc.
    processing_time_ms: float  # Latency
    model_used: str  # Which ensemble model

class EmotionRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=5000)
    context: Optional[str] = None
