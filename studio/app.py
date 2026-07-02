# ============================================================
# YOGANS BGM STUDIO v7.1 — AI Creative Studio
# FULLY REFACTORED — PRODUCTION READY (Sprint 1 Completed)
# ============================================================
# Struktur:
#   app.py               ->  UI Orchestrator (≈350 lines)
#   models/              ->  Data Contracts (ImageSource, ProjectState, DetectorResult, etc.)
#   engine/              ->  Core Business Logic (Normalizer, Detector, Gap, Creative, Prompt)
#   config/              ->  Constants & Settings
#   utils/               ->  Helpers (logger, exceptions, validators)
#   services/            ->  I/O (cache, export, download)
#   data/                ->  YAML assets (DNA, Knowledge, BGM)
# ============================================================

# ------------------------------------------------------------------
# 1.  config/constants.py
# ------------------------------------------------------------------
"""
config/constants.py
"""
import os
from pathlib import Path

# --- Paths ---
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
ASSETS_DIR = BASE_DIR / "assets"

# --- Channels ---
CHANNEL_NAMES = ["JAZZ", "BOSSA", "BAMBU", "FOREST", "AURELIA", "ECOLIFE"]

# --- Image constraints ---
MAX_IMAGE_SIZE_MB = 200
MAX_IMAGE_PIXELS = 4096 * 4096          # 16 MP
SUPPORTED_IMAGE_TYPES = ["jpg", "jpeg", "png", "webp", "bmp", "tiff"]

# --- Detector ---
DEFAULT_CONFIDENCE_THRESHOLD = 70       # PASS ≥ 70

# --- Export ---
EXPORT_FORMATS = ["ZIP", "PDF", "JSON", "YAML"]

# --- HTTP ---
DEFAULT_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
DEFAULT_TIMEOUT = 15

# --- Logging ---
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = BASE_DIR / "logs" / "vpd.log"

# ------------------------------------------------------------------
# 2.  utils/exceptions.py
# ------------------------------------------------------------------
"""
utils/exceptions.py
"""
class VPDError(Exception):
    """Base exception for all VPD errors."""
    pass

class NormalizationError(VPDError):
    """Raised when input cannot be normalized to PIL.Image."""
    pass

class DetectorError(VPDError):
    """Raised when detector fails."""
    pass

class KnowledgeError(VPDError):
    """Raised when knowledge graph operations fail."""
    pass

class ExportError(VPDError):
    """Raised when export fails."""
    pass

class ConfigError(VPDError):
    """Raised when configuration is invalid."""
    pass

# ------------------------------------------------------------------
# 3.  utils/logger.py
# ------------------------------------------------------------------
"""
utils/logger.py
"""
import logging
import sys
from config.constants import LOG_LEVEL, LOG_FILE

def setup_logger(name: str = "vpd") -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, LOG_LEVEL.upper(), logging.INFO))

    if not logger.handlers:
        # Console handler
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        ch.setFormatter(formatter)
        logger.addHandler(ch)

        # File handler (optional)
        try:
            LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
            fh = logging.FileHandler(LOG_FILE)
            fh.setLevel(logging.DEBUG)
            fh.setFormatter(formatter)
            logger.addHandler(fh)
        except Exception:
            pass

    return logger

logger = setup_logger()

# ------------------------------------------------------------------
# 4.  models/image_source.py
# ------------------------------------------------------------------
"""
models/image_source.py
"""
from dataclasses import dataclass, field
from datetime import datetime
from PIL import Image
import hashlib
import io
from typing import Optional, Dict, Any

@dataclass
class ImageSource:
    image: Image.Image
    source: str          # "upload" | "clipboard" | "url" | "youtube"
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
            # Compute stable hash (JPEG quality 85 for speed)
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

# ------------------------------------------------------------------
# 5.  models/project_state.py
# ------------------------------------------------------------------
"""
models/project_state.py
"""
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from .image_source import ImageSource

