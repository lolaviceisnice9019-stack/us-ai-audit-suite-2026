# US AI Audit Suite 2026

A mean, lean audit suite for AI product / design-system governance, focused on
**United States AI regulation as of 2026**. Built to be tough-tested and honest:
it never auto-passes a check it cannot verify, and it labels every verdict with
the evaluator that produced it.

## What it audits

1. **Regulatory readiness** — a catalog of US AI obligations in force or
   landing in 2026 (Colorado AI Act, Texas TRAIGA, California SB 53 / AB 2013 /
   SB 942, Utah AI Policy Act, NYC Local Law 144, Illinois AIVIA, federal
   EO 14365 + the March 2026 National Policy Framework, TAKE IT DOWN Act,
   FTC Act §5, NIST AI RMF). Each check names the law, the effective date, and
   the evidence required.
2. **Design-token accessibility** — parses CSS custom properties from your
   design system and computes real WCAG 2.x contrast ratios for every
   foreground/background pairing. No vibes: actual luminance math.
3. **Reduced-motion / prefer-reduced-motion support** — checks that animation
   tokens respect user motion preferences.

## Honesty contract

- `PASS` / `FAIL` are only emitted from verifiable evidence or deterministic
  computation.
- Missing evidence produces `UNVERIFIED`, never a silent pass.
- `NOT_APPLICABLE` requires a stated reason.
- Every result records which evaluator ran: `openai:<model>` or
  `offline-deterministic` (clearly not LLM-verified).

## OpenAI API routing

Evidence evaluation routes through the OpenAI **Responses API**
(`client.responses.parse` with a Pydantic verdict schema) when
`OPENAI_API_KEY` is set:

```bash
export OPENAI_API_KEY=sk-...
export AUDIT_MODEL=gpt-4o-mini   # optional, default shown
```

Without a key, the suite falls back to a deterministic offline evaluator and
says so in the report. Any API error also falls back and is recorded — the
suite never fabricates an LLM verdict.

## Usage

```bash
python -m us_ai_audit_suite_2026.cli \
  --tokens path/to/theme.css \
  --evidence evidence.json \
  --out audit_out/
```

`evidence.json` is optional; it maps check IDs to free-text evidence, e.g.:

```json
{
  "CO-AIA-01": "Impact assessment completed 2026-03-15 for the recommendation engine...",
  "CA-SB53-02": "We are not a frontier developer; no model training above 1e26 FLOPs."
}
```

Outputs: `audit_results.json` (machine-readable) and `audit_results.md`
(human-readable).

## Tests

```bash
python -m pytest tests/ -q
```

The suite is tested against itself: contrast math against known WCAG values,
parser edge cases, judge fallback behavior with a mocked OpenAI client, and
scoring integrity (UNVERIFIED must count against readiness).
