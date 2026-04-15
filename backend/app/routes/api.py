import os
import time
from fastapi import APIRouter, Depends, Query, HTTPException
from fastapi.responses import FileResponse
from loguru import logger
from sqlalchemy.orm import Session
from app.database import get_db
from app.db_models import SynthesisLog
from app.schemas.synthesis import SynthesisRequest, SynthesisResponse
from app.container import container
from app.config import settings

router = APIRouter()

@router.post("/synthesize", response_model=SynthesisResponse)
async def synthesize(request: SynthesisRequest, db: Session = Depends(get_db)):
    """
    Main Orchestration Endpoint (Layer 1).
    Coordinates Layer 3 (Detection), Layer 4 (Mapping), and Layer 5 (Synthesis).
    """
    start_time = time.time()
    
    try:
        # 1. Access Services via Container (DI)
        detector = container.get_emotion_detector()
        mapper = container.get_voice_mapper()
        tts = container.get_tts_service()
        
        # 2. Emotion Detection (Layer 3)
        # If user provided an emotion, we use it but still run detector for confidence/intensity
        detection_res = detector.detect_emotion(request.text)
        
        emotion = request.emotion or detection_res["primary_emotion"]
        intensity = request.intensity or detection_res["intensity"]
        
        # 3. Voice Mapping (Layer 4)
        voice_params = mapper.map_to_voice_parameters(
            emotion=emotion,
            intensity=intensity,
            gender=request.target_voice_gender
        )
        
        # 4. Neural Synthesis & Post-Processing (Layer 5)
        audio_filename = await tts.synthesize(
            text=request.text,
            params=voice_params,
            output_format=request.output_format
        )
        audio_path = os.path.join(settings.TEMP_AUDIO_DIR, audio_filename)
        
        # 5. Quality Metrics & Cleanup
        metrics = tts.calculate_metrics(audio_path)
        processing_time_ms = int((time.time() - start_time) * 1000)
        
        # 6. Audit Logging (Layer 6)
        log_entry = SynthesisLog(
            request_id=str(time.time()), # Placeholder for more robust UUID if needed
            text_sample=request.text[:497] + "...",
            detected_emotion=emotion,
            intensity=intensity,
            confidence=detection_res["confidence"],
            voice_params=voice_params.dict(),
            audio_filename=audio_filename,
            processing_time_ms=processing_time_ms,
            quality_metrics=metrics
        )
        db.add(log_entry)
        db.commit()
        
        # 7. Final Response
        return SynthesisResponse(
            audio_url=f"/api/v1/audio/{audio_filename}",
            detected_emotion=emotion,
            detected_intensity=intensity,
            confidence=detection_res["confidence"],
            voice_parameters_applied=voice_params,
            processing_time_ms=processing_time_ms,
            quality_metrics=metrics
        )
        
    except Exception as e:
        logger.error(f"Orchestration failed: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/audio/{filename}")
async def serve_audio(filename: str):
    """Securely serve generated audio assets."""
    file_path = os.path.join(settings.TEMP_AUDIO_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Audio resource not found")
    return FileResponse(file_path)

@router.get("/history")
async def get_history(db: Session = Depends(get_db)):
    """Retrieve synthesis audit trail."""
    return db.query(SynthesisLog).order_by(SynthesisLog.created_at.desc()).limit(20).all()
