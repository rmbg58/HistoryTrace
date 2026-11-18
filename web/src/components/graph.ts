/** 知识图谱(径向关联图):中心实体 + 环上关联实体,SVG 自绘,点击跳转(反馈6)。 */

import { dynastyForYear, type LineageEntry } from "../lib/lineage";
import { formatYear } from "./timeline";
import { getState, setState, type EventMeta, type PoetFootprint } from "../state";

interface GNode {
  id: string;
  label: string;
  kind: "place" | "poet" | "event" | "work" | "dynasty";
  year?: number;
}
interface GEdge {
  from: string;
  to: string;
  label: string;
}

const KIND_LABEL: Record<GNode["kind"], string> = {
  place: "城",
  poet: "诗人",
  event: "史事",
  work: "作品",
  dynasty: "朝",
};

export function renderGraphTab(body: HTMLElement): void {
  const { places, lineages, selectedPlaceId, footprints, events, year, activePoetId } = getState();
  const place = places.find((p) => p.id === selectedPlaceId);
  const poet = footprints.find((p) => p.id === activePoetId);

  if (place) {
    renderPlaceGraph(body, place, lineages.get(place.id) ?? [], footprints, events);
    return;
  }
  if (poet) {
    renderPoetGraph(body, poet, year);
    return;
  }
  const tip = document.createElement("div");
  tip.className = "panel-empty";
  tip.innerHTML = "点选城邑或诗人<br>观其关联之网";
  body.appendChild(tip);
}

function renderPlaceGraph(
  body: HTMLElement,
  place: { id: string; name: string; lng?: number; lat?: number },
  entries: LineageEntry[],
  footprints: PoetFootprint[],
  events: EventMeta[],
): void {
  const nodes: GNode[] = [{ id: `place:${place.id}`, label: place.name, kind: "place" }];
  const edges: GEdge[] = [];
  const center = `place:${place.id}`;

  for (const e of entries) {
    const d = dynastyForYear(getState().dynasties, Math.floor((e.earliest + e.latest) / 2));
    const nid = `dynasty:${d?.key ?? e.earliest}`;
    if (!nodes.some((n) => n.id === nid)) nodes.push({ id: nid, label: d?.label ?? "", kind: "dynasty" });
    edges.push({ from: center, to: nid, label: e.name });
  }
  for (const ev of events) {
    const d = getState().dynasties.find((x) => ev.year >= x.earliest && ev.year <= x.latest);
    const near =
      ev.place.lng != null && ev.place.lat != null && place?.lng != null && place?.lat != null &&
      Math.abs(ev.place.lng - place.lng) < 1.5 && Math.abs(ev.place.lat - place.lat) < 1.5;
    if (!near) continue;
    const nid = `event:${ev.id}`;
    nodes.push({ id: nid, label: ev.name, kind: "event", year: ev.year });
    edges.push({ from: center, to: nid, label: "史事" });
    void d;
  }
  for (const poet of footprints) {
    const stopsHere = poet.stops.filter(
      (s) =>
        s.lng != null && s.lat != null && place?.lng != null && place?.lat != null &&
        Math.abs(s.lng - place.lng) < 0.9 && Math.abs(s.lat - place.lat) < 0.9,
    );
    if (stopsHere.length === 0) continue;
    const nid = `poet:${poet.id}`;
    nodes.push({ id: nid, label: poet.name, kind: "poet" });
    for (const s of stopsHere.slice(0, 2)) {
      edges.push({ from: center, to: nid, label: `${s.year}年${s.event.slice(0, 6)}` });
    }
  }
  drawRadial(body, center, nodes, edges);
}

function renderPoetGraph(body: HTMLElement, poet: PoetFootprint, year: number): void {
  const nodes: GNode[] = [{ id: `poet:${poet.id}`, label: poet.name, kind: "poet" }];
  const edges: GEdge[] = [];
  const center = `poet:${poet.id}`;
  for (const s of poet.stops) {
    const nid = `place:${s.name}`;
    if (!nodes.some((n) => n.id === nid)) nodes.push({ id: nid, label: s.name, kind: "place", year: s.year });
    edges.push({ from: center, to: nid, label: `${formatYear(s.year)}${s.event.slice(0, 6)}` });
  }
  for (const w of poet.works) {
    if (w.year && w.year > year) continue;
    const nid = `work:${w.id}`;
    nodes.push({ id: nid, label: w.title, kind: "work", year: w.year ?? undefined });
    edges.push({ from: center, to: nid, label: w.year ? formatYear(w.year) : "" });
  }
  drawRadial(body, center, nodes, edges);
}

