<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
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
=======
=======
>>>>>>> 1123db3 (fix: Phase C — Evidence extraction and synthesis (#4))
=======
>>>>>>> 10d6757 (fix: Phase D — Manuscript production and quality control (#5))
=======
>>>>>>> 3eda405 (fix: Phase E — Reliability, Git integration and release (#6))
"""Tests for query model."""

import pytest

from researcher_support_agent.models.query import SearchQuery


class TestSearchQuery:
    def test_minimal(self):
<<<<<<< HEAD
<<<<<<< HEAD
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
<<<<<<< HEAD
>>>>>>> e45cda7 (fix: Phase B — Literature discovery and ingestion (#3))
=======
>>>>>>> 1123db3 (fix: Phase C — Evidence extraction and synthesis (#4))
=======
=======
>>>>>>> 3eda405 (fix: Phase E — Reliability, Git integration and release (#6))
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
<<<<<<< HEAD
>>>>>>> 10d6757 (fix: Phase D — Manuscript production and quality control (#5))
=======
>>>>>>> 3eda405 (fix: Phase E — Reliability, Git integration and release (#6))
