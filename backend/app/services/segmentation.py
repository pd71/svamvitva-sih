import cv2
import numpy as np
from typing import List, Dict, Any, Tuple
from app.ml.base import SegmentationModel
from app.services.gis import (
    contour_to_polygon_geojson,
    contour_to_linestring_geojson,
    calculate_polygon_area,
    calculate_line_length,
    calculate_centroid
)

def run_segmentation_pipeline(
    image_rgb: np.ndarray,
    model: SegmentationModel
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Executes AI segmentation on image_rgb.
    Extracts individual vector features: Buildings, Roads, Waterbodies.
    """
    h, w, c = image_rgb.shape
    segmentation_mask, confidence_maps = model.predict_segmentation(image_rgb)

    buildings = []
    roads = []
    waterbodies = []

    # --- Extract Building Polygons (Class 1) ---
    bldg_mask = np.uint8(segmentation_mask == 1) * 255
    contours, _ = cv2.findContours(bldg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    bldg_idx = 1
    for cnt in contours:
        # Filter small noise artifacts
        area_px = cv2.contourArea(cnt)
        if area_px < 80:  # min 80 pixels
            continue
        
        # Approximate polygon to straighten roof edges
        epsilon = 0.02 * cv2.arcLength(cnt, True)
        approx_cnt = cv2.approxPolyDP(cnt, epsilon, True)
        if len(approx_cnt) < 3:
            approx_cnt = cnt

        geojson = contour_to_polygon_geojson(approx_cnt, h, w)
        if not geojson:
            continue

        area_sqm = calculate_polygon_area(approx_cnt)
        cx, cy = calculate_centroid(approx_cnt)
        
        # Get bounding box crop for roof classification
        x, y, bw, bh = cv2.boundingRect(approx_cnt)
        
        # Average confidence inside building contour
        mask_cnt = np.zeros((h, w), dtype=np.uint8)
        cv2.drawContours(mask_cnt, [cnt], -1, 255, -1)
        cnt_conf = float(np.mean(confidence_maps["building"][mask_cnt > 0])) if np.any(mask_cnt > 0) else 0.85

        buildings.append({
            "building_index": bldg_idx,
            "geometry_geojson": geojson,
            "area_sqm": area_sqm,
            "centroid_x": cx,
            "centroid_y": cy,
            "bbox": (x, y, bw, bh),
            "confidence": round(cnt_conf, 3),
            "status": "detected"
        })
        bldg_idx += 1

    # --- Extract Road Lines (Class 2) ---
    road_mask = np.uint8(segmentation_mask == 2) * 255
    road_contours, _ = cv2.findContours(road_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    road_idx = 1
    for cnt in road_contours:
        if cv2.arcLength(cnt, False) < 40:
            continue
        
        geojson = contour_to_linestring_geojson(cnt)
        if not geojson:
            continue

        length_m = calculate_line_length(cnt)
        roads.append({
            "road_index": road_idx,
            "geometry_geojson": geojson,
            "length_m": length_m,
            "confidence": 0.82
        })
        road_idx += 1

    # --- Extract Waterbodies (Class 3) ---
    water_mask = np.uint8(segmentation_mask == 3) * 255
    water_contours, _ = cv2.findContours(water_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    water_idx = 1
    for cnt in water_contours:
        if cv2.contourArea(cnt) < 150:
            continue
        
        geojson = contour_to_polygon_geojson(cnt, h, w)
        if not geojson:
            continue

        area_sqm = calculate_polygon_area(cnt)
        waterbodies.append({
            "waterbody_index": water_idx,
            "geometry_geojson": geojson,
            "area_sqm": area_sqm,
            "confidence": 0.91
        })
        water_idx += 1

    return buildings, roads, waterbodies
