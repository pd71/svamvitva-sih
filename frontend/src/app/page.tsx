"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { 
  Building2, 
  MapPin, 
  Milestone, 
  Waves, 
  ShieldCheck, 
  ArrowRight, 
  Play, 
  PlusCircle, 
  RefreshCw,
  Activity,
  CheckCircle2,
  Clock
} from "lucide-react";

export default function Dashboard() {
  const [stats, setStats] = useState<any>(null);
  const [datasetInfo, setDatasetInfo] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [demoLoading, setDemoLoading] = useState(false);

  const fetchStats = async () => {
    try {
      setLoading(true);
      const res = await fetch("/api/dashboard/stats");
      if (res.ok) {
        const data = await res.json();
        setStats(data);
      }

      const resD = await fetch("/api/svamitva-dataset");
      if (resD.ok) {
        const dataD = await resD.json();
        setDatasetInfo(dataD);
      }
    } catch (err) {
      console.error("Failed to load dashboard stats", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStats();
  }, []);

  const handleLoadDemo = async () => {
    try {
      setDemoLoading(true);
      const res = await fetch("/api/analysis/demo", { method: "POST" });
      if (res.ok) {
        const data = await res.json();
        window.location.href = `/analysis?id=${data.id}`;
      }
    } catch (err) {
      console.error(err);
    } finally {
      setDemoLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Hero Control Banner */}
      <div className="gis-card p-6 bg-gradient-to-r from-[#161f33] via-[#1e293b] to-[#0f172a] border-l-4 border-l-sky-500 flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <span className="text-xs font-mono font-semibold text-sky-400 uppercase tracking-widest">
            Control Room Dashboard
          </span>
          <h2 className="text-2xl font-bold text-white mt-1">
            Automated Drone Feature Extraction System
          </h2>
          <p className="text-sm text-slate-300 mt-1 max-w-2xl">
            Real-time geospatial intelligence pipeline for multi-class building, road, and waterbody segmentation with automated roof classification and GIS vector output.
          </p>
        </div>
        <div className="flex items-center gap-3 w-full md:w-auto">
          <button
            onClick={handleLoadDemo}
            disabled={demoLoading}
            className="flex-1 md:flex-initial flex items-center justify-center space-x-2 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white px-4 py-2.5 rounded-md font-semibold text-sm shadow-lg shadow-emerald-900/30 transition-all disabled:opacity-50"
          >
            <Play className="w-4 h-4 fill-current" />
            <span>{demoLoading ? "Loading Demo..." : "Load Demo Village"}</span>
          </button>
          <Link
            href="/analysis"
            className="flex-1 md:flex-initial flex items-center justify-center space-x-2 bg-sky-600 hover:bg-sky-500 text-white px-4 py-2.5 rounded-md font-semibold text-sm shadow-lg shadow-sky-900/30 transition-all"
          >
            <PlusCircle className="w-4 h-4" />
            <span>Upload Orthophoto</span>
          </Link>
        </div>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
        {/* Card 1: Villages */}
        <div className="gis-card p-4 gis-card-hover flex items-center space-x-4">
          <div className="p-3 bg-sky-950/80 border border-sky-800/50 rounded-lg text-sky-400">
            <MapPin className="w-6 h-6" />
          </div>
          <div>
            <div className="text-2xl font-bold text-white">
              {loading ? "..." : stats?.total_villages_processed || 0}
            </div>
            <div className="text-xs text-slate-400 font-medium">Villages Processed</div>
          </div>
        </div>

        {/* Card 2: Buildings */}
        <div className="gis-card p-4 gis-card-hover flex items-center space-x-4">
          <div className="p-3 bg-amber-950/80 border border-amber-800/50 rounded-lg text-amber-400">
            <Building2 className="w-6 h-6" />
          </div>
          <div>
            <div className="text-2xl font-bold text-white">
              {loading ? "..." : stats?.total_buildings_detected || 0}
            </div>
            <div className="text-xs text-slate-400 font-medium">Buildings Extracted</div>
          </div>
        </div>

        {/* Card 3: Roads */}
        <div className="gis-card p-4 gis-card-hover flex items-center space-x-4">
          <div className="p-3 bg-cyan-950/80 border border-cyan-800/50 rounded-lg text-cyan-400">
            <Milestone className="w-6 h-6" />
          </div>
          <div>
            <div className="text-2xl font-bold text-white">
              {loading ? "..." : `${stats?.total_road_length_m || 0} m`}
            </div>
            <div className="text-xs text-slate-400 font-medium">Road Corridor Length</div>
          </div>
        </div>

        {/* Card 4: Water */}
        <div className="gis-card p-4 gis-card-hover flex items-center space-x-4">
          <div className="p-3 bg-blue-950/80 border border-blue-800/50 rounded-lg text-blue-400">
            <Waves className="w-6 h-6" />
          </div>
          <div>
            <div className="text-2xl font-bold text-white">
              {loading ? "..." : `${stats?.total_waterbody_area_sqm || 0} m²`}
            </div>
            <div className="text-xs text-slate-400 font-medium">Waterbody Area</div>
          </div>
        </div>

        {/* Card 5: Confidence */}
        <div className="gis-card p-4 gis-card-hover flex items-center space-x-4">
          <div className="p-3 bg-emerald-950/80 border border-emerald-800/50 rounded-lg text-emerald-400">
            <ShieldCheck className="w-6 h-6" />
          </div>
          <div>
            <div className="text-2xl font-bold text-white">
              {loading ? "..." : `${((stats?.average_confidence || 0) * 100).toFixed(1)}%`}
            </div>
            <div className="text-xs text-slate-400 font-medium">Avg AI Confidence</div>
          </div>
        </div>
      </div>

      {/* Main Content Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: Recent Analyses */}
        <div className="lg:col-span-2 space-y-4">
          <div className="gis-card p-5 space-y-4">
            <div className="flex items-center justify-between border-b border-[#2a3854] pb-3">
              <div className="flex items-center space-x-2">
                <Activity className="w-5 h-5 text-sky-400" />
                <h3 className="font-bold text-white text-base">Recent Village Surveys</h3>
              </div>
              <button 
                onClick={fetchStats} 
                className="text-xs text-slate-400 hover:text-sky-400 flex items-center space-x-1"
              >
                <RefreshCw className="w-3.5 h-3.5" />
                <span>Refresh</span>
              </button>
            </div>

            {loading ? (
              <div className="py-8 text-center text-slate-400 text-sm">Loading recent processing jobs...</div>
            ) : !stats?.recent_analyses || stats.recent_analyses.length === 0 ? (
              <div className="py-12 text-center space-y-3">
                <p className="text-slate-400 text-sm">No orthophoto analyses run yet.</p>
                <button
                  onClick={handleLoadDemo}
                  className="px-4 py-2 bg-sky-600 hover:bg-sky-500 text-white rounded text-xs font-semibold"
                >
                  Load Demo Village Now
                </button>
              </div>
            ) : (
              <div className="space-y-3">
                {stats.recent_analyses.map((item: any) => (
                  <div
                    key={item.id}
                    className="p-3.5 rounded bg-[#0f172a] border border-[#2a3854] hover:border-sky-500 transition-all flex items-center justify-between gap-4"
                  >
                    <div className="space-y-1">
                      <div className="flex items-center space-x-2">
                        <span className="font-semibold text-white text-sm">{item.village_name}</span>
                        <span className={`text-[10px] px-2 py-0.5 rounded font-mono ${
                          item.status === 'completed' 
                            ? 'bg-emerald-950 text-emerald-400 border border-emerald-800' 
                            : 'bg-amber-950 text-amber-400 border border-amber-800'
                        }`}>
                          {item.stage || item.status}
                        </span>
                      </div>
                      <div className="text-xs text-slate-400 flex items-center space-x-4">
                        <span>File: {item.original_filename}</span>
                        <span>•</span>
                        <span>{new Date(item.created_at).toLocaleDateString()}</span>
                      </div>
                    </div>

                    <div className="flex items-center space-x-6">
                      <div className="text-right hidden sm:block">
                        <div className="text-xs font-mono text-white">
                          {item.total_buildings} bldgs | {item.total_roads_len}m road
                        </div>
                        <div className="text-[11px] text-slate-400">
                          {item.crs_name}
                        </div>
                      </div>

                      <Link
                        href={`/analysis?id=${item.id}`}
                        className="p-2 rounded bg-sky-950 text-sky-400 hover:bg-sky-900 border border-sky-800 transition-all"
                      >
                        <ArrowRight className="w-4 h-4" />
                      </Link>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Right Column: Dataset Status & Pipeline Architecture */}
        <div className="space-y-4">
          {/* Official SVAMITVA Dataset Status Card */}
          <div className="gis-card p-5 space-y-3 border-l-4 border-l-sky-500">
            <h3 className="font-bold text-white text-sm flex items-center justify-between border-b border-[#2a3854] pb-2">
              <span>Official SVAMITVA Dataset</span>
              <span className={`text-[10px] px-2 py-0.5 rounded font-mono ${
                datasetInfo?.is_svamitva_loaded 
                  ? 'bg-emerald-950 text-emerald-400 border border-emerald-800'
                  : 'bg-amber-950 text-amber-400 border border-amber-800'
              }`}>
                {datasetInfo?.is_svamitva_loaded ? 'Dataset Loaded' : 'Demo Mode Active'}
              </span>
            </h3>

            <div className="space-y-2 text-xs font-mono">
              <div className="flex justify-between">
                <span className="text-slate-400">Target Resolution:</span>
                <span className="text-sky-400">{datasetInfo?.spatial_resolution || "50 cm / pixel"}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Portal Source:</span>
                <span className="text-slate-200">{datasetInfo?.source || "svamitva.nic.in"}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Raw TIF Images:</span>
                <span className="text-white font-bold">{datasetInfo?.tif_count || 0} Files</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Vector Shapefiles:</span>
                <span className="text-white font-bold">{datasetInfo?.shp_count || 0} Files</span>
              </div>
              
              {datasetInfo?.instruction && (
                <div className="p-2.5 rounded bg-[#0f172a] border border-[#2a3854] text-[11px] text-slate-300 space-y-1.5">
                  <div className="text-amber-400 font-bold">Official Download Source (SIH 2024):</div>
                  <div className="text-[10px] text-slate-400 truncate">https://svamitva.nic.in/DownloadPDF/TifFile/Maharashtra_1.zip</div>
                  <p className="text-[10px] text-slate-400">
                    Place extracted .tif and .shp files into <code className="text-sky-300">backend/svamitva_dataset_repository/</code> for real U-Net training.
                  </p>
                </div>
              )}
            </div>
          </div>

          <div className="gis-card p-5 space-y-4">
            <h3 className="font-bold text-white text-base border-b border-[#2a3854] pb-3 flex items-center justify-between">
              <span>Pipeline Architecture</span>
              <span className="text-xs text-emerald-400 font-mono flex items-center gap-1">
                <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping"></span>
                Active Engine
              </span>
            </h3>

            <div className="space-y-3 text-xs">
              <div className="p-2.5 rounded bg-[#0f172a] border border-[#2a3854] flex items-center justify-between">
                <div>
                  <div className="font-semibold text-slate-200">1. Data Ingestion & Tiling</div>
                  <div className="text-[11px] text-slate-400">GeoTIFF / PNG 512x512 Patches</div>
                </div>
                <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              </div>

              <div className="p-2.5 rounded bg-[#0f172a] border border-[#2a3854] flex items-center justify-between">
                <div>
                  <div className="font-semibold text-slate-200">2. Semantic Segmentation</div>
                  <div className="text-[11px] text-slate-400">U-Net / DeepLabV3+ (CV Prototype)</div>
                </div>
                <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              </div>

              <div className="p-2.5 rounded bg-[#0f172a] border border-[#2a3854] flex items-center justify-between">
                <div>
                  <div className="font-semibold text-slate-200">3. Roof Classification</div>
                  <div className="text-[11px] text-slate-400">EfficientNet-B4 (RCC/Tile/Tin/Other)</div>
                </div>
                <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              </div>

              <div className="p-2.5 rounded bg-[#0f172a] border border-[#2a3854] flex items-center justify-between">
                <div>
                  <div className="font-semibold text-slate-200">4. GIS Vector & Reports</div>
                  <div className="text-[11px] text-slate-400">Shapely + ReportLab + PostGIS/GeoJSON</div>
                </div>
                <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              </div>
            </div>

            <div className="pt-2">
              <Link
                href="/architecture"
                className="w-full py-2 bg-slate-800 hover:bg-slate-700 text-sky-400 text-xs font-semibold rounded block text-center border border-slate-700 transition-all"
              >
                View Deep Architecture Details →
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
