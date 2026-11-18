/** 现代省界参考层(今界):DataV GeoAtlas geojson + 省名淡标注。 */

import maplibregl from "maplibre-gl";
import type { FeatureCollection } from "geojson";

const PROV_FILL = "rgba(109, 138, 106, 0.04)"; // 极淡石绿
const PROV_LINE = "rgba(74, 68, 60, 0.28)"; // 细墨虚线(今界)

let installed = false;

export function installProvinces(
  map: maplibregl.Map,
  fc: FeatureCollection,
  labels: { name: string; lng: number; lat: number }[],
): void {
  if (installed) return;
  installed = true;
  map.addSource("provinces", { type: "geojson", data: fc });
  // 插到 polities-fill 之下(今界作底,历史疆界在上)
  const before = map.getLayer("polities-fill") ? "polities-fill" : undefined;
  map.addLayer(
    {
      id: "provinces-fill",
      type: "fill",
      source: "provinces",
      paint: { "fill-color": PROV_FILL },
    },
    before,
  );
  map.addLayer(
    {
      id: "provinces-line",
      type: "line",
      source: "provinces",
      paint: { "line-color": PROV_LINE, "line-width": 0.8, "line-dasharray": [3, 2] },
    },
    before,
  );
  // 省名淡标注(HTML marker,随地图移动)
  for (const l of labels) {
    const el = document.createElement("div");
    el.className = "prov-label";
    el.textContent = l.name.replace(/(省|市|自治区|特别行政区|壮族|回族|维吾尔)/g, "");
    new maplibregl.Marker({ element: el, anchor: "center" })
      .setLngLat([l.lng, l.lat])
      .addTo(map);
  }
}
