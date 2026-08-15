import os
import cv2
import numpy as np

def generate_sample_village_orthophoto(output_path: str = "sample_data/demo_village.png") -> str:
    """
    Generates a synthetic high-resolution aerial village drone orthophoto (1024x1024)
    containing buildings (RCC, Tiled, Tin roofs), roads, and a river waterbody.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    if os.path.exists(output_path):
        return output_path

    width, height = 1024, 1024
    
    # Base landscape (lush green grass / fields background)
    base = np.zeros((height, width, 3), dtype=np.uint8)
    base[:, :, 0] = 35 + np.random.randint(-5, 5, (height, width))  # B
    base[:, :, 1] = 110 + np.random.randint(-10, 10, (height, width)) # G
    base[:, :, 2] = 45 + np.random.randint(-5, 5, (height, width))  # R

    # Add subtle terrain noise
    noise = np.random.normal(0, 8, (height, width, 3)).astype(np.int16)
    base = np.clip(base.astype(np.int16) + noise, 0, 255).astype(np.uint8)

    # --- 1. Draw Winding Blue River (Waterbody) ---
    pts_water = np.array([
        [0, 800], [250, 750], [450, 830], [700, 780], [1024, 850],
        [1024, 980], [700, 920], [450, 960], [250, 900], [0, 940]
    ], dtype=np.int32)
    cv2.fillPoly(base, [pts_water], (210, 110, 20))  # BGR water blue
    cv2.polylines(base, [pts_water], True, (240, 130, 30), 3)

    # --- 2. Draw Main Road Network (Asphalt / Grey Roads) ---
    # Horizontal highway
    cv2.line(base, (0, 480), (1024, 480), (80, 80, 80), 36)
    cv2.line(base, (0, 480), (1024, 480), (220, 220, 220), 2)  # center dash marker
    
    # Vertical connecting road
    cv2.line(base, (512, 0), (512, 800), (80, 80, 80), 30)

    # --- 3. Draw Buildings with various Roof Types ---
    # Helper to draw a building
    def draw_building(x, y, w, h, roof_type):
        poly = np.array([[x, y], [x + w, y], [x + w, y + h], [x, y + h]], dtype=np.int32)
        if roof_type == "Tiled":
            # Terracotta Red (BGR: 30, 40, 210)
            color = (35, 45, 215)
        elif roof_type == "Tin":
            # Metallic Cyan Blue (BGR: 220, 180, 40)
            color = (220, 175, 40)
        else: # RCC
            # Concrete Light Grey (BGR: 180, 180, 180)
            color = (180, 180, 180)

        cv2.fillPoly(base, [poly], color)
        # Drop shadow
        shadow_poly = np.array([[x+6, y+h], [x+w+6, y+h], [x+w+6, y+h+8], [x+6, y+h+8]], dtype=np.int32)
        cv2.fillPoly(base, [shadow_poly], (20, 20, 20))
        # White border
        cv2.polylines(base, [poly], True, (245, 245, 245), 2)

    # Layout a realistic cluster of village houses
    bldgs = [
        # Top-Left Cluster (Tiled roofs)
        (80, 100, 90, 70, "Tiled"),
        (220, 90, 100, 80, "Tiled"),
        (100, 240, 80, 90, "Tiled"),
        (260, 230, 110, 75, "RCC"),
        
        # Top-Right Cluster (Mix RCC & Tin)
        (600, 120, 120, 85, "RCC"),
        (760, 100, 95, 110, "Tin"),
        (620, 270, 100, 90, "Tiled"),
        (780, 260, 110, 80, "RCC"),
        (910, 150, 75, 120, "Tin"),

        # Bottom-Left Cluster
        (90, 560, 110, 85, "RCC"),
        (240, 580, 95, 100, "Tiled"),
        (120, 690, 105, 80, "Tin"),

        # Bottom-Right Cluster near river
        (600, 560, 130, 90, "Tiled"),
        (770, 550, 115, 95, "RCC"),
        (620, 680, 90, 80, "Tin"),
        (760, 670, 100, 85, "Tiled"),
    ]

    for b in bldgs:
        draw_building(*b)

    # Save generated village image
    cv2.imwrite(output_path, base)
    return output_path
