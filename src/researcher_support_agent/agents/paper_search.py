"""Scholarly paper-search agent with source adapters.

Adapters:
- OpenAlex  (openalex.org)
- Crossref  (crossref.org)
- Europe PMC (europepmc.org)
- arXiv     (arxiv.org)

Results are normalised into ``Paper`` records with query provenance
and deduplication across sources.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any

import structlog

from ..models.paper import Paper
from ..models.query import SearchQuery

logger = structlog.get_logger(__name__)


class SourceAdapter(ABC):
    """Abstract base for a scholarly-source adapter."""

    source_name: str = "base"

    @abstractmethod
    def search(self, query: SearchQuery) -> list[dict[str, Any]]:
        """Execute a search and return raw (unnormalised) results."""

    def normalize(self, raw: dict[str, Any]) -> Paper | None:
        """Convert a single raw result dict into a ``Paper``.

        Override in subclasses.  Returns ``None`` if the record cannot
        be normalised.
        """
        return None


def deduplicate_papers(papers: list[Paper]) -> list[Paper]:
    """Deduplicate a list of papers by stable identifier, keeping the first."""
    seen: set[str] = set()
    deduplicated: list[Paper] = []
    for paper in papers:
        key = paper.get_identifier()
        if key and key in seen:
            logger.debug("dedup_duplicate", doi=key)
            continue
        if key:
            seen.add(key)
        # Also deduplicate by (title, year) as a fallback when no ID exists
        fallback_key = (paper.title.strip().lower(), paper.year) if paper.year else None
        if fallback_key and fallback_key in seen:
            logger.debug("dedup_duplicate_title_year", title=paper.title)
            continue
        if fallback_key:
            seen.add(fallback_key)
        deduplicated.append(paper)
    return deduplicated


class PaperSearchAgent:
    """Orchestrates searches across multiple scholarly sources."""

    def __init__(
        self,
        adapters: list[SourceAdapter] | None = None,
        max_pages: int = 3,
        page_size: int = 25,
        rate_limit_delay: float = 0.5,
    ) -> None:
        self.adapters = adapters or []
        self.max_pages = max_pages
        self.page_size = page_size
        self.rate_limit_delay = rate_limit_delay

    def search(
        self,
        query_string: str,
        sources: list[str] | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
    ) -> list[Paper]:
        """Run a search across the configured adapters.

        Returns deduplicated ``Paper`` records with query provenance.
        """
        all_raw: list[dict[str, Any]] = []
        used_adapters: list[SourceAdapter] = self.adapters
        if sources:
            used_adapters = [
                a for a in self.adapters if a.source_name in sources
            ]

        for adapter in used_adapters:
            for page in range(1, self.max_pages + 1):
                q = SearchQuery(
                    query=query_string,
                    database=adapter.source_name,
                    filters={},
                    page=page,
                    page_size=self.page_size,
                )
                if date_from:
                    q.filters["date_from"] = date_from
                if date_to:
                    q.filters["date_to"] = date_to

                raw_results = adapter.search(q)
                all_raw.extend(raw_results)
                if len(raw_results) < self.page_size:
                    break  # no more pages

        papers: list[Paper] = []
        for raw in all_raw:
            paper = None
            for adapter in used_adapters:
                paper = adapter.normalize(raw)
                if paper is not None:
                    break
            if paper is not None:
                paper.metadata.setdefault("query_provenance", {
                    "query": query_string,
                    "date_from": date_from,
                    "date_to": date_to,
                    "searched_at": datetime.now(timezone.utc).isoformat(),
                    "sources": [a.source_name for a in used_adapters],
                })
                papers.append(paper)

        return deduplicate_papers(papers)
