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
            return "RCC", 0.75, {"RCC": 0.75, "Tiled": 0.10, "Tin": 0.10, "Other": 0.05}

        hsv = _rgb_to_hsv_numpy(image_crop)
        mean_h = float(np.mean(hsv[:, :, 0]))
        mean_s = float(np.mean(hsv[:, :, 1]))
        mean_v = float(np.mean(hsv[:, :, 2]))

        gray = (0.2126 * image_crop[:, :, 0] +
                0.7152 * image_crop[:, :, 1] +
                0.0722 * image_crop[:, :, 2]).astype(np.float32)
        std_dev = float(np.std(gray))

        scores = {"RCC": 0.1, "Tiled": 0.1, "Tin": 0.1, "Other": 0.1}

        if (mean_h <= 25 or mean_h >= 155) and mean_s > 45:
            scores["Tiled"] += 0.75
            scores["RCC"] += 0.1
            scores["Tin"] += 0.05
        elif (75 <= mean_h <= 125 and mean_s > 35) or (mean_v > 200 and mean_s < 30):
            scores["Tin"] += 0.75
            scores["RCC"] += 0.1
            scores["Tiled"] += 0.05
        elif mean_s <= 45 and 60 <= mean_v <= 210:
            scores["RCC"] += 0.70
            scores["Tiled"] += 0.12
            scores["Tin"] += 0.10
        else:
            scores["Other"] += 0.60
            scores["RCC"] += 0.20

        total = sum(scores.values())
        probs = {k: round(v / total, 4) for k, v in scores.items()}
        predicted_class = max(probs, key=probs.get)
        confidence = probs[predicted_class]

        return predicted_class, confidence, probs
