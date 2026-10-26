"""Tests for evidence model."""

import pytest

from researcher_support_agent.models.evidence import Evidence, ReviewFinding


class TestEvidence:
    def test_minimal(self):
        e = Evidence(claim="Test claim")
        assert e.supporting_paper_ids == []
        assert e.strength == "weak"
        assert e.confidence == 0.0

    def test_full(self):
        e = Evidence(
            claim="X improves Y",
            supporting_paper_ids=["p1", "p2", "p3"],
            strength="strong",
            confidence=0.95,
        )
        assert len(e.supporting_paper_ids) == 3
        assert e.confidence == 0.95

    def test_validation_confidence_range(self):
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            Evidence(claim="test", confidence=-0.1)

        with pytest.raises(ValidationError):
            Evidence(claim="test", confidence=1.1)


class TestReviewFinding:
    def test_minimal(self):
        f = ReviewFinding(category="bias", severity="medium", description="Selection bias")
        assert f.category == "bias"
        assert f.resolution is None
