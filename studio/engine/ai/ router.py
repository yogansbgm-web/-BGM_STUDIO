# engine/detector.py
"""
Detector Engine — Vision AI untuk menganalisis gambar.
Mendukung: MockDetector (simulasi), GeminiDetector (Google), OpenRouterVisionDetector (Qwen2.5-VL dll.)
"""

from typing import Optional, Dict, Any
from PIL import Image
import os
import json
import re

from models.detector_result import DetectorResult
from utils.logger import logger
from config.constants import GEMINI_API_KEY, OPENROUTER_API_KEY, VISION_MODEL, OPENROUTER_VISION_MODEL


# ============================================================
# BASE DETECTOR
# ============================================================
class BaseDetector:
    """Abstract base class for all detectors."""
    def detect(self, image: Image.Image) -> DetectorResult:
        raise NotImplementedError


# ============================================================
# MOCK DETECTOR (Fallback / Simulasi)
# ============================================================
class MockDetector(BaseDetector):
    """Simulasi detector — tidak butuh API key."""
    def detect(self, image: Image.Image) -> DetectorResult:
        return DetectorResult(
            channel="JAZZ",
            architecture="Speakeasy",
            material="Weathered Walnut",
            lighting="Low-key",
            motion="Smoke Drift",
            age="1920s",
            confidence=91.0,
            palette=["Amber", "Indigo", "Walnut"],
            mood=["Warm", "Intimate", "Noir"],
            raw={}
        )


# ============================================================
# SMART MOCK DETECTOR (Berdasarkan Warna)
# ============================================================
class SmartMockDetector(BaseDetector):
    """Detector berbasis warna dominan — tidak butuh API key."""
    def detect(self, image: Image.Image) -> DetectorResult:
        from PIL import ImageStat
        img = image.convert('RGB')
        stat = ImageStat.Stat(img)
        r, g, b = stat.mean

        if r > g and r > b:
            channel = "JAZZ"
        elif g > r and g > b:
            channel = "FOREST"
        elif b > r and b > g:
            channel = "BOSSA"
        else:
            channel = "BAMBU"

        mapping = {
            "JAZZ": {"arch": "Speakeasy", "mat": "Weathered Walnut", "light": "Low-key"},
            "BOSSA": {"arch": "Beach House", "mat": "Terracotta", "light": "Golden Hour"},
            "BAMBU": {"arch": "Japanese Teahouse", "mat": "Bamboo", "light": "Overcast"},
            "FOREST": {"arch": "Cabin", "mat": "Moss", "light": "Volumetric"},
            "AURELIA": {"arch": "Study Room", "mat": "Wood", "light": "Soft"},
            "ECOLIFE": {"arch": "Greenhouse", "mat": "Ceramic", "light": "Morning Sun"}
        }
        info = mapping.get(channel, mapping["JAZZ"])

        return DetectorResult(
            channel=channel,
            architecture=info["arch"],
            material=info["mat"],
            lighting=info["light"],
            motion="",
            age="",
            confidence=75.0,
            palette=["Warm", "Neutral"] if channel in ["JAZZ","BOSSA"] else ["Cool"],
            mood=["Calm"],
            raw={"method": "color_based", "rgb": (r, g, b)}
        )


# ============================================================
# GEMINI DETECTOR (Google Gemini Vision)
# ============================================================
class GeminiDetector(BaseDetector):
    """Detector menggunakan Google Gemini Vision API."""
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or GEMINI_API_KEY
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not set")
        import google.generativeai as genai
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        logger.info("✅ GeminiDetector initialized")

    def detect(self, image: Image.Image) -> DetectorResult:
        import google.generativeai as genai
        prompt = """
        Analyze this image and return ONLY a JSON object with this exact structure:
        {
            "description": "a vivid, detailed description of the image (3-5 sentences)",
            "subjects": ["main", "subjects", "in", "the", "image"],
            "colors": ["dominant", "colors"],
            "mood": ["mood", "words"],
            "materials": ["materials", "seen"],
            "lighting": "lighting description",
            "era": "era or style",
            "architecture": "architecture style"
        }
        Do not include any other text. Only the JSON.
        """
        try:
            response = self.model.generate_content([prompt, image])
            text = response.text
            text = re.sub(r'```json\s*', '', text)
            text = re.sub(r'\s*```', '', text)
            data = json.loads(text)

            channel = self._match_channel(data)

            return DetectorResult(
                channel=channel,
                architecture=data.get('architecture', ''),
                material=", ".join(data.get('materials', [])),
                lighting=data.get('lighting', ''),
                motion="",
                age=data.get('era', ''),
                confidence=92.0,
                palette=data.get('colors', []),
                mood=data.get('mood', []),
                raw=data
            )
        except Exception as e:
            logger.warning(f"Gemini vision gagal: {e}. Fallback ke Mock.")
            return MockDetector().detect(image)

    def _match_channel(self, data: dict) -> str:
        description = data.get('description', '').lower()
        subjects = [s.lower() for s in data.get('subjects', [])]
        colors = [c.lower() for c in data.get('colors', [])]
        mood = [m.lower() for m in data.get('mood', [])]

        channels = {
            "JAZZ": ["piano", "whiskey", "speakeasy", "amber", "indigo", "smoke", "rain", "noir"],
            "BOSSA": ["ocean", "palm", "coffee", "beach", "orange", "turquoise", "sand", "sun"],
            "BAMBU": ["bamboo", "mist", "dew", "teahouse", "sage", "grey", "stone"],
            "FOREST": ["river", "moss", "fog", "cabin", "emerald", "bark", "wild"],
            "AURELIA": ["writing", "vinyl", "desk", "study", "amber", "blue"],
            "ECOLIFE": ["monstera", "mug", "book", "greenhouse", "green", "terracotta"]
        }
        scores = {ch: 0 for ch in channels}
        for ch, keywords in channels.items():
            score = 0
            for kw in keywords:
                if kw in description: score += 3
                if kw in subjects: score += 5
                if kw in colors: score += 4
                if kw in mood: score += 4
            scores[ch] = score
        return max(scores, key=scores.get)


