from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime

class BuildingSchema(BaseModel):
    id: str
    building_index: int
    analysis_id: str
    geometry_geojson: Dict[str, Any]
    area_sqm: float
    centroid_x: float
    centroid_y: float
    confidence: float
    roof_type: str
    roof_confidence: float
    status: str
    review_notes: Optional[str] = None

    class Config:
        from_attributes = True

class RoadSchema(BaseModel):
    id: str
    road_index: int
    analysis_id: str
    geometry_geojson: Dict[str, Any]
    length_m: float
    confidence: float

    class Config:
        from_attributes = True

class WaterbodySchema(BaseModel):
    id: str
    waterbody_index: int
    analysis_id: str
    geometry_geojson: Dict[str, Any]
    area_sqm: float
    confidence: float

    class Config:
        from_attributes = True

class AnalysisSchema(BaseModel):
    id: str
    title: str
    village_name: str
    status: str
    stage: str
    progress_pct: int
    original_filename: str
    image_path: str
    overlay_path: Optional[str] = None
    width: int
    height: int
    file_size: int
    crs_name: str
    is_georeferenced: bool
    total_buildings: int
    total_roads_len: float
    total_water_area: float
    avg_confidence: float
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class AnalysisDetailSchema(AnalysisSchema):
    buildings: List[BuildingSchema] = []
    roads: List[RoadSchema] = []
    waterbodies: List[WaterbodySchema] = []

class ReviewUpdateRequest(BaseModel):
    building_id: str
    updated_roof_type: Optional[str] = None
    status: str  # approved, rejected, edited
    comments: Optional[str] = None

class ChangeDetectionRequest(BaseModel):
    prev_analysis_id: Optional[str] = None
    curr_analysis_id: Optional[str] = None
