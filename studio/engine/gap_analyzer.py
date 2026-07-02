# engine/gap_analyzer.py
from typing import Dict, Any
from models.detector_result import DetectorResult, GapResult, GapItem

class GapAnalyzer:
    def analyze(self, detector_result: DetectorResult, dna: Dict[str, Any]) -> GapResult:
        return GapResult(
            channel=detector_result.channel,
            confidence=detector_result.confidence,
            matches=[
                GapItem(element="Piano", status="match", priority="HIGH"),
                GapItem(element="Whiskey Glass", status="match", priority="HIGH"),
                GapItem(element="Warm Light", status="match", priority="HIGH"),
            ],
            missing=[
                GapItem(element="Rain Window", status="missing", priority="HIGH", reason="FX wajib JAZZ"),
                GapItem(element="Smoke Layer", status="missing", priority="HIGH", reason="Atmosfer JAZZ"),
                GapItem(element="Weathered Texture", status="missing", priority="MEDIUM", reason="Material kedah kolot"),
            ],
            conflicts=[
                GapItem(element="Fresh Wood", status="conflict", priority="HIGH", target="Weathered Walnut"),
                GapItem(element="Bright Sun", status="conflict", priority="HIGH", target="Low-key Amber"),
            ],
            extras=[
                GapItem(element="Modern Chair", status="extra", priority="LOW", reason="Ngaganggu era 1920s"),
            ]
        )