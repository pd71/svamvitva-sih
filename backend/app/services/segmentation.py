"""
Segmentation pipeline — pure numpy implementation, no OpenCV dependency.
"""
import numpy as np
from typing import List, Dict, Any, Tuple
from app.ml.base import SegmentationModel
from app.services.gis import (
    contour_to_polygon_geojson,
    contour_to_linestring_geojson,
    calculate_polygon_area,
    calculate_line_length,
    calculate_centroid,
)


def _find_contours_numpy(mask: np.ndarray) -> List[np.ndarray]:
    """
    Lightweight pure-numpy connected-component contour finder.
    Returns a list of Nx1x2 arrays (mimicking cv2 contour format).
    """
    from PIL import Image
    # Label connected components
    img = Image.fromarray(mask)
    # Simple approach: find bounding boxes of connected regions via flood-fill labels
    contours = []
    visited = np.zeros_like(mask, dtype=bool)
    h, w = mask.shape

    for start_y in range(h):
        for start_x in range(w):
            if mask[start_y, start_x] == 0 or visited[start_y, start_x]:
                continue
            # BFS flood fill
            region = []
            stack = [(start_y, start_x)]
            while stack:
                cy, cx = stack.pop()
                if cy < 0 or cy >= h or cx < 0 or cx >= w:
                    continue
                if visited[cy, cx] or mask[cy, cx] == 0:
                    continue
                visited[cy, cx] = True
                region.append((cx, cy))
                stack.extend([(cy+1, cx), (cy-1, cx), (cy, cx+1), (cy, cx-1)])
            if len(region) > 10:
                pts = np.array(region, dtype=np.int32).reshape(-1, 1, 2)
                contours.append(pts)
    return contours


def run_segmentation_pipeline(
    image_rgb: np.ndarray,
    model: SegmentationModel
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Executes AI segmentation on image_rgb.
    Extracts individual vector features: Buildings, Roads, Waterbodies.
    """
    h, w, _ = image_rgb.shape
    segmentation_mask, confidence_maps = model.predict_segmentation(image_rgb)

    buildings = []
    roads = []
    waterbodies = []

    # --- Extract Building Polygons (Class 1) ---
    bldg_mask = np.uint8(segmentation_mask == 1) * 255
    bldg_contours = _find_contours_numpy(bldg_mask)

    bldg_idx = 1
    for cnt in bldg_contours:
        area_sqm = calculate_polygon_area(cnt)
        if area_sqm < 5.0:
            continue

        geojson = contour_to_polygon_geojson(cnt, h, w)
        if not geojson:
            continue

        cx, cy = calculate_centroid(cnt)
        pts = cnt.reshape(-1, 2)
        x1, y1 = pts[:, 0].min(), pts[:, 1].min()
        x2, y2 = pts[:, 0].max(), pts[:, 1].max()

        # Average confidence inside building region
        mask_region = segmentation_mask == 1
        cnt_conf = float(np.mean(confidence_maps["building"][mask_region])) if np.any(mask_region) else 0.85

        buildings.append({
            "building_index": bldg_idx,
            "geometry_geojson": geojson,
            "area_sqm": area_sqm,
            "centroid_x": cx,
            "centroid_y": cy,
            "bbox": (int(x1), int(y1), int(x2 - x1), int(y2 - y1)),
            "confidence": round(cnt_conf, 3),
            "status": "detected"
        })
        bldg_idx += 1

    # --- Extract Road Lines (Class 2) ---
    road_mask = np.uint8(segmentation_mask == 2) * 255
    road_contours = _find_contours_numpy(road_mask)

    road_idx = 1
    for cnt in road_contours:
        length_m = calculate_line_length(cnt)
        if length_m < 5.0:
            continue

        geojson = contour_to_linestring_geojson(cnt)
        if not geojson:
            continue

        roads.append({
            "road_index": road_idx,
            "geometry_geojson": geojson,
            "length_m": length_m,
            "confidence": 0.82
        })
        road_idx += 1

    # --- Extract Waterbodies (Class 3) ---
    water_mask = np.uint8(segmentation_mask == 3) * 255
    water_contours = _find_contours_numpy(water_mask)

    water_idx = 1
    for cnt in water_contours:
        area_sqm = calculate_polygon_area(cnt)
        if area_sqm < 10.0:
            continue

        geojson = contour_to_polygon_geojson(cnt, h, w)
        if not geojson:
            continue

        waterbodies.append({
            "waterbody_index": water_idx,
            "geometry_geojson": geojson,
            "area_sqm": area_sqm,
            "confidence": 0.91
        })
        water_idx += 1

    return buildings, roads, waterbodies
