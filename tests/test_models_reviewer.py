"""Tests for academic reviewer models."""

import pytest

from researcher_support_agent.models.reviewer import (
    ReviewCriteria,
    ReviewPass,
    ReviewReport,
    Severity,
)
from researcher_support_agent.models.reviewer import (
    ReviewFinding as AcademicReviewFinding,
)


class TestReviewFinding:
    def test_minimal(self):
        f = AcademicReviewFinding(
            pass_name=ReviewPass.STRUCTURE,
            location="introduction",
            severity=Severity.MINOR,
            title="Short introduction",
            rationale="The introduction is too brief.",
        )
        assert f.pass_name == ReviewPass.STRUCTURE
        assert f.location == "introduction"
        assert f.severity == Severity.MINOR
        assert f.resolved is False
        assert f.resolution_note is None

    def test_mark_resolved(self):
        f = AcademicReviewFinding(
            pass_name=ReviewPass.STRUCTURE,
            location="intro",
            severity=Severity.MINOR,
            title="Issue",
            rationale="Rationale.",
        )
        f.mark_resolved("Fixed the issue")
        assert f.resolved is True
        assert f.resolution_note == "Fixed the issue"

    def test_sorting_by_severity(self):
        critical = AcademicReviewFinding(
            pass_name=ReviewPass.EVIDENCE,
            location="results",
            severity=Severity.CRITICAL,
            title="Critical",
            rationale="Critical issue",
        )
        minor = AcademicReviewFinding(
            pass_name=ReviewPass.EVIDENCE,
            location="results",
            severity=Severity.MINOR,
            title="Minor",
            rationale="Minor issue",
        )
        suggestion = AcademicReviewFinding(
            pass_name=ReviewPass.EVIDENCE,
            location="results",
            severity=Severity.SUGGESTION,
            title="Suggestion",
            rationale="Suggestion",
        )

        findings = [suggestion, critical, minor]
        findings.sort()
        assert findings[0] == critical
        assert findings[1] == minor
        assert findings[2] == suggestion


class TestReviewReport:
    def test_minimal(self):
        r = ReviewReport(title="Test Manuscript")
        assert r.title == "Test Manuscript"
        assert r.findings == []

    def test_add_finding(self):
        r = ReviewReport(title="Test")
        f = AcademicReviewFinding(
            pass_name=ReviewPass.STRUCTURE,
            location="intro",
            severity=Severity.MINOR,
            title="Short intro",
            rationale="Too brief.",
        )
        r.add_finding(f)
        assert len(r.findings) == 1
        assert r.findings[0] == f

    def test_get_unresolved(self):
        r = ReviewReport(title="Test")
        f1 = AcademicReviewFinding(
            pass_name=ReviewPass.STRUCTURE,
            location="intro",
            severity=Severity.MINOR,
            title="Issue 1",
            rationale="Rationale.",
        )
        f2 = AcademicReviewFinding(
            pass_name=ReviewPass.STRUCTURE,
            location="methods",
            severity=Severity.MINOR,
            title="Issue 2",
            rationale="Rationale.",
        )
        r.add_finding(f1)
        r.add_finding(f2)
        f2.mark_resolved("Fixed")
        unresolved = r.get_unresolved()
        assert len(unresolved) == 1
        assert unresolved[0].title == "Issue 1"

    def test_get_critical_findings(self):
        r = ReviewReport(title="Test")
        critical = AcademicReviewFinding(
            pass_name=ReviewPass.EVIDENCE,
            location="results",
            severity=Severity.CRITICAL,
            title="Critical",
            rationale="Critical issue",
        )
        minor = AcademicReviewFinding(
            pass_name=ReviewPass.STRUCTURE,
            location="intro",
            severity=Severity.MINOR,
            title="Minor",
            rationale="Minor issue",
        )
        r.add_finding(critical)
        r.add_finding(minor)
        critical_findings = r.get_critical_findings()
        assert len(critical_findings) == 1
        assert critical_findings[0].title == "Critical"

    def test_get_findings_by_pass(self):
        r = ReviewReport(title="Test")
        structure_f = AcademicReviewFinding(
            pass_name=ReviewPass.STRUCTURE,
            location="intro",
            severity=Severity.MINOR,
            title="Structure issue",
            rationale="Rationale.",
        )
        evidence_f = AcademicReviewFinding(
            pass_name=ReviewPass.EVIDENCE,
            location="results",
            severity=Severity.MAJOR,
            title="Evidence issue",
            rationale="Rationale.",
        )
        r.add_finding(structure_f)
        r.add_finding(evidence_f)

        structure_findings = r.get_findings_by_pass(ReviewPass.STRUCTURE)
        assert len(structure_findings) == 1
        assert structure_findings[0].title == "Structure issue"

    def test_to_markdown(self):
        r = ReviewReport(title="Test Manuscript")
        f = AcademicReviewFinding(
            pass_name=ReviewPass.STRUCTURE,
            location="intro",
            severity=Severity.MINOR,
            title="Short intro",
            rationale="Too brief.",
            suggested_correction="Expand the introduction.",
        )
        r.add_finding(f)
        md = r.to_markdown()
        assert "# Review Report: Test Manuscript" in md
        assert "## Structure Review" in md
        assert "MINOR: Short intro" in md
        assert "Expand the introduction" in md

    def test_mark_all_resolved(self):
        r = ReviewReport(title="Test")
        f1 = AcademicReviewFinding(
            pass_name=ReviewPass.STRUCTURE,
            location="intro",
            severity=Severity.MINOR,
            title="Issue 1",
            rationale="Rationale.",
        )
        f2 = AcademicReviewFinding(
            pass_name=ReviewPass.STRUCTURE,
            location="methods",
            severity=Severity.MINOR,
            title="Issue 2",
            rationale="Rationale.",
        )
        r.add_finding(f1)
        r.add_finding(f2)
        count = r.mark_all_resolved()
        assert count == 2
        assert all(f.resolved for f in r.findings)


