"""arXiv adapter for paper search."""

from __future__ import annotations

from ..models.paper import Paper
from ..reliability import RateLimiter, RetryPolicy, RetryableError


class ArxivAdapter:
    """Adapter for the arXiv API.

    Includes rate limiting and retry policies (Phase E reliability).
    """

    BASE_URL = "http://export.arxiv.org/api/query"

    def __init__(self, rate_limiter: RateLimiter | None = None) -> None:
        self.rate_limiter = rate_limiter
        self.retry_policy = RetryPolicy(
            max_retries=3,
            base_delay=1.0,
            retryable_exceptions=(RetryableError,),
        )

    def search(self, query: str, max_results: int = 10) -> list[Paper]:
        """Search arXiv for papers matching a query.

        Uses rate limiting and retry policy for reliability.
        """
        if self.rate_limiter:
            self.rate_limiter.acquire()

        def _do_search() -> list[Paper]:
            # Placeholder: in production, call the arXiv API
            return []

        return self.retry_policy.execute(_do_search)

    def get_paper(self, arxiv_id: str) -> Paper | None:
        """Retrieve a specific paper by arXiv ID."""
        if self.rate_limiter:
            self.rate_limiter.acquire()

        def _do_get() -> Paper | None:
            return None

        return self.retry_policy.execute(_do_get)
