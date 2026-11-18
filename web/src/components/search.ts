/** 全局搜索:城(含历代名)/诗人/事件,输入即列,点击定位(反馈3:降低定位成本)。 */

import { getState } from "../state";

interface Hit {
  kind: "place" | "poet" | "event";
  id: string;
  label: string;
  sub: string;
  year?: string;
}

function buildIndex(): { hit: Hit; hay: string }[] {
  const { places, lineages, footprints, events } = getState();
  const idx: { hit: Hit; hay: string }[] = [];
  const placeById = new Map(places.map((p) => [p.id, p]));

  for (const p of places) {
    idx.push({
      hit: { kind: "place", id: p.id, label: p.name, sub: p.province },
      hay: p.name + p.province,
    });
  }
  for (const [pid, entries] of lineages) {
    const place = placeById.get(pid);
    if (!place) continue;
    for (const e of entries) {
      if (e.name) {
        idx.push({
          hit: { kind: "place", id: pid, label: e.name, sub: `${place.name}·${dynLabel(e.earliest, e.latest)}` },
          hay: e.name,
        });
      }
    }
  }
  for (const poet of footprints) {
    idx.push({
      hit: { kind: "poet", id: poet.id, label: poet.name, sub: `${poet.dynasty}·${poet.years}` },
      hay: poet.name + poet.desc,
    });
  }
  for (const ev of events) {
    idx.push({
      hit: { kind: "event", id: ev.id, label: ev.name, sub: ev.summary.slice(0, 18), year: String(ev.year) },
      hay: ev.name + ev.summary,
    });
  }
  return idx;
}

function dynLabel(e1: number, e2: number): string {
  const mid = Math.floor((e1 + e2) / 2);
  const d = getState().dynasties.find((x) => mid >= x.earliest && mid <= x.latest);
  return d?.label ?? "";
}

const KIND_LABEL: Record<Hit["kind"], string> = { place: "城", poet: "诗人", event: "史事" };

export function renderSearch(root: HTMLElement): void {
  root.innerHTML = "";
  const box = document.createElement("div");
  box.className = "search-box";

  const input = document.createElement("input");
  input.type = "search";
  input.placeholder = "搜索城邑 / 诗人 / 史事…";
  input.setAttribute("aria-label", "全局搜索");
  const drop = document.createElement("div");
  drop.className = "search-drop";
  box.append(input, drop);

  input.addEventListener("input", () => {
    const kw = input.value.trim();
    drop.innerHTML = "";
    if (kw.length < 1) {
      drop.classList.remove("open");
      return;
    }
    const idx = buildIndex();
    const hits = idx.filter((x) => x.hit.label.includes(kw) || x.hay.includes(kw)).slice(0, 12);
    if (hits.length === 0) {
      const empty = document.createElement("div");
      empty.className = "search-empty";
      empty.textContent = "无匹配";
      drop.appendChild(empty);
    }
    for (const h of hits) {
      const row = document.createElement("button");
      row.className = "search-row";
      row.innerHTML = `<span class="sk sk-${h.hit.kind}">${KIND_LABEL[h.hit.kind]}</span><span class="sl">${h.hit.label}</span><span class="ss">${h.hit.sub}</span>`;
      row.addEventListener("click", () => {
        drop.classList.remove("open");
        input.value = "";
        document.dispatchEvent(new CustomEvent("ht:search-goto", { detail: h.hit }));
      });
      drop.appendChild(row);
    }
    drop.classList.add("open");
  });
  input.addEventListener("keydown", (ev) => {
    if (ev.key === "Enter") {
      const first = drop.querySelector<HTMLButtonElement>(".search-row");
      first?.click();
    }
    if (ev.key === "Escape") drop.classList.remove("open");
  });
  document.addEventListener("click", (ev) => {
    if (!box.contains(ev.target as Node)) drop.classList.remove("open");
  });

  root.appendChild(box);
}
