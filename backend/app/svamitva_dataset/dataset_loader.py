import os
import json
from typing import Dict, Any
from app.svamitva_dataset.gis_rasterizer import inspect_svamitva_repository

def get_svamitva_dataset_summary() -> Dict[str, Any]:
    """
    Returns actual information regarding SVAMITVA SIH 2024 dataset repository:
    - State / Source: svamitva.nic.in
    - Image count, Vector count, Resolution, CRS
    - Available classes
    - Manual download instructions if direct HTTP GET returned 404
    """
    report = inspect_svamitva_repository()
    return report
