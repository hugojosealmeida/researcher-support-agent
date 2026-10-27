"""Tests for the paper search agent and adapters."""

import os

from researcher_support_agent.agents.arxiv_adapter import ArxivAdapter
from researcher_support_agent.agents.crossref_adapter import CrossrefAdapter
from researcher_support_agent.agents.europe_pmc_adapter import EuropePMCAdapter
from researcher_support_agent.agents.openalex_adapter import OpenAlexAdapter
from researcher_support_agent.agents.paper_search import (
    PaperSearchAgent,
    deduplicate_papers,
)
from researcher_support_agent.models.paper import Paper


class TestDeduplication:
    def test_deduplicate_by_doi(self):
        p1 = Paper(title="A", doi="10.1234/test", source_id="1")
        p2 = Paper(title="A", doi="10.1234/test", source_id="2")
        result = deduplicate_papers([p1, p2])
        assert len(result) == 1

    def test_deduplicate_by_title_year(self):
        p1 = Paper(title="Same Title", year=2023, source_id="1")
        p2 = Paper(title="Same Title", year=2023, source_id="2")
        result = deduplicate_papers([p1, p2])
        assert len(result) == 1

    def test_no_dedup_different_dois(self):
        p1 = Paper(title="A", doi="10.1234/a", source_id="1")
        p2 = Paper(title="B", doi="10.5678/b", source_id="2")
        result = deduplicate_papers([p1, p2])
        assert len(result) == 2

    def test_no_dedup_different_years(self):
        p1 = Paper(title="Same Title", year=2023, source_id="1")
        p2 = Paper(title="Same Title", year=2024, source_id="2")
        result = deduplicate_papers([p1, p2])
        assert len(result) == 2

    def test_empty_list(self):
        assert deduplicate_papers([]) == []


class TestOpenAlexAdapter:
    def test_normalize_fixture(self, openalex_fixture):
        os.environ["OPENALEX_FIXTURE"] = str(openalex_fixture)
        adapter = OpenAlexAdapter()
        try:
            q = type(
                "Query",
                (),
                {"page": 1, "page_size": 25, "query": "test", "filters": {}},
            )()
            raw = adapter.search(q)
            assert len(raw) == 2
            papers = [adapter.normalize(r) for r in raw]
            papers = [p for p in papers if p is not None]
            assert len(papers) == 2
            assert papers[0].title == "Deep Learning for Natural Language Processing"
            assert papers[0].doi == "10.1234/example"
            assert papers[0].authors[0].full_name == "Alice Smith"
            assert papers[0].authors[0].orcid == "https://orcid.org/0000-0001-2345-6789"
            assert papers[0].year == 2023
        finally:
            os.environ.pop("OPENALEX_FIXTURE", None)

    def test_normalize_none_for_empty_title(self):
        adapter = OpenAlexAdapter()
        result = adapter.normalize({"id": "W1"})
        assert result is None

    def test_abstract_reconstructed_from_positions(self):
        adapter = OpenAlexAdapter()
        record = {
            "id": "W999",
            "title": "Positional Abstract Test",
            "abstract_inverted_index": {"zebra": [0], "apple": [1]},
        }
        result = adapter.normalize(record)
        assert result is not None
        assert result.abstract == "zebra apple"


class TestCrossrefAdapter:
    def test_normalize_fixture(self, crossref_fixture):
        os.environ["CROSSREF_FIXTURE"] = str(crossref_fixture)
        adapter = CrossrefAdapter()
        try:
            q = type(
                "Query",
                (),
                {"page": 1, "page_size": 25, "query": "test", "filters": {}},
            )()
            raw = adapter.search(q)
            assert len(raw) == 2
            papers = [adapter.normalize(r) for r in raw]
            papers = [p for p in papers if p is not None]
            assert len(papers) == 2
            assert papers[0].title == "Bayesian Methods in Clinical Trials"
            assert papers[0].doi == "10.9999/clinical"
            assert papers[0].authors[0].full_name == "David Brown"
            assert papers[0].year == 2022
        finally:
            os.environ.pop("CROSSREF_FIXTURE", None)


