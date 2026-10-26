"""Crossref adapter for paper search."""

from __future__ import annotations

from ..models.paper import Paper
from ..reliability import RateLimiter, RetryableError, RetryPolicy


class CrossrefAdapter:
    """Adapter for the Crossref API.

    Includes rate limiting and retry policies (Phase E reliability).
    """

    BASE_URL = "https://api.crossref.org/works"

    def __init__(self, rate_limiter: RateLimiter | None = None) -> None:
        self.rate_limiter = rate_limiter
        self.retry_policy = RetryPolicy(
            max_retries=3,
            base_delay=1.0,
            retryable_exceptions=(RetryableError,),
        )

    def search(self, query: str, max_results: int = 10) -> list[Paper]:
        """Search Crossref for papers matching a query."""
        if self.rate_limiter:
            self.rate_limiter.acquire()

        def _do_search() -> list[Paper]:
            return []

        return self.retry_policy.execute(_do_search)

    def get_paper(self, doi: str) -> Paper | None:
        """Retrieve a specific paper by DOI."""
        if self.rate_limiter:
            self.rate_limiter.acquire()

        def _do_get() -> Paper | None:
            return None

        return self.retry_policy.execute(_do_get)
