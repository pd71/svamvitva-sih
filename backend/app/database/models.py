import datetime
import uuid
from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, ForeignKey, JSON, Text
from sqlalchemy.orm import relationship
from app.database.db import Base

class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False, default="Village Orthophoto Analysis")
    village_name = Column(String, default="Sample Village")
    status = Column(String, default="pending")  # pending, processing, completed, failed
    stage = Column(String, default="Upload")    # 1. Upload, 2. Preprocessing, 3. Tiling, 4. Segmentation, 5. Roof classification, 6. GIS processing, 7. Report generation, 8. Complete
    progress_pct = Column(Integer, default=0)
    original_filename = Column(String, nullable=False)
    image_path = Column(String, nullable=False)
    overlay_path = Column(String, nullable=True)
    width = Column(Integer, default=0)
    height = Column(Integer, default=0)
    file_size = Column(Integer, default=0)
    crs_name = Column(String, default="Demo / Local Coordinates")
    is_georeferenced = Column(Boolean, default=False)
    
    total_buildings = Column(Integer, default=0)
    total_roads_len = Column(Float, default=0.0)
    total_water_area = Column(Float, default=0.0)
    avg_confidence = Column(Float, default=0.0)
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    buildings = relationship("Building", back_populates="analysis", cascade="all, delete-orphan")
    roads = relationship("Road", back_populates="analysis", cascade="all, delete-orphan")
    waterbodies = relationship("Waterbody", back_populates="analysis", cascade="all, delete-orphan")
    jobs = relationship("ProcessingJob", back_populates="analysis", cascade="all, delete-orphan")


class Building(Base):
    __tablename__ = "buildings"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    building_index = Column(Integer, nullable=False)
    analysis_id = Column(String, ForeignKey("analyses.id"), nullable=False)
    geometry_geojson = Column(JSON, nullable=False)
    area_sqm = Column(Float, default=0.0)
    centroid_x = Column(Float, default=0.0)
    centroid_y = Column(Float, default=0.0)
    confidence = Column(Float, default=0.0)
    roof_type = Column(String, default="RCC") # RCC, Tiled, Tin, Other
    roof_confidence = Column(Float, default=0.0)
    status = Column(String, default="detected") # detected, approved, rejected, edited
    review_notes = Column(Text, nullable=True)

    analysis = relationship("Analysis", back_populates="buildings")
    reviews = relationship("Review", back_populates="building", cascade="all, delete-orphan")


class Road(Base):
    __tablename__ = "roads"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    road_index = Column(Integer, nullable=False)
    analysis_id = Column(String, ForeignKey("analyses.id"), nullable=False)
    geometry_geojson = Column(JSON, nullable=False)
    length_m = Column(Float, default=0.0)
    confidence = Column(Float, default=0.0)

    analysis = relationship("Analysis", back_populates="roads")


class Waterbody(Base):
    __tablename__ = "waterbodies"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    waterbody_index = Column(Integer, nullable=False)
    analysis_id = Column(String, ForeignKey("analyses.id"), nullable=False)
    geometry_geojson = Column(JSON, nullable=False)
    area_sqm = Column(Float, default=0.0)
    confidence = Column(Float, default=0.0)

    analysis = relationship("Analysis", back_populates="waterbodies")


class ProcessingJob(Base):
    __tablename__ = "processing_jobs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    analysis_id = Column(String, ForeignKey("analyses.id"), nullable=False)
    stage = Column(String, nullable=False)
    progress_pct = Column(Integer, default=0)
    status = Column(String, default="running") # running, completed, failed
    log_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    analysis = relationship("Analysis", back_populates="jobs")


class Review(Base):
    __tablename__ = "reviews"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    building_id = Column(String, ForeignKey("buildings.id"), nullable=False)
    original_roof_type = Column(String, nullable=False)
    updated_roof_type = Column(String, nullable=False)
    status = Column(String, nullable=False) # approved, rejected, edited
    comments = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    building = relationship("Building", back_populates="reviews")
