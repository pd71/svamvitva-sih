"use client";

import { useEffect, useState } from "react";
import { FileSpreadsheet, Download, FileText, Code2, CheckCircle2, MapPin } from "lucide-react";

export default function ReportsPage() {
  const [analyses, setAnalyses] = useState<any[]>([]);

  useEffect(() => {
    fetchAnalyses();
  }, []);

  const fetchAnalyses = async () => {
    try {
      const res = await fetch("/api/analyses");
      if (res.ok) {
        const data = await res.json();
        setAnalyses(data);
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleDownloadGeoJSON = async (id: string, villageName: string) => {
    try {
      const res = await fetch(`/api/analysis/${id}/features`);
      if (res.ok) {
        const data = await res.json();
        const jsonStr = JSON.stringify(data, null, 2);
        const blob = new Blob([jsonStr], { type: "application/json" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `SVAMITVA_${villageName.replace(/\s+/g, "_")}_features.geojson`;
        a.click();
      }
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="border-b border-[#2a3854] pb-4">
        <h2 className="text-xl font-bold text-white flex items-center gap-2">
          <FileSpreadsheet className="w-5 h-5 text-sky-400" />
          SVAMITVA Automated Report & GIS Export Center
        </h2>
        <p className="text-xs text-slate-400 mt-1">
          Generate executive PDF summary reports, export raw feature CSV inventories, and download GeoJSON vector layers for CAD/QGIS integration.
        </p>
      </div>

      {/* Reports Table / List */}
      <div className="gis-card p-5 space-y-4">
        <h3 className="font-bold text-white text-sm border-b border-[#2a3854] pb-3">
          Completed Village Survey Reports
        </h3>

        {analyses.length === 0 ? (
          <div className="py-12 text-center text-slate-400 text-xs">
            No village survey analyses completed yet.
          </div>
        ) : (
          <div className="space-y-4">
            {analyses.map((item) => (
              <div
                key={item.id}
                className="p-5 rounded bg-[#0f172a] border border-[#2a3854] hover:border-sky-500 transition-all flex flex-col md:flex-row justify-between items-start md:items-center gap-4"
              >
                <div className="space-y-2">
                  <div className="flex items-center space-x-3">
                    <span className="font-bold text-white text-base">{item.village_name}</span>
                    <span className="text-[10px] px-2 py-0.5 rounded font-mono bg-emerald-950 text-emerald-400 border border-emerald-800">
                      {item.status.toUpperCase()}
                    </span>
                    <span className="text-xs text-slate-400">({item.original_filename})</span>
                  </div>

                  <div className="flex flex-wrap items-center gap-4 text-xs font-mono text-slate-300">
                    <span className="text-amber-400">🏢 {item.total_buildings} Buildings</span>
                    <span className="text-cyan-400">🛣️ {item.total_roads_len}m Road</span>
                    <span className="text-blue-400">🌊 {item.total_water_area}m² Water</span>
                    <span className="text-emerald-400">🛡️ {(item.avg_confidence * 100).toFixed(1)}% Conf</span>
                  </div>
                </div>

                <div className="flex flex-wrap items-center gap-2 w-full md:w-auto">
                  {/* PDF Download Button */}
                  <a
                    href={`/api/analysis/${item.id}/report`}
                    target="_blank"
                    rel="noreferrer"
                    className="flex-1 md:flex-initial flex items-center justify-center space-x-1.5 bg-gradient-to-r from-red-600 to-rose-600 hover:from-red-500 text-white px-3.5 py-2 rounded text-xs font-semibold shadow transition-all"
                  >
                    <FileText className="w-4 h-4" />
                    <span>Download PDF</span>
                  </a>

                  {/* CSV Export Button */}
                  <a
                    href={`/api/analysis/${item.id}/export-csv`}
                    target="_blank"
                    rel="noreferrer"
                    className="flex-1 md:flex-initial flex items-center justify-center space-x-1.5 bg-emerald-600 hover:bg-emerald-500 text-white px-3.5 py-2 rounded text-xs font-semibold shadow transition-all"
                  >
                    <Download className="w-4 h-4" />
                    <span>Export CSV</span>
                  </a>

                  {/* GeoJSON Export Button */}
                  <button
                    onClick={() => handleDownloadGeoJSON(item.id, item.village_name)}
                    className="flex-1 md:flex-initial flex items-center justify-center space-x-1.5 bg-sky-600 hover:bg-sky-500 text-white px-3.5 py-2 rounded text-xs font-semibold shadow transition-all"
                  >
                    <Code2 className="w-4 h-4" />
                    <span>GeoJSON</span>
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
