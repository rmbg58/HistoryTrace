"""Cliopatria 疆界提取:v0.0.1 GeoJSON(本地缓存)→ 朝代快照 GeoJSON。

数据:Seshat Cliopatria v0.0.1(CC BY 4.0,DOI 10.5281/zenodo.13363121),
本地缓存 data/_downloaded/(不入库)。产物为**示意边界**(单一来源、未逐条考据),
web 端按"参考层"视觉降级展示(见 verification-protocol §8)。
"""

from __future__ import annotations

import zipfile
from pathlib import Path
from typing import Any

from shapely.geometry import Polygon, box, mapping, shape

from . import DATA_DIR, REPO_ROOT

CACHE_DIR = DATA_DIR / "_downloaded" / "cliopatria"
GEOJSON_NAME = "cliopatria.geojson"

# 中国历史主区包围盒(含西域/幽燕/岭南)
CHINA_BBOX = (70.0, 15.0, 140.0, 55.0)
SIMPLIFY_TOL = 0.02  # 度(约 2km),示意层够用

# 常见政权英文名 → 汉译(展示层编辑;未收录者展示原文)
ZH_NAMES: dict[str, str] = {
    "Han Dynasty": "汉",
    "Tang Dynasty": "唐",
    "Song Dynasty": "宋",
    "Northern Song": "北宋",
    "Ming Dynasty": "明",
    "Qing Dynasty": "清",
    "Tibetan Empire": "吐蕃",
    "Nanzhao": "南诏",
    "Dali Kingdom": "大理",
    "Uyghur Khaganate": "回鹘",
    "Second Turkic Khaganate": "后突厥",
    "Turks": "突厥",
    "First Turkic Khaganate": "突厥",
    "Western Turks": "西突厥",
    "Eastern Turks": "东突厥",
    "Khitan Liao Dynasty": "辽",
    "Liao Dynasty": "辽",
    "Kitans": "契丹",
    "Jin Dynasty": "金",
    "Western Xia": "西夏",
    "Tangut Xia": "西夏",
    "Balhae": "渤海",
    "Bohai": "渤海",
    "Unified Silla": "新罗",
    "Byeonhan": "弁韩",
    "Dongye": "东濊",
    "Buyeo": "夫余",
    "Goguryeo": "高句丽",
    "Great Yuan": "大宛",
    "Wusun": "乌孙",
    "Kangju": "康居",
    "Xiongnu": "匈奴",
    "Xianbei State": "鲜卑",
    "Chagatai Khanate": "察合台汗国",
    "Oirats": "瓦剌",
    "Tatars": "鞑靼",
    "Joseon": "朝鲜",
    "Ryukyu Kingdom": "琉球",
    "Yamato": "倭",
    "Ashikaga Shogunate": "室町幕府",
    "Pala Empire": "波罗王朝",
    "Gurjara-Pratihara Dynasty": "瞿折罗-波罗提诃罗",
    "Rashtrakuta Empire": "罗湿陀罗拘陀",
    "Chola Empire": "朱罗",
    "Delhi Sultanate": "德里苏丹国",
    "Ava Kingdom": "阿瓦王国",
    "Ayutthaya Kingdom": "阿瑜陀耶",
    "Pyu City-States": "骠人城邦",
    "Champa": "占城",
    "Khmer Empire": "高棉帝国",
    "Kashmir": "迦湿弥罗",
    "Yenisei Kyrgyz": "黠戛斯",
    "Karluks": "葛逻禄",
    "Samanid Empire": "萨曼王朝",
    "Abbasid Caliphate": "阿拔斯王朝",
    "Indian Civilizations": "印度诸国",
    "Indo-Greeks": "印度-希腊王国",
    "Scythians": "塞种",
    "Tocharians": "吐火罗",
    "Kucha": "龟兹",
    "Khotan": "于阗",
    "Kharosthi Kingdoms": "西域城郭诸国",
    "Tarim Basin City States": "西域城郭诸国",
    "Vietnamese Dynasties": "越南诸朝",
    "Dai Viet": "大越",
    "Mongol Empire": "蒙古帝国",
    "Yuan Dynasty": "元",
    "Northern Yuan": "北元",
    "Later Jin": "后金",
    "Sakya": "萨迦政权",
    "Phagmodrupa": "帕木竹巴",
    "Rinpungpa": "仁蚌巴",
    "Tsangpa": "藏巴汗",
}


