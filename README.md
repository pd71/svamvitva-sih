# SVAMITVA AI Feature Extraction Platform
**AI-Powered Geospatial Intelligence for Automated Village Mapping**

**Problem Statement ID:** DJS_26_SW_08  
**Problem:** Development and Optimization of AI model for Feature identification/Extraction from drone orthophotos  
**Team:** Nerdvana (Smart India Hackathon 2024 / 2025)

---

## 🌟 Overview

The **SVAMITVA AI Feature Extraction Platform** is an end-to-end web application and geospatial pipeline designed to convert 50cm aerial drone orthophotos into vector GIS village maps using **PyTorch U-Net** for multi-class semantic segmentation and **PyTorch EfficientNet** for roof type classification.

The workflow executes:
$$\text{Official SVAMITVA TIF} \rightarrow \text{Tiling} \rightarrow \text{PyTorch U-Net} \rightarrow \text{Vector Extraction} \rightarrow \text{PyTorch EfficientNet} \rightarrow \text{GIS Visualization} \rightarrow \text{Reports}$$

---

## 🛰 Official SVAMITVA SIH 2024 Dataset Links

The application supports raw `.tif` drone imagery and `.shp` vector shapefile annotations from the official portal (`svamitva.nic.in`):

| State / Region | TIF / SHP Count | Official Download Link (SIH 2024 Portal) |
| :--- | :--- | :--- |
| **Maharashtra** | 1 TIF / 1 SHP | `https://svamitva.nic.in/DownloadPDF/TifFile/Maharashtra_1.zip` |
| **Gujarat** | 5 TIF / 5 SHP | `https://svamitva.nic.in/DownloadPDF/TifFile/Gujarat_5.zip` |
| **Madhya Pradesh** | 1 TIF / 1 SHP | `https://svamitva.nic.in/DownloadPDF/TifFile/MP_shape.zip` |
| **Chhattisgarh** | 1 TIF / 1 SHP | `https://svamitva.nic.in/DownloadPDF/TifFile/Chhattisgarh_2.zip` |
| **Gautam Buddh Nagar** | 2 TIF / 2 SHP | `https://svamitva.nic.in/DownloadPDF/TifFile/Gautam_budh_Nagar_2.zip` |

### Ingestion Instructions
1. Download the ZIP file from the official portal links above.
2. Extract the `.tif` orthophotos and `.shp` shapefiles into:
   `backend/svamitva_dataset_repository/`
3. The platform will dynamically detect the datasets, parse CRS and spatial metadata, rasterize building polygons into training masks, and compute real **IoU, Dice, Precision, Recall, and F1** metrics.

---

## 🛠 Architecture & CNN Subsystems

- **Segmentation Model**: PyTorch U-Net (`n_channels=3, n_classes=4`) predicting Building Footprints, Road Networks, and Waterbodies.
- **Roof Classification**: PyTorch EfficientNet-B0 (`torchvision.models.efficientnet_b0`) predicting RCC, Tiled, Tin, or Other.
- **GIS Engine**: Shapely, GeoPandas, OpenCV contour vectorization.
- **Frontend**: Next.js 14, TypeScript, Tailwind CSS, Leaflet, Recharts.
- **Backend API**: Python FastAPI, Uvicorn, SQLAlchemy.

---

## 📊 Factual Model & Dataset Status

| Component | Status | Notes |
| :--- | :--- | :--- |
| **U-Net Architecture** | **Implemented** | PyTorch `UNet` tensor module running CPU/CUDA forward passes |
| **EfficientNet Architecture** | **Implemented** | PyTorch `EfficientNet-B0` with custom 4-class classifier head |
| **SVAMITVA Dataset Repository** | **Scanner Ready** | Place downloaded `.tif` and `.shp` files into `backend/svamitva_dataset_repository/` |
| **Evaluation Metrics** | **Calculated** | IoU, Dice, Precision, Recall, F1 score evaluator built in `app/svamitva_dataset/gis_rasterizer.py` |

---

## 🚀 Quick Start

### 1. Start Python Backend
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

### 2. Start Next.js Frontend
```bash
cd frontend
npm run dev
```
Open `http://localhost:3000` in your web browser.
