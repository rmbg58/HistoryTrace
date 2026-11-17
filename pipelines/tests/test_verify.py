"""校验流水线测试。"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from ht.loader import LoadError, load_claims, load_registry, validate_against_schema
from ht.verify import _computed_confidence, verify

REPO = Path(__file__).resolve().parents[2]


def test_real_dataset_passes():
    """种子数据全量必须通过 R0+R1。"""
    report = verify()
    errors = [i for i in report.issues if i.level == "error"]
    assert not errors, f"种子数据存在校验错误: {[ (i.claim_id, i.message) for i in errors ]}"
    assert report.total >= 50, "种子数据应≥50条(10城×5朝)"


def test_computed_confidence_rules():
    registry = load_registry()
    two_c = {
        "attestations": [
            {"source": "src_hanshu_ws", "locus": "x"},
            {"source": "src_hanshu_ctext", "locus": "y"},
        ]
    }
    assert _computed_confidence(two_c, registry) == "G3"

    single = {"attestations": [{"source": "src_hanshu_ws", "locus": "x"}]}
    assert _computed_confidence(single, registry) == "G2"

    none = {"attestations": []}
    assert _computed_confidence(none, registry) == "G1"

    with_d = {
        "attestations": [
            {"source": "src_hanshu_ws", "locus": "x"},
            {"source": "src_daizhige", "locus": "y"},
        ]
    }
    assert _computed_confidence(with_d, registry) == "G3"  # 2源即G3;G4 需人工裁决


def test_restricted_source_rejected(tmp_path, monkeypatch):
    """受限来源(CHGIS/CBDB)进入 attestation 必须报错(ADR-002 红线)。"""
    claim = {
        "id": "clm_test_bad_src",
        "subject": {"type": "place", "id": "plc_xian"},
        "predicate": "name_in_period",
        "object": {"name": "长安"},
        "period": {"earliest": -202, "latest": 8, "precision": "year", "calendar": "proleptic-julian"},
        "attestations": [{"source": "src_chgis_v6", "locus": "v6_time_pref_pgn", "quote": None}],
        "verdicts": [],
        "confidence": "G2",
        "status": "draft",
        "disputes": [],
        "provenance": {"created_by": "test", "created_at": "2026-11-18", "pipeline_runs": []},
    }
    validate_against_schema(claim, "claim", Path("claim.json"))  # schema 本身合法
    # 把坏 claim 放入临时目录并让 loader 指向它
    claims_dir = REPO / "data" / "claims"
    target = claims_dir / "clm_test_bad_src.json"
    target.write_text(json.dumps(claim, ensure_ascii=False), encoding="utf-8")
    try:
        from ht import verify as verify_mod

        report = verify_mod.verify()
        rules = {(i.claim_id, i.rule) for i in report.issues if i.level == "error"}
        assert ("clm_test_bad_src", "R0-license") in rules
    finally:
        target.unlink()


def test_conflict_detection(tmp_path):
    """重叠时段未声明 disputes 必须报错(R2:冲突不合并)。"""
    from ht import verify as verify_mod

    base = {
        "subject": {"type": "place", "id": "plc_conflicttest"},
        "predicate": "name_in_period",
        "object": {"name": "X"},
        "period": {"earliest": 1, "latest": 100, "precision": "year", "calendar": "proleptic-julian"},
        "attestations": [
            {"source": "src_hanshu_ws", "locus": "a"},
            {"source": "src_hanshu_ctext", "locus": "b"},
        ],
        "verdicts": [],
        "confidence": "G3",
        "status": "draft",
        "disputes": [],
        "provenance": {"created_by": "test", "created_at": "2026-11-18", "pipeline_runs": []},
    }
    claims_dir = REPO / "data" / "claims"
    files = []
    for i, (name, disp) in enumerate([("甲", []), ("乙", ["clm_test_conflict_a"])]):
        c = dict(base)
        c["id"] = f"clm_test_conflict_{'ab'[i]}"
        c["object"] = {"name": name}
        c["disputes"] = disp
        p = claims_dir / f"{c['id']}.json"
        p.write_text(json.dumps(c, ensure_ascii=False), encoding="utf-8")
        files.append(p)
    try:
        report = verify_mod.verify()
        ids = {i.claim_id for i in report.issues if i.rule == "R1-conflict" and i.level == "error"}
        assert not ids, "disputes 声明后不应报冲突"
        # 去掉 disputes 再试
        for p in files:
            c = json.loads(p.read_text(encoding="utf-8"))
            c["disputes"] = []
            p.write_text(json.dumps(c, ensure_ascii=False), encoding="utf-8")
        report = verify_mod.verify()
        ids = {i.claim_id for i in report.issues if i.rule == "R1-conflict" and i.level == "error"}
        assert ids, "重叠且无 disputes 必须报冲突"
    finally:
        for p in files:
            p.unlink()


def test_every_claim_has_two_sources_minimum():
    """种子数据每条至少 2 个 attestation(M1 验收标准)。"""
    for c in load_claims():
        assert len(c["attestations"]) >= 2, f"{c['id']} 少于 2 来源"


def test_load_error_on_broken_json(tmp_path):
    bad = tmp_path / "broken.json"
    bad.write_text("{ not json", encoding="utf-8")
    with pytest.raises(LoadError):
        from ht.loader import load_json

        load_json(bad)
