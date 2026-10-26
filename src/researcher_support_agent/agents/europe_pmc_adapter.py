"""Europe PMC adapter for paper search."""

from __future__ import annotations

from ..models.paper import Paper
from ..reliability import RateLimiter, RetryPolicy, RetryableError


class EuropePMCAdapter:
    """Adapter for the Europe PMC API.

    Includes rate limiting and retry policies (Phase E reliability).
    """

    BASE_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"

    def __init__(self, rate_limiter: RateLimiter | None = None) -> None:
        self.rate_limiter = rate_limiter
        self.retry_policy = RetryPolicy(
            max_retries=3,
            base_delay=1.0,
            retryable_exceptions=(RetryableError,),
        )

    def search(self, query: str, max_results: int = 10) -> list[Paper]:
        """Search Europe PMC for papers matching a query."""
        if self.rate_limiter:
            self.rate_limiter.acquire()

        def _do_search() -> list[Paper]:
            return []

        return self.retry_policy.execute(_do_search)

    def get_paper(self, pmid: str) -> Paper | None:
        """Retrieve a specific paper by PMID."""

        def _do_get() -> Paper | None:
            return None

        return self.retry_policy.execute(_do_get)
