# engine/input_normalizer.py
from PIL import Image, ImageOps
import io
import base64
import numpy as np
from typing import Any, Optional, Callable, List
from streamlit.runtime.uploaded_file_manager import UploadedFile

class NormalizationError(Exception):
    """Raised when input cannot be normalized to PIL.Image."""
    pass

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
        except Exception:
            pass
    return None

@register_normalizer
def _normalize_bytes(obj: Any) -> Optional[Image.Image]:
    if isinstance(obj, bytes):
        try:
            return Image.open(io.BytesIO(obj))
        except Exception:
            pass
    return None

@register_normalizer
def _normalize_base64(obj: Any) -> Optional[Image.Image]:
    if isinstance(obj, str) and obj.startswith('data:image'):
        try:
            header, encoded = obj.split(',', 1)
            data = base64.b64decode(encoded)
            return Image.open(io.BytesIO(data))
        except Exception:
            pass
    return None

@register_normalizer
def _normalize_filepath(obj: Any) -> Optional[Image.Image]:
    if isinstance(obj, str) and not obj.startswith('data:image'):
        try:
            return Image.open(obj)
        except Exception:
            pass
    return None

@register_normalizer
def _normalize_numpy(obj: Any) -> Optional[Image.Image]:
    if isinstance(obj, np.ndarray):
        try:
            return Image.fromarray(obj)
        except Exception:
            pass
    return None

@register_normalizer
def _normalize_dict(obj: Any) -> Optional[Image.Image]:
    if isinstance(obj, dict):
        for key in ['image', 'img', 'data', 'blob', 'value', 'content']:
            if key in obj:
                try:
                    return normalize_to_pil(obj[key])
                except Exception:
                    continue
    return None

@register_normalizer
def _normalize_paste_result(obj: Any) -> Optional[Image.Image]:
    """Special handler for streamlit_paste_button.PasteResult."""
    # Check class name (because type(obj) might not be directly imported)
    if obj.__class__.__name__ == "PasteResult":
        for attr in ['image', 'data', 'bytes', 'content', 'value']:
            if hasattr(obj, attr):
                try:
                    val = getattr(obj, attr)
                    if val is not None:
                        return normalize_to_pil(val)
                except Exception:
                    continue
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
        except Exception:
            pass
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
        except Exception:
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