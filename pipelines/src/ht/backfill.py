"""引文回填:对 L1 对校命中的 attestation,从维基文库命中页抓取原文片段回填 quote。

- quote 是从来源页面截取的**真实原文**(非生成);
- claim status 升为 cross-checked(引文在档),**不自动升 G4**;
- 升 G4 必须人工在复核队列(docs/gov/threads/review-queue.md)裁决(R3 铁律)。

用法: uv run ht backfill [--dyn han] [--limit 5] [--dry-run]
"""

from __future__ import annotations

import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

from .import_wikisource import UA
from .loader import DATA_DIR, load_claims
from .proofread import BOOK_TITLES

WIKI = "https://zh.wikisource.org/w/api.php"
CONTEXT_BEFORE = 60
CONTEXT_AFTER = 140


def fetch_page_wikitext(title: str) -> str:
    import json as _json
    import time

    params = {
        "action": "query",
        "prop": "revisions",
        "rvprop": "content",
        "rvslots": "main",
        "format": "json",
        "titles": title,
    }
    for attempt in range(4):
        req = urllib_request(f"{WIKI}?{urllib.parse.urlencode(params)}")
        try:
            with req_open(req, timeout=60) as resp:
                data = _json.load(resp)
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < 3:
                time.sleep(15 * (attempt + 1))
                continue
            raise
        for page in data["query"]["pages"].values():
            if "revisions" in page:
                return page["revisions"][0]["slots"]["main"]["*"]
        return ""
    raise LookupError(f"页面不存在: {title}")


def urllib_request(url: str):
    import urllib.request

    return urllib.request.Request(url, headers={"User-Agent": UA})


def req_open(req, timeout: int):
    import urllib.request

    return urllib.request.urlopen(req, timeout=timeout)


def clean_wikitext(text: str) -> str:
    """粗清 wikitext 标记,保留可读原文。"""
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\{\{[^}]*\}\}", "", text)
    text = text.replace("[[", "").replace("]]", "").replace("'", "")
    return re.sub(r"\s+", "", text)  # 中文原文去空白(竖排录入常有换行)


def extract_context(wikitext: str, term: str) -> str | None:
    """在原文中定位条目名,截取前后文窗口。

    排除"书目著录"型出现(term 后紧跟「志」,如 艺文志里的「常德府志四十八卷」),
    只取真正描述政区的语境;全部为书目出现时返回 None。
    """
    plain = clean_wikitext(wikitext)
    start_pos = 0
    while True:
        i = plain.find(term, start_pos)
        if i < 0:
            return None
        nxt = i + len(term)
        if nxt < len(plain) and plain[nxt] == "志":
            start_pos = nxt
            continue
        start = max(0, i - CONTEXT_BEFORE)
        end = min(len(plain), i + len(term) + CONTEXT_AFTER)
        return plain[start:end]


def run_backfill(dyn_filter: str | None, limit: int, dry_run: bool) -> list[dict[str, Any]]:
    from .proofread import search_wikisource

    claims = load_claims()
    targets = [
        c
        for c in claims
        if c["predicate"] == "name_in_period"
        and (dyn_filter is None or c["id"].endswith(f"_{dyn_filter}"))
        and any(a.get("quote") in (None, "") for a in c["attestations"])
        and any(a["source"] in BOOK_TITLES for a in c["attestations"])
    ][:limit]

    report: list[dict[str, Any]] = []
    for claim in targets:
        cid = claim["id"]
        for att in claim["attestations"]:
            if att.get("quote"):
                continue
            sid = att["source"]
            if sid not in BOOK_TITLES:
                continue
            book = BOOK_TITLES[sid]
            term = att["locus"].split("/")[-1].strip()
            try:
                pages = search_wikisource(book, term)
                if not pages:
                    report.append({"claimId": cid, "source": sid, "term": term, "status": "miss"})
                    continue
                # 优先"卷"页(正文),避免命中考异/注释类页面
                page = next((p for p in pages if "卷" in p), pages[0])
                wikitext = fetch_page_wikitext(page)
                quote = extract_context(wikitext, term)
                time.sleep(0.8)
                if not quote:
                    report.append({"claimId": cid, "source": sid, "term": term, "status": "not-found-in-page"})
                    continue
                if not dry_run:
                    att["quote"] = f"『{quote}』——《{book}》({page})"
                    claim["status"] = "cross-checked" if claim["status"] == "machine-checked" else claim["status"]
                    path = DATA_DIR / "claims" / f"{cid}.json"
                    path.write_text(
                        json.dumps(claim, ensure_ascii=False, indent=1, sort_keys=True) + "\n",
                        encoding="utf-8",
                    )
                report.append({"claimId": cid, "source": sid, "term": term, "status": "backfilled", "page": page, "quote": quote})
            except Exception as e:  # noqa: BLE001 单条失败不阻塞整批
                report.append({"claimId": cid, "source": sid, "term": term, "status": f"error:{e}"})
    return report


def write_review_queue(report: list[dict[str, Any]]) -> Path:
    """生成/合并人工复核队列(裁决后由人工把 confidence 升 G4 并写 verdict)。"""
    out = DATA_DIR.parent / "docs" / "gov" / "threads" / "review-queue.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    ok = [r for r in report if r["status"] == "backfilled"]

    existing_ids: set[str] = set()
    existing_text = out.read_text(encoding="utf-8") if out.exists() else ""
    for m in re.finditer(r"^## `([^`]+)`", existing_text, re.MULTILINE):
        existing_ids.add(m.group(1))

    if not existing_text:
        header = [
            "# 引文复核队列(升 G4 待人工裁决)",
            "",
            "> 以下 claim 已由 `ht backfill` 从维基文库回填真实原文片段(status=cross-checked)。",
            "> 裁决方式:核对引文与 claim 断言一致后,在对应 claim 文件追加",
            '> `verdict {round:"R3", by:"<裁决人>", date:"<日期>", decision:"accept", basis:"引文核对一致"}`',
            "> 并将 confidence 升为 G4。机器与代理不得代替本裁决(协议 R3/R4)。",
            "",
        ]
        out.write_text("\n".join(header) + "\n", encoding="utf-8")

    lines: list[str] = []
    added = 0
    for r in ok:
        if r["claimId"] in existing_ids:
            continue
        lines.append(f"## `{r['claimId']}`({r['source']}·「{r['term']}」)")
        lines.append(f"- 命中页:{r.get('page', '-')}")
        lines.append(f"- 回填引文:{(r.get('quote') or '')[:120]}…")
        lines.append("")
        added += 1
    if lines:
        with out.open("a", encoding="utf-8") as f:
            f.write("\n".join(lines))
    return out
