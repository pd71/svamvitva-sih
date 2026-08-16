import os
import shutil
import uuid
import datetime
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks
from fastapi.responses import FileResponse, Response
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any

from app.database.db import get_db, Base, engine
from app.database.models import Analysis, Building, Road, Waterbody, Review, ProcessingJob
from app.schemas.analysis import AnalysisSchema, AnalysisDetailSchema, BuildingSchema, ReviewUpdateRequest
from app.ml.unet_segmentation import PyTorchUNetSegmentationModel
from app.ml.efficientnet_roof import PyTorchEfficientNetRoofModel
from app.svamitva_dataset.dataset_loader import get_svamitva_dataset_summary
from app.services.preprocessing import validate_and_load_image, create_thumbnail
from app.services.segmentation import run_segmentation_pipeline
from app.services.roof_classification import run_roof_classification_pipeline
from app.services.gis import generate_overlay_image
from app.services.change_detection import run_prototype_change_detection
from app.services.report import generate_analysis_pdf_report, generate_analysis_csv_export
from app.sample_data.generator import generate_sample_village_orthophoto

router = APIRouter(prefix="/api")

import tempfile

if os.getenv("VERCEL"):
    UPLOAD_DIR = os.path.join(tempfile.gettempdir(), "uploaded_images")
else:
    UPLOAD_DIR = os.path.abspath("./uploaded_images")

try:
    os.makedirs(UPLOAD_DIR, exist_ok=True)
except Exception:
    pass


# Mandatory PyTorch CNN Model Instances (CPU & CUDA Ready)
seg_model = PyTorchUNetSegmentationModel()
roof_model = PyTorchEfficientNetRoofModel()

