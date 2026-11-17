"""ht — HistoryTrace 数据管线 CLI。"""

from __future__ import annotations

import json
from pathlib import Path

import click

from . import __version__
from .build import build as build_data
from .era import EraError, era_to_year, find_era
from .report import render_report
from .verify import run_verify_command


@click.group()
@click.version_option(__version__, prog_name="ht")
def main() -> None:
    """HistoryTrace 数据管线:verify(R0/R1) → build(静态产物) → report(质量报告)。"""


@main.command()
def verify() -> None:
    """R0(许可/schema)+ R1(机器一致性)校验。"""
    raise SystemExit(run_verify_command())


@main.command()
@click.option("--out", type=click.Path(path_type=Path), default=None, help="输出目录(默认 web/public/data)")
def build(out: Path | None) -> None:
    """由 claims 生成 web 静态产物。"""
    counts = build_data(out_dir=out)
    click.echo(
        f"build OK: places={counts['places']} claims={counts['claims']} "
        f"conf={counts['byConfidence']}"
    )


@main.command()
def report() -> None:
    """输出数据质量报告(协议 §10)。"""
    click.echo(render_report())


@main.command()
@click.argument("era")
@click.argument("n", type=int)
def era(era: str, n: int) -> None:
    """年号纪年 → 公元。例:ht era 贞观 14"""
    try:
        year = era_to_year(era, n)
    except EraError as e:
        raise SystemExit(f"error: {e}") from e
    hits = ", ".join(f"{e}{y}" for e, y in find_era(year)) or "-"
    click.echo(f"{era}{n}年 → {year}(公元;反查: {hits})")


@main.command("import-wikisource")
@click.argument("title")
@click.option("--out", type=click.Path(path_type=Path), default=None, help="输出文件(默认 data/_downloaded/wikisource/)")
def import_wikisource(title: str, out: Path | None) -> None:
    """从维基文库抓取页面 wikitext 到本地缓存(不进入 git)。"""
    from .import_wikisource import fetch_wikitext

    dest = out or (Path("data") / "_downloaded" / "wikisource" / f"{title}.txt")
    dest.parent.mkdir(parents=True, exist_ok=True)
    revid, text = fetch_wikitext(title)
    dest.write_text(text, encoding="utf-8")
    click.echo(f"saved {dest} (revid={revid}, {len(text)} 字)")


@main.command("import-cliopatria")
def import_cliopatria() -> None:
    """从本地 Cliopatria 缓存提取朝代疆界快照(→ web/public/data/boundaries.json)。"""
    from .cliopatria import build_boundaries

    stats = build_boundaries()
    for dyn, s in stats.items():
        click.echo(f"  {dyn} ({s['year']}): {s['polities']} polities")
    click.echo("boundaries.json OK")


@main.command()
@click.option("--dyn", default=None, help="只校某朝(如 han/tang/song/ming/qing)")
@click.option("--limit", type=int, default=None, help="限制条数(试跑)")
@click.option("--json-out", type=click.Path(path_type=Path), default=None, help="结果写 JSON")
def proofread(dyn: str | None, limit: int | None, json_out: Path | None) -> None:
    """L1 对校:维基文库 insource 核验 claim 条目(命中供人工回填引文)。"""
    from .proofread import proofread, render

    results = proofread(dyn_filter=dyn, limit=limit)
    if json_out:
        json_out.parent.mkdir(parents=True, exist_ok=True)
        json_out.write_text(
            json.dumps(
                [
                    {
                        "claimId": r.claim_id,
                        "source": r.source,
                        "term": r.term,
                        "status": r.status,
                        "pages": r.pages,
                    }
                    for r in results
                ],
                ensure_ascii=False,
                indent=1,
            )
            + "\n",
            encoding="utf-8",
        )
    click.echo(render(results))


@main.command()
@click.option("--dyn", default=None, help="只回填某朝")
@click.option("--limit", type=int, default=5, help="本批回填条数(限流友好)")
@click.option("--dry-run", is_flag=True, help="只检索不写回")
def backfill(dyn: str | None, limit: int, dry_run: bool) -> None:
    """引文回填:抓命中页原文片段回填 quote,生成复核队列(升 G4 须人工裁决)。"""
    from .backfill import run_backfill, write_review_queue

    report = run_backfill(dyn_filter=dyn, limit=limit, dry_run=dry_run)
    for r in report:
        click.echo(f"  [{r['status']}] {r['claimId']} {r['source']}「{r['term']}」")
    if not dry_run:
        queue = write_review_queue(report)
        click.echo(f"复核队列已生成:{queue}")
    done = sum(1 for r in report if r["status"] == "backfilled")
    click.echo(f"backfill {'(dry-run) ' if dry_run else ''}OK: {done}/{len(report)} 回填")


if __name__ == "__main__":
    main()


if __name__ == "__main__":
    main()
