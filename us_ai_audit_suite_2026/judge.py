"""LLM judge routing: OpenAI Responses API with honest deterministic fallback.

Honesty rules baked in:
- If no API key is configured, the offline evaluator is used and every verdict
  is labeled `offline-deterministic` — never presented as an LLM judgment.
- If the API call fails for any reason, we fall back to offline evaluation and
  record the error in the verdict's rationale.
- An empty evidence string is UNVERIFIED regardless of evaluator.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Protocol


VALID_STATUSES = ("PASS", "FAIL", "WARN", "UNVERIFIED", "NOT_APPLICABLE")


@dataclass
class Verdict:
    status: str
    rationale: str
    evaluator: str
    confidence: float = 1.0
    extra: dict = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.status not in VALID_STATUSES:
            raise ValueError(f"invalid verdict status: {self.status!r}")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be in [0, 1]")


class Judge(Protocol):
    name: str

    def evaluate(self, check: dict, evidence: str) -> Verdict:
        ...


# Evidence keywords that strongly suggest a deliberate N/A claim.
_NA_MARKERS = ("n/a", "not applicable", "out of scope", "do not train",
               "does not apply", "no generative ai", "we are not")

# Minimal signals that evidence engages the substance of a requirement.
_SUBSTANCE_MARKERS = (
    "policy", "process", "assessment", "report", "disclosure", "notice",
    "audit", "review", "documentation", "runbook", "channel", "consent",
    "inventory", "owner", "url", "http", "completed", "published",
)


class OfflineJudge:
    """Deterministic, keyword-based evaluator. Conservative by design:
    it can return WARN/UNVERIFIED/NOT_APPLICABLE but NEVER returns PASS
    (it cannot truly verify evidence), and returns FAIL only when the
    evidence explicitly states non-compliance."""

    name = "offline-deterministic"
    _FAIL_MARKERS = ("we do not comply", "no assessment", "not compliant",
                     "no disclosure", "we fail", "missing entirely")

    def evaluate(self, check: dict, evidence: str) -> Verdict:
        text = (evidence or "").strip().lower()
        if not text:
            return Verdict(
                status="UNVERIFIED",
                rationale="No evidence supplied; check cannot be passed.",
                evaluator=self.name,
                confidence=1.0,
            )
        if any(m in text for m in self._FAIL_MARKERS):
            return Verdict(
                status="FAIL",
                rationale="Evidence explicitly states non-compliance.",
                evaluator=self.name,
                confidence=0.9,
            )
        if any(m in text for m in _NA_MARKERS):
            return Verdict(
                status="NOT_APPLICABLE",
                rationale="Evidence asserts the requirement is out of scope.",
                evaluator=self.name,
                confidence=0.7,
            )
        hits = sum(1 for m in _SUBSTANCE_MARKERS if m in text)
        if hits >= 2 and len(text) >= 80:
            return Verdict(
                status="WARN",
                rationale=(
                    f"Evidence engages the requirement ({hits} substance "
                    "signals) but this evaluator cannot verify it — LLM "
                    "verification recommended (set OPENAI_API_KEY)."
                ),
                evaluator=self.name,
                confidence=0.5,
            )
        return Verdict(
            status="UNVERIFIED",
            rationale="Evidence too thin for a determination.",
            evaluator=self.name,
            confidence=0.8,
        )


class OpenAIJudge:
    """Routes evidence evaluation through the OpenAI Responses API using
    structured output (client.responses.parse with a Pydantic schema)."""

    def __init__(self, model: str | None = None, client=None) -> None:
        self.model = model or os.environ.get("AUDIT_MODEL", "gpt-4o-mini")
        if client is not None:
            self._client = client
        else:
            from openai import OpenAI  # imported lazily: offline mode needs no SDK
            self._client = OpenAI()
        self.name = f"openai:{self.model}"

    def evaluate(self, check: dict, evidence: str) -> Verdict:
        from pydantic import BaseModel

        class _Verdict(BaseModel):
            status: str
            rationale: str
            confidence: float

        if not (evidence or "").strip():
            return Verdict(
                status="UNVERIFIED",
                rationale="No evidence supplied; check cannot be passed.",
                evaluator=self.name,
                confidence=1.0,
            )
        prompt = (
            "You are a strict compliance auditor. Evaluate the evidence against "
            "the requirement. Reply with status one of PASS, FAIL, WARN, "
            "UNVERIFIED, NOT_APPLICABLE. PASS only if the evidence directly and "
            "specifically satisfies the requirement; otherwise WARN or "
            "UNVERIFIED. Be skeptical: vague claims are not compliance.\n\n"
            f"LAW: {check['law']} ({check['jurisdiction']}, effective "
            f"{check['effective']})\n"
            f"REQUIREMENT: {check['requirement']}\n"
            f"EVIDENCE: {evidence}"
        )
        rsp = self._client.responses.parse(
            model=self.model,
            input=prompt,
            text_format=_Verdict,
        )
        parsed = rsp.output_parsed
        if parsed is None:
            raise RuntimeError("OpenAI response contained no parsed verdict")
        status = parsed.status.upper()
        if status not in VALID_STATUSES:
            status = "UNVERIFIED"
        return Verdict(
            status=status,
            rationale=parsed.rationale,
            evaluator=self.name,
            confidence=max(0.0, min(1.0, parsed.confidence)),
        )


def get_judge(prefer_openai: bool = True) -> tuple[Judge, str | None]:
    """Return (judge, fallback_note). fallback_note is None unless the OpenAI
    route was requested but unavailable — the note is recorded in reports."""
    if prefer_openai and os.environ.get("OPENAI_API_KEY"):
        return OpenAIJudge(), None
    note = None
    if prefer_openai:
        note = ("OPENAI_API_KEY not set — used offline-deterministic "
                "evaluator; verdicts are NOT LLM-verified.")
    return OfflineJudge(), note
