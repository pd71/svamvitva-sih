from abc import ABC, abstractmethod
from typing import Dict, List, Any, Tuple
import numpy as np

class MLModel(ABC):
    """Abstract base class for all AI/ML models in the pipeline."""
    
    @abstractmethod
    def load_model(self, weights_path: str = None) -> bool:
        """Load model weights or initialize model resources."""
        pass

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Return human-readable model identification."""
        pass


class SegmentationModel(MLModel):
    """
    Abstract interface for Multi-Class Semantic Segmentation Model.
    Target classes: Buildings, Roads, Waterbodies, Background.
    Production replacement: U-Net / DeepLabV3+ / SegNet trained on SVAMITVA orthophotos.
    """

    @abstractmethod
    def predict_segmentation(self, image_np: np.ndarray) -> Tuple[np.ndarray, Dict[str, np.ndarray]]:
        """
        Input: RGB image as numpy array (H, W, 3).
        Returns:
            - mask: Class index map (H, W) where 0=Background, 1=Building, 2=Road, 3=Waterbody
            - class_confidence: Dict mapping class names to confidence score maps (H, W)
        """
        pass


class RoofClassificationModel(MLModel):
    """
    Abstract interface for Roof Type Classification Model.
    Target classes: RCC (Reinforced Cement Concrete), Tiled, Tin (Corrugated Sheet), Other.
    Production replacement: EfficientNet-B4 / ResNet50 trained on cropped roof patches.
    """

    @abstractmethod
    def classify_roof(self, image_crop: np.ndarray) -> Tuple[str, float, Dict[str, float]]:
        """
        Input: Cropped building RGB patch (H, W, 3).
        Returns:
            - predicted_class: String ("RCC", "Tiled", "Tin", "Other")
            - confidence: Float confidence score (0.0 to 1.0)
            - class_probabilities: Dict mapping all classes to their probability scores
        """
        pass
