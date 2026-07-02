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

    # ---- OUTPUT LAYER ----
    final_prompt: str = ""
    revisions: List[Dict[str, Any]] = field(default_factory=list)
    research_links: List[Dict[str, Any]] = field(default_factory=list)

    def clear_analysis(self) -> None:
        """Clear all analysis results without removing the image."""
        self.detector_result = None
        self.gap_result = None
        self.creative_result = None
        self.final_prompt = ""

    def clear_all(self) -> None:
        """Hard reset of the entire project."""
        self.image_source = None
        self.detector_result = None
        self.gap_result = None
        self.creative_result = None
        self.final_prompt = ""
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