"""构建产物与纪年换算测试。"""

from __future__ import annotations

import json

from ht.build import build
from ht.era import EraError, era_to_year, find_era


def test_build_deterministic_and_complete(tmp_path):
    counts1 = build(out_dir=tmp_path)
    snapshot1 = {p.name: p.read_text(encoding="utf-8") for p in sorted(tmp_path.rglob("*.json"))}
    counts2 = build(out_dir=tmp_path)
    snapshot2 = {p.name: p.read_text(encoding="utf-8") for p in sorted(tmp_path.rglob("*.json"))}
    assert snapshot1 == snapshot2, "构建必须可复现(排除时间戳)"
    assert counts1 == counts2
    assert counts1["places"] == 127
    assert counts1["claims"] >= 630

    index = json.loads((tmp_path / "index.json").read_text(encoding="utf-8"))
    assert len(index["dynasties"]) == 5
    assert len(index["places"]) == 127

    xian = json.loads((tmp_path / "lineages" / "plc_xian.json").read_text(encoding="utf-8"))
    names = [e["name"] for e in xian["lineage"]]
    assert names[0] == "长安"
    assert xian["lineage"][-1]["name"] == "西安府"
    # 每条沿革至少 2 佐证、置信不高于 G3(机器上限)
    for e in xian["lineage"]:
        assert len(e["attestations"]) >= 2
        assert e["confidence"] in ("G2", "G3")


def test_era_conversion():
    assert era_to_year("贞观", 14) == 640
    assert era_to_year("洪武", 1) == 1368
    assert era_to_year("康熙", 12) == 1673
    assert era_to_year("建元", 1) == -140
    with __import__("pytest").raises(EraError):
        era_to_year("不存在", 1)
    with __import__("pytest").raises(EraError):
        era_to_year("贞观", 30)  # 贞观共23年


def test_era_reverse():
    hits = dict(find_era(640))
    assert hits.get("贞观") == 14
    assert dict(find_era(1368)).get("洪武") == 1
