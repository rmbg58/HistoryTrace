/** 极简 pub/sub 全局状态。 */

import type { Dynasty, LineageEntry } from "./lib/lineage";

export interface AppState {
  year: number;
  dynasties: Dynasty[];
  places: PlaceMeta[];
  /** placeId → 沿革条目(按时间排序) */
  lineages: Map<string, LineageEntry[]>;
  selectedPlaceId: string | null;
  panelTab: PanelTab;
  events: EventMeta[];
  footprints: PoetFootprint[];
  activePoetId: string | null;
  activeEventId: string | null;
}

export type PanelTab = "lineage" | "events" | "poets";

export interface PlaceMeta {
  id: string;
  name: string;
  lng: number;
  lat: number;
  province: string;
}

export interface EventMeta {
  id: string;
  name: string;
  type: string;
  summary: string;
  year: number;
  place: { name: string; lng: number | null; lat: number | null };
  confidence: string;
  attestations: { source: string; locus: string; quote: string | null }[];
}

export interface FootprintStop {
  year: number;
  toYear: number;
  name: string;
  lng: number | null;
  lat: number | null;
  event: string;
  confidence: string;
  /** OT-007:ht build 预计算的作品关联(构建期按坐标最近站点匹配) */
  workIds?: string[];
}

export interface WorkMeta {
  id: string;
  poetId: string;
  title: string;
  lines: string;
  year: number | null;
  yearNote: string;
  placeId?: string | null;
  lng?: number | null;
  lat?: number | null;
  placeName?: string | null;
}

export interface PoetFootprint {
  id: string;
  name: string;
  dynasty: string;
  years: string;
  desc: string;
  stops: FootprintStop[];
  works: WorkMeta[];
}

type Listener = (s: AppState) => void;

const state: AppState = {
  year: 618,
  dynasties: [],
  places: [],
  lineages: new Map(),
  selectedPlaceId: null,
  panelTab: "lineage",
  events: [],
  footprints: [],
  activePoetId: null,
  activeEventId: null,
};

const listeners = new Set<Listener>();

export function getState(): AppState {
  return state;
}

export function subscribe(fn: Listener): () => void {
  listeners.add(fn);
  return () => listeners.delete(fn);
}

export function setState(patch: Partial<AppState>): void {
  Object.assign(state, patch);
  for (const fn of listeners) fn(state);
}

export function selectPlace(id: string | null): void {
  setState({ selectedPlaceId: id, panelTab: "lineage" });
}
