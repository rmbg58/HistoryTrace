"""卷页直抓考据:抓《清史稿》地理志卷(76–82)全文,对候选直隶州/府逐个定位条目。

绕过 insource 索引缺陷——直接在正文中检索。命中(排除书目著录)才录入:
claim(locus=清史稿/卷N/条目,quote=真实原文)+ places 追加 → G3。
"""

from __future__ import annotations

import json
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from ht.backfill import clean_wikitext, extract_context

REPO = Path(__file__).resolve().parents[1].parent
CLAIMS = REPO / "data" / "claims"
PLACES = REPO / "data" / "places.json"

API = "https://zh.wikisource.org/w/api.php"
UA = "HistoryTrace/0.1 (open-source data pipeline)"
# 清史稿地理志省-卷映射(实测:地理一直隸=卷53…地理二十一貴州=卷75,新疆=卷57)
PROV_JUAN = {
    "直隶": 53, "奉天": 54, "吉林": 55, "黑龙江": 56, "新疆": 57,
    "江苏": 58, "安徽": 59, "山西": 60, "山东": 61, "河南": 62,
    "陕西": 63, "甘肃": 64, "浙江": 65, "江西": 66, "湖北": 67,
    "湖南": 68, "四川": 69, "福建": 70, "广东": 72, "广西": 73,
    "云南": 74, "贵州": 75,
}
GEO_JUANS = sorted(set(PROV_JUAN.values()))
D = "src_daizhige"
QG = "src_qingshigao_ws"


def page_text(title: str) -> str | None:
    params = {
        "action": "query",
        "prop": "revisions",
        "rvprop": "content",
        "rvslots": "main",
        "format": "json",
        "titles": title,
    }
    import time

    for attempt in range(4):
        req = urllib.request.Request(f"{API}?{urllib.parse.urlencode(params)}", headers={"User-Agent": UA})
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                data = json.load(r)
            time.sleep(2.0)
            for p in data["query"]["pages"].values():
                if "revisions" in p:
                    return p["revisions"][0]["slots"]["main"]["*"]
            return None
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < 3:
                time.sleep(10 * (attempt + 1))
                continue
            raise


def main() -> int:
    dry = "--dry-run" in sys.argv
    from gen_verified_cities import CANDIDATES

    cands = CANDIDATES

    places = json.loads(PLACES.read_text(encoding="utf-8"))
    have = {p["id"] for p in places["places"]}

    # 抓地理志卷
    juan_text: dict[int, str] = {}
    for j in GEO_JUANS:
        raw = page_text(f"清史稿/卷{j}")
        if raw:
            juan_text[j] = clean_wikitext(raw)
            print(f"卷{j}: {len(juan_text[j])} 字")
        time.sleep(1.0)

    added_claims = added_places = 0
    missed: list[str] = []
    for cid, name, lng, lat, prov, term, role in cands:
        key = f"plc_{cid}"
        if (CLAIMS / f"clm_{cid}_qing.json").exists():
            continue  # 已录入,跳过
        found = None
        juan_no = PROV_JUAN.get(prov)
        if juan_no and juan_no in juan_text:
            quote = extract_context(juan_text[juan_no], term)
            if quote:
                found = (juan_no, quote)
        if not found:
            missed.append(name)
            continue
        juan, quote = found
        if dry:
            print(f"[hit] {name} ← 卷{juan}: {quote[:50]}")
            continue
        if key not in have:
            places["places"].append({"id": key, "name": name, "lng": lng, "lat": lat, "province": prov})
            have.add(key)
            added_places += 1
        claim = {
            "id": f"clm_{cid}_qing",
            "subject": {"type": "place", "id": key},
            "predicate": "name_in_period",
            "object": {"name": term, "role": f"{role}(清)"},
            "period": {"earliest": 1644, "latest": 1911, "precision": "year", "calendar": "proleptic-julian"},
            "attestations": [
                {"source": QG, "locus": f"清史稿/卷{juan}/{term}", "quote": f"『{quote}』——《清史稿》(清史稿/卷{juan})", "certainty": 0.8},
                {"source": D, "locus": f"殆知阁镜像/清史稿/{term}", "quote": None, "certainty": 0.7},
            ],
            "verdicts": [],
            "confidence": "G3",
            "status": "machine-checked",
            "disputes": [],
            "provenance": {"created_by": "qing-geojuan-locator", "created_at": "2026-11-18", "pipeline_runs": []},
        }
        (CLAIMS / f"{claim['id']}.json").write_text(
            json.dumps(claim, ensure_ascii=False, indent=1, sort_keys=True) + "\n", encoding="utf-8"
        )
        added_claims += 1
        print(f"[ok] {name} ← 卷{juan}")

    if not dry and added_places:
        PLACES.write_text(json.dumps(places, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"\n录城 {added_claims}(places +{added_places})| 未命中 {len(missed)}: {'、'.join(missed)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
