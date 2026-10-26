"""Paper search agent.

Searches academic databases (OpenAlex, Crossref, Europe PMC, arXiv)
for papers matching the research query.

Acceptance criteria:
- Search results include paper metadata, abstracts, and identifiers.
- Results are deduplicated across sources.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from ..models.paper import Paper
from ..models.query import SearchQuery


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