def find_cached_geojson() -> Path:
    """定位本地缓存的 cliopatria.geojson(支持 zip 内嵌套)。"""
    direct = CACHE_DIR / GEOJSON_NAME
    if direct.exists():
        return direct
    for zdir in CACHE_DIR.glob("Seshat-*/"):
        inner = zdir / GEOJSON_NAME
        if inner.exists():
            return inner
        inner_zip = zdir / "cliopatria.geojson.zip"
        if inner_zip.exists():
            inner_zip.parent.mkdir(exist_ok=True)
            with zipfile.ZipFile(inner_zip) as zf:
                zf.extractall(zdir)
            return inner
    raise FileNotFoundError(
        "未找到 Cliopatria 缓存。请先从 Zenodo 下载 v0.0.1 并解压到 "
        f"{CACHE_DIR}(DOI 10.5281/zenodo.13363121)"
    )


def _feature_for_year(feat: dict[str, Any], year: int) -> bool:
    p = feat.get("properties", {})
    return p.get("FromYear", 1) <= year <= p.get("ToYear", -1)


def extract_snapshot(
    all_features: list[dict[str, Any]], year: int, china: Polygon
) -> list[dict[str, Any]]:
    """取某年与中国主区相交的政体,简化几何并翻译名称。"""
    out: list[dict[str, Any]] = []
    for feat in all_features:
        if not _feature_for_year(feat, year):
            continue
        geom = shape(feat["geometry"])
        if not geom.intersects(china):
            continue
        simplified = geom.simplify(SIMPLIFY_TOL, preserve_topology=True)
        if simplified.is_empty:
            continue
        props = feat["properties"]
        name = props.get("Name", "")
        name_key = name.strip("() ")  # 数据中部分名称带括号变体,如 "(Tang Dynasty)"
        out.append(
            {
                "name": name,
                "nameZh": ZH_NAMES.get(name_key, ""),
                "type": props.get("Type", "POLITY"),
                "wiki": props.get("Wikipedia", ""),
                "fromYear": props.get("FromYear"),
                "toYear": props.get("ToYear"),
                "geometry": mapping(simplified),
            }
        )
    out.sort(key=lambda f: f["name"])
    return out


def build_boundaries(out_dir: Path | None = None) -> dict[str, Any]:
    """生成 web/public/data/boundaries.json(按朝代取中位年快照)。"""
    import json as _json

    path = find_cached_geojson()
    with path.open(encoding="utf-8") as f:
        data = _json.load(f)
    feats = data.get("features", [])
    china = box(*CHINA_BBOX)

    dynasties = _json.loads((DATA_DIR / "dynasties.json").read_text(encoding="utf-8"))
    # 朝代中位年 → 快照年(取数据可命中的最近年:直接用中位年,区间连续)
    snapshots: dict[str, Any] = {}
    for dyn in dynasties:
        mid = round((dyn["earliest"] + dyn["latest"]) / 2)
        picked = extract_snapshot(feats, mid, china)
        snapshots[dyn["key"]] = {"year": mid, "label": dyn["label"], "features": picked}

    out = out_dir or (REPO_ROOT / "web" / "public" / "data")
    out.mkdir(parents=True, exist_ok=True)
    payload = {
        "meta": {
            "source": "Cliopatria v0.0.1 (Seshat Global History Databank)",
            "license": "CC-BY-4.0",
            "citation": (
                "Bennett, J. S., et al. (2025). Cliopatria: A geospatial database of "
                "world-wide political entities from 3400BCE to 2024CE. Scientific Data 12, 247. "
                "v0.0.1, DOI 10.5281/zenodo.13363121"
            ),
            "precisionHint": "示意边界:单一来源、未逐条考据,仅作参考层展示(协议 G2 思想)",
            "simplifyToleranceDeg": SIMPLIFY_TOL,
        },
        "snapshots": snapshots,
    }
    (out / "boundaries.json").write_text(
        _json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8"
    )
    return {
        dyn: {"year": v["year"], "polities": len(v["features"])} for dyn, v in snapshots.items()
    }
