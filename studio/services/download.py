# services/download.py
import requests
from PIL import Image
from io import BytesIO
from typing import Optional, Tuple
import re
from config.constants import DEFAULT_USER_AGENT, DEFAULT_TIMEOUT

def download_image_from_url(url: str, timeout: int = DEFAULT_TIMEOUT) -> Optional[Image.Image]:
    """Download image from URL with proper headers and timeout."""
    headers = {"User-Agent": DEFAULT_USER_AGENT}
    try:
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        img = Image.open(BytesIO(response.content))
        return img
    except Exception:
        return None

def get_youtube_thumbnail(video_url: str) -> Tuple[Optional[str], Optional[str]]:
    """Extract YouTube video ID and return thumbnail URL (fallback chain)."""
    pattern = r'(?:youtube\.com\/watch\?v=|youtu\.be\/)([a-zA-Z0-9_-]{11})'
    match = re.search(pattern, video_url)
    if not match:
        return None, None
    video_id = match.group(1)
    candidates = [
        f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg",
        f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg",
        f"https://img.youtube.com/vi/{video_id}/sddefault.jpg",
    ]
    for url in candidates:
        try:
            resp = requests.get(url, stream=True, timeout=DEFAULT_TIMEOUT, headers={"User-Agent": DEFAULT_USER_AGENT})
            if resp.status_code == 200:
                return url, video_id
        except Exception:
            continue
    return None, video_id