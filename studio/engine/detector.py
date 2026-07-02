# engine/detector.py
from PIL import Image
from models.detector_result import DetectorResult

class BaseDetector:
    def detect(self, image: Image.Image) -> DetectorResult:
        raise NotImplementedError

class MockDetector(BaseDetector):
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

_default_detector = None

def get_detector() -> BaseDetector:
    global _default_detector
    if _default_detector is None:
        _default_detector = MockDetector()
    return _default_detector