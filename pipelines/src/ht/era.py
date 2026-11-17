"""历史纪年换算(最小集):年号 ⇄ 公元。

覆盖种子朝代常用年号;后续按需扩充并交叉验证
(CBDB NIANHAO 表为受限来源,只作本地比对,不入此文件——ADR-002)。
"""

from __future__ import annotations

# 年号 → (起年公元, 讫年公元)
ERAS: dict[str, tuple[int, int]] = {
    "建元": (-140, -135),
    "元狩": (-122, -117),
    "贞观": (627, 649),
    "开元": (713, 741),
    "天宝": (742, 756),
    "庆历": (1041, 1048),
    "元丰": (1078, 1085),
    "洪武": (1368, 1398),
    "永乐": (1403, 1424),
    "万历": (1573, 1620),
    "康熙": (1662, 1722),
    "乾隆": (1736, 1795),
    "道光": (1821, 1850),
    "光绪": (1875, 1908),
}


class EraError(ValueError):
    """年号/序年无法换算。"""


def era_to_year(era: str, n: int) -> int:
    """年号 N 年 → 公元年。贞观十四年 → 640。"""
    if era not in ERAS:
        raise EraError(f"未收录年号: {era}")
    start, end = ERAS[era]
    year = start + n - 1
    if year > end:
        raise EraError(f"{era}{n}年超出该年号范围({start}–{end})")
    return year


def find_era(year: int) -> list[tuple[str, int]]:
    """公元年 → [(年号, 序年)]。只返回完整覆盖该年的年号。"""
    hits = []
    for era, (start, end) in ERAS.items():
        n = year - start + 1
        if 1 <= n <= end - start + 1:
            hits.append((era, n))
    return hits
