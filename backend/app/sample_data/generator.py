import os
import numpy as np
from PIL import Image, ImageDraw


def generate_sample_village_orthophoto(output_path: str = "sample_data/demo_village.png") -> str:
    """
    Generates a synthetic high-resolution aerial village drone orthophoto (1024x1024)
    containing buildings (RCC, Tiled, Tin roofs), roads, and a river waterbody.
    Pure PIL/numpy — no OpenCV dependency.
    """
    try:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
    except Exception:
        pass

    if os.path.exists(output_path):
        return output_path

    width, height = 1024, 1024

    # Base landscape — lush green fields
    base = np.zeros((height, width, 3), dtype=np.uint8)
    rng = np.random.default_rng(42)
    base[:, :, 0] = np.clip(45  + rng.integers(-5, 5, (height, width)), 0, 255)   # R
    base[:, :, 1] = np.clip(110 + rng.integers(-10, 10, (height, width)), 0, 255) # G
    base[:, :, 2] = np.clip(35  + rng.integers(-5, 5, (height, width)), 0, 255)   # B

    img = Image.fromarray(base, mode='RGB')
    draw = ImageDraw.Draw(img)

    # 1. Draw River (Waterbody)
    water_pts = [
        (0, 800), (250, 750), (450, 830), (700, 780), (1024, 850),
        (1024, 980), (700, 920), (450, 960), (250, 900), (0, 940)
    ]
    draw.polygon(water_pts, fill=(30, 110, 210))
    draw.line(water_pts + [water_pts[0]], fill=(0, 140, 255), width=3)

    # 2. Draw Roads
    draw.rectangle([0, 462, 1024, 498], fill=(80, 80, 80))       # Horizontal
    draw.line([(0, 480), (1024, 480)], fill=(220, 220, 220), width=2)  # Centre dash
    draw.rectangle([497, 0, 527, 800], fill=(80, 80, 80))         # Vertical

    # 3. Draw Buildings
    roof_colors = {
        "Tiled": (215, 45, 35),    # Terracotta Red
        "Tin":   (40, 175, 220),   # Metallic Cyan
        "RCC":   (180, 180, 180),  # Concrete Grey
    }

    def draw_building(x, y, w, h, roof_type):
        color = roof_colors.get(roof_type, (160, 160, 160))
        # Shadow
        draw.rectangle([x+5, y+h, x+w+5, y+h+8], fill=(20, 20, 20))
        # Roof fill
        draw.rectangle([x, y, x+w, y+h], fill=color)
        # White border
        draw.rectangle([x, y, x+w, y+h], outline=(245, 245, 245), width=2)

    bldgs = [
        (80, 100, 90, 70, "Tiled"),  (220, 90, 100, 80, "Tiled"),
        (100, 240, 80, 90, "Tiled"), (260, 230, 110, 75, "RCC"),
        (600, 120, 120, 85, "RCC"),  (760, 100, 95, 110, "Tin"),
        (620, 270, 100, 90, "Tiled"),(780, 260, 110, 80, "RCC"),
        (910, 150, 75, 120, "Tin"),
        (90, 560, 110, 85, "RCC"),   (240, 580, 95, 100, "Tiled"),
        (120, 690, 105, 80, "Tin"),
        (600, 560, 130, 90, "Tiled"),(770, 550, 115, 95, "RCC"),
        (620, 680, 90, 80, "Tin"),   (760, 670, 100, 85, "Tiled"),
    ]
    for b in bldgs:
        draw_building(*b)

    try:
        img.save(output_path)
    except Exception:
        # If output path isn't writable (e.g. Vercel /tmp issue), skip silently
        pass

    return output_path
