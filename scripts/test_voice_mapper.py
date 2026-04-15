import sys
import os

# Add the backend path to sys.path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.models.voice_mapper import VoiceParameterMapper
from app.schemas.emotion import EmotionResult

def test_mapper():
    mapper = VoiceParameterMapper()
    
    test_emotions = [
        ("HAPPY", 0.9),
        ("SAD", 0.8),
        ("ANGRY", 0.7),
        ("CALM", 0.4),
        ("NEUTRAL", 0.0),
        ("SURPRISED", 1.0)
    ]
    
    print("\n🔊 --- VOICE PARAMETER MAPPING TESTS ---\n")
    
    for emotion, intensity in test_emotions:
        # Mock EmotionResult
        result = EmotionResult(
            primary_emotion=emotion,
            confidence=0.9,
            intensity=intensity,
            intensity_level="n/a",
            all_emotions={emotion: 0.9},
            model_scores={},
            linguistic_cues={},
            processing_time_ms=0.0,
            model_used="Mock"
        )
        
        params = mapper.map_emotion_to_voice(result)
        print(f"Emotion: {emotion} (Intensity: {intensity})")
        print(f"  Pitch Multiplier: {params.pitch_multiplier}")
        print(f"  Rate Multiplier: {params.rate_multiplier}")
        print(f"  Volume Offset: {params.volume_db_offset}dB")
        print(f"  SSML Example: {params.ssml_markup}")
        print(f"  Traits: {params.recommended_voice_traits}")
        print("-" * 50)

if __name__ == "__main__":
    test_mapper()
