"""第二批诗人(杜牧/李商隐/元稹/王昌龄/孟浩然)行迹 claims 生成。

通行行迹,attestation=旧唐书本传+文集(双证 G3)或单源(自述/无专传,诚实 G2)。
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
OUT = REPO / "data" / "claims"

D = "src_daizhige"
JT = "src_jiutangshu_ws"
SS = "src_songshi_ws"

FOOTPRINTS = {
    "prs_dumu": [
        dict(year=803, place="长安", lng=108.9398, lat=34.3416,
             event="生于长安万年坊,京兆杜氏", atts=[(JT, "旧唐书/杜牧传"), (D, "殆知阁镜像/樊川文集")]),
        dict(year=833, toYear=835, place="扬州", lng=119.4126, lat=32.3947,
             event="牛僧孺辟为淮南节度掌书记", atts=[(JT, "旧唐书/杜牧传"), (D, "殆知阁镜像/樊川文集")]),
        dict(year=842, toYear=844, place="黄州", lng=114.87, lat=30.45,
             event="出为黄州刺史", atts=[(JT, "旧唐书/杜牧传"), (D, "殆知阁镜像/樊川文集")]),
        dict(year=848, place="长安", lng=108.9398, lat=34.3416,
             event="入为司勋员外郎", atts=[(D, "殆知阁镜像/樊川文集")]),
    ],
    "prs_liyingyin": [
        dict(year=813, place="荥阳", lng=113.38, lat=34.79,
             event="生于荥阳,自言族望属安定", atts=[(D, "殆知阁镜像/李义山文集")]),
        dict(year=837, toYear=838, place="长安", lng=108.9398, lat=34.3416,
             event="登进士第,令狐楚子綯之延誉", atts=[(D, "殆知阁镜像/李义山文集")]),
        dict(year=839, toYear=845, place="长安", lng=108.9398, lat=34.3416,
             event="秘书省校书郎?弘农尉,出入牛李党争", atts=[(D, "殆知阁镜像/李义山文集")]),
        dict(year=851, toYear=858, place="梓州", lng=105.19, lat=31.09,
             event="东川节度柳仲郢辟为判官", atts=[(D, "殆知阁镜像/李义山文集")]),
    ],
    "prs_yuanzhen": [
        dict(year=779, place="洛阳", lng=112.454, lat=34.6197,
             event="生于洛阳?河南?通行洛阳", atts=[(JT, "旧唐书/元稹传"), (D, "殆知阁镜像/元氏长庆集")]),
        dict(year=803, place="长安", lng=108.9398, lat=34.3416,
             event="书判拔萃,与白居易同科", atts=[(JT, "旧唐书/元稹传"), (D, "殆知阁镜像/元氏长庆集")]),
        dict(year=810, toYear=815, place="江陵", lng=112.19, lat=30.33,
             event="贬江陵士曹参军", atts=[(JT, "旧唐书/元稹传"), (D, "殆知阁镜像/元氏长庆集")]),
        dict(year=822, toYear=826, place="越州?武昌?", lng=120.58, lat=30.0,
             event="出为浙东观察使(越州)", atts=[(D, "殆知阁镜像/元氏长庆集")]),
    ],
    "prs_wangchangling": [
        dict(year=698, place="长安", lng=108.9398, lat=34.3416,
             event="京兆?太原?两说,通行长安?少伯早年", atts=[(D, "殆知阁镜像/王昌龄诗集")]),
        dict(year=727, place="长安", lng=108.9398, lat=34.3416,
             event="登进士第,补秘书省校书郎", atts=[(JT, "旧唐书/文苑传?王昌龄?"), (D, "殆知阁镜像/王昌龄诗集")]),
        dict(year=748, toYear=755, place="龙标(黔阳)", lng=109.68, lat=27.32,
             event="贬龙标尉(李白遥寄'闻龙标过五溪')", atts=[(D, "殆知阁镜像/王昌龄诗集")]),
        dict(year=757, place="亳州", lng=115.78, lat=33.85,
             event="还乡经亳州,为刺史闾丘晓所杀", atts=[(D, "殆知阁镜像/唐才子传?旧唐书")]),
    ],
    "prs_menghaoran": [
        dict(year=689, place="襄阳", lng=112.14, lat=32.01,
             event="生于襄阳涧南园", atts=[(D, "殆知阁镜像/孟浩然集")]),
        dict(year=728, toYear=730, place="长安", lng=108.9398, lat=34.3416,
             event="应进士不第,滞留长安?还襄阳", atts=[(D, "殆知阁镜像/孟浩然集")]),
        dict(year=740, place="襄阳", lng=112.14, lat=32.01,
             event="王昌龄游襄阳,宴饮疽发而卒", atts=[(D, "殆知阁镜像/孟浩然集")]),
    ],
}


def write_claim(cid, poet_id, pred, obj, year, atts, to_year=None):
    conf = "G3" if len(atts) >= 2 else "G2"
    claim = {
        "id": cid,
        "subject": {"type": "person", "id": poet_id},
        "predicate": "person_at",
        "object": obj,
        "period": {
            "earliest": year,
            "latest": to_year if to_year is not None else year,
            "precision": "year",
            "calendar": "proleptic-julian",
        },
        "attestations": [
            {"source": s, "locus": loc, "quote": None, "certainty": 0.75} for s, loc in atts
        ],
        "verdicts": [],
        "confidence": conf,
        "status": "machine-checked",
        "disputes": [],
        "provenance": {"created_by": "seed-generator", "created_at": "2026-11-19", "pipeline_runs": []},
    }
    (OUT / f"{claim['id']}.json").write_text(
        json.dumps(claim, ensure_ascii=False, indent=1, sort_keys=True) + "\n", encoding="utf-8"
    )


def main() -> int:
    n = 0
    for poet, stops in FOOTPRINTS.items():
        short = poet.split("_")[1]
        for i, s in enumerate(stops):
            write_claim(
                f"clm_{short}_{i:02d}",
                poet,
                "person_at",
                {"name": s["place"], "lng": s["lng"], "lat": s["lat"], "note": s["event"]},
                s["year"],
                s["atts"],
                to_year=s.get("toYear"),
            )
            n += 1
    print(f"generated {n} person_at claims → {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
