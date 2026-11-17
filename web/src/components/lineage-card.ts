/** 沿革卡片:某城邑的历代名称 + 置信印章 + 可展开佐证笺注。 */

import { confidenceMeta, dynastyForYear, entryForYear, type LineageEntry } from "../lib/lineage";
import { formatYear } from "./timeline";
import { getState, type PlaceMeta } from "../state";

export function renderPanel(root: HTMLElement): void {
  const { places, lineages, selectedPlaceId, year, dynasties } = getState();
  root.innerHTML = "";

  const head = document.createElement("div");
  head.className = "panel-head";
  const body = document.createElement("div");
  body.className = "panel-body";
  root.append(head, body);

  const place = places.find((p) => p.id === selectedPlaceId);
  if (!place) {
    head.innerHTML = `<div class="place">诸城沿革</div><div class="sub">点选地图或下方城名</div>`;
    renderPlaceIndex(body, places);
    return;
  }

  head.innerHTML = `<div class="place">${place.name}</div><div class="sub">${place.province} · 今 ${place.lng.toFixed(2)}°E ${place.lat.toFixed(2)}°N</div>`;

  const entries = lineages.get(place.id) ?? [];
  const active = entryForYear(entries, year);
  const activeDyn = dynastyForYear(dynasties, year);

  for (const e of entries) {
    body.appendChild(renderEntry(e, activeDyn?.earliest, activeDyn?.latest, active?.claimId === e.claimId));
  }
}

function renderPlaceIndex(body: HTMLElement, places: PlaceMeta[]): void {
  for (const p of places) {
    const b = document.createElement("button");
    b.className = "entry";
    b.innerHTML = `<span class="entry-row"><span class="name">${p.name}</span><span class="span">${p.province}</span></span>`;
    b.addEventListener("click", () => {
      // 通过自定义事件请 main 联动选中(避免循环依赖 map 模块)
      document.dispatchEvent(new CustomEvent("ht:select-place", { detail: p.id }));
    });
    body.appendChild(b);
  }
}

function renderEntry(e: LineageEntry, dEarliest: number | undefined, dLatest: number | undefined, isActive: boolean): HTMLElement {
  const el = document.createElement("article");
  el.className = "entry" + (isActive ? " is-active" : "");
  const meta = confidenceMeta(e.confidence);
  const isCurrent = dEarliest !== undefined && dLatest !== undefined && e.earliest <= dLatest && e.latest >= dEarliest;

  el.innerHTML = `
    <button class="entry-row" aria-expanded="false">
      <span class="dyn-tag">${dynastyLabel(e)}</span>
      <span class="name">${e.name}</span>
      <span class="seal ${meta.cls}" title="${meta.title}">${meta.label}</span>
      <span class="span">${formatYear(e.earliest)}–${formatYear(e.latest)}</span>
    </button>
    ${e.role ? `<div class="role">${e.role}</div>` : ""}
    ${e.note ? `<div class="note">${e.note}</div>` : ""}
    ${isCurrent ? `<div class="note">◉ 当前时间轴所指时期</div>` : ""}
  `;

  const row = el.querySelector<HTMLButtonElement>(".entry-row")!;
  row.addEventListener("click", () => toggleAtts(el, e));
  return el;
}

function dynastyLabel(e: LineageEntry): string {
  const { dynasties } = getState();
  const mid = Math.floor((e.earliest + e.latest) / 2);
  return dynastyForYear(dynasties, mid)?.label ?? `${e.earliest}`;
}

function toggleAtts(el: HTMLElement, e: LineageEntry): void {
  const existing = el.querySelector(".atts");
  if (existing) {
    existing.remove();
    el.querySelector<HTMLElement>(".entry-row")?.setAttribute("aria-expanded", "false");
    return;
  }
  el.querySelector<HTMLElement>(".entry-row")?.setAttribute("aria-expanded", "true");
  const wrap = document.createElement("div");
  wrap.className = "atts";
  for (const a of e.attestations) {
    const d = document.createElement("div");
    d.className = "att";
    const cert = a.certainty !== null ? ` <span class="cert">certainty ${a.certainty.toFixed(2)}</span>` : "";
    const quote = a.quote
      ? `<span class="quote">${a.quote}</span>`
      : `<span class="pending">引文待回填(封顶 G3,R4 回归项)</span>`;
    d.innerHTML = `<span class="src">${a.source}</span>〔${a.tier}级〕 <span class="locus">${a.locus}</span>${cert}${quote}`;
    wrap.appendChild(d);
  }
  if (e.attestations.length === 0) {
    wrap.innerHTML = `<div class="att"><span class="pending">无佐证记录(G1)</span></div>`;
  }
  el.appendChild(wrap);
}
