<<<<<<< HEAD
<<<<<<< HEAD
"""Scholarly paper-search agent with source adapters.

Adapters:
- OpenAlex  (openalex.org)
- Crossref  (crossref.org)
- Europe PMC (europepmc.org)
- arXiv     (arxiv.org)

Results are normalised into ``Paper`` records with query provenance
and deduplication across sources.
=======
=======
>>>>>>> 3eda405 (fix: Phase E — Reliability, Git integration and release (#6))
"""Paper search agent.

Searches academic databases (OpenAlex, Crossref, Europe PMC, arXiv)
for papers matching the research query.

Acceptance criteria:
- Search results include paper metadata, abstracts, and identifiers.
- Results are deduplicated across sources.
<<<<<<< HEAD
>>>>>>> 10d6757 (fix: Phase D — Manuscript production and quality control (#5))
=======
>>>>>>> 3eda405 (fix: Phase E — Reliability, Git integration and release (#6))
"""

from __future__ import annotations

<<<<<<< HEAD
<<<<<<< HEAD
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any

import structlog
=======
from pydantic import BaseModel, Field
>>>>>>> 10d6757 (fix: Phase D — Manuscript production and quality control (#5))
=======
from pydantic import BaseModel, Field
>>>>>>> 3eda405 (fix: Phase E — Reliability, Git integration and release (#6))

from ..models.paper import Paper
from ..models.query import SearchQuery

<<<<<<< HEAD
<<<<<<< HEAD
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
=======
=======
>>>>>>> 3eda405 (fix: Phase E — Reliability, Git integration and release (#6))

class PaperSearchResult(BaseModel):
    """Result of a paper search query."""

    query: SearchQuery = Field(..., description="The search query that was executed")
    papers: list[Paper] = Field(default_factory=list, description="Matching papers")
    total_results: int = Field(default=0, description="Total number of results available")
    source: str = Field(default="", description="Which database was searched")
    search_time_ms: int | None = Field(default=None)


class PaperSearchAgent:
    """Agent that searches for papers across academic databases."""

    def __init__(self) -> None:
        pass

    def search(self, query: SearchQuery) -> PaperSearchResult:
        """Execute a paper search against available databases."""
        # This is a placeholder implementation.
        # In production, this would call the OpenAlex, Crossref, Europe PMC, and arXiv APIs.
        return PaperSearchResult(
            query=query,
            papers=[],
            total_results=0,
            source=query.databases[0] if query.databases else "multiple",
        )

    def search_multiple(self, queries: list[SearchQuery]) -> list[PaperSearchResult]:
        """Execute multiple searches."""
        return [self.search(q) for q in queries]
<<<<<<< HEAD
>>>>>>> 10d6757 (fix: Phase D — Manuscript production and quality control (#5))
=======
>>>>>>> 3eda405 (fix: Phase E — Reliability, Git integration and release (#6))
