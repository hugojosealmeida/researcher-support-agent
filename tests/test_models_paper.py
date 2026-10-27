"""Tests for data models."""


from datetime import UTC

import pytest

from researcher_support_agent.models.common import make_id, now_utc
from researcher_support_agent.models.evidence import Evidence
from researcher_support_agent.models.manuscript import Manuscript
from researcher_support_agent.models.paper import (
    Author,
    Citation,
    Paper,
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
        with pytest.raises(ValueError):
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
        c = Citation(
            key="alice2023", raw="Alice et al. (2023)", year=2023, title="Title"
        )
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

        assert ts.tzinfo == UTC

    def test_make_id(self):
        id1 = make_id()
        id2 = make_id()
        assert id1 != id2
        assert str(id1)  # should not raise
