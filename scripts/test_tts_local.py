import asyncio
import sys
import os

# Add the backend path to sys.path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.services.tts_service import Pyttsx3LocalProvider
from app.schemas.voice import VoiceParameters
from loguru import logger

async def test_local_tts():
    provider = Pyttsx3LocalProvider()
    
    # Simulate voice parameters for two different emotions
    test_cases = [
        ("Happy text", VoiceParameters(
            pitch_multiplier=1.2,
            rate_multiplier=1.1,
            volume_db_offset=3.0,
            prosody_markers=["high-pitch", "fast-tempo"]
        )),
        ("Sad text", VoiceParameters(
            pitch_multiplier=0.85,
            rate_multiplier=0.8,
            volume_db_offset=-5.0,
            prosody_markers=["low-pitch", "slow-tempo"]
        ))
    ]
    
    logger.info("Starting Local TTS Synthesis Tests")
    
    for i, (text, params) in enumerate(test_cases):
        logger.info(f"Synthesizing Case {i+1}: '{text}'")
        try:
            output = await provider.synthesize(
                f"This is a test of {text}. Emotional parameters applied.", 
                params
            )
            
            # Save audio for manual verification
            filename = f"test_output_{i+1}.wav"
            with open(filename, "wb") as f:
                f.write(output.audio_bytes)
            
            print(f"✅ Success! Saved to {filename}")
            print(f"   Duration: {output.duration_ms}ms")
            print(f"   Processing Time: {output.processing_time_ms}ms")
            
        except Exception as e:
            logger.error(f"Failed to synthesize case {i+1}: {e}")

if __name__ == "__main__":
    asyncio.run(test_local_tts())
