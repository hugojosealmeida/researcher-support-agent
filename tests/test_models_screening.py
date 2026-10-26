"""Tests for screening models."""


import pytest

from researcher_support_agent.models.screening import ScreeningDecision, ScreeningResult


class TestScreeningDecision:
    def test_values(self):
        assert ScreeningDecision.ACCEPT.value == "accept"
        assert ScreeningDecision.EXCLUDE.value == "exclude"
        assert ScreeningDecision.BORDERLINE.value == "borderline"


class TestScreeningResult:
    def test_minimal(self):
        r = ScreeningResult(
            paper_id="p1",
            decision=ScreeningDecision.ACCEPT,
            reason="Matches criteria",
        )
        assert r.paper_id == "p1"
        assert r.decision == ScreeningDecision.ACCEPT
        assert r.reason == "Matches criteria"
        assert r.uncertainty == 0.0
        assert r.criteria_matched == []
        assert r.flagged_for_review is False
        assert r.screened_at is not None
        assert r.source == "automated"

    def test_borderline(self):
        r = ScreeningResult(
            paper_id="p1",
            decision=ScreeningDecision.BORDERLINE,
            reason="Unclear fit",
            flagged_for_review=True,
        )
        assert r.flagged_for_review is True

    def test_validation_uncertainty_range(self):
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            ScreeningResult(
                paper_id="p1",
                decision=ScreeningDecision.ACCEPT,
                reason="test",
                uncertainty=-0.1,
            )

        with pytest.raises(ValidationError):
            ScreeningResult(
                paper_id="p1",
                decision=ScreeningDecision.ACCEPT,
                reason="test",
                uncertainty=1.1,
            )

    def test_serialization(self):
        r = ScreeningResult(
            paper_id="p1",
            decision=ScreeningDecision.EXCLUDE,
            reason="Wrong topic",
            uncertainty=0.9,
            criteria_matched=["not relevant"],
        )
        data = r.model_dump()
        assert data["paper_id"] == "p1"
        assert data["decision"] == "exclude"
        assert data["flagged_for_review"] is False

    def test_roundtrip(self):
        r = ScreeningResult(
            paper_id="p1",
            decision=ScreeningDecision.BORDERLINE,
            reason="Need human review",
            uncertainty=0.5,
            flagged_for_review=True,
            source="human",
        )
        data = r.model_dump()
        r2 = ScreeningResult(**data)
        assert r2.paper_id == r.paper_id
        assert r2.decision == r.decision
        assert r2.flagged_for_review is True
