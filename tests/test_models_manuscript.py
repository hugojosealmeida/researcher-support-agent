"""Tests for manuscript model with section templates and citation tracking."""

import pytest

from researcher_support_agent.models.manuscript import (
    Manuscript,
    ManuscriptSection,
    ManuscriptTemplate,
    SectionTemplate,
)


class TestSectionTemplate:
    def test_minimal(self):
        s = SectionTemplate(name="intro", purpose="Frame the question")
        assert s.name == "intro"
        assert s.purpose == "Frame the question"

    def test_validation(self):
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            SectionTemplate(name="", purpose="test")

        with pytest.raises(ValidationError):
            SectionTemplate(name="test", purpose="")


class TestManuscriptSection:
    def test_minimal(self):
        s = ManuscriptSection(name="abstract", purpose="Summarize")
        assert s.name == "abstract"
        assert s.purpose == "Summarize"
        assert s.content == ""
        assert s.citations_used == []

    def test_mark_completed(self):
        from researcher_support_agent.models.common import Status

        s = ManuscriptSection(name="intro", purpose="Frame")
        assert s.status == Status.PENDING
        s.mark_completed()
        assert s.status == Status.COMPLETED
        assert s.completed_at is not None


class TestManuscriptTemplate:
    def test_narrative_review_sections(self):
        sections = ManuscriptTemplate.NARRATIVE_REVIEW.get_sections()
        assert len(sections) == 6
        names = [s.name for s in sections]
        assert "abstract" in names
        assert "introduction" in names
        assert "methods" in names
        assert "results" in names
        assert "discussion" in names
        assert "conclusion" in names

    def test_systematic_review_sections(self):
        sections = ManuscriptTemplate.SYSTEMATIC_REVIEW.get_sections()
        assert len(sections) == 6
        for s in sections:
            assert s.purpose  # Every section has a purpose

    def test_scoping_review_sections(self):
        sections = ManuscriptTemplate.SCOPING_REVIEW.get_sections()
        assert len(sections) == 6

    def test_discipline_specific_sections(self):
        sections = ManuscriptTemplate.DISCIPLINE_SPECIFIC.get_sections()
        assert len(sections) == 6

    def test_all_sections_have_purpose(self):
        for template in ManuscriptTemplate:
            sections = template.get_sections()
            for section in sections:
                assert section.purpose and len(section.purpose) > 0


class TestManuscript:
    def test_minimal(self):
        m = Manuscript(title="Test Manuscript")
        assert m.title == "Test Manuscript"
        assert m.sections == {}
        assert m.version == 1
        assert m.reference_ids == []

    def test_from_template(self):
        m = Manuscript.from_template("Test Review", ManuscriptTemplate.NARRATIVE_REVIEW)
        assert m.template == ManuscriptTemplate.NARRATIVE_REVIEW
        assert len(m.sections) == 6
        assert "abstract" in m.sections
        assert m.sections["abstract"].purpose  # Has purpose

    def test_add_section(self):
        m = Manuscript(title="Test")
        section = m.add_section("supplement", "Additional info")
        assert "supplement" in m.sections
        assert section.name == "supplement"

    def test_set_section_content(self):
        m = Manuscript.from_template("Test", ManuscriptTemplate.NARRATIVE_REVIEW)
        m.set_section_content(
            "abstract",
            "This is the abstract content.",
            citations=["paper-1", "paper-2"],
        )
        assert m.sections["abstract"].content == "This is the abstract content."
        assert "paper-1" in m.sections["abstract"].citations_used
        assert "paper-2" in m.sections["abstract"].citations_used

    def test_set_section_content_invalid_section(self):
        m = Manuscript(title="Test")
        with pytest.raises(KeyError):
            m.set_section_content("nonexistent", "content")

    def test_add_reference_deduplicates(self):
        m = Manuscript(title="Test")
        m.add_reference("paper-1")
        m.add_reference("paper-2")
        m.add_reference("paper-1")  # Duplicate
        assert len(m.reference_ids) == 2

    def test_validate_citations(self):
        m = Manuscript.from_template("Test", ManuscriptTemplate.NARRATIVE_REVIEW)
        m.set_section_content("abstract", "Content.", citations=["known-1", "unknown-1"])
        m.add_reference("known-2")
        m.add_reference("unknown-2")

        known = {"known-1", "known-2"}
        unresolved = m.validate_citations(known)
        assert "unknown-1" in unresolved
        assert "unknown-2" in unresolved
        assert "known-1" not in unresolved
        assert "known-2" not in unresolved

    def test_validate_all_citations_valid(self):
        m = Manuscript.from_template("Test", ManuscriptTemplate.NARRATIVE_REVIEW)
        m.set_section_content("abstract", "Content.", citations=["p1"])
        known = {"p1"}
        unresolved = m.validate_citations(known)
        assert unresolved == []

    def test_get_cited_paper_ids(self):
        m = Manuscript.from_template("Test", ManuscriptTemplate.NARRATIVE_REVIEW)
        m.set_section_content("abstract", "Content.", citations=["p1", "p2"])
        m.add_reference("p3")
        m.add_reference("p1")  # duplicate in references
        cited = m.get_cited_paper_ids()
        # Only section citations are returned, not uncited references
        assert sorted(cited) == ["p1", "p2"]

    def test_bump_version(self):
        m = Manuscript(title="Test")
        v1 = m.version
        m.bump_version()
        assert m.version == v1 + 1

    def test_to_markdown(self):
        m = Manuscript.from_template("My Review", ManuscriptTemplate.NARRATIVE_REVIEW)
        m.set_section_content("abstract", "This is the abstract.", citations=["p1"])
        md = m.to_markdown()
        assert "# My Review" in md
        assert "## Abstract" in md
        assert "This is the abstract." in md

    def test_has_uncited_bibliography(self):
        m = Manuscript.from_template("Test", ManuscriptTemplate.NARRATIVE_REVIEW)
        m.add_reference("p1")
        assert m.has_uncited_bibliography() is True
        # Now cite p1
        m.set_section_content("abstract", "Content.", citations=["p1"])
        assert m.has_uncited_bibliography() is False
