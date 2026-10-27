"""Tests for the paper search agent."""

from researcher_support_agent.agents.paper_search import (
    PaperSearchAgent,
    PaperSearchResult,
)
from researcher_support_agent.models.query import SearchQuery


class TestPaperSearchResult:
    def test_minimal(self):
        r = PaperSearchResult(query=SearchQuery(terms=["test"]))
        assert r.papers == []
        assert r.total_results == 0


class TestPaperSearchAgent:
    def test_search(self):
        agent = PaperSearchAgent()
        query = SearchQuery(terms=["deep learning"], databases=["PubMed"])
        result = agent.search(query)
        assert isinstance(result, PaperSearchResult)
        assert result.query == query
        assert result.source == "PubMed"

    def test_search_multiple(self):
        agent = PaperSearchAgent()
        queries = [
            SearchQuery(terms=["test"], databases=["PubMed"]),
            SearchQuery(terms=["test2"], databases=["Scopus"]),
        ]
        results = agent.search_multiple(queries)
        assert len(results) == 2
        for r in results:
            assert isinstance(r, PaperSearchResult)
