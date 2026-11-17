import "./styles/tokens.css";
import "./styles/app.css";

import { renderPanel } from "./components/panel";
import { renderTimeline } from "./components/timeline";
import type { Dynasty, LineageEntry } from "./lib/lineage";
import {
  addPlaces,
  clearFootprint,
  flyTo,
  flyToCoords,
  initMap,
  installBoundaryLayers,
  refreshEventDim,
  refreshMarkers,
  setEvents,
  setFootprint,
  showWorkPopup,
  toFeatureCollection,
} from "./map/stage";
import {
  getState,
  selectPlace,
  setState,
  subscribe,
  type EventMeta,
  type PlaceMeta,
  type PoetFootprint,
} from "./state";

interface IndexPayload {
  dynasties: Dynasty[];
  places: PlaceMeta[];
  counts: Record<string, unknown>;
}

interface BoundarySnapshot {
  year: number;
  label: string;
  features: unknown[];
}

interface BoundariesPayload {
  meta: Record<string, unknown>;
  snapshots: Record<string, BoundarySnapshot>;
}

const GOLD = "rgba(163, 129, 79, 0.9)"; // 行迹淡金

async function fetchJson<T>(url: string): Promise<T> {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`${url} → ${res.status}`);
  return (await res.json()) as T;
}

async function loadLineage(id: string): Promise<LineageEntry[]> {
  const data = await fetchJson<{ lineage: LineageEntry[] }>(`./data/lineages/${id}.json`);
  return data.lineage;
}

function resolveWorksCoords(footprints: PoetFootprint[], places: PlaceMeta[]): void {
  const byId = new Map(places.map((p) => [p.id, p]));
  for (const poet of footprints) {
    for (const w of poet.works) {
      if (w.lng == null && w.placeId) {
        const p = byId.get(w.placeId);
        if (p) {
          w.lng = p.lng;
          w.lat = p.lat;
          w.placeName = w.placeName ?? p.name;
        }
      }
    }
  }
}

function worksAtStop(poet: PoetFootprint, idx: number): void {
  const stop = poet.stops[idx];
  if (!stop || stop.lng === null || stop.lat === null) return;
  const near = poet.works.filter(
    (w) =>
      w.lng != null &&
      w.lat != null &&
      Math.abs(w.lng - stop.lng!) < 0.7 &&
      Math.abs(w.lat - stop.lat!) < 0.7,
  );
  const html = near.length
    ? `<div class="work-popup"><div class="wp-title">${stop.name}·诗踪</div>${near
        .map(
          (w) =>
            `<div class="wp-item"><b>${w.title}</b>${w.year ? `(${w.year})` : ""}<span class="poem">${w.lines.replace(/\n/g, "<br>")}</span></div>`,
        )
        .join("")}</div>`
    : `<div class="work-popup"><div class="wp-title">${stop.name}</div><div class="wp-item">此站暂无录入名作</div></div>`;
  showWorkPopup(stop.lng, stop.lat, html);
}

let playTimer: ReturnType<typeof setInterval> | null = null;

function playFootprint(poetId: string): void {
  const poet = getState().footprints.find((p) => p.id === poetId);
  if (!poet || poet.stops.length === 0) return;
  if (playTimer) clearInterval(playTimer);
  setState({ activePoetId: poetId, panelTab: "poets" });
  let i = 0;
  const step = (): void => {
    const stop = poet.stops[i];
    if (!stop) {
      if (playTimer) clearInterval(playTimer);
      playTimer = null;
      return;
    }
    setState({ year: stop.year });
    if (stop.lng !== null && stop.lat !== null) {
      flyToCoords(stop.lng, stop.lat, 4.8);
      worksAtStop(poet, i);
    }
    i += 1;
  };
  step();
  playTimer = setInterval(step, 900);
}

