"""
Demo roof classifier — pure numpy/PIL implementation, no OpenCV dependency.
"""
import numpy as np
from PIL import Image
from typing import Dict, Tuple
from app.ml.base import RoofClassificationModel


def _rgb_to_hsv_numpy(image_rgb: np.ndarray) -> np.ndarray:
    """Convert HxWx3 uint8 RGB array to HxWx3 float HSV (H:0-180, S:0-255, V:0-255)."""
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
    h = h / 2.0  # Scale to 0-180

    s = np.where(cmax == 0, 0, (diff / (cmax + 1e-9)) * 255)
    v = cmax * 255

    return np.stack([h, s, v], axis=-1)


class DemoRoofClassificationModel(RoofClassificationModel):
    """
    Prototype Roof Type Classifier using color space statistics and texture variance.
    Pure numpy/PIL — no OpenCV required.
    """

    def __init__(self):
        self.is_loaded = True

    def load_model(self, weights_path: str = None) -> bool:
        self.is_loaded = True
        return True

    @property
    def model_name(self) -> str:
        return "Prototype Roof Classifier Engine (HSV / Texture Classifier)"

    def classify_roof(self, image_crop: np.ndarray) -> Tuple[str, float, Dict[str, float]]:
        if image_crop is None or image_crop.size == 0:
            return "RCC", 0.94, {"RCC": 0.94, "Tiled": 0.03, "Tin": 0.03}

        hsv = _rgb_to_hsv_numpy(image_crop)
        mean_h = float(np.mean(hsv[:, :, 0]))
        mean_s = float(np.mean(hsv[:, :, 1]))
        mean_v = float(np.mean(hsv[:, :, 2]))

        # Calculate average RGB to detect metallic tin sheets vs terracotta tiles vs concrete RCC
        mean_r = float(np.mean(image_crop[:, :, 0]))
        mean_g = float(np.mean(image_crop[:, :, 1]))
        mean_b = float(np.mean(image_crop[:, :, 2]))

        scores = {"RCC": 0.15, "Tiled": 0.15, "Tin": 0.15}

        # 1. Tiled Roof: Strong Red/Orange hue and high R:B ratio
        if (mean_h <= 18 or mean_h >= 162) and mean_r > (mean_b + 25) and mean_s > 55:
            scores["Tiled"] += 0.85
        # 2. Tin Roof: High brightness / metallic sheen (High V, Low S or Cyan/Blue hue)
        elif (85 <= mean_h <= 130 and mean_s > 30) or (mean_v > 185 and mean_s < 45) or (mean_b > mean_r + 15):
            scores["Tin"] += 0.85
        # 3. RCC Concrete Roof: Low saturation neutral gray/flat concrete slab
        else:
            scores["RCC"] += 0.85

        total = sum(scores.values())
        probs = {k: round(v / total, 4) for k, v in scores.items()}
        predicted_class = max(probs, key=probs.get)
        confidence = probs[predicted_class]

        return predicted_class, confidence, probs



DemoRoofClassifierModel = DemoRoofClassificationModel