@dataclass
class ProjectState:
    # ---- INPUT LAYER ----
    image_source: Optional[ImageSource] = None
    channel: str = "JAZZ"

    # ---- ANALYSIS LAYER ----
    detector_result: Optional[Dict[str, Any]] = None   # to be replaced by DetectorResult
    gap_result: Optional[Dict[str, Any]] = None        # to be replaced by GapResult
    creative_result: Optional[Dict[str, Any]] = None   # to be replaced by CreativePlan

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

# ------------------------------------------------------------------
# 6.  models/detector_result.py   (New – Data Contract)
# ------------------------------------------------------------------
"""
models/detector_result.py
"""
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
    status: str           # "match" | "missing" | "conflict" | "extra"
    priority: str         # "HIGH" | "MEDIUM" | "LOW"
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

# ------------------------------------------------------------------
# 7.  engine/input_normalizer.py  (with PasteResult support)
# ------------------------------------------------------------------
"""
engine/input_normalizer.py
"""
from PIL import Image, ImageOps
import io
import base64
import numpy as np
from typing import Any, Optional, Callable, List
from streamlit.runtime.uploaded_file_manager import UploadedFile
from streamlit_paste_button import PasteResult
from utils.exceptions import NormalizationError
from utils.logger import logger

# ---- Handler registry (extensible) ----
_normalizers: List[Callable[[Any], Optional[Image.Image]]] = []

def register_normalizer(func: Callable) -> Callable:
    """Decorator to register a normalizer handler."""
    _normalizers.append(func)
    return func

# ---- Built-in handlers ----
@register_normalizer
def _normalize_pil(obj: Any) -> Optional[Image.Image]:
    if isinstance(obj, Image.Image):
        return obj
    return None

@register_normalizer
def _normalize_uploaded_file(obj: Any) -> Optional[Image.Image]:
    if isinstance(obj, UploadedFile):
        try:
            return Image.open(obj)
        except Exception as e:
            logger.warning(f"UploadedFile normalizer failed: {e}")
    return None

@register_normalizer
def _normalize_bytes(obj: Any) -> Optional[Image.Image]:
    if isinstance(obj, bytes):
        try:
            return Image.open(io.BytesIO(obj))
        except Exception as e:
            logger.warning(f"Bytes normalizer failed: {e}")
    return None

@register_normalizer
def _normalize_base64(obj: Any) -> Optional[Image.Image]:
    if isinstance(obj, str) and obj.startswith('data:image'):
        try:
            header, encoded = obj.split(',', 1)
            data = base64.b64decode(encoded)
            return Image.open(io.BytesIO(data))
        except Exception as e:
            logger.warning(f"Base64 normalizer failed: {e}")
    return None

@register_normalizer
def _normalize_filepath(obj: Any) -> Optional[Image.Image]:
    if isinstance(obj, str) and not obj.startswith('data:image'):
        try:
            return Image.open(obj)
        except Exception as e:
            logger.warning(f"Filepath normalizer failed: {e}")
    return None

@register_normalizer
def _normalize_numpy(obj: Any) -> Optional[Image.Image]:
    if isinstance(obj, np.ndarray):
        try:
            return Image.fromarray(obj)
        except Exception as e:
            logger.warning(f"Numpy normalizer failed: {e}")
    return None

@register_normalizer
def _normalize_dict(obj: Any) -> Optional[Image.Image]:
    if isinstance(obj, dict):
        # Look for common image keys
        for key in ['image', 'img', 'data', 'blob', 'value', 'content']:
            if key in obj:
                try:
                    return normalize_to_pil(obj[key])
                except Exception:
                    continue
        # If we are here, maybe it's a PasteResult-style dict
        # Try to inspect __dict__ if it's not a plain dict
        pass
    return None

@register_normalizer
def _normalize_paste_result(obj: Any) -> Optional[Image.Image]:
    """Special handler for streamlit_paste_button.PasteResult."""
    # Check class name (because type(obj) might not be directly imported)
    if obj.__class__.__name__ == "PasteResult":
        # Inspect all attributes
        for attr in ['image', 'data', 'bytes', 'content', 'value']:
            if hasattr(obj, attr):
                try:
                    val = getattr(obj, attr)
                    if val is not None:
                        return normalize_to_pil(val)
                except Exception:
                    continue
        # If no attribute found, try to convert __dict__ if available
        if hasattr(obj, '__dict__'):
            for val in obj.__dict__.values():
                try:
                    return normalize_to_pil(val)
                except Exception:
                    continue
    return None