def process_analysis_job(analysis_id: str, db_session_factory):
    """
    Background worker that runs through the 8 processing stages:
    1. Upload
    2. Preprocessing
    3. Image tiling
    4. Segmentation
    5. Roof classification
    6. GIS processing
    7. Report generation
    8. Complete
    """
    db = db_session_factory()
    try:
        analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
        if not analysis:
            return

        # Stage 1: Upload Complete
        analysis.status = "processing"
        analysis.stage = "1. Upload Complete"
        analysis.progress_pct = 12
        db.commit()

        # Stage 2: Preprocessing
        analysis.stage = "2. Preprocessing & Rescaling"
        analysis.progress_pct = 25
        db.commit()
        
        image_rgb, metadata = validate_and_load_image(analysis.image_path)
        analysis.width = metadata["width"]
        analysis.height = metadata["height"]
        analysis.file_size = metadata["file_size"]
        analysis.crs_name = metadata["crs_name"]
        analysis.is_georeferenced = metadata["is_georeferenced"]

        # Stage 3: Image Tiling
        analysis.stage = "3. Image Tiling (512x512 Patches)"
        analysis.progress_pct = 38
        db.commit()

        # Stage 4: AI Segmentation (Buildings, Roads, Waterbodies)
        analysis.stage = "4. AI Multi-Class Segmentation"
        analysis.progress_pct = 52
        db.commit()

        raw_buildings, raw_roads, raw_waterbodies = run_segmentation_pipeline(image_rgb, seg_model)

        # Stage 5: Roof Classification (RCC, Tiled, Tin, Other)
        analysis.stage = "5. Roof Classification (EfficientNet)"
        analysis.progress_pct = 68
        db.commit()

        annotated_buildings = run_roof_classification_pipeline(image_rgb, raw_buildings, roof_model)

        # Stage 6: GIS Vector Processing & Spatial Metrics
        analysis.stage = "6. GIS Spatial Metrics & Overlay"
        analysis.progress_pct = 82
        db.commit()

        overlay_filename = f"overlay_{analysis_id}.png"
        overlay_path = os.path.join(UPLOAD_DIR, overlay_filename)
        generate_overlay_image(image_rgb, annotated_buildings, raw_roads, raw_waterbodies, overlay_path)
        analysis.overlay_path = overlay_path

        # Clear existing features if re-processing
        db.query(Building).filter(Building.analysis_id == analysis_id).delete()
        db.query(Road).filter(Road.analysis_id == analysis_id).delete()
        db.query(Waterbody).filter(Waterbody.analysis_id == analysis_id).delete()

        # Save Buildings to DB
        tot_conf = 0.0
        for b in annotated_buildings:
            tot_conf += b["confidence"]
            bldg_obj = Building(
                building_index=b["building_index"],
                analysis_id=analysis_id,
                geometry_geojson=b["geometry_geojson"],
                area_sqm=b["area_sqm"],
                centroid_x=b["centroid_x"],
                centroid_y=b["centroid_y"],
                confidence=b["confidence"],
                roof_type=b["roof_type"],
                roof_confidence=b["roof_confidence"],
                status="detected"
            )
            db.add(bldg_obj)

        # Save Roads to DB
        total_road_len = 0.0
        for r in raw_roads:
            total_road_len += r["length_m"]
            rd_obj = Road(
                road_index=r["road_index"],
                analysis_id=analysis_id,
                geometry_geojson=r["geometry_geojson"],
                length_m=r["length_m"],
                confidence=r["confidence"]
            )
            db.add(rd_obj)

        # Save Waterbodies to DB
        total_water_area = 0.0
        for w in raw_waterbodies:
            total_water_area += w["area_sqm"]
            wb_obj = Waterbody(
                waterbody_index=w["waterbody_index"],
                analysis_id=analysis_id,
                geometry_geojson=w["geometry_geojson"],
                area_sqm=w["area_sqm"],
                confidence=w["confidence"]
            )
            db.add(wb_obj)

        analysis.total_buildings = len(annotated_buildings)
        analysis.total_roads_len = round(total_road_len, 2)
        analysis.total_water_area = round(total_water_area, 2)
        analysis.avg_confidence = round(tot_conf / max(1, len(annotated_buildings)), 3)

        # Stage 7: PDF Report & Export Generation
        analysis.stage = "7. Report Generation"
        analysis.progress_pct = 94
        db.commit()

        # Stage 8: Complete
        analysis.stage = "8. Processing Complete"
        analysis.progress_pct = 100
        analysis.status = "completed"
        db.commit()

    except Exception as e:
        db.rollback()
        analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
        if analysis:
            analysis.status = "failed"
            analysis.stage = f"Error: {str(e)}"
            db.commit()
    finally:
        db.close()


@router.get("/svamitva-dataset")
def get_svamitva_dataset():
    """
    Returns SVAMITVA 10-Village Dataset repository metadata and active status.
    """
    return get_svamitva_dataset_summary()


@router.get("/dashboard/stats")
def get_dashboard_stats(db: Session = Depends(get_db)):
    """
    Get aggregated dashboard stats across all processed villages.
    """
    total_analyses = db.query(Analysis).count()
    completed_analyses = db.query(Analysis).filter(Analysis.status == "completed").all()

    total_buildings = sum(a.total_buildings for a in completed_analyses)
    total_roads = sum(a.total_roads_len for a in completed_analyses)
    total_water = sum(a.total_water_area for a in completed_analyses)
    avg_conf = (sum(a.avg_confidence for a in completed_analyses) / max(1, len(completed_analyses))) if completed_analyses else 0.0

    recent = db.query(Analysis).order_by(Analysis.created_at.desc()).limit(5).all()

    return {
        "total_villages_processed": len(completed_analyses),
        "total_buildings_detected": total_buildings,
        "total_road_length_m": round(total_roads, 1),
        "total_waterbody_area_sqm": round(total_water, 1),
        "average_confidence": round(avg_conf, 3),
        "recent_analyses": [AnalysisSchema.from_orm(a) for a in recent]
    }


