/** 地图舞台:MapLibre + 宣纸底 + HTML 城邑标记(名称随时间轴变化)。 */

import maplibregl from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";
import { entryForYear, isCapitalRole } from "../lib/lineage";
import { getState, type PlaceMeta } from "../state";

let map: maplibregl.Map | null = null;
const markers = new Map<string, { marker: maplibregl.Marker; label: HTMLElement; dot: HTMLElement; place: PlaceMeta }>();

const PAPER = "#f6f1e3";

export function initMap(container: HTMLElement): maplibregl.Map {
  map = new maplibregl.Map({
    container,
    style: {
      version: 8,
      sources: {},
      layers: [{ id: "paper", type: "background", paint: { "background-color": PAPER } }],
    },
    center: [105, 36],
    zoom: 4.2,
    minZoom: 3,
    maxZoom: 9,
    attributionControl: false,
    // 宣纸风格:禁默认倾斜/旋转,保持稳定阅读
    pitchWithRotate: false,
    dragRotate: false,
  });
  return map;
}

export function addPlaces(places: PlaceMeta[], onPick: (id: string) => void): void {
  if (!map) throw new Error("map 未初始化");
  for (const place of places) {
    const el = document.createElement("div");
    el.className = "marker";
    el.setAttribute("role", "button");
    el.setAttribute("tabindex", "0");
    el.setAttribute("aria-label", place.name);

    const dot = document.createElement("span");
    dot.className = "dot";
    const label = document.createElement("span");
    label.className = "label";
    el.append(dot, label);

    el.addEventListener("click", () => onPick(place.id));
    el.addEventListener("keydown", (ev) => {
      if (ev.key === "Enter" || ev.key === " ") {
        ev.preventDefault();
        onPick(place.id);
      }
    });

    const marker = new maplibregl.Marker({ element: el, anchor: "bottom" })
      .setLngLat([place.lng, place.lat])
      .addTo(map);
    markers.set(place.id, { marker, label, dot, place });
  }
  refreshMarkers();
}

/** 依当前年份刷新所有标记的古名与都城态。 */
export function refreshMarkers(): void {
  const { lineages, year, selectedPlaceId } = getState();
  for (const { marker, label, dot, place } of markers.values()) {
    const entries = lineages.get(place.id) ?? [];
    const active = entryForYear(entries, year);
    label.textContent = active ? active.name : place.name;
    const capital = active ? isCapitalRole(active.role) : false;
    dot.parentElement?.classList.toggle("is-capital", capital);
    marker.getElement().classList.toggle("is-active", selectedPlaceId === place.id);
  }
}

export function flyTo(place: PlaceMeta): void {
  map?.flyTo({ center: [place.lng, place.lat], zoom: Math.max(map.getZoom(), 5.5), duration: 400 });
}
