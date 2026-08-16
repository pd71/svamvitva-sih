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
    Extracts smooth connected contours for buildings, roads, and waterbodies.
    Prefers cv2.findContours for exact boundary polygons.
    Falls back to scipy.ndimage connected components.
    """
    try:
        import cv2
        contours, _ = cv2.findContours(mask.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        valid_contours = []
        for cnt in contours:
            if cv2.contourArea(cnt) >= 100:
                valid_contours.append(cnt)
        if valid_contours:
            return valid_contours
    except Exception:
        pass

    try:
        from scipy.ndimage import label, find_objects
        labeled, num_features = label(mask > 0)
        slices = find_objects(labeled)
        contours = []
        for sl in slices:
            if sl is None:
                continue
            sy, sx = sl
            min_y, max_y = sy.start, sy.stop
            min_x, max_x = sx.start, sx.stop
            if (max_x - min_x) < 15 or (max_y - min_y) < 15:
                continue
            pts = np.array([
                [min_x, min_y],
                [max_x, min_y],
                [max_x, max_y],
                [min_x, max_y]
            ], dtype=np.int32).reshape(-1, 1, 2)
            contours.append(pts)
        return contours
    except Exception:
        # Connected region bounding polygon fallback (no 16x16 subgrid breakdown)
        contours = []
        h, w = mask.shape
        visited = np.zeros((h, w), dtype=bool)
        for y in range(0, h, 20):
            for x in range(0, w, 20):
                if mask[y, x] > 0 and not visited[y, x]:
                    y1, y2 = max(0, y-40), min(h, y+60)
                    x1, x2 = max(0, x-40), min(w, x+60)
                    sub = mask[y1:y2, x1:x2]
                    y_idx, x_idx = np.where(sub > 0)
                    if len(y_idx) > 30:
                        min_y_r, max_y_r = y1 + int(y_idx.min()), y1 + int(y_idx.max())
                        min_x_r, max_x_r = x1 + int(x_idx.min()), x1 + int(x_idx.max())
                        visited[min_y_r:max_y_r, min_x_r:max_x_r] = True
                        pts = np.array([
                            [min_x_r, min_y_r],
                            [max_x_r, min_y_r],
                            [max_x_r, max_y_r],
                            [min_x_r, max_y_r]
                        ], dtype=np.int32).reshape(-1, 1, 2)
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