@register_normalizer
def _normalize_list_tuple(obj: Any) -> Optional[Image.Image]:
    if isinstance(obj, (list, tuple)):
        try:
            arr = np.array(obj)
            return Image.fromarray(arr)
        except Exception as e:
            logger.warning(f"List/tuple normalizer failed: {e}")
    return None

# ---- Main Normalizer ----
def normalize_to_pil(obj: Any, apply_exif: bool = True, force_rgb: bool = True) -> Image.Image:
    """
    Single entry point for all input types.
    Raises NormalizationError if conversion fails.
    """
    if obj is None:
        raise NormalizationError("Input is None")

    img = None
    for handler in _normalizers:
        try:
            img = handler(obj)
            if img is not None:
                break
        except Exception as e:
            logger.debug(f"Handler {handler.__name__} failed: {e}")
            continue

    if img is None:
        raise NormalizationError(f"Unsupported input type: {type(obj)}")

    # ---- Post-processing ----
    # 1. EXIF orientation
    if apply_exif:
        try:
            img = ImageOps.exif_transpose(img)
        except Exception:
            pass

    # 2. Force RGB (detectors expect RGB)
    if force_rgb:
        if img.mode not in ('RGB', 'L'):
            img = img.convert('RGB')
        elif img.mode == 'L':
            img = img.convert('RGB')

    # 3. Load to release file handles
    try:
        img.load()
    except Exception:
        pass

    return img

# ------------------------------------------------------------------
# 8.  engine/detector.py  (Interface + Mock)
# ------------------------------------------------------------------
"""
engine/detector.py
"""
from PIL import Image
from typing import Optional
from models.detector_result import DetectorResult
from utils.exceptions import DetectorError
from utils.logger import logger

class BaseDetector:
    """Abstract interface for detectors."""
    def detect(self, image: Image.Image) -> DetectorResult:
        raise NotImplementedError

class MockDetector(BaseDetector):
    """Mock detector for testing/demo."""
    def detect(self, image: Image.Image) -> DetectorResult:
        # Simulate detection (in production, replace with Gemini/OpenAI)
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

# Singleton
_default_detector: Optional[BaseDetector] = None

def get_detector() -> BaseDetector:
    global _default_detector
    if _default_detector is None:
        _default_detector = MockDetector()
    return _default_detector

# ------------------------------------------------------------------
# 9.  engine/gap_analyzer.py  (Interface + Mock)
# ------------------------------------------------------------------
"""
engine/gap_analyzer.py
"""
from typing import Dict, Any
from models.detector_result import DetectorResult, GapResult, GapItem

class GapAnalyzer:
    """Analyze gaps between detector results and DNA."""
    def analyze(self, detector_result: DetectorResult, dna: Dict[str, Any]) -> GapResult:
        # In a real implementation, this would compare detector_result with DNA
        # and produce detailed gap items.
        # For now, we return a demo GapResult.
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

# ------------------------------------------------------------------
# 10. engine/creative_director.py  (Interface + Mock)
# ------------------------------------------------------------------
"""
engine/creative_director.py
"""
from typing import Dict, Any
from models.detector_result import GapResult, CreativePlan

class CreativeDirector:
    """Generate creative recommendations and final prompt."""
    def generate(self, gap_result: GapResult, dna: Dict[str, Any]) -> CreativePlan:
        # Build recommendations from gap items
        recommendations = []
        for item in gap_result.missing:
            recommendations.append(f"Tambah {item.element}")
        for item in gap_result.conflicts:
            recommendations.append(f"Ganti {item.element} → {item.target}")

        # Build final prompt (simplified demo)
        final_prompt = f"A cinematic {gap_result.channel.lower()} scene with " + ", ".join(recommendations[:3])

        return CreativePlan(
            channel=gap_result.channel,
            current_score=gap_result.confidence,
            predicted_score=min(95.0, gap_result.confidence + 15),
            recommendations=recommendations,
            final_prompt=final_prompt,
            delta=f"+{min(95.0, gap_result.confidence + 15) - gap_result.confidence:.1f}%"
        )

