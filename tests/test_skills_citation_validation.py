"""Tests for the citation validation skill."""

import pytest

from researcher_support_agent.models.citation import Bibliography
from researcher_support_agent.models.manuscript import (
    Manuscript,
    ManuscriptTemplate,
)
from researcher_support_agent.skills.citation_validation_skill import (
    CitationValidationSkill,
    validate_author_names,
    validate_doi,
    validate_publication_year,
)


class TestCitationValidationSkill:
    @pytest.fixture()
    def skill(self):
        return CitationValidationSkill()

    @pytest.fixture()
    def good_manuscript(self):
        m = Manuscript.from_template("Test", ManuscriptTemplate.NARRATIVE_REVIEW)
        m.set_section_content("abstract", "Content.", citations=["paper-1"])
        m.add_reference("paper-1")
        return m

    def test_validate_all_no_issues(self, skill, good_manuscript):
        known_ids = {"paper-1"}
        issues = skill.validate_all(good_manuscript, known_ids)
        assert issues == []

    def test_validate_citation_resolution(self, skill, good_manuscript):
        known_ids = {"known-paper"}  # paper-1 is not known
        issues = skill._validate_citation_resolution(good_manuscript, known_ids)
        assert len(issues) > 0
        assert "Unresolved" in issues[0]

    def test_validate_no_fabrication(self, skill, good_manuscript):
        known_ids = {"known-paper"}  # paper-1 not in known_ids
        issues = skill._validate_no_fabrication(good_manuscript, known_ids)
        assert len(issues) > 0
        assert "fabrication" in issues[0].lower()

    def test_validate_no_duplicates(self, skill, good_manuscript):
        # Add duplicate reference
        good_manuscript.reference_ids.append("paper-1")  # already has one
        issues = skill._validate_no_duplicates(good_manuscript)
        assert len(issues) > 0
        assert "Duplicate" in issues[0]

    def test_validate_citation_consistency(self, skill, good_manuscript):
        # Add a reference that's not cited
        good_manuscript.add_reference("paper-2")
        known_ids = {"paper-1", "paper-2"}
        issues = skill._validate_citation_consistency(good_manuscript, known_ids)
        assert any("not cited" in i.lower() for i in issues)

    def test_validate_bibliography_duplicates(self, skill):
        Bibliography()
        type("FakeRecord", (), {"paper_id": "p1", "id": "r1"})()
        # Add a duplicate by directly appending (simulating bad state)
        skill.bibliography.references.append(
            type(
                "FakeRecord",
                (),
                {"paper_id": "p1", "id": "r1", "title": "A", "authors": []},
            )()
        )
        skill.bibliography.references.append(
            type(
                "FakeRecord",
                (),
                {"paper_id": "p1", "id": "r2", "title": "B", "authors": []},
            )()
        )
        issues = skill._validate_bibliography_integrity(Manuscript(title="Test"))
        assert any("duplicate" in i for i in issues)


class TestValidateAuthorNames:
    def test_valid_names(self):
        issues = validate_author_names(["Alice Smith", "Bob Jones"])
        assert issues == []

    def test_empty_name(self):
        issues = validate_author_names(["Alice", "", "Bob"])
        assert len(issues) > 0
        assert "empty" in issues[0].lower()

    def test_short_name(self):
        issues = validate_author_names(["Alice", "X", "Bob"])
        assert len(issues) > 0
        assert "too short" in issues[0].lower()


class TestValidateDOI:
    def test_none_doi(self):
        result = validate_doi(None)
        assert result is None

    def test_invalid_doi_format(self):
        result = validate_doi("not-a-doi")
        assert result is not None
        assert result.resolved is False
        assert "Invalid" in result.error

    def test_valid_format(self):
        result = validate_doi("10.1234/test-paper")
        assert result is not None
        assert result.doi == "10.1234/test-paper"
        # Resolved is False because we don't actually call the API
        assert result.resolved is False


class TestValidatePublicationYear:
    def test_valid_year(self):
        issues = validate_publication_year(2023)
        assert issues == []

    def test_future_year(self):
        issues = validate_publication_year(2030)
        assert len(issues) > 0
        assert "future" in issues[0].lower()

    def test_early_year(self):
        issues = validate_publication_year(1700)
        assert len(issues) > 0
        assert "implausibly" in issues[0].lower()

    def test_none_year(self):
        issues = validate_publication_year(None)
        assert issues == []