# ============================================================
# OPENROUTER VISION DETECTOR (Qwen2.5-VL, InternVL, dll.)
# ============================================================
class OpenRouterVisionDetector(BaseDetector):
    """Vision detector using OpenRouter with Qwen2.5-VL or other models."""
    def __init__(self, model: str = "qwen/qwen2.5-vl", api_key: Optional[str] = None):
        from engine.ai.openrouter_client import OpenRouterClient
        self.client = OpenRouterClient(api_key)
        self.model = model
        logger.info(f"✅ OpenRouterVisionDetector initialized with model: {model}")

    def detect(self, image: Image.Image) -> DetectorResult:
        try:
            result = self.client.vision_detect(image, self.model)

            if "error" in result:
                logger.warning(f"OpenRouter error: {result['error']}. Falling back to Mock.")
                return MockDetector().detect(image)

            channel = self._match_channel(result)

            return DetectorResult(
                channel=channel,
                architecture=result.get("architecture", ""),
                material=", ".join(result.get("materials", [])),
                lighting=result.get("lighting", ""),
                motion=result.get("motion", ""),
                age=result.get("time", ""),
                confidence=float(result.get("confidence", 80.0)),
                palette=result.get("colors", []),
                mood=result.get("mood", []),
                raw=result
            )
        except Exception as e:
            logger.error(f"OpenRouter vision failed: {e}. Falling back to Mock.")
            return MockDetector().detect(image)

    def _match_channel(self, data: dict) -> str:
        description = data.get("scene", "").lower() + " " + " ".join(data.get("mood", [])).lower()
        objects = " ".join(data.get("objects", [])).lower()
        colors = " ".join(data.get("colors", [])).lower()

        channel_scores = {
            "JAZZ": ["speakeasy", "piano", "whiskey", "jazz", "amber", "intimate", "noir"],
            "BOSSA": ["beach", "ocean", "palm", "coffee", "bossa", "sunny", "relaxed"],
            "BAMBU": ["bamboo", "zen", "teahouse", "mist", "meditative", "calm"],
            "FOREST": ["forest", "river", "moss", "cabin", "healing", "wild"],
            "AURELIA": ["study", "desk", "vinyl", "writing", "focused", "nostalgic"],
            "ECOLIFE": ["greenhouse", "plant", "sustainable", "organic", "mindful"]
        }
        scores = {ch: 0 for ch in channel_scores}
        for ch, keywords in channel_scores.items():
            for kw in keywords:
                if kw in description or kw in objects or kw in colors:
                    scores[ch] += 1
        best = max(scores, key=scores.get)
        return best if scores[best] > 0 else "JAZZ"


# ============================================================
# DETECTOR FACTORY (get_detector)
# ============================================================
_default_detector: Optional[BaseDetector] = None

def get_detector() -> BaseDetector:
    """Factory — mengembalikan detector sesuai konfigurasi environment."""
    global _default_detector
    if _default_detector is not None:
        return _default_detector

    vision_model = VISION_MODEL.lower() if VISION_MODEL else "mock"

    if vision_model == "openrouter":
        try:
            _default_detector = OpenRouterVisionDetector(
                model=OPENROUTER_VISION_MODEL or "qwen/qwen2.5-vl"
            )
            logger.info("✅ Using OpenRouterVisionDetector")
        except Exception as e:
            logger.warning(f"OpenRouter init failed: {e}. Falling back to Mock.")
            _default_detector = MockDetector()

    elif vision_model == "gemini":
        try:
            _default_detector = GeminiDetector()
            logger.info("✅ Using GeminiDetector")
        except Exception as e:
            logger.warning(f"Gemini init failed: {e}. Falling back to Mock.")
            _default_detector = MockDetector()

    elif vision_model == "smartmock":
        _default_detector = SmartMockDetector()
        logger.info("ℹ️ Using SmartMockDetector (color-based)")

    else:
        _default_detector = MockDetector()
        logger.info("ℹ️ Using MockDetector (no AI Vision)")

    return _default_detector