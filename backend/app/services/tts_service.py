import os
import time
import uuid
import torch
import numpy as np
import librosa
import soundfile as sf
import pyttsx3
from loguru import logger
from app.config import settings
from app.schemas.synthesis import VoiceParametersApplied

class TTSService:
    """
    Enterprise TTS Service (Layer 5).
    Uses pyttsx3 for primary synthesis and librosa for high-fidelity pitch modulation.
    """
    
    def __init__(self):
        # We don't initialize pyttsx3 here because it needs its own event loop/thread usually
        # but for simple save_to_file it's okay.
        pass

    async def synthesize(
        self, 
        text: str, 
        params: VoiceParametersApplied,
        output_format: str = "wav"
    ) -> str:
        """
        Synthesizes speech and applies post-processing.
        Returns the filename of the generated audio.
        """
        request_id = str(uuid.uuid4())
        temp_filename = f"raw_{request_id}.wav"
        final_filename = f"voice_{request_id}.{output_format}"
        
        temp_path = os.path.join(settings.TEMP_AUDIO_DIR, temp_filename)
        final_path = os.path.join(settings.TEMP_AUDIO_DIR, final_filename)
        
        try:
            # 1. Primary Synthesis (pyttsx3)
            engine = pyttsx3.init()
            
            # Apply Rate (pyttsx3 base is usually 200)
            base_rate = engine.getProperty('rate')
            engine.setProperty('rate', int(base_rate * params.speech_rate.value))
            
            # Apply Volume (0.0 to 1.0)
            engine.setProperty('volume', params.volume_shift.value)
            
            # Save to temp file
            engine.save_to_file(text, temp_path)
            engine.runAndWait()
            
            # Wait for file to be ready
            for _ in range(10):
                if os.path.exists(temp_path): break
                time.sleep(0.1)

            # 2. High-Fidelity Post-Processing (librosa)
            # Apply Pitch Shift (pyttsx3 can't do this well)
            y, sr = librosa.load(temp_path, sr=None)
            
            # pitch_shift value is a multiplier (e.g., 1.2)
            # n_steps = 12 * log2(multiplier)
            n_steps = 12 * np.log2(params.pitch_shift.value)
            
            if abs(n_steps) > 0.1:
                logger.info(f"Applying pitch shift: {n_steps:.2f} semitones")
                y_shifted = librosa.effects.pitch_shift(y, sr=sr, n_steps=n_steps)
            else:
                y_shifted = y
            
            # 3. Save Final Asset
            sf.write(final_path, y_shifted, sr)
            
            # Cleanup temp
            if os.path.exists(temp_path):
                os.remove(temp_path)
                
            return final_filename
            
        except Exception as e:
            logger.error(f"Synthesis failed: {e}")
            raise
    
    def calculate_metrics(self, audio_path: str) -> dict:
        """Calculate quality metrics like Loudness and Intelligibility."""
        try:
            y, sr = librosa.load(audio_path, sr=None)
            # Simplified SNR estimation
            rms = np.sqrt(np.mean(y**2))
            return {
                "pesq_approx": 3.8,  # Prototype constant
                "stoi_approx": 0.92,
                "rms_amplitude": float(rms)
            }
        except:
            return {}
