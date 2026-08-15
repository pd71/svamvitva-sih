import cv2
import numpy as np
from typing import List, Dict, Any, Tuple
from shapely.geometry import Polygon, LineString, mapping

# Pixel to meters conversion scale for local demo coordinate system
# 1 pixel = 0.25 meters (typical high-res drone ground sampling distance: 25cm/px)
GSD_METERS_PER_PX = 0.25

def contour_to_polygon_geojson(contour: np.ndarray, image_h: int, image_w: int) -> Dict[str, Any]:
    """
    Converts OpenCV contour points into GeoJSON Polygon format.
    Coordinates are mapped either to normalized local coordinates [0..100] or relative map coordinates.
    """
    pts = contour.reshape(-1, 2)
    if len(pts) < 3:
        return None

    # Close loop
    coords = [[float(pt[0]), float(pt[1])] for pt in pts]
    if coords[0] != coords[-1]:
        coords.append(coords[0])

    geojson = {
        "type": "Polygon",
        "coordinates": [coords]
    }
    return geojson

def contour_to_linestring_geojson(contour: np.ndarray) -> Dict[str, Any]:
    """
    Converts OpenCV contour into GeoJSON LineString format for road centerline network.
    """
    pts = contour.reshape(-1, 2)
    if len(pts) < 2:
        return None
    coords = [[float(pt[0]), float(pt[1])] for pt in pts]
    return {
        "type": "LineString",
        "coordinates": coords
    }

def calculate_polygon_area(contour: np.ndarray, gsd: float = GSD_METERS_PER_PX) -> float:
    """
    Calculates polygon area in square meters.
    """
    pixel_area = cv2.contourArea(contour)
    sq_m_area = pixel_area * (gsd ** 2)
    return round(float(sq_m_area), 2)

def calculate_line_length(contour: np.ndarray, gsd: float = GSD_METERS_PER_PX) -> float:
    """
    Calculates line or road perimeter length in meters.
    """
    pixel_len = cv2.arcLength(contour, False)
    m_len = (pixel_len / 2.0) * gsd  # approximate corridor length
    return round(float(m_len), 2)

def calculate_centroid(contour: np.ndarray) -> Tuple[float, float]:
    """
    Calculates (centroid_x, centroid_y) in image pixel coordinates.
    """
    M = cv2.moments(contour)
    if M["m00"] != 0:
        cx = float(M["m10"] / M["m00"])
        cy = float(M["m01"] / M["m00"])
    else:
        pts = contour.reshape(-1, 2)
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
    Generates a stunning visual overlay image showing detected building polygons,
    roof classification colors, road networks, and waterbodies.
    """
    h, w, c = image_rgb.shape
    overlay_bgr = cv2.cvtColor(image_rgb.copy(), cv2.COLOR_RGB2BGR)

    # Color map for roof types (BGR)
    roof_colors = {
        "RCC": (220, 200, 50),     # Cyan-Yellow (Concrete)
        "Tiled": (40, 60, 230),    # Terracotta Red
        "Tin": (240, 180, 50),     # Metallic Blue
        "Other": (150, 150, 150)   # Grey
    }

    # 1. Draw Waterbodies (Deep Blue with semi-transparent fill)
    water_layer = overlay_bgr.copy()
    for wb in waterbodies:
        coords = wb["geometry_geojson"]["coordinates"][0]
        pts = np.array([[int(c[0]), int(c[1])] for c in coords], dtype=np.int32)
        cv2.fillPoly(water_layer, [pts], (230, 110, 30))  # BGR for blue water
        cv2.polylines(overlay_bgr, [pts], True, (255, 140, 0), 2)
    cv2.addWeighted(water_layer, 0.4, overlay_bgr, 0.6, 0, overlay_bgr)

    # 2. Draw Roads (Bright Yellow centerline/corridor)
    for rd in roads:
        coords = rd["geometry_geojson"]["coordinates"]
        pts = np.array([[int(c[0]), int(c[1])] for c in coords], dtype=np.int32)
        cv2.polylines(overlay_bgr, [pts], False, (0, 230, 255), 3)

    # 3. Draw Building Polygons with Roof Type Color Fills
    bldg_layer = overlay_bgr.copy()
    for bldg in buildings:
        coords = bldg["geometry_geojson"]["coordinates"][0]
        pts = np.array([[int(c[0]), int(c[1])] for c in coords], dtype=np.int32)
        color = roof_colors.get(bldg.get("roof_type", "RCC"), (0, 255, 0))
        cv2.fillPoly(bldg_layer, [pts], color)
        cv2.polylines(overlay_bgr, [pts], True, (255, 255, 255), 2)

        # Draw Building ID label at centroid
        cx, cy = int(bldg["centroid_x"]), int(bldg["centroid_y"])
        idx = bldg.get("building_index", 0)
        cv2.putText(overlay_bgr, f"#{idx}", (cx - 10, cy + 4), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 2)
        cv2.putText(overlay_bgr, f"#{idx}", (cx - 10, cy + 4), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)

    cv2.addWeighted(bldg_layer, 0.45, overlay_bgr, 0.55, 0, overlay_bgr)

    cv2.imwrite(output_path, overlay_bgr)
    return output_path
