"""
Change detection pipeline — pure numpy/PIL implementation, no OpenCV dependency.
"""
import numpy as np
from PIL import Image
from typing import Dict, Any, List


def _rgb_to_gray(image_rgb: np.ndarray) -> np.ndarray:
    """Convert RGB numpy array to grayscale using luminosity formula."""
    return (0.2126 * image_rgb[:, :, 0] +
            0.7152 * image_rgb[:, :, 1] +
            0.0722 * image_rgb[:, :, 2]).astype(np.float32)


def _resize_numpy(image_rgb: np.ndarray, target_h: int, target_w: int) -> np.ndarray:
    img = Image.fromarray(image_rgb.astype(np.uint8))
    img = img.resize((target_w, target_h), Image.Resampling.LANCZOS)
    return np.array(img)


def _threshold(arr: np.ndarray, thresh: float) -> np.ndarray:
    return (arr > thresh).astype(np.uint8) * 255


def _find_changed_regions(diff_mask: np.ndarray) -> List[np.ndarray]:
    """Find bounding-box regions of changed areas using simple row/col scanning."""
    regions = []
    labeled = np.zeros_like(diff_mask, dtype=np.int32)
    label = 0
    h, w = diff_mask.shape

    visited = np.zeros_like(diff_mask, dtype=bool)
    for sy in range(h):
        for sx in range(w):
            if diff_mask[sy, sx] == 0 or visited[sy, sx]:
                continue
            label += 1
            region = []
            stack = [(sy, sx)]
            while stack:
                cy, cx = stack.pop()
                if cy < 0 or cy >= h or cx < 0 or cx >= w:
                    continue
                if visited[cy, cx] or diff_mask[cy, cx] == 0:
                    continue
                visited[cy, cx] = True
                region.append((cx, cy))
                stack.extend([(cy+1, cx), (cy-1, cx), (cy, cx+1), (cy, cx-1)])
            if len(region) > 60:
                pts = np.array(region, dtype=np.int32)
                regions.append(pts)
    return regions


def run_prototype_change_detection(
    prev_image_rgb: np.ndarray,
    curr_image_rgb: np.ndarray
) -> Dict[str, Any]:
    """
    Prototype temporal change detection between previous and current survey orthophotos.
    Uses absolute difference, thresholding, and BFS region finding — no OpenCV required.
    """
    hp, wp, _ = prev_image_rgb.shape
    hc, wc, _ = curr_image_rgb.shape

    if (hp, wp) != (hc, wc):
        curr_resized = _resize_numpy(curr_image_rgb, hp, wp)
    else:
        curr_resized = curr_image_rgb

    prev_gray = _rgb_to_gray(prev_image_rgb)
    curr_gray = _rgb_to_gray(curr_resized)

    diff = np.abs(curr_gray - prev_gray)
    # Simple box blur approximation for GaussianBlur
    from numpy.lib.stride_tricks import sliding_window_view
    try:
        padded = np.pad(diff, 3, mode='reflect')
        blurred = sliding_window_view(padded, (7, 7)).mean(axis=(-2, -1))
    except Exception:
        blurred = diff

    thresh_diff = _threshold(blurred, 35)

    regions = _find_changed_regions(thresh_diff.astype(np.uint8))

    new_buildings = 0
    expanded_buildings = 0
    removed_structures = 0
    total_change_area = 0.0
    changes_geojson_list = []
    gsd = 0.25

    for pts in regions:
        area_px = float(len(pts))
        if area_px < 60:
            continue

        area_sqm = area_px * (gsd ** 2)
        total_change_area += area_sqm

        cx = float(np.mean(pts[:, 0]))
        cy = float(np.mean(pts[:, 1]))

        # Classify change type by brightness delta at region centroid
        ys = np.clip(pts[:, 1], 0, hp - 1)
        xs = np.clip(pts[:, 0], 0, wp - 1)
        prev_mean = float(np.mean(prev_gray[ys, xs]))
        curr_mean = float(np.mean(curr_gray[ys, xs]))

        if curr_mean > prev_mean + 15:
            change_type = "New Building / Structure"
            new_buildings += 1
        elif curr_mean < prev_mean - 15:
            change_type = "Removed / Demolished Structure"
            removed_structures += 1
        else:
            change_type = "Expanded Building / Modified Boundary"
            expanded_buildings += 1

        coords = [[float(p[0]), float(p[1])] for p in pts]
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
