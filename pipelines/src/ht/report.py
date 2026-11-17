"""数据质量报告(docs/verification-protocol.md §10)。"""

from __future__ import annotations

from collections import Counter

from .loader import load_claims, load_registry
from .verify import _computed_confidence, verify


def render_report() -> str:
    rep = verify()
    registry = load_registry()
    claims = load_claims()

    lines: list[str] = []
    lines.append("# 数据质量报告\n")
    lines.append(f"- claims 总数:{rep.total}")
    lines.append(f"- 校验错误:{sum(1 for i in rep.issues if i.level == 'error')}")
    lines.append(f"- 校验警告:{sum(1 for i in rep.issues if i.level == 'warn')}")

    conf = Counter()
    missing_quote = []
    source_use: Counter = Counter()
    for c in claims:
        conf[_computed_confidence(c, registry)] += 1
        if not any(a.get("quote") for a in c["attestations"]):
            missing_quote.append(c["id"])
        for a in c["attestations"]:
            source_use[a["source"]] += 1

    lines.append("- 置信分布(机器分):" + "、".join(f"{k}:{v}" for k, v in sorted(conf.items())))
    lines.append(f"- 缺引文(待回填,封顶 G3):{len(missing_quote)} 条")
    lines.append("- 来源使用:" + "、".join(f"{k}:{v}" for k, v in sorted(source_use.items())))
    if rep.issues:
        lines.append("\n## 未决问题\n")
        for i in rep.issues:
            lines.append(f"- `{i.claim_id}` [{i.rule}] {i.message}")
    lines.append("\n> 本报告由 `ht report` 生成,可随时重放。\n")
    return "\n".join(lines)
