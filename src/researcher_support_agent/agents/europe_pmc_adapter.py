"""Europe PMC adapter for paper search."""

from __future__ import annotations

from ..models.paper import Paper


class EuropePMCAdapter:
    """Adapter for the Europe PMC API."""

    BASE_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"

    def search(self, query: str, max_results: int = 10) -> list[Paper]:
        """Search Europe PMC for papers matching a query."""
        return []

    def get_paper(self, pmid: str) -> Paper | None:
        """Retrieve a specific paper by PMID."""
        return None
