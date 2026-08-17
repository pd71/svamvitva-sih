# SVAMITVA AI Feature Extraction Platform
**AI-Powered Geospatial Intelligence for Automated Village Mapping**

**Problem Statement ID:** DJS_26_SW_08  
**Problem:** Development and Optimization of AI model for Feature identification/Extraction from drone orthophotos  
**Team:** Nerdvana (Smart India Hackathon 2024 / 2025)

---

## 🌟 Executive Summary & Workflow

The **SVAMITVA AI Feature Extraction Platform** is an end-to-end web application and geospatial AI pipeline designed to convert 50cm aerial drone orthophotos into vector GIS village maps. It leverages **PyTorch U-Net** for multi-class semantic segmentation, **PyTorch EfficientNet-B0** for roof type classification, custom **GIS vectorization algorithms**, and a **multitemporal change detection engine**.

$$\text{Official SVAMITVA TIF} \xrightarrow{\text{Tiling \& Preprocessing}} \text{PyTorch U-Net} \xrightarrow{\text{Contour Vectorization}} \text{PyTorch EfficientNet} \xrightarrow{\text{GIS Visualization \& Metrics}} \text{Executive Reports}$$

---

## 📊 PPT Slide-Ready Executive Summary

> [!TIP]
> **Copy-paste ready bullet points for presentation slides, pitch decks, and technical summaries.**

### 🖥️ Slide 1: Deep Learning Architectures & Training Pipeline
- **Multi-Class Semantic Segmentation (PyTorch U-Net)**:
  - 4-Class Deep Encoder-Decoder CNN with skip connections predicting **Background**, **Building Footprints**, **Road Networks**, and **Waterbodies**.
  - Reflective tensor padding & multi-scale downsampling to process ultra-high resolution drone orthophotos seamlessly.
- **Roof Material Classification (PyTorch EfficientNet-B0)**:
  - Deep CNN with Compound Scaling fine-tuned via Transfer Learning to classify cropped building patches into 4 structural types: **RCC (Concrete)**, **Tiled (Terracotta)**, **Tin (Corrugated Sheet)**, and **Other**.
- **Loss Function & Optimization**:
  - Trained using **Combined BCE + Dice Loss** with **AdamW** optimizer ($\eta = 10^{-3}$, weight decay $= 10^{-4}$) on a 70/15/15 split of 690 annotated SVAMITVA drone imagery tiles.
- **Model Weight Hub**: Production weights synced live from **Hugging Face Model Hub** (`holypreet/svamitva-unet-weights`).

### 🗺️ Slide 2: GIS Vectorization & Spatial Analytics
- **Contour Vectorization Algorithm**:
  - Extracts smooth connected boundary polygons from raster segmentation masks into GIS-standard **GeoJSON Polygons & LineStrings** using OpenCV `findContours` and SciPy connected components fallbacks.
- **Shoelace Polygon Area Calculation**:
  - Implements Gauss’s Area Formula scaled by Ground Sampling Distance ($\text{GSD} = 0.25\text{m--}0.50\text{m/px}$) to derive real-world surface area in $m^2$.
- **Euclidean Polyline Integration**:
  - Calculates continuous road network polyline lengths in meters across coordinate vertices.
- **HSV Spectral Refinement**:
  - Uses Hue-Saturation-Value color space decomposition ($H \in [0^\circ, 360^\circ], S, V$) for fine-grained boundary alignment across high-reflectance roads and water absorption bands.

### 🔄 Slide 3: Multitemporal Change Detection & Report Engine
- **Grayscale Luminosity Reduction**:
  - Converts multi-date survey orthophotos using standard weighted luminosity ($Y = 0.2126R + 0.7152G + 0.0722B$).
- **Sliding-Window Noise Reduction**:
  - 7x7 spatial moving-average blur filter eliminating high-frequency shadow variations and environmental artifacts.
- **BFS Delta Classification**:
  - Breadth-First Search connected region algorithm categorizing spatial deltas into **New Buildings ($\Delta Y > +15$)**, **Demolished Structures ($\Delta Y < -15$)**, and **Modified Boundaries**.
- **Automated PDF & CSV Generation**:
  - Instant executive report generation via ReportLab PDF engine and structured CSV inventory export.

---

## 🔬 Deep Technical Breakdown of Algorithms & Mathematics

### 1. PyTorch Multi-Class U-Net Segmentation Architecture
- **Encoder Path**: 4 downsampling blocks consisting of Double Convolutions ($\text{Conv2D}(3 \times 3) \rightarrow \text{BatchNorm} \rightarrow \text{ReLU} \times 2$) followed by $2 \times 2$ Max Pooling. Channel progression: $3 \rightarrow 32 \rightarrow 64 \rightarrow 128 \rightarrow 256$.
- **Decoder Path**: 3 upsampling blocks utilizing Bilinear Interpolation ($\text{scale}=2$) combined with Tensor Padding and Skip-Connection Concatenation. Channel progression: $384 \rightarrow 128 \rightarrow 192 \rightarrow 64 \rightarrow 96 \rightarrow 32$.
- **Output Layer**: $1 \times 1$ Convolution yielding 4 class logits (or binary building probabilities).
- **Reflective Tensor Padding**: Ensures arbitrary orthophoto resolutions are padded to multiples of 16 prior to forward pass.

#### Objective Loss Function
$$\mathcal{L}_{\text{total}} = \mathcal{L}_{\text{BCEWithLogits}} + \mathcal{L}_{\text{Dice}}$$

