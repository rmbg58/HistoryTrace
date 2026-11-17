import "./styles/tokens.css";
import "./styles/app.css";

import { renderPanel } from "./components/lineage-card";
import { renderTimeline } from "./components/timeline";
import type { Dynasty, LineageEntry } from "./lib/lineage";
import { addPlaces, flyTo, initMap, refreshMarkers } from "./map/stage";
import { getState, selectPlace, setState, subscribe, type PlaceMeta } from "./state";

interface IndexPayload {
  dynasties: Dynasty[];
  places: PlaceMeta[];
  counts: Record<string, unknown>;
}

async function fetchJson<T>(url: string): Promise<T> {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`${url} → ${res.status}`);
  return (await res.json()) as T;
}

async function loadLineage(id: string): Promise<LineageEntry[]> {
  const data = await fetchJson<{ lineage: LineageEntry[] }>(`./data/lineages/${id}.json`);
  return data.lineage;
}

async function bootstrap(): Promise<void> {
  const index = await fetchJson<IndexPayload>("./data/index.json");
  const ids = index.places.map((p) => p.id);
  const lineages = await Promise.all(ids.map(loadLineage));
  const lineageMap = new Map<string, LineageEntry[]>();
  ids.forEach((id, i) => lineageMap.set(id, lineages[i] ?? []));

  setState({
    dynasties: index.dynasties,
    places: index.places,
    lineages: lineageMap,
    selectedPlaceId: "plc_xian", // 默认展示示范沿革
  });

  const map = initMap(document.getElementById("map")!);
  map.on("load", () => {
    addPlaces(index.places, (id) => {
      selectPlace(id);
      const place = getState().places.find((p) => p.id === id);
      if (place) flyTo(place);
    });
  });

  renderTimeline(document.getElementById("timeline")!);
  renderPanel(document.getElementById("panel")!);

  subscribe(() => {
    renderTimeline(document.getElementById("timeline")!);
    renderPanel(document.getElementById("panel")!);
    refreshMarkers();
  });

  // 面板城名列表 → 选中联动
  document.addEventListener("ht:select-place", (ev) => {
    const id = (ev as CustomEvent<string>).detail;
    selectPlace(id);
    const place = getState().places.find((p) => p.id === id);
    if (place) flyTo(place);
  });

  document.querySelector(".loading")?.classList.add("is-done");
  window.setTimeout(() => document.querySelector(".loading")?.remove(), 300);
}

bootstrap().catch((err) => {
  console.error(err);
  const el = document.querySelector(".loading");
  if (el) {
    el.textContent = "数据载入失败 — 先运行 uv run ht build";
    el.classList.remove("is-done");
  }
});
