"""Tests for date-window filtering in the arXiv adapter.

Regression coverage for issue #43: ``PaperSearchAgent`` threads ``date_from`` /
``date_to`` into every adapter via ``query.filters``, but the arXiv adapter only
flipped ``sortBy``/``sortOrder`` and never put the dates into ``search_query``.
An arXiv search with a publication window therefore returned the same
unfiltered corpus as one without — and an upper bound clobbered the sort
direction chosen for the lower bound.  ``_build_url`` now emits an explicit
``submittedDate:[YYYYMMDDHHMM TO YYYYMMDDHHMM]`` clause.
"""

from typing import Any
from urllib.parse import parse_qs, unquote_plus, urlencode, urlparse

import pytest

from researcher_support_agent.agents import http_client
from researcher_support_agent.agents.arxiv_adapter import (
    BASE_URL,
    OPEN_END,
    OPEN_START,
    ArxivAdapter,
    _submitted_date,
)
from researcher_support_agent.models.query import SearchQuery

ARXIV_ATOM = b"""<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom"
      xmlns:opensearch="http://a9.com/-/spec/opensearch/1.1/">
  <opensearch:totalResults>1</opensearch:totalResults>
  <entry>
    <title>Windowed Preprint</title>
    <id>http://arxiv.org/abs/2105.00001</id>
    <summary>Published inside the requested window.</summary>
    <published>2021-05-03T00:00:00Z</published>
    <author><name>Hugo Almeida</name></author>
  </entry>
</feed>"""


def _query_params(url: str) -> dict[str, str]:
    """Decode ``url``'s query string into single-valued parameters."""
    return {key: values[0] for key, values in parse_qs(urlparse(url).query).items()}


def _url_for(**filters: Any) -> str:
    query = SearchQuery(terms=["transformer"], query="transformer", filters=filters)
    return ArxivAdapter()._build_url(query)


class TestSubmittedDateStamps:
    """Unit coverage for the ISO -> ``YYYYMMDDHHMM`` conversion."""

    @pytest.mark.parametrize(
        ("value", "expected"),
        [
            ("2020-01-01", "202001010000"),
            ("2020-1-1", "202001010000"),
            ("2020/01/01", "202001010000"),
            ("20200101", "202001010000"),
            ("20200101T0930", "202001010000"),
            # A time component still starts the day: the window bounds are
            # whole days for the caller.
            ("2020-01-01T09:30:00Z", "202001010000"),
            # Partial dates widen to the start of their month/year.
            ("2020", "202001010000"),
            ("2020-03", "202003010000"),
            ("202003", "202003010000"),
            # Impossible months/days clamp into their valid range.
            ("2023-02-30", "202302280000"),
            ("2023-13-05", "202312050000"),
        ],
    )
    def test_lower_bound(self, value: str, expected: str):
        assert _submitted_date(value, end_of_day=False) == expected

    @pytest.mark.parametrize(
        ("value", "expected"),
        [
            ("2023-12-31", "202312312359"),
            ("2023-12-31T07:15:00Z", "202312312359"),
            ("20231231", "202312312359"),
            ("2023", "202312312359"),
            ("2024-02", "202402292359"),
            ("2023-02", "202302282359"),
            ("2023-02-30", "202302282359"),
        ],
    )
    def test_upper_bound(self, value: str, expected: str):
        assert _submitted_date(value, end_of_day=True) == expected

    @pytest.mark.parametrize(
        "value", ["", "   ", "recent", "n/a", None, 0, "year 2020"]
    )
    def test_unusable_values_return_none(self, value: Any):
        assert _submitted_date(value, end_of_day=False) is None


