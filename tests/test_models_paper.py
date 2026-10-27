<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
"""Tests for paper models: Paper, Author, Citation, PaperSummary."""
=======
"""Tests for data models."""
>>>>>>> e45cda7 (fix: Phase B — Literature discovery and ingestion (#3))
=======
"""Tests for data models."""
>>>>>>> 1123db3 (fix: Phase C — Evidence extraction and synthesis (#4))

import json

import pytest

<<<<<<< HEAD
<<<<<<< HEAD
from researcher_support_agent.models import (
=======
=======
>>>>>>> 1123db3 (fix: Phase C — Evidence extraction and synthesis (#4))
from researcher_support_agent.models.common import make_id, now_utc
from researcher_support_agent.models.evidence import Evidence, ReviewFinding
from researcher_support_agent.models.manuscript import Manuscript
from researcher_support_agent.models.paper import (
<<<<<<< HEAD
>>>>>>> e45cda7 (fix: Phase B — Literature discovery and ingestion (#3))
=======
>>>>>>> 1123db3 (fix: Phase C — Evidence extraction and synthesis (#4))
    Author,
    Citation,
    Paper,
    PaperSummary,
<<<<<<< HEAD
<<<<<<< HEAD
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
=======
=======
>>>>>>> 1123db3 (fix: Phase C — Evidence extraction and synthesis (#4))
)
from researcher_support_agent.models.pdf_conversion import (
    ExtractionWarning,
    PDFConversionResult,
)
from researcher_support_agent.models.project import ProjectStatus, ResearchProject
from researcher_support_agent.models.query import SearchQuery


class TestResearchProject:
    def test_create_project(self):
        proj = ResearchProject(title="Test Project", questions=["Q1", "Q2"])
        assert proj.title == "Test Project"
        assert len(proj.questions) == 2
        assert proj.status == ProjectStatus.DRAFT

    def test_touch_updates_timestamp(self):
        import time

        proj = ResearchProject(title="Test")
        before = proj.updated_at
        time.sleep(0.01)
        proj.touch()
        assert proj.updated_at > before

    def test_validation_rejects_empty_title(self):
        with pytest.raises(Exception):
            ResearchProject(title="")


class TestPaper:
    def test_create_paper(self):
        paper = Paper(title="A Paper", authors=[Author(full_name="Alice")])
        assert paper.get_identifier() is None

    def test_get_identifier_doi(self):
        paper = Paper(title="A", doi="10.1234/test")
        assert paper.get_identifier() == "10.1234/test"

    def test_get_identifier_pmid(self):
        paper = Paper(title="A", pmid="12345")
        assert paper.get_identifier() == "12345"

    def test_get_identifier_arxiv(self):
        paper = Paper(title="A", arxiv_id="2301.1234")
        assert paper.get_identifier() == "2301.1234"

    def test_serialization(self):
        paper = Paper(
            title="Test",
            authors=[Author(full_name="Alice", orcid="0000-0001-2345-6789")],
            year=2023,
            doi="10.1234/test",
        )
        data = paper.model_dump()
        assert data["title"] == "Test"
        assert data["authors"][0]["full_name"] == "Alice"
        assert data["year"] == 2023


class TestAuthor:
    def test_author_without_optional_fields(self):
        a = Author(full_name="Test Author")
        assert a.orcid is None
        assert a.affiliation is None

    def test_author_with_all_fields(self):
        a = Author(full_name="Test", orcid="0000-0001-2345-6789", affiliation="Uni")
        assert a.orcid == "0000-0001-2345-6789"


class TestCitation:
    def test_create_citation(self):
        c = Citation(key="alice2023", raw="Alice et al. (2023)", year=2023, title="Title")
        assert c.year == 2023


class TestEvidence:
    def test_create_evidence(self):
        e = Evidence(claim="X causes Y", supporting_paper_ids=["1"], confidence=0.8)
        assert e.confidence == 0.8


class TestManuscript:
    def test_bump_version(self):
        m = Manuscript(sections={"intro": "Hello"})
        assert m.version == 1
        v = m.bump_version()
        assert v == 2
        assert m.version == 2


class TestSearchQuery:
    def test_create_query(self):
        q = SearchQuery(query="test", database="openalex")
        assert q.database == "openalex"
        assert q.page == 1


class TestCommon:
    def test_now_utc(self):
        ts = now_utc()
        from datetime import timezone

        assert ts.tzinfo == timezone.utc

    def test_make_id(self):
        id1 = make_id()
        id2 = make_id()
        assert id1 != id2
        assert str(id1)  # should not raise
<<<<<<< HEAD
>>>>>>> e45cda7 (fix: Phase B — Literature discovery and ingestion (#3))
=======
>>>>>>> 1123db3 (fix: Phase C — Evidence extraction and synthesis (#4))
=======
=======
>>>>>>> 3eda405 (fix: Phase E — Reliability, Git integration and release (#6))
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
<<<<<<< HEAD
>>>>>>> 10d6757 (fix: Phase D — Manuscript production and quality control (#5))
=======
>>>>>>> 3eda405 (fix: Phase E — Reliability, Git integration and release (#6))
