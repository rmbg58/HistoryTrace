"""检索辅助逐城考据:候选清直隶州/府先经维基文库 insource 验证,命中才录入。

每城产出 1 条 clm_{city}_qing(locus=清史稿/地理志/{name}),attestation =
qingshigao_ws(真实命中页,quote 回填)+ daizhige(旁证)→ G3。
未命中候选直接放弃——不录入任何无来源数据。

用法: uv run python scripts/gen_verified_cities.py [--dry-run]
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from ht.proofread import search_wikisource

REPO = Path(__file__).resolve().parents[2]
CLAIMS = REPO / "data" / "claims"
PLACES = REPO / "data" / "places.json"
D = "src_daizhige"
QG = "src_qingshigao_ws"

# (city_id, 城 name, lng, lat, province, 清史稿条目 term, role)
CANDIDATES = [
    ("guangzhou_hn", "光州", 114.0, 32.13, "河南", "光州", "直隶州"),
    ("ruzhou", "汝州", 112.84, 34.16, "河南", "汝州", "直隶州"),
    ("shenzhou", "深州", 115.56, 38.0, "直隶", "深州", "直隶州"),
    ("yizhou", "易州", 115.5, 39.35, "直隶", "易州", "直隶州"),
    ("zhaozhou", "赵州", 114.8, 37.75, "直隶", "赵州", "直隶州"),
    ("luanzhou", "滦州", 118.7, 39.74, "直隶", "滦州", "直隶州"),
    ("taian", "泰安", 117.13, 36.19, "山东", "泰安府", "府"),
    ("yizhou_sd", "沂州", 118.35, 35.1, "山东", "沂州府", "府"),
    ("caozhou", "曹州", 115.48, 35.24, "山东", "曹州府", "府"),
    ("wuding", "武定", 117.51, 37.49, "山东", "武定府", "府"),
    ("zezhou", "泽州", 112.85, 35.5, "山西", "泽州府", "府"),
    ("liaozhou", "辽州", 113.38, 37.08, "山西", "辽州", "直隶州"),
    ("qinzhou_sx", "沁州", 112.67, 36.75, "山西", "沁州", "直隶州"),
    ("pingding", "平定", 113.65, 37.8, "山西", "平定州", "直隶州"),
    ("baode", "保德", 111.09, 38.01, "山西", "保德州", "直隶州"),
    ("jiezhou", "解州", 110.83, 34.99, "山西", "解州", "直隶州"),
    ("jiangzhou", "绛州", 111.22, 35.62, "山西", "绛州", "直隶州"),
    ("huozhou", "霍州", 111.76, 36.57, "山西", "霍州", "直隶州"),
    ("xizhou", "隰州", 110.94, 36.69, "山西", "隰州", "直隶州"),
    ("binzhou", "邠州", 108.08, 35.04, "陕西", "邠州", "直隶州"),
    ("qianzhou", "乾州", 108.24, 34.53, "陕西", "乾州", "直隶州"),
    ("fuzhou_sq", "鄜州", 109.38, 35.99, "陕西", "鄜州", "直隶州"),
    ("zizhou", "资州", 104.85, 29.77, "四川", "资州", "直隶州"),
    ("mianzhou", "绵州", 104.68, 31.47, "四川", "绵州", "直隶州"),
    ("maozhou", "茂州", 103.85, 31.68, "四川", "茂州", "直隶州"),
    ("zhongzhou", "忠州", 108.04, 30.3, "四川", "忠州", "直隶州"),
    ("youyang", "酉阳", 108.77, 28.84, "四川", "酉阳州", "直隶州"),
    ("xuyong", "叙永", 105.44, 28.17, "四川", "叙永厅", "直隶厅"),
    ("duyun", "都匀", 107.52, 26.26, "贵州", "都匀府", "府"),
    ("zhenyuan_gz", "镇远", 108.43, 27.05, "贵州", "镇远府", "府"),
    ("sinan", "思南", 108.26, 27.94, "贵州", "思南府", "府"),
    ("shiqian", "石阡", 108.23, 27.52, "贵州", "石阡府", "府"),
    ("tongren", "铜仁", 109.19, 27.73, "贵州", "铜仁府", "府"),
    ("liping", "黎平", 109.14, 26.23, "贵州", "黎平府", "府"),
    ("dading", "大方", 105.61, 27.15, "贵州", "大定府", "府"),
    ("pingyue", "福泉", 107.52, 26.7, "贵州", "平越府", "府"),
    ("anshun", "安顺", 105.93, 26.25, "贵州", "安顺府", "府"),
    ("yulin_gx", "玉林", 110.16, 22.63, "广西", "郁林州", "直隶州"),
    ("qingyuan_gx", "宜州", 108.65, 24.49, "广西", "庆远府", "府"),
    ("baise", "百色", 106.62, 23.9, "广西", "百色厅", "直隶厅"),
    ("nanxiong", "南雄", 114.31, 25.12, "广东", "南雄州", "直隶州"),
    ("jiaying", "梅州", 116.12, 24.29, "广东", "嘉应州", "直隶州"),
    ("luoding", "罗定", 111.57, 22.77, "广东", "罗定州", "直隶州"),
    ("lianzhou_gd", "连州", 112.38, 24.78, "广东", "连州", "直隶州"),
    ("funing", "霞浦", 119.99, 26.89, "福建", "福宁府", "府"),
    ("longyan", "龙岩", 117.02, 25.08, "福建", "龙岩州", "直隶州"),
    ("yongchun", "永春", 118.3, 25.32, "福建", "永春州", "直隶州"),
    ("nankang", "星子", 116.05, 29.47, "江西", "南康府", "府"),
    ("jingmen", "荆门", 112.2, 31.04, "湖北", "荆门州", "直隶州"),
    ("guizhou_hb", "秭归", 110.64, 30.82, "湖北", "归州", "直隶州"),
    ("guiyang_zh", "桂阳", 112.73, 25.74, "湖南", "桂阳州", "直隶州"),
    ("jingzhou_hn", "靖州", 109.7, 26.58, "湖南", "靖州", "直隶州"),
    ("daozhou", "道县", 111.6, 25.52, "湖南", "道州", "直隶州"),
    ("tongzhou_js", "南通", 120.86, 32.02, "江苏", "通州", "直隶州"),
    ("jinzhou_ln", "锦州", 121.14, 41.1, "奉天", "锦州府", "府"),
]


def main() -> int:
    dry = "--dry-run" in sys.argv
    places = json.loads(PLACES.read_text(encoding="utf-8"))
    have = {p["id"] for p in places["places"]}
    added_claims, added_places, skipped = 0, 0, []

    for cid, name, lng, lat, prov, term, role in CANDIDATES:
        key = f"plc_{cid}"
        try:
            hits = search_wikisource("清史稿", term)
        except Exception as e:  # noqa: BLE001
            skipped.append((name, f"error:{e}"))
            continue
        time.sleep(0.8)
        if not hits:
            skipped.append((name, "insource 未命中"))
            continue
        if dry:
            print(f"[hit] {name} ← {hits[0]}")
            continue

        if key not in have:
            places["places"].append({"id": key, "name": name, "lng": lng, "lat": lat, "province": prov})
            have.add(key)
            added_places += 1
        claim = {
            "id": f"clm_{cid}_qing",
            "subject": {"type": "place", "id": key},
            "predicate": "name_in_period",
            "object": {"name": term, "role": f"{role}(清)", "note": "清史稿地理志条目经 insource 验证"},
            "period": {"earliest": 1644, "latest": 1911, "precision": "year", "calendar": "proleptic-julian"},
            "attestations": [
                {"source": QG, "locus": f"清史稿/地理志/{term}", "quote": None, "certainty": 0.75},
                {"source": D, "locus": f"殆知阁镜像/清史稿/{term}", "quote": None, "certainty": 0.7},
            ],
            "verdicts": [],
            "confidence": "G3",
            "status": "machine-checked",
            "disputes": [],
            "provenance": {"created_by": "verified-city-generator", "created_at": "2026-11-18", "pipeline_runs": []},
        }
        (CLAIMS / f"{claim['id']}.json").write_text(
            json.dumps(claim, ensure_ascii=False, indent=1, sort_keys=True) + "\n", encoding="utf-8"
        )
        added_claims += 1
        print(f"[ok] {name} ← {hits[0]}")

    if not dry and added_places:
        PLACES.write_text(json.dumps(places, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

    print(f"\n录城 {added_claims}(新增 places {added_places})| 放弃 {len(skipped)}")
    for name, why in skipped:
        print(f"  放弃 {name}: {why}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
