from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from .image_source import ImageSource

@dataclass
class ProjectState:
    image_source: Optional[ImageSource] = None
    channel: str = "JAZZ"
    detector_result: Optional[Dict[str, Any]] = None
    gap_result: Optional[Dict[str, Any]] = None
    creative_result: Optional[Dict[str, Any]] = None
    final_prompt: str = ""
    revisions: List[Dict[str, Any]] = field(default_factory=list)
    research_links: List[Dict[str, Any]] = field(default_factory=list)

    def clear_analysis(self) -> None:
        self.detector_result = None
        self.gap_result = None
        self.creative_result = None
        self.final_prompt = ""

    def clear_all(self) -> None:
        self.image_source = None
        self.detector_result = None
        self.gap_result = None
        self.creative_result = None
        self.final_prompt = ""
        self.revisions = []
        self.research_links = []

    def has_image(self) -> bool:
        return self.image_source is not None