from sqlalchemy import Column, String, Float, DateTime, JSON, Integer
from .database import Base
from datetime import datetime
from uuid import uuid4

class SynthesisLog(Base):
    """
    Layer 6 Audit Log: Tracks every synthesis event with full metadata.
    """
    __tablename__ = "synthesis_logs"

    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(String, unique=True, index=True, default=lambda: str(uuid4()))
    text_sample = Column(String(500))
    detected_emotion = Column(String)
    intensity = Column(Float)
    confidence = Column(Float)
    voice_params = Column(JSON)
    audio_filename = Column(String)
    processing_time_ms = Column(Float)
    quality_metrics = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

class SystemMetrics(Base):
    """Tracks global system performance KPIs."""
    __tablename__ = "system_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    metric_name = Column(String)
    metric_value = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)
