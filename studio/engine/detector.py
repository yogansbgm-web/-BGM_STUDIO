# engine/detector.py
import logging
from PIL import Image
from models.detector_result import DetectorResult
from config.constants import GEMINI_API_KEY
from utils.logger import logger

class BaseDetector:
    def detect(self, image: Image.Image) -> DetectorResult:
        raise NotImplementedError

# ------------------------------------------------------------
# 1. FALLBACK: Color-based Smart Detector (tanpa API Key)
# ------------------------------------------------------------
class SmartMockDetector(BaseDetector):
    def detect(self, image: Image.Image) -> DetectorResult:
        from PIL import ImageStat
        img = image.convert('RGB')
        stat = ImageStat.Stat(img)
        r, g, b = stat.mean

        # channel based on dominant color
        if r > g and r > b:
            channel = "JAZZ"
        elif g > r and g > b:
            channel = "FOREST"
        elif b > r and b > g:
            channel = "BOSSA"
        else:
            channel = "BAMBU"

        mapping_arch = {
            "JAZZ": "Speakeasy", "BOSSA": "Beach House",
            "BAMBU": "Japanese Teahouse", "FOREST": "Cabin",
            "AURELIA": "Study Room", "ECOLIFE": "Greenhouse"
        }
        mapping_mat = {
            "JAZZ": "Weathered Walnut", "BOSSA": "Terracotta",
            "BAMBU": "Bamboo", "FOREST": "Moss",
            "AURELIA": "Wood", "ECOLIFE": "Ceramic"
        }
        mapping_light = {
            "JAZZ": "Low-key", "BOSSA": "Golden Hour",
            "BAMBU": "Overcast", "FOREST": "Volumetric",
            "AURELIA": "Soft", "ECOLIFE": "Morning Sun"
        }

        return DetectorResult(
            channel=channel,
            architecture=mapping_arch.get(channel, "Room"),
            material=mapping_mat.get(channel, "Wood"),
            lighting=mapping_light.get(channel, "Natural"),
            motion="",
            age="",
            confidence=75.0,
            palette=["Warm", "Neutral"] if channel in ["JAZZ","BOSSA"] else ["Cool"],
            mood=["Calm"],
            raw={"method": "color_based", "rgb": (r, g, b)}
        )

# Alias untuk kompatibilitas dengan import yang ada
MockDetector = SmartMockDetector

# ------------------------------------------------------------
# 2. REAL DETECTOR: Gemini Vision (butuh API Key)
# ------------------------------------------------------------
class VisionDetector(BaseDetector):
    def detect(self, image: Image.Image) -> DetectorResult:
        import google.generativeai as genai
        import json
        import re
        
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
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
            response = model.generate_content([prompt, image])
            text = response.text
            text = re.sub(r'```json\s*', '', text)
            text = re.sub(r'\s*```', '', text)
            data = json.loads(text)
            
            channel = self.match_channel(data)
            
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
            logger.warning(f"Gemini vision gagal: {e}. Fallback ke SmartMock.")
            return SmartMockDetector().detect(image)
    
    def match_channel(self, data: dict) -> str:
        description = data.get('description', '').lower()
        subjects = [s.lower() for s in data.get('subjects', [])]
        colors = [c.lower() for c in data.get('colors', [])]
        mood = [m.lower() for m in data.get('mood', [])]
        
        channels = {
            "JAZZ": ["piano", "whiskey", "cat", "speakeasy", "amber", "indigo", "smoke", "rain", "noir"],
            "BOSSA": ["ocean", "palm", "coffee", "beach", "orange", "turquoise", "sand", "sun"],
            "BAMBU": ["bamboo", "mist", "dew", "teahouse", "sage", "grey", "stone"],
            "FOREST": ["river", "moss", "fog", "cabin", "emerald", "bark", "wild"],
            "AURELIA": ["writing", "vinyl", "desk", "study", "amber", "blue"],
            "ECOLIFE": ["monstera", "mug", "book", "greenhouse", "green", "terracotta"]
        }
        
        scores = {ch: 0 for ch in channels}
        for channel, keywords in channels.items():
            score = 0
            for kw in keywords:
                if kw in description:
                    score += 3
                if kw in subjects:
                    score += 5
                if kw in colors:
                    score += 4
                if kw in mood:
                    score += 4
            scores[channel] = score
        return max(scores, key=scores.get)

# ------------------------------------------------------------
# 3. FACTORY
# ------------------------------------------------------------
_default_detector = None

def get_detector() -> BaseDetector:
    global _default_detector
    if _default_detector is None:
        if GEMINI_API_KEY:
            try:
                _default_detector = VisionDetector()
                logger.info("✅ VisionDetector (Gemini) aktif!")
            except Exception as e:
                logger.warning(f"VisionDetector gagal: {e}. Make SmartMock.")
                _default_detector = SmartMockDetector()
        else:
            _default_detector = SmartMockDetector()
            logger.info("ℹ️ SmartMockDetector (tanpa API Key) — berbasis warna.")
    return _default_detector