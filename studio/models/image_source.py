from dataclasses import dataclass, field
from datetime import datetime
from PIL import Image
import hashlib
import io
from typing import Dict, Any

@dataclass
class ImageSource:
    image: Image.Image
    source: str
    filename: str = "untitled.png"
    width: int = 0
    height: int = 0
    mode: str = ""
    format: str = ""
    mime: str = "image/png"
    source_id: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    hash: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if self.image:
            self.width, self.height = self.image.size
            self.mode = self.image.mode
            self.format = self.image.format or "PNG"
            try:
                buffer = io.BytesIO()
                self.image.convert("RGB").save(buffer, format="JPEG", quality=85)
                self.hash = hashlib.sha256(buffer.getvalue()).hexdigest()[:16]
            except Exception:
                self.hash = "unknown"
        if not self.source_id:
            self.source_id = f"{self.source}_{self.hash[:8]}"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "filename": self.filename,
            "width": self.width,
            "height": self.height,
            "mode": self.mode,
            "format": self.format,
            "mime": self.mime,
            "source": self.source,
            "source_id": self.source_id,
            "hash": self.hash,
            "timestamp": self.timestamp,
        }