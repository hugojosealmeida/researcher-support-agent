"""OpenAlex adapter for scholarly works."""

from __future__ import annotations

import contextlib
import os
from typing import Any, cast

from ..models.paper import Author, Paper
from ..models.query import SearchQuery
from ..reliability import RateLimiter, RetryableError, RetryPolicy
from .paper_search import SourceAdapter

BASE_URL = "https://api.openalex.org"


class OpenAlexAdapter(SourceAdapter):
    """Adapter for the OpenAlex API.

    Includes rate limiting and retry policies (Phase E reliability) while
    preserving fixture-backed search/normalise behaviour.
    """

    source_name = "openalex"

    def __init__(self, rate_limiter: RateLimiter | None = None) -> None:
        self.rate_limiter = rate_limiter
        self.retry_policy = RetryPolicy(
            max_retries=3,
            base_delay=1.0,
            retryable_exceptions=(RetryableError,),
        )

    def _build_url(self, query: SearchQuery) -> str:
        params: dict[str, str] = {
            "search": query.query,
            "per_page": str(query.page_size),
            "page": str(query.page),
        }
        filter_parts: list[str] = []
        if query.filters.get("date_from"):
            filter_parts.append(f"from_publication_date:{query.filters['date_from']}")
        if query.filters.get("date_to"):
            filter_parts.append(f"to_publication_date:{query.filters['date_to']}")
        if filter_parts:
            params["filter"] = ";".join(filter_parts)
        from urllib.parse import urlencode

        return f"{BASE_URL}/works?{urlencode(params)}"

    def _parse_paper(self, record: dict[str, Any]) -> Paper | None:
        title = record.get("title")
        if isinstance(title, list):
            title = title[0] if title else None
        if not title or not isinstance(title, str):
            return None
        title = title.strip()

        authors: list[Author] = []
        author_display_names = record.get("authorships", [])
        if not author_display_names:
            for author in record.get("author", [])[:20]:
                given = author.get("given", "")
                family = author.get("family", "")
                name = f"{given} {family}".strip() or "Unknown"
                authors.append(Author(full_name=name, orcid=author.get("ORCID")))
        else:
            for authorship in author_display_names[:20]:
                author = authorship.get("author", {})
                aff = (
                    author.get("affiliations", [{}])[0].get("institution", {})
                    if author.get("affiliations")
                    else {}
                )
                authors.append(
                    Author(
                        full_name=author.get("display_name", "Unknown"),
                        orcid=author.get("orcid", None),
                        affiliation=aff.get("display_name"),
                    )
                )

        doi = record.get("doi")
        if doi and isinstance(doi, str):
            doi = doi.replace("https://doi.org/", "")

        publication_date = record.get("publication_date")
        year: int | None = None
        if publication_date:
            with contextlib.suppress(ValueError, TypeError):
                year = int(publication_date[:4])

        venue = None
        primary_location = record.get("primary_location", {}) or {}
        source_info = primary_location.get("source", {}) or {}
        if source_info:
            venue = source_info.get("display_name")

        abstract_raw = record.get("abstract_inverted_index")
        abstract: str | None = None
        if isinstance(abstract_raw, dict) and abstract_raw:
            try:
                # OpenAlex stores abstracts as an inverted index mapping each
                # word to the list of positions where it occurs. Reconstruct
                # the original text by placing words at their positions.
                max_pos = -1
                for positions in abstract_raw.values():
                    if isinstance(positions, (list, tuple)):
                        for pos in positions:
                            if isinstance(pos, bool):
                                continue
                            try:
                                p = int(pos)
                            except (TypeError, ValueError):
                                continue
                            if p > max_pos:
                                max_pos = p

                if max_pos >= 0:
                    tokens: list[str | None] = [None] * (max_pos + 1)
                    for word, positions in abstract_raw.items():
                        if not isinstance(word, str):
                            continue
                        if not isinstance(positions, (list, tuple)):
                            continue
                        for pos in positions:
                            if isinstance(pos, bool):
                                continue
                            try:
                                p = int(pos)
                            except (TypeError, ValueError):
                                continue
                            if 0 <= p <= max_pos:
                                tokens[p] = word
                    words = [w for w in tokens if w is not None]
                    abstract = " ".join(words) if words else None
            except (AttributeError, TypeError, ValueError, IndexError, KeyError):
                abstract = None

        return Paper(
            title=title,
            authors=authors,
            year=year,
            venue=venue,
            doi=doi,
            source_id=record.get("id"),
            abstract=abstract,
            url=f"https://openalex.org/{record.get('id', '')}"
            if record.get("id")
            else None,
            retrieval_status="retrieved",
            processing_status="pending",
            metadata={"openalex_id": record.get("id")},
        )

    def search(self, query: SearchQuery) -> list[dict[str, Any]]:
        """Execute search against OpenAlex API."""
        if self.rate_limiter:
            self.rate_limiter.acquire()

        def _do_search() -> list[dict[str, Any]]:
            fixture = os.environ.get("OPENALEX_FIXTURE")
            if fixture:
                try:
                    import json

                    with open(fixture) as f:
                        data = json.load(f)
                    start = (query.page - 1) * query.page_size
                    end = start + query.page_size
                    return cast(
                        list[dict[str, Any]], data.get("results", [])[start:end]
                    )
                except FileNotFoundError:
                    pass

            try:
                import requests

                url = self._build_url(query)
                resp = requests.get(url, timeout=30)
                resp.raise_for_status()
                data = resp.json()
                query.results_count = data.get("count", 0)
                return cast(list[dict[str, Any]], data.get("results", []))
            except ImportError:
                return []

        return self.retry_policy.execute(_do_search)

    def normalize(self, raw: dict[str, Any]) -> Paper | None:
        if isinstance(raw, dict):
            return self._parse_paper(raw)
        return None

    def get_paper(self, oa_id: str) -> Paper | None:
        if self.rate_limiter:
            self.rate_limiter.acquire()

        def _do_get() -> Paper | None:
            return None

        return self.retry_policy.execute(_do_get)
