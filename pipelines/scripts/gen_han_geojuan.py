"""汉期第二批卷页直抓:候选城在《漢書·卷028》地理志全文定位,命中才录入。

含已登记城市(补 han 期 claim)与新城市(先加 places 再录 claim)。
"""

from __future__ import annotations

import json
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from ht.backfill import clean_wikitext, extract_context

REPO = Path(__file__).resolve().parents[1].parent
CLAIMS = REPO / "data" / "claims"
PLACES = REPO / "data" / "places.json"

API = "https://zh.wikisource.org/w/api.php"
UA = "HistoryTrace/0.1 (open-source data pipeline)"
D = "src_daizhige"
HG = "src_hanshu_ws"

# (cid, 城 name, lng, lat, province, 漢書条目 term, role)
CANDIDATES = [
    ("qinyang", "沁阳", 112.9453, 35.0893, "河南", "野王", "河內郡治"),
    ("yanan", "延安", 109.4908, 36.5855, "陕西", "膚施", "上郡治"),
    ("daixian", "代县", 112.9591, 39.0667, "山西", "廣武", "雁門郡轄"),
    ("taian", "泰安", 117.1201, 36.19, "山东", "奉高", "泰山郡治(今泰安東)"),
    ("lintao", "临洮", 103.862, 35.378, "甘肃", "狄道", "隴西郡治"),
    ("juxian", "莒县", 118.84, 35.58, "山东", "莒", "城陽國都"),
    ("pingyuan", "平原", 116.44, 37.16, "山东", "平原", "平原郡轄"),
    ("cangzhou", "沧州", 116.58, 38.3, "河北", "浮陽", "渤海郡轄"),
    ("qinghe", "清河", 115.66, 37.04, "河北", "清陽", "清河郡治"),
    ("gaomi", "高密", 119.76, 36.38, "山东", "高密", "高密國都"),
]


def page_text(title: str) -> str:
    params = {
        "action": "query",
        "prop": "revisions",
        "rvprop": "content",
        "rvslots": "main",
        "format": "json",
        "titles": title,
    }
    for attempt in range(3):
        req = urllib.request.Request(f"{API}?{urllib.parse.urlencode(params)}", headers={"User-Agent": UA})
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                data = json.load(r)
            time.sleep(2.0)
            for p in data["query"]["pages"].values():
                if "revisions" in p:
                    return p["revisions"][0]["slots"]["main"]["*"]
            return ""
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < 2:
                time.sleep(20)
                continue
            raise
    return ""


def main() -> int:
    dry = "--dry-run" in sys.argv
    text = clean_wikitext(page_text("漢書/卷028"))
    print(f"漢書/卷028 全文 {len(text)} 字")

    places = json.loads(PLACES.read_text(encoding="utf-8"))
    have = {p["id"] for p in places["places"]}
    added = 0
    missed: list[str] = []

    for cid, name, lng, lat, prov, term, role in CANDIDATES:
        key = f"plc_{cid}"
        claim_path = CLAIMS / f"clm_{cid}_han.json"
        if claim_path.exists():
            continue  # 已有 han claim,跳过
        q = extract_context(text, term)
        if not q:
            missed.append(name)
            continue
        if dry:
            print(f"[hit] {name}「{term}」: {q[:50]}")
            continue
        if key not in have:
            places["places"].append({"id": key, "name": name, "lng": lng, "lat": lat, "province": prov})
            have.add(key)
        claim = {
            "id": f"clm_{cid}_han",
            "subject": {"type": "place", "id": key},
            "predicate": "name_in_period",
            "object": {"name": term, "role": role},
            "period": {"earliest": -202, "latest": 8, "precision": "year", "calendar": "proleptic-julian"},
            "attestations": [
                {
                    "source": HG,
                    "locus": f"漢書/卷028/地理志上·{term}",
                    "quote": f"『{q}』——《漢書》(漢書/卷028)",
                    "certainty": 0.8,
                },
                {"source": D, "locus": f"殆知閣鏡像/漢書/{term}", "quote": None, "certainty": 0.7},
            ],
            "verdicts": [],
            "confidence": "G3",
            "status": "cross-checked",
            "disputes": [],
            "provenance": {"created_by": "han-geojuan-locator", "created_at": "2026-11-18", "pipeline_runs": []},
        }
        claim_path.write_text(
            json.dumps(claim, ensure_ascii=False, indent=1, sort_keys=True) + "\n", encoding="utf-8"
        )
        added += 1
        print(f"[ok] {name}「{term}」")

    if not dry:
        PLACES.write_text(json.dumps(places, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"\n录城 {added} | 未命中 {len(missed)}: {'、'.join(missed)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
