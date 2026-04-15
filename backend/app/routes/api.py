from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.schemas.emotion import EmotionRequest, EmotionResult
from app.schemas.tts import SynthesizeRequest, SynthesizeResponse
from app.models.emotion_detector import EmotionDetector
from app.models.voice_mapper import VoiceParameterMapper
from app.services.tts_service import Pyttsx3LocalProvider
from app.config import settings
from app.database import get_db, init_db
from app.db_models import EmotionDetectionLog, SynthesisLog
from loguru import logger
import os
import time

init_db()

router = APIRouter()

detector = EmotionDetector()
mapper = VoiceParameterMapper()
local_tts = Pyttsx3LocalProvider()

@router.post("/process", response_model=EmotionResult)
async def process_text(request: EmotionRequest, db: Session = Depends(get_db)):

    try:
        result = detector.detect_emotion(request.text)

        db_log = EmotionDetectionLog(
            text=request.text,
            detected_emotion=result.primary_emotion,
            confidence=result.confidence,
            intensity=result.intensity,
            intensity_level=result.intensity_level,
            all_emotions=result.all_emotions,
            linguistic_cues=result.linguistic_cues,
            processing_time_ms=result.processing_time_ms
        )
        db.add(db_log)
        db.commit()

        return result
    except Exception as e:
        logger.error(f"Error processing text: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/synthesize", response_model=SynthesizeResponse)
async def synthesize_voice(request: SynthesizeRequest, db: Session = Depends(get_db)):

    try:
        start_time = time.time()

        emotion_result = detector.detect_emotion(request.text)

        voice_params = mapper.map_emotion_to_voice(emotion_result, text=request.text)

        audio_output = await local_tts.synthesize(request.text, voice_params)

        duration_ms = (time.time() - start_time) * 1000

        filename = os.path.basename(audio_output.audio_path) if audio_output.audio_path else "fallback.wav"
        audio_url = f"{settings.API_V1_STR}/audio/{filename}"

        db_detect = EmotionDetectionLog(
            text=request.text,
            detected_emotion=emotion_result.primary_emotion,
            confidence=emotion_result.confidence,
            intensity=emotion_result.intensity,
            intensity_level=emotion_result.intensity_level,
            all_emotions=emotion_result.all_emotions,
            linguistic_cues=emotion_result.linguistic_cues,
            processing_time_ms=emotion_result.processing_time_ms
        )
        db.add(db_detect)
        db.flush() 

        db_synth = SynthesisLog(
            text=request.text,
            emotion_id=db_detect.id,
            voice_id=request.voice_id,
            audio_url=audio_url,
            pitch_multiplier=voice_params.pitch_multiplier,
            rate_multiplier=voice_params.rate_multiplier,
            volume_db_offset=voice_params.volume_db_offset,
            ssml_used=True,
            provider=audio_output.provider_used
        )
        db.add(db_synth)
        db.commit()

        return {
            "text": request.text,
            "emotion": emotion_result,
            "voice_parameters": voice_params,
            "audio_url": audio_url,
            "audio_metadata": {
                "format": audio_output.format,
                "duration_ms": audio_output.duration_ms,
                "provider": audio_output.provider_used,
                "total_processing_time_ms": round(duration_ms, 2)
            }
        }
    except Exception as e:
        logger.error(f"Synthesis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/audio/{filename}")
async def get_audio_file(filename: str):

    safe_filename = os.path.basename(filename)
    file_path = os.path.join(settings.TEMP_AUDIO_DIR, safe_filename)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Audio not found")

    return FileResponse(file_path, media_type="audio/wav")

@router.get("/history")
async def get_history(limit: int = 50, db: Session = Depends(get_db)):

    history = db.query(SynthesisLog).order_by(SynthesisLog.created_at.desc()).limit(limit).all()
    return history

@router.post("/feedback")
async def submit_feedback(audio_id: str, rating: int, comment: str = None, db: Session = Depends(get_db)):

    logger.info(f"Feedback for {audio_id}: Rating {rating}, Comment: {comment}")
    return {"status": "success", "message": "Feedback received"}
