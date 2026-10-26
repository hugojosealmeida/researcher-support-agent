"""Tests for screening model."""


from researcher_support_agent.models.screening import ScreeningDecision, ScreeningResult


class TestScreeningDecision:
    def test_values(self):
        assert ScreeningDecision.INCLUDE == "include"
        assert ScreeningDecision.EXCLUDE == "exclude"
        assert ScreeningDecision.MAYBE == "maybe"


class TestScreeningResult:
    def test_minimal(self):
        r = ScreeningResult(
            paper_id="paper-1",
            decision=ScreeningDecision.INCLUDE,
        )
        assert r.paper_id == "paper-1"
        assert r.decision == ScreeningDecision.INCLUDE
        assert r.reason == ""

    def test_with_reason(self):
        r = ScreeningResult(
            paper_id="paper-1",
            decision=ScreeningDecision.EXCLUDE,
            reason="Out of scope",
        )
        assert r.reason == "Out of scope"
