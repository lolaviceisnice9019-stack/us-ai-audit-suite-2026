"""Audit engine: runs regulatory checks and design-token checks, scores honestly.

Scoring:
- readiness = PASS / (PASS + FAIL + WARN + UNVERIFIED)  — N/A excluded.
- UNVERIFIED counts AGAINST readiness. This is deliberate: unverified is not
  compliant.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, asdict

from .judge import Judge
from .regulations import REGULATIONS
from .tokens import (
    classify_tokens,
    contrast_ratio,
    parse_css_variables,
    wcag_grade,
)


@dataclass
class CheckResult:
    id: str
    category: str
    title: str
    status: str
    severity: str
    detail: str
    evaluator: str
    remediation: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


def run_regulatory_audit(
    judge: Judge,
    evidence: dict[str, str] | None = None,
    regulations: list[dict] | None = None,
) -> list[CheckResult]:
    evidence = evidence or {}
    regulations = regulations if regulations is not None else REGULATIONS
    results: list[CheckResult] = []
    for check in regulations:
        verdict = judge.evaluate(check, evidence.get(check["id"], ""))
        remediation = ""
        if verdict.status in ("FAIL", "UNVERIFIED"):
            remediation = check["evidence_prompt"]
        results.append(
            CheckResult(
                id=check["id"],
                category=f"{check['jurisdiction']} — {check['law']}",
                title=check["requirement"][:160].rstrip() + ("…" if len(check["requirement"]) > 160 else ""),
                status=verdict.status,
                severity=check["severity"],
                detail=verdict.rationale,
                evaluator=verdict.evaluator,
                remediation=remediation,
            )
        )
    return results


def run_token_audit(css_text: str) -> list[CheckResult]:
    """Real WCAG contrast audit over the design system's own tokens."""
    results: list[CheckResult] = []
    variables = parse_css_variables(css_text)
    if not variables:
        return [
            CheckResult(
                id="DS-TOKENS-00",
                category="Design tokens",
                title="CSS custom properties present",
                status="FAIL",
                severity="high",
                detail="No CSS custom properties found in the provided source.",
                evaluator="deterministic-wcag",
                remediation="Supply the design system's token/theme CSS.",
            )
        ]

    foregrounds, backgrounds = classify_tokens(variables)
    if not foregrounds or not backgrounds:
        results.append(
            CheckResult(
                id="DS-TOKENS-01",
                category="Design tokens",
                title="Classifiable foreground/background color tokens",
                status="FAIL",
                severity="high",
                detail=(
                    f"Parsed {len(variables)} tokens but could not classify "
                    f"foregrounds ({len(foregrounds)}) and backgrounds "
                    f"({len(backgrounds)})."
                ),
                evaluator="deterministic-wcag",
                remediation="Name color tokens with clear fg/bg roles.",
            )
        )
        return results

    # Every foreground against every background surface it may sit on.
    pairs = []
    for fg_name, fg_val in sorted(foregrounds.items()):
        for bg_name, bg_val in sorted(backgrounds.items()):
            ratio = contrast_ratio(fg_val, bg_val)
            pairs.append((fg_name, bg_name, ratio))

    failing = [p for p in pairs if p[2] < 4.5]
    marginal = [p for p in pairs if 4.5 <= p[2] < 7.0]
    passing = [p for p in pairs if p[2] >= 7.0]

    if failing:
        worst = min(failing, key=lambda p: p[2])
        detail = (
            f"{len(failing)}/{len(pairs)} fg/bg pairs fail WCAG AA normal text "
            f"(<4.5:1). Worst: --{worst[0]} on --{worst[1]} = {worst[2]:.2f}:1. "
            + "All failures: "
            + "; ".join(f"--{f} on --{b} = {r:.2f}" for f, b, r in failing)
        )
        status, sev = "FAIL", "high"
    elif marginal:
        detail = (
            f"All {len(pairs)} pairs pass AA; {len(marginal)} pairs below AAA "
            "(<7:1): " + "; ".join(f"--{f} on --{b} = {r:.2f}" for f, b, r in marginal)
        )
        status, sev = "WARN", "low"
    else:
        detail = f"All {len(pairs)} fg/bg pairs meet WCAG AAA (>=7:1)."
        status, sev = "PASS", "info"

    results.append(
        CheckResult(
            id="DS-CONTRAST-01",
            category="Design tokens",
            title="WCAG 2.x contrast for text tokens on surfaces (AA 4.5:1 / AAA 7:1)",
            status=status,
            severity=sev,
            detail=detail,
            evaluator="deterministic-wcag",
            remediation=(
                "Raise luminance of failing text tokens (e.g. --color-subtle, "
                "--color-danger) or darken surfaces." if status == "FAIL" else ""
            ),
        )
    )

    # AAA-grade the pairs individually for the record.
    for fg_name, bg_name, ratio in pairs:
        grade = wcag_grade(ratio)
        results.append(
            CheckResult(
                id=f"DS-CONTRAST-PAIR::{fg_name}::{bg_name}",
                category="Design tokens — pair detail",
                title=f"--{fg_name} on --{bg_name}",
                status="PASS" if grade in ("AA", "AAA") else "FAIL",
                severity="info" if grade in ("AA", "AAA") else "medium",
                detail=f"contrast {ratio:.2f}:1 — WCAG {grade}",
                evaluator="deterministic-wcag",
            )
        )

    # Reduced motion support.
    has_prm = bool(re.search(r"prefers-reduced-motion\s*:\s*reduce", css_text))
    has_broken = bool(re.search(r"!\s*important\s*;", css_text) and
                      re.search(r"important\s*;\s*important", css_text))
    if has_prm and not has_broken:
        prm_status, prm_detail = "PASS", (
            "prefers-reduced-motion media query present and syntactically clean.")
    elif has_prm and has_broken:
        prm_status, prm_detail = "WARN", (
            "prefers-reduced-motion block exists but contains malformed "
            "declarations (repeated '!important'); the rule may not apply.")
    else:
        prm_status, prm_detail = "FAIL", (
            "No prefers-reduced-motion handling found while motion tokens "
            "(--motion-*) exist.")
    results.append(
        CheckResult(
            id="DS-MOTION-01",
            category="Design tokens",
            title="Reduced-motion accessibility support",
            status=prm_status,
            severity="medium" if prm_status != "PASS" else "info",
            detail=prm_detail,
            evaluator="deterministic-css",
            remediation=(
                "Add a clean @media (prefers-reduced-motion: reduce) block "
                "that neutralizes animations." if prm_status != "PASS" else ""
            ),
        )
    )
    return results


def score(results: list[CheckResult]) -> dict:
    counts: dict[str, int] = {}
    for r in results:
        counts[r.status] = counts.get(r.status, 0) + 1
    applicable = sum(
        counts.get(s, 0) for s in ("PASS", "FAIL", "WARN", "UNVERIFIED")
    )
    passes = counts.get("PASS", 0)
    readiness = (passes / applicable) if applicable else 0.0
    return {
        "counts": counts,
        "total": len(results),
        "applicable": applicable,
        "readiness": round(readiness, 4),
        "readiness_pct": round(readiness * 100, 1),
    }
