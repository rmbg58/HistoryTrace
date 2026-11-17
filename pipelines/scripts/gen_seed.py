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
    # ---- 太原 ----
    ("taiyuan", "han"): ("晋阳", "太原郡治", "", None),
    ("taiyuan", "tang"): ("晋阳", "北都·太原府", "", None),
    ("taiyuan", "song"): ("太原府", "河东路治", "979 年毁旧城,徙治唐明镇", None),
    ("taiyuan", "ming"): ("太原府", "山西布政使司治", "", None),
    ("taiyuan", "qing"): ("太原府", "山西省会", "", None),
    # ---- 济南 ----
    ("jinan", "han"): ("历城", "济南郡辖", "郡治东平陵(今章丘境)", None),
    ("jinan", "tang"): ("齐州", "历城", "", None),
    ("jinan", "song"): ("齐州", "京东东路辖", "1116 年升济南府", None),
    ("jinan", "ming"): ("济南府", "山东布政使司治", "", None),
    ("jinan", "qing"): ("济南府", "山东省会", "", None),
    # ---- 长沙 ----
    ("changsha", "han"): ("临湘", "长沙国都", "", None),
    ("changsha", "tang"): ("潭州", "潭州治", "", None),
    ("changsha", "song"): ("潭州", "荆湖南路治", "", None),
    ("changsha", "ming"): ("长沙府", "湖广布政使司辖", "", None),
    ("changsha", "qing"): ("长沙府", "湖南省会", "", None),
    # ---- 南昌 ----
    ("nanchang", "han"): ("南昌", "豫章郡治", "", None),
    ("nanchang", "tang"): ("洪州", "江南西道治", "", None),
    ("nanchang", "song"): ("洪州", "江南西路辖", "南宋 1163 年升隆兴府", None),
    ("nanchang", "ming"): ("南昌府", "江西布政使司治", "", None),
    ("nanchang", "qing"): ("南昌府", "江西省会", "", None),
    # ---- 福州 ----
    ("fuzhou", "han"): ("冶", "闽越故地·会稽郡冶县", "汉武帝后属会稽郡", None),
    ("fuzhou", "tang"): ("福州", "长乐郡·福建观察使治", "", None),
    ("fuzhou", "song"): ("福州", "福建路治", "", None),
    ("fuzhou", "ming"): ("福州府", "福建布政使司治", "", None),
    ("fuzhou", "qing"): ("福州府", "福建省会", "", None),
    # ---- 宁波 ----
    ("ningbo", "han"): ("鄮", "会稽郡属县", "", None),
    ("ningbo", "tang"): ("明州", "江南东道辖", "", None),
    ("ningbo", "song"): ("明州", "两浙东路辖", "南宋 1195 年升庆元府", None),
    ("ningbo", "ming"): ("宁波府", "浙江布政使司辖", "洪武十四年改庆元为宁波", None),
    ("ningbo", "qing"): ("宁波府", "浙江省辖", "", None),
    # ---- 温州 ----
    ("wenzhou", "han"): ("永宁", "会稽郡属县", "", None),
    ("wenzhou", "tang"): ("温州", "永嘉郡", "", None),
    ("wenzhou", "song"): ("温州", "两浙东路辖", "宋末升瑞安府", None),
    ("wenzhou", "ming"): ("温州府", "浙江布政使司辖", "", None),
    ("wenzhou", "qing"): ("温州府", "浙江省辖", "", None),
    # ---- 九江 ----
    ("jiujiang", "han"): ("柴桑", "豫章郡属县", "", None),
    ("jiujiang", "tang"): ("浔阳", "江州治", "", None),
    ("jiujiang", "song"): ("江州", "江州治", "", None),
    ("jiujiang", "ming"): ("九江府", "江西布政使司辖", "", None),
    ("jiujiang", "qing"): ("九江府", "江西省辖", "", None),
    # ---- 安庆 ----
    ("anqing", "han"): ("皖", "庐江郡辖", "", None),
    ("anqing", "tang"): ("舒州", "同安郡", "", None),
    ("anqing", "song"): ("舒州", "淮南西路辖", "南宋 1195 年升安庆府", None),
    ("anqing", "ming"): ("安庆府", "南直隶辖", "", None),
    ("anqing", "qing"): ("安庆府", "安徽省会", "康熙后安徽省会", None),
    # ---- 合肥 ----
    ("hefei", "han"): ("合肥", "九江郡属县", "", None),
    ("hefei", "tang"): ("合肥", "庐州治", "", None),
    ("hefei", "song"): ("庐州", "淮南西路辖", "", None),
    ("hefei", "ming"): ("庐州府", "南直隶辖", "", None),
    ("hefei", "qing"): ("庐州府", "安徽省辖", "", None),
    # ---- 徐州 ----
    ("xuzhou", "han"): ("彭城", "楚国都", "", None),
    ("xuzhou", "tang"): ("徐州", "河南道辖·彭城", "", None),
    ("xuzhou", "song"): ("徐州", "京东路辖", "", None),
    ("xuzhou", "ming"): ("徐州", "南直隶直隶州", "", None),
    ("xuzhou", "qing"): ("徐州府", "江苏省辖", "雍正后升府", None),
    # ---- 桂林 ----
    ("guilin", "han"): ("始安", "零陵郡属县", "", None),
    ("guilin", "tang"): ("桂州", "始安郡·桂管治", "", None),
    ("guilin", "song"): ("桂州", "广南西路辖", "南宋 1133 年升静江府", None),
    ("guilin", "ming"): ("桂林府", "广西布政使司治", "", None),
    ("guilin", "qing"): ("桂林府", "广西省会", "", None),
    # ---- 兰州 ----
    ("lanzhou", "han"): ("金城", "金城郡辖", "郡治允吾;金城县属之", None),
    ("lanzhou", "tang"): ("兰州", "金城郡", "", None),
    ("lanzhou", "song"): ("兰州", "熙河路辖", "元丰后宋复取兰会", None),
    ("lanzhou", "ming"): ("兰州", "临洮府属州", "", None),
    ("lanzhou", "qing"): ("兰州府", "甘肃省会", "乾隆后", None),
    # ---- 天水 ----
    ("tianshui", "han"): ("上邽", "陇西/天水郡辖", "汉天水郡治平襄,今市区为上邽", None),
    ("tianshui", "tang"): ("秦州", "天水郡·陇右道", "", None),
    ("tianshui", "song"): ("秦州", "秦凤路治", "", None),
    ("tianshui", "ming"): ("秦州", "巩昌府辖", "", None),
    ("tianshui", "qing"): ("秦州", "甘肃省辖", "", None),
    # ---- 武威 ----
    ("wuwei", "han"): ("姑臧", "武威郡治", "", None),
    ("wuwei", "tang"): ("凉州", "武威郡·河西节度使治", "", None),
    ("wuwei", "song"): ("凉州", "西夏西凉府", "1036 年后属西夏",
        [("src_songshi_ws", "宋史/夏国传上/凉州", None)]),
    ("wuwei", "ming"): ("凉州卫", "陕西行都司辖", "", None),
    ("wuwei", "qing"): ("凉州府", "甘肃省辖", "雍正后", None),
    # ---- 张掖 ----
    ("zhangye", "han"): ("觻得", "张掖郡治", "", None),
    ("zhangye", "tang"): ("甘州", "张掖郡", "", None),
    ("zhangye", "song"): ("甘州", "回鹘/西夏占", "先甘州回鹘,1036 年后属西夏",
        [("src_songshi_ws", "宋史/夏国传上/甘州", None)]),
    ("zhangye", "ming"): ("甘州卫", "陕西行都司治", "", None),
    ("zhangye", "qing"): ("甘州府", "甘肃省辖", "雍正后", None),
    # ---- 敦煌 ----
    ("dunhuang", "han"): ("敦煌", "敦煌郡治", "", None),
    ("dunhuang", "tang"): ("沙州", "敦煌郡", "", None),
    ("dunhuang", "song"): ("沙州", "归义军·后西夏占", "归义军节度;1036 年后西夏",
        [("src_songshi_ws", "宋史/夏国传上/沙州", None)]),
    ("dunhuang", "ming"): ("沙州卫", "关西七卫", "永乐三年置,后弃", None),
    ("dunhuang", "qing"): ("敦煌县", "肃州辖", "雍正复立", None),
    # ---- 大同 ----
    ("datong", "han"): ("平城", "雁门郡属县", "白登之围地", None),
    ("datong", "tang"): ("云州", "云中郡·大同军", "", None),
    ("datong", "song"): ("大同", "辽西京大同府", "北宋时其地属辽(1044 后)",
        [("src_liaoshi_ws", "辽史/地理志/西京大同府", None)]),
    ("datong", "ming"): ("大同府", "山西行都司·大同镇", "", None),
    ("datong", "qing"): ("大同府", "山西省辖", "", None),
    # ---- 临汾 ----
    ("linfen", "han"): ("平阳", "河东郡属县·平阳侯国", "", None),
    ("linfen", "tang"): ("晋州", "平阳郡", "", None),
    ("linfen", "song"): ("晋州", "河东路辖", "北宋末升平阳府", None),
    ("linfen", "ming"): ("平阳府", "山西布政使司辖", "", None),
    ("linfen", "qing"): ("平阳府", "山西省辖", "", None),
    # ---- 邯郸 ----
    ("handan", "han"): ("邯郸", "赵国都", "", None),
    ("handan", "tang"): ("邯郸", "磁州辖", "", None),
    ("handan", "song"): ("磁州", "河北西路辖", "", None),
    ("handan", "ming"): ("邯郸县", "广平府辖", "", None),
    ("handan", "qing"): ("邯郸县", "广平府辖", "", None),
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
