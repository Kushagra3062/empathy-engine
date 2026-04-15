import sys
import os

# Add the backend path to sys.path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.models.emotion_detector import EmotionDetector
import json

def run_benchmarks():
    detector = EmotionDetector()
    
    test_cases = [
        "I LOVE THIS!!! 😍",
        "This is terrible...",
        "Really?",
        "", # Empty
        "I am extremely frustrated with the service I received today!!",
        "The weather is quite neutral today.",
        "WOW! I didn't see that coming, amazing!",
        "I'm a bit worried about the upcoming deadline..."
    ]
    
    print("\n🚀 --- EMPATHY ENGINE EMOTION DETECTION BENCHMARKS ---\n")
    
    for i, test in enumerate(test_cases):
        print(f"CASE {i+1}: '{test}'")
        result = detector.detect_emotion(test)
        print(f"  Primary Emotion: {result.primary_emotion}")
        print(f"  Confidence: {result.confidence}")
        print(f"  Intensity: {result.intensity} ({result.intensity_level})")
        print(f"  Processing Time: {result.processing_time_ms}ms")
        print(f"  Linguistic Cues: {result.linguistic_cues}")
        print("-" * 50)

if __name__ == "__main__":
    run_benchmarks()