/* ---- 径向 SVG 布局 ---- */

const R = 108;
const CX = 150;
const CY = 128;

const KIND_COLOR: Record<GNode["kind"], string> = {
  place: "#9e3d34",
  poet: "#a3814f",
  event: "#3d5568",
  work: "#6d8a6a",
  dynasty: "#8a8272",
};

function drawRadial(body: HTMLElement, centerId: string, nodes: GNode[], edges: GEdge[]): void {
  const ring = nodes.filter((n) => n.id !== centerId);
  const svgNS = "http://www.w3.org/2000/svg";
  const svg = document.createElementNS(svgNS, "svg");
  svg.setAttribute("viewBox", `0 0 300 256`);
  svg.classList.add("graph-svg");

  // 环上节点均分角度
  const pos = new Map<string, { x: number; y: number }>();
  pos.set(centerId, { x: CX, y: CY });
  ring.forEach((n, i) => {
    const a = (2 * Math.PI * i) / ring.length - Math.PI / 2;
    pos.set(n.id, { x: CX + R * Math.cos(a), y: CY + R * Math.sin(a) * 0.86 });
  });

  // 边
  for (const e of edges) {
    const a = pos.get(e.from);
    const b = pos.get(e.to);
    if (!a || !b) continue;
    const line = document.createElementNS(svgNS, "line");
    line.setAttribute("x1", String(a.x));
    line.setAttribute("y1", String(a.y));
    line.setAttribute("x2", String(b.x));
    line.setAttribute("y2", String(b.y));
    line.setAttribute("class", "g-edge");
    svg.appendChild(line);
  }
  // 节点
  for (const n of nodes) {
    const isCenter = n.id === centerId;
    const p = pos.get(n.id)!;
    const g = document.createElementNS(svgNS, "g");
    g.setAttribute("class", "g-node" + (isCenter ? " g-center" : ""));
    const c = document.createElementNS(svgNS, "circle");
    c.setAttribute("cx", String(p.x));
    c.setAttribute("cy", String(p.y));
    c.setAttribute("r", isCenter ? "20" : "14");
    c.setAttribute("stroke", KIND_COLOR[n.kind]);
    c.setAttribute("fill", isCenter ? KIND_COLOR[n.kind] : "var(--paper)");
    g.appendChild(c);
    const t = document.createElementNS(svgNS, "text");
    t.setAttribute("x", String(p.x));
    t.setAttribute("y", String(p.y + 4));
    t.textContent = n.label.slice(0, isCenter ? 5 : 4);
    g.appendChild(t);
    if (!isCenter) {
      const tip = document.createElementNS(svgNS, "title");
      tip.textContent = (n.year !== undefined ? `${formatYear(n.year)}·` : "") + n.label;
      g.appendChild(tip);
    }
    // 关联节点点击 → 跳转
    if (n.kind === "place") {
      const pid = n.id.slice("place:".length);
      const target = getState().places.find((x) => x.id === pid);
      g.classList.add("g-clickable");
      g.addEventListener("click", () => {
        if (target) {
          selectPlace(target.id);
          document.dispatchEvent(new CustomEvent("ht:fly-place", { detail: target }));
        }
      });
    } else if (n.kind === "poet") {
      g.classList.add("g-clickable");
      g.addEventListener("click", () => setState({ activePoetId: n.id.slice("poet:".length), panelTab: "poets" }));
    } else if (n.kind === "event") {
      g.classList.add("g-clickable");
      g.addEventListener("click", () => {
        setState({ activeEventId: n.id.slice("event:".length), panelTab: "events" });
        const ev = getState().events.find((x) => x.id === n.id.slice("event:".length));
        setState({ year: ev?.year ?? getState().year });
      });
    }
    svg.appendChild(g);
  }
  body.appendChild(svg);

  // 图例
  const legend = document.createElement("div");
  legend.className = "g-legend";
  legend.innerHTML = Object.entries(KIND_COLOR)
    .map(([k, col]) => `<span><i style="border-color:${col}"></i>${KIND_LABEL[k as keyof typeof KIND_LABEL]}</span>`)
    .join("");
  body.appendChild(legend);
}

function selectPlace(id: string): void {
  setState({ selectedPlaceId: id, panelTab: "lineage" });
}
