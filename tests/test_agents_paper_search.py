"""Tests for the paper search agent and adapters."""

import inspect
import os
from typing import Any

import pytest

from researcher_support_agent.agents import http_client
from researcher_support_agent.agents.arxiv_adapter import ArxivAdapter
from researcher_support_agent.agents.crossref_adapter import CrossrefAdapter
from researcher_support_agent.agents.europe_pmc_adapter import EuropePMCAdapter
from researcher_support_agent.agents.openalex_adapter import OpenAlexAdapter
from researcher_support_agent.agents.paper_search import (
    PaperSearchAgent,
    PaperSearchResult,
    SourceAdapter,
    deduplicate_papers,
)
from researcher_support_agent.models.paper import Paper
from researcher_support_agent.models.query import SearchQuery
from researcher_support_agent.reliability import NonRetryableError

ALL_ADAPTERS = [
    OpenAlexAdapter,
    CrossrefAdapter,
    ArxivAdapter,
    EuropePMCAdapter,
]

# Adapter search() short-circuits to a fixture file when these are set, so
# tests that exercise the live HTTP path must make sure none of them leak in.
FIXTURE_ENV_VARS = [
    "OPENALEX_FIXTURE",
    "CROSSREF_FIXTURE",
    "ARXIV_FIXTURE",
    "EUROPEPMC_FIXTURE",
]


@pytest.fixture()
def no_fixtures(monkeypatch: pytest.MonkeyPatch) -> None:
    """Force every adapter down its live-HTTP code path."""
    for name in FIXTURE_ENV_VARS:
        monkeypatch.delenv(name, raising=False)


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

    def test_abstract_reconstructed_from_inverted_index(self):
        adapter = OpenAlexAdapter()
        result = adapter.normalize(
            {"title": "T", "abstract_inverted_index": {"b": [1], "a": [0]}}
        )
        assert result is not None
        assert result.abstract == "a b"

    def test_abstract_none_for_missing_or_empty_or_non_dict(self):
        adapter = OpenAlexAdapter()
        for value in (None, {}, "not a dict", 42):
            result = adapter.normalize({"title": "T", "abstract_inverted_index": value})
            assert result is not None
            assert result.abstract is None

    def test_abstract_handles_repeated_positions_and_words(self):
        adapter = OpenAlexAdapter()
        result = adapter.normalize(
            {
                "title": "T",
                "abstract_inverted_index": {"the": [0, 3], "cat": [1, 1], "sat": [2]},
            }
        )
        assert result is not None
        assert result.abstract == "the cat sat the"

    def test_abstract_fixture_still_deep_learning_nlp(self, openalex_fixture):
        os.environ["OPENALEX_FIXTURE"] = str(openalex_fixture)
        adapter = OpenAlexAdapter()
        try:
            q = type(
                "Query",
                (),
                {"page": 1, "page_size": 25, "query": "test", "filters": {}},
            )()
            raw = adapter.search(q)
            papers = [p for p in (adapter.normalize(r) for r in raw) if p is not None]
            assert papers[0].abstract == "deep learning nlp"
            assert papers[1].abstract is None
        finally:
            os.environ.pop("OPENALEX_FIXTURE", None)


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


class TestCrossrefTitleNormalization:
    def test_string_and_list_titles(self):
        adapter = CrossrefAdapter()
        assert (
            adapter.normalize({"title": "Full Title String"}).title
            == "Full Title String"
        )
        assert (
            adapter.normalize({"title": ["Full Title String"]}).title
            == "Full Title String"
        )
        assert adapter.normalize({"title": ""}) is None
        assert adapter.normalize({"title": []}) is None


class TestArxivTitleNormalization:
    def test_string_and_list_titles(self):
        adapter = ArxivAdapter()
        assert (
            adapter.normalize({"title": "  Full Title String  "}).title
            == "Full Title String"
        )
        assert (
            adapter.normalize({"title": ["  Full Title String  "]}).title
            == "Full Title String"
        )
        assert adapter.normalize({"title": ""}) is None
        assert adapter.normalize({"title": []}) is None


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
            assert len(dois) == len(set(dois))
        finally:
            os.environ.pop("OPENALEX_FIXTURE", None)
            os.environ.pop("CROSSREF_FIXTURE", None)


class TestPaperSearchResult:
    def test_minimal(self):
        r = PaperSearchResult(query=SearchQuery(terms=["test"]))
        assert r.papers == []
        assert r.total_results == 0


