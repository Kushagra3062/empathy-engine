from typing import Dict, Any, List
from loguru import logger
from app.schemas.voice import VoiceParameters
from app.schemas.emotion import EmotionResult

class VoiceParameterMapper:

    EMOTION_VOICE_CORRELATES = {
        "HAPPY": {
            "pitch_range": (1.2, 1.6),
            "rate_range": (1.2, 1.8),
            "volume_range": (+2.0, +6.0),
            "traits": {"pitch": "high", "speed": "fast", "energy": "high"}
        },
        "ANGRY": {
            "pitch_range": (0.85, 0.7),
            "rate_range": (1.1, 1.4),
            "volume_range": (+3.0, +8.0),
            "traits": {"pitch": "low/harsh", "speed": "fast/staccato", "energy": "intense"}
        },
        "SAD": {
            "pitch_range": (0.75, 0.6),
            "rate_range": (0.6, 0.4),
            "volume_range": (-10.0, -4.0),
            "traits": {"pitch": "very low", "speed": "very slow", "energy": "low"}
        },
        "FRUSTRATED": {
            "pitch_range": (0.9, 0.8),
            "rate_range": (1.1, 1.3),
            "volume_range": (+2.0, +5.0),
            "traits": {"pitch": "tense", "speed": "hurried", "energy": "unstable"}
        },
        "CALM": {
            "pitch_range": (0.95, 0.9),
            "rate_range": (0.8, 0.7),
            "volume_range": (-3.0, -1.0),
            "traits": {"pitch": "stable", "speed": "relaxed", "energy": "low"}
        },
        "SURPRISED": {
            "pitch_range": (1.3, 1.8),
            "rate_range": (1.2, 1.5),
            "volume_range": (+2.0, +5.0),
            "traits": {"pitch": "very high", "speed": "fast", "energy": "explosive"}
        },
        "CONCERNED": {
            "pitch_range": (1.05, 1.15),
            "rate_range": (1.0, 1.1),
            "volume_range": (-2.0, +1.0),
            "traits": {"pitch": "slightly high", "speed": "moderate", "energy": "uncertain"}
        },
        "NEUTRAL": {
            "pitch_range": (1.0, 1.0),
            "rate_range": (1.0, 1.0),
            "volume_range": (0.0, 0.0),
            "traits": {"pitch": "flat", "speed": "normal", "energy": "neutral"}
        }
    }

    def map_emotion_to_voice(self, emotion_result: EmotionResult, text: str = "Placeholder text") -> VoiceParameters:

        emotion = emotion_result.primary_emotion.upper()
        intensity = emotion_result.intensity

        correlates = self.EMOTION_VOICE_CORRELATES.get(emotion, self.EMOTION_VOICE_CORRELATES["NEUTRAL"])

        pitch_mult = self._interpolate(1.0, correlates["pitch_range"], intensity)
        rate_mult = self._interpolate(1.0, correlates["rate_range"], intensity)
        volume_offset = self._interpolate(0.0, correlates["volume_range"], intensity)

        prosody_markers = self._generate_prosody_markers(pitch_mult, rate_mult, volume_offset)

        logger.info(f"Mapped {emotion} (Int: {intensity:.2f}) -> Pitch: {pitch_mult:.2f}, Rate: {rate_mult:.2f}, Vol: {volume_offset:+.1f}dB")

        return VoiceParameters(
            pitch_multiplier=round(pitch_mult, 3),
            rate_multiplier=round(rate_mult, 3),
            volume_db_offset=round(volume_offset, 1),
            prosody_markers=prosody_markers,
            recommended_voice_traits=correlates["traits"],
            ssml_markup=self.generate_ssml_wrapper(text, pitch_mult, rate_mult, volume_offset)
        )

    def _interpolate(self, base: float, range_tuple: tuple, intensity: float) -> float:

        extreme_target = range_tuple[1] if abs(range_tuple[1] - base) > abs(range_tuple[0] - base) else range_tuple[0]

        spread = extreme_target - base

        curved_intensity = intensity ** 0.5

        return base + (spread * curved_intensity)

    def _generate_prosody_markers(self, pitch: float, rate: float, volume: float) -> List[str]:
        markers = []
        if pitch > 1.1: markers.append("high-pitch")
        elif pitch < 0.9: markers.append("low-pitch")

        if rate > 1.1: markers.append("fast-tempo")
        elif rate < 0.9: markers.append("slow-tempo")

        if volume > 3: markers.append("increased-volume")
        elif volume < -3: markers.append("decreased-volume")

        return markers

    def generate_ssml_wrapper(self, text: str, pitch: float, rate: float, volume: float) -> str:

        pitch_pct = f"{int((pitch - 1.0) * 100):+d}%"
        rate_pct = f"{int(rate * 100)}%"
        vol_db = f"{volume:+.1f}dB"

        enhanced_text = text.replace(".", '. <break time="400ms"/>')
        enhanced_text = enhanced_text.replace("!", '! <break time="200ms"/>')
        enhanced_text = enhanced_text.replace("?", '? <break time="500ms"/>')
        enhanced_text = enhanced_text.replace(",", ', <break time="100ms"/>')

        if "!" in text:
            enhanced_text = f'<emphasis level="strong">{enhanced_text}</emphasis>'

        return f'<prosody pitch="{pitch_pct}" rate="{rate_pct}" volume="{vol_db}">{enhanced_text}</prosody>'
