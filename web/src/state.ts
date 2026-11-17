/** 极简 pub/sub 全局状态。 */

import type { Dynasty, LineageEntry } from "./lib/lineage";

export interface AppState {
  year: number;
  dynasties: Dynasty[];
  places: PlaceMeta[];
  /** placeId → 沿革条目(按时间排序) */
  lineages: Map<string, LineageEntry[]>;
  selectedPlaceId: string | null;
}

export interface PlaceMeta {
  id: string;
  name: string;
  lng: number;
  lat: number;
  province: string;
}

type Listener = (s: AppState) => void;

const state: AppState = {
  year: 618,
  dynasties: [],
  places: [],
  lineages: new Map(),
  selectedPlaceId: null,
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
  setState({ selectedPlaceId: id });
}
