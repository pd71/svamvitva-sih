"use client";

import { useEffect, useState } from "react";
import L from "leaflet";
import "leaflet/dist/leaflet.css";

interface GISMapProps {
  analysis: any;
  features: any;
  onSelectFeature?: (feature: any) => void;
}

export default function GISMapComponent({ analysis, features, onSelectFeature }: GISMapProps) {
  const [map, setMap] = useState<L.Map | null>(null);

  useEffect(() => {
    if (!analysis) return;

    const mapContainer = document.getElementById("leaflet-gis-map");
    if (!mapContainer) return;

    // Destroy previous map instance if exists
    if (map) {
      map.remove();
    }

    // Set CRS based on georeferenced status
    const bounds: L.LatLngBoundsExpression = [
      [0, 0],
      [analysis.height || 1000, analysis.width || 1000]
    ];

    const leafletMap = L.map("leaflet-gis-map", {
      crs: L.CRS.Simple,
      minZoom: -2,
      maxZoom: 3,
      zoomControl: true,
      attributionControl: false
    });

    // Image overlay layer
    const imageUrl = `/api/analysis/${analysis.id}/image`;
    L.imageOverlay(imageUrl, bounds).addTo(leafletMap);
    leafletMap.fitBounds(bounds);

    // Color map for roof types
    const roofColors: Record<string, string> = {
      RCC: "#f59e0b",
      Tiled: "#ef4444",
      Tin: "#06b6d4",
      Other: "#64748b"
    };

    if (features && features.features) {
      L.geoJSON(features, {
        style: (feature) => {
          const category = feature?.properties?.category;
          if (category === "Building") {
            const roof = feature?.properties?.roof_type || "RCC";
            const color = roofColors[roof] || "#10b981";
            return {
              color: color,
              weight: 2,
              fillColor: color,
              fillOpacity: 0.45
            };
          } else if (category === "Road") {
            return {
              color: "#f59e0b",
              weight: 4,
              opacity: 0.9
            };
          } else if (category === "Waterbody") {
            return {
              color: "#0284c7",
              weight: 2,
              fillColor: "#0ea5e9",
              fillOpacity: 0.5
            };
          }
          return { color: "#3388ff" };
        },
        onEachFeature: (feature, layer) => {
          const p = feature.properties;
          let popupContent = "";

          if (p.category === "Building") {
            popupContent = `
              <div style="font-family: sans-serif; font-size: 12px; color: #0f172a; padding: 4px;">
                <b style="font-size: 13px; color: #0ea5e9;">Building #${p.building_index}</b><br/>
                <b>Roof Type:</b> <span style="color: #d97706; font-weight: bold;">${p.roof_type}</span><br/>
                <b>Confidence:</b> ${(p.confidence * 100).toFixed(1)}%<br/>
                <b>Area:</b> ${p.area_sqm} m²<br/>
                <b>Status:</b> ${p.status.toUpperCase()}
              </div>
            `;
          } else if (p.category === "Road") {
            popupContent = `
              <div style="font-family: sans-serif; font-size: 12px; color: #0f172a; padding: 4px;">
                <b style="font-size: 13px; color: #d97706;">Road Corridor #${p.road_index}</b><br/>
                <b>Length:</b> ${p.length_m} m
              </div>
            `;
          } else if (p.category === "Waterbody") {
            popupContent = `
              <div style="font-family: sans-serif; font-size: 12px; color: #0f172a; padding: 4px;">
                <b style="font-size: 13px; color: #0284c7;">Waterbody #${p.waterbody_index}</b><br/>
                <b>Area:</b> ${p.area_sqm} m²
              </div>
            `;
          }

          layer.bindPopup(popupContent);
          layer.on("click", () => {
            if (onSelectFeature) {
              onSelectFeature(feature);
            }
          });
        }
      }).addTo(leafletMap);
    }

    setMap(leafletMap);

    return () => {
      leafletMap.remove();
    };
  }, [analysis, features]);

  return <div id="leaflet-gis-map" className="w-full h-[650px] rounded-lg border border-[#2a3854]" />;
}
