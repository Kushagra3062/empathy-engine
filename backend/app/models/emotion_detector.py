import time
import torch
import re
import numpy as np
from typing import Dict, Any, List, Optional
from transformers import pipeline
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from loguru import logger
from app.config import settings

class LinguisticFeatureAnalyzer:
    """Analyzes punctuation, casing, and negations."""
    def analyze(self, text: str) -> Dict[str, Any]:
        text_lower = text.lower()
        return {
            "all_caps": text.isupper() and len(text) > 3,
            "exclamation_count": text.count('!'),
            "has_ellipsis": "..." in text,
            "repeated_chars": bool(re.search(r'(.)\1{2,}', text)),
            "negations": ["not", "never", "no", "don't", "can't", "won't", "isn't", "wasn't"],
            "has_negation": any(neg in text_lower.split() for neg in ["not", "never", "no", "don't", "can't", "won't", "isn't", "wasn't"])
        }

class EmotionDetector:
    """Enterprise Ensemble Emotion Detector (VADER + DistilBERT + RoBERTa)"""
    
    def __init__(self):
        self.device = 0 if torch.cuda.is_available() and settings.DEVICE == "cuda" else -1
        self.analyzer = SentimentIntensityAnalyzer()
        self.feature_analyzer = LinguisticFeatureAnalyzer()
        
        # Models initialized lazily to save startup time
        self._distilbert = None
        self._roberta = None

    @property
    def distilbert(self):
        if self._distilbert is None:
            self._distilbert = pipeline("sentiment-analysis", model=settings.DISTILBERT_MODEL, device=self.device)
        return self._distilbert

    @property
    def roberta(self):
        if self._roberta is None:
            self._roberta = pipeline("text-classification", model=settings.ROBERTA_MODEL, top_k=None, device=self.device)
        return self._roberta

    def detect_emotion(self, text: str) -> Dict[str, Any]:
        start_time = time.time()
        
        # 1. Lexical Layer (VADER) - 20% weight
        vs = self.analyzer.polarity_scores(text)
        vader_vec = self._vader_to_vector(vs)
        
        # 2. Semantic Layer (DistilBERT) - 40% weight
        db_res = self.distilbert(text)[0]
        db_vec = self._db_to_vector(db_res)
        
        # 3. Nuance Layer (RoBERTa) - 40% weight
        rob_res = self.roberta(text)[0]
        rob_vec = self._roberta_to_vector(rob_res)
        
        # 4. Weighted Ensemble
        ensemble = {}
        for emotion in ["HAPPY", "ANGRY", "FRUSTRATED", "CALM", "SAD", "SURPRISED", "CONCERNED", "NEUTRAL"]:
            ensemble[emotion] = (vader_vec.get(emotion, 0) * 0.2 + 
                               db_vec.get(emotion, 0) * 0.4 + 
                               rob_vec.get(emotion, 0) * 0.4)
        
        # 5. Linguistic Boosting & Negation
        cues = self.feature_analyzer.analyze(text)
        ensemble = self._apply_boosting(text, ensemble, cues)
        
        # Final selection
        primary_emotion = max(ensemble, key=ensemble.get)
        confidence = ensemble[primary_emotion]
        
        # Intensity scaling (Sigmoid logic)
        intensity = self._calculate_intensity(confidence, cues)
        
        return {
            "primary_emotion": primary_emotion,
            "confidence": confidence,
            "intensity": intensity,
            "all_emotions": ensemble,
            "processing_time_ms": (time.time() - start_time) * 1000
        }

    def _vader_to_vector(self, vs):
        vec = {e: 0.0 for e in ["HAPPY", "ANGRY", "FRUSTRATED", "CALM", "SAD", "SURPRISED", "CONCERNED", "NEUTRAL"]}
        if vs['compound'] >= 0.05: vec["HAPPY"] = vs['pos']
        elif vs['compound'] <= -0.05: vec["ANGRY"] = vs['neg']
        else: vec["NEUTRAL"] = 1.0
        return vec

    def _db_to_vector(self, res):
        vec = {e: 0.0 for e in ["HAPPY", "ANGRY", "FRUSTRATED", "CALM", "SAD", "SURPRISED", "CONCERNED", "NEUTRAL"]}
        if res['label'] == 'POSITIVE': vec["HAPPY"] = res['score']
        else: vec["SAD"] = res['score']
        return vec

    def _roberta_to_vector(self, results):
        vec = {e: 0.0 for e in ["HAPPY", "ANGRY", "FRUSTRATED", "CALM", "SAD", "SURPRISED", "CONCERNED", "NEUTRAL"]}
        mapping = {'joy':'HAPPY', 'anger':'ANGRY', 'sadness':'SAD', 'surprise':'SURPRISED', 'neutral':'NEUTRAL'}
        for r in results:
            label = r['label'].lower()
            if label in mapping: vec[mapping[label]] += r['score']
        return vec

    def _apply_boosting(self, text, scores, cues):
        text_lower = text.lower()
        # Boost based on keywords
        if "furious" in text_lower or "rage" in text_lower: scores["ANGRY"] += 0.5
        if "not" in text_lower and "happy" in text_lower: 
            scores["HAPPY"] *= 0.2
            scores["SAD"] += 0.4
        
        # Normalize
        total = sum(scores.values())
        return {k: v/total for k, v in scores.items()}

    def _calculate_intensity(self, confidence, cues):
        intensity = confidence * 0.5
        if cues["all_caps"]: intensity += 0.3
        intensity += min(cues["exclamation_count"] * 0.1, 0.3)
        return min(intensity, 1.0)
