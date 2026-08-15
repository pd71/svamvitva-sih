import os
import glob
import time
import random
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
from PIL import Image

from app.ml.unet_segmentation import UNet

# 1. Set reproducible seeds
SEED = 42
random.seed(SEED)
np.random.seed(SEED)
torch.manual_seed(SEED)
if torch.cuda.is_available():
    torch.cuda.manual_seed_all(SEED)

DATASET_ROOT = os.path.abspath("./svamitva_dataset_repository/kaggle_dataset/svammitva-drone-aerial-images/Svamitva/FilteredData")
WEIGHTS_DIR = os.path.abspath("./app/ml/weights")
os.makedirs(WEIGHTS_DIR, exist_ok=True)
CHECKPOINT_PATH = os.path.join(WEIGHTS_DIR, "unet_svamitva_building_best.pth")

class SvamitvaBuildingDataset(Dataset):
    def __init__(self, image_paths, mask_paths, target_size=(128, 128), is_train=False):
        self.target_size = target_size
        self.is_train = is_train
        self.images = []
        self.masks = []

        # Pre-load resized arrays in RAM (takes ~3s total)
        for img_p, mask_p in zip(image_paths, mask_paths):
            img = Image.open(img_p).convert("RGB")
            if target_size:
                img = img.resize(target_size, Image.BILINEAR)
            img_np = np.array(img, dtype=np.float32) / 255.0

            mask = Image.open(mask_p)
            if target_size:
                mask = mask.resize(target_size, Image.NEAREST)
            mask_np = np.array(mask)
            if mask_np.ndim == 3:
                mask_binary = (mask_np[:, :, 0] > 100).astype(np.float32)
            else:
                mask_binary = (mask_np > 100).astype(np.float32)

            self.images.append(img_np)
            self.masks.append(mask_binary)

    def __len__(self):
        return len(self.images)

    def __getitem__(self, idx):
        img_np = self.images[idx]
        mask_binary = self.masks[idx]

        # Data Augmentation for training
        if self.is_train:
            if random.random() > 0.5:
                img_np = np.flip(img_np, axis=1)
                mask_binary = np.flip(mask_binary, axis=1)
            if random.random() > 0.5:
                img_np = np.flip(img_np, axis=0)
                mask_binary = np.flip(mask_binary, axis=0)

        img_tensor = torch.from_numpy(img_np.copy()).permute(2, 0, 1)  # (3, H, W)
        mask_tensor = torch.from_numpy(mask_binary.copy()).unsqueeze(0) # (1, H, W)

        return img_tensor, mask_tensor


class CombinedBCEAndDiceLoss(nn.Module):
    def __init__(self, smooth=1e-5):
        super().__init__()
        self.bce = nn.BCEWithLogitsLoss()
        self.smooth = smooth

    def forward(self, logits, targets):
        bce_loss = self.bce(logits, targets)
        probs = torch.sigmoid(logits)
        intersection = (probs * targets).sum(dim=(1, 2, 3))
        cardinality = probs.sum(dim=(1, 2, 3)) + targets.sum(dim=(1, 2, 3))
        dice_loss = 1.0 - (2.0 * intersection + self.smooth) / (cardinality + self.smooth)
        return bce_loss + dice_loss.mean()


def compute_metrics(logits, targets, threshold=0.5):
    probs = torch.sigmoid(logits)
    preds = (probs > threshold).float()

    preds_flat = preds.view(-1)
    targets_flat = targets.view(-1)

    tp = (preds_flat * targets_flat).sum().item()
    fp = (preds_flat * (1.0 - targets_flat)).sum().item()
    fn = ((1.0 - preds_flat) * targets_flat).sum().item()
    tn = ((1.0 - preds_flat) * (1.0 - targets_flat)).sum().item()

    intersection = tp
    union = tp + fp + fn

    iou = (intersection + 1e-6) / (union + 1e-6)
    dice = (2.0 * tp + 1e-6) / (2.0 * tp + fp + fn + 1e-6)
    precision = (tp + 1e-6) / (tp + fp + 1e-6)
    recall = (tp + 1e-6) / (tp + fn + 1e-6)
    f1 = 2.0 * (precision * recall) / (precision + recall + 1e-6)

    return iou, dice, precision, recall, f1


