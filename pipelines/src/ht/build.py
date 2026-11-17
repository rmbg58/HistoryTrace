"""构建:claims → web/public/data 静态产物(web 唯一可读数据)。"""

from __future__ import annotations

import json
from datetime import date
from typing import Any

from . import WEB_PUBLIC_DATA
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


def build(out_dir: Any = None) -> dict[str, Any]:
    """生成 places/lineages/index 三类产物。返回统计信息。"""
    registry = load_registry()
    places = load_places()["places"]
    dynasties = load_dynasties()
    claims = [c for c in load_claims() if c["predicate"] == "name_in_period"]

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

    index = {
        "generatedAt": generated_at,
        "dynasties": dynasties,
        "places": [
            {"id": p["id"], "name": p["name"], "lng": p["lng"], "lat": p["lat"], "province": p.get("province", "")}
            for p in places
        ],
        "counts": {"claims": len(claims), "places": len(places), "byConfidence": counts},
    }
    (out / "index.json").write_text(
        json.dumps(index, ensure_ascii=False, indent=1, sort_keys=True) + "\n", encoding="utf-8"
    )
    return index["counts"]
