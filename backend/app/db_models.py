from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, Text, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from .database import Base

class EmotionDetectionLog(Base):
    __tablename__ = "emotion_detection_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    text = Column(Text, nullable=False)
    detected_emotion = Column(String(50), index=True)
    confidence = Column(Float)
    intensity = Column(Float)
    intensity_level = Column(String(20))
    all_emotions = Column(JSON)
    linguistic_cues = Column(JSON)
    processing_time_ms = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class SynthesisLog(Base):
    __tablename__ = "synthesis_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    text = Column(Text, nullable=False)
    emotion_id = Column(String(36), ForeignKey("emotion_detection_logs.id"))
    voice_id = Column(String(100))
    audio_url = Column(String(255))
    pitch_multiplier = Column(Float)
    rate_multiplier = Column(Float)
    volume_db_offset = Column(Float)
    ssml_used = Column(Boolean, default=False)
    provider = Column(String(50))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
