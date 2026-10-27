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

:func:`http_get` additionally translates transport-level ``requests``
failures into the retry policy's vocabulary (:class:`RetryableError` for
connection errors, timeouts and HTTP 429/5xx — honoring ``Retry-After`` —
:class:`NonRetryableError` for permanent 4xx), so the adapters' configured
retry policies actually engage on transient failures.
"""

from __future__ import annotations

from typing import Any

from ..logging_config import get_logger
from ..reliability import NonRetryableError, RetryableError

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

# ``requests`` exception aliases used by the helpers below, each bound exactly
# once at module level: importing them inside the ``try`` and re-binding them
# in ``except ImportError`` is a ``mypy --strict`` ``no-redef`` error.  The
# real classes are resolved off ``requests.exceptions`` only when the library
# imported cleanly.  Under a broken install the aliases degrade to empty
# tuples, which keeps ``isinstance``/``except`` guards valid (never matching);
# ``get_http_client`` raises before any HTTP call anyway.
RequestsConnectionError: Any
RequestsHTTPError: Any
RequestsRequestException: Any
RequestsTimeout: Any
# Flattened so ``isinstance`` never receives nested non-type tuples when the
# aliases degrade to ``()``.
RETRYABLE_TRANSPORT_ERRORS: tuple[type[Exception], ...]

if REQUESTS_AVAILABLE:
    RequestsConnectionError = requests.exceptions.ConnectionError
    RequestsHTTPError = requests.exceptions.HTTPError
    RequestsRequestException = requests.exceptions.RequestException
    RequestsTimeout = requests.exceptions.Timeout
    RETRYABLE_TRANSPORT_ERRORS = (RequestsConnectionError, RequestsTimeout)
else:  # pragma: no cover - requests is a declared dependency
    RequestsConnectionError = ()
    RequestsHTTPError = ()
    RequestsRequestException = ()
    RequestsTimeout = ()
    RETRYABLE_TRANSPORT_ERRORS = ()


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


def _retry_after_seconds(response: Any) -> float | None:
    """Parse a numeric ``Retry-After`` header (delta-seconds) from a response.

    HTTP-date forms are ignored (the policy's exponential backoff applies);
    keeping seconds-only is the simple, header-shaped case APIs like Crossref
    return under rate limiting.
    """
    headers = getattr(response, "headers", None)
    if not headers:
        return None
    raw = headers.get("Retry-After") or headers.get("retry-after")
    if raw is None:
        return None
    try:
        seconds = float(str(raw).strip())
    except (TypeError, ValueError):
        return None
    return seconds if seconds >= 0 else None


def translate_http_error(exc: Exception, *, source_name: str = "") -> Exception:
    """Map a ``requests`` exception onto the retry policy's vocabulary.

    Transient outcomes (connection errors, timeouts, HTTP 429/5xx) become
    :class:`RetryableError`; permanent outcomes (other HTTP status codes and
    malformed requests such as invalid URLs or unparseable bodies) become
    :class:`NonRetryableError`.
    """
    label = f"{source_name or 'http'} request failed"
    if isinstance(exc, RETRYABLE_TRANSPORT_ERRORS):
        return RetryableError(f"{label}: transient transport error: {exc}")
    if isinstance(exc, RequestsHTTPError):
        response = getattr(exc, "response", None)
        status = getattr(response, "status_code", None)
        if isinstance(status, int) and (status == 429 or status >= 500):
            return RetryableError(
                f"{label}: HTTP {status} (transient)",
                retry_after=_retry_after_seconds(response),
            )
        return NonRetryableError(f"{label}: HTTP {status} is not retryable")
    return NonRetryableError(f"{label}: {exc}")


def http_get(
    client: Any, url: str, *, source_name: str = "", timeout: float = 30
) -> Any:
    """GET ``url``, translating transport failures for :class:`RetryPolicy`.

    Wraps ``client.get(url, timeout=...)`` plus ``raise_for_status()`` so that
    transient network blips and rate-limit/server errors surface as
    :class:`RetryableError` (retryable) instead of being misclassified as
    unexpected by the policy's generic arm.

    Raises:
        RetryableError: connection error, timeout, or HTTP 429/5xx.
        NonRetryableError: other HTTP status codes or malformed requests.
    """
    try:
        resp = client.get(url, timeout=timeout)
        resp.raise_for_status()
    except RequestsRequestException as exc:
        translated = translate_http_error(exc, source_name=source_name)
        logger.warning(
            "http_error_translated source=%s url=%s translated_as=%s error=%s",
            source_name or "unknown",
            url,
            type(translated).__name__,
            exc,
        )
        raise translated from exc
    return resp