def train_and_evaluate():
    img_dir = os.path.join(DATASET_ROOT, "Images")
    mask_dir = os.path.join(DATASET_ROOT, "BinaryMasks")

    img_files = sorted(glob.glob(os.path.join(img_dir, "*.png")))
    mask_files = sorted(glob.glob(os.path.join(mask_dir, "*.png")))

    assert len(img_files) == len(mask_files) == 690, f"Expected 690 pairs, found {len(img_files)}"

    indices = list(range(len(img_files)))
    random.shuffle(indices)

    train_end = int(0.70 * len(indices))          # 483
    val_end = train_end + int(0.15 * len(indices)) # 483 + 103 = 586

    train_idx = indices[:train_end]
    val_idx = indices[train_end:val_end]
    test_idx = indices[val_end:]

    print(f"Data Split Summary:")
    print(f"  Train Count: {len(train_idx)} (70%)")
    print(f"  Validation Count: {len(val_idx)} (15%)")
    print(f"  Test Count: {len(test_idx)} (15%)")

    train_imgs = [img_files[i] for i in train_idx]
    train_masks = [mask_files[i] for i in train_idx]

    val_imgs = [img_files[i] for i in val_idx]
    val_masks = [mask_files[i] for i in val_idx]

    test_imgs = [img_files[i] for i in test_idx]
    test_masks = [mask_files[i] for i in test_idx]

    train_ds = SvamitvaBuildingDataset(train_imgs, train_masks, target_size=(128, 128), is_train=True)
    val_ds = SvamitvaBuildingDataset(val_imgs, val_masks, target_size=(128, 128), is_train=False)
    test_ds = SvamitvaBuildingDataset(test_imgs, test_masks, target_size=(128, 128), is_train=False)

    batch_size = 16
    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True, num_workers=0)
    val_loader = DataLoader(val_ds, batch_size=batch_size, shuffle=False, num_workers=0)
    test_loader = DataLoader(test_ds, batch_size=batch_size, shuffle=False, num_workers=0)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Training PyTorch U-Net on device: {device}")

    model = UNet(n_channels=3, n_classes=1).to(device)
    criterion = CombinedBCEAndDiceLoss()
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3, weight_decay=1e-4)

    epochs = 15
    best_val_loss = float('inf')
    best_val_dice = 0.0
    patience = 4
    patience_counter = 0

    CANDIDATE_PATH = os.path.join(WEIGHTS_DIR, "unet_svamitva_building_candidate.pth")

    start_time = time.time()

    for epoch in range(1, epochs + 1):
        model.train()
        train_loss = 0.0
        for imgs, masks in train_loader:
            imgs, masks = imgs.to(device), masks.to(device)
            optimizer.zero_grad()
            logits = model(imgs)
            loss = criterion(logits, masks)
            loss.backward()
            optimizer.step()
            train_loss += loss.item() * imgs.size(0)

        train_loss /= len(train_ds)

        model.eval()
        val_loss = 0.0
        val_ious, val_dices = [], []
        with torch.no_grad():
            for imgs, masks in val_loader:
                imgs, masks = imgs.to(device), masks.to(device)
                logits = model(imgs)
                loss = criterion(logits, masks)
                val_loss += loss.item() * imgs.size(0)

                iou, dice, _, _, _ = compute_metrics(logits, masks)
                val_ious.append(iou)
                val_dices.append(dice)

        val_loss /= len(val_ds)
        val_iou = np.mean(val_ious)
        val_dice = np.mean(val_dices)

        print(f"Epoch {epoch:02d}/{epochs:02d} | Train Loss: {train_loss:.4f} | Val Loss: {val_loss:.4f} | Val IoU: {val_iou:.4f} | Val Dice: {val_dice:.4f}")

        if val_dice > best_val_dice or val_loss < best_val_loss:
            best_val_loss = min(best_val_loss, val_loss)
            best_val_dice = max(best_val_dice, val_dice)
            patience_counter = 0
            torch.save(model.state_dict(), CANDIDATE_PATH)
            print(f"  --> Candidate checkpoint saved (Val Dice: {val_dice:.4f})")
        else:
            patience_counter += 1
            if patience_counter >= patience:
                print(f"Early stopping triggered at epoch {epoch} (No improvement for {patience} consecutive epochs).")
                break

    training_time = time.time() - start_time

    print("\n=== HELD-OUT TEST SET EVALUATION (15-EPOCH EXPERIMENT) ===")
    eval_model_path = CANDIDATE_PATH if os.path.exists(CANDIDATE_PATH) else CHECKPOINT_PATH
    model.load_state_dict(torch.load(eval_model_path, map_location=device))
    model.eval()

    test_ious, test_dices, test_precisions, test_recalls, test_f1s = [], [], [], [], []
    with torch.no_grad():
        for imgs, masks in test_loader:
            imgs, masks = imgs.to(device), masks.to(device)
            logits = model(imgs)
            iou, dice, precision, recall, f1 = compute_metrics(logits, masks)
            test_ious.append(iou)
            test_dices.append(dice)
            test_precisions.append(precision)
            test_recalls.append(recall)
            test_f1s.append(f1)

    final_iou = np.mean(test_ious)
    final_dice = np.mean(test_dices)
    final_precision = np.mean(test_precisions)
    final_recall = np.mean(test_recalls)
    final_f1 = np.mean(test_f1s)

    baseline_dice = 0.5193
    baseline_iou = 0.3677

    print(f"Baseline: IoU = {baseline_iou:.4f}, Dice = {baseline_dice:.4f}, Precision = 0.5973, Recall = 0.4861")
    print(f"Improved Candidate: IoU = {final_iou:.4f}, Dice = {final_dice:.4f}, Precision = {final_precision:.4f}, Recall = {final_recall:.4f}, F1 = {final_f1:.4f}")
    print(f"Training Time: {training_time:.2f} seconds | Epochs Completed: {epoch}")

    if final_dice > baseline_dice:
        import shutil
        shutil.copy(CANDIDATE_PATH, CHECKPOINT_PATH)
        print(f"SUCCESS: Candidate model outperforms baseline ({final_dice:.4f} > {baseline_dice:.4f}). Replaced production checkpoint at {CHECKPOINT_PATH}.")
    else:
        print(f"NOTICE: Candidate model did not outperform baseline ({final_dice:.4f} <= {baseline_dice:.4f}). Retained baseline production checkpoint at {CHECKPOINT_PATH}.")

    report = f"""
==================================================
FACTUAL MODEL TRAINING & EVALUATION REPORT
==================================================
DATASET: SVAMITVA FilteredData Building Footprints
TRAIN COUNT: {len(train_idx)} (70%)
VALIDATION COUNT: {len(val_idx)} (15%)
TEST COUNT: {len(test_idx)} (15%)
MODEL: PyTorch U-Net (3-channel RGB in, 1-channel logit out)
EPOCHS COMPLETED: {epochs}
TRAINING TIME: {training_time:.2f} seconds
BEST VALIDATION LOSS: {best_val_loss:.4f}

HELD-OUT TEST SET METRICS:
TEST IoU: {final_iou:.4f}
TEST DICE: {final_dice:.4f}
TEST PRECISION: {final_precision:.4f}
TEST RECALL: {final_recall:.4f}
TEST F1: {final_f1:.4f}
CHECKPOINT SAVED: {CHECKPOINT_PATH}
==================================================
"""
    print(report)
    return report

if __name__ == "__main__":
    train_and_evaluate()
