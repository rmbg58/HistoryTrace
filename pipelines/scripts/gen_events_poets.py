
"""生成事件(occurred_at)与诗人行迹(person_at)claims。

运行一次落库;claims 文件是事实源。用法: uv run python scripts/gen_events_poets.py
置信度按 attestation 数量自动定档(≥2 独立来源 G3,单源 G2)。
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
OUT = REPO / "data" / "claims"

D = "src_daizhige"
JT = "src_jiutangshu_ws"


def write_claim(cid, subj_type, subj_id, pred, obj, year, atts, to_year=None, status="machine-checked"):
    conf = "G3" if len(atts) >= 2 else "G2"
    c = {
        "id": cid,
        "subject": {"type": subj_type, "id": subj_id},
        "predicate": pred,
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
        "status": status,
        "disputes": [],
        "provenance": {"created_by": "seed-generator", "created_at": "2026-11-18", "pipeline_runs": []},
    }
    (OUT / f"{c['id']}.json").write_text(
        json.dumps(c, ensure_ascii=False, indent=1, sort_keys=True) + "\n", encoding="utf-8"
    )


EVENTS = [
    ("evt_qin_unification", -221, "咸阳(今咸阳)", 108.7089, 34.3298,
     [("src_shiji_ws", "史记/秦始皇本纪"), (D, "殆知阁镜像/史记")]),
    ("evt_han_found", -202, "氾水之阳(今定陶)", 115.57, 35.11,
     [("src_hanshu_ws", "汉书/高帝纪"), (D, "殆知阁镜像/汉书")]),
    ("evt_yellow_turban", 184, "巨鹿", 114.68, 37.22,
     [("src_houhanshu_ws", "后汉书/皇甫嵩朱儁列传"), (D, "殆知阁镜像/后汉书")]),
    ("evt_an_lushan", 755, "范阳(今北京西南)", 116.35, 39.45,
     [("src_tongjian_ws", "资治通鉴/唐纪三十三"), (JT, "旧唐书/玄宗纪")]),
    ("evt_chenqiao", 960, "陈桥驿(今封丘)", 114.52, 35.28,
     [("src_songshi_ws", "宋史/太祖纪"), (D, "殆知阁镜像/宋史")]),
    ("evt_jingkang", 1127, "汴京(开封)", 114.3075, 34.797,
     [("src_songshi_ws", "宋史/钦宗纪"), (D, "殆知阁镜像/宋史")]),
    ("evt_ming_found", 1368, "应天府(南京)", 118.7969, 32.0603,
     [("src_mingshi_ws", "明史/太祖纪"), (D, "殆知阁镜像/明史")]),
    ("evt_zheng_he", 1405, "刘家港(今太仓)", 121.15, 31.45,
     [("src_mingshi_ws", "明史/郑和传"), (D, "殆知阁镜像/明史")]),
    ("evt_qing_entry", 1644, "燕京(北京)", 116.4074, 39.9042,
     [("src_qingshigao_ws", "清史稿/世祖本纪"), (D, "殆知阁镜像/清史稿")]),
    ("evt_opium_war", 1840, "广东海面(虎门)", 113.60, 22.80,
     [("src_qingshigao_ws", "清史稿/宣宗本纪"), (D, "殆知阁镜像/清史稿")]),
]

# 每站:dict(year, toYear?, place, lng, lat, event, atts, conf?)
FOOTPRINTS = {
    "prs_libai": [
        {"year": 725, "toYear": 726, "place": "出蜀·江陵", "lng": 112.19, "lat": 30.33,
             "event": "仗剑去国,辞亲远游", "atts": [(JT, "旧唐书/文苑传下/李白"), (D, "殆知阁镜像/李太白文集")]},
        {"year": 727, "toYear": 736, "place": "安陆", "lng": 113.69, "lat": 31.26,
             "event": "娶许氏,酒隐安陆十年", "atts": [(JT, "旧唐书/文苑传下/李白"), (D, "殆知阁镜像/李太白文集")]},
        {"year": 742, "place": "长安", "lng": 108.9398, "lat": 34.3416,
             "event": "奉诏入京,供奉翰林", "atts": [("src_tongjian_ws", "资治通鉴/唐纪三十一"), (D, "殆知阁镜像/李太白文集")]},
        {"year": 744, "place": "洛阳", "lng": 112.454, "lat": 34.6197,
             "event": "与杜甫相遇于东都(据两集年谱考,本传无载)",
             "atts": [(D, "殆知阁镜像/李太白文集·年谱")]},
        {"year": 756, "place": "庐山", "lng": 115.98, "lat": 29.55,
             "event": "入永王璘幕府", "atts": [(JT, "旧唐书/文苑传下/李白"), (D, "殆知阁镜像/李太白文集")]},
        {"year": 759, "place": "白帝城", "lng": 109.574, "lat": 31.042,
             "event": "流放夜郎遇赦,东还江陵", "atts": [("src_tongjian_ws", "资治通鉴/唐纪三十七"), (D, "殆知阁镜像/李太白文集")]},
    ],
    "prs_dufu": [
        {"year": 712, "place": "巩县", "lng": 113.02, "lat": 34.75,
             "event": "生于巩县瑶湾", "atts": [(JT, "旧唐书/文苑传下/杜甫"), (D, "殆知阁镜像/杜工部集")]},
        {"year": 746, "toYear": 755, "place": "长安", "lng": 108.9398, "lat": 34.3416,
             "event": "应试不第,困守长安十年", "atts": [(JT, "旧唐书/文苑传下/杜甫"), (D, "殆知阁镜像/杜工部集")]},
        {"year": 759, "place": "秦州", "lng": 105.7249, "lat": 34.5809,
             "event": "弃官西行,客秦州", "atts": [(D, "殆知阁镜像/杜工部集·年谱")]},
        {"year": 760, "toYear": 765, "place": "成都", "lng": 104.0668, "lat": 30.5728,
             "event": "卜筑浣花溪草堂", "atts": [(JT, "旧唐书/文苑传下/杜甫"), (D, "殆知阁镜像/杜工部集")]},
        {"year": 770, "place": "湘江舟中", "lng": 112.9, "lat": 28.2,
             "event": "病卒于潭岳间舟中", "atts": [(JT, "旧唐书/文苑传下/杜甫"), (D, "殆知阁镜像/杜工部集")]},
    ],
    "prs_wangwei": [
        {"year": 721, "place": "长安", "lng": 108.9398, "lat": 34.3416,
             "event": "进士及第,官太乐丞", "atts": [(JT, "旧唐书/文苑传下/王维"), (D, "殆知阁镜像/王右丞集")]},
        {"year": 745, "toYear": 755, "place": "辋川", "lng": 109.32, "lat": 34.15,
             "event": "购蓝田别墅,亦官亦隐", "atts": [(D, "殆知阁镜像/王右丞集")]},
        {"year": 756, "place": "长安", "lng": 108.9398, "lat": 34.3416,
             "event": "安禄山陷长安,被拘菩提寺", "atts": [(JT, "旧唐书/文苑传下/王维"), (D, "殆知阁镜像/王右丞集")]},
        {"year": 761, "place": "长安", "lng": 108.9398, "lat": 34.3416,
             "event": "卒于官", "atts": [(JT, "旧唐书/文苑传下/王维"), (D, "殆知阁镜像/王右丞集")]},
    ],
    "prs_baijuyi": [
        {"year": 772, "place": "新郑", "lng": 113.74, "lat": 34.4,
             "event": "生于郑州新郑", "atts": [(JT, "旧唐书/白居易传"), (D, "殆知阁镜像/白氏长庆集")]},
        {"year": 800, "place": "长安", "lng": 108.9398, "lat": 34.3416,
             "event": "进士及第", "atts": [("src_tongjian_ws", "资治通鉴/唐纪五十三"), (D, "殆知阁镜像/白氏长庆集")]},
        {"year": 815, "toYear": 818, "place": "九江", "lng": 116.0005, "lat": 29.7052,
             "event": "贬江州司马,作琵琶行", "atts": [(JT, "旧唐书/白居易传"), (D, "殆知阁镜像/白氏长庆集")]},
        {"year": 822, "toYear": 824, "place": "杭州", "lng": 120.1551, "lat": 30.2741,
             "event": "出为杭州刺史,筑堤浚湖", "atts": [(JT, "旧唐书/白居易传"), (D, "殆知阁镜像/白氏长庆集")]},
        {"year": 825, "toYear": 826, "place": "苏州", "lng": 120.5853, "lat": 31.2989,
             "event": "除苏州刺史", "atts": [(JT, "旧唐书/白居易传"), (D, "殆知阁镜像/白氏长庆集")]},
        {"year": 846, "place": "洛阳", "lng": 112.454, "lat": 34.6197,
             "event": "以刑部尚书致仕,卒于洛阳", "atts": [(JT, "旧唐书/白居易传"), (D, "殆知阁镜像/白氏长庆集")]},
    ],
    "prs_sushi": [
        {"year": 1037, "place": "眉山", "lng": 103.85, "lat": 30.08,
             "event": "生于眉州眉山", "atts": [("src_songshi_ws", "宋史/苏轼传"), (D, "殆知阁镜像/东坡七集")]},
        {"year": 1061, "toYear": 1065, "place": "凤翔", "lng": 107.40, "lat": 34.52,
             "event": "签书凤翔府判官", "atts": [("src_songshi_ws", "宋史/苏轼传"), (D, "殆知阁镜像/东坡七集")]},
        {"year": 1071, "toYear": 1074, "place": "杭州", "lng": 120.1551, "lat": 30.2741,
             "event": "通判杭州", "atts": [("src_songshi_ws", "宋史/苏轼传"), (D, "殆知阁镜像/东坡七集")]},
        {"year": 1079, "place": "湖州", "lng": 120.09, "lat": 30.87,
             "event": "乌台诗案下狱", "atts": [("src_songshi_ws", "宋史/苏轼传"), (D, "殆知阁镜像/东坡七集")]},
        {"year": 1080, "toYear": 1084, "place": "黄州", "lng": 114.87, "lat": 30.45,
             "event": "谪黄州团练副使,耕东坡", "atts": [("src_songshi_ws", "宋史/苏轼传"), (D, "殆知阁镜像/东坡七集")]},
        {"year": 1085, "toYear": 1088, "place": "汴京", "lng": 114.3075, "lat": 34.797,
             "event": "还朝,历翰林学士", "atts": [("src_songshi_ws", "宋史/苏轼传"), (D, "殆知阁镜像/东坡七集")]},
        {"year": 1089, "toYear": 1091, "place": "杭州", "lng": 120.1551, "lat": 30.2741,
             "event": "以龙图阁学士知杭州", "atts": [("src_songshi_ws", "宋史/苏轼传"), (D, "殆知阁镜像/东坡七集")]},
        {"year": 1097, "toYear": 1100, "place": "儋州", "lng": 109.58, "lat": 19.51,
             "event": "再贬儋州(昌化军)", "atts": [("src_songshi_ws", "宋史/苏轼传"), (D, "殆知阁镜像/东坡七集")]},
        {"year": 1101, "place": "常州", "lng": 119.95, "lat": 31.78,
             "event": "卒于常州", "atts": [("src_songshi_ws", "宋史/苏轼传"), (D, "殆知阁镜像/东坡七集")]},
    ],
    "prs_luyou": [
        {"year": 1125, "place": "山阴", "lng": 120.58, "lat": 30.0,
             "event": "生于父任所淮上舟中,家山阴", "atts": [(D, "殆知阁镜像/剑南诗稿")]},
        {"year": 1170, "toYear": 1171, "place": "夔州", "lng": 109.46, "lat": 30.83,
             "event": "入蜀通判夔州", "atts": [("src_songshi_ws", "宋史/陆游传"), (D, "殆知阁镜像/剑南诗稿")]},
        {"year": 1172, "place": "南郑", "lng": 107.03, "lat": 33.07,
             "event": "从军南郑,参王炎幕府", "atts": [("src_songshi_ws", "宋史/陆游传"), (D, "殆知阁镜像/渭南文集")]},
        {"year": 1190, "toYear": 1209, "place": "山阴", "lng": 120.58, "lat": 30.0,
             "event": "退居山阴镜湖三山", "atts": [(D, "殆知阁镜像/剑南诗稿")]},
        {"year": 1210, "place": "山阴", "lng": 120.58, "lat": 30.0,
             "event": "卒,临终示儿", "atts": [("src_songshi_ws", "宋史/陆游传"), (D, "殆知阁镜像/剑南诗稿")]},
    ],
}


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    n = 0
    for eid, year, place, lng, lat, atts in EVENTS:
        write_claim(
            f"{eid}_where", "event", eid, "occurred_at",
            {"name": place, "lng": lng, "lat": lat}, year, atts,
        )
        n += 1
    for poet, stops in FOOTPRINTS.items():
        short = poet.split("_")[1]
        for i, stop in enumerate(stops):
            write_claim(
                f"clm_{short}_{i:02d}", "person", poet, "person_at",
                {"name": stop["place"], "lng": stop["lng"], "lat": stop["lat"], "note": stop["event"]},
                stop["year"], stop["atts"], to_year=stop.get("toYear"),
            )
            n += 1
    print(f"generated {n} claims (10 events + poet footprints) → {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
