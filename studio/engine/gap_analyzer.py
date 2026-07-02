# engine/gap_analyzer.py
from typing import Dict, Any
from models.detector_result import DetectorResult, GapResult, GapItem

class GapAnalyzer:
    def analyze(self, detector_result: DetectorResult, dna: Dict[str, Any]) -> GapResult:
        # Simpen raw data detector (deskripsi gambar)
        raw = detector_result.raw if hasattr(detector_result, 'raw') else {}
        
        # Simpen missing items (dummy samentawis)
        missing = [
            GapItem(element="Rain Window", status="missing", priority="HIGH", reason="FX wajib JAZZ"),
            GapItem(element="Smoke Layer", status="missing", priority="HIGH", reason="Atmosfer JAZZ"),
        ]
        
        return GapResult(
            channel=detector_result.channel,
            confidence=detector_result.confidence,
            matches=[GapItem(element="Piano", status="match", priority="HIGH")],
            missing=missing,
            conflicts=[],
            extras=[],
            raw=raw  # <-- Simpen deskripsi gambar
        )