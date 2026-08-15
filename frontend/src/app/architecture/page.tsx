"use client";

import { Cpu, Layers, Database, FileText, CheckCircle2, ArrowDown, Box } from "lucide-react";

export default function ArchitecturePage() {
  const steps = [
    {
      title: "1. Drone Orthophoto Ingestion",
      tech: "Rasterio / OpenCV / GeoTIFF CRS Reader",
      description: "Ingests ultra-high-resolution aerial drone imagery in JPG, PNG, TIFF, or GeoTIFF format. Extracts ground sampling distance (GSD), image dimensions, and CRS projection metadata.",
      type: "Ingestion"
    },
    {
      title: "2. Preprocessing & Tiling Engine",
      tech: "NumPy / SciPy Tiling Pipeline",
      description: "Normalizes RGB reflectance channels and splits large gigapixel orthophotos into overlapping 512x512 pixel patches for deep learning batch inference without memory bottlenecks.",
      type: "Preprocessing"
    },
    {
      title: "3. Semantic Segmentation Model",
      tech: "U-Net / DeepLabV3+ (CV Prototype Engine)",
      description: "Multi-class deep convolutional network predicting per-pixel class masks for Buildings, Roads, and Waterbodies. Prototype uses HSV color space analysis, Canny edge detection, and morphological watershed.",
      type: "AI Model"
    },
    {
      title: "4. Roof Type Classification",
      tech: "EfficientNet-B4 / HSV Color-Texture Classifier",
      description: "Crops individual candidate building footprints and runs fine-grained roof material classification into RCC (Concrete), Tiled (Terracotta), Tin (Corrugated Sheet), or Other.",
      type: "AI Model"
    },
    {
      title: "5. GIS Vector Processing",
      tech: "Shapely / GeoPandas / PostGIS",
      description: "Converts pixel mask contours into clean spatial vector geometries (Polygon / LineString), computes footprint areas (m²), road corridor lengths, and centroid coordinates.",
      type: "GIS Processing"
    },
    {
      title: "6. FastAPI REST Engine & Database",
      tech: "FastAPI / SQLAlchemy / SQLite / PostgreSQL",
      description: "Manages asynchronous background processing jobs, serves real-time status polling endpoints, stores feature geometries, and manages human review approvals.",
      type: "Backend"
    },
    {
      title: "7. Dashboard, Interactive GIS & PDF Reports",
      tech: "Next.js 14 / Leaflet / Recharts / ReportLab",
      description: "Presents interactive vector GIS map overlays, building detail inspector drawers, human-in-the-loop review queues, temporal change detection tools, and downloadable PDF reports.",
      type: "Frontend / Output"
    }
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="border-b border-[#2a3854] pb-4">
        <h2 className="text-xl font-bold text-white flex items-center gap-2">
          <Cpu className="w-5 h-5 text-sky-400" />
          SVAMITVA AI System Architecture & Model Pipeline
        </h2>
        <p className="text-xs text-slate-400 mt-1">
          Detailed technical workflow showing production U-Net / EfficientNet deep learning integration and prototype computer vision abstraction layer.
        </p>
      </div>

      {/* Architecture Flow Diagram */}
      <div className="gis-card p-6 space-y-6">
        <div className="text-center max-w-xl mx-auto space-y-1">
          <h3 className="text-base font-bold text-white uppercase tracking-wider">
            End-to-End Processing Workflow
          </h3>
          <p className="text-xs text-slate-400">
            Drone Orthophoto &rarr; AI Multi-Class Feature Extraction &rarr; GIS Delivery
          </p>
        </div>

        <div className="max-w-3xl mx-auto space-y-4">
          {steps.map((stg, idx) => (
            <div key={stg.title} className="space-y-3">
              <div className="p-4 rounded-lg bg-[#0f172a] border border-[#2a3854] hover:border-sky-500 transition-all flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
                <div className="space-y-1">
                  <div className="flex items-center space-x-3">
                    <span className="font-bold text-white text-sm">{stg.title}</span>
                    <span className="text-[10px] px-2 py-0.5 rounded font-mono bg-sky-950 text-sky-400 border border-sky-800">
                      {stg.type}
                    </span>
                  </div>
                  <p className="text-xs text-slate-300">{stg.description}</p>
                </div>
                <div className="text-right text-[11px] font-mono text-amber-400 bg-amber-950/40 px-2.5 py-1 rounded border border-amber-800/50 whitespace-nowrap">
                  {stg.tech}
                </div>
              </div>

              {idx < steps.length - 1 && (
                <div className="flex justify-center py-0.5">
                  <ArrowDown className="w-5 h-5 text-sky-400 animate-bounce" />
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Production Plug-in Interface Callout Box */}
      <div className="gis-card p-6 border-l-4 border-l-emerald-500 space-y-3">
        <h3 className="text-sm font-bold text-white flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4 text-emerald-400" />
          Production Model Modular Plug-in Design
        </h3>
        <p className="text-xs text-slate-300 leading-relaxed">
          The backend architecture uses Python Abstract Base Classes (<code className="text-sky-300 font-mono">SegmentationModel</code> and <code className="text-sky-300 font-mono">RoofClassificationModel</code>). The prototype current runs <code className="text-sky-300 font-mono">DemoSegmentationModel</code> and <code className="text-sky-300 font-mono">DemoRoofClassificationModel</code>. When trained weights (e.g. PyTorch U-Net or EfficientNet weights trained on SVAMITVA village orthophotos) are placed in <code className="text-sky-300 font-mono">backend/app/ml/weights/</code>, the engine seamlessly switches without modifying the API contracts or frontend.
        </p>
      </div>
    </div>
  );
}
