"""
Demo segmentation model — pure numpy/PIL implementation, no OpenCV dependency.
"""
import numpy as np
from PIL import Image
from typing import Dict, Tuple
from app.ml.base import SegmentationModel


def _rgb_to_hsv_numpy(image_rgb: np.ndarray) -> np.ndarray:
    r = image_rgb[:, :, 0].astype(np.float32) / 255.0
    g = image_rgb[:, :, 1].astype(np.float32) / 255.0
    b = image_rgb[:, :, 2].astype(np.float32) / 255.0

    cmax = np.maximum(np.maximum(r, g), b)
    cmin = np.minimum(np.minimum(r, g), b)
    diff = cmax - cmin + 1e-9

    h = np.zeros_like(r)
    mask_r = (cmax == r)
    mask_g = (cmax == g)
    mask_b = (cmax == b)
    h[mask_r] = (60 * ((g[mask_r] - b[mask_r]) / diff[mask_r]) % 360)
    h[mask_g] = (60 * ((b[mask_g] - r[mask_g]) / diff[mask_g]) + 120)
    h[mask_b] = (60 * ((r[mask_b] - g[mask_b]) / diff[mask_b]) + 240)
    h = h / 2.0  # 0-180

    s = np.where(cmax == 0, 0.0, (diff / (cmax + 1e-9)) * 255.0)
    v = cmax * 255.0

    return np.stack([h, s, v], axis=-1)


def _in_range(hsv: np.ndarray, lo: np.ndarray, hi: np.ndarray) -> np.ndarray:
    return np.all((hsv >= lo) & (hsv <= hi), axis=-1).astype(np.uint8)


def _morphology_close(mask: np.ndarray, ksize: int = 5) -> np.ndarray:
    """Simple morphological close using PIL max/min filter."""
    from PIL import ImageFilter
    img = Image.fromarray(mask)
    dilated = img.filter(ImageFilter.MaxFilter(ksize))
    eroded = dilated.filter(ImageFilter.MinFilter(ksize))
    return np.array(eroded)


def _morphology_open(mask: np.ndarray, ksize: int = 5) -> np.ndarray:
    from PIL import ImageFilter
    img = Image.fromarray(mask)
    eroded = img.filter(ImageFilter.MinFilter(ksize))
    dilated = eroded.filter(ImageFilter.MaxFilter(ksize))
    return np.array(dilated)


class DemoSegmentationModel(SegmentationModel):
    """
    Computer-Vision powered prototype segmentation model.
    Extracts buildings, roads, and waterbodies via HSV color analysis.
    Pure numpy/PIL — no OpenCV required.
    """

    def __init__(self):
        self.is_loaded = True

    def load_model(self, weights_path: str = None) -> bool:
        self.is_loaded = True
        return True

    @property
    def model_name(self) -> str:
        return "Prototype CV Segmentation Engine (HSV / Color-Space Analysis)"

    def predict_segmentation(self, image_np: np.ndarray) -> Tuple[np.ndarray, Dict[str, np.ndarray]]:
        h, w, _ = image_np.shape
        segmentation_mask = np.zeros((h, w), dtype=np.uint8)

        hsv = _rgb_to_hsv_numpy(image_np)
        gray = (0.2126 * image_np[:, :, 0] +
                0.7152 * image_np[:, :, 1] +
                0.0722 * image_np[:, :, 2]).astype(np.float32)

        # --- 1. WATERBODY DETECTION ---
        water_mask = _in_range(hsv, np.array([90, 40, 40]), np.array([135, 255, 250]))
        dark_water = _in_range(hsv, np.array([80, 20, 20]), np.array([140, 180, 100]))
        combined_water = np.clip(water_mask + dark_water, 0, 255).astype(np.uint8)
        combined_water = _morphology_close(combined_water, 7)
        combined_water = _morphology_open(combined_water, 7)

        # --- 2. ROAD DETECTION ---
        road_candidate = _in_range(hsv, np.array([0, 0, 70]), np.array([180, 40, 200]))
        road_mask = _morphology_close(road_candidate, 5)

        # --- 3. BUILDING DETECTION ---
        tile_mask = np.clip(
            _in_range(hsv, np.array([0, 50, 50]), np.array([20, 255, 255])) +
            _in_range(hsv, np.array([160, 50, 50]), np.array([180, 255, 255])),
            0, 255
        ).astype(np.uint8)
        tin_mask = _in_range(hsv, np.array([85, 30, 180]), np.array([115, 200, 255]))
        rcc_candidate = _in_range(hsv, np.array([0, 0, 100]), np.array([180, 35, 220]))

        raw_building = np.clip(tile_mask + tin_mask + rcc_candidate, 0, 255).astype(np.uint8)
        building_mask = _morphology_close(raw_building, 5)
        building_mask = _morphology_open(building_mask, 3)

        # Precedence: water > road > building
        building_mask[combined_water > 0] = 0
        road_mask[combined_water > 0] = 0
        building_mask[road_mask > 0] = 0

        segmentation_mask[road_mask > 0] = 2
        segmentation_mask[building_mask > 0] = 1
        segmentation_mask[combined_water > 0] = 3

        rng = np.random.default_rng(42)
        confidence_maps = {
            "building": np.where(segmentation_mask == 1, 0.85 + 0.12 * rng.random((h, w)), 0.05),
            "road":     np.where(segmentation_mask == 2, 0.80 + 0.15 * rng.random((h, w)), 0.05),
            "waterbody":np.where(segmentation_mask == 3, 0.90 + 0.08 * rng.random((h, w)), 0.05),
        }

        return segmentation_mask, confidence_maps
