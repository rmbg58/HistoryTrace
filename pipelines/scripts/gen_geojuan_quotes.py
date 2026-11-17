"""通用卷页引文回填:抓各史地理志卷页全文,给名称类 claims 回填真源引文。

- 繁体转换(opencc s2t)检索;排除书目著录型出现(term+志);
- 命中→回填 attestation.quote(f『…』——《書》(書/卷N)),status 升 cross-checked
  (引文在档;G4 仍需双侧来源,本管道只填本史侧);
- 未命中→进入报告(人工复核名单)。

用法: uv run python scripts/gen_geojuan_quotes.py [--dyn han] [--limit N] [--dry-run]
"""

from __future__ import annotations

import json
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from ht.backfill import clean_wikitext, extract_context

REPO = Path(__file__).resolve().parents[2]
CLAIMS = REPO / "data" / "claims"

API = "https://zh.wikisource.org/w/api.php"
UA = "HistoryTrace/0.1 (open-source data pipeline)"

# src → (史书维基页名, 地理志候选卷段)  卷段为候选,脚本会逐卷探测(开头含"地理")
SOURCES = {
    "src_hanshu_ws": ("漢書", [28, 96]),
    "src_jiutangshu_ws": ("舊唐書", list(range(38, 42))),
    "src_songshi_ws": ("宋史", list(range(85, 91))),
    "src_mingshi_ws": ("明史", list(range(40, 47))),
    "src_qingshigao_ws": ("清史稿", list(range(53, 76))),
    "src_liaoshi_ws": ("遼史", list(range(37, 42))),
    "src_shiji_ws": ("史記", []),  # 史記无地理志,跳过
    "src_houhanshu_ws": ("後漢書", []),
}


def page_text(title: str) -> str | None:
    """带 429 退避的页面抓取(遵守 Wikimedia 礼仪)。"""
    params = {
        "action": "query",
        "prop": "revisions",
        "rvprop": "content",
        "rvslots": "main",
        "format": "json",
        "titles": title,
    }
    for attempt in range(4):
        req = urllib.request.Request(f"{API}?{urllib.parse.urlencode(params)}", headers={"User-Agent": UA})
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                data = json.load(r)
            time.sleep(2.0)
            for p in data["query"]["pages"].values():
                if "revisions" in p:
                    return p["revisions"][0]["slots"]["main"]["*"]
            return None
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < 3:
                time.sleep(15 * (attempt + 1))
                continue
            raise


def is_redirect(t: str) -> bool:
    return t.strip().lower().startswith("#redirect")


def page_text_any(book: str, j: int) -> str | None:
    """尝试两种卷页命名(零填充/不填充),如 漢書/卷028 与 清史稿/卷76。"""
    for title in (f"{book}/卷{j:03d}", f"{book}/卷{j:02d}", f"{book}/卷{j}"):
        raw = page_text(title)
        time.sleep(1.5)
        if raw and not is_redirect(raw):
            return raw
    return None


def load_geo_text(book: str, juans: list[int]) -> dict[int, str]:
    """逐卷抓取,仅保留非重定向、非空壳的正文页。"""
    out: dict[int, str] = {}
    for j in juans:
        raw = page_text_any(book, j)
        if not raw:
            continue
        plain = clean_wikitext(raw)
        if len(plain) < 500:  # 空壳
            continue
        out[j] = plain
    return out


def _trad(term: str) -> str:
    try:
        from opencc import OpenCC

        return OpenCC("s2t").convert(term)
    except ImportError:
        return term


def main() -> int:
    dyn_filter = None
    limit = None
    dry = False
    args = sys.argv[1:]
    if "--dyn" in args:
        dyn_filter = args[args.index("--dyn") + 1]
    if "--limit" in args:
        limit = int(args[args.index("--limit") + 1])
    dry = "--dry-run" in args

    try:
        from opencc import OpenCC  # noqa: F401  确认可用性
    except ImportError:
        print("warn: opencc 未安装,繁体检索不可用")

    claims_all = []
    for p in sorted(CLAIMS.glob("clm_*.json")) + sorted(CLAIMS.glob("evt_*.json")):
        claims_all.append(json.loads(p.read_text(encoding="utf-8")))

    targets = []
    for c in claims_all:
        if c["predicate"] != "name_in_period":
            continue
        if dyn_filter and not c["id"].endswith(f"_{dyn_filter}"):
            continue
        if all(a.get("quote") for a in c["attestations"]):
            continue  # 已有引文
        targets.append(c)
    if limit:
        targets = targets[:limit]

    # 按来源分组加载地理志全文(每书一次)
    geo_cache: dict[str, dict[int, str]] = {}

    def geo_for(sid: str) -> dict[int, str]:
        if sid not in geo_cache:
            book, juans = SOURCES[sid]
            geo_cache[sid] = load_geo_text(book, juans)
        return geo_cache[sid]

    filled, missed = 0, []
    for c in targets:
        cid = c["id"]
        for att in c["attestations"]:
            if att.get("quote"):
                continue
            sid = att["source"]
            if sid not in SOURCES or not SOURCES[sid][1]:
                continue
            book = SOURCES[sid][0]
            term_t = _trad(att["locus"].split("/")[-1].strip())
            geo = geo_for(sid)
            hit = None
            for j, plain in sorted(geo.items()):
                q = extract_context(plain, term_t)
                if q:
                    hit = (j, q)
                    break
            if not hit:
                missed.append((cid, sid, term_t))
                continue
            j, q = hit
            if not dry:
                att["quote"] = f"『{q}』——《{book}》({book}/卷{j:02d})"
                if c["status"] == "machine-checked":
                    c["status"] = "cross-checked"
                (CLAIMS / f"{cid}.json").write_text(
                    json.dumps(c, ensure_ascii=False, indent=1, sort_keys=True) + "\n", encoding="utf-8"
                )
            filled += 1
            print(f"[fill] {cid} ← {book}/卷{j:02d}「{term_t}」")
            break  # 每 claim 一条引文即够
        time.sleep(0.3)

    print(f"\n回填 {filled} | 未命中 {len(missed)}")
    if missed:
        print("未命中(人工复核):")
        for cid, sid, t in missed[:40]:
            print(f"  {cid} {sid}「{t}」")
    return 0


if __name__ == "__main__":
    sys.exit(main())