class TestEuropePMCAdapter:
    def test_normalize_fixture(self, europe_pmc_fixture):
        os.environ["EUROPEPMC_FIXTURE"] = str(europe_pmc_fixture)
        adapter = EuropePMCAdapter()
        try:
            raw = adapter.search(
                type(
                    "Query",
                    (),
                    {"page": 1, "page_size": 25, "query": "test", "filters": {}},
                )()
            )
            assert len(raw) == 2
            papers = [adapter.normalize(r) for r in raw]
            papers = [p for p in papers if p is not None]
            assert len(papers) == 2
            assert papers[0].title == "Protein Structure Prediction"
            assert papers[0].pmid == "36000001"
            assert papers[0].doi == "10.1186/example1"
            assert papers[0].abstract == "We present a novel method..."
            assert papers[1].pmid == "36000002"
        finally:
            os.environ.pop("EUROPEPMC_FIXTURE", None)

    def test_empty_abstract_becomes_none(self, europe_pmc_fixture):
        os.environ["EUROPEPMC_FIXTURE"] = str(europe_pmc_fixture)
        adapter = EuropePMCAdapter()
        try:
            raw = adapter.search(
                type(
                    "Query",
                    (),
                    {"page": 1, "page_size": 25, "query": "test", "filters": {}},
                )()
            )
            paper = adapter.normalize(raw[1])
            assert paper.abstract is None
        finally:
            os.environ.pop("EUROPEPMC_FIXTURE", None)

    def test_string_title(self):
        adapter = EuropePMCAdapter()
        record = {
            "pmid": "36000099",
            "title": "A String Title",
            "authorList": {"author": []},
            "publishDate": "2023-01-01",
            "journalTitle": "Journal",
            "abstractText": "Abstract text",
        }
        paper = adapter.normalize(record)
        assert paper is not None
        assert paper.title == "A String Title"


class TestArxivAdapter:
    def test_normalize_fixture(self, arxiv_fixture):
        os.environ["ARXIV_FIXTURE"] = str(arxiv_fixture)
        adapter = ArxivAdapter()
        try:
            raw = adapter.search(
                type(
                    "Query",
                    (),
                    {"page": 1, "page_size": 25, "query": "test", "filters": {}},
                )()
            )
            assert len(raw) == 2
            papers = [adapter.normalize(r) for r in raw]
            papers = [p for p in papers if p is not None]
            assert len(papers) == 2
            assert papers[0].title == "Attention Is All You Need Revisited"
            assert papers[0].arxiv_id == "2301.12345"
            assert papers[0].year == 2023
            assert papers[0].authors[0].full_name == "Jack Chen"
        finally:
            os.environ.pop("ARXIV_FIXTURE", None)


class TestPaperSearchAgent:
    def test_search_with_fixtures(self, openalex_fixture, crossref_fixture):
        os.environ["OPENALEX_FIXTURE"] = str(openalex_fixture)
        os.environ["CROSSREF_FIXTURE"] = str(crossref_fixture)
        try:
            agent = PaperSearchAgent(
                adapters=[OpenAlexAdapter(), CrossrefAdapter()],
                max_pages=1,
                page_size=10,
            )
            papers = agent.search("test query", sources=["openalex", "crossref"])
            assert len(papers) > 0
            for paper in papers:
                prov = paper.metadata.get("query_provenance", {})
                assert prov.get("query") == "test query"
        finally:
            os.environ.pop("OPENALEX_FIXTURE", None)
            os.environ.pop("CROSSREF_FIXTURE", None)

    def test_deduplication_across_sources(self, openalex_fixture, crossref_fixture):
        """Papers with the same DOI from different sources should be deduplicated."""
        os.environ["OPENALEX_FIXTURE"] = str(openalex_fixture)
        os.environ["CROSSREF_FIXTURE"] = str(crossref_fixture)
        try:
            agent = PaperSearchAgent(
                adapters=[OpenAlexAdapter(), CrossrefAdapter()],
                max_pages=1,
                page_size=10,
            )
            papers = agent.search("test query")
            dois = [p.doi for p in papers if p.doi]
            assert len(dois) == len(set(dois))  # no duplicates
        finally:
            os.environ.pop("OPENALEX_FIXTURE", None)
            os.environ.pop("CROSSREF_FIXTURE", None)
