"""Tests for transient-failure retry translation in the source adapters.

Regression coverage for issue #41: the adapters' ``RetryPolicy`` only listed
``RetryableError``, but transport failures (connection errors, timeouts, HTTP
429/5xx from ``raise_for_status()``) were leaking through the policy's generic
arm as ``NonRetryableError`` after a single attempt.  ``http_get`` now
translates them into the policy's vocabulary so retries with backoff engage.
"""

from typing import Any

import pytest
from requests.exceptions import (
    ConnectionError as ReqConnectionError,
)
from requests.exceptions import (
    HTTPError as ReqHTTPError,
)
from requests.exceptions import (
    InvalidURL,
    TooManyRedirects,
)
from requests.exceptions import (
    Timeout as ReqTimeout,
)

from researcher_support_agent.agents import http_client
from researcher_support_agent.agents.arxiv_adapter import ArxivAdapter
from researcher_support_agent.agents.crossref_adapter import CrossrefAdapter
from researcher_support_agent.agents.europe_pmc_adapter import EuropePMCAdapter
from researcher_support_agent.agents.openalex_adapter import OpenAlexAdapter
from researcher_support_agent.models.query import SearchQuery
from researcher_support_agent.reliability import (
    NonRetryableError,
    RetryableError,
)

# Adapter search() short-circuits to a fixture file when these are set, so
# tests that exercise the live HTTP path must make sure none of them leak in.
FIXTURE_ENV_VARS = [
    "OPENALEX_FIXTURE",
    "CROSSREF_FIXTURE",
    "ARXIV_FIXTURE",
    "EUROPEPMC_FIXTURE",
]

ARXIV_ATOM = b"""<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom"
      xmlns:opensearch="http://a9.com/-/spec/opensearch/1.1/">
  <opensearch:totalResults>1</opensearch:totalResults>
  <entry>
    <title>Attention Is All You Need Revisited</title>
    <id>http://arxiv.org/abs/2301.12345</id>
    <summary>We revisit the attention mechanism.</summary>
    <published>2023-01-25T00:00:00Z</published>
    <author><name>Jack Chen</name></author>
  </entry>
</feed>"""

# Success payloads so each adapter's parse path completes after a retry.
LIVE_SUCCESS: dict[type, tuple[Any, bytes]] = {
    OpenAlexAdapter: (
        {"count": 1, "results": [{"id": "W1", "title": "Retried Result"}]},
        b"",
    ),
    CrossrefAdapter: (
        {
            "message": {
                "total-results": 1,
                "items": [{"DOI": "10.9999/x", "title": ["Retried Result"]}],
            }
        },
        b"",
    ),
    EuropePMCAdapter: (
        {
            "resultCount": 1,
            "resultList": {"result": [{"pmid": "123", "title": ["Retried Result"]}]},
        },
        b"",
    ),
    ArxivAdapter: (None, ARXIV_ATOM),
}

ALL_ADAPTERS = list(LIVE_SUCCESS)


@pytest.fixture()
def no_fixtures(monkeypatch: pytest.MonkeyPatch) -> None:
    """Force every adapter down its live-HTTP code path."""
    for name in FIXTURE_ENV_VARS:
        monkeypatch.delenv(name, raising=False)


@pytest.fixture()
def recorded_sleeps(monkeypatch: pytest.MonkeyPatch) -> list[float]:
    """Capture RetryPolicy backoff sleeps so tests never actually delay."""
    delays: list[float] = []

    def fake_sleep(seconds: float) -> None:
        delays.append(seconds)

    monkeypatch.setattr("time.sleep", fake_sleep)
    return delays


class _ScriptedResponse:
    """Minimal ``requests.Response`` stand-in with a real HTTP status."""

    def __init__(
        self,
        status_code: int = 200,
        payload: Any = None,
        content: bytes = b"",
        headers: dict[str, str] | None = None,
    ) -> None:
        self.status_code = status_code
        self._payload = payload
        self.content = content
        self.headers = headers or {}

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise ReqHTTPError(f"{self.status_code} Error", response=self)

    def json(self) -> Any:
        return self._payload


