
"""作品系年 claim 化:works.json 的通行系年/创作地转写为 written_when / written_at claims。

按协议:作品系年默认 G2 以下——attestation 单源(src_own_manual,通行编年整理),
precision 按把握度给 year 或 approx 区间。运行: uv run python scripts/gen_works_claims.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
OUT = REPO / "data" / "claims"

OWN = "src_own_manual"

# (work_id, when=(y1,y2,precision) 或 None, at=(name,lng,lat) 或 None, note)
ROWS = [
    ("wrk_libai_baidicheng", (759, 759, "year"), ("白帝城(夔州)", 109.574, 31.042), "乾元二年流放遇赦东还,通行编年"),
    ("wrk_dufu_chunwang", (757, 757, "year"), ("长安", 108.9398, 34.3416), "至德二载身陷长安时作"),
    ("wrk_dufu_denggao", (767, 767, "year"), ("夔州", 109.574, 31.042), "大历二年夔州重九登高"),
    ("wrk_dufu_caotang", (761, 761, "year"), ("成都", 104.0668, 30.5728), "上元二年成都草堂作"),
    ("wrk_dufu_wenguan", (763, 763, "year"), ("梓州", 105.19, 31.09), "广德元年春梓州作"),
    ("wrk_baijuyi_caoyuan", (787, 788, "approx"), ("长安", 108.9398, 34.3416), "贞元初应考习作,一说十六岁作"),
    ("wrk_baijuyi_pipa", (816, 816, "year"), ("江州(九江)", 116.0005, 29.7052), "元和十一年江州司马任上"),
    ("wrk_baijuyi_qiantang", (824, 824, "year"), ("杭州", 120.1551, 30.2741), "长庆杭州刺史任内作"),
    ("wrk_sushi_shuidiao", (1076, 1076, "year"), ("密州", 119.75, 36.77), "熙宁九年密州中秋,小序自证"),
    ("wrk_sushi_nian-nu-jiao", (1082, 1082, "year"), ("黄州", 114.87, 30.45), "元丰五年黄州作,通行说"),
    ("wrk_sushi_yinhu", (1073, 1073, "year"), ("杭州", 120.1551, 30.2741), "熙宁六年杭州通判任上作"),
    ("wrk_luyou_shier", (1210, 1210, "year"), ("山阴", 120.58, 30.0), "临终绝笔,编年无争议"),
    ("wrk_luyou_shanxi", (1167, 1167, "year"), ("山阴", 120.58, 30.0), "乾道三年罢官居山阴作"),
    ("wrk_luyou_shufen", (1186, 1186, "year"), ("山阴", 120.58, 30.0), "淳熙十三年山阴作"),
    # M6 新增诗人作品
    ("wrk_liuzongyuan_jiangxue", (805, 815, "approx"), ("永州", 111.6131, 26.4345), "永州十年间作,通行说"),
    ("wrk_liuzongyuan_liuzhou", (815, 819, "approx"), ("柳州", 109.4155, 24.3255), "柳州刺史任上作"),
    ("wrk_hanyu_languan", (819, 819, "year"), ("蓝关(蓝田)", 109.32, 34.15), "元和十四年贬潮州途中,诗题自证"),
    ("wrk_hanyu_zaocun", (823, 823, "year"), ("长安", 108.9398, 34.3416), "长庆三年长安作,通行说"),
    ("wrk_xinqiji_pozhenzi", (1188, 1189, "approx"), ("上饶·带湖", 117.94, 28.45), "闲居带湖期作(约)"),
    ("wrk_xinqiji_yongyule", (1205, 1205, "year"), ("京口(镇江)", 119.4252, 32.1884), "开禧元年镇江知府任上,通行说"),
]


def main() -> int:
    works = json.loads((REPO / "data" / "works.json").read_text(encoding="utf-8"))["works"]
    by_id = {w["id"]: w for w in works}
    n = 0
    for wid, when, at, note in ROWS:
        w = by_id[wid]
        slug = wid.split("_", 1)[1].replace("-", "_")
        base = {
            "subject": {"type": "work", "id": wid},
            "attestations": [
                {"source": OWN, "locus": f"通行编年整理:{note}", "quote": None, "certainty": 0.6}
            ],
            "verdicts": [],
            "confidence": "G2",
            "status": "machine-checked",
            "disputes": [],
            "provenance": {"created_by": "seed-generator", "created_at": "2026-11-18", "pipeline_runs": []},
        }
        if when:
            y1, y2, prec = when
            c = {
                **base,
                "id": f"clm_when_{slug}",
                "predicate": "written_when",
                "object": {"note": f"通行系年:{w['yearNote']}"},
                "period": {"earliest": y1, "latest": y2, "precision": prec, "calendar": "proleptic-julian"},
            }
            (OUT / f"{c['id']}.json").write_text(
                json.dumps(c, ensure_ascii=False, indent=1, sort_keys=True) + "\n", encoding="utf-8"
            )
            n += 1
        if at:
            name, lng, lat = at
            c = {
                **base,
                "id": f"clm_at_{slug}",
                "predicate": "written_at",
                "object": {"name": name, "lng": lng, "lat": lat},
                "period": {"earliest": 0, "latest": 2100, "precision": "year", "calendar": "proleptic-julian"},
            }
            # written_at 不应有大区间——用作品系年区间更严谨
            if when:
                y1, y2, prec = when
                c["period"] = {"earliest": y1, "latest": y2, "precision": prec, "calendar": "proleptic-julian"}
            (OUT / f"{c['id']}.json").write_text(
                json.dumps(c, ensure_ascii=False, indent=1, sort_keys=True) + "\n", encoding="utf-8"
            )
            n += 1
    print(f"generated {n} work-dating claims → {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
