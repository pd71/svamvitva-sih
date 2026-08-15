import cv2
import numpy as np
from typing import Dict, Tuple
from app.ml.base import RoofClassificationModel

class DemoRoofClassificationModel(RoofClassificationModel):
    """
    Prototype Roof Type Classifier using color space statistics (HSV) and texture variance.
    Classifies roof patches into RCC (Concrete), Tiled (Terracotta), Tin (Corrugated Sheet), or Other.
    
    Replace with EfficientNet-B4 / ResNet50 for production deployment.
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
        """
        Input: crop image array (H, W, 3) in RGB format.
        """
        if image_crop is None or image_crop.size == 0:
            return "RCC", 0.75, {"RCC": 0.75, "Tiled": 0.10, "Tin": 0.10, "Other": 0.05}

        bgr = cv2.cvtColor(image_crop, cv2.COLOR_RGB2BGR)
        hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
        
        mean_h = np.mean(hsv[:, :, 0])
        mean_s = np.mean(hsv[:, :, 1])
        mean_v = np.mean(hsv[:, :, 2])
        
        gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
        std_dev = np.std(gray)

        # Initial scores
        scores = {"RCC": 0.1, "Tiled": 0.1, "Tin": 0.1, "Other": 0.1}

        # Red/Terracotta roof heuristic (Hue 0-25 or 155-180, high saturation)
        if (mean_h <= 25 or mean_h >= 155) and mean_s > 45:
            scores["Tiled"] += 0.75
            scores["RCC"] += 0.1
            scores["Tin"] += 0.05
        # Tin / Corrugated Sheet heuristic (Cyan/Blue hue or very high brightness metallic)
        elif (75 <= mean_h <= 125 and mean_s > 35) or (mean_v > 200 and mean_s < 30):
            scores["Tin"] += 0.75
            scores["RCC"] += 0.1
            scores["Tiled"] += 0.05
        # RCC / Concrete heuristic (Low saturation, moderate-high value, grey tone)
        elif mean_s <= 45 and 60 <= mean_v <= 210:
            scores["RCC"] += 0.70
            scores["Tiled"] += 0.12
            scores["Tin"] += 0.10
        else:
            scores["Other"] += 0.60
            scores["RCC"] += 0.20

        # Normalize probabilities
        total = sum(scores.values())
        probs = {k: round(v / total, 4) for k, v in scores.items()}

        # Pick top predicted class
        predicted_class = max(probs, key=probs.get)
        confidence = probs[predicted_class]

        return predicted_class, confidence, probs
