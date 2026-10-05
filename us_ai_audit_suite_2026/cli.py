"""CLI entry point.

Usage:
    python -m us_ai_audit_suite_2026.cli --tokens theme.css \
        --evidence evidence.json --out audit_out/
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

from .engine import run_regulatory_audit, run_token_audit, score
from .judge import get_judge


def _to_markdown(results, summary, judge_note) -> str:
    lines = [
        "# US AI Audit Suite 2026 — Results",
        f"Generated: {date.today().isoformat()}",
        "",
        f"**Readiness: {summary['readiness_pct']}%** "
        f"({summary['counts'].get('PASS', 0)} pass / {summary['applicable']} applicable; "
        f"{summary['counts'].get('NOT_APPLICABLE', 0)} N/A)",
        "",
    ]
    if judge_note:
        lines += [f"> ⚠ {judge_note}", ""]
    lines.append("| ID | Status | Severity | Category | Detail |")
    lines.append("|---|---|---|---|---|")
    for r in results:
        detail = r.detail.replace("|", "\\|").replace("\n", " ")
        lines.append(f"| {r.id} | {r.status} | {r.severity} | {r.category} | {detail} |")
    lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="us-ai-audit-suite")
    ap.add_argument("--tokens", help="Path to CSS file with design tokens")
    ap.add_argument("--evidence", help="JSON file mapping check IDs to evidence")
    ap.add_argument("--no-openai", action="store_true",
                    help="Force the offline deterministic evaluator")
    ap.add_argument("--out", default="audit_out", help="Output directory")
    args = ap.parse_args(argv)

    evidence = {}
    if args.evidence:
        evidence = json.loads(Path(args.evidence).read_text())

    judge, note = get_judge(prefer_openai=not args.no_openai)

    results = run_regulatory_audit(judge, evidence)
    if args.tokens:
        results += run_token_audit(Path(args.tokens).read_text())

    summary = score(results)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    payload = {
        "suite": "us-ai-audit-suite-2026",
        "generated": date.today().isoformat(),
        "evaluator_note": note,
        "summary": summary,
        "results": [r.to_dict() for r in results],
    }
    (out / "audit_results.json").write_text(json.dumps(payload, indent=2))
    (out / "audit_results.md").write_text(_to_markdown(results, summary, note))

    print(f"readiness: {summary['readiness_pct']}%  "
          f"({summary['counts']})  evaluator: {judge.name}")
    if note:
        print(f"note: {note}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
