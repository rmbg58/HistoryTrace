/** 朝代时间轴:chips + 年份滑块。 */

import { dynastyForYear } from "../lib/lineage";
import { getState, setState } from "../state";

export function renderTimeline(root: HTMLElement): void {
  const { dynasties, year } = getState();
  const min = Math.min(...dynasties.map((d) => d.earliest));
  const max = Math.max(...dynasties.map((d) => d.latest));

  root.innerHTML = "";
  const chips = document.createElement("div");
  chips.className = "dynasty-chips";
  for (const d of dynasties) {
    const b = document.createElement("button");
    b.className = "chip";
    b.dataset.key = d.key;
    b.textContent = d.label;
    b.title = d.note ? `${d.label}(${d.earliest}–${d.latest},${d.note})` : `${d.label}(${d.earliest}–${d.latest})`;
    b.addEventListener("click", () => setState({ year: d.earliest }));
    chips.appendChild(b);
  }

  const slider = document.createElement("input");
  slider.type = "range";
  slider.min = String(min);
  slider.max = String(max);
  slider.step = "1";
  slider.value = String(year);
  slider.setAttribute("aria-label", "年份");
  slider.addEventListener("input", () => setState({ year: Number(slider.value) }));

  const readout = document.createElement("div");
  readout.className = "readout";
  const yearEl = document.createElement("span");
  yearEl.className = "year";
  const dynEl = document.createElement("span");
  dynEl.className = "dyn";
  readout.append(yearEl, dynEl);

  root.append(chips, slider, readout);

  const active = dynastyForYear(dynasties, year);
  for (const chip of chips.querySelectorAll<HTMLButtonElement>(".chip")) {
    chip.classList.toggle("is-active", chip.dataset.key === active?.key);
  }
  slider.value = String(Math.min(Math.max(year, min), max));
  yearEl.textContent = formatYear(year);
  dynEl.textContent = active ? `${active.label}${active.note ? `(${active.note})` : ""}` : "—";
}

export function formatYear(y: number): string {
  return y < 0 ? `前${Math.abs(y)}` : `${y}`;
}