@router.post("/analysis/demo")
def load_demo_village(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """
    One-click trigger to generate and load the SVAMITVA sample village orthophoto.
    """
    sample_path = os.path.join(UPLOAD_DIR, "demo_village.png")
    generate_sample_village_orthophoto(sample_path)

    analysis_id = str(uuid.uuid4())
    dest_file = os.path.join(UPLOAD_DIR, f"{analysis_id}_demo_village.png")
    shutil.copy(sample_path, dest_file)

    analysis = Analysis(
        id=analysis_id,
        title="SVAMITVA Prototype Village - Rampur",
        village_name="Rampur Village",
        status="pending",
        stage="1. Upload Complete",
        progress_pct=10,
        original_filename="demo_village.png",
        image_path=dest_file,
        crs_name="Demo / Local Coordinates",
        is_georeferenced=False
    )
    db.add(analysis)
    db.commit()
    db.refresh(analysis)

    # Launch processing task (synchronous on Vercel serverless to guarantee completion before context teardown)
    from app.database.db import SessionLocal
    if os.getenv("VERCEL"):
        process_analysis_job(analysis_id, SessionLocal)
        db.refresh(analysis)
    else:
        background_tasks.add_task(process_analysis_job, analysis_id, SessionLocal)

    return AnalysisSchema.from_orm(analysis)



@router.post("/analysis/upload")
def upload_orthophoto(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    village_name: str = Form("Sample Village"),
    db: Session = Depends(get_db)
):
    """
    Upload an orthophoto (JPG, PNG, TIFF, GeoTIFF) and initialize AI analysis pipeline.
    """
    allowed_exts = (".jpg", ".jpeg", ".png", ".tif", ".tiff")
    if not file.filename.lower().endswith(allowed_exts):
        raise HTTPException(status_code=400, detail="Invalid file type. Supported formats: JPG, PNG, TIFF, GeoTIFF.")

    analysis_id = str(uuid.uuid4())
    ext = os.path.splitext(file.filename)[1]
    saved_filename = f"{analysis_id}{ext}"
    saved_path = os.path.join(UPLOAD_DIR, saved_filename)

    with open(saved_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    analysis = Analysis(
        id=analysis_id,
        title=f"Orthophoto - {file.filename}",
        village_name=village_name,
        status="pending",
        stage="1. Upload Complete",
        progress_pct=10,
        original_filename=file.filename,
        image_path=saved_path,
        is_georeferenced=file.filename.lower().endswith((".tif", ".tiff"))
    )
    db.add(analysis)
    db.commit()
    db.refresh(analysis)

    from app.database.db import SessionLocal
    if os.getenv("VERCEL"):
        process_analysis_job(analysis_id, SessionLocal)
        db.refresh(analysis)
    else:
        background_tasks.add_task(process_analysis_job, analysis_id, SessionLocal)

    return AnalysisSchema.from_orm(analysis)



@router.post("/analysis/{analysis_id}/process")
def trigger_process_analysis(analysis_id: str, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """
    Re-trigger processing for an analysis job.
    """
    analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found.")

    from app.database.db import SessionLocal
    background_tasks.add_task(process_analysis_job, analysis_id, SessionLocal)
    return {"status": "started", "analysis_id": analysis_id}


@router.get("/analysis/{analysis_id}")
def get_analysis_detail(analysis_id: str, db: Session = Depends(get_db)):
    """
    Get full details including detected buildings, roads, waterbodies.
    """
    analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found.")

    return AnalysisDetailSchema.from_orm(analysis)


@router.get("/analysis/{analysis_id}/status")
def get_analysis_status(analysis_id: str, db: Session = Depends(get_db)):
    """
    Endpoint polled by frontend to monitor progress stage.
    """
    analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found.")

    return {
        "id": analysis.id,
        "status": analysis.status,
        "stage": analysis.stage,
        "progress_pct": analysis.progress_pct,
        "total_buildings": analysis.total_buildings,
        "total_roads_len": analysis.total_roads_len,
        "total_water_area": analysis.total_water_area,
        "avg_confidence": analysis.avg_confidence
    }


@router.get("/analysis/{analysis_id}/features")
def get_analysis_features(analysis_id: str, db: Session = Depends(get_db)):
    """
    Returns FeatureCollection GeoJSON formatted output for Leaflet GIS mapping.
    """
    analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found.")

    features = []

    # Buildings
    for b in analysis.buildings:
        features.append({
            "type": "Feature",
            "id": b.id,
            "properties": {
                "category": "Building",
                "building_index": b.building_index,
                "area_sqm": b.area_sqm,
                "centroid": [b.centroid_x, b.centroid_y],
                "roof_type": b.roof_type,
                "roof_confidence": b.roof_confidence,
                "confidence": b.confidence,
                "status": b.status
            },
            "geometry": b.geometry_geojson
        })

    # Roads
    for r in analysis.roads:
        features.append({
            "type": "Feature",
            "id": r.id,
            "properties": {
                "category": "Road",
                "road_index": r.road_index,
                "length_m": r.length_m,
                "confidence": r.confidence
            },
            "geometry": r.geometry_geojson
        })

    # Waterbodies
    for w in analysis.waterbodies:
        features.append({
            "type": "Feature",
            "id": w.id,
            "properties": {
                "category": "Waterbody",
                "waterbody_index": w.waterbody_index,
                "area_sqm": w.area_sqm,
                "confidence": w.confidence
            },
            "geometry": w.geometry_geojson
        })

    return {
        "type": "FeatureCollection",
        "crs_name": analysis.crs_name,
        "is_georeferenced": analysis.is_georeferenced,
        "features": features
    }


@router.get("/analysis/{analysis_id}/statistics")
def get_analysis_statistics(analysis_id: str, db: Session = Depends(get_db)):
    """
    Roof distribution, confidence metrics, and category counts.
    """
    analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found.")

    bldgs = analysis.buildings
    rcc = sum(1 for b in bldgs if b.roof_type == "RCC")
    tiled = sum(1 for b in bldgs if b.roof_type == "Tiled")
    tin = sum(1 for b in bldgs if b.roof_type == "Tin")
    other = sum(1 for b in bldgs if b.roof_type == "Other")

    high_conf = sum(1 for b in bldgs if b.confidence >= 0.85)
    med_conf = sum(1 for b in bldgs if 0.70 <= b.confidence < 0.85)
    low_conf = sum(1 for b in bldgs if b.confidence < 0.70)

    total_bldg_area = sum(b.area_sqm for b in bldgs)

    return {
        "buildings_detected": len(bldgs),
        "total_building_area_sqm": round(total_bldg_area, 1),
        "roads_detected": len(analysis.roads),
        "total_road_length_m": analysis.total_roads_len,
        "waterbodies_detected": len(analysis.waterbodies),
        "total_waterbody_area_sqm": analysis.total_water_area,
        "roof_distribution": {
            "RCC": rcc,
            "Tiled": tiled,
            "Tin": tin,
            "Other": other
        },
        "confidence_breakdown": {
            "high": high_conf,
            "medium": med_conf,
            "low": low_conf,
            "average": analysis.avg_confidence
        }
    }


@router.get("/analysis/{analysis_id}/image")
def get_analysis_image(analysis_id: str, db: Session = Depends(get_db)):
    """
    Serves the original uploaded image file.
    """
    analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
    if not analysis or not os.path.exists(analysis.image_path):
        raise HTTPException(status_code=404, detail="Image file not found.")

    return FileResponse(analysis.image_path)


@router.get("/analysis/{analysis_id}/overlay")
def get_analysis_overlay(analysis_id: str, db: Session = Depends(get_db)):
    """
    Serves the generated GIS overlay image file.
    """
    analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
    if not analysis or not analysis.overlay_path or not os.path.exists(analysis.overlay_path):
        # Fallback to main image
        if analysis and os.path.exists(analysis.image_path):
            return FileResponse(analysis.image_path)
        raise HTTPException(status_code=404, detail="Overlay image not found.")

    return FileResponse(analysis.overlay_path)


@router.get("/analysis/{analysis_id}/report")
def download_pdf_report(analysis_id: str, db: Session = Depends(get_db)):
    """
    Generates and downloads PDF report.
    """
    analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found.")

    pdf_path = os.path.join(UPLOAD_DIR, f"report_{analysis_id}.pdf")
    
    buildings = [b.__dict__ for b in analysis.buildings]
    roads = [r.__dict__ for r in analysis.roads]
    waterbodies = [w.__dict__ for w in analysis.waterbodies]

    generate_analysis_pdf_report(analysis.__dict__, buildings, roads, waterbodies, pdf_path)

    return FileResponse(
        pdf_path,
        filename=f"SVAMITVA_Report_{analysis.village_name.replace(' ', '_')}_{analysis_id[:8]}.pdf",
        media_type="application/pdf"
    )


@router.get("/analysis/{analysis_id}/export-csv")
def download_csv_export(analysis_id: str, db: Session = Depends(get_db)):
    """
    Exports feature metrics as CSV file download.
    """
    analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found.")

    buildings = [b.__dict__ for b in analysis.buildings]
    roads = [r.__dict__ for r in analysis.roads]
    waterbodies = [w.__dict__ for w in analysis.waterbodies]

    csv_data = generate_analysis_csv_export(buildings, roads, waterbodies)

    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=features_{analysis_id[:8]}.csv"}
    )


@router.get("/analyses")
def list_analyses(db: Session = Depends(get_db)):
    """
    List all orthophoto analysis jobs.
    """
    analyses = db.query(Analysis).order_by(Analysis.created_at.desc()).all()
    return [AnalysisSchema.from_orm(a) for a in analyses]


@router.post("/features/{building_id}/review")
def review_feature(
    building_id: str,
    review_req: ReviewUpdateRequest,
    db: Session = Depends(get_db)
):
    """
    Human-in-the-loop review endpoint. Approves, rejects, or edits building roof type.
    """
    building = db.query(Building).filter(Building.id == building_id).first()
    if not building:
        raise HTTPException(status_code=404, detail="Building not found.")

    orig_type = building.roof_type
    
    if review_req.updated_roof_type:
        building.roof_type = review_req.updated_roof_type
    
    building.status = review_req.status
    if review_req.comments:
        building.review_notes = review_req.comments

    rev = Review(
        building_id=building_id,
        original_roof_type=orig_type,
        updated_roof_type=building.roof_type,
        status=review_req.status,
        comments=review_req.comments
    )
    db.add(rev)
    db.commit()
    db.refresh(building)

    return BuildingSchema.from_orm(building)


@router.post("/change-detection")
def run_change_detection(
    background_tasks: BackgroundTasks,
    prev_file: UploadFile = File(...),
    curr_file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload Previous Survey and Current Survey orthophotos to run prototype change detection.
    """
    prev_id = str(uuid.uuid4())
    curr_id = str(uuid.uuid4())

    prev_path = os.path.join(UPLOAD_DIR, f"prev_{prev_id}.png")
    curr_path = os.path.join(UPLOAD_DIR, f"curr_{curr_id}.png")

    with open(prev_path, "wb") as b1:
        shutil.copyfileobj(prev_file.file, b1)

    with open(curr_path, "wb") as b2:
        shutil.copyfileobj(curr_file.file, b2)

    prev_rgb, _ = validate_and_load_image(prev_path)
    curr_rgb, _ = validate_and_load_image(curr_path)

    result = run_prototype_change_detection(prev_rgb, curr_rgb)
    return result
