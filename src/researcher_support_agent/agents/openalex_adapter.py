"""OpenAlex adapter for paper search."""

from __future__ import annotations

from ..models.paper import Paper


class OpenAlexAdapter:
    """Adapter for the OpenAlex API."""

    BASE_URL = "https://api.openalex.org/works"

    def search(self, query: str, max_results: int = 10) -> list[Paper]:
        """Search OpenAlex for papers matching a query."""
        return []

    def get_paper(self, oa_id: str) -> Paper | None:
        """Retrieve a specific paper by OpenAlex ID."""
        return None
