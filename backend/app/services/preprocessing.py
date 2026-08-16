import os
import numpy as np
from PIL import Image
from typing import Dict, Any, Tuple


def validate_and_load_image(file_path: str) -> Tuple[np.ndarray, Dict[str, Any]]:
    """
    Validates uploaded orthophoto file, extracts image properties.
    Pure PIL — no OpenCV dependency.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    try:
        with Image.open(file_path) as img:
            width, height = img.size
            format_name = img.format or "PNG"
            image_rgb = np.array(img.convert('RGB'))
    except Exception as e:
        raise ValueError(f"Could not decode image: {e}")

    file_size = os.path.getsize(file_path)

    metadata = {
        "width": width,
        "height": height,
        "file_size": file_size,
        "format": format_name,
        "is_georeferenced": file_path.lower().endswith((".tif", ".tiff")),
        "crs_name": "EPSG:4326 (GeoTIFF Metadata)" if file_path.lower().endswith((".tif", ".tiff")) else "Demo / Local Coordinates"
    }

    return image_rgb, metadata


def create_thumbnail(image_rgb: np.ndarray, output_path: str, max_dim: int = 512) -> str:
    """
    Generates a resized thumbnail for quick preview rendering.
    Pure PIL — no OpenCV dependency.
    """
    h, w, _ = image_rgb.shape
    scale = min(max_dim / w, max_dim / h)
    img = Image.fromarray(image_rgb.astype(np.uint8))
    if scale < 1.0:
        new_w, new_h = int(w * scale), int(h * scale)
        img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)

    try:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
    except Exception:
        pass
    img.save(output_path)
    return output_path
