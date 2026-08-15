import cv2
import numpy as np
from typing import Dict, Any, List

def run_prototype_change_detection(
    prev_image_rgb: np.ndarray,
    curr_image_rgb: np.ndarray
) -> Dict[str, Any]:
    """
    Prototype temporal change detection between Previous Survey and Current Survey orthophotos.
    Uses structural dissimilarity (absdiff / SSIM / thresholding) and contour tracking
    to highlight new structures, expanded buildings, and removed features.
    """
    # Resize current image to match previous if dimensions differ slightly
    hp, wp, _ = prev_image_rgb.shape
    hc, wc, _ = curr_image_rgb.shape

    if (hp, wp) != (hc, wc):
        curr_resized = cv2.resize(curr_image_rgb, (wp, hp))
    else:
        curr_resized = curr_image_rgb

    # Gray conversion
    prev_gray = cv2.cvtColor(prev_image_rgb, cv2.COLOR_RGB2GRAY)
    curr_gray = cv2.cvtColor(curr_resized, cv2.COLOR_RGB2GRAY)

    # Compute absolute difference
    diff = cv2.absdiff(curr_gray, prev_gray)
    blur_diff = cv2.GaussianBlur(diff, (7, 7), 0)
    _, thresh_diff = cv2.threshold(blur_diff, 35, 255, cv2.THRESH_BINARY)

    # Morphological cleaning
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    cleaned_diff = cv2.morphologyEx(thresh_diff, cv2.MORPH_OPEN, kernel)
    cleaned_diff = cv2.morphologyEx(cleaned_diff, cv2.MORPH_CLOSE, kernel)

    contours, _ = cv2.findContours(cleaned_diff, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    new_buildings = 0
    expanded_buildings = 0
    removed_structures = 0
    total_change_area = 0.0

    changes_geojson_list = []
    
    # Scale factor 0.25 sq m per pixel
    gsd = 0.25

    for cnt in contours:
        area_px = cv2.contourArea(cnt)
        if area_px < 60:
            continue

        area_sqm = area_px * (gsd ** 2)
        total_change_area += area_sqm

        M = cv2.moments(cnt)
        cx = float(M["m10"] / M["m00"]) if M["m00"] != 0 else 0.0
        cy = float(M["m01"] / M["m00"]) if M["m00"] != 0 else 0.0

        # Sample pixel brightness to classify change type
        mask_cnt = np.zeros((hp, wp), dtype=np.uint8)
        cv2.drawContours(mask_cnt, [cnt], -1, 255, -1)
        
        prev_mean = np.mean(prev_gray[mask_cnt > 0])
        curr_mean = np.mean(curr_gray[mask_cnt > 0])

        if curr_mean > prev_mean + 15:
            change_type = "New Building / Structure"
            new_buildings += 1
        elif curr_mean < prev_mean - 15:
            change_type = "Removed / Demolished Structure"
            removed_structures += 1
        else:
            change_type = "Expanded Building / Modified Boundary"
            expanded_buildings += 1

        pts = cnt.reshape(-1, 2)
        coords = [[float(pt[0]), float(pt[1])] for pt in pts]
        if coords[0] != coords[-1]:
            coords.append(coords[0])

        changes_geojson_list.append({
            "type": "Feature",
            "properties": {
                "change_type": change_type,
                "area_sqm": round(area_sqm, 2),
                "centroid": [round(cx, 1), round(cy, 1)]
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": [coords]
            }
        })

    return {
        "status": "success",
        "label": "Prototype Temporal Change Detection Engine",
        "new_buildings": new_buildings,
        "expanded_buildings": expanded_buildings,
        "removed_structures": removed_structures,
        "total_changed_area_sqm": round(total_change_area, 2),
        "change_features_geojson": {
            "type": "FeatureCollection",
            "features": changes_geojson_list
        }
    }
