"""校验流水线:R0(许可/schema)与 R1(机器一致性)。

铁律(见 docs/verification-protocol.md §0):
- R1 每条声明必有来源;R2 冲突不合并;R3 机器只降级不升级;R4 理校永不自动定论。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .loader import LoadError, load_claims, load_registry, load_whitelist

# 置信等级序(越高越可信)
G_ORDER = {"G1": 1, "G2": 2, "G3": 3, "G4": 4}

# 机器可给出的最高等级:G4 必须有人工裁决(R3 铁律)
MACHINE_CEILING = "G3"


@dataclass
class Issue:
    claim_id: str
    level: str  # error | warn
    message: str
    rule: str  # R0/R1-xxx


@dataclass
class VerifyReport:
    issues: list[Issue] = field(default_factory=list)
    total: int = 0
    downgraded: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not any(i.level == "error" for i in self.issues)


def _computed_confidence(claim: dict[str, Any], registry: dict[str, dict[str, Any]]) -> str:
    """机器置信:只依据 attestation 的来源数量与层级(不含人工裁决)。"""
    atts = claim.get("attestations", [])
    if not atts:
        return "G1"
    if len(atts) >= 2:
        return "G3"
    return "G2"


def verify() -> VerifyReport:
    """执行 R0 + R1,返回报告。error 表示阻塞入库/构建。"""
    report = VerifyReport()
    registry = load_registry()
    whitelist = load_whitelist()
    claims = load_claims()
    report.total = len(claims)
    distributable = set(whitelist["distributable"])

    seen: dict[tuple[str, str], list[dict[str, Any]]] = {}

    for claim in claims:
        cid = claim["id"]

        # ---- R0: 来源引用与许可 ----
        if not claim.get("attestations"):
            report.issues.append(Issue(cid, "error", "无任何 attestation(违反铁律 R1:每条声明必有来源)", "R0"))
        for att in claim.get("attestations", []):
            sid = att["source"]
            if sid not in registry:
                report.issues.append(Issue(cid, "error", f"attestation 引用未注册来源 {sid}", "R0"))
                continue
            if sid in registry and sid not in distributable:
                report.issues.append(
                    Issue(
                        cid,
                        "error",
                        f"受限来源 {sid} 不得进入 attestation(ADR-002);只能写入 verdict.basis",
                        "R0-license",
                    )
                )

        # ---- R1: 一致性 ----
        period = claim["period"]
        if period["latest"] < period["earliest"]:
            report.issues.append(Issue(cid, "error", "period.latest < earliest", "R1-period"))

        for att in claim.get("attestations", []):
            c = att.get("certainty")
            if c is not None and not (0 <= c <= 1):
                report.issues.append(Issue(cid, "error", f"certainty 越界: {c}", "R1"))

        # 置信度机器复核(R3:只降级不升级)
        computed = _computed_confidence(claim, registry)
        claimed = claim["confidence"]
        if G_ORDER[claimed] > G_ORDER[computed]:
            report.issues.append(
                Issue(cid, "error", f"置信度 {claimed} 高于机器上限 {computed}(R3 铁律)", "R1-confidence")
            )
        elif claimed != computed:
            report.downgraded.append(cid)
        if G_ORDER[claimed] >= G_ORDER["G4"]:
            has_verdict = any(v["decision"] == "accept" for v in claim.get("verdicts", []))
            has_quotes = all(att.get("quote") for att in claim.get("attestations", []))
            if not (has_verdict and has_quotes):
                report.issues.append(
                    Issue(cid, "error", "G4 必须有人工 accept 裁决且全部 attestation 带引文", "R1-g4")
                )

        # 冲突检测(R2:重叠时段视为冲突,除非已声明 disputes)
        key = (claim["subject"]["id"], claim["predicate"])
        seen.setdefault(key, []).append(claim)

    for (subj, pred), group in seen.items():
        if len(group) < 2:
            continue
        for i, a in enumerate(group):
            for b in group[i + 1 :]:
                if a["period"]["earliest"] <= b["period"]["latest"] and b["period"]["earliest"] <= a["period"]["latest"]:
                    if a.get("disputes") or b.get("disputes"):
                        continue
                    report.issues.append(
                        Issue(
                            a["id"],
                            "error",
                            f"与 {b['id']} 时段重叠且未声明 disputes(R2:冲突不合并) [{subj}/{pred}]",
                            "R1-conflict",
                        )
                    )

    return report


def run_verify_command() -> int:
    try:
        report = verify()
    except LoadError as e:
        print(f"FAIL: {e}")
        return 2
    errors = [i for i in report.issues if i.level == "error"]
    warns = [i for i in report.issues if i.level == "warn"]
    print(f"claims: {report.total} | errors: {len(errors)} | warns: {len(warns)}")
    for i in report.issues:
        print(f"  [{i.level}] {i.claim_id} {i.rule}: {i.message}")
    if report.downgraded:
        print(f"  机器降级(R3,已按机器分生效): {', '.join(report.downgraded)}")
    print("OK" if report.ok else "FAIL")
    return 0 if report.ok else 1
