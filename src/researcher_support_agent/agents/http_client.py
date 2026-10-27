"""Shared HTTP client access for the source adapters.

``requests`` is a declared project dependency (see ``pyproject.toml``) and is
imported here at module scope so adapter modules stay importable and the
dependency is resolved once, up front.

If the library is somehow unavailable (a broken or partial install) the
adapters must fail loudly instead of silently returning an empty paper list —
the historical ``except ImportError: return []`` behaviour that made live
Crossref/arXiv/OpenAlex/Europe PMC searches look like "zero results" with no
error and no log line.  :func:`get_http_client` logs and raises
:class:`~researcher_support_agent.reliability.NonRetryableError`, which each
adapter's retry policy propagates immediately.  ``research doctor`` reports the
package status separately.
"""

from __future__ import annotations

from typing import Any

from ..logging_config import get_logger
from ..reliability import NonRetryableError

logger = get_logger(__name__)

try:
    import requests

    REQUESTS_AVAILABLE = True
except ImportError:  # pragma: no cover - requests is a declared dependency
    REQUESTS_AVAILABLE = False
    logger.warning(
        "http_library_missing: 'requests' is not installed; live scholarly "
        "API searches will fail. Reinstall with 'pip install -e .'."
    )


def get_http_client(source_name: str = "") -> Any:
    """Return the ``requests`` module used for live API calls.

    Args:
        source_name: Adapter/source that needs HTTP, used in the error message.

    Raises:
        NonRetryableError: if ``requests`` cannot be imported. This is a
            permanent environment problem, so it is surfaced loudly rather than
            swallowed into an empty result list.
    """
    if not REQUESTS_AVAILABLE:
        logger.error(
            "http_library_unavailable source=%s: 'requests' is not installed; "
            "cannot perform live search",
            source_name or "unknown",
        )
        target = f" for the {source_name} API" if source_name else ""
        raise NonRetryableError(
            f"HTTP library unavailable{target}: 'requests' is not installed "
            "(install project dependencies with 'pip install -e .')"
        )
    return requests
