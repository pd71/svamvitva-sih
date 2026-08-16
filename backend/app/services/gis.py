"""
GIS Utility Functions — pure numpy/PIL implementation, no OpenCV dependency.
"""
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from typing import List, Dict, Any, Tuple
from shapely.geometry import Polygon, LineString

GSD_METERS_PER_PX = 0.25  # 25cm/px typical drone GSD


def contour_to_polygon_geojson(contour: np.ndarray, image_h: int, image_w: int) -> Dict[str, Any]:
    pts = contour.reshape(-1, 2)
    if len(pts) < 3:
        return None
    coords = [[float(pt[0]), float(pt[1])] for pt in pts]
    if coords[0] != coords[-1]:
        coords.append(coords[0])
    return {"type": "Polygon", "coordinates": [coords]}


def contour_to_linestring_geojson(contour: np.ndarray) -> Dict[str, Any]:
    pts = contour.reshape(-1, 2)
    if len(pts) < 2:
        return None
    coords = [[float(pt[0]), float(pt[1])] for pt in pts]
    return {"type": "LineString", "coordinates": coords}


def calculate_polygon_area(contour: np.ndarray, gsd: float = GSD_METERS_PER_PX) -> float:
    pts = contour.reshape(-1, 2).astype(np.float64)
    # Shoelace formula
    n = len(pts)
    if n < 3:
        return 0.0
    x, y = pts[:, 0], pts[:, 1]
    pixel_area = 0.5 * abs(np.dot(x, np.roll(y, -1)) - np.dot(y, np.roll(x, -1)))
    return round(float(pixel_area * (gsd ** 2)), 2)


def calculate_line_length(contour: np.ndarray, gsd: float = GSD_METERS_PER_PX) -> float:
    pts = contour.reshape(-1, 2).astype(np.float64)
    diffs = np.diff(pts, axis=0)
    pixel_len = float(np.sum(np.sqrt((diffs ** 2).sum(axis=1))))
    return round((pixel_len / 2.0) * gsd, 2)


def calculate_centroid(contour: np.ndarray) -> Tuple[float, float]:
    pts = contour.reshape(-1, 2).astype(np.float64)
    cx = float(np.mean(pts[:, 0]))
    cy = float(np.mean(pts[:, 1]))
    return round(cx, 2), round(cy, 2)


def generate_overlay_image(
    image_rgb: np.ndarray,
    buildings: List[Dict[str, Any]],
    roads: List[Dict[str, Any]],
    waterbodies: List[Dict[str, Any]],
    output_path: str
) -> str:
    """
    Generates a visual overlay image using PIL — no OpenCV required.
    """
    img = Image.fromarray(image_rgb.astype(np.uint8)).convert("RGBA")
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    roof_colors = {
        "RCC":   (50, 200, 220, 140),
        "Tiled": (230, 60, 40, 140),
        "Tin":   (50, 180, 240, 140),
        "Other": (150, 150, 150, 140),
    }

    # Waterbodies
    for wb in waterbodies:
        try:
            coords = wb["geometry_geojson"]["coordinates"][0]
            pts = [(int(c[0]), int(c[1])) for c in coords]
            draw.polygon(pts, fill=(30, 110, 230, 100), outline=(0, 140, 255, 220))
        except Exception:
            pass

    # Roads
    for rd in roads:
        try:
            coords = rd["geometry_geojson"]["coordinates"]
            pts = [(int(c[0]), int(c[1])) for c in coords]
            draw.line(pts, fill=(255, 230, 0, 220), width=3)
        except Exception:
            pass

    # Buildings
    for bldg in buildings:
        try:
            coords = bldg["geometry_geojson"]["coordinates"][0]
            pts = [(int(c[0]), int(c[1])) for c in coords]
            color = roof_colors.get(bldg.get("roof_type", "RCC"), (0, 255, 0, 140))
            draw.polygon(pts, fill=color, outline=(255, 255, 255, 240))
        except Exception:
            pass

    img = Image.alpha_composite(img, overlay).convert("RGB")

    try:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
    except Exception:
        pass
    img.save(output_path)
    return output_path
