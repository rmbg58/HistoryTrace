"""维基文库批量抓取(MediaWiki API,遵守礼仪:UA 标识 + 串行)。"""

from __future__ import annotations

import urllib.parse
import urllib.request

API = "https://zh.wikisource.org/w/api.php"
UA = "HistoryTrace/0.1 (open-source data pipeline; contact: repo issues)"


def build_query(title: str) -> str:
    """构造取页面 wikitext 的 API URL(纯函数,便于测试)。"""
    params = {
        "action": "query",
        "prop": "revisions",
        "rvprop": "content",
        "rvslots": "main",
        "format": "json",
        "titles": title,
    }
    return f"{API}?{urllib.parse.urlencode(params)}"


def fetch_wikitext(title: str) -> tuple[str, str]:
    """抓取页面 wikitext,返回 (revid, wikitext)。遵守 Wikimedia API 礼仪。"""
    req = urllib.request.Request(build_query(title), headers={"User-Agent": UA})
    import json

    with urllib.request.urlopen(req, timeout=30) as resp:  # 固定 https 域名,参数不可控外部输入
        data = json.load(resp)
    pages = data["query"]["pages"]
    for page in pages.values():
        rev = page["revisions"][0]
        return str(rev["revid"]), rev["slots"]["main"]["*"]
    raise LookupError(f"维基文库未找到页面: {title}")