$$\mathcal{L}_{\text{Dice}} = 1 - \frac{2 \sum_{i} p_i y_i + \epsilon}{\sum_{i} p_i + \sum_{i} y_i + \epsilon} \quad (\epsilon = 10^{-5})$$

### 2. PyTorch EfficientNet-B0 Roof Classifier
- **Base Backbone**: EfficientNet-B0 featuring depthwise separable convolutions and squeeze-and-excitation optimization.
- **Custom Head**: Replaced final projection layer with `nn.Linear(in_features, 4)` mapping to `["RCC", "Tiled", "Tin", "Other"]`.
- **Pre-processing**: Crop extracted building bbox $\rightarrow$ Lanczos resize ($128 \times 128$) $\rightarrow$ ImageNet Z-score Normalization ($\mu = [0.485, 0.456, 0.406]$, $\sigma = [0.229, 0.224, 0.225]$) $\rightarrow$ Softmax probability distribution.

### 3. Vectorization & GIS Spatial Analytics
- **Shoelace Polygon Area Formula**:
  $$A = \frac{1}{2} \left| \sum_{i=1}^{n-1} (x_i y_{i+1} - x_{i+1} y_i) \right| \times \text{GSD}^2$$
- **Euclidean Polyline Path Integration**:
  $$L = \frac{1}{2} \sum_{i=1}^{n-1} \sqrt{(x_{i+1} - x_i)^2 + (y_{i+1} - y_i)^2} \times \text{GSD}$$
- **Centroid Coordinates**:
  $$C_x = \frac{1}{n} \sum_{i=1}^{n} x_i, \quad C_y = \frac{1}{n} \sum_{i=1}^{n} y_i$$

### 4. Spectral Refinement (HSV Decomposition)
- RGB imagery converted to Hue ($H$), Saturation ($S$), Value ($V$):
  $$H = \begin{cases} 60^\circ \times \left(\frac{G - B}{\Delta} \bmod 6\right) & \text{if } C_{\max} = R \\ 60^\circ \times \left(\frac{B - R}{\Delta} + 2\right) & \text{if } C_{\max} = G \\ 60^\circ \times \left(\frac{R - G}{\Delta} + 4\right) & \text{if } C_{\max} = B \end{cases}$$
- **Water Absorption Filter**: $85^\circ \le H \le 135^\circ \land S \ge 30 \land V \ge 30$.
- **Road Reflectance Filter**: $S \le 40 \land 70 \le V \le 200$.

### 5. Multitemporal Temporal Change Detection
- **Luminosity Reduction**: $Y = 0.2126 R + 0.7152 G + 0.0722 B$.
- **7x7 Spatial Moving Mean Filter**: Reduces high-frequency shadow variation between survey dates.
- **BFS Region Component Labeling**: Extracts connected change clusters larger than 60 pixels.
- **Delta Classification**: Intensity differential ($\Delta Y$) classifies structural modifications:
  - $\Delta Y > +15 \implies \text{New Building / Structure}$
  - $\Delta Y < -15 \implies \text{Demolished / Removed Structure}$
  - Otherwise $\implies \text{Expanded Building / Modified Boundary}$

---

## 🌐 Live Cloud Infrastructure & AI Weights

| Layer | Hosting Provider | Resource / Repository |
| :--- | :--- | :--- |
| **Model Weight Hub** | [Hugging Face](https://huggingface.co/holypreet/svamitva-unet-weights) | [`holypreet/svamitva-unet-weights`](https://huggingface.co/holypreet/svamitva-unet-weights) |
| **Backend Web Service** | [Render](https://render.com) | Python FastAPI Docker Web Service (`render.yaml`) |
| **Frontend Web App** | [Vercel](https://vercel.com) | Next.js 14 Web UI |

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

## 🛠 Architecture & Subsystems

- **Segmentation Model**: PyTorch U-Net (`n_channels=3, n_classes=4`) predicting Building Footprints, Road Networks, and Waterbodies.
- **Roof Classification**: PyTorch EfficientNet-B0 (`torchvision.models.efficientnet_b0`) predicting RCC, Tiled, Tin, or Other.
- **GIS Engine**: Shapely, GeoPandas, OpenCV contour vectorization, Shoelace Area Calculator.
- **Frontend**: Next.js 14, TypeScript, Tailwind CSS, Leaflet, Recharts.
- **Backend API**: Python FastAPI, Uvicorn, ReportLab PDF Engine, SQLAlchemy.

---

## 📊 Factual Model & Dataset Status

| Component | Status | Notes |
| :--- | :--- | :--- |
| **U-Net Architecture** | **Implemented** | PyTorch `UNet` tensor module running CPU/CUDA forward passes |
| **EfficientNet Architecture** | **Implemented** | PyTorch `EfficientNet-B0` with custom 4-class classifier head |
| **Hugging Face Weight Hub** | **Live** | Model weights hosted at `holypreet/svamitva-unet-weights` |
| **SVAMITVA Dataset Repository** | **Scanner Ready** | Place downloaded `.tif` and `.shp` files into `backend/svamitva_dataset_repository/` |
| **Evaluation Metrics** | **Calculated** | IoU, Dice, Precision, Recall, F1 score evaluator built in `app/svamitva_dataset/gis_rasterizer.py` |

---

## 🚀 Local Quick Start

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

---

## 🌐 Render Backend & Cloud Deployment Guide

To deploy the FastAPI backend service 24/7 on **Render** using Hugging Face models, refer to the step-by-step guide in [`README_RENDER_DEPLOYMENT.md`](README_RENDER_DEPLOYMENT.md).