class TestArxivDateFiltersInUrl:
    def test_closed_window_adds_submitted_date_clause(self):
        url = _url_for(date_from="2020-01-01", date_to="2023-12-31")

        # The clause is percent-encoded in the URL itself, so compare decoded.
        assert "submittedDate:[202001010000 TO 202312312359]" in unquote_plus(url)
        assert (
            _query_params(url)["search_query"]
            == "all:transformer AND submittedDate:[202001010000 TO 202312312359]"
        )

    def test_date_from_only_opens_the_upper_bound(self):
        params = _query_params(_url_for(date_from="2020-01-01"))
        assert (
            params["search_query"]
            == f"all:transformer AND submittedDate:[202001010000 TO {OPEN_END}]"
        )

    def test_date_to_only_opens_the_lower_bound(self):
        params = _query_params(_url_for(date_to="2023-12-31"))
        assert (
            params["search_query"]
            == f"all:transformer AND submittedDate:[{OPEN_START} TO 202312312359]"
        )

    def test_no_date_filters_leaves_query_shape_unchanged(self):
        url = _url_for()
        expected = (
            f"{BASE_URL}?"
            f"{urlencode({'search_query': 'all:transformer', 'start': '0', 'max_results': '25'})}"
        )
        assert url == expected

        params = _query_params(url)
        assert params["search_query"] == "all:transformer"
        assert "sortBy" not in params
        assert "sortOrder" not in params

    def test_unparseable_bounds_are_left_out_of_the_query(self):
        params = _query_params(_url_for(date_from="last year"))
        assert params["search_query"] == "all:transformer"
        assert "sortBy" not in params

    def test_pagination_survives_the_date_clause(self):
        query = SearchQuery(
            terms=["transformer"],
            query="transformer",
            page=3,
            page_size=10,
            filters={"date_from": "2020-01-01", "date_to": "2023-12-31"},
        )
        params = _query_params(ArxivAdapter()._build_url(query))
        assert params["start"] == "20"
        assert params["max_results"] == "10"
        assert "submittedDate:" in params["search_query"]


class TestArxivSortOrder:
    def test_date_from_sorts_ascending(self):
        params = _query_params(_url_for(date_from="2020-01-01"))
        assert params["sortBy"] == "submittedDate"
        assert params["sortOrder"] == "ascending"

    def test_date_to_sorts_descending(self):
        params = _query_params(_url_for(date_to="2023-12-31"))
        assert params["sortBy"] == "submittedDate"
        assert params["sortOrder"] == "descending"

    def test_date_to_does_not_clobber_date_from_direction(self):
        params = _query_params(_url_for(date_from="2020-01-01", date_to="2023-12-31"))
        assert params["sortBy"] == "submittedDate"
        assert params["sortOrder"] == "ascending"


class _WindowedResponse:
    """Minimal ``requests.Response`` stand-in for the arXiv Atom feed."""

    def raise_for_status(self) -> None:
        return None

    @property
    def content(self) -> bytes:
        return ARXIV_ATOM


class _RecordingClient:
    """``requests``-lookalike that records the URL it was asked to fetch."""

    def __init__(self) -> None:
        self.calls: list[str] = []

    def get(self, url: str, timeout: Any = None) -> _WindowedResponse:
        assert timeout is not None, "live HTTP calls must set a timeout"
        self.calls.append(url)
        return _WindowedResponse()


class TestSearchUsesTheWindow:
    def test_search_request_carries_the_date_clause(
        self, monkeypatch: pytest.MonkeyPatch
    ):
        monkeypatch.delenv("ARXIV_FIXTURE", raising=False)
        client = _RecordingClient()
        monkeypatch.setattr(http_client, "REQUESTS_AVAILABLE", True)
        monkeypatch.setattr(http_client, "requests", client, raising=False)

        adapter = ArxivAdapter()
        papers = adapter.search(
            SearchQuery(
                terms=["transformer"],
                query="transformer",
                filters={"date_from": "2020-01-01", "date_to": "2023-12-31"},
            )
        )

        assert len(papers) == 1
        assert len(client.calls) == 1
        assert "submittedDate:[202001010000 TO 202312312359]" in unquote_plus(
            client.calls[0]
        )
