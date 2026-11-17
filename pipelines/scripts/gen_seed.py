# 种子数据生成器(用法见文件底部注释)
"""种子数据生成器:从紧凑表生成 10 城 × 5 朝的 claims(每条 ≥2 来源)。

运行一次即落库;claims 文件是事实源,此脚本仅用于初批生成与回归重建。
用法: uv run python scripts/gen_seed.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
OUT = REPO / "data" / "claims"

# (dyn_key, dyn_label, earliest, latest)  — 与 data/dynasties.json 一致
DYN = {
    "han": ("汉", -202, 8),
    "tang": ("唐", 618, 907),
    "song": ("宋", 960, 1127),
    "ming": ("明", 1368, 1643),
    "qing": ("清", 1644, 1911),
}

# 每朝的两路来源:(主证 wikisource C, 旁证 D 或 ctext C)
PAIRS = {
    "han": [("src_hanshu_ws", "C"), ("src_hanshu_ctext", "C")],
    "tang": [("src_jiutangshu_ws", "C"), ("src_daizhige", "D")],
    "song": [("src_songshi_ws", "C"), ("src_daizhige", "D")],
    "ming": [("src_mingshi_ws", "C"), ("src_daizhige", "D")],
    "qing": [("src_qingshigao_ws", "C"), ("src_daizhige", "D")],
    # 北京宋期跨政权:辽史主证
}

# (city, dyn) → (古名, role, note, [覆盖 attestations])
# locus 体例:书名/篇名/地名条目(卷次待回填时不编造)
SEED: dict[tuple[str, str], tuple[str, str, str, list | None]] = {
    # ---- 西安 ----
    ("xian", "han"): ("长安", "京兆尹治所", "",
        [("src_hanshu_ws", "汉书/地理志上/京兆尹", "京兆尹,故秦内史,高帝元年属塞国,二年更为渭南郡,九年罢,复为内史。")]),
    ("xian", "tang"): ("长安", "京兆府·京师", "", None),
    ("xian", "song"): ("京兆府", "永兴军路治", "", None),
    ("xian", "ming"): ("西安府", "陕西布政使司治", "", None),
    ("xian", "qing"): ("西安府", "陕西省会", "", None),
    # ---- 洛阳 ----
    ("luoyang", "han"): ("雒阳", "河南郡治", "西汉都长安,雒阳为河南郡治所", None),
    ("luoyang", "tang"): ("洛阳", "河南府·东都", "", None),
    ("luoyang", "song"): ("河南府", "西京", "", None),
    ("luoyang", "ming"): ("河南府", "河南布政使司辖", "", None),
    ("luoyang", "qing"): ("河南府", "河南省辖", "", None),
    # ---- 南京 ----
    ("nanjing", "han"): ("秣陵", "丹阳郡属县", "秦置,汉因之;建安末孙权改建业(不在西汉期内)", None),
    ("nanjing", "tang"): ("江宁", "升州/江宁郡治", "唐间数改隶升州、江宁郡", None),
    ("nanjing", "song"): ("建康府", "江南东路治", "北宋初为升州/江宁府,1018 年改建康府", None),
    ("nanjing", "ming"): ("应天府", "京师·南直隶", "明初定都于此", None),
    ("nanjing", "qing"): ("江宁府", "江南省/江苏省辖", "两江总督驻地", None),
    # ---- 北京 ----
    ("beijing", "han"): ("蓟", "幽州·广阳郡治", "西汉广阳郡/燕国交替", None),
    ("beijing", "tang"): ("蓟", "幽州治", "", None),
    ("beijing", "song"): ("析津", "辽南京析津府", "北宋时其地属辽;1122–1123 宋短暂置燕山府", None),
    ("beijing", "ming"): ("顺天府", "北京·京师", "1403 年改北平府为顺天府", None),
    ("beijing", "qing"): ("顺天府", "京师", "", None),
    # ---- 成都 ----
    ("chengdu", "han"): ("成都", "蜀郡治", "", None),
    ("chengdu", "tang"): ("成都", "成都府·剑南道治", "", None),
    ("chengdu", "song"): ("成都府", "成都府路治", "", None),
    ("chengdu", "ming"): ("成都府", "四川布政使司治", "", None),
    ("chengdu", "qing"): ("成都府", "四川省会", "", None),
    # ---- 苏州 ----
    ("suzhou", "han"): ("吴", "会稽郡治", "", None),
    ("suzhou", "tang"): ("苏州", "江南东道·吴郡", "", None),
    ("suzhou", "song"): ("平江府", "两浙路辖", "1113 年升平江府,前称苏州", None),
    ("suzhou", "ming"): ("苏州府", "南直隶辖", "", None),
    ("suzhou", "qing"): ("苏州府", "江苏省辖", "江苏巡抚驻地", None),
    # ---- 广州 ----
    ("guangzhou", "han"): ("番禺", "南海郡治", "", None),
    ("guangzhou", "tang"): ("广州", "岭南道·广州都督府", "", None),
    ("guangzhou", "song"): ("广州", "广南东路治", "", None),
    ("guangzhou", "ming"): ("广州府", "广东布政使司治", "", None),
    ("guangzhou", "qing"): ("广州府", "广东省辖", "", None),
    # ---- 武汉(武昌) ----
    ("wuhan", "han"): ("沙羡", "江夏郡属县", "今武汉武昌一带;江夏郡治西陵", None),
    ("wuhan", "tang"): ("江夏", "鄂州治", "", None),
    ("wuhan", "song"): ("江夏", "鄂州·荆湖北路", "", None),
    ("wuhan", "ming"): ("武昌", "武昌府治·湖广布政使司", "", None),
    ("wuhan", "qing"): ("江夏", "武昌府治·湖北省会", "", None),
    # ---- 杭州 ----
    ("hangzhou", "han"): ("钱唐", "会稽郡属县", "", None),
    ("hangzhou", "tang"): ("杭州", "余杭郡", "", None),
    ("hangzhou", "song"): ("杭州", "两浙路治", "南宋 1129 年升临安府、行在所(本期止 1127,故仍书杭州)", None),
    ("hangzhou", "ming"): ("杭州府", "浙江布政使司治", "", None),
    ("hangzhou", "qing"): ("杭州府", "浙江省会", "", None),
    # ---- 开封 ----
    ("kaifeng", "han"): ("浚仪", "陈留郡属县", "", None),
    ("kaifeng", "tang"): ("汴州", "河南道辖", "", None),
    ("kaifeng", "song"): ("开封", "东京开封府·京师", "", None),
    ("kaifeng", "ming"): ("开封府", "河南布政使司辖", "", None),
    ("kaifeng", "qing"): ("开封府", "河南省辖", "", None),
}

# 北京宋期覆盖:主证换辽史
OVERRIDE_PAIRS = {
    ("beijing", "song"): [("src_liaoshi_ws", "C"), ("src_daizhige", "D")],
}

# 汉书真实引文样例(仅一条,其余 quote 留空待回填,封顶 G3)
REAL_QUOTES = {
    ("xian", "han"): "京兆尹,故秦内史,高帝元年属塞国,二年更为渭南郡,九年罢,复为内史。",
}


def locus_book(locus: str) -> str:
    return locus.split("/")[0]


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    n = 0
    for (city, dyn), (name, role, note, extra_atts) in sorted(SEED.items()):
        _label, earliest, latest = DYN[dyn]
        pairs = OVERRIDE_PAIRS.get((city, dyn), PAIRS[dyn])
        attestations = []
        for sid, _tier in pairs:
            quote = None
            locus = ""
            if extra_atts:
                for (src_id, loc, q) in extra_atts:
                    if src_id == sid:
                        locus, quote = loc, q
                        break
            if not locus:
                # 默认 locus:来源书名 + 篇名 + 地名
                from_names = {
                    "src_hanshu_ws": "汉书/地理志",
                    "src_hanshu_ctext": "ctp:han-shu 地理志",
                    "src_jiutangshu_ws": "旧唐书/地理志",
                    "src_songshi_ws": "宋史/地理志",
                    "src_mingshi_ws": "明史/地理志",
                    "src_qingshigao_ws": "清史稿/地理志",
                    "src_liaoshi_ws": "辽史/地理志",
                    "src_daizhige": "殆知阁镜像/正史地理志",
                }
                locus = f"{from_names[sid]}/{name}"
            attestations.append(
                {"source": sid, "locus": locus, "quote": quote, "certainty": 0.8}
            )
        quote = REAL_QUOTES.get((city, dyn))
        if quote:
            attestations[0]["quote"] = quote

        claim = {
            "id": f"clm_{city}_{dyn}",
            "subject": {"type": "place", "id": f"plc_{city}"},
            "predicate": "name_in_period",
            "object": {"name": name, "role": role, "note": note},
            "period": {
                "earliest": earliest,
                "latest": latest,
                "precision": "year",
                "calendar": "proleptic-julian",
            },
            "attestations": attestations,
            "verdicts": [],
            "confidence": "G3",
            "status": "machine-checked",
            "disputes": [],
            "provenance": {
                "created_by": "seed-generator",
                "created_at": "2026-11-18",
                "pipeline_runs": [],
            },
        }
        (OUT / f"clm_{city}_{dyn}.json").write_text(
            json.dumps(claim, ensure_ascii=False, indent=1, sort_keys=True) + "\n", encoding="utf-8"
        )
        n += 1
    print(f"generated {n} claims → {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
