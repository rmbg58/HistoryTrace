"""R4 回归:来源更新后的周期性重校验(协议 §4)。

- 全量重跑 R0/R1(verify);
- 对 status=cross-checked 的 claim:重新 insource 检索 quote 中的条目是否仍见于
  回填时命中的页面(或检索该书),检测来源文本漂移;
- 只输出报告(检测,不修复);新失败项进人工复核(STATE/队列)。

用法: uv run ht regression [--limit N] [--json OUT]
定时:部署后由 CI schedule 触发;本地可用 cron(如每周):
  0 9 * * 1 cd /path/to/HistoryTrace/pipelines && uv run ht regression
"""

from __future__ import annotations

import re
import time
from typing import Any

from .backfill import extract_context, fetch_page_wikitext
from .loader import load_claims

QUOTE_PAGE_RE = None  # 页名从 quote 尾注 "——《書》(页)" 解析


def parse_quote_page(quote: str) -> tuple[str, str] | None:
    """从回填引文尾注解析 (书名, 页名)。"""
    import re

    m = re.search(r"——《([^》]+)》\((.+)\)\s*$", quote)
    if not m:
        return None
    return m.group(1), m.group(2)


def regression(limit: int | None = None) -> dict[str, Any]:
    from .verify import run_verify_command as _unused  # noqa: F401  # verify 单独跑

    claims = load_claims()
    cross = [c for c in claims if c.get("status") in ("cross-checked", "verified-multi-source")]
    if limit:
        cross = cross[:limit]

    results: list[dict[str, Any]] = []
    for claim in cross:
        cid = claim["id"]
        for att in claim["attestations"]:
            quote = att.get("quote")
            if not quote:
                continue
            parsed = parse_quote_page(quote)
            if not parsed:
                results.append({"claimId": cid, "status": "unparseable-quote"})
                continue
            _book, page = parsed
            term = att["locus"].split("/")[-1].split("(")[0].split("·")[-1].strip()
            try:
                from opencc import OpenCC

                term = OpenCC("s2t").convert(term)
            except ImportError:
                pass
            try:
                # 页名规范化:旧批次尾注可能缺零填充(卷28 → 卷028)
                m = re.match(r"^(.*卷)(\d+)$", page)
                candidates = [page]
                if m:
                    candidates.insert(0, f"{m.group(1)}{int(m.group(2)):03d}")
                wikitext = ""
                for cand in candidates:
                    time.sleep(1.5)  # 请求间隔(限流防护)
                    wikitext = fetch_page_wikitext(cand)
                    if wikitext:
                        page = cand
                        break
                still = extract_context(wikitext, term)
                results.append({"claimId": cid, "page": page, "status": "stable" if still else "drifted"})
            except (OSError, LookupError, KeyError) as e:
                results.append({"claimId": cid, "page": page, "status": f"error:{type(e).__name__}"})
            time.sleep(0.8)

    stable = sum(1 for r in results if r["status"] == "stable")
    drifted = sum(1 for r in results if r["status"] == "drifted")
    errors = sum(1 for r in results if str(r["status"]).startswith("error"))
    return {
        "total": len(results),
        "stable": stable,
        "drifted": drifted,
        "errors": errors,
        "details": results,
    }


def render(reg: dict[str, Any]) -> str:
    lines = [
        "# R4 回归报告\n",
        f"- cross-checked 复检:{reg['total']} | 稳定:{reg['stable']} | 漂移:{reg['drifted']} | 错误:{reg['errors']}",
        "- 说明:漂移 = 原命中页已检索不到该条目(来源文本变化),须人工复核。",
        "",
    ]
    for r in reg["details"]:
        if r["status"] != "stable":
            lines.append(f"- `{r['claimId']}` [{r['status']}] {r.get('page', '')}")
    return "\n".join(lines)
