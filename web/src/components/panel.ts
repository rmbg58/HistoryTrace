/** 右侧面板:tab 框架(沿革 | 事件 | 诗人)+ 各 tab 内容。 */

import {
  confidenceMeta,
  dynastyForYear,
  entryForYear,
  type LineageEntry,
} from "../lib/lineage";
import { formatYear } from "./timeline";
import { getState, setState, type EventMeta, type PlaceMeta } from "../state";

export function renderPanel(root: HTMLElement): void {
  const { panelTab } = getState();
  root.innerHTML = "";

  const head = document.createElement("div");
  head.className = "panel-head";
  const tabs = document.createElement("div");
  tabs.className = "panel-tabs";
  for (const [key, label] of [
    ["lineage", "沿革"],
    ["events", "事件"],
    ["poets", "诗人"],
  ] as const) {
    const b = document.createElement("button");
    b.className = "ptab" + (panelTab === key ? " is-active" : "");
    b.textContent = label;
    b.addEventListener("click", () => setState({ panelTab: key }));
    tabs.appendChild(b);
  }
  head.appendChild(tabs);

  const body = document.createElement("div");
  body.className = "panel-body";
  root.append(head, body);

  if (panelTab === "lineage") renderLineageTab(body);
  else if (panelTab === "events") renderEventsTab(body);
  else renderPoetsTab(body);
}

/* ---------------- 沿革 tab ---------------- */

function renderLineageTab(body: HTMLElement): void {
  const { places, lineages, selectedPlaceId, year, dynasties } = getState();
  const place = places.find((p) => p.id === selectedPlaceId);
  if (!place) {
    const tip = document.createElement("div");
    tip.className = "panel-empty";
    tip.textContent = "点选地图城邑,阅其历代沿革";
    body.appendChild(tip);
    renderPlaceIndex(body, places);
    return;
  }
  const title = document.createElement("div");
  title.className = "tab-title";
  title.innerHTML = `${place.name}<span class="sub">${place.province} · 今 ${place.lng.toFixed(2)}°E ${place.lat.toFixed(2)}°N</span>`;
  body.appendChild(title);

  const entries = lineages.get(place.id) ?? [];
  const active = entryForYear(entries, year);
  const activeDyn = dynastyForYear(dynasties, year);
  for (const e of entries) {
    body.appendChild(
      renderEntry(e, activeDyn?.earliest, activeDyn?.latest, active?.claimId === e.claimId),
    );
  }
}

function renderPlaceIndex(body: HTMLElement, places: PlaceMeta[]): void {
  for (const p of places) {
    const b = document.createElement("button");
    b.className = "entry";
    b.innerHTML = `<span class="entry-row"><span class="name">${p.name}</span><span class="span">${p.province}</span></span>`;
    b.addEventListener("click", () => {
      document.dispatchEvent(new CustomEvent("ht:select-place", { detail: p.id }));
    });
    body.appendChild(b);
  }
}

function renderEntry(
  e: LineageEntry,
  dEarliest: number | undefined,
  dLatest: number | undefined,
  isActive: boolean,
): HTMLElement {
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
  el.querySelector<HTMLButtonElement>(".entry-row")!.addEventListener("click", () => toggleAtts(el, e));
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
    return;
  }
  appendAtts(el, e.attestations);
}

function appendAtts(el: HTMLElement, atts: { source: string; locus: string; quote?: string | null }[]): void {
  const wrap = document.createElement("div");
  wrap.className = "atts";
  for (const a of atts) {
    const d = document.createElement("div");
    d.className = "att";
    const quote = a.quote
      ? `<span class="quote">${a.quote}</span>`
      : `<span class="pending">引文待回填(封顶 G3,R4 回归项)</span>`;
    d.innerHTML = `<span class="src">${a.source}</span> <span class="locus">${a.locus}</span>${quote}`;
    wrap.appendChild(d);
  }
  if (atts.length === 0) {
    wrap.innerHTML = `<div class="att"><span class="pending">无佐证记录(G1)</span></div>`;
  }
  el.appendChild(wrap);
}

/* ---------------- 事件 tab ---------------- */

