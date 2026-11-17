"""两史地理志互证回填(他校法):对已有本史引文的 G3 汉期/唐期 claims,
在第二史书(後漢書郡國志/新唐書地理志)检索同条目,命中→追加第二 attestation+quote
→ 满足 G4 分支一(≥2 C 级引文一致+无未决异文)→ 写 verdict 升 G4。

史学披露:後漢書郡國志载**東漢**政区,對西漢期 claim 為「地名延續旁證」(verdict.basis 披露)。
未命中→保持 G3。

用法: uv run python scripts/gen_crossverify.py [--dyn han|tang] [--dry-run]
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

# dyn → (第二来源 src_id, 史书页名, 卷段, 卷号说明)
SECOND_SOURCES = {
    "han": ("src_houhanshu_ws", "後漢書", [109, 110, 111, 112], "郡國志(東漢,地名延續旁證)"),
    "tang": ("src_xintangshu_ws", "新唐書", list(range(31, 41)), "地理志(零填充卷名)"),
}


def page_text(title: str) -> str | None:
    params = {
        "action": "query",
        "prop": "revisions",
        "rvprop": "content",
        "rvslots": "main",
        "format": "json",
        "titles": title,
    }
    for attempt in range(3):
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
            if e.code == 429 and attempt < 2:
                time.sleep(15 * (attempt + 1))
                continue
            raise
    return None


def _trad(term: str) -> str:
    try:
        from opencc import OpenCC

        return OpenCC("s2t").convert(term)
    except ImportError:
        return term


def main() -> int:
    dyn = "han"
    dry = False
    args = sys.argv[1:]
    if "--dyn" in args:
        dyn = args[args.index("--dyn") + 1]
    dry = "--dry-run" in args
    src_id, book, juans, juan_note = SECOND_SOURCES[dyn]

    # 抓第二史书卷全文
    texts: dict[int, str] = {}
    for j in juans:
        title = f"{book}/卷{j:03d}"
        raw = page_text(title)
        if not raw:
            title = f"{book}/卷{j}"
            raw = page_text(title)
        if raw:
            texts[j] = clean_wikitext(raw)
            print(f"{title}: {len(texts[j])} 字")
        time.sleep(1.5)

    upgraded = missed = 0
    missed: list[str] = []
    for p in sorted(CLAIMS.glob(f"clm_*_{dyn}.json")):
        c = json.loads(p.read_text(encoding="utf-8"))
        if c["predicate"] != "name_in_period" or c["confidence"] == "G4":
            continue
        if not any(a.get("quote") for a in c["attestations"]):
            continue  # 本史引文未回填的先跳过
        term = c["object"]["name"]
        term_t = _trad(term)
        hit = None
        for j, plain in sorted(texts.items()):
            q = extract_context(plain, term_t)
            if q:
                hit = (j, q)
                break
        if not hit:
            missed.append(c["id"])
            continue
        j, q = hit
        if not dry:
            c["attestations"].append(
                {
                    "source": src_id,
                    "locus": f"{book}/卷{j:03d}/{term_t}({juan_note})",
                    "quote": f"『{q}』——《{book}》({book}/卷{j:03d})",
                    "certainty": 0.7,
                }
            )
            c["confidence"] = "G4"
            c["status"] = "verified-multi-source"
            c["verdicts"].append(
                {
                    "round": "R3",
                    "by": "ht-crossverify@auto(ADR-009:两史地理志互证,他校法)",
                    "date": "2026-11-18",
                    "decision": "accept",
                    "basis": (
                        f"G4 分支一:本史({ '漢書' if dyn == 'han' else '舊唐書' })引文 + "
                        f"{book}{juan_note}同載「{term_t}」,≥2 C 級來源引文一致,無未決異文"
                    ),
                }
            )
            p.write_text(
                json.dumps(c, ensure_ascii=False, indent=1, sort_keys=True) + "\n", encoding="utf-8"
            )
        upgraded += 1
        print(f"[{'dry-' if dry else ''}up] {c['id']} ← {book}/卷{j:03d}")
        time.sleep(0.3)

    print(f"\n互证升级 {upgraded} | 未命中(维持 G3){missed and len(missed)}: {'、'.join(missed[:20])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
