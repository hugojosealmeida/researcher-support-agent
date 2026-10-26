"""Tests for search query model."""

import pytest

from researcher_support_agent.models import SearchQuery


class TestSearchQuery:
    def test_valid_creation(self):
        q = SearchQuery(query="machine learning review", database="PubMed")
        assert q.query == "machine learning review"
        assert q.database == "PubMed"

    def test_empty_query_raises(self):
        with pytest.raises(ValueError):
            SearchQuery(query="", database="PubMed")

    def test_with_filters(self):
        q = SearchQuery(
            query="test",
            database="arXiv",
            filters={"year_from": 2020},
        )
        assert q.filters == {"year_from": 2020}

    def test_with_results(self):
        q = SearchQuery(query="test", database="PubMed")
        q.results_count = 42
        q.paper_ids = ["p1", "p2"]
        assert q.results_count == 42
        assert q.paper_ids == ["p1", "p2"]
