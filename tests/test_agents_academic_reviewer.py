"""Tests for the academic reviewer agent."""

import pytest

from researcher_support_agent.agents.academic_reviewer import AcademicReviewer
from researcher_support_agent.models.manuscript import (
    Manuscript,
    ManuscriptTemplate,
)
from researcher_support_agent.models.reviewer import ReviewPass


class TestAcademicReviewer:
    @pytest.fixture()
    def reviewer(self):
        return AcademicReviewer()

    @pytest.fixture()
    def sample_manuscript(self):
        return Manuscript.from_template("Test Review", ManuscriptTemplate.NARRATIVE_REVIEW)

    @pytest.fixture()
    def good_manuscript(self):
        m = Manuscript.from_template("Test Review", ManuscriptTemplate.NARRATIVE_REVIEW)
        m.set_section_content(
            "abstract",
            "**Purpose:** This review examines X. **Methods:** Systematic search. "
            "**Results:** Key findings presented. **Conclusion:** Important implications.",
            citations=["paper-1"],
        )
        m.set_section_content(
            "introduction",
            "This review examines the current state of research on the topic.",
            citations=["paper-1"],
        )
        m.set_section_content(
            "methods",
            "A comprehensive search was conducted. Inclusion criteria were applied.",
            citations=["paper-1"],
        )
        m.set_section_content(
            "results",
            "Ten studies were included. Key findings: X improves Y.",
            citations=["paper-1", "paper-2"],
        )
        m.set_section_content(
            "discussion",
            "Findings suggest X is effective. Limitations include small sample sizes. "
            "Contributions include new synthesis.",
            citations=["paper-1", "paper-2"],
        )
        m.set_section_content(
            "conclusion",
            "X shows promise. Future research should address limitations.",
            citations=["paper-1"],
        )
        for pid in ["paper-1", "paper-2"]:
            m.add_reference(pid)
        return m

    def test_review_missing_abstract(self, reviewer, sample_manuscript):
        known_ids = {"paper-1"}
        report = reviewer.review(sample_manuscript, known_ids)
        abstract_findings = report.get_findings_by_pass(ReviewPass.ABSTRACT)
        # The abstract section exists but has no content
        assert len(abstract_findings) > 0

    def test_review_empty_abstract(self, reviewer, sample_manuscript):
        known_ids = {"paper-1"}
        report = reviewer.review(sample_manuscript, known_ids)
        abstract_findings = report.get_findings_by_pass(ReviewPass.ABSTRACT)
        assert any("Empty" in f.title or "empty" in f.title for f in abstract_findings)

    def test_review_abstract_purpose_missing(self, reviewer):
        m = Manuscript.from_template("Test", ManuscriptTemplate.NARRATIVE_REVIEW)
        m.set_section_content(
            "abstract",
            "This paper studies something important.",
            citations=["paper-1"],
        )
        m.add_reference("paper-1")
        known_ids = {"paper-1"}
        report = reviewer.review(m, known_ids)
        abstract_findings = report.get_findings_by_pass(ReviewPass.ABSTRACT)
        # Should flag missing purpose/methods/results
        titles = [f.title for f in abstract_findings]
        assert any("purpose" in t.lower() for t in titles) or any("methods" in t.lower() for t in titles)

    def test_review_structure_empty_sections(self, reviewer, sample_manuscript):
        known_ids = {"paper-1"}
        report = reviewer.review(sample_manuscript, known_ids)
        structure_findings = report.get_findings_by_pass(ReviewPass.STRUCTURE)
        # Multiple empty sections should be flagged
        assert len(structure_findings) > 0

    def test_review_evidence_unresolved_citations(self, reviewer):
        m = Manuscript.from_template("Test", ManuscriptTemplate.NARRATIVE_REVIEW)
        m.set_section_content(
            "abstract",
            "Content.",
            citations=["unknown-paper"],
        )
        m.add_reference("unknown-paper")
        known_ids = {"known-paper"}  # unknown-paper is not known
        report = reviewer.review(m, known_ids)
        evidence_findings = report.get_findings_by_pass(ReviewPass.EVIDENCE)
        assert any("Unresolved" in f.title or "unresolved" in f.title for f in evidence_findings)

    def test_review_bibliography_uncited(self, reviewer):
        m = Manuscript.from_template("Test", ManuscriptTemplate.NARRATIVE_REVIEW)
        m.set_section_content(
            "abstract",
            "Content.",
            citations=["paper-1"],
        )
        m.add_reference("paper-1")
        m.add_reference("paper-2")  # Not cited
        known_ids = {"paper-1", "paper-2"}
        report = reviewer.review(m, known_ids)
        bib_findings = report.get_findings_by_pass(ReviewPass.BIBLIOGRAPHY)
        assert any("not cited" in f.title.lower() or "Uncited" in f.title for f in bib_findings)

    def test_review_academic_quality_limitations(self, reviewer):
        m = Manuscript.from_template("Test", ManuscriptTemplate.NARRATIVE_REVIEW)
        m.set_section_content(
            "abstract",
            "Content.",
            citations=["paper-1"],
        )
        m.set_section_content(
            "discussion",
            "Findings are interesting. Future work should explore more.",
            citations=["paper-1"],
        )
        m.add_reference("paper-1")
        known_ids = {"paper-1"}
        report = reviewer.review(m, known_ids)
        quality_findings = report.get_findings_by_pass(ReviewPass.ACADEMIC_QUALITY)
        assert any("limitation" in f.title.lower() for f in quality_findings)

    def test_review_research_integrity(self, reviewer):
        m = Manuscript.from_template("Test", ManuscriptTemplate.NARRATIVE_REVIEW)
        m.set_section_content(
            "abstract",
            "Content.",
            citations=["fabricated-paper"],
        )
        m.add_reference("fabricated-paper")
        known_ids = {"known-paper"}  # fabricated-paper not known
        report = reviewer.review(m, known_ids)
        integrity_findings = report.get_findings_by_pass(ReviewPass.RESEARCH_INTEGRITY)
        assert any("fabricated" in f.title.lower() for f in integrity_findings)

    def test_review_good_manuscript(self, reviewer, good_manuscript):
        known_ids = {"paper-1", "paper-2"}
        report = reviewer.review(good_manuscript, known_ids)
        # Should have fewer findings than a bad manuscript
        report.get_unresolved()
        critical = report.get_critical_findings()
        assert len(critical) == 0  # No critical findings in a good manuscript

    def test_report_to_markdown(self, reviewer, sample_manuscript):
        known_ids = {"paper-1"}
        report = reviewer.review(sample_manuscript, known_ids)
        md = report.to_markdown()
        assert "# Review Report: Test Review" in md
        assert "**Total findings:**" in md
