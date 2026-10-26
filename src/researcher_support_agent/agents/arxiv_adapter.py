"""arXiv adapter for paper search."""

from __future__ import annotations

from ..models.paper import Paper


class ArxivAdapter:
    """Adapter for the arXiv API."""

    BASE_URL = "http://export.arxiv.org/api/query"

    def search(self, query: str, max_results: int = 10) -> list[Paper]:
        """Search arXiv for papers matching a query."""
        # Placeholder: in production, call the arXiv API
        return []

    def get_paper(self, arxiv_id: str) -> Paper | None:
        """Retrieve a specific paper by arXiv ID."""
        return None
