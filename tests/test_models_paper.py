"""Tests for paper model."""

import pytest

from researcher_support_agent.models.paper import Author, Paper, PaperStatus


class TestAuthor:
    def test_minimal(self):
        a = Author(full_name="Alice Smith")
        assert a.full_name == "Alice Smith"
        assert a.orcid is None
        assert a.affiliation is None

    def test_with_orcid(self):
        a = Author(full_name="Alice", orcid="0000-0001-2345-6789")
        assert a.orcid == "0000-0001-2345-6789"


class TestPaper:
    def test_minimal(self):
        p = Paper(title="Test Paper")
        assert p.title == "Test Paper"
        assert p.authors == []
        assert p.retrieval_status == PaperStatus.RETRIEVED

    def test_with_authors(self):
        p = Paper(
            title="Test",
            authors=[Author(full_name="Alice"), Author(full_name="Bob")],
            year=2023,
        )
        assert len(p.authors) == 2
        assert p.year == 2023

    def test_get_identifier_doi(self):
        p = Paper(title="Test", doi="10.1234/test")
        assert p.get_identifier() == "10.1234/test"

    def test_get_identifier_pmid(self):
        p = Paper(title="Test", pmid="36000001")
        assert p.get_identifier() == "36000001"

    def test_get_identifier_arxiv(self):
        p = Paper(title="Test", arxiv_id="2301.12345")
        assert p.get_identifier() == "2301.12345"

    def test_get_identifier_priority(self):
        p = Paper(title="Test", doi="10.1234/d", pmid="360", arxiv_id="2301.12345")
        assert p.get_identifier() == "10.1234/d"  # DOI has highest priority

    def test_get_identifier_none(self):
        p = Paper(title="Test")
        assert p.get_identifier() is None

    def test_validation_min_length(self):
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            Paper(title="")


class TestPaperGetPaperId:
    def test_get_paper_id_doi(self):
        p = Paper(title="Test", doi="10.1234/test")
        assert p.get_paper_id() == "10.1234/test"

    def test_get_paper_id_pmid(self):
        p = Paper(title="Test", pmid="36000001")
        assert p.get_paper_id() == "36000001"

    def test_get_paper_id_arxiv(self):
        p = Paper(title="Test", arxiv_id="2301.12345")
        assert p.get_paper_id() == "2301.12345"

    def test_get_paper_id_priority(self):
        p = Paper(title="Test", doi="10.1234/d", pmid="360", arxiv_id="2301.12345")
        assert p.get_paper_id() == "10.1234/d"

    def test_get_paper_id_priority_source_id(self):
        p = Paper(title="Test", arxiv_id="2301.12345", source_id="src-123")
        assert p.get_paper_id() == "2301.12345"

    def test_get_paper_id_source_id(self):
        p = Paper(title="Test", source_id="src-123")
        assert p.get_paper_id() == "src-123"

    def test_get_paper_id_fallback_title_slug(self):
        p = Paper(title="Test Paper")
        assert p.get_paper_id() == "Test_Paper"
