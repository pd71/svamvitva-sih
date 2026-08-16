import sys
import os

# Ensure backend root directory is in Python path for Vercel Serverless execution
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

import tempfile
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.database.db import Base, engine, SessionLocal
from app.api.endpoints import router as api_router
from app.sample_data.generator import generate_sample_village_orthophoto
from app.database.models import Analysis

# Create database tables safely
try:
    Base.metadata.create_all(bind=engine)
except Exception as db_err:
    print(f"Database table creation notice: {db_err}")

app = FastAPI(
    title="SVAMITVA AI Feature Extraction API",
    description="Backend API for Drone Orthophoto Feature Extraction, Multi-Class Segmentation, Roof Classification, GIS Analytics & Human Review",
    version="1.0.0"
)

# Enable CORS for Next.js / Vite frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API endpoints under all possible Vercel serverless path variations
app.include_router(api_router, prefix="")
app.include_router(api_router, prefix="/api")
app.include_router(api_router, prefix="/main.py")
app.include_router(api_router, prefix="/main.py/api")
app.include_router(api_router, prefix="/api/index.py")
app.include_router(api_router, prefix="/api/index.py/api")
app.include_router(api_router, prefix="/api/index")
app.include_router(api_router, prefix="/api/index/api")

# Serve uploaded static media files safely
if os.getenv("VERCEL"):
    UPLOAD_DIR = os.path.join(tempfile.gettempdir(), "uploaded_images")
else:
    UPLOAD_DIR = os.path.abspath("./uploaded_images")

try:
    os.makedirs(UPLOAD_DIR, exist_ok=True)
except Exception:
    pass

try:
    app.mount("/static", StaticFiles(directory=UPLOAD_DIR), name="static")
except Exception as static_err:
    print(f"Static files mount notice: {static_err}")


@app.on_event("startup")
def startup_event():
    """
    Generate sample village orthophoto on startup to ensure instant zero-setup demo experience.
    """
    try:
        sample_file = os.path.join(UPLOAD_DIR, "demo_village.png")
        generate_sample_village_orthophoto(sample_file)
    except Exception as e:
        print(f"Startup demo generation notice: {e}")

@app.get("/")
def root():
    return {
        "service": "SVAMITVA AI Feature Extraction Platform Backend",
        "status": "online",
        "team": "Nerdvana",
        "problem_id": "DJS_26_SW_08",
        "docs_url": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
