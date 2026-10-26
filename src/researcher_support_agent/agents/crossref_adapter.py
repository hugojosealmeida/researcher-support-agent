"""Crossref adapter for paper search."""

from __future__ import annotations

from ..models.paper import Paper


class CrossrefAdapter:
    """Adapter for the Crossref API."""

    BASE_URL = "https://api.crossref.org/works"

    def search(self, query: str, max_results: int = 10) -> list[Paper]:
        """Search Crossref for papers matching a query."""
        return []

    def get_paper(self, doi: str) -> Paper | None:
        """Retrieve a specific paper by DOI."""
        return None
