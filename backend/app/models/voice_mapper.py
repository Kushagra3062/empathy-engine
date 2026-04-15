import math
from typing import Dict, NamedTuple, Optional
from pydantic import BaseModel
from app.schemas.synthesis import VoiceParametersApplied, VoiceParameter

class AcousticProfile(NamedTuple):
    """
    Per-emotion acoustic characteristics based on human speech studies.
    Values derived from Juslin & Scherer (2005) and Mozziconacci (1998).
    """
    emotion: str
    pitch_mean_hz: float
    pitch_variance: float
    speech_rate_wpm: int
    loudness_db: float
    pitch_direction: str  # "up", "down", "flat", "wave"
    glottal_tension: float  # 0=relaxed, 1=tense
    breathiness_level: float

# Research-based acoustic profiles
ACOUSTIC_PROFILES = {
    "HAPPY": AcousticProfile("HAPPY", 180, 0.7, 140, 3.0, "up", 0.6, 0.2),
    "ANGRY": AcousticProfile("ANGRY", 120, 0.5, 160, 6.0, "down", 0.9, 0.0),
    "SAD": AcousticProfile("SAD", 110, 0.2, 100, -4.0, "down", 0.2, 0.5),
    "CALM": AcousticProfile("CALM", 140, 0.3, 120, -1.0, "flat", 0.3, 0.3),
    "SURPRISED": AcousticProfile("SURPRISED", 200, 0.8, 140, 2.0, "up", 0.7, 0.4),
    "FRUSTRATED": AcousticProfile("FRUSTRATED", 130, 0.5, 125, 2.0, "wave", 0.7, 0.1),
    "CONCERNED": AcousticProfile("CONCERNED", 155, 0.4, 115, -0.5, "up", 0.5, 0.2),
    "NEUTRAL": AcousticProfile("NEUTRAL", 150, 0.2, 130, 0.0, "flat", 0.4, 0.2)
}

class ScientificVoiceParameterMapper:
    """
    Maps emotion + intensity to voice parameters using a Sigmoid Intensity Curve.
    """
    
    def calculate_modulation_factor(self, intensity: float, param_weight: float = 1.0) -> float:
        """
        Sigmoid curve for smooth, natural intensity scaling.
        f(x) = 1 / (1 + e^(-6*(x-0.5)))
        """
        # Clamp intensity
        intensity = max(0.0, min(1.0, intensity))
        # Sigmoid formula
        modulation = 1.0 / (1.0 + math.exp(-6 * (intensity - 0.5)))
        return modulation * param_weight

    def map_to_voice_parameters(
        self, 
        emotion: str, 
        intensity: float = 0.5,
        gender: str = "neutral"
    ) -> VoiceParametersApplied:
        
        profile = ACOUSTIC_PROFILES.get(emotion.upper(), ACOUSTIC_PROFILES["NEUTRAL"])
        
        # Calculate modulation factors
        mod_pitch = self.calculate_modulation_factor(intensity, 1.0)
        mod_rate = self.calculate_modulation_factor(intensity, 0.8)
        mod_vol = self.calculate_modulation_factor(intensity, 0.5)

        # Base calculations
        gender_offset = -60 if gender == "male" else (75 if gender == "female" else 0)
        
        # Pitch: Multiplier logic for synthesis
        # Neutral is 1.0. Happy is 1.3, Sad is 0.7, etc.
        pitch_base = (profile.pitch_mean_hz + gender_offset) / (150 + gender_offset)
        # Scale movement away from 1.0 by modulation
        final_pitch = 1.0 + (pitch_base - 1.0) * mod_pitch

        # Rate: Multiplier logic (1.0 = normal)
        rate_base = profile.speech_rate_wpm / 130
        final_rate = 1.0 + (rate_base - 1.0) * mod_rate
        
        # Volume: 0-1 linear for synthesis
        vol_base = profile.loudness_db
        # Volume modulation (log to linear approx)
        final_vol = 1.0 + (vol_base / 20) * mod_vol
        final_vol = max(0.1, min(1.0, final_vol))

        return VoiceParametersApplied(
            pitch_shift=VoiceParameter(value=final_pitch, unit="multiplier", description=f"Pitch for {emotion}"),
            speech_rate=VoiceParameter(value=final_rate, unit="multiplier", description=f"Rate for {emotion}"),
            volume_shift=VoiceParameter(value=final_vol, unit="linear", description=f"Volume for {emotion}"),
            breathiness=VoiceParameter(value=profile.breathiness_level * mod_pitch, unit="0-1", description="Vulnerability"),
            harshness=VoiceParameter(value=profile.glottal_tension * mod_pitch, unit="0-1", description="Gristle/Tension"),
            articulation_clarity=0.7 + (0.3 if emotion == "ANGRY" else (-0.2 if emotion == "SAD" else 0)) * intensity,
            pause_duration_ms=int(200 if emotion == "NEUTRAL" else (300 if emotion == "SAD" else 100))
        )
