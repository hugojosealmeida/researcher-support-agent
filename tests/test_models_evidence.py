<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
"""Tests for evidence and review models."""

import pytest

from researcher_support_agent.models import Evidence, ReviewFinding


class TestEvidence:
    def test_valid_creation(self):
        e = Evidence(claim="X causes Y", strength="strong")
        assert e.claim == "X causes Y"

    def test_empty_claim_raises(self):
        with pytest.raises(ValueError):
            Evidence(claim="")

    def test_with_supporting_papers(self):
        e = Evidence(claim="Test", supporting_paper_ids=["p1", "p2"])
        assert e.supporting_paper_ids == ["p1", "p2"]

    def test_confidence_bounds(self):
        e = Evidence(claim="T", confidence=0.9)
        assert e.confidence == 0.9

    def test_confidence_bounds_error(self):
        with pytest.raises(ValueError):
            Evidence(claim="T", confidence=1.5)


class TestReviewFinding:
    def test_valid_creation(self):
        f = ReviewFinding(
            category="abstract",
            severity="minor",
            description="Typo found",
        )
        assert f.category == "abstract"
        assert f.severity == "minor"

    def test_valid_severities(self):
        for sev in ("critical", "major", "minor", "suggestion"):
            f = ReviewFinding(category="test", severity=sev, description="d")
            assert f.severity == sev

    def test_invalid_severity_raises(self):
        with pytest.raises(ValueError, match="severity must be one of"):
            ReviewFinding(category="test", severity="invalid", description="d")

    def test_empty_category_raises(self):
        with pytest.raises(ValueError):
            ReviewFinding(category="", severity="minor", description="d")

    def test_resolution(self):
        f = ReviewFinding(
            category="citations",
            severity="major",
            description="Missing ref",
            resolution="Added reference",
        )
        assert f.resolution == "Added reference"
=======
=======
>>>>>>> 1123db3 (fix: Phase C — Evidence extraction and synthesis (#4))
=======
>>>>>>> 10d6757 (fix: Phase D — Manuscript production and quality control (#5))
=======
>>>>>>> 3eda405 (fix: Phase E — Reliability, Git integration and release (#6))
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
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
>>>>>>> e45cda7 (fix: Phase B — Literature discovery and ingestion (#3))
=======
>>>>>>> 1123db3 (fix: Phase C — Evidence extraction and synthesis (#4))
=======
>>>>>>> 10d6757 (fix: Phase D — Manuscript production and quality control (#5))
=======
>>>>>>> 3eda405 (fix: Phase E — Reliability, Git integration and release (#6))
