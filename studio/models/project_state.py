# models/project_state.py
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from .image_source import ImageSource

@dataclass
class ProjectState:
    # ---- INPUT LAYER ----
    image_source: Optional[ImageSource] = None
    channel: str = "JAZZ"

    # ---- ANALYSIS LAYER ----
    detector_result: Optional[Dict[str, Any]] = None
    gap_result: Optional[Dict[str, Any]] = None
    creative_result: Optional[Dict[str, Any]] = None
    
    # ---- NEW: Scene & Attributes ----
    matched_scene: Optional[Dict[str, Any]] = None
    extracted_attributes: Optional[Dict[str, Any]] = None
    suggested_attributes: Optional[Dict[str, Any]] = None
    fused_result: Optional[Dict[str, Any]] = None
    variants: Optional[List[Dict[str, Any]]] = None
    motion_plan: Optional[Dict[str, Any]] = None
    music_plan: Optional[Dict[str, Any]] = None
    learned: Optional[Dict[str, Any]] = None

    # ---- OUTPUT LAYER ----
    final_prompt: str = ""
    revisions: List[Dict[str, Any]] = field(default_factory=list)
    research_links: List[Dict[str, Any]] = field(default_factory=list)

    def clear_analysis(self) -> None:
        self.detector_result = None
        self.gap_result = None
        self.creative_result = None
        self.final_prompt = ""
        self.matched_scene = None
        self.extracted_attributes = None
        self.suggested_attributes = None
        self.fused_result = None
        self.variants = None
        self.motion_plan = None
        self.music_plan = None
        self.learned = None

    def clear_all(self) -> None:
        self.image_source = None
        self.clear_analysis()
        self.revisions = []
        self.research_links = []

    def has_image(self) -> bool:
        return self.image_source is not None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "channel": self.channel,
            "has_image": self.has_image(),
            "image_info": self.image_source.to_dict() if self.image_source else None,
            "detector": self.detector_result,
            "gap": self.gap_result,
            "creative": self.creative_result,
            "final_prompt": self.final_prompt,
            "revisions_count": len(self.revisions),
            "research_count": len(self.research_links),
        }