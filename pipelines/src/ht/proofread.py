"""L1 对校(维基文库):用 CirrusSearch insource 检索核验 claim 的 locus 条目
是否真实出现在对应史书原文中——命中仅证明"原文存在该条目",报告供人工回填引文;
任何升级到 G4 仍必须人工裁决(R3 铁律)。

用法: uv run ht proofread [--dyn han] [--json OUT]
"""

from __future__ import annotations

import json
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from typing import Any

from .import_wikisource import API, UA
from .loader import load_claims

# 来源 → 维基文库主页面标题(繁体,与 zh.wikisource 页面名一致)
BOOK_TITLES = {
    "src_hanshu_ws": "漢書",
    "src_shiji_ws": "史記",
    "src_houhanshu_ws": "後漢書",
    "src_jiutangshu_ws": "舊唐書",
    "src_tongjian_ws": "資治通鑑",
    "src_songshi_ws": "宋史",
    "src_liaoshi_ws": "遼史",
    "src_mingshi_ws": "明史",
    "src_qingshigao_ws": "清史稿",
}


@dataclass
class ProofResult:
    claim_id: str
    source: str
    term: str
    status: str  # hit | miss | unsupported
    pages: list[str] = field(default_factory=list)


def build_search_query(book: str, term: str) -> str:
    """构造 insource 检索 URL(纯函数,便于测试)。"""
    params = {
        "action": "query",
        "list": "search",
        "srsearch": f'insource:"{term}" intitle:{book}',
        "srlimit": "5",
        "format": "json",
    }
    return f"{API}?{urllib.parse.urlencode(params)}"


def parse_search_response(data: dict[str, Any]) -> list[str]:
    """从 search 响应提取页面标题。"""
    return [
        r["title"]
        for r in data.get("query", {}).get("search", [])
        if isinstance(r, dict) and "title" in r
    ]


def search_wikisource(book: str, term: str) -> list[str]:
    """串行检索,含 429 退避重试(遵守 Wikimedia API 礼仪)。"""
    import time

    for attempt in range(3):
        req = urllib.request.Request(build_search_query(book, term), headers={"User-Agent": UA})
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:  # 固定 https 域名
                data = json.load(resp)
            time.sleep(0.8)  # 请求间隔,避免触发限流
            return parse_search_response(data)
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < 2:
                time.sleep(3 * (attempt + 1))
                continue
            raise


def _proof_term(locus: str) -> str:
    """取 locus 末段作为检索词(条目/郡县名),转繁体(维基文库为繁体原文)。"""
    raw = locus.replace("ctp:han-shu ", "").split("/")[-1].strip()
    try:
        from opencc import OpenCC

        return OpenCC("s2t").convert(raw)
    except ImportError:  # 未装 opencc 时退回原词(繁简同形条目仍可命中)
        return raw


def proofread(dyn_filter: str | None = None, limit: int | None = None) -> list[ProofResult]:
    """对名称类 claims 逐条做 insource 对校检索。"""
    claims = [
        c
        for c in load_claims()
        if c["predicate"] == "name_in_period"
        and (dyn_filter is None or c["id"].endswith(f"_{dyn_filter}"))
    ]
    if limit:
        claims = claims[:limit]
    results: list[ProofResult] = []
    seen_terms: dict[tuple[str, str], list[str]] = {}
    for claim in claims:
        cid = claim["id"]
        for att in claim["attestations"]:
            sid = att["source"]
            if sid not in BOOK_TITLES:
                results.append(ProofResult(cid, sid, _proof_term(att["locus"]), "unsupported"))
                continue
            term = _proof_term(att["locus"])
            key = (sid, term)
            if key not in seen_terms:
                try:
                    seen_terms[key] = search_wikisource(BOOK_TITLES[sid], term)
                except (OSError, json.JSONDecodeError) as e:  # 网络失败不阻塞
                    seen_terms[key] = []
                    print(f"warn: search {term} in {sid} failed: {e}")
            pages = seen_terms[key]
            status = "hit" if pages else "miss"
            results.append(ProofResult(cid, sid, term, status, pages))
    return results


def render(results: list[ProofResult]) -> str:
    hits = sum(1 for r in results if r.status == "hit")
    miss = sum(1 for r in results if r.status == "miss")
    unsup = sum(1 for r in results if r.status == "unsupported")
    lines = [
        "# L1 对校报告(维基文库 insource)\n",
        f"- 检索条目:{len(results)} | 命中:{hits} | 未命中:{miss} | 不支持:{unsup}",
        "- 说明:命中仅证明原文存在该条目,供人工回填引文;升级 G4 必须人工裁决(协议 §5)",
        "- 注意:未命中可能为繁简/异体差异(维基文库为繁体,如 臨沅/毘陵),人工复核时需转换检索\n",
    ]
    misses = [r for r in results if r.status == "miss"]
    if misses:
        lines.append("## 未命中(待人工复核)\n")
        for r in misses[:50]:
            lines.append(f"- `{r.claim_id}` {r.source}:「{r.term}」")
        if len(misses) > 50:
            lines.append(f"- …另 {len(misses) - 50} 条")
    return "\n".join(lines)