class TestPaperSearchAgentBasic:
    def test_search(self):
        agent = PaperSearchAgent()
        query = SearchQuery(terms=["deep learning"], databases=["PubMed"])
        result = agent.search(query)
        assert isinstance(result, PaperSearchResult)
        assert result.query == query
        assert result.source == "PubMed"
        # No adapters are registered, so nothing can be found — but the
        # search must still execute the real pipeline instead of a stub.
        assert result.papers == []
        assert result.total_results == 0

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


class _RecordingAdapter(SourceAdapter):
    """In-memory adapter that records the queries it receives."""

    def __init__(
        self,
        source_name: str,
        results: list[dict[str, Any]] | None = None,
        reported_total: int | None = None,
    ) -> None:
        self.source_name = source_name
        self.queries: list[Any] = []
        self._results = results if results is not None else []
        self._reported_total = reported_total

    def search(self, query: Any) -> list[dict[str, Any]]:
        self.queries.append(query)
        if self._reported_total is not None:
            query.results_count = self._reported_total
        return list(self._results)

    def normalize(self, raw: dict[str, Any]) -> Paper | None:
        if not raw.get("title"):
            return None
        return Paper(title=raw["title"], doi=raw.get("doi"), source_id=raw.get("id"))


class TestPaperSearchAgentSearchQuery:
    """``search(SearchQuery(...))`` must run the real adapters, not a stub."""

    def test_typed_search_returns_papers_with_fixtures(
        self, openalex_fixture, crossref_fixture
    ):
        os.environ["OPENALEX_FIXTURE"] = str(openalex_fixture)
        try:
            agent = PaperSearchAgent(
                adapters=[OpenAlexAdapter(), CrossrefAdapter()],
                max_pages=1,
                page_size=10,
            )
            result = agent.search(
                SearchQuery(terms=["deep learning"], databases=["openalex"])
            )
            assert isinstance(result, PaperSearchResult)
            assert result.papers, "typed search must return adapter results"
            assert result.total_results > 0
            assert result.source == "openalex"
            # Only the selected database was searched.
            titles = {p.title for p in result.papers}
            assert "Deep Learning for Natural Language Processing" in titles
            assert "Bayesian Methods in Clinical Trials" not in titles
            prov = result.papers[0].metadata["query_provenance"]
            assert prov["query"] == "deep learning"
            assert prov["sources"] == ["openalex"]
        finally:
            os.environ.pop("OPENALEX_FIXTURE", None)

    def test_databases_filtering_selects_matching_adapters(self):
        alpha = _RecordingAdapter(
            "alpha", results=[{"title": "From Alpha", "id": "A1"}]
        )
        beta = _RecordingAdapter("beta", results=[{"title": "From Beta", "id": "B1"}])
        agent = PaperSearchAgent(adapters=[alpha, beta], max_pages=1, page_size=10)

        result = agent.search(SearchQuery(terms=["x"], databases=["alpha"]))
        assert [p.title for p in result.papers] == ["From Alpha"]
        assert alpha.queries, "selected adapter must be invoked"
        assert not beta.queries, "unselected adapter must not be invoked"
        assert result.total_results == 1

    def test_databases_filtering_is_case_insensitive(self):
        adapter = _RecordingAdapter("openalex", results=[{"title": "From OpenAlex"}])
        agent = PaperSearchAgent(adapters=[adapter], max_pages=1, page_size=10)
        result = agent.search(SearchQuery(terms=["x"], databases=["OpenAlex"]))
        assert [p.title for p in result.papers] == ["From OpenAlex"]

    def test_empty_databases_searches_all_adapters(self):
        alpha = _RecordingAdapter(
            "alpha", results=[{"title": "From Alpha", "id": "A1"}]
        )
        beta = _RecordingAdapter("beta", results=[{"title": "From Beta", "id": "B1"}])
        agent = PaperSearchAgent(adapters=[alpha, beta], max_pages=1, page_size=10)

        result = agent.search(SearchQuery(terms=["x"]))
        assert alpha.queries and beta.queries
        assert {p.title for p in result.papers} == {"From Alpha", "From Beta"}
        assert result.source == "multiple"

    def test_query_string_prefers_query_then_joins_terms_with_and(self):
        alpha = _RecordingAdapter("alpha")
        agent = PaperSearchAgent(adapters=[alpha], max_pages=1, page_size=10)

        agent.search(SearchQuery(terms=["a", "b"]))
        assert alpha.queries[-1].query == "a AND b"

        agent.search(SearchQuery(terms=["ignored"], query="explicit text"))
        assert alpha.queries[-1].query == "explicit text"

    def test_date_filters_are_passed_through(self):
        alpha = _RecordingAdapter("alpha")
        agent = PaperSearchAgent(adapters=[alpha], max_pages=1, page_size=10)

        agent.search(
            SearchQuery(
                terms=["x"],
                databases=["alpha"],
                date_from="2020-01-01",
                date_to="2024-12-31",
            )
        )
        filters = alpha.queries[-1].filters
        assert filters["date_from"] == "2020-01-01"
        assert filters["date_to"] == "2024-12-31"

    def test_total_results_from_adapter_results_count(self):
        alpha = _RecordingAdapter(
            "alpha",
            results=[{"title": f"P{page}", "id": str(page)} for page in range(10)],
            reported_total=500,
        )
        agent = PaperSearchAgent(adapters=[alpha], max_pages=1, page_size=10)

        result = agent.search(SearchQuery(terms=["x"], databases=["alpha"]))
        # The source-reported total wins over the number of returned papers.
        assert result.total_results == 500
        assert len(result.papers) == 10

    def test_typed_search_deduplicates_across_sources(self):
        alpha = _RecordingAdapter(
            "alpha", results=[{"title": "Same", "id": "1", "doi": "10.1/x"}]
        )
        beta = _RecordingAdapter(
            "beta", results=[{"title": "Same", "id": "2", "doi": "10.1/x"}]
        )
        agent = PaperSearchAgent(adapters=[alpha, beta], max_pages=1, page_size=10)
        result = agent.search(SearchQuery(terms=["x"]))
        assert len(result.papers) == 1

    def test_search_multiple_returns_real_results(
        self, openalex_fixture, arxiv_fixture
    ):
        os.environ["OPENALEX_FIXTURE"] = str(openalex_fixture)
        os.environ["ARXIV_FIXTURE"] = str(arxiv_fixture)
        try:
            agent = PaperSearchAgent(
                adapters=[OpenAlexAdapter(), ArxivAdapter()],
                max_pages=1,
                page_size=10,
            )
            results = agent.search_multiple(
                [
                    SearchQuery(terms=["deep learning"], databases=["openalex"]),
                    SearchQuery(terms=["attention"], databases=["arxiv"]),
                ]
            )
            assert len(results) == 2
            for r in results:
                assert r.papers, "search_multiple must not return empty results"
                assert r.total_results > 0
            titles = {r.papers[0].title for r in results}
            assert "Deep Learning for Natural Language Processing" in titles
            assert "Attention Is All You Need Revisited" in titles
        finally:
            os.environ.pop("OPENALEX_FIXTURE", None)
            os.environ.pop("ARXIV_FIXTURE", None)