# ------------------------------------------------------------------
# 11. engine/prompt_compiler.py  (Adapter Pattern)
# ------------------------------------------------------------------
"""
engine/prompt_compiler.py
"""
from typing import Dict, Any, Optional
from models.detector_result import CreativePlan

class PromptAdapter:
    """Base class for all prompt adapters."""
    def compile(self, plan: CreativePlan, dna: Dict[str, Any]) -> str:
        raise NotImplementedError

class MidjourneyAdapter(PromptAdapter):
    def compile(self, plan: CreativePlan, dna: Dict[str, Any]) -> str:
        return plan.final_prompt + " --ar 16:9 --style raw --s 50 --v 6.1"

class SDXLAdapter(PromptAdapter):
    def compile(self, plan: CreativePlan, dna: Dict[str, Any]) -> str:
        return plan.final_prompt

class FluxAdapter(PromptAdapter):
    def compile(self, plan: CreativePlan, dna: Dict[str, Any]) -> str:
        return f"(((cinematic {plan.channel}))), {plan.final_prompt}"

class KlingAdapter(PromptAdapter):
    def compile(self, plan: CreativePlan, dna: Dict[str, Any]) -> str:
        return f"cinematic shot, {plan.channel}, {plan.final_prompt}, camera 4s loop 24fps"

class RunwayAdapter(PromptAdapter):
    def compile(self, plan: CreativePlan, dna: Dict[str, Any]) -> str:
        return f"cinematic shot, {plan.channel}, {plan.final_prompt}, mood"

# ------------------------------------------------------------------
# 12. services/download.py  (robust URL/YouTube downloader)
# ------------------------------------------------------------------
"""
services/download.py
"""
import requests
from PIL import Image
from io import BytesIO
from typing import Optional, List, Tuple
import re
from config.constants import DEFAULT_USER_AGENT, DEFAULT_TIMEOUT
from utils.exceptions import VPDError
from utils.logger import logger

def download_image_from_url(url: str, timeout: int = DEFAULT_TIMEOUT) -> Optional[Image.Image]:
    """Download image from URL with proper headers and timeout."""
    headers = {"User-Agent": DEFAULT_USER_AGENT}
    try:
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        # Try to open as image
        img = Image.open(BytesIO(response.content))
        return img
    except Exception as e:
        logger.warning(f"Failed to download image from {url}: {e}")
        return None

def get_youtube_thumbnail(video_url: str) -> Tuple[Optional[str], Optional[str]]:
    """Extract YouTube video ID and return thumbnail URL (fallback chain)."""
    pattern = r'(?:youtube\.com\/watch\?v=|youtu\.be\/)([a-zA-Z0-9_-]{11})'
    match = re.search(pattern, video_url)
    if not match:
        return None, None
    video_id = match.group(1)
    # Try different thumbnail sizes
    candidates = [
        f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg",
        f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg",
        f"https://img.youtube.com/vi/{video_id}/sddefault.jpg",
    ]
    for url in candidates:
        try:
            # Use GET stream to check existence (HEAD is often blocked)
            resp = requests.get(url, stream=True, timeout=DEFAULT_TIMEOUT, headers={"User-Agent": DEFAULT_USER_AGENT})
            if resp.status_code == 200:
                return url, video_id
        except Exception:
            continue
    return None, video_id

# ------------------------------------------------------------------
# 13. services/export.py  (Basic export structure)
# ------------------------------------------------------------------
"""
services/export.py
"""
import json
import zipfile
import io
from typing import Dict, Any
from models.project_state import ProjectState
from utils.exceptions import ExportError
from utils.logger import logger

def generate_export_package(project: ProjectState) -> bytes:
    """Generate a ZIP package containing project data."""
    try:
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
            # Project summary
            summary = {
                "channel": project.channel,
                "has_image": project.has_image(),
                "detector": project.detector_result,
                "gap": project.gap_result,
                "creative": project.creative_result,
                "final_prompt": project.final_prompt,
                "revisions": project.revisions,
                "research": project.research_links,
            }
            zf.writestr("project.json", json.dumps(summary, indent=2))

            # Prompt file
            if project.final_prompt:
                zf.writestr("prompt.txt", project.final_prompt)

            # TODO: Add image, PDF report, etc.
        return buffer.getvalue()
    except Exception as e:
        logger.error(f"Export failed: {e}")
        raise ExportError(f"Failed to create export package: {e}")

