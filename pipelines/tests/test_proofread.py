"""L1 对校管道测试(离线:只测纯函数)。"""

from __future__ import annotations

from ht.proofread import build_search_query, parse_search_response, proofread, render


def test_build_query():
    url = build_search_query("漢書", "京兆尹")
    assert "action=query" in url
    assert "insource%3A%22%E4%BA%AC%E5%85%86%E5%B0%B9%22" in url  # insource:"京兆尹"
    assert "intitle%3A%E6%BC%A2%E6%9B%B8" in url  # intitle:漢書


def test_parse_response():
    data = {
        "query": {
            "search": [
                {"title": "漢書/卷028上", "ns": 0},
                {"title": "漢書/卷028下", "ns": 0},
            ]
        }
    }
    assert parse_search_response(data) == ["漢書/卷028上", "漢書/卷028下"]
    assert parse_search_response({}) == []


def test_proofread_term_extraction():
    """取 locus 末段为检索词;unsupported 来源标记正确。"""
    from unittest.mock import patch

    fake = {"query": {"search": [{"title": "漢書/卷028上"}]}}
    with patch("ht.proofread.search_wikisource", return_value=parse_search_response(fake)), \
         patch("ht.proofread.load_claims") as fake_claims:
        fake_claims.return_value = [
            {
                "id": "clm_xian_han",
                "predicate": "name_in_period",
                "subject": {"type": "place", "id": "plc_xian"},
                "attestations": [
                    {"source": "src_hanshu_ws", "locus": "汉书/地理志上/京兆尹"},
                    {"source": "src_daizhige", "locus": "殆知阁镜像/汉书/京兆尹"},
                ],
            }
        ]
        results = proofread()
    assert len(results) == 2
    assert results[0].status == "hit"
    assert results[0].pages == ["漢書/卷028上"]
    assert results[1].status == "unsupported"


def test_render_report():
    from ht.proofread import ProofResult

    out = render(
        [
            ProofResult("a", "src_hanshu_ws", "京兆尹", "hit", ["漢書/卷028上"]),
            ProofResult("b", "src_songshi_ws", "某州", "miss", []),
        ]
    )
    assert "命中:1" in out
    assert "未命中:1" in out
    assert "`b`" in out
