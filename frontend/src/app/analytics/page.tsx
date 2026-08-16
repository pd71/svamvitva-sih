"use client";

import { useEffect, useState } from "react";
import { 
  BarChart3, 
  PieChart as PieIcon, 
  ShieldAlert, 
  ArrowLeftRight, 
  Upload, 
  Play, 
  CheckCircle2,
  Building2,
  Milestone,
  Waves,
  Loader2
} from "lucide-react";
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from "recharts";

import { getApiUrl } from "@/lib/api";

export default function AnalyticsPage() {
  const [analyses, setAnalyses] = useState<any[]>([]);
  const [selectedAnalysisId, setSelectedAnalysisId] = useState<string>("");
  const [stats, setStats] = useState<any>(null);

  // Change Detection State
  const [prevFile, setPrevFile] = useState<File | null>(null);
  const [currFile, setCurrFile] = useState<File | null>(null);
  const [changeLoading, setChangeLoading] = useState(false);
  const [changeResults, setChangeResults] = useState<any>(null);

  useEffect(() => {
    fetchAnalyses();
  }, []);

  const fetchAnalyses = async () => {
    try {
      const res = await fetch(getApiUrl("/api/analyses"));
      if (res.ok) {
        const data = await res.json();
        setAnalyses(data);
        if (data.length > 0) {
          setSelectedAnalysisId(data[0].id);
        }
      }
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    if (!selectedAnalysisId) return;

    const fetchStatistics = async () => {
      try {
        const res = await fetch(getApiUrl(`/api/analysis/${selectedAnalysisId}/statistics`));
        if (res.ok) {
          const data = await res.json();
          setStats(data);
        }
      } catch (err) {
        console.error(err);
      }
    };

    fetchStatistics();
  }, [selectedAnalysisId]);

  const handleRunChangeDetection = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!prevFile || !currFile) return;

    setChangeLoading(true);
    const formData = new FormData();
    formData.append("prev_file", prevFile);
    formData.append("curr_file", currFile);

    try {
      const res = await fetch(getApiUrl("/api/change-detection"), {
        method: "POST",
        body: formData,
      });

      if (res.ok) {
        const data = await res.json();
        setChangeResults(data);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setChangeLoading(false);
    }
  };

  const roofPieData = stats?.roof_distribution
    ? [
        { name: "RCC (Concrete)", value: stats.roof_distribution.RCC, color: "#f59e0b" },
        { name: "Tiled (Terracotta)", value: stats.roof_distribution.Tiled, color: "#ef4444" },
        { name: "Tin (Metal Sheet)", value: stats.roof_distribution.Tin, color: "#06b6d4" },
        { name: "Other", value: stats.roof_distribution.Other, color: "#64748b" },
      ]
    : [];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 border-b border-[#2a3854] pb-4">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <BarChart3 className="w-5 h-5 text-sky-400" />
            Geospatial AI Analytics & Change Detection
          </h2>
          <p className="text-xs text-slate-400">
            Comprehensive feature distributions, roof material metrics, AI confidence stats, and survey temporal change monitoring.
          </p>
        </div>

        {/* Village Selector Dropdown */}
        <div className="flex items-center space-x-2">
          <span className="text-xs font-semibold text-slate-300">Select Village:</span>
          <select
            value={selectedAnalysisId}
            onChange={(e) => setSelectedAnalysisId(e.target.value)}
            className="px-3 py-1.5 bg-[#161f33] border border-[#2a3854] rounded text-xs text-white focus:outline-none focus:border-sky-500"
          >
            {analyses.map((a) => (
              <option key={a.id} value={a.id}>
                {a.village_name} ({a.original_filename})
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Top Metrics Cards */}
      {stats && (
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div className="gis-card p-4 flex items-center space-x-4 border-l-4 border-l-amber-500">
            <div className="p-3 bg-amber-950/80 rounded text-amber-400">
              <Building2 className="w-6 h-6" />
            </div>
            <div>
              <div className="text-xl font-bold text-white">
                {stats.buildings_detected} Buildings ({stats.total_building_area_sqm} m²)
              </div>
              <div className="text-xs text-slate-400">Building Footprint Inventory</div>
            </div>
          </div>

          <div className="gis-card p-4 flex items-center space-x-4 border-l-4 border-l-cyan-500">
            <div className="p-3 bg-cyan-950/80 rounded text-cyan-400">
              <Milestone className="w-6 h-6" />
            </div>
            <div>
              <div className="text-xl font-bold text-white">
                {stats.roads_detected} Corridors ({stats.total_road_length_m} m)
              </div>
              <div className="text-xs text-slate-400">Road Corridor Length</div>
            </div>
          </div>

          <div className="gis-card p-4 flex items-center space-x-4 border-l-4 border-l-blue-500">
            <div className="p-3 bg-blue-950/80 rounded text-blue-400">
              <Waves className="w-6 h-6" />
            </div>
            <div>
              <div className="text-xl font-bold text-white">
                {stats.waterbodies_detected} Bodies ({stats.total_waterbody_area_sqm} m²)
              </div>
              <div className="text-xs text-slate-400">Waterbodies Surface Area</div>
            </div>
          </div>
        </div>
      )}

      {/* Middle Row: Roof Distribution Pie Chart & Confidence Breakdown */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Roof Distribution Chart */}
        <div className="gis-card p-5 space-y-4">
          <h3 className="font-bold text-white text-sm border-b border-[#2a3854] pb-2 flex items-center justify-between">
            <span>Roof Classification Material Share</span>
            <PieIcon className="w-4 h-4 text-sky-400" />
          </h3>

          <div className="h-[280px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={roofPieData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={90}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {roofPieData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{ backgroundColor: "#0f172a", borderColor: "#2a3854", borderRadius: "6px", fontSize: "12px" }}
                />
                <Legend formatter={(value) => <span className="text-slate-300 text-xs">{value}</span>} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Confidence Metrics */}
        <div className="gis-card p-5 space-y-4">
          <h3 className="font-bold text-white text-sm border-b border-[#2a3854] pb-2 flex items-center justify-between">
            <span>AI Model Confidence Metrics</span>
            <ShieldAlert className="w-4 h-4 text-sky-400" />
          </h3>

          {stats?.confidence_breakdown && (
            <div className="space-y-4 pt-2">
              <div className="p-3 bg-[#0f172a] rounded border border-[#2a3854] flex justify-between items-center">
                <span className="text-xs text-slate-300 font-semibold">Average Model Confidence:</span>
                <span className="text-lg font-bold text-emerald-400 font-mono">
                  {(stats.confidence_breakdown.average * 100).toFixed(1)}%
                </span>
              </div>

              <div className="space-y-2 text-xs">
                <div className="flex justify-between items-center p-2 bg-[#0f172a] rounded border border-[#2a3854]">
                  <span className="text-emerald-400 font-semibold">High Confidence (&gt;85%):</span>
                  <span className="font-mono text-white font-bold">{stats.confidence_breakdown.high} detections</span>
                </div>

                <div className="flex justify-between items-center p-2 bg-[#0f172a] rounded border border-[#2a3854]">
                  <span className="text-amber-400 font-semibold">Medium Confidence (70-85%):</span>
                  <span className="font-mono text-white font-bold">{stats.confidence_breakdown.medium} detections</span>
                </div>

                <div className="flex justify-between items-center p-2 bg-[#0f172a] rounded border border-[#2a3854]">
                  <span className="text-red-400 font-semibold">Low Confidence (&lt;70% - Requires Review):</span>
                  <span className="font-mono text-white font-bold">{stats.confidence_breakdown.low} detections</span>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Bottom Section: Temporal Change Detection Comparison Tool */}
      <div className="gis-card p-6 space-y-5 border-t-4 border-t-sky-500">
        <div>
          <h3 className="text-base font-bold text-white flex items-center gap-2">
            <ArrowLeftRight className="w-5 h-5 text-sky-400" />
            Survey Temporal Change Monitoring (Prototype Tool)
          </h3>
          <p className="text-xs text-slate-400 mt-1">
            Compare two temporal drone survey orthophotos (Previous Survey vs Current Survey) to automatically detect new buildings, expanded structures, and removed features.
          </p>
        </div>

        <form onSubmit={handleRunChangeDetection} className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="p-4 bg-[#0f172a] border border-[#2a3854] rounded space-y-2">
            <label className="text-xs font-semibold text-slate-300 block">1. Upload Previous Survey Image</label>
            <input
              type="file"
              accept="image/*"
              onChange={(e) => setPrevFile(e.target.files?.[0] || null)}
              className="w-full text-xs text-slate-400 file:mr-3 file:py-1.5 file:px-3 file:rounded file:border-0 file:text-xs file:bg-sky-950 file:text-sky-400 border border-[#2a3854] rounded"
            />
          </div>

          <div className="p-4 bg-[#0f172a] border border-[#2a3854] rounded space-y-2">
            <label className="text-xs font-semibold text-slate-300 block">2. Upload Current Survey Image</label>
            <input
              type="file"
              accept="image/*"
              onChange={(e) => setCurrFile(e.target.files?.[0] || null)}
              className="w-full text-xs text-slate-400 file:mr-3 file:py-1.5 file:px-3 file:rounded file:border-0 file:text-xs file:bg-sky-950 file:text-sky-400 border border-[#2a3854] rounded"
            />
          </div>

          <div className="md:col-span-2">
            <button
              type="submit"
              disabled={!prevFile || !currFile || changeLoading}
              className="w-full py-2.5 bg-sky-600 hover:bg-sky-500 text-white rounded text-xs font-bold transition-all disabled:opacity-50 flex items-center justify-center space-x-2"
            >
              {changeLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4" />}
              <span>{changeLoading ? "Running Temporal Change Analysis..." : "Execute Change Detection Pipeline"}</span>
            </button>
          </div>
        </form>

        {changeResults && (
          <div className="p-4 bg-[#0f172a] border border-sky-500/40 rounded space-y-3">
            <div className="flex items-center justify-between border-b border-[#2a3854] pb-2">
              <span className="font-bold text-white text-xs">{changeResults.label}</span>
              <span className="text-xs text-emerald-400 font-mono">
                Total Changed Area: {changeResults.total_changed_area_sqm} m²
              </span>
            </div>

            <div className="grid grid-cols-3 gap-3 text-center text-xs font-mono">
              <div className="p-2 bg-emerald-950/60 border border-emerald-800 rounded text-emerald-300">
                <div className="text-lg font-bold">{changeResults.new_buildings}</div>
                <div>New Structures</div>
              </div>
              <div className="p-2 bg-amber-950/60 border border-amber-800 rounded text-amber-300">
                <div className="text-lg font-bold">{changeResults.expanded_buildings}</div>
                <div>Expanded Footprints</div>
              </div>
              <div className="p-2 bg-red-950/60 border border-red-800 rounded text-red-300">
                <div className="text-lg font-bold">{changeResults.removed_structures}</div>
                <div>Removed Structures</div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
