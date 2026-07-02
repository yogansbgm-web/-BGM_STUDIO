from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

@dataclass
class DetectorResult:
    channel: str
    architecture: str
    material: str
    lighting: str
    motion: str
    age: str
    confidence: float
    palette: List[str] = field(default_factory=list)
    mood: List[str] = field(default_factory=list)
    raw: Optional[Dict[str, Any]] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "channel": self.channel,
            "architecture": self.architecture,
            "material": self.material,
            "lighting": self.lighting,
            "motion": self.motion,
            "age": self.age,
            "confidence": self.confidence,
            "palette": self.palette,
            "mood": self.mood,
        }

@dataclass
class GapItem:
    element: str
    status: str
    priority: str
    reason: str = ""
    target: Optional[str] = None

@dataclass
class GapResult:
    channel: str
    confidence: float
    matches: List[GapItem] = field(default_factory=list)
    missing: List[GapItem] = field(default_factory=list)
    conflicts: List[GapItem] = field(default_factory=list)
    extras: List[GapItem] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "channel": self.channel,
            "confidence": self.confidence,
            "match": [{"element": m.element, "status": m.status} for m in self.matches],
            "missing": [{"element": m.element, "priority": m.priority, "reason": m.reason} for m in self.missing],
            "conflict": [{"element": c.element, "action": "REPLACE", "target": c.target} for c in self.conflicts],
            "extra": [{"element": e.element, "reason": e.reason} for e in self.extras],
        }

@dataclass
class CreativePlan:
    channel: str
    current_score: float
    predicted_score: float
    recommendations: List[str] = field(default_factory=list)
    final_prompt: str = ""
    delta: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "channel": self.channel,
            "current_score": self.current_score,
            "predicted_score": self.predicted_score,
            "recommendations": self.recommendations,
            "final_prompt": self.final_prompt,
        }