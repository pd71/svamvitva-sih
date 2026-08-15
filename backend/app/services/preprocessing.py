import os
import cv2
import numpy as np
from PIL import Image
from typing import Dict, Any, Tuple

def validate_and_load_image(file_path: str) -> Tuple[np.ndarray, Dict[str, Any]]:
    """
    Validates uploaded orthophoto file, extracts image properties.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    # Read image using PIL to check format
    with Image.open(file_path) as img:
        width, height = img.size
        format_name = img.format

    # Read image using OpenCV for CV pipeline
    image_np = cv2.imread(file_path)
    if image_np is None:
        raise ValueError("Could not decode image format.")

    # Convert BGR to RGB
    image_rgb = cv2.cvtColor(image_np, cv2.COLOR_BGR2RGB)
    
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
    """
    h, w, c = image_rgb.shape
    scale = min(max_dim / w, max_dim / h)
    if scale < 1.0:
        new_w, new_h = int(w * scale), int(h * scale)
        thumb = cv2.resize(image_rgb, (new_w, new_h), interpolation=cv2.INTER_AREA)
    else:
        thumb = image_rgb

    thumb_bgr = cv2.cvtColor(thumb, cv2.COLOR_RGB2BGR)
    cv2.imwrite(output_path, thumb_bgr)
    return output_path
