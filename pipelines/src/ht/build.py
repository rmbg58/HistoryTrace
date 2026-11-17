"""构建:claims → web/public/data 静态产物(web 唯一可读数据)。"""

from __future__ import annotations

import json
from datetime import date
from typing import Any

from . import DATA_DIR, WEB_PUBLIC_DATA
from .loader import LoadError, load_claims, load_dynasties, load_places, load_registry
from .verify import G_ORDER, _computed_confidence


def _effective_confidence(claim: dict[str, Any], registry: dict[str, dict[str, Any]]) -> str:
    """R3:机器只降级不升级。有人工裁决且证据完备时允许 G4。"""
    claimed = claim["confidence"]
    computed = _computed_confidence(claim, registry)
    level = min(claimed, computed, key=lambda g: G_ORDER[g])
    if claimed == "G4":
        has_verdict = any(v["decision"] == "accept" for v in claim.get("verdicts", []))
        has_quotes = all(att.get("quote") for att in claim["attestations"])
        if has_verdict and has_quotes:
            level = "G4"
    return level


def build_lineage(claims: list[dict[str, Any]], registry: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """把一个 place 的 name_in_period claims 聚合为沿革条目列表。"""
    entries = []
    for claim in claims:
        atts = []
        for att in claim["attestations"]:
            src = registry[att["source"]]
            atts.append(
                {
                    "source": src["title"],
                    "sourceId": att["source"],
                    "edition": src.get("edition", ""),
                    "locus": att["locus"],
                    "quote": att.get("quote"),
                    "certainty": att.get("certainty"),
                    "tier": src["tier"],
                }
            )
        obj = claim["object"]
        entries.append(
            {
                "claimId": claim["id"],
                "earliest": claim["period"]["earliest"],
                "latest": claim["period"]["latest"],
                "precision": claim["period"]["precision"],
                "name": obj.get("name", ""),
                "role": obj.get("role", ""),
                "note": obj.get("note", ""),
                "confidence": _effective_confidence(claim, registry),
                "status": claim["status"],
                "attestations": sorted(atts, key=lambda a: a["sourceId"]),
                "verdicts": claim.get("verdicts", []),
            }
        )
    entries.sort(key=lambda e: (e["earliest"], e["latest"]))
    return {"entries": entries}


def build_events(claims: list[dict[str, Any]], registry: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    """事件索引:occurred_at claims + events.json 编辑信息。"""
    meta = {
        e["id"]: e for e in json.loads((DATA_DIR / "events.json").read_text(encoding="utf-8"))["events"]
    }
    events = []
    for claim in claims:
        eid = claim["subject"]["id"]
        info = meta.get(eid)
        if info is None:
            raise LoadError(f"occurred_at claim 引用未登记的事件: {eid}")
        atts = [
            {
                "source": registry[a["source"]]["title"],
                "locus": a["locus"],
                "quote": a.get("quote"),
            }
            for a in claim["attestations"]
        ]
        obj = claim["object"]
        events.append(
            {
                "id": eid,
                "name": info["name"],
                "type": info.get("type", "event"),
                "summary": info.get("summary", ""),
                "year": claim["period"]["earliest"],
                "place": {"name": obj.get("name", ""), "lng": obj.get("lng"), "lat": obj.get("lat")},
                "confidence": _effective_confidence(claim, registry),
                "attestations": atts,
            }
        )
    events.sort(key=lambda e: e["year"])
    return events


def build_footprints(claims: list[dict[str, Any]], registry: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    """诗人行迹:person_at claims 聚合 + 作品(OT-007:作品→站点关联在构建期预计算)。"""
    poets = json.loads((DATA_DIR / "poets.json").read_text(encoding="utf-8"))["poets"]
    works = json.loads((DATA_DIR / "works.json").read_text(encoding="utf-8"))["works"]
    by_poet: dict[str, list[dict[str, Any]]] = {}
    for claim in claims:
        by_poet.setdefault(claim["subject"]["id"], []).append(claim)
    out = []
    for poet in poets:
        pid = poet["id"]
        stops = []
        for claim in sorted(by_poet.get(pid, []), key=lambda c: c["period"]["earliest"]):
            obj = claim["object"]
            stop = {
                "year": claim["period"]["earliest"],
                "toYear": claim["period"]["latest"],
                "name": obj.get("name", ""),
                "lng": obj.get("lng"),
                "lat": obj.get("lat"),
                "event": obj.get("note", ""),
                "confidence": _effective_confidence(claim, registry),
            }
            stops.append(stop)
        poet_works = [dict(w) for w in works if w["poetId"] == pid]
        # 构建期关联:作品挂到地理上最近的站点(written_at 同址或距离 <0.7°)
        for w in poet_works:
            if w.get("lng") is None or w.get("lat") is None:
                continue
            best, best_d = None, 0.7
            for i, s in enumerate(stops):
                if s["lng"] is None or s["lat"] is None:
                    continue
                d = max(abs(w["lng"] - s["lng"]), abs(w["lat"] - s["lat"]))
                if d < best_d:
                    best, best_d = i, d
            if best is not None:
                stops[best].setdefault("workIds", []).append(w["id"])
        out.append({**poet, "stops": stops, "works": poet_works})
    return out


def build(out_dir: Any = None) -> dict[str, Any]:
    """生成 places/lineages/events/footprints/index 产物。返回统计信息。"""
    registry = load_registry()
    places = load_places()["places"]
    dynasties = load_dynasties()
    all_claims = load_claims()
    claims = [c for c in all_claims if c["predicate"] == "name_in_period"]
    event_claims = [c for c in all_claims if c["predicate"] == "occurred_at"]
    person_claims = [c for c in all_claims if c["predicate"] == "person_at"]

    out = WEB_PUBLIC_DATA if out_dir is None else out_dir
    lineages_dir = out / "lineages"
    lineages_dir.mkdir(parents=True, exist_ok=True)

    by_place: dict[str, list[dict[str, Any]]] = {}
    for claim in claims:
        by_place.setdefault(claim["subject"]["id"], []).append(claim)

    place_ids = {p["id"] for p in places}
    for pid in by_place:
        if pid not in place_ids:
            raise LoadError(f"claim 引用未登记的 place: {pid}")

    generated_at = date.today().isoformat()
    counts: dict[str, int] = {"G1": 0, "G2": 0, "G3": 0, "G4": 0}

    for place in places:
        pid = place["id"]
        lineage = build_lineage(by_place.get(pid, []), registry)
        for e in lineage["entries"]:
            counts[e["confidence"]] += 1
        payload = {"place": place, "lineage": lineage["entries"]}
        (lineages_dir / f"{pid}.json").write_text(
            json.dumps(payload, ensure_ascii=False, indent=1, sort_keys=True) + "\n",
            encoding="utf-8",
        )

    events = build_events(event_claims, registry)
    footprints = build_footprints(person_claims, registry)
    (out / "events.json").write_text(
        json.dumps({"events": events}, ensure_ascii=False, indent=1, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (out / "footprints.json").write_text(
        json.dumps({"poets": footprints}, ensure_ascii=False, indent=1, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    index = {
        "generatedAt": generated_at,
        "dynasties": dynasties,
        "places": [
            {"id": p["id"], "name": p["name"], "lng": p["lng"], "lat": p["lat"], "province": p.get("province", "")}
            for p in places
        ],
        "counts": {
            "claims": len(all_claims),
            "places": len(places),
            "events": len(events),
            "poets": len(footprints),
            "byConfidence": counts,
        },
    }
    (out / "index.json").write_text(
        json.dumps(index, ensure_ascii=False, indent=1, sort_keys=True) + "\n", encoding="utf-8"
    )
    return index["counts"]
