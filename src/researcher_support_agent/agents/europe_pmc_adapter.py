"""Europe PMC adapter for biomedical literature."""

from __future__ import annotations

import contextlib
import os
from typing import Any, cast

from ..models.paper import Author, Paper
from ..models.query import SearchQuery
from ..reliability import RateLimiter, RetryableError, RetryPolicy
from .http_client import get_http_client
from .paper_search import SourceAdapter

BASE_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest"


class EuropePMCAdapter(SourceAdapter):
    """Adapter for the Europe PMC API.

    Includes rate limiting and retry policies (Phase E reliability) while
    preserving fixture-backed search/normalise behaviour.
    """

    source_name = "europe_pmc"

    def __init__(self, rate_limiter: RateLimiter | None = None) -> None:
        self.rate_limiter = rate_limiter
        self.retry_policy = RetryPolicy(
            max_retries=3,
            base_delay=1.0,
            retryable_exceptions=(RetryableError,),
        )

    def _build_url(self, query: SearchQuery) -> str:
        from urllib.parse import urlencode

        params: dict[str, str] = {
            "query": query.query,
            "resultType": "core",
            "pageSize": str(query.page_size),
            "page": str(query.page),
        }
        if query.filters.get("date_from"):
            params["fromDate"] = query.filters["date_from"]
        if query.filters.get("date_to"):
            params["toDate"] = query.filters["date_to"]

        return f"{BASE_URL}/search?{urlencode(params)}"

    def _parse_paper(self, record: dict[str, Any]) -> Paper | None:
        from collections.abc import Sequence

        title = record.get("title")
        title_text: str | None = None
        if isinstance(title, str):
            title_text = title
        elif isinstance(title, Sequence) and not isinstance(title, (bytes, bytearray)):
            first = title[0]
            if isinstance(first, str):
                title_text = first
        if not title_text:
            return None

        authors: list[Author] = []
        for author in record.get("authorList", {}).get("author", [])[:20]:
            full = f"{author.get('forename', '')} {author.get('surname', '')}".strip()
            authors.append(Author(full_name=full or "Unknown"))

        pmid = record.get("pmid")
        pmcid = record.get("pmcid")
        doi = record.get("doi")

        pub_date = record.get("publishDate")
        year: int | None = None
        if pub_date:
            with contextlib.suppress(ValueError, TypeError):
                year = int(pub_date[:4])

        journal_title = record.get("journalTitle")
        venue: str | None = None
        if isinstance(journal_title, str):
            venue = journal_title
        abstract = record.get("abstractText")
        if abstract == "":
            abstract = None

        return Paper(
            title=title_text,
            authors=authors,
            year=year,
            venue=venue,
            doi=doi,
            pmid=pmid,
            source_id=pmcid or pmid,
            abstract=abstract,
            url=f"https://www.ebi.ac.uk/europepmc/abstract/MED/{pmid}"
            if pmid
            else None,
            retrieval_status="retrieved",
            processing_status="pending",
            metadata={"europe_pmc_id": pmcid or pmid},
        )

    def search(self, query: SearchQuery) -> list[dict[str, Any]]:
        """Execute search against Europe PMC API."""
        if self.rate_limiter:
            self.rate_limiter.acquire()

        def _do_search() -> list[dict[str, Any]]:
            url = self._build_url(query)

            fixture = os.environ.get("EUROPEPMC_FIXTURE")
            if fixture:
                try:
                    import json

                    with open(fixture) as f:
                        data = json.load(f)
                    results = data.get("resultList", {}).get("result", [])
                    start = (query.page - 1) * query.page_size
                    end = start + query.page_size
                    return cast(list[dict[str, Any]], results[start:end])
                except FileNotFoundError:
                    pass

            client = get_http_client(self.source_name)
            resp = client.get(url, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            query.results_count = int(data.get("resultCount", 0))
            return cast(
                list[dict[str, Any]], data.get("resultList", {}).get("result", [])
            )

        return self.retry_policy.execute(_do_search)

    def normalize(self, raw: dict[str, Any]) -> Paper | None:
        if isinstance(raw, dict):
            return self._parse_paper(raw)
        return None

    def get_paper(self, pmid: str) -> Paper | None:
        if self.rate_limiter:
            self.rate_limiter.acquire()

        def _do_get() -> Paper | None:
            return None

        return self.retry_policy.execute(_do_get)
