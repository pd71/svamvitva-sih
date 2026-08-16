"use client";

import { useEffect, useState } from "react";
import { CheckSquare, CheckCircle2, XCircle, Edit3, ShieldAlert, Save, RefreshCw } from "lucide-react";
import { getApiUrl } from "@/lib/api";

export default function ReviewPage() {
  const [analyses, setAnalyses] = useState<any[]>([]);
  const [selectedAnalysisId, setSelectedAnalysisId] = useState<string>("");
  const [analysisDetail, setAnalysisDetail] = useState<any>(null);
  const [confidenceThreshold, setConfidenceThreshold] = useState<number>(85);
  
  const [updatingBuildingId, setUpdatingBuildingId] = useState<string | null>(null);
  const [editRoofMap, setEditRoofMap] = useState<Record<string, string>>({});
  const [commentMap, setCommentMap] = useState<Record<string, string>>({});

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

  const fetchDetail = async (id: string) => {
    try {
      const res = await fetch(getApiUrl(`/api/analysis/${id}`));
      if (res.ok) {
        const data = await res.json();
        setAnalysisDetail(data);
      }
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    if (selectedAnalysisId) {
      fetchDetail(selectedAnalysisId);
    }
  }, [selectedAnalysisId]);

  const handleReviewAction = async (buildingId: string, status: string) => {
    setUpdatingBuildingId(buildingId);
    try {
      const updatedRoof = editRoofMap[buildingId];
      const comments = commentMap[buildingId];

      const res = await fetch(getApiUrl(`/api/features/${buildingId}/review`), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          building_id: buildingId,
          updated_roof_type: updatedRoof,
          status: status,
          comments: comments
        })
      });

      if (res.ok) {
        // Refresh detail list
        fetchDetail(selectedAnalysisId);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setUpdatingBuildingId(null);
    }
  };

  // Filter low-confidence or unreviewed buildings
  const reviewQueue = analysisDetail?.buildings
    ? analysisDetail.buildings.filter((b: any) => (b.confidence * 100) <= confidenceThreshold || b.status !== "detected")
    : [];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 border-b border-[#2a3854] pb-4">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <CheckSquare className="w-5 h-5 text-sky-400" />
            Human-in-the-Loop AI Detection Review Queue
          </h2>
          <p className="text-xs text-slate-400">
            Manual verification workflow for low-confidence feature segmentations and roof classifications before official SVAMITVA map GIS commit.
          </p>
        </div>

        {/* Controls */}
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <span className="text-xs font-semibold text-slate-300">Confidence Threshold:</span>
            <select
              value={confidenceThreshold}
              onChange={(e) => setConfidenceThreshold(Number(e.target.value))}
              className="px-2.5 py-1.5 bg-[#161f33] border border-[#2a3854] rounded text-xs text-white"
            >
              <option value={90}>&le; 90% (Strict Review)</option>
              <option value={85}>&le; 85% (Recommended)</option>
              <option value={75}>&le; 75% (Low Confidence)</option>
            </select>
          </div>

          <div className="flex items-center space-x-2">
            <span className="text-xs font-semibold text-slate-300">Village:</span>
            <select
              value={selectedAnalysisId}
              onChange={(e) => setSelectedAnalysisId(e.target.value)}
              className="px-3 py-1.5 bg-[#161f33] border border-[#2a3854] rounded text-xs text-white"
            >
              {analyses.map((a) => (
                <option key={a.id} value={a.id}>
                  {a.village_name}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Review Queue Cards */}
      <div className="gis-card p-5 space-y-4">
        <div className="flex items-center justify-between border-b border-[#2a3854] pb-3">
          <div className="flex items-center space-x-2">
            <ShieldAlert className="w-5 h-5 text-amber-400" />
            <h3 className="font-bold text-white text-sm">
              Review Queue Candidates ({reviewQueue.length} Detections)
            </h3>
          </div>
          <button onClick={() => fetchDetail(selectedAnalysisId)} className="text-xs text-slate-400 hover:text-sky-400 flex items-center gap-1">
            <RefreshCw className="w-3.5 h-3.5" />
            <span>Reload</span>
          </button>
        </div>

        {reviewQueue.length === 0 ? (
          <div className="py-12 text-center text-slate-400 text-xs">
            All detections in this survey satisfy the confidence threshold (&gt;{confidenceThreshold}%).
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {reviewQueue.map((bldg: any) => {
              const currentRoof = editRoofMap[bldg.id] || bldg.roof_type;
              const isUpdating = updatingBuildingId === bldg.id;

              return (
                <div
                  key={bldg.id}
                  className={`p-4 rounded border transition-all ${
                    bldg.status === "approved"
                      ? "bg-emerald-950/40 border-emerald-800"
                      : bldg.status === "rejected"
                      ? "bg-red-950/40 border-red-800"
                      : "bg-[#0f172a] border-[#2a3854]"
                  }`}
                >
                  <div className="flex items-center justify-between border-b border-[#2a3854] pb-2">
                    <div className="flex items-center space-x-2">
                      <span className="font-bold text-white text-sm">Building #{bldg.building_index}</span>
                      <span className="text-[10px] px-2 py-0.5 rounded font-mono bg-sky-950 text-sky-400 border border-sky-800">
                        Area: {bldg.area_sqm} m²
                      </span>
                    </div>

                    <div className="flex items-center space-x-2">
                      <span className={`text-[10px] px-2 py-0.5 rounded font-bold uppercase ${
                        bldg.status === 'approved' ? 'bg-emerald-900 text-emerald-300' :
                        bldg.status === 'rejected' ? 'bg-red-900 text-red-300' : 'bg-amber-900 text-amber-300'
                      }`}>
                        {bldg.status}
                      </span>
                      <span className="text-xs font-mono font-bold text-amber-400">
                        {(bldg.confidence * 100).toFixed(1)}% Conf
                      </span>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-3 py-3 text-xs">
                    <div>
                      <label className="text-slate-400 text-[10px] block">Roof Classification</label>
                      <select
                        value={currentRoof}
                        onChange={(e) => setEditRoofMap({ ...editRoofMap, [bldg.id]: e.target.value })}
                        className="w-full mt-1 px-2 py-1 bg-[#161f33] border border-[#2a3854] rounded text-white text-xs"
                      >
                        <option value="RCC">RCC (Concrete)</option>
                        <option value="Tiled">Tiled (Terracotta)</option>
                        <option value="Tin">Tin (Metal Sheet)</option>
                        <option value="Other">Other / Traditional</option>
                      </select>
                    </div>

                    <div>
                      <label className="text-slate-400 text-[10px] block">Centroid Coordinates</label>
                      <div className="mt-1 font-mono text-slate-300 p-1 bg-[#161f33] rounded border border-[#2a3854] text-[11px]">
                        ({bldg.centroid_x.toFixed(1)}, {bldg.centroid_y.toFixed(1)})
                      </div>
                    </div>
                  </div>

                  <div className="space-y-2 pt-1">
                    <input
                      type="text"
                      placeholder="Add reviewer notes / ground-truth remarks..."
                      value={commentMap[bldg.id] || bldg.review_notes || ""}
                      onChange={(e) => setCommentMap({ ...commentMap, [bldg.id]: e.target.value })}
                      className="w-full px-2.5 py-1.5 bg-[#161f33] border border-[#2a3854] rounded text-xs text-white placeholder-slate-500"
                    />

                    <div className="flex items-center space-x-2 pt-2">
                      <button
                        onClick={() => handleReviewAction(bldg.id, "approved")}
                        disabled={isUpdating}
                        className="flex-1 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded text-xs font-semibold flex items-center justify-center space-x-1"
                      >
                        <CheckCircle2 className="w-3.5 h-3.5" />
                        <span>Approve</span>
                      </button>

                      <button
                        onClick={() => handleReviewAction(bldg.id, "rejected")}
                        disabled={isUpdating}
                        className="flex-1 py-1.5 bg-red-600 hover:bg-red-500 text-white rounded text-xs font-semibold flex items-center justify-center space-x-1"
                      >
                        <XCircle className="w-3.5 h-3.5" />
                        <span>Reject</span>
                      </button>

                      <button
                        onClick={() => handleReviewAction(bldg.id, "edited")}
                        disabled={isUpdating}
                        className="flex-1 py-1.5 bg-sky-600 hover:bg-sky-500 text-white rounded text-xs font-semibold flex items-center justify-center space-x-1"
                      >
                        <Save className="w-3.5 h-3.5" />
                        <span>Save Edit</span>
                      </button>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
