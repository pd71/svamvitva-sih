import numpy as np
from typing import List, Tuple

def create_tiles(image_rgb: np.ndarray, tile_size: int = 512, overlap: int = 64) -> List[Tuple[np.ndarray, int, int, int, int]]:
    """
    Tiles large drone orthophotos into overlapping patches for deep learning / CV processing.
    Returns list of (patch_np, y_start, y_end, x_start, x_end).
    """
    h, w, c = image_rgb.shape
    stride = tile_size - overlap
    tiles = []

    for y in range(0, h, stride):
        for x in range(0, w, stride):
            y_end = min(y + tile_size, h)
            x_end = min(x + tile_size, w)
            y_start = max(0, y_end - tile_size)
            x_start = max(0, x_end - tile_size)

            tile_crop = image_rgb[y_start:y_end, x_start:x_end]
            tiles.append((tile_crop, y_start, y_end, x_start, x_end))

    return tiles
