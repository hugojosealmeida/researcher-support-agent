<<<<<<< HEAD
<<<<<<< HEAD
"""Crossref adapter for DOI and bibliographic metadata."""

from __future__ import annotations

from typing import Any

from ..models.paper import Author, Paper
from ..models.query import SearchQuery
from .paper_search import SourceAdapter

BASE_URL = "https://api.crossref.org/works"


class CrossrefAdapter(SourceAdapter):
    source_name = "crossref"

    def _build_url(self, query: SearchQuery) -> str:
        from urllib.parse import urlencode

        params: dict[str, str] = {
            "query": query.query,
            "rows": str(query.page_size),
            "offset": str((query.page - 1) * query.page_size),
            "mailto": "researcher-support-agent@example.com",
        }
        if query.filters.get("date_from"):
            params["from-published-date"] = query.filters["date_from"]
        if query.filters.get("date_to"):
            params["until-published-date"] = query.filters["date_to"]

        return f"{BASE_URL}?{urlencode(params)}"

    def _parse_paper(self, record: dict[str, Any]) -> Paper | None:
        title_list = record.get("title", [])
        if not title_list:
            return None
        title = title_list[0]

        authors: list[Author] = []
        for author in record.get("author", [])[:20]:
            given = author.get("given", "")
            family = author.get("family", "")
            name = f"{given} {family}".strip() or "Unknown"
            authors.append(
                Author(
                    full_name=name,
                    orcid=author.get("ORCID", None),
                )
            )

        doi = record.get("DOI", None)
        published_print = record.get("published-print", {}) or record.get("published", {})
        year: int | None = None
        if published_print:
            date_parts = published_print.get("date-parts", [[]])[0]
            if date_parts:
                year = date_parts[0]

        container = record.get("container-title", [])
        venue = container[0] if container else None

        abstract = record.get("abstract", None)

        return Paper(
            title=title,
            authors=authors,
            year=year,
            venue=venue,
            doi=doi,
            source_id=record.get("DOI"),
            abstract=abstract,
            url=f"https://doi.org/{doi}" if doi else None,
            retrieval_status="retrieved",
            processing_status="pending",
            metadata={"crossref_id": record.get("ID")},
        )

    def search(self, query: SearchQuery) -> list[dict[str, Any]]:
        """Execute search against Crossref API."""
        import os

        url = self._build_url(query)

        fixture = os.environ.get("CROSSREF_FIXTURE")
        if fixture:
            try:
                import json

                with open(fixture) as f:
                    data = json.load(f)
                items = data.get("message", {}).get("items", [])
                start = (query.page - 1) * query.page_size
                end = start + query.page_size
                return items[start:end]
            except FileNotFoundError:
                pass

        try:
            import requests

            resp = requests.get(url, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            message = data.get("message", {})
            query.results_count = message.get("total-results", 0)
            return message.get("items", [])
        except ImportError:
            return []

    def normalize(self, raw: dict[str, Any]) -> Paper | None:
        if isinstance(raw, dict):
            return self._parse_paper(raw)
=======
=======
>>>>>>> 3eda405 (fix: Phase E — Reliability, Git integration and release (#6))
"""Crossref adapter for paper search."""

from __future__ import annotations

from ..models.paper import Paper
<<<<<<< HEAD


class CrossrefAdapter:
    """Adapter for the Crossref API."""

    BASE_URL = "https://api.crossref.org/works"

    def search(self, query: str, max_results: int = 10) -> list[Paper]:
        """Search Crossref for papers matching a query."""
        return []

    def get_paper(self, doi: str) -> Paper | None:
        """Retrieve a specific paper by DOI."""
>>>>>>> 10d6757 (fix: Phase D — Manuscript production and quality control (#5))
        return None
=======
from ..reliability import RateLimiter, RetryPolicy, RetryableError


class CrossrefAdapter:
    """Adapter for the Crossref API.

    Includes rate limiting and retry policies (Phase E reliability).
    """

    BASE_URL = "https://api.crossref.org/works"

    def __init__(self, rate_limiter: RateLimiter | None = None) -> None:
        self.rate_limiter = rate_limiter
        self.retry_policy = RetryPolicy(
            max_retries=3,
            base_delay=1.0,
            retryable_exceptions=(RetryableError,),
        )

    def search(self, query: str, max_results: int = 10) -> list[Paper]:
        """Search Crossref for papers matching a query."""
        if self.rate_limiter:
            self.rate_limiter.acquire()

        def _do_search() -> list[Paper]:
            return []

        return self.retry_policy.execute(_do_search)

    def get_paper(self, doi: str) -> Paper | None:
        """Retrieve a specific paper by DOI."""

        def _do_get() -> Paper | None:
            return None

        return self.retry_policy.execute(_do_get)
>>>>>>> 3eda405 (fix: Phase E — Reliability, Git integration and release (#6))
