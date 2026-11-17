/** 地图舞台:MapLibre + 宣纸底 + HTML 城邑标记(名称随时间轴变化)。 */

import maplibregl from "maplibre-gl";
import type { Feature, FeatureCollection } from "geojson";
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

/* ---- 疆界图层(Cliopatria 示意边界,参考层) ---- */

const BOUNDARY_FILL = "rgba(163, 129, 79, 0.07)"; // 赭石淡彩
const BOUNDARY_LINE = "rgba(47, 43, 38, 0.55)"; // 墨线
const GHOST_LINE = "rgba(74, 68, 60, 0.22)"; // 幽灵边界(前朝)

export function installBoundaryLayers(
  currentFC: FeatureCollection,
  ghostFC: FeatureCollection | null,
): void {
  if (!map) return;
  if (!map.getSource("polities")) {
    map.addSource("polities", { type: "geojson", data: currentFC });
    map.addSource("polities-ghost", { type: "geojson", data: emptyFC() });
    map.addLayer({
      id: "polities-fill",
      type: "fill",
      source: "polities",
      paint: { "fill-color": BOUNDARY_FILL },
    });
    map.addLayer({
      id: "polities-line",
      type: "line",
      source: "polities",
      paint: { "line-color": BOUNDARY_LINE, "line-width": 1.4 },
    });
    map.addLayer({
      id: "polities-ghost-line",
      type: "line",
      source: "polities-ghost",
      paint: { "line-color": GHOST_LINE, "line-width": 1, "line-dasharray": [2, 3] },
    });
  } else {
    (map.getSource("polities") as maplibregl.GeoJSONSource).setData(currentFC);
    (map.getSource("polities-ghost") as maplibregl.GeoJSONSource).setData(ghostFC ?? emptyFC());
  }
}

function emptyFC(): FeatureCollection {
  return { type: "FeatureCollection", features: [] };
}

export function toFeatureCollection(features: unknown[]): FeatureCollection {
  return {
    type: "FeatureCollection",
    features: features as Feature[],
  };
}

export function flyTo(place: PlaceMeta): void {
  map?.flyTo({ center: [place.lng, place.lat], zoom: Math.max(map.getZoom(), 5.5), duration: 400 });
}

/* ---- 事件落点(朱砂印章) ---- */

const eventMarkers = new Map<string, { marker: maplibregl.Marker; el: HTMLElement }>();

export function setEvents(
  events: { id: string; year: number; lng: number | null; lat: number | null; name: string }[],
  onPick: (id: string) => void,
): void {
  if (!map) return;
  const seen = new Set<string>();
  for (const ev of events) {
    if (ev.lng === null || ev.lat === null) continue;
    seen.add(ev.id);
    if (eventMarkers.has(ev.id)) continue;
    const el = document.createElement("div");
    el.className = "ev-marker";
    el.textContent = "事";
    el.title = `${ev.name}(${ev.year})`;
    el.setAttribute("role", "button");
    el.setAttribute("tabindex", "0");
    el.addEventListener("click", () => onPick(ev.id));
    el.addEventListener("keydown", (k) => {
      if (k.key === "Enter") onPick(ev.id);
    });
    const marker = new maplibregl.Marker({ element: el, anchor: "center" })
      .setLngLat([ev.lng, ev.lat])
      .addTo(map);
    eventMarkers.set(ev.id, { marker, el });
  }
  for (const [id, m] of eventMarkers) {
    if (!seen.has(id)) {
      m.marker.remove();
      eventMarkers.delete(id);
    }
  }
  refreshEventDim();
}

/** 当前朝代期内的事件高亮(朱),其余淡墨。 */
export function refreshEventDim(): void {
  const { events, year, dynasties } = getState();
  const cur = dynasties.find((d) => year >= d.earliest && year <= d.latest);
  for (const [id, m] of eventMarkers) {
    const ev = events.find((e) => e.id === id);
    const inDyn = cur && ev && ev.year >= cur.earliest && ev.year <= cur.latest;
    m.el.classList.toggle("is-dim", !inDyn);
  }
}

/* ---- 诗人行迹(淡金线 + 站点) ---- */

let fpLine = false;
const fpMarkers: maplibregl.Marker[] = [];

export function setFootprint(
  stops: { year: number; lng: number | null; lat: number | null; name: string }[],
  color: string,
  pick: (idx: number) => void,
): void {
  if (!map) return;
  clearFootprint();
  const pts = stops.filter((s) => s.lng !== null && s.lat !== null) as { year: number; lng: number; lat: number; name: string }[];
  if (pts.length === 0) return;
  const fc: FeatureCollection = {
    type: "FeatureCollection",
    features: [
      {
        type: "Feature",
        properties: {},
        geometry: { type: "LineString", coordinates: pts.map((p) => [p.lng, p.lat]) },
      },
    ],
  };
  map.addSource("footprint", { type: "geojson", data: fc });
  map.addLayer({
    id: "footprint-line",
    type: "line",
    source: "footprint",
    paint: { "line-color": color, "line-width": 1.6, "line-dasharray": [1.5, 2] },
  });
  fpLine = true;
  for (const s of pts) {
    const el = document.createElement("div");
    el.className = "fp-stop";
    el.style.background = color;
    const label = document.createElement("span");
    label.className = "fp-label";
    label.textContent = `${s.name}·${s.year}`;
    const dot = document.createElement("span");
    dot.className = "fp-dot";
    el.append(dot, label);
    const idx = stops.indexOf(s);
    el.addEventListener("click", () => pick(idx));
    const marker = new maplibregl.Marker({ element: el, anchor: "center" })
      .setLngLat([s.lng, s.lat])
      .addTo(map);
    fpMarkers.push(marker);
  }
}

export function clearFootprint(): void {
  if (!map) return;
  if (fpLine) {
    map.getLayer("footprint-line") && map.removeLayer("footprint-line");
    map.getSource("footprint") && map.removeSource("footprint");
    fpLine = false;
  }
  for (const m of fpMarkers) m.remove();
  fpMarkers.length = 0;
}

/* ---- 作品气泡(墨笺) ---- */

export function showWorkPopup(lng: number, lat: number, html: string): void {
  if (!map) return;
  // 同屏只保留一个气泡(播放时逐站弹出)
  for (const p of document.querySelectorAll(".maplibregl-popup")) p.remove();
  new maplibregl.Popup({ closeButton: false, maxWidth: "300px", offset: 14 })
    .setLngLat([lng, lat])
    .setDOMContent(htmlToEl(html))
    .addTo(map);
}

function htmlToEl(html: string): HTMLElement {
  const d = document.createElement("div");
  d.innerHTML = html;
  return d;
}

export function flyToCoords(lng: number, lat: number, zoom = 5.5): void {
  map?.flyTo({ center: [lng, lat], zoom: Math.max(map?.getZoom() ?? 0, zoom), duration: 400 });
}
