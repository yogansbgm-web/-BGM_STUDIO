# engine/vision/extractor.py
from typing import Dict, List, Any, Optional
from models.detector_result import DetectorResult
from utils.logger import logger
import yaml
from pathlib import Path
from config.constants import DATA_DIR

class AttributeExtractor:
    """Extract structured attributes from DetectorResult (Gemini/Mock)"""
    
    def __init__(self):
        self.attribute_library = self._load_library()
    
    def _load_library(self) -> Dict:
        path = DATA_DIR / "knowledge" / "attribute_library.yaml"
        try:
            with open(path, "r") as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.warning(f"Attribute library load failed: {e}")
            return {}
    
    def extract(self, detector_result: DetectorResult) -> Dict[str, Any]:
        """
        Convert flat detector result into structured attributes.
        """
        raw = detector_result.raw if hasattr(detector_result, 'raw') else {}
        
        # 1. Base attributes from detector
        base = {
            "architecture": detector_result.architecture,
            "material": detector_result.material,
            "lighting": detector_result.lighting,
            "motion": detector_result.motion,
            "age": detector_result.age,
            "palette": detector_result.palette,
            "mood": detector_result.mood,
        }
        
        # 2. Extract detailed objects from raw description
        objects = self._extract_objects(raw.get('description', ''))
        scenes = self._extract_scenes(raw.get('description', ''))
        fx = self._extract_fx(raw.get('description', ''))
        emotions = self._extract_emotions(raw.get('description', ''))
        
        # 3. Build structured result
        return {
            "base": base,
            "objects": objects,
            "scenes": scenes,
            "fx": fx,
            "emotions": emotions,
            "raw_description": raw.get('description', ''),
            "suggestion": raw.get('suggestion', ''),
            "confidence": detector_result.confidence,
        }
    
    def _extract_objects(self, text: str) -> List[str]:
        """Extract potential objects from description."""
        objects = []
        common_objects = ["piano", "whiskey", "glass", "bamboo", "desk", "book", 
                         "laptop", "coffee", "palm", "ocean", "chair", "table", "lamp"]
        for obj in common_objects:
            if obj in text.lower():
                objects.append(obj.title())
        return objects
    
    def _extract_scenes(self, text: str) -> List[str]:
        """Extract scene types from description."""
        scenes = []
        scene_keywords = {
            "speakeasy": "Speakeasy",
            "jazz": "Jazz",
            "forest": "Forest",
            "bamboo": "Bamboo",
            "study": "Study",
            "cafe": "Cafe",
            "beach": "Beach"
        }
        for key, val in scene_keywords.items():
            if key in text.lower():
                scenes.append(val)
        return scenes
    
    def _extract_fx(self, text: str) -> List[str]:
        """Extract visual effects from description."""
        fx = []
        fx_keywords = ["rain", "smoke", "fog", "mist", "dew", "steam", "dust", "sun flare", "breeze"]
        for f in fx_keywords:
            if f in text.lower():
                fx.append(f.title())
        return fx
    
    def _extract_emotions(self, text: str) -> List[str]:
        """Extract emotional markers from description."""
        emotions = []
        mood_words = ["warm", "intimate", "cozy", "calm", "zen", "focused", 
                      "nostalgic", "relaxed", "luxury", "moody"]
        for m in mood_words:
            if m in text.lower():
                emotions.append(m.title())
        return emotions