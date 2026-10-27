<<<<<<< HEAD
<<<<<<< HEAD
"""arXiv adapter for preprints."""

from __future__ import annotations

from typing import Any

from ..models.paper import Author, Paper
from ..models.query import SearchQuery
from .paper_search import SourceAdapter

BASE_URL = "http://export.arxiv.org/api/query"


class ArxivAdapter(SourceAdapter):
    source_name = "arxiv"

    def _build_url(self, query: SearchQuery) -> str:
        from urllib.parse import urlencode

        params: dict[str, str] = {
            "search_query": f"all:{query.query}",
            "start": str((query.page - 1) * query.page_size),
            "max_results": str(query.page_size),
        }
        if query.filters.get("date_from"):
            params["sortBy"] = "submittedDate"
            params["sortOrder"] = "ascending"
        if query.filters.get("date_to"):
            params["sortBy"] = "submittedDate"
            params["sortOrder"] = "descending"

        return f"{BASE_URL}?{urlencode(params)}"

    def _parse_paper(self, entry: dict[str, Any]) -> Paper | None:
        title = entry.get("title", "")
        if not title:
            return None
        title = title.strip()

        authors: list[Author] = []
        for name in entry.get("authors", []):
            authors.append(Author(full_name=name.get("name", "Unknown")))

        published = entry.get("published", "")
        year: int | None = None
        if published:
            try:
                year = int(published[:4])
            except (ValueError, TypeError):
                pass

        arxiv_id = entry.get("id", "")
        summary = entry.get("summary", "")

        return Paper(
            title=title,
            authors=authors,
            year=year,
            arxiv_id=arxiv_id.replace("http://arxiv.org/abs/", "")
            .replace("https://arxiv.org/abs/", "")
            .strip(),
            source_id=entry.get("id"),
            abstract=summary,
            url=entry.get("id"),
            retrieval_status="retrieved",
            processing_status="pending",
            metadata={"arxiv_entry": entry.get("id")},
        )

    def search(self, query: SearchQuery) -> list[dict[str, Any]]:
        """Execute search against arXiv API (Atom XML)."""
        import os

        url = self._build_url(query)

        fixture = os.environ.get("ARXIV_FIXTURE")
        if fixture:
            try:
                import json

                with open(fixture) as f:
                    data = json.load(f)
                entries = data.get("entries", [])
                start = (query.page - 1) * query.page_size
                end = start + query.page_size
                return entries[start:end]
            except FileNotFoundError:
                pass

        try:
            import requests

            resp = requests.get(url, timeout=30)
            resp.raise_for_status()
            import xml.etree.ElementTree as ET

            ns = {
                "atom": "http://www.w3.org/2005/Atom",
                "arxiv": "http://arxiv.org/schemas/atom",
            }
            root = ET.fromstring(resp.content)
            entries_raw = root.findall("atom:entry", ns)

            total = root.find("atom:totalResults", ns)
            if total is not None:
                query.results_count = int(total.text)

            entries: list[dict[str, Any]] = []
            for entry in entries_raw:
                record: dict[str, Any] = {}
                record["title"] = entry.findtext("atom:title", "", ns).strip()
                record["id"] = entry.findtext("atom:id", "", ns)
                record["summary"] = entry.findtext("atom:summary", "", ns).strip()
                record["published"] = entry.findtext("atom:published", "", ns)
                authors_el = entry.findall("atom:author", ns)
                record["authors"] = [
                    {"name": a.findtext("atom:name", "", ns)} for a in authors_el
                ]
                entries.append(record)
            return entries
        except ImportError:
            return []

    def normalize(self, raw: dict[str, Any]) -> Paper | None:
        if isinstance(raw, dict):
            return self._parse_paper(raw)
=======
=======
>>>>>>> 3eda405 (fix: Phase E — Reliability, Git integration and release (#6))
"""arXiv adapter for paper search."""

from __future__ import annotations

from ..models.paper import Paper
<<<<<<< HEAD


class ArxivAdapter:
    """Adapter for the arXiv API."""

    BASE_URL = "http://export.arxiv.org/api/query"

    def search(self, query: str, max_results: int = 10) -> list[Paper]:
        """Search arXiv for papers matching a query."""
        # Placeholder: in production, call the arXiv API
        return []

    def get_paper(self, arxiv_id: str) -> Paper | None:
        """Retrieve a specific paper by arXiv ID."""
>>>>>>> 10d6757 (fix: Phase D — Manuscript production and quality control (#5))
        return None
=======
from ..reliability import RateLimiter, RetryPolicy, RetryableError


class ArxivAdapter:
    """Adapter for the arXiv API.

    Includes rate limiting and retry policies (Phase E reliability).
    """

    BASE_URL = "http://export.arxiv.org/api/query"

    def __init__(self, rate_limiter: RateLimiter | None = None) -> None:
        self.rate_limiter = rate_limiter
        self.retry_policy = RetryPolicy(
            max_retries=3,
            base_delay=1.0,
            retryable_exceptions=(RetryableError,),
        )

    def search(self, query: str, max_results: int = 10) -> list[Paper]:
        """Search arXiv for papers matching a query.

        Uses rate limiting and retry policy for reliability.
        """
        if self.rate_limiter:
            self.rate_limiter.acquire()

        def _do_search() -> list[Paper]:
            # Placeholder: in production, call the arXiv API
            return []

        return self.retry_policy.execute(_do_search)

    def get_paper(self, arxiv_id: str) -> Paper | None:
        """Retrieve a specific paper by arXiv ID."""
        if self.rate_limiter:
            self.rate_limiter.acquire()

        def _do_get() -> Paper | None:
            return None

        return self.retry_policy.execute(_do_get)
>>>>>>> 3eda405 (fix: Phase E — Reliability, Git integration and release (#6))