class _ScriptedClient:
    """``requests``-module lookalike that replays a script of outcomes."""

    def __init__(self, script: list[Any]) -> None:
        self.script = list(script)
        self.calls: list[tuple[str, Any]] = []

    def get(self, url: str, timeout: Any = None) -> _ScriptedResponse:
        assert timeout is not None, "live HTTP calls must set a timeout"
        self.calls.append((url, timeout))
        if not self.script:
            raise AssertionError("unexpected extra HTTP call")
        outcome = self.script.pop(0)
        if isinstance(outcome, BaseException):
            raise outcome
        return outcome


def _install(
    monkeypatch: pytest.MonkeyPatch, client: _ScriptedClient
) -> _ScriptedClient:
    monkeypatch.setattr(http_client, "REQUESTS_AVAILABLE", True)
    monkeypatch.setattr(http_client, "requests", client, raising=False)
    return client


def _success_response(adapter_class: type) -> _ScriptedResponse:
    payload, content = LIVE_SUCCESS[adapter_class]
    return _ScriptedResponse(payload=payload, content=content)


class TestAdapterRetries:
    """Transient transport failures must be retried; permanent ones must not."""

    @pytest.mark.parametrize("adapter_class", ALL_ADAPTERS)
    def test_connection_errors_then_success_is_retried(
        self,
        adapter_class: type,
        monkeypatch: pytest.MonkeyPatch,
        no_fixtures: None,
        recorded_sleeps: list[float],
    ):
        _install(
            monkeypatch,
            _ScriptedClient(
                [
                    ReqConnectionError("network blip 1"),
                    ReqConnectionError("network blip 2"),
                    _success_response(adapter_class),
                ]
            ),
        )

        adapter = adapter_class()
        raw = adapter.search(SearchQuery(terms=["test"], query="test"))

        assert len(raw) == 1, "search must succeed after transient failures"
        assert len(recorded_sleeps) == 2
        # Exponential backoff with the adapters' base_delay=1.0, multiplier=2.
        assert recorded_sleeps == [1.0, 2.0]

    @pytest.mark.parametrize("adapter_class", ALL_ADAPTERS)
    def test_timeout_is_retried(
        self,
        adapter_class: type,
        monkeypatch: pytest.MonkeyPatch,
        no_fixtures: None,
        recorded_sleeps: list[float],
    ):
        _install(
            monkeypatch,
            _ScriptedClient([ReqTimeout("slow"), _success_response(adapter_class)]),
        )

        adapter = adapter_class()
        raw = adapter.search(SearchQuery(terms=["test"], query="test"))

        assert len(raw) == 1
        assert recorded_sleeps == [1.0]

    @pytest.mark.parametrize("adapter_class", ALL_ADAPTERS)
    def test_server_error_500_is_retried(
        self,
        adapter_class: type,
        monkeypatch: pytest.MonkeyPatch,
        no_fixtures: None,
        recorded_sleeps: list[float],
    ):
        _install(
            monkeypatch,
            _ScriptedClient(
                [
                    _ScriptedResponse(status_code=500),
                    _ScriptedResponse(status_code=502),
                    _success_response(adapter_class),
                ]
            ),
        )

        adapter = adapter_class()
        raw = adapter.search(SearchQuery(terms=["test"], query="test"))

        assert len(raw) == 1
        assert recorded_sleeps == [1.0, 2.0]

    @pytest.mark.parametrize("adapter_class", ALL_ADAPTERS)
    def test_rate_limit_429_is_retried_and_honors_retry_after(
        self,
        adapter_class: type,
        monkeypatch: pytest.MonkeyPatch,
        no_fixtures: None,
        recorded_sleeps: list[float],
    ):
        _install(
            monkeypatch,
            _ScriptedClient(
                [
                    _ScriptedResponse(status_code=429, headers={"Retry-After": "7"}),
                    _success_response(adapter_class),
                ]
            ),
        )

        adapter = adapter_class()
        raw = adapter.search(SearchQuery(terms=["test"], query="test"))

        assert len(raw) == 1
        # Retry-After (7s) exceeds the computed backoff (1s), so it wins.
        assert recorded_sleeps == [7.0]

    @pytest.mark.parametrize("adapter_class", ALL_ADAPTERS)
    def test_not_found_404_fails_fast(
        self,
        adapter_class: type,
        monkeypatch: pytest.MonkeyPatch,
        no_fixtures: None,
        recorded_sleeps: list[float],
    ):
        client = _install(monkeypatch, _ScriptedClient([_ScriptedResponse(404)]))

        adapter = adapter_class()
        with pytest.raises(NonRetryableError, match="HTTP 404"):
            adapter.search(SearchQuery(terms=["test"], query="test"))

        assert len(client.calls) == 1, "permanent failures must not be retried"
        assert recorded_sleeps == []

    @pytest.mark.parametrize("adapter_class", ALL_ADAPTERS)
    def test_malformed_request_fails_fast(
        self,
        adapter_class: type,
        monkeypatch: pytest.MonkeyPatch,
        no_fixtures: None,
        recorded_sleeps: list[float],
    ):
        client = _install(monkeypatch, _ScriptedClient([InvalidURL("bad url")]))

        adapter = adapter_class()
        with pytest.raises(NonRetryableError):
            adapter.search(SearchQuery(terms=["test"], query="test"))

        assert len(client.calls) == 1
        assert recorded_sleeps == []

    def test_retries_exhaust_then_propagate(
        self,
        monkeypatch: pytest.MonkeyPatch,
        no_fixtures: None,
        recorded_sleeps: list[float],
    ):
        client = _install(
            monkeypatch,
            _ScriptedClient(
                [
                    ReqConnectionError("down 1"),
                    ReqConnectionError("down 2"),
                    ReqConnectionError("down 3"),
                ]
            ),
        )

        adapter = CrossrefAdapter()  # policy has max_retries=3
        with pytest.raises(RetryableError, match="down 3") as excinfo:
            adapter.search(SearchQuery(terms=["test"], query="test"))

        # The policy re-raises the last translated error; the original
        # transport failure stays available as the chained cause.
        assert isinstance(excinfo.value.__cause__, ReqConnectionError)
        assert len(client.calls) == 3
        assert recorded_sleeps == [1.0, 2.0]


