"""Tests for judge routing: honesty guarantees and OpenAI fallback behavior."""

import pytest

from us_ai_audit_suite_2026.judge import (
    OfflineJudge,
    OpenAIJudge,
    Verdict,
    get_judge,
)

CHECK = {
    "id": "X-1",
    "law": "Test Law",
    "jurisdiction": "Test",
    "effective": "2026-01-01",
    "requirement": "Must disclose AI interaction to users.",
    "evidence_prompt": "Show the disclosure.",
}


# ---------- Verdict validation ----------

def test_verdict_rejects_bad_status():
    with pytest.raises(ValueError):
        Verdict(status="KINDA_OK", rationale="r", evaluator="e")


def test_verdict_rejects_bad_confidence():
    with pytest.raises(ValueError):
        Verdict(status="PASS", rationale="r", evaluator="e", confidence=1.5)


# ---------- Offline judge honesty ----------

def test_offline_judge_never_passes():
    judge = OfflineJudge()
    # Even glowing evidence must not produce PASS offline.
    v = judge.evaluate(CHECK, "We have a completed disclosure policy, published "
                             "documentation, an audit report at https://x.test, "
                             "and a review process owned by compliance.")
    assert v.status in ("WARN", "UNVERIFIED", "NOT_APPLICABLE")
    assert v.evaluator == "offline-deterministic"


def test_offline_judge_empty_evidence_unverified():
    assert OfflineJudge().evaluate(CHECK, "").status == "UNVERIFIED"
    assert OfflineJudge().evaluate(CHECK, None).status == "UNVERIFIED"


def test_offline_judge_explicit_failure_fails():
    v = OfflineJudge().evaluate(CHECK, "We do not comply with this requirement.")
    assert v.status == "FAIL"


def test_offline_judge_na_detection():
    v = OfflineJudge().evaluate(CHECK, "N/A — we do not train models.")
    assert v.status == "NOT_APPLICABLE"


# ---------- OpenAI judge (mocked client) ----------

class _Parsed:
    def __init__(self, status, rationale, confidence):
        self.status = status
        self.rationale = rationale
        self.confidence = confidence


class _Rsp:
    def __init__(self, parsed):
        self.output_parsed = parsed


class _FakeResponses:
    def __init__(self, parsed=None, error=None):
        self._parsed = parsed
        self._error = error

    def parse(self, **kwargs):
        if self._error:
            raise self._error
        return _Rsp(self._parsed)


class _FakeClient:
    def __init__(self, parsed=None, error=None):
        self.responses = _FakeResponses(parsed, error)


def test_openai_judge_parses_structured_output():
    client = _FakeClient(parsed=_Parsed("pass", "Evidence directly satisfies.", 0.92))
    judge = OpenAIJudge(model="test-model", client=client)
    v = judge.evaluate(CHECK, "We show an 'AI assistant' badge on every chat screen.")
    assert v.status == "PASS"
    assert v.evaluator == "openai:test-model"
    assert v.confidence == 0.92


def test_openai_judge_invalid_status_coerced_to_unverified():
    client = _FakeClient(parsed=_Parsed("LOOKS_GOOD", "nonsense status", 0.5))
    v = OpenAIJudge(client=client).evaluate(CHECK, "some evidence text")
    assert v.status == "UNVERIFIED"


def test_openai_judge_clamps_confidence():
    client = _FakeClient(parsed=_Parsed("warn", "partial", 42.0))
    v = OpenAIJudge(client=client).evaluate(CHECK, "some evidence text")
    assert v.confidence == 1.0


def test_openai_judge_empty_evidence_short_circuits_api():
    client = _FakeClient(error=AssertionError("API must not be called"))
    v = OpenAIJudge(client=client).evaluate(CHECK, "   ")
    assert v.status == "UNVERIFIED"


# ---------- Routing ----------

def test_get_judge_offline_without_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    judge, note = get_judge()
    assert judge.name == "offline-deterministic"
    assert note and "NOT LLM-verified" in note


def test_get_judge_no_openai_flag(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-fake")
    judge, note = get_judge(prefer_openai=False)
    assert judge.name == "offline-deterministic"
    assert note is None
