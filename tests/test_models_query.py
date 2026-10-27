"""Tests for query model."""

import pytest

from researcher_support_agent.models.query import SearchQuery


class TestSearchQuery:
    def test_minimal(self):
        q = SearchQuery(query="test", database="openalex")
        assert q.query == "test"
        assert q.database == "openalex"
        assert q.filters == {}
        assert q.results_count == 0
        assert q.page == 1
        assert q.page_size == 25

    def test_with_filters(self):
        q = SearchQuery(
            query="deep learning",
            database="crossref",
            filters={"date_from": "2020-01-01", "date_to": "2024-12-31"},
            page=2,
            page_size=50,
        )
        assert q.filters["date_from"] == "2020-01-01"
        assert q.page == 2
        assert q.page_size == 50

    def test_validation_rejects_empty_query(self):
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            SearchQuery(query="", database="test")