async function bootstrap(): Promise<void> {
  const index = await fetchJson<IndexPayload>("./data/index.json");
  const ids = index.places.map((p) => p.id);
  const lineages = await Promise.all(ids.map(loadLineage));
  const lineageMap = new Map<string, LineageEntry[]>();
  ids.forEach((id, i) => lineageMap.set(id, lineages[i] ?? []));

  // 疆界/事件/行迹(可选加载:失败不阻塞主功能)
  let boundaries: BoundariesPayload | null = null;
  let events: EventMeta[] = [];
  let footprints: PoetFootprint[] = [];
  try {
    boundaries = await fetchJson<BoundariesPayload>("./data/boundaries.json");
  } catch {
    console.warn("boundaries.json 加载失败,疆界图层跳过");
  }
  try {
    events = (await fetchJson<{ events: EventMeta[] }>("./data/events.json")).events;
  } catch {
    console.warn("events.json 加载失败,事件层跳过");
  }
  try {
    footprints = (await fetchJson<{ poets: PoetFootprint[] }>("./data/footprints.json")).poets;
    resolveWorksCoords(footprints, index.places);
  } catch {
    console.warn("footprints.json 加载失败,诗人层跳过");
  }

  setState({
    dynasties: index.dynasties,
    places: index.places,
    lineages: lineageMap,
    events,
    footprints,
    selectedPlaceId: "plc_xian", // 默认展示示范沿革
  });

  const map = initMap(document.getElementById("map")!);
  let mapReady = false;

  const applyBoundaries = (): void => {
    if (!boundaries) return;
    const { dynasties, year } = getState();
    const idx = dynasties.findIndex((d) => year >= d.earliest && year <= d.latest);
    const cur = idx >= 0 ? dynasties[idx] : undefined;
    if (!cur) return;
    const prev = idx > 0 ? dynasties[idx - 1] : null;
    const curSnap = boundaries.snapshots[cur.key];
    const ghostSnap = prev ? boundaries.snapshots[prev.key] : null;
    installBoundaryLayers(
      toFeatureCollection(curSnap?.features ?? []),
      ghostSnap ? toFeatureCollection(ghostSnap.features) : null,
    );
  };

  const applyEvents = (): void => {
    setEvents(
      getState().events.map((e) => ({ id: e.id, year: e.year, lng: e.place.lng, lat: e.place.lat, name: e.name })),
      (id) => {
        setState({ activeEventId: id, panelTab: "events" });
        const ev = getState().events.find((e) => e.id === id);
        if (ev?.place.lng != null && ev.place.lat != null) flyToCoords(ev.place.lng, ev.place.lat);
      },
    );
  };

  const applyFootprint = (): void => {
    const { activePoetId, footprints: fps, year } = getState();
    if (!activePoetId) {
      clearFootprint();
      return;
    }
    const poet = fps.find((p) => p.id === activePoetId);
    if (!poet) return;
    const visible = poet.stops.filter((s) => s.year <= year);
    setFootprint(visible, GOLD, (idx) => {
      // idx 相对可见子集;弹作品用全局索引
      const stop = visible[idx];
      if (!stop) return;
      const globalIdx = poet.stops.indexOf(stop);
      if (stop.lng != null && stop.lat != null) {
        flyToCoords(stop.lng, stop.lat, 5);
        worksAtStop(poet, globalIdx);
      }
    });
  };

  const applyAll = (): void => {
    renderTimeline(document.getElementById("timeline")!);
    renderPanel(document.getElementById("panel")!);
    refreshMarkers();
    if (!mapReady) return;
    refreshEventDim();
    applyBoundaries();
    applyEvents();
    applyFootprint();
  };

  subscribe(applyAll);

  map.on("load", () => {
    mapReady = true;
    addPlaces(index.places, (id) => {
      selectPlace(id);
      const place = getState().places.find((p) => p.id === id);
      if (place) flyTo(place);
    });
    applyAll(); // 初始渲染(疆界/事件/行迹)
  });

  // 面板城名列表 → 选中联动
  document.addEventListener("ht:select-place", (ev) => {
    const id = (ev as CustomEvent<string>).detail;
    selectPlace(id);
    const place = getState().places.find((p) => p.id === id);
    if (place) flyTo(place);
  });
  document.addEventListener("ht:fly-coords", (ev) => {
    const { lng, lat } = (ev as CustomEvent<{ lng: number; lat: number }>).detail;
    flyToCoords(lng, lat);
  });
  document.addEventListener("ht:goto-stop", (ev) => {
    const { poetId, idx } = (ev as CustomEvent<{ poetId: string; idx: number }>).detail;
    const poet = getState().footprints.find((p) => p.id === poetId);
    const stop = poet?.stops[idx];
    if (poet && stop) {
      setState({ activePoetId: poetId });
      if (stop.lng !== null && stop.lat !== null) {
        flyToCoords(stop.lng, stop.lat, 5);
        worksAtStop(poet, idx);
      }
    }
  });
  document.addEventListener("ht:play-poet", (ev) => {
    playFootprint((ev as CustomEvent<string>).detail);
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