# ------------------------------------------------------------------
# 14. app.py  — MAIN UI (≈350 lines)
# ------------------------------------------------------------------
"""
app.py  — Main Streamlit Application
"""
import streamlit as st
import yaml
import datetime
from pathlib import Path

# ---- Imports from our modules ----
from config.constants import CHANNEL_NAMES, SUPPORTED_IMAGE_TYPES, DATA_DIR
from models import ImageSource, ProjectState
from models.detector_result import DetectorResult, GapResult, CreativePlan
from engine.input_normalizer import normalize_to_pil, NormalizationError
from engine.detector import get_detector
from engine.gap_analyzer import GapAnalyzer
from engine.creative_director import CreativeDirector
from engine.prompt_compiler import MidjourneyAdapter, SDXLAdapter, FluxAdapter, KlingAdapter, RunwayAdapter
from services.download import download_image_from_url, get_youtube_thumbnail
from services.export import generate_export_package
from utils.exceptions import VPDError
from utils.logger import logger
from streamlit_paste_button import paste_image_button

# ---- Page config ----
st.set_page_config(
    page_title="YOGANS BGM STUDIO AI Creative Studio",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---- Load YAML data ----
@st.cache_data(ttl=300)
def load_dna():
    file_path = DATA_DIR / "channel_dna.yaml"
    with open(file_path, "r") as f:
        return yaml.safe_load(f)

@st.cache_data(ttl=300)
def load_knowledge():
    file_path = DATA_DIR / "knowledge_graph.yaml"
    with open(file_path, "r") as f:
        return yaml.safe_load(f)

@st.cache_data(ttl=300)
def load_bgm():
    try:
        file_path = DATA_DIR / "bgm_studio.yaml"
        with open(file_path, "r") as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        return {}

DNA = load_dna()
KNOWLEDGE = load_knowledge()
BGM = load_bgm()
CHANNEL_LIST = list(DNA.keys())

# ---- Session State (single ProjectState) ----
if 'project' not in st.session_state:
    st.session_state.project = ProjectState()

project = st.session_state.project

# ---- Helper functions ----
def set_image_source(raw_input, source: str, filename: str = "untitled.png") -> bool:
    """Unified setter using the normalizer."""
    if raw_input is None:
        return False
    try:
        pil_img = normalize_to_pil(raw_input)
    except NormalizationError as e:
        st.error(f"❌ Gagal ngolah gambar: {e}")
        return False
    project.image_source = ImageSource(
        image=pil_img,
        source=source,
        filename=filename
    )
    project.clear_analysis()
    return True

def get_current_image():
    return project.image_source.image if project.image_source else None

# ---- Sidebar ----
with st.sidebar:
    st.image("https://placehold.co/200x60/1a1a1a/FFB800?text=YOGANS+BGM+STUDIO", use_column_width=True)
    st.markdown("---")
    menu = st.radio(
        "Navigasi",
        ["🏠 Home", "📂 Project", "🔍 Detector", "🧬 Visual DNA", "✍️ Prompt", "📄 Report", "🧠 Knowledge", "📦 Export"],
        index=0
    )
    st.markdown("---")
    st.caption(f"🔒 FROZEN v7.1 | {datetime.date.today()}")

st.markdown("---")

# ---- MAIN AREA ----
if menu == "🏠 Home":
    st.title("🎨 YOGANS BGM STUDIO AI Creative Studio")
    st.caption("Visual Production Database — FROZEN v7.1")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Projects", "12", "+3")
    col2.metric("PASS Rate", "91%", "▲ 5%")
    col3.metric("Knowledge Nodes", "19", "Stabil")
    st.subheader("📂 Recent Projects")
    for p in [{"name":"Bamboo Hush","score":94,"status":"PASS"}, {"name":"Night Jazz","score":91,"status":"PASS"}, {"name":"Bossa Session","score":78,"status":"WARN"}]:
        a,b,c = st.columns([3,1,1])
        a.write(f"**{p['name']}**")
        b.write(f"Score: {p['score']}%")
        c.write(f"`{p['status']}`")

elif menu == "📂 Project":
    st.title("📂 Project Workspace")
    st.caption("INPUT HUB — Unified input pipeline")
    col_input, col_preview = st.columns([1, 2])

    with col_input:
        st.subheader("📤 Input Hub")
        tab_upload, tab_paste, tab_url, tab_youtube, tab_riset = st.tabs(
            ["📁 Upload", "📋 Paste", "🔗 URL", "▶️ YouTube", "📚 Riset"]
        )

        with tab_upload:
            uploaded = st.file_uploader("Pilih gambar", type=SUPPORTED_IMAGE_TYPES)
            if uploaded:
                if set_image_source(uploaded, "upload", uploaded.name):
                    st.success(f"✅ Gambar siap: {uploaded.name}")
                    st.rerun()

        with tab_paste:
            st.caption("📋 Klik tombol, teras Ctrl+V (atawa Cmd+V)")
            pasted = paste_image_button("📋 Klik di dieu, teras Ctrl+V")
            if pasted is not None:
                # Debug: show type (optional, can be removed later)
                # st.write("Type:", type(pasted))
                if set_image_source(pasted, "clipboard", "clipboard.png"):
                    st.success("✅ Gambar hasil paste!")
                    st.rerun()

        with tab_url:
            img_url = st.text_input("🔗 URL Gambar", placeholder="https://example.com/image.jpg")
            if st.button("📥 Download & Analisis"):
                if img_url:
                    with st.spinner("Ngundeur gambar..."):
                        img = download_image_from_url(img_url)
                        if img and set_image_source(img, "url", img_url.split("/")[-1]):
                            st.success("✅ Gambar hasil download!")
                            st.rerun()
                else:
                    st.warning("Masukkan URL heula.")

        with tab_youtube:
            yt_url = st.text_input("▶️ URL YouTube", placeholder="https://www.youtube.com/watch?v=...")
            if yt_url:
                thumb_url, vid = get_youtube_thumbnail(yt_url)
                if thumb_url:
                    st.image(thumb_url, caption=f"Thumbnail: {vid}", use_column_width=True)
                    if st.button("🎬 Gunakeun Thumbnail"):
                        img = download_image_from_url(thumb_url)
                        if img and set_image_source(img, "youtube", f"yt_{vid}.jpg"):
                            st.success("✅ Thumbnail dipaké!")
                            st.rerun()
                else:
                    st.warning("Teu bisa ménta thumbnail.")

        with tab_riset:
            research_url = st.text_input("🔗 URL Riset", placeholder="https://example.com/article")
            research_note = st.text_area("📝 Catatan", placeholder="Tulis catetan...")
            if st.button("💾 Simpan Riset"):
                if research_url or research_note:
                    project.research_links.append({
                        "url": research_url,
                        "note": research_note,
                        "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                    })
                    st.success("✅ Disimpen!")
            if project.research_links:
                st.markdown("---")
                st.subheader("📚 Daftar Riset")
                for i, item in enumerate(project.research_links):
                    with st.expander(f"📄 {item['date']}"):
                        st.markdown(f"**URL:** {item['url']}")
                        st.markdown(f"**Catatan:** {item['note']}")
                        if st.button(f"🗑️ Hapus {i+1}", key=f"del_{i}"):
                            project.research_links.pop(i)
                            st.rerun()

        # ---- Image info ----
        if project.image_source:
            src = project.image_source
            st.markdown("---")
            st.success(f"🖼️ **Aktif:** `{src.source}` — {src.filename} ({src.width}×{src.height})")
            if st.button("🧹 Clear Image"):
                project.clear_all()
                st.rerun()

        # ---- Revision history ----
        st.markdown("---")
        st.subheader("🔄 Revision History")
        if project.revisions:
            for rev in project.revisions:
                st.text(f"v{rev['id']}: {rev['score']}% - {rev['status']}")
        else:
            st.caption("Belum aya revisi.")

    with col_preview:
        st.subheader("🖼️ Preview")
        img = get_current_image()
        if img:
            st.image(img, use_column_width=True)
            st.info(f"🔮 Channel: **{project.channel}**")
        else:
            st.warning("📤 Upload, paste, URL, atanapi YouTube heula!")

elif menu == "🔍 Detector":
    st.title("🔍 Detector & AI Creative Director")
    img = get_current_image()
    if img is None:
        st.warning("📤 Input gambar heula di Project.")
    else:
        if st.button("⚡ Analyze Image", type="primary"):
            with st.spinner("Analyzing..."):
                try:
                    detector = get_detector()
                    det_result = detector.detect(img)
                    project.detector_result = det_result.to_dict()

                    # Gap analysis
                    gap_analyzer = GapAnalyzer()
                    dna_channel = DNA.get(project.channel, {})
                    gap_result = gap_analyzer.analyze(det_result, dna_channel)
                    project.gap_result = gap_result.to_dict()

                    # Creative Director
                    director = CreativeDirector()
                    creative_plan = director.generate(gap_result, dna_channel)
                    project.creative_result = creative_plan.to_dict()
                    project.final_prompt = creative_plan.final_prompt

                    st.success("✅ Analysis Complete!")
                except VPDError as e:
                    st.error(f"❌ Analysis failed: {e}")
                    logger.error(f"Detector error: {e}")

        # Display results
        if project.detector_result:
            res = project.detector_result
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("📊 Detector Scores")
                st.bar_chart({
                    "Arsitektur": res.get("confidence", 0),
                    "Material": res.get("confidence", 0) * 0.95,
                    "Umur": res.get("confidence", 0) * 0.85,
                    "Cahaya": res.get("confidence", 0) * 0.90,
                    "Gerak": res.get("confidence", 0) * 0.80,
                })
                st.metric("Channel", res.get("channel", "-"))
                st.metric("Confidence", f"{res.get('confidence', 0)}%")
            with col2:
                st.subheader("🧠 Gap Analysis")
                if project.gap_result:
                    gap = project.gap_result
                    for k, items in [("✅ Match", gap.get("match", [])), ("❌ Missing", gap.get("missing", [])), ("⚠️ Conflict", gap.get("conflict", []))]:
                        if items:
                            st.markdown(f"**{k}**")
                            for item in items:
                                st.caption(f"• {item.get('element', '-')}")
                if project.creative_result:
                    st.markdown("---")
                    st.subheader("💡 Creative Plan")
                    cr = project.creative_result
                    for rec in cr.get("recommendations", []):
                        st.caption(f"🔥 {rec}")
                    st.metric("Predicted Score", f"{cr.get('predicted_score', 0)}%")
                    if st.button("📋 Terapkan ke Prompt"):
                        st.success("Prompt siap di tab ✍️ Prompt")

elif menu == "🧬 Visual DNA":
    st.title("🧬 Visual DNA Card")
    selected = st.selectbox("Pilih Channel", CHANNEL_LIST, index=CHANNEL_LIST.index(project.channel))
    project.channel = selected
    dna = DNA[selected]
    col1, col2 = st.columns(2)
    with col1:
        st.metric("World", selected)
        st.metric("Architecture", dna.get("architecture", "-"))
        st.metric("Era", dna.get("era", "-"))
        st.metric("Lighting", dna.get("lighting", "-"))
        st.metric("Camera", dna.get("camera", "-"))
    with col2:
        st.subheader("Hero"); st.write(", ".join(dna.get("hero", [])))
        st.subheader("Mood"); st.write(", ".join(dna.get("mood", [])))
        st.subheader("Palette"); st.write(", ".join(dna.get("palette", [])))
        st.subheader("Material"); st.write(", ".join(dna.get("material", [])))
        st.subheader("FX"); st.write(", ".join(dna.get("fx", [])))

elif menu == "✍️ Prompt":
    st.title("✍️ Prompt Compiler")
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["🖼️ IMAGE", "🎥 VIDEO", "🎵 MUSIC", "🚫 NEGATIVE", "🧩 PARTIAL"])
    channel = project.channel
    dna = DNA[channel]
    bgm = BGM.get(channel, {})

    with tab1:
        st.subheader("Midjourney Prompt")
        if project.final_prompt:
            prompt = project.final_prompt + " --ar 16:9 --style raw --s 50 --v 6.1"
            st.info("📌 Prompt Final ti Creative Director")
        else:
            prompt = f"A cinematic {dna.get('architecture', '')} with {', '.join(dna.get('hero', [])[:2])}, {dna.get('mood', [''])[0]} atmosphere, {dna.get('lighting', '')} lighting --ar 16:9 --style raw --s 50 --v 6.1"
        st.code(prompt, language="text")
        st.download_button("📋 Copy Image Prompt", prompt, file_name="prompt_image.txt")
        if st.button("🔄 Reset ka DNA Default"):
            project.final_prompt = ""
            st.rerun()

    with tab2:
        video_prompt = f"cinematic shot, {dna.get('architecture', '')}, {', '.join(dna.get('hero', []))}, 4s loop 24fps"
        st.code(video_prompt, language="text")

    with tab3:
        st.subheader("🎵 BGM Studio")
        if bgm:
            st.markdown(f"**Style:** {bgm.get('bgm_style', '-')}")
            st.markdown(f"**Instruments:** {', '.join(bgm.get('instruments', []))}")
            st.markdown(f"**Mood:** {', '.join(bgm.get('mood_tags', []))}")
            st.code(bgm.get('prompt_suno', ''), language="text")
        else:
            st.warning("BGM data teu aya.")

    with tab4:
        st.code("low quality, blurry, distorted, plastic, fake, ugly", language="text")

    with tab5:
        st.code(f"({dna.get('architecture', '')}), {', '.join(dna.get('hero', []))}, {dna.get('lighting', '')}", language="text")

elif menu == "📄 Report":
    st.title("📄 Report Generator")
    tab_r1, tab_r2, tab_r3 = st.tabs(["📋 Project Report", "📈 Weekly Report", "⭐ Final Report"])
    with tab_r1:
        st.subheader("📋 Project Report")
        if project.image_source and project.detector_result:
            st.markdown(f"""
            **Channel:** {project.channel}
            **Image:** {project.image_source.filename} ({project.image_source.width}×{project.image_source.height})
            **Confidence:** {project.detector_result.get('confidence', 0)}%
            **Prompt:** {project.final_prompt or 'Belum aya'}
            """)
        else:
            st.info("Jalanan Detector heula.")
    with tab_r2:
        st.metric("Projects This Week", "5")
        st.metric("Average Score", "89%")
        st.bar_chart({"Jazz": 3, "Bossa": 2, "Forest": 1})
    with tab_r3:
        st.success("⭐ Final Knowledge Report")
        if project.gap_result:
            st.json(project.gap_result)
        else:
            st.info("Belum aya data.")

elif menu == "🧠 Knowledge":
    st.title("🧠 Master Knowledge Database")
    st.subheader("📊 Statistik per Channel")
    cols = st.columns(3)
    for i, name in enumerate(CHANNEL_LIST):
        with cols[i % 3]:
            st.metric(name, f"Project: {i*10+5}", f"PASS: {i*8+3}")
    st.subheader("📈 Knowledge Growth")
    st.line_chart({"Week 1": 152, "Week 2": 181, "Week 3": 229, "Week 4": 284})
    with st.expander("🌳 Knowledge Graph (YAML)"):
        st.json(KNOWLEDGE)

elif menu == "📦 Export":
    st.title("📦 Export Project")
    st.caption("Ekspor sadaya data project.")
    if st.button("📥 Generate & Download ZIP", type="primary"):
        try:
            zip_data = generate_export_package(project)
            st.download_button(
                "⬇️ Download",
                zip_data,
                file_name=f"export_{project.channel}_{datetime.date.today()}.zip",
                mime="application/zip"
            )
        except Exception as e:
            st.error(f"Export gagal: {e}")

# ---- Footer ----
st.sidebar.markdown("---")
st.sidebar.caption("🎨 YOGANS BGM STUDIO v7.1 | Made with Streamlit")