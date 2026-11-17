"""ht — HistoryTrace 数据管线 CLI。"""

from __future__ import annotations

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


if __name__ == "__main__":
    main()
