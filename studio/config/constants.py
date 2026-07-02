# config/constants.py
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
MAX_IMAGE_PIXELS = 4096 * 4096
SUPPORTED_IMAGE_TYPES = ["jpg", "jpeg", "png", "webp", "bmp", "tiff"]

# --- Detector ---
DEFAULT_CONFIDENCE_THRESHOLD = 70

# --- Export ---
EXPORT_FORMATS = ["ZIP", "PDF", "JSON", "YAML"]

# --- HTTP ---
DEFAULT_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
DEFAULT_TIMEOUT = 15

# --- Logging ---
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = BASE_DIR / "logs" / "vpd.log"

# --- Vision Model Selection ---
VISION_MODEL = os.getenv("VISION_MODEL", "mock")
OPENROUTER_VISION_MODEL = os.getenv("OPENROUTER_VISION_MODEL", "qwen/qwen2.5-vl")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")