class TestTranslateHttpError:
    """Unit coverage for the shared exception-translation helper."""

    def test_connection_error_is_retryable(self):
        exc = http_client.translate_http_error(
            ReqConnectionError("reset"), source_name="crossref"
        )
        assert isinstance(exc, RetryableError)
        assert "crossref" in str(exc)

    def test_timeout_is_retryable(self):
        exc = http_client.translate_http_error(ReqTimeout("slow"))
        assert isinstance(exc, RetryableError)

    def test_http_429_is_retryable_with_retry_after(self):
        response = _ScriptedResponse(429, headers={"Retry-After": "30"})
        exc = http_client.translate_http_error(
            ReqHTTPError("too many", response=response), source_name="openalex"
        )
        assert isinstance(exc, RetryableError)
        assert exc.retry_after == 30.0

    def test_http_503_with_retry_after_header(self):
        response = _ScriptedResponse(503, headers={"Retry-After": "1.5"})
        exc = http_client.translate_http_error(
            ReqHTTPError("unavailable", response=response)
        )
        assert isinstance(exc, RetryableError)
        assert exc.retry_after == 1.5

    def test_retry_after_http_date_form_is_ignored(self):
        response = _ScriptedResponse(
            429, headers={"Retry-After": "Wed, 21 Oct 2015 07:28:00 GMT"}
        )
        exc = http_client.translate_http_error(
            ReqHTTPError("limited", response=response)
        )
        assert isinstance(exc, RetryableError)
        assert exc.retry_after is None

    def test_missing_or_blank_retry_after_is_none(self):
        for headers in ({}, {"Retry-After": ""}):
            response = _ScriptedResponse(429, headers=headers)
            exc = http_client.translate_http_error(
                ReqHTTPError("limited", response=response)
            )
            assert isinstance(exc, RetryableError)
            assert exc.retry_after is None

    @pytest.mark.parametrize("status", [400, 401, 403, 404, 422])
    def test_client_errors_are_not_retryable(self, status: int):
        response = _ScriptedResponse(status)
        exc = http_client.translate_http_error(
            ReqHTTPError("client error", response=response)
        )
        assert isinstance(exc, NonRetryableError)
        assert f"HTTP {status}" in str(exc)

    def test_http_error_without_response_is_not_retryable(self):
        exc = http_client.translate_http_error(ReqHTTPError("status unknown"))
        assert isinstance(exc, NonRetryableError)

    def test_other_request_exceptions_are_not_retryable(self):
        exc = http_client.translate_http_error(TooManyRedirects("loop"))
        assert isinstance(exc, NonRetryableError)

    def test_plain_exceptions_are_not_retryable(self):
        exc = http_client.translate_http_error(ValueError("not transport"))
        assert isinstance(exc, NonRetryableError)
