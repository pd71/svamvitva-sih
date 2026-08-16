"use client";

import { useEffect, useState } from "react";
import dynamic from "next/dynamic";
import { Map as MapIcon, Layers, Info, Filter, ShieldCheck, Compass } from "lucide-react";

// Dynamically import Leaflet GIS map with SSR disabled
const GISMapComponent = dynamic(() => import("@/components/gis/GISMapComponent"), {
  ssr: false,
  loading: () => (
    <div className="w-full h-[650px] bg-[#0b1120] rounded-lg border border-[#2a3854] flex items-center justify-center text-slate-400 text-sm">
      Initializing Leaflet GIS Engine...
    </div>
  ),
});

import { getApiUrl } from "@/lib/api";

export default function GISViewPage() {
  const [analyses, setAnalyses] = useState<any[]>([]);
  const [selectedAnalysisId, setSelectedAnalysisId] = useState<string>("");
  const [analysis, setAnalysis] = useState<any>(null);
  const [features, setFeatures] = useState<any>(null);
  const [selectedFeature, setSelectedFeature] = useState<any>(null);

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

    const loadData = async () => {
      try {
        const resA = await fetch(getApiUrl(`/api/analysis/${selectedAnalysisId}`));
        if (resA.ok) {
          const dataA = await resA.json();
          setAnalysis(dataA);
        }

        const resF = await fetch(getApiUrl(`/api/analysis/${selectedAnalysisId}/features`));
        if (resF.ok) {
          const dataF = await resF.json();
          setFeatures(dataF);
        }
      } catch (err) {
        console.error(err);
      }
    };

    loadData();
  }, [selectedAnalysisId]);


  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 border-b border-[#2a3854] pb-4">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <MapIcon className="w-5 h-5 text-sky-400" />
            Interactive GIS Map & Spatial Intelligence
          </h2>
          <p className="text-xs text-slate-400">
            Select village orthophotos to inspect spatial vector layers, roof attributes, and local coordinate bounds.
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

      {/* Main Map + Sidebar Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Map Container */}
        <div className="lg:col-span-3 space-y-4">
          <div className="gis-card p-3 relative">
            {/* Coordinate / CRS Badge */}
            <div className="absolute top-6 left-6 z-[400] bg-slate-950/90 backdrop-blur-sm border border-sky-500/40 rounded px-3 py-1.5 text-xs text-sky-300 font-mono shadow-xl flex items-center space-x-2">
              <Compass className="w-4 h-4 text-sky-400 animate-spin" />
              <span>CRS: {analysis?.crs_name || "Demo / Local Coordinates"}</span>
            </div>

            {analysis && (
              <GISMapComponent
                analysis={analysis}
                features={features}
                onSelectFeature={(feat) => setSelectedFeature(feat)}
              />
            )}
          </div>
        </div>

        {/* GIS Controls & Legend Sidebar */}
        <div className="space-y-4">
          {/* Legend Box */}
          <div className="gis-card p-5 space-y-4">
            <h3 className="font-bold text-white text-sm border-b border-[#2a3854] pb-2 flex items-center justify-between">
              <span>Map Symbology Legend</span>
              <Layers className="w-4 h-4 text-sky-400" />
            </h3>

            <div className="space-y-2.5 text-xs">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <span className="w-3.5 h-3.5 rounded bg-amber-500 border border-amber-300"></span>
                  <span className="text-slate-200">RCC (Concrete Roof)</span>
                </div>
                <span className="text-[10px] text-slate-400 font-mono">Building</span>
              </div>

              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <span className="w-3.5 h-3.5 rounded bg-red-500 border border-red-300"></span>
                  <span className="text-slate-200">Tiled (Terracotta Roof)</span>
                </div>
                <span className="text-[10px] text-slate-400 font-mono">Building</span>
              </div>

              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <span className="w-3.5 h-3.5 rounded bg-cyan-500 border border-cyan-300"></span>
                  <span className="text-slate-200">Tin (Corrugated Metal)</span>
                </div>
                <span className="text-[10px] text-slate-400 font-mono">Building</span>
              </div>

              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <span className="w-3.5 h-3.5 rounded bg-slate-500 border border-slate-300"></span>
                  <span className="text-slate-200">Other / Traditional</span>
                </div>
                <span className="text-[10px] text-slate-400 font-mono">Building</span>
              </div>

              <div className="border-t border-[#2a3854] my-2"></div>

              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <span className="w-4 h-1 bg-amber-500 rounded"></span>
                  <span className="text-slate-200">Road Corridor Network</span>
                </div>
                <span className="text-[10px] text-slate-400 font-mono">LineString</span>
              </div>

              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <span className="w-3.5 h-3.5 rounded bg-sky-500 border border-sky-300"></span>
                  <span className="text-slate-200">Waterbody / River</span>
                </div>
                <span className="text-[10px] text-slate-400 font-mono">Polygon</span>
              </div>
            </div>
          </div>

          {/* Selected Feature Attributes Panel */}
          <div className="gis-card p-5 space-y-3">
            <h3 className="font-bold text-white text-sm border-b border-[#2a3854] pb-2 flex items-center justify-between">
              <span>Feature Attribute Inspector</span>
              <Info className="w-4 h-4 text-sky-400" />
            </h3>

            {selectedFeature ? (
              <div className="space-y-2 text-xs font-mono">
                <div className="p-2 bg-[#0f172a] rounded border border-[#2a3854]">
                  <span className="text-slate-400">Category: </span>
                  <span className="text-sky-400 font-bold">{selectedFeature.properties.category}</span>
                </div>

                {selectedFeature.properties.category === "Building" && (
                  <>
                    <div className="p-2 bg-[#0f172a] rounded border border-[#2a3854] flex justify-between">
                      <span className="text-slate-400">Building ID:</span>
                      <span className="text-white font-bold">#{selectedFeature.properties.building_index}</span>
                    </div>

                    <div className="p-2 bg-[#0f172a] rounded border border-[#2a3854] flex justify-between">
                      <span className="text-slate-400">Roof Classification:</span>
                      <span className="text-amber-400 font-bold">{selectedFeature.properties.roof_type}</span>
                    </div>

                    <div className="p-2 bg-[#0f172a] rounded border border-[#2a3854] flex justify-between">
                      <span className="text-slate-400">Footprint Area:</span>
                      <span className="text-white font-bold">{selectedFeature.properties.area_sqm} m²</span>
                    </div>

                    <div className="p-2 bg-[#0f172a] rounded border border-[#2a3854] flex justify-between">
                      <span className="text-slate-400">AI Confidence:</span>
                      <span className="text-emerald-400 font-bold">
                        {(selectedFeature.properties.confidence * 100).toFixed(1)}%
                      </span>
                    </div>
                  </>
                )}

                {selectedFeature.properties.category === "Road" && (
                  <div className="p-2 bg-[#0f172a] rounded border border-[#2a3854] flex justify-between">
                    <span className="text-slate-400">Length:</span>
                    <span className="text-amber-400 font-bold">{selectedFeature.properties.length_m} m</span>
                  </div>
                )}

                {selectedFeature.properties.category === "Waterbody" && (
                  <div className="p-2 bg-[#0f172a] rounded border border-[#2a3854] flex justify-between">
                    <span className="text-slate-400">Surface Area:</span>
                    <span className="text-sky-400 font-bold">{selectedFeature.properties.area_sqm} m²</span>
                  </div>
                )}
              </div>
            ) : (
              <div className="py-8 text-center text-xs text-slate-500">
                Click any vector feature on the map to inspect its spatial and classification metadata.
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
