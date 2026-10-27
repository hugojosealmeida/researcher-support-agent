"""Tests for the bibliography skill."""

import pytest

from researcher_support_agent.models.citation import ReferenceFormat
from researcher_support_agent.models.manuscript import (
    Manuscript,
    ManuscriptTemplate,
)
from researcher_support_agent.skills.bibliography_skill import BibliographySkill


class TestBibliographySkill:
    @pytest.fixture()
    def skill(self):
        return BibliographySkill()

    def test_add_reference(self, skill):
        ref = skill.add_reference(
            paper_id="paper-1",
            title="Attention Is All You Need",
            authors=["Alice Vaswani", "Bob Shazeer"],
            year=2017,
            journal="NeurIPS",
        )
        assert ref.paper_id == "paper-1"
        assert ref.title == "Attention Is All You Need"

    def test_get_reference(self, skill):
        skill.add_reference(
            paper_id="paper-1",
            title="Test Paper",
            authors=["Alice"],
        )
        found = skill.get_reference("paper-1")
        assert found is not None
        assert found.title == "Test Paper"

    def test_get_nonexistent(self, skill):
        assert skill.get_reference("nonexistent") is None

    def test_export_bibtex(self, skill):
        skill.add_reference(
            paper_id="paper-1",
            title="Test Paper",
            authors=["Alice Smith"],
            year=2023,
            journal="Test Journal",
        )
        bibtex = skill.export(ReferenceFormat.BIBTEX)
        assert "@article" in bibtex
        assert "Test Paper" in bibtex

    def test_export_csl_json(self, skill):
        skill.add_reference(
            paper_id="paper-1",
            title="Test Paper",
            authors=["Alice Smith"],
            year=2023,
        )
        csl = skill.export_csl_json()
        assert len(csl) == 1
        assert csl[0]["title"] == "Test Paper"

    def test_validate_against_manuscript_no_issues(self, skill):
        # Add a reference that matches what the manuscript cites
        skill.add_reference(
            paper_id="paper-1",
            title="Test Paper",
            authors=["Alice"],
        )

        m = Manuscript.from_template("Test", ManuscriptTemplate.NARRATIVE_REVIEW)
        m.set_section_content("abstract", "Content.", citations=["paper-1"])
        m.add_reference("paper-1")

        known_ids = {"paper-1"}
        issues = skill.validate_against_manuscript(m, known_ids)
        assert issues == []

    def test_validate_against_manuscript_missing_record(self, skill):
        m = Manuscript.from_template("Test", ManuscriptTemplate.NARRATIVE_REVIEW)
        m.set_section_content("abstract", "Content.", citations=["paper-1"])
        m.add_reference("paper-1")

        known_ids = {"paper-1"}
        # No reference record added for paper-1
        issues = skill.validate_against_manuscript(m, known_ids)
        assert len(issues) > 0
        assert "reference record" in issues[0].lower()

    def test_validate_against_manuscript_fabricated(self, skill):
        skill.add_reference(
            paper_id="fabricated",
            title="Fake Paper",
            authors=["Alice"],
        )

        m = Manuscript.from_template("Test", ManuscriptTemplate.NARRATIVE_REVIEW)
        m.add_reference("fabricated")

        known_ids = {"known-paper"}  # fabricated is NOT in known_ids
        issues = skill.validate_against_manuscript(m, known_ids)
        assert len(issues) > 0
        assert "fabricated" in issues[0].lower()
