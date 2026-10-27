"""Tests for query model."""

import pytest

from researcher_support_agent.models.query import SearchQuery


class TestSearchQuery:
    def test_minimal(self):
        q = SearchQuery(terms=["test"])
        assert q.terms == ["test"]
        assert q.databases == []

    def test_full(self):
        q = SearchQuery(
            terms=["deep learning"],
            databases=["PubMed", "Scopus"],
            date_from="2020-01-01",
            limit=100,
        )
        assert q.terms == ["deep learning"]
        assert q.databases == ["PubMed", "Scopus"]
        assert q.limit == 100

    def test_validation_min_terms(self):
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            SearchQuery(terms=[])
