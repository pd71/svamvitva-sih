import numpy as np
from PIL import Image
from typing import Dict, Tuple
from app.ml.base import RoofClassificationModel


try:
    import torch
    import torch.nn as nn
    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False
    class nn:
        class Module:
            pass

try:
    import torchvision.models as models
    import torchvision.transforms as transforms
    HAS_TORCHVISION = True
except ImportError:
    HAS_TORCHVISION = False

class PyTorchEfficientNetRoofModel(RoofClassificationModel):
    """
    Mandatory PyTorch EfficientNet Roof Type Classifier.
    Evaluates cropped building RGB patches through EfficientNet neural network
    to predict RCC (Concrete), Tiled (Terracotta), Tin (Corrugated Sheet), or Other.
    """

    CLASSES = ["RCC", "Tiled", "Tin", "Other"]

    def __init__(self, weights_path: str = None):
        self.weights_loaded = False
        
        if not HAS_TORCH:
            print("PyTorch not installed in environment, using lightweight CV roof classifier.")
            return

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        if HAS_TORCHVISION:
            self.net = models.efficientnet_b0(weights=None)
            in_features = self.net.classifier[1].in_features
            self.net.classifier[1] = nn.Linear(in_features, len(self.CLASSES))
        else:
            # Lightweight custom CNN fallback head
            self.net = nn.Sequential(
                nn.Conv2d(3, 32, kernel_size=3, padding=1),
                nn.BatchNorm2d(32),
                nn.ReLU(),
                nn.AdaptiveAvgPool2d((1, 1)),
                nn.Flatten(),
                nn.Linear(32, len(self.CLASSES))
            )
        self.net.to(self.device)
        self.net.eval()

        import os
        if os.getenv("VERCEL"):
            import tempfile
            default_weights = os.path.join(tempfile.gettempdir(), "efficientnet_svamitva_roof_best.pth")
        else:
            default_weights = os.path.abspath("./app/ml/weights/efficientnet_svamitva_roof_best.pth")

        target_weights = weights_path if (weights_path and os.path.exists(weights_path)) else default_weights

        # Auto-download from Hugging Face Model Hub if missing
        if not os.path.exists(target_weights):
            repo_id = os.getenv("HF_MODEL_REPO_EFFICIENTNET", "holypreet/svamitva-unet-weights")
            filename = "efficientnet_svamitva_roof_best.pth"
            try:
                os.makedirs(os.path.dirname(target_weights), exist_ok=True)
                from huggingface_hub import hf_hub_download
                print(f"Downloading EfficientNet roof model from HF Hub ({repo_id}/{filename})...")
                hf_token = os.getenv("HF_TOKEN", None)
                downloaded_file = hf_hub_download(repo_id=repo_id, filename=filename, token=hf_token)
                import shutil
                shutil.copy(downloaded_file, target_weights)

            except Exception as dl_err:
                print(f"EfficientNet HF Hub auto-download notice: {dl_err}")

        if os.path.exists(target_weights):
            self.load_model(target_weights)


    def load_model(self, weights_path: str = None) -> bool:
        if not HAS_TORCH or not hasattr(self, 'net'):
            return False
        try:
            state_dict = torch.load(weights_path, map_location=self.device)
            self.net.load_state_dict(state_dict)
            self.weights_loaded = True
            return True
        except Exception as e:
            print(f"Could not load EfficientNet weights from {weights_path}: {e}")
            return False

    @property
    def model_name(self) -> str:
        status = "SVAMITVA-Trained Weights" if self.weights_loaded else "Demo Checkpoint (PyTorch CPU Ready)"
        return f"PyTorch EfficientNet-B0 Neural Network [{status}]"

    def classify_roof(self, image_crop: np.ndarray) -> Tuple[str, float, Dict[str, float]]:
        """
        Input: crop image array (H, W, 3) in RGB format.
        Returns: (predicted_class, confidence, probabilities_dict)
        """
        if not HAS_TORCH or not hasattr(self, 'net'):
            from app.ml.demo_roof_classifier import DemoRoofClassificationModel
            return DemoRoofClassificationModel().classify_roof(image_crop)

        if image_crop is None or image_crop.size == 0:
            return "Other", 0.5, {c: 0.25 for c in self.CLASSES}

        try:
            pil_crop = Image.fromarray(image_crop.astype(np.uint8)).resize((128, 128), Image.Resampling.LANCZOS)
            resized = np.array(pil_crop)
            tensor = torch.from_numpy(resized.astype(np.float32) / 255.0).permute(2, 0, 1)
            mean = torch.tensor([0.485, 0.456, 0.406]).view(3, 1, 1)
            std = torch.tensor([0.229, 0.224, 0.225]).view(3, 1, 1)
            tensor = ((tensor - mean) / std).unsqueeze(0).to(self.device)


            with torch.no_grad():
                logits = self.net(tensor)
                probs = torch.softmax(logits, dim=1).squeeze().cpu().numpy()
                pred_idx = int(np.argmax(probs))
                predicted_class = self.CLASSES[pred_idx]
                confidence = float(probs[pred_idx])

                prob_dict = {self.CLASSES[i]: float(probs[i]) for i in range(len(self.CLASSES))}
                return predicted_class, confidence, prob_dict
        except Exception as e:
            print(f"Error in EfficientNet roof classification: {e}")
            from app.ml.demo_roof_classifier import DemoRoofClassificationModel
            return DemoRoofClassificationModel().classify_roof(image_crop)