class TestReviewCriteria:
    def test_default_criteria(self):
        c = ReviewCriteria()
        assert c.max_severity_to_accept == Severity.MINOR
        assert c.max_iterations == 5
        assert c.require_all_critical_resolved is True
        assert c.require_all_major_resolved is False

    def test_would_pass_no_findings(self):
        c = ReviewCriteria()
        r = ReviewReport(title="Test")
        assert c.would_pass(r) is True

    def test_would_pass_with_suggestions_only(self):
        c = ReviewCriteria()
        r = ReviewReport(title="Test")
        f = AcademicReviewFinding(
            pass_name=ReviewPass.STRUCTURE,
            location="intro",
            severity=Severity.SUGGESTION,
            title="Suggestion",
            rationale="Rationale.",
        )
        r.add_finding(f)
        assert c.would_pass(r) is True  # Suggestions are acceptable

    def test_would_fail_with_unresolved_critical(self):
        c = ReviewCriteria()
        r = ReviewReport(title="Test")
        f = AcademicReviewFinding(
            pass_name=ReviewPass.EVIDENCE,
            location="results",
            severity=Severity.CRITICAL,
            title="Critical",
            rationale="Critical issue.",
        )
        r.add_finding(f)
        assert c.would_pass(r) is False

    def test_requires_human_approval_for_critical(self):
        c = ReviewCriteria()
        r = ReviewReport(title="Test")
        f = AcademicReviewFinding(
            pass_name=ReviewPass.EVIDENCE,
            location="results",
            severity=Severity.CRITICAL,
            title="Critical",
            rationale="Critical issue.",
        )
        r.add_finding(f)
        assert c.requires_human_approval(r) is True

    def test_no_human_approval_for_suggestions(self):
        c = ReviewCriteria()
        r = ReviewReport(title="Test")
        f = AcademicReviewFinding(
            pass_name=ReviewPass.STRUCTURE,
            location="intro",
            severity=Severity.SUGGESTION,
            title="Suggestion",
            rationale="Rationale.",
        )
        r.add_finding(f)
        assert c.requires_human_approval(r) is False

    def test_max_iterations_range(self):
        with pytest.raises(ValueError):  # Pydantic validation
            ReviewCriteria(max_iterations=0)

        with pytest.raises(ValueError):
            ReviewCriteria(max_iterations=51)