class TestHttpGetClient:
    def test_returns_library_when_available(self, monkeypatch: pytest.MonkeyPatch):
        sentinel = object()
        monkeypatch.setattr(http_client, "REQUESTS_AVAILABLE", True)
        monkeypatch.setattr(http_client, "requests", sentinel, raising=False)
        assert http_client.get_http_client("crossref") is sentinel

    def test_raises_when_library_missing(self, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setattr(http_client, "REQUESTS_AVAILABLE", False)
        with pytest.raises(NonRetryableError, match="requests"):
            http_client.get_http_client("crossref")

    def test_missing_library_error_names_the_source(
        self, monkeypatch: pytest.MonkeyPatch
    ):
        monkeypatch.setattr(http_client, "REQUESTS_AVAILABLE", False)
        with pytest.raises(NonRetryableError, match="for the arxiv API"):
            http_client.get_http_client("arxiv")


class TestHttpLibraryMissing:
    """A missing HTTP library must be loud, never an empty result list.

    Regression coverage for the silent ``except ImportError: return []``
    fallback that made live searches look like "zero papers found".
    """

    @pytest.mark.parametrize("adapter_class", ALL_ADAPTERS)
    def test_search_raises_instead_of_returning_empty(
        self,
        adapter_class: type,
        monkeypatch: pytest.MonkeyPatch,
        no_fixtures: None,
    ):
        monkeypatch.setattr(http_client, "REQUESTS_AVAILABLE", False)

        adapter = adapter_class()
        query = SearchQuery(terms=["deep learning"], query="deep learning")
        with pytest.raises(NonRetryableError) as excinfo:
            adapter.search(query)
        assert "not installed" in str(excinfo.value)

    @pytest.mark.parametrize("adapter_class", ALL_ADAPTERS)
    def test_adapters_do_not_swallow_import_error(self, adapter_class: type):
        """Guards against reintroducing the silent ImportError fallback."""
        source = inspect.getsource(adapter_class)
        assert "except ImportError" not in source


ARXIV_ATOM = b"""<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom"
      xmlns:opensearch="http://a9.com/-/spec/opensearch/1.1/">
  <opensearch:totalResults>42</opensearch:totalResults>
  <entry>
    <title>Attention Is All You Need Revisited</title>
    <id>http://arxiv.org/abs/2301.12345</id>
    <summary>We revisit the attention mechanism.</summary>
    <published>2023-01-25T00:00:00Z</published>
    <author><name>Jack Chen</name></author>
  </entry>
</feed>"""


class _FakeResponse:
    def __init__(self, payload: Any = None, content: bytes = b"") -> None:
        self._payload = payload
        self.content = content

    def raise_for_status(self) -> None:
        return None

    def json(self) -> Any:
        return self._payload


class _FakeRequests:
    """Stand-in for the ``requests`` module on the live code path."""

    def __init__(self, response: _FakeResponse) -> None:
        self.response = response
        self.calls: list[tuple[str, Any]] = []

    def get(self, url: str, timeout: Any = None) -> _FakeResponse:
        assert timeout is not None, "live HTTP calls must set a timeout"
        self.calls.append((url, timeout))
        return self.response


class TestLiveHttpSearch:
    """The live (non-fixture) code path is reachable now that ``requests`` is
    a declared dependency."""

    @pytest.mark.parametrize(
        "adapter_class,payload,content,expected_count",
        [
            (
                OpenAlexAdapter,
                {
                    "count": 12,
                    "results": [{"id": "W1234567", "title": "Deep Learning for NLP"}],
                },
                b"",
                12,
            ),
            (
                CrossrefAdapter,
                {
                    "message": {
                        "total-results": 7,
                        "items": [{"DOI": "10.9999/clinical", "title": ["Clinical"]}],
                    }
                },
                b"",
                7,
            ),
            (
                EuropePMCAdapter,
                {
                    "resultCount": 5,
                    "resultList": {
                        "result": [{"pmid": "36000001", "title": ["Protein"]}]
                    },
                },
                b"",
                5,
            ),
            (ArxivAdapter, None, ARXIV_ATOM, None),
        ],
    )
    def test_search_calls_api_and_parses_results(
        self,
        adapter_class: type,
        payload: Any,
        content: bytes,
        expected_count: int | None,
        monkeypatch: pytest.MonkeyPatch,
        no_fixtures: None,
    ):
        fake = _FakeRequests(_FakeResponse(payload=payload, content=content))
        monkeypatch.setattr(http_client, "REQUESTS_AVAILABLE", True)
        monkeypatch.setattr(http_client, "requests", fake, raising=False)

        adapter = adapter_class()
        query = SearchQuery(terms=["test"], query="test")
        raw = adapter.search(query)

        assert len(fake.calls) == 1
        assert raw, "live search must return the API results"
        if adapter_class is ArxivAdapter:
            assert raw[0]["title"] == "Attention Is All You Need Revisited"
            assert raw[0]["authors"] == [{"name": "Jack Chen"}]
        else:
            assert query.results_count == expected_count

    def test_agent_aggregates_live_results(
        self, monkeypatch: pytest.MonkeyPatch, no_fixtures: None
    ):
        fake = _FakeRequests(
            _FakeResponse(
                payload={
                    "message": {
                        "total-results": 1,
                        "items": [
                            {
                                "DOI": "10.9999/live",
                                "title": ["Live Result"],
                                "author": [{"given": "Ada", "family": "Lovelace"}],
                            }
                        ],
                    }
                }
            )
        )
        monkeypatch.setattr(http_client, "REQUESTS_AVAILABLE", True)
        monkeypatch.setattr(http_client, "requests", fake, raising=False)

        agent = PaperSearchAgent(adapters=[CrossrefAdapter()], max_pages=1)
        papers = agent.search("live query")
        assert [p.title for p in papers] == ["Live Result"]
        assert papers[0].authors[0].full_name == "Ada Lovelace"
