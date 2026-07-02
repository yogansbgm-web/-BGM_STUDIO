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