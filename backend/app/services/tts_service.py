import os
import io
import time
import abc
from typing import Optional, List
from loguru import logger
from pydub import AudioSegment
from app.schemas.tts import AudioOutput
from app.schemas.voice import VoiceParameters

class BaseTTSEngine(abc.ABC):

    @abc.abstractmethod
    async def synthesize(self, text: str, voice_params: VoiceParameters) -> AudioOutput:
        pass

class Pyttsx3LocalProvider(BaseTTSEngine):

    def __init__(self):
        import pyttsx3
        self.engine = pyttsx3.init()
        logger.info("Initialized pyttsx3 Local Provider")

    async def synthesize(self, text: str, voice_params: VoiceParameters) -> AudioOutput:
        import pyttsx3
        import uuid
        start_time = time.time()

        from app.config import settings

        os.makedirs(settings.TEMP_AUDIO_DIR, exist_ok=True)

        unique_id = uuid.uuid4().hex[:8]
        temp_file = os.path.join(settings.TEMP_AUDIO_DIR, f"voice_{unique_id}.wav")

        try:

            rate = self.engine.getProperty('rate')
            self.engine.setProperty('rate', int(rate * voice_params.rate_multiplier))

            vol = 0.8 + (voice_params.volume_db_offset / 20.0)
            self.engine.setProperty('volume', max(0.1, min(1.0, vol)))

            self.engine.save_to_file(text, temp_file)
            self.engine.runAndWait()

            with open(temp_file, "rb") as f:
                audio_bytes = f.read()

            audio = AudioSegment.from_wav(temp_file)
            duration_ms = len(audio)

            logger.info(f"Synthesized audio: {temp_file} ({duration_ms}ms)")

            return AudioOutput(
                audio_bytes=audio_bytes,
                audio_path=temp_file,
                format="wav",
                duration_ms=duration_ms,
                sample_rate=audio.frame_rate,
                provider_used="pyttsx3-local",
                processing_time_ms=int((time.time() - start_time) * 1000),
                ssml_used=False
            )
        except Exception as e:
            logger.error(f"Local TTS Error: {e}")
            if os.path.exists(temp_file):
                os.remove(temp_file)
            raise e

class GoogleCloudProvider(BaseTTSEngine):
    async def synthesize(self, text: str, voice_params: VoiceParameters) -> AudioOutput:

        logger.warning("Google Cloud TTS Implementation pending credentials")
        raise NotImplementedError("Google Cloud credentials required")

class ElevenLabsProvider(BaseTTSEngine):
    async def synthesize(self, text: str, voice_params: VoiceParameters) -> AudioOutput:
        logger.warning("ElevenLabs Implementation pending API Key")
        raise NotImplementedError("ElevenLabs API Key required")
