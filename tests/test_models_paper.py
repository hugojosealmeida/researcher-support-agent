"""Tests for paper models: Paper, Author, Citation, PaperSummary."""

import json

import pytest

from researcher_support_agent.models import (
    Author,
    Citation,
    Paper,
    PaperSummary,
    RetrievalStatus,
    Status,
)


class TestAuthor:
    def test_valid_creation(self):
        a = Author(full_name="Jane Doe", orcid="0000-0000-0000-0000")
        assert a.full_name == "Jane Doe"

    def test_empty_name_raises(self):
        with pytest.raises(ValueError):
            Author(full_name="")


class TestCitation:
    def test_creation(self):
        c = Citation(key="smith2024", raw="Smith et al. (2024)", year=2024)
        assert str(c) == "Smith et al. (2024)"


class TestPaper:
    def test_valid_creation(self):
        p = Paper(title="Test Paper", year=2024)
        assert p.title == "Test Paper"
        assert p.retrieval_status == RetrievalStatus.NOT_RETRIEVED
        assert p.processing_status == Status.PENDING

    def test_empty_title_raises(self):
        with pytest.raises(ValueError):
            Paper(title="")

    def test_with_author(self):
        p = Paper(title="Paper", authors=[Author(full_name="Jane")])
        assert len(p.authors) == 1

    def test_doi_normalization(self):
        p = Paper(title="P", doi="https://doi.org/10.1234/test")
        assert p.doi == "10.1234/test"

    def test_pmid_normalization(self):
        p = Paper(title="P", pmid="  12345678  ")
        assert p.pmid == "12345678"

    def test_arxiv_normalization(self):
        p = Paper(title="P", arxiv_id="arxiv:2101.12345v2")
        assert p.arxiv_id == "2101.12345v2"

    def test_get_stable_id_returns_doi(self):
        p = Paper(title="P", doi="10.1234/test")
        assert p.get_stable_id() == "10.1234/test"

    def test_get_stable_id_returns_pmid(self):
        p = Paper(title="P", pmid="12345678")
        assert p.get_stable_id() == "12345678"

    def test_get_stable_id_returns_arxiv(self):
        p = Paper(title="P", arxiv_id="2101.12345")
        assert p.get_stable_id() == "2101.12345"

    def test_get_stable_id_none(self):
        p = Paper(title="P")
        assert p.get_stable_id() is None

    def test_duplicate_detection_same_doi(self):
        p1 = Paper(title="A", doi="10.1234/test")
        p2 = Paper(title="Different Title", doi="10.1234/test")
        assert p1.is_duplicate_of(p2)

    def test_duplicate_detection_same_doi_case_insensitive(self):
        p1 = Paper(title="A", doi="10.1234/Test")
        p2 = Paper(title="B", doi="10.1234/test")
        assert p1.is_duplicate_of(p2)

    def test_no_duplicate_different_doi(self):
        p1 = Paper(title="A", doi="10.1234/a")
        p2 = Paper(title="A", doi="10.1234/b")
        assert not p1.is_duplicate_of(p2)

    def test_no_stable_id_returns_false(self):
        p1 = Paper(title="A")
        p2 = Paper(title="A")
        assert not p1.is_duplicate_of(p2)

    def test_serialization(self):
        p = Paper(
            title="Test",
            year=2024,
            doi="10.1234/test",
            authors=[Author(full_name="Jane")],
            citations=[Citation(key="ref1", raw="Ref1")],
        )
        data = json.loads(p.model_dump_json())
        assert data["title"] == "Test"
        assert data["retrieval_status"] == "not_retrieved"
        assert data["processing_status"] == "pending"


class TestPaperSummary:
    def test_valid_creation(self):
        s = PaperSummary(paper_id="abc123", notes="Some notes")
        assert s.paper_id == "abc123"

    def test_relevance_score_validation(self):
        s = PaperSummary(paper_id="x", relevance_score=0.8)
        assert s.relevance_score == 0.8

    def test_relevance_score_bounds(self):
        with pytest.raises(ValueError):
            PaperSummary(paper_id="x", relevance_score=1.5)
        with pytest.raises(ValueError):
            PaperSummary(paper_id="x", relevance_score=-0.1)