function renderEventsTab(body: HTMLElement): void {
  const { events, activeEventId, dynasties, year } = getState();
  const title = document.createElement("div");
  title.className = "tab-title";
  title.innerHTML = `史事编年<span class="sub">朱印者:当前朝代期内</span>`;
  body.appendChild(title);

  const cur = dynastyForYear(dynasties, year);
  const sorted = [...events].sort((a, b) => a.year - b.year);
  const active = sorted.find((e) => e.id === activeEventId);

  if (active) {
    body.appendChild(renderEventCard(active));
  }
  for (const ev of sorted) {
    if (active && ev.id === active.id) continue;
    const inDyn = cur && ev.year >= cur.earliest && ev.year <= cur.latest;
    const el = document.createElement("button");
    el.className = "entry" + (inDyn ? " is-active" : "");
    const seal = confidenceMeta(ev.confidence as LineageEntry["confidence"]);
    el.innerHTML = `
      <span class="entry-row">
        <span class="dyn-tag">${inDyn ? cur!.label : "·"}</span>
        <span class="name">${ev.name}</span>
        <span class="seal ${seal.cls}" title="${seal.title}">${seal.label}</span>
        <span class="span">${formatYear(ev.year)}</span>
      </span>
      <div class="note">${ev.place.name}</div>
    `;
    el.addEventListener("click", () => {
      setState({ activeEventId: ev.id });
      if (ev.place.lng !== null && ev.place.lat !== null) {
        document.dispatchEvent(new CustomEvent("ht:fly-coords", { detail: { lng: ev.place.lng, lat: ev.place.lat } }));
      }
    });
    body.appendChild(el);
  }
}

function renderEventCard(ev: EventMeta): HTMLElement {
  const el = document.createElement("article");
  el.className = "entry is-active";
  const seal = confidenceMeta(ev.confidence as LineageEntry["confidence"]);
  el.innerHTML = `
    <div class="entry-row">
      <span class="name">${ev.name}</span>
      <span class="seal ${seal.cls}" title="${seal.title}">${seal.label}</span>
      <span class="span">${formatYear(ev.year)}</span>
    </div>
    <div class="role">${ev.place.name}</div>
    <div class="note">${ev.summary}</div>
  `;
  appendAtts(el, ev.attestations);
  return el;
}

/* ---------------- 诗人 tab ---------------- */

function renderPoetsTab(body: HTMLElement): void {
  const { footprints, activePoetId, year } = getState();
  const title = document.createElement("div");
  title.className = "tab-title";
  title.innerHTML = `诗人足迹<span class="sub">淡金为行迹 · 随时间轴渐显</span>`;
  body.appendChild(title);

  const poet = footprints.find((p) => p.id === activePoetId);
  if (!poet) {
    for (const p of footprints) {
      const el = document.createElement("button");
      el.className = "entry";
      el.innerHTML = `
        <span class="entry-row">
          <span class="name">${p.name}</span>
          <span class="span">${p.dynasty} · ${p.years}</span>
        </span>
        <div class="note">${p.desc}</div>
      `;
      el.addEventListener("click", () => setState({ activePoetId: p.id }));
      body.appendChild(el);
    }
    return;
  }

  // 诗人详情
  const head = document.createElement("article");
  head.className = "entry is-active";
  head.innerHTML = `
    <div class="entry-row">
      <span class="name">${poet.name}</span>
      <span class="span">${poet.dynasty} · ${poet.years}</span>
    </div>
    <div class="note">${poet.desc}</div>
  `;
  const playBtn = document.createElement("button");
  playBtn.className = "play-btn";
  playBtn.textContent = "▶ 播放行迹(随时间轴)";
  playBtn.addEventListener("click", () => {
    document.dispatchEvent(new CustomEvent("ht:play-poet", { detail: poet.id }));
  });
  head.appendChild(playBtn);
  body.appendChild(head);

  for (const [i, s] of poet.stops.entries()) {
    const future = s.year > year;
    const el = document.createElement("button");
    el.className = "entry" + (future ? " is-future" : "");
    const spanTxt = s.toYear !== s.year ? `${formatYear(s.year)}–${formatYear(s.toYear)}` : `${formatYear(s.year)}`;
    el.innerHTML = `
      <span class="entry-row">
        <span class="name">${s.name}</span>
        <span class="span">${spanTxt}</span>
      </span>
      <div class="note">${s.event}</div>
    `;
    el.addEventListener("click", () => {
      document.dispatchEvent(new CustomEvent("ht:goto-stop", { detail: { poetId: poet.id, idx: i } }));
    });
    body.appendChild(el);
  }

  // 作品(通行系年,G2 以下按协议)
  const worksTitle = document.createElement("div");
  worksTitle.className = "works-title";
  worksTitle.textContent = "名作(通行系年)";
  body.appendChild(worksTitle);
  for (const w of poet.works) {
    const el = document.createElement("article");
    el.className = "entry";
    const where = w.placeName ?? poet.stops.find((s) => s.name)?.name ?? "";
    const when = w.year ? `${formatYear(w.year)}` : "系年缺";
    el.innerHTML = `
      <div class="entry-row">
        <span class="name">${w.title}</span>
        <span class="span">${when} · ${where}</span>
      </div>
      <div class="poem">${w.lines.replace(/\n/g, "<br>")}</div>
      <div class="note">${w.yearNote}</div>
    `;
    body.appendChild(el);
  }
}
