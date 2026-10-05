"""Tests for the audit engine and scoring integrity."""

from us_ai_audit_suite_2026.engine import (
    CheckResult,
    run_regulatory_audit,
    run_token_audit,
    score,
)
from us_ai_audit_suite_2026.judge import OfflineJudge
from us_ai_audit_suite_2026.regulations import REGULATIONS

DARK_THEME = """
@theme {
  --color-bg: #0c0c0e;
  --color-surface: #161618;
  --color-fg: #eeeee8;
  --color-muted: #9aa8b4;
  --color-subtle: #6b7380;
}
@media (prefers-reduced-motion: reduce) {
  .x { animation: none; }
}
"""


def test_regulatory_audit_no_evidence_all_unverified_or_na():
    results = run_regulatory_audit(OfflineJudge(), evidence={})
    assert len(results) == len(REGULATIONS)
    assert all(r.status == "UNVERIFIED" for r in results)
    # unverified checks must carry a remediation prompt
    assert all(r.remediation for r in results)


def test_regulatory_audit_explicit_na():
    evidence = {REGULATIONS[0]["id"]: "Not applicable — we do not train models."}
    results = run_regulatory_audit(OfflineJudge(), evidence=evidence)
    assert results[0].status == "NOT_APPLICABLE"
    assert all(r.status == "UNVERIFIED" for r in results[1:])


def test_token_audit_finds_contrast_failures():
    results = run_token_audit(DARK_THEME)
    pair_results = [r for r in results if r.id.startswith("DS-CONTRAST-PAIR")]
    assert pair_results, "expected per-pair results"
    # --color-subtle #6b7380 on #0c0c0e is ~3.3:1 -> must FAIL
    subtle = [r for r in pair_results if r.id.startswith("DS-CONTRAST-PAIR::color-subtle")]
    assert subtle and all(r.status == "FAIL" for r in subtle)
    # --color-fg #eeeee8 on dark surfaces should pass
    fg = [r for r in pair_results if r.id.startswith("DS-CONTRAST-PAIR::color-fg")]
    assert fg and all(r.status == "PASS" for r in fg)
    summary = [r for r in results if r.id == "DS-CONTRAST-01"][0]
    assert summary.status == "FAIL"


def test_token_audit_reduced_motion_detected():
    results = run_token_audit(DARK_THEME)
    motion = [r for r in results if r.id == "DS-MOTION-01"][0]
    assert motion.status == "PASS"


def test_token_audit_broken_reduced_motion_warns():
    broken = DARK_THEME.replace("animation: none;", "animation: none! important; important;")
    results = run_token_audit(broken)
    motion = [r for r in results if r.id == "DS-MOTION-01"][0]
    assert motion.status == "WARN"


def test_token_audit_empty_css_fails():
    results = run_token_audit("")
    assert results[0].status == "FAIL"


def test_score_unverified_counts_against_readiness():
    results = [
        CheckResult("1", "c", "t", "PASS", "info", "d", "e"),
        CheckResult("2", "c", "t", "UNVERIFIED", "high", "d", "e"),
        CheckResult("3", "c", "t", "NOT_APPLICABLE", "info", "d", "e"),
    ]
    s = score(results)
    assert s["applicable"] == 2  # N/A excluded
    assert s["readiness"] == 0.5


def test_score_all_na_is_zero_not_perfect():
    results = [CheckResult("1", "c", "t", "NOT_APPLICABLE", "info", "d", "e")]
    assert score(results)["readiness"] == 0.0


def test_result_serialization_roundtrip():
    r = CheckResult("x", "cat", "title", "PASS", "low", "detail", "eval")
    d = r.to_dict()
    assert d["id"] == "x" and d["evaluator"] == "eval"
    CheckResult(**d)  # must reconstruct without error
