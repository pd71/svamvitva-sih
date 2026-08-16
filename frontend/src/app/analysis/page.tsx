"use client";

import { useEffect, useState, useRef, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import { 
  Upload, 
  Play, 
  Layers, 
  Eye, 
  FileText, 
  Building2, 
  Milestone, 
  Waves, 
  CheckCircle2, 
  AlertCircle,
  Loader2,
  Maximize2,
  Sparkles
} from "lucide-react";

function AnalysisContent() {
  const searchParams = useSearchParams();
  const initialId = searchParams.get("id");

  const [analysisId, setAnalysisId] = useState<string | null>(initialId);
  const [analysis, setAnalysis] = useState<any>(null);
  const [features, setFeatures] = useState<any>(null);
  const [selectedBuilding, setSelectedBuilding] = useState<any>(null);
  
  const [uploading, setUploading] = useState(false);
  const [villageName, setVillageName] = useState("Rampur Village");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  // Toggle Overlay Controls
  const [showOriginal, setShowOriginal] = useState(true);
  const [showBuildings, setShowBuildings] = useState(true);
  const [showRoads, setShowRoads] = useState(true);
  const [showWaterbodies, setShowWaterbodies] = useState(true);

  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const imageObjRef = useRef<HTMLImageElement | null>(null);

  // Load Analysis Detail and Poll Status
  const fetchAnalysisDetail = async (id: string) => {
    try {
      const res = await fetch(`/api/analysis/${id}`);
      if (res.ok) {
        const data = await res.json();
        setAnalysis(data);
        if (data.status === "completed") {
          fetchFeatures(id);
        }
      }
    } catch (err) {
      console.error(err);
    }
  };

  const fetchFeatures = async (id: string) => {
    try {
      const res = await fetch(`/api/analysis/${id}/features`);
      if (res.ok) {
        const data = await res.json();
        setFeatures(data);
      }
    } catch (err) {
      console.error(err);
    }
  };

  // Poll analysis status every 1.5s while processing
  useEffect(() => {
    if (!analysisId) return;
    fetchAnalysisDetail(analysisId);

    const interval = setInterval(async () => {
      const res = await fetch(`/api/analysis/${analysisId}/status`);
      if (res.ok) {
        const statusData = await res.json();
        setAnalysis((prev: any) => ({ ...prev, ...statusData }));
        if (statusData.status === "completed") {
          fetchAnalysisDetail(analysisId);
          clearInterval(interval);
        }
      }
    }, 1500);

    return () => clearInterval(interval);
  }, [analysisId]);

  // Handle File Upload
  const handleUploadSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedFile) return;

    setUploading(true);
    const formData = new FormData();
    formData.append("file", selectedFile);
    formData.append("village_name", villageName);

    try {
      const res = await fetch("/api/analysis/upload", {
        method: "POST",
        body: formData,
      });
      if (res.ok) {
        const data = await res.json();
        setAnalysisId(data.id);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setUploading(false);
    }
  };

  const handleLoadDemo = async () => {
    setUploading(true);
    try {
      const res = await fetch("/api/analysis/demo", { method: "POST" });
      if (res.ok) {
        const data = await res.json();
        setAnalysisId(data.id);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setUploading(false);
    }
  };

  // Canvas Overlay Renderer
  useEffect(() => {
    if (!analysis || !canvasRef.current) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const img = new Image();
    const imageSrc = `/api/analysis/${analysis.id}/image`;
    img.src = imageSrc;

    img.onload = () => {
      imageObjRef.current = img;
      canvas.width = img.width;
      canvas.height = img.height;

      // Clear Canvas
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      // 1. Draw Original Image
      if (showOriginal) {
        ctx.drawImage(img, 0, 0);
      } else {
        ctx.fillStyle = "#0b1120";
        ctx.fillRect(0, 0, canvas.width, canvas.height);
      }

      if (!features || !features.features) return;

      // 2. Draw Waterbodies
      if (showWaterbodies) {
        features.features
          .filter((f: any) => f.properties.category === "Waterbody")
          .forEach((f: any) => {
            const coords = f.geometry.coordinates[0];
            ctx.beginPath();
            ctx.moveTo(coords[0][0], coords[0][1]);
            for (let i = 1; i < coords.length; i++) {
              ctx.lineTo(coords[i][0], coords[i][1]);
            }
            ctx.closePath();
            ctx.fillStyle = "rgba(14, 165, 233, 0.4)";
            ctx.fill();
            ctx.strokeStyle = "#0284c7";
            ctx.lineWidth = 3;
            ctx.stroke();
          });
      }

      // 3. Draw Roads
      if (showRoads) {
        features.features
          .filter((f: any) => f.properties.category === "Road")
          .forEach((f: any) => {
            const coords = f.geometry.coordinates;
            ctx.beginPath();
            ctx.moveTo(coords[0][0], coords[0][1]);
            for (let i = 1; i < coords.length; i++) {
              ctx.lineTo(coords[i][0], coords[i][1]);
            }
            ctx.strokeStyle = "#f59e0b";
            ctx.lineWidth = 5;
            ctx.stroke();
          });
      }

      // 4. Draw Buildings
      if (showBuildings) {
        features.features
          .filter((f: any) => f.properties.category === "Building")
          .forEach((f: any) => {
            const coords = f.geometry.coordinates[0];
            const roofType = f.properties.roof_type;
            const isSelected = selectedBuilding && selectedBuilding.id === f.id;

            let fillColor = "rgba(16, 185, 129, 0.45)"; // RCC Default Green
            let strokeColor = "#10b981";

            if (roofType === "RCC") {
              fillColor = "rgba(245, 158, 11, 0.45)"; // RCC Amber
              strokeColor = "#f59e0b";
            } else if (roofType === "Tiled") {
              fillColor = "rgba(239, 68, 68, 0.45)"; // Tiled Red
              strokeColor = "#ef4444";
            } else if (roofType === "Tin") {
              fillColor = "rgba(6, 182, 212, 0.45)"; // Tin Cyan
              strokeColor = "#06b6d4";
            }

            ctx.beginPath();
            ctx.moveTo(coords[0][0], coords[0][1]);
            for (let i = 1; i < coords.length; i++) {
              ctx.lineTo(coords[i][0], coords[i][1]);
            }
            ctx.closePath();
            ctx.fillStyle = isSelected ? "rgba(255, 255, 255, 0.7)" : fillColor;
            ctx.fill();
            ctx.strokeStyle = isSelected ? "#ffffff" : strokeColor;
            ctx.lineWidth = isSelected ? 4 : 2;
            ctx.stroke();

            // Label (only draw label for selected building to keep map view clean)
            if (isSelected) {
              const cx = f.properties.centroid[0];
              const cy = f.properties.centroid[1];
              ctx.fillStyle = "#ffffff";
              ctx.font = "bold 12px sans-serif";
              ctx.fillText(`#${f.properties.building_index}`, cx - 8, cy + 4);
            }
          });
      }
    };
  }, [analysis, features, showOriginal, showBuildings, showRoads, showWaterbodies, selectedBuilding]);

  // Handle Canvas Click to Select Building
  const handleCanvasClick = (e: React.MouseEvent<HTMLCanvasElement>) => {
    if (!canvasRef.current || !features || !features.features) return;
    const canvas = canvasRef.current;
    const rect = canvas.getBoundingClientRect();
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;

    const clickX = (e.clientX - rect.left) * scaleX;
    const clickY = (e.clientY - rect.top) * scaleY;

    // Find clicked building based on centroid distance
    let closest: any = null;
    let minDistance = 50;

    features.features
      .filter((f: any) => f.properties.category === "Building")
      .forEach((f: any) => {
        const cx = f.properties.centroid[0];
        const cy = f.properties.centroid[1];
        const dist = Math.hypot(clickX - cx, clickY - cy);
        if (dist < minDistance) {
          minDistance = dist;
          closest = f;
        }
      });

    if (closest) {
      setSelectedBuilding(closest);
    }
  };

  const stagesList = [
    "1. Upload Complete",
    "2. Preprocessing & Rescaling",
    "3. Image Tiling (512x512 Patches)",
    "4. AI Multi-Class Segmentation",
    "5. Roof Classification (EfficientNet)",
    "6. GIS Spatial Metrics & Overlay",
    "7. Report Generation",
    "8. Processing Complete"
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 border-b border-[#2a3854] pb-4">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <Layers className="w-5 h-5 text-sky-400" />
            Drone Orthophoto Feature Extraction Engine
          </h2>
          <p className="text-xs text-slate-400">
            Upload aerial drone imagery to run multi-class segmentation, roof type classification, and GIS spatial extraction.
          </p>
        </div>
        
        <button
          onClick={handleLoadDemo}
          disabled={uploading}
          className="flex items-center space-x-2 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 text-white px-3.5 py-2 rounded text-xs font-semibold shadow-md transition-all"
        >
          <Sparkles className="w-4 h-4" />
          <span>Load Demo Village</span>
        </button>
      </div>

      {/* Upload Dropzone Bar if no active analysis */}
      {!analysisId && (
        <div className="gis-card p-8 text-center space-y-4 max-w-2xl mx-auto border-dashed border-2 border-sky-500/40">
          <div className="w-12 h-12 rounded-full bg-sky-950/80 border border-sky-800 text-sky-400 flex items-center justify-center mx-auto">
            <Upload className="w-6 h-6 animate-bounce" />
          </div>
          <div>
            <h3 className="text-base font-bold text-white">Upload Orthophoto Image</h3>
            <p className="text-xs text-slate-400 mt-1">
              Supports JPG, JPEG, PNG, TIFF, and GeoTIFF formats. (Recommended GSD: &lt;25cm/px)
            </p>
          </div>

          <form onSubmit={handleUploadSubmit} className="space-y-4 max-w-md mx-auto pt-2">
            <input
              type="text"
              value={villageName}
              onChange={(e) => setVillageName(e.target.value)}
              placeholder="Village / Location Name"
              className="w-full px-3 py-2 bg-[#0f172a] border border-[#2a3854] rounded text-xs text-white placeholder-slate-500 focus:outline-none focus:border-sky-500"
            />

            <input
              type="file"
              accept=".jpg,.jpeg,.png,.tif,.tiff"
              onChange={(e) => setSelectedFile(e.target.files?.[0] || null)}
              className="w-full text-xs text-slate-400 file:mr-4 file:py-2 file:px-4 file:rounded file:border-0 file:text-xs file:font-semibold file:bg-sky-950 file:text-sky-400 border border-[#2a3854] rounded bg-[#0f172a]"
            />

            <div className="flex gap-3 pt-2">
              <button
                type="submit"
                disabled={!selectedFile || uploading}
                className="w-full py-2.5 bg-sky-600 hover:bg-sky-500 text-white rounded text-xs font-bold transition-all disabled:opacity-50 flex items-center justify-center space-x-2"
              >
                {uploading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4" />}
                <span>{uploading ? "Uploading & Initializing..." : "Run AI Analysis"}</span>
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Main Active Analysis Pipeline View */}
      {analysis && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column: Interactive Canvas & Layer Controls */}
          <div className="lg:col-span-2 space-y-4">
            <div className="gis-card p-4 space-y-3">
              {/* Controls Bar */}
              <div className="flex flex-wrap items-center justify-between gap-3 border-b border-[#2a3854] pb-3">
                <div className="flex items-center space-x-2 text-xs font-semibold text-white">
                  <span>Layer Controls:</span>
                  <label className="flex items-center space-x-1 cursor-pointer bg-[#0f172a] px-2.5 py-1 rounded border border-[#2a3854]">
                    <input
                      type="checkbox"
                      checked={showOriginal}
                      onChange={(e) => setShowOriginal(e.target.checked)}
                      className="rounded accent-sky-500"
                    />
                    <span>Original</span>
                  </label>

                  <label className="flex items-center space-x-1 cursor-pointer bg-[#0f172a] px-2.5 py-1 rounded border border-[#2a3854] text-emerald-400">
                    <input
                      type="checkbox"
                      checked={showBuildings}
                      onChange={(e) => setShowBuildings(e.target.checked)}
                      className="rounded accent-emerald-500"
                    />
                    <span>Buildings</span>
                  </label>

                  <label className="flex items-center space-x-1 cursor-pointer bg-[#0f172a] px-2.5 py-1 rounded border border-[#2a3854] text-amber-400">
                    <input
                      type="checkbox"
                      checked={showRoads}
                      onChange={(e) => setShowRoads(e.target.checked)}
                      className="rounded accent-amber-500"
                    />
                    <span>Roads</span>
                  </label>

                  <label className="flex items-center space-x-1 cursor-pointer bg-[#0f172a] px-2.5 py-1 rounded border border-[#2a3854] text-sky-400">
                    <input
                      type="checkbox"
                      checked={showWaterbodies}
                      onChange={(e) => setShowWaterbodies(e.target.checked)}
                      className="rounded accent-sky-500"
                    />
                    <span>Waterbodies</span>
                  </label>
                </div>

                <div className="text-xs text-slate-400 font-mono">
                  {analysis.width} × {analysis.height} px | {(analysis.file_size / 1024 / 1024).toFixed(2)} MB
                </div>
              </div>

              {/* Interactive Canvas Overlay Container */}
              <div className="relative bg-[#0b1120] rounded border border-[#2a3854] overflow-hidden min-h-[420px] flex items-center justify-center">
                <canvas
                  ref={canvasRef}
                  onClick={handleCanvasClick}
                  className="max-w-full max-h-[600px] object-contain cursor-crosshair"
                />

                {analysis.status !== "completed" && (
                  <div className="absolute inset-0 bg-slate-950/80 backdrop-blur-sm flex flex-col items-center justify-center space-y-3 p-6 text-center">
                    <Loader2 className="w-8 h-8 text-sky-400 animate-spin" />
                    <div className="text-sm font-bold text-white">{analysis.stage}</div>
                    <div className="w-64 bg-slate-800 rounded-full h-2 overflow-hidden border border-slate-700">
                      <div
                        className="bg-sky-500 h-full transition-all duration-500"
                        style={{ width: `${analysis.progress_pct}%` }}
                      ></div>
                    </div>
                    <p className="text-xs text-slate-400 font-mono">{analysis.progress_pct}% Completed</p>
                  </div>
                )}
              </div>

              {/* Instructions */}
              <p className="text-[11px] text-slate-400 text-center italic">
                * Click on any building footprint polygon on the image above to open the detailed building feature panel.
              </p>
            </div>
          </div>

          {/* Right Column: Stages Tracker & Inspector */}
          <div className="space-y-4">
            {/* Live Stages Status */}
            <div className="gis-card p-5 space-y-4">
              <h3 className="font-bold text-white text-sm border-b border-[#2a3854] pb-2 flex items-center justify-between">
                <span>AI Job Progress Stages</span>
                <span className="text-xs font-mono text-sky-400">{analysis.progress_pct}%</span>
              </h3>

              <div className="space-y-2">
                {stagesList.map((stg, idx) => {
                  const isCurrent = analysis.stage === stg;
                  const isDone = analysis.progress_pct > (idx + 1) * 12.5 || analysis.status === "completed";

                  return (
                    <div
                      key={stg}
                      className={`p-2 rounded text-xs flex items-center justify-between transition-all ${
                        isCurrent
                          ? "bg-sky-950 border border-sky-500 text-sky-300 font-bold"
                          : isDone
                          ? "bg-[#0f172a] text-slate-300 border border-[#2a3854]"
                          : "bg-[#0b1120] text-slate-600 border border-transparent"
                      }`}
                    >
                      <span>{stg}</span>
                      {isDone ? (
                        <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                      ) : isCurrent ? (
                        <Loader2 className="w-4 h-4 text-sky-400 animate-spin" />
                      ) : (
                        <span className="w-2 h-2 rounded-full bg-slate-700"></span>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Selected Building Detail Inspector */}
            <div className="gis-card p-5 space-y-3">
              <h3 className="font-bold text-white text-sm border-b border-[#2a3854] pb-2 flex items-center justify-between">
                <span>Building Detail Inspector</span>
                {selectedBuilding && (
                  <span className="text-xs px-2 py-0.5 rounded bg-sky-950 text-sky-400 border border-sky-800 font-mono">
                    #{selectedBuilding.properties.building_index}
                  </span>
                )}
              </h3>

              {selectedBuilding ? (
                <div className="space-y-3 text-xs">
                  <div className="grid grid-cols-2 gap-2">
                    <div className="p-2 bg-[#0f172a] rounded border border-[#2a3854]">
                      <div className="text-slate-400 text-[10px]">Roof Classification</div>
                      <div className={`font-bold text-sm ${
                        selectedBuilding.properties.roof_type === 'RCC' ? 'text-amber-400' :
                        selectedBuilding.properties.roof_type === 'Tiled' ? 'text-red-400' : 'text-cyan-400'
                      }`}>
                        {selectedBuilding.properties.roof_type}
                      </div>
                    </div>

                    <div className="p-2 bg-[#0f172a] rounded border border-[#2a3854]">
                      <div className="text-slate-400 text-[10px]">AI Confidence</div>
                      <div className="font-bold text-sm text-emerald-400">
                        {(selectedBuilding.properties.confidence * 100).toFixed(1)}%
                      </div>
                    </div>
                  </div>

                  <div className="p-2.5 bg-[#0f172a] rounded border border-[#2a3854] space-y-1.5 font-mono">
                    <div className="flex justify-between">
                      <span className="text-slate-400">Footprint Area:</span>
                      <span className="text-white font-bold">{selectedBuilding.properties.area_sqm} m²</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-400">Centroid Coordinates:</span>
                      <span className="text-slate-200">
                        ({selectedBuilding.properties.centroid[0].toFixed(1)}, {selectedBuilding.properties.centroid[1].toFixed(1)})
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-400">Review Status:</span>
                      <span className="text-sky-400 uppercase">{selectedBuilding.properties.status}</span>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="py-6 text-center text-xs text-slate-500">
                  Click any building on the map overlay to view individual spatial & classification attributes.
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default function AnalysisPage() {
  return (
    <Suspense fallback={<div className="p-8 text-center text-slate-400 font-mono">Loading Analysis Pipeline...</div>}>
      <AnalysisContent />
    </Suspense>
  );
}

