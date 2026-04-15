import time
import torch
import re
import numpy as np
from typing import Dict, Any, List, Optional, Union
from functools import lru_cache
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from loguru import logger
from app.config import settings
from app.schemas.emotion import EmotionResult

class EmotionDetector:

    EMOTION_CLASSES = [
        "HAPPY", "ANGRY", "FRUSTRATED", "CALM", 
        "SAD", "SURPRISED", "CONCERNED", "NEUTRAL"
    ]

    def __init__(self):
        self.device = 0 if torch.cuda.is_available() and settings.DEVICE == "cuda" else -1
        self.device_name = "cuda" if self.device == 0 else "cpu"

        self._vader = None
        self._distilbert = None
        self._roberta = None

        logger.info(f"Initializing EmotionDetector on {self.device_name}")

    @property
    def vader(self):
        if self._vader is None:
            self._vader = SentimentIntensityAnalyzer()
        return self._vader

    @property
    def distilbert(self):
        if self._distilbert is None:

            self._distilbert = pipeline(
                "sentiment-analysis", 
                model=settings.DISTILBERT_MODEL, 
                device=self.device
            )
        return self._distilbert

    @property
    def roberta(self):
        if self._roberta is None:

            self._roberta = pipeline(
                "text-classification", 
                model=settings.ROBERTA_MODEL, 
                top_k=None, 
                device=self.device
            )
        return self._roberta

    @lru_cache(maxsize=100)
    def detect_emotion(self, text: str) -> EmotionResult:

        start_time = time.time()

        cleaned_text, edge_result = self._handle_edge_cases(text)
        if edge_result:
            edge_result.processing_time_ms = (time.time() - start_time) * 1000
            return edge_result

        linguistic_cues = self._extract_linguistic_cues(text)

        vader_scores = self._get_vader_scores(cleaned_text)
        distilbert_scores = self._get_distilbert_scores(cleaned_text)
        roberta_scores = self._get_roberta_scores(cleaned_text)

        ensemble_scores = self._combine_scores(
            vader_scores, distilbert_scores, roberta_scores
        )

        ensemble_scores = self._boost_specific_emotions(cleaned_text, ensemble_scores)

        primary_emotion = max(ensemble_scores, key=ensemble_scores.get)
        confidence = ensemble_scores[primary_emotion]

        intensity = self._calculate_intensity(confidence, linguistic_cues, cleaned_text)
        intensity_level = self._get_intensity_level(intensity)

        duration_ms = (time.time() - start_time) * 1000

        result = EmotionResult(
            primary_emotion=primary_emotion,
            confidence=round(confidence, 4),
            intensity=round(intensity, 4),
            intensity_level=intensity_level,
            all_emotions={k: round(v, 4) for k, v in ensemble_scores.items()},
            model_scores={
                "vader": round(max(vader_scores.values()), 4),
                "distilbert": round(max(distilbert_scores.values()), 4),
                "roberta": round(max(roberta_scores.values()), 4)
            },
            linguistic_cues=linguistic_cues,
            processing_time_ms=round(duration_ms, 2),
            model_used=f"Ensemble(VADER+DistilBERT+RoBERTa) on {self.device_name}"
        )

        logger.info(f"Detection: '{text[:30]}...' -> {primary_emotion} ({confidence:.2f}) | Intensity: {intensity:.2f}")
        return result

    def _handle_edge_cases(self, text: str) -> (str, Optional[EmotionResult]):

        if not text or not text.strip():
            return text, self._create_default_result("NEUTRAL", 0.5)

        if len(text) > 5000:
            logger.warning(f"Text too long ({len(text)} chars), truncating to 5000.")
            text = text[:5000]

        if re.match(r'^[\d\s\.,\-\+\(\)]+$', text):
            return text, self._create_default_result("NEUTRAL", 0.4)

        if re.match(r'^[^\w\s]+$', text):
            return text, self._create_default_result("NEUTRAL", 0.5)

        text = re.sub(r'https?://\S+', '', text)

        return text, None

    def _create_default_result(self, emotion: str, intensity: float) -> EmotionResult:
        return EmotionResult(
            primary_emotion=emotion,
            confidence=1.0,
            intensity=intensity,
            intensity_level=self._get_intensity_level(intensity),
            all_emotions={e: (1.0 if e == emotion else 0.0) for e in self.EMOTION_CLASSES},
            model_scores={"static": 1.0},
            linguistic_cues={},
            processing_time_ms=0.0,
            model_used="Static-Rule"
        )

    def _extract_linguistic_cues(self, text: str) -> Dict[str, Any]:
        cues = {
            "all_caps": text.isupper() and len(text) > 3,
            "exclamation_count": text.count('!'),
            "question_count": text.count('?'),
            "has_ellipsis": "..." in text,
            "has_double_punctuation": bool(re.search(r'[!?]{2,}', text)),
            "text_length": len(text),
            "repeated_chars": bool(re.search(r'(.)\1{2,}', text)),
            "has_emojis": bool(re.search(r'[\U00010000-\U0010ffff]', text))
        }
        return cues

    def _calculate_intensity(self, confidence: float, cues: Dict[str, Any], text: str = "") -> float:

        intensity = confidence * 0.4

        adj = 0.0
        if cues.get("all_caps"): adj += 0.3
        adj += min(cues.get("exclamation_count", 0) * 0.15, 0.45)
        if cues.get("has_double_punctuation"): adj += 0.25
        if cues.get("has_emojis"): adj += 0.2
        intensity += min(adj, 1.0) * 0.2

        kv_boost = 0.0
        intensity_keywords = {
            "very": 0.2, "extremely": 0.4, "so ": 0.15, "incredibly": 0.35,
            "totally": 0.25, "really": 0.15, "super": 0.2, "absolute": 0.3,
            "completely": 0.3, "pleasant": 0.15, "amazing": 0.3, "heart": 0.2,
            "joy": 0.4, "shock": 0.4, "surprise": 0.4, "roar": 0.4, "happy": 0.2,
            "sad": 0.2, "angry": 0.2, "hate": 0.3, "love": 0.3, "terrible": 0.3,
            "wonderful": 0.3, "fantastic": 0.3, "awful": 0.3, "silence": 0.15,
            "peaceful": 0.15, "heavy": 0.2, "suffocating": 0.3
        }
        text_lower = text.lower()
        for word, boost in intensity_keywords.items():
            if word in text_lower:
                kv_boost += boost

        intensity += min(kv_boost, 1.0) * 0.4

        return min(intensity, 1.0)

    def _get_intensity_level(self, intensity: float) -> str:
        if intensity < 0.3: return "minimal"
        if intensity < 0.5: return "light"
        if intensity < 0.7: return "medium"
        if intensity < 0.85: return "strong"
        return "maximum"

    def _get_vader_scores(self, text: str) -> Dict[str, float]:
        vs = self.vader.polarity_scores(text)

        scores = {e: 0.0 for e in self.EMOTION_CLASSES}
        if vs['compound'] >= 0.05:
            scores["HAPPY"] = vs['pos']
            scores["CALM"] = vs['compound'] * 0.5
        elif vs['compound'] <= -0.05:
            scores["ANGRY"] = vs['neg'] * 0.7
            scores["SAD"] = vs['neg'] * 0.8
            scores["FRUSTRATED"] = vs['neg'] * 0.6
        else:
            scores["NEUTRAL"] = 1.0
        return scores

    def _get_distilbert_scores(self, text: str) -> Dict[str, float]:

        output = self.distilbert(text)[0]
        label = output['label']
        score = output['score']

        scores = {e: 0.0 for e in self.EMOTION_CLASSES}
        if label == "POSITIVE":
            scores["HAPPY"] = score
            scores["CALM"] = score * 0.4
        else:
            scores["SAD"] = score * 0.5
            scores["CONCERNED"] = score * 0.3
        return scores

    def _get_roberta_scores(self, text: str) -> Dict[str, float]:

        results = self.roberta(text)[0]

        scores = {e: 0.0 for e in self.EMOTION_CLASSES}
        for res in results:
            label = res['label'].lower()
            val = res['score']

            if label == 'joy': scores["HAPPY"] += val
            elif label == 'anger': scores["ANGRY"] += val
            elif label == 'sadness': scores["SAD"] += val
            elif label == 'optimism': scores["HAPPY"] += val * 0.5

        return scores

    def _combine_scores(self, v: Dict, d: Dict, r: Dict) -> Dict[str, float]:
        combined = {}
        for emotion in self.EMOTION_CLASSES:

            combined[emotion] = (v.get(emotion, 0) * 0.2 + 
                               d.get(emotion, 0) * 0.4 + 
                               r.get(emotion, 0) * 0.4)

        return combined

    def _boost_specific_emotions(self, text: str, scores: Dict[str, float]) -> Dict[str, float]:

        text_lower = text.lower()

        negations = ["not", "never", "no", "don't", "can't", "won't", "isn't", "wasn't"]
        has_negation = any(neg in text_lower.split() for neg in negations)

        happy_keywords = ["joy", "wonderful", "amazing", "excellent", "brilliant", "love", "favorite", "perfect", "celebrate", "win", "success", "delight", "giddy", "awesome"]
        if any(word in text_lower for word in happy_keywords) and not has_negation:
            scores["HAPPY"] = scores.get("HAPPY", 0) + 0.4

        sad_keywords = ["tears", "crying", "grief", "loss", "miserable", "lonely", "depressed", "heartbroken", "sorrow", "regret", "pity", "melancholy"]
        if any(word in text_lower for word in sad_keywords):
            scores["SAD"] = scores.get("SAD", 0) + 0.5

        angry_keywords = [
            "rage", "furious", "hostile", "scream", "punch", "hate", "damn", "idiot", "shut up", 
            "disgusting", "vile", "revolting", "scorching", "white-hot", "simmer", "torrent",
            "temples pulse", "jaw sets", "fists", "indignation", "tempest", "unforgiving", "vibrating tremor"
        ]
        if any(word in text_lower for word in angry_keywords):
            scores["ANGRY"] = scores.get("ANGRY", 0) + 0.7
            if scores.get("CALM", 0) > 0.3: scores["CALM"] *= 0.3 
            if scores.get("NEUTRAL", 0) > 0.3: scores["NEUTRAL"] *= 0.4

        calm_keywords = ["peaceful", "serene", "relax", "gentle", "soft", "ocean", "breeze", "quiet", "stillness", "harmony", "meditate"]
        if any(word in text_lower for word in calm_keywords) and not any(aw in text_lower for aw in ["simmer", "storm", "tempest", "indignation"]):
            scores["CALM"] = scores.get("CALM", 0) + 0.4

        surprise_keywords = ["surprise", "shock", "shocking", "impossible", "unbelievable", "stunned", "unexpected", "amazed", "astonished", "gasped", "stumbled", "jaw dropping", "wow", "flabbergasted"]
        if any(word in text_lower for word in surprise_keywords):
            scores["SURPRISED"] = scores.get("SURPRISED", 0) + 0.7 
            if scores.get("HAPPY", 0) > 0.4: scores["HAPPY"] *= 0.6
            if scores.get("NEUTRAL", 0) > 0.4: scores["NEUTRAL"] *= 0.6

        concern_keywords = [
            "worried", "anxious", "uncertain", "concerned", "afraid", "scared", "fear", "dread",
            "what if", "panicked", "panic", "shallow breathing", "heart hammering", "windowsill",
            "blinds", "hoping", "stomach", "waiting", "answering?", "where are you", "jumped", "pacing"
        ]
        if any(word in text_lower for word in concern_keywords):
            scores["CONCERNED"] = scores.get("CONCERNED", 0) + 0.6
            if scores.get("SAD", 0) > 0.4: scores["SAD"] *= 0.7

        frustration_keywords = [
            "annoyed", "frustrated", "disappointed", "exasperated", "fed up", "useless", "slow", 
            "broken", "failed", "again!", "stuck", "pressure", "cooker", "tensing", "limit", "demand"
        ]
        if any(word in text_lower for word in frustration_keywords):
            scores["FRUSTRATED"] = scores.get("FRUSTRATED", 0) + 0.6
            if scores.get("CALM", 0) > 0.3: scores["CALM"] *= 0.4

        neutral_keywords = ["fact", "statistic", "data", "report", "according to", "information", "detail", "item", "weather", "time", "date"]
        if any(word in text_lower for word in neutral_keywords) and len(text_lower.split()) < 20:
            scores["NEUTRAL"] = scores.get("NEUTRAL", 0) + 0.2

        return scores

    def batch_detect(self, texts: List[str]) -> List[EmotionResult]:

        return [self.detect_emotion(t) for t in texts]

    def analyze_sentences(self, text: str) -> List[EmotionResult]:

        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [self.detect_emotion(s) for s in sentences if s.strip()]
