"""arXiv adapter for preprints."""

from __future__ import annotations

import calendar
import contextlib
import os
import re
import xml.etree.ElementTree as ET
from typing import Any, cast

from ..models.paper import Author, Paper
from ..models.query import SearchQuery
from ..reliability import RateLimiter, RetryableError, RetryPolicy
from .http_client import get_http_client, http_get
from .paper_search import SourceAdapter

BASE_URL = "http://export.arxiv.org/api/query"

START_OF_DAY = "0000"
END_OF_DAY = "2359"
# arXiv rejects wildcard range endpoints (HTTP 500), so open-ended bounds are
# expressed with sentinel stamps: 1990 predates arXiv's July 1991 launch, and
# year 9999 is far beyond any submission.
OPEN_START = "199001010000"
OPEN_END = "999912312359"

# ``YYYY[-/]M[-/]D`` or the compact ``YYYY[M[M[M[M]]]]``; anything trailing
# (a time component, timezone) is ignored.
_DATE_PATTERN = re.compile(
    r"^(?P<year>\d{4})(?:"
    r"[-/](?P<month>\d{1,2})(?:[-/](?P<day>\d{1,2}))?"
    r"|(?P<month_compact>\d{2})?(?P<day_compact>\d{2})?"
    r")?"
)


def _submitted_date(value: Any, *, end_of_day: bool) -> str | None:
    """Convert a publication-window bound into an arXiv ``YYYYMMDDHHMM`` stamp.

    ``PaperSearchAgent`` threads ISO ``YYYY-MM-DD`` strings through
    ``query.filters``; the arXiv API wants them compacted and given a boundary
    time so a whole day is covered (``0000`` for the lower bound, ``2359`` for
    the upper one). Partial values are expanded to the first/last day of their
    month or year. Returns ``None`` when no year can be read, so the caller
    leaves the clause out rather than sending a malformed query.
    """
    match = _DATE_PATTERN.match(str(value).strip())
    if match is None:
        return None

    year = int(match.group("year"))
    month = match.group("month") or match.group("month_compact")
    day = match.group("day") or match.group("day_compact")

    # Widen a partial bound to the edge of its month/year matching the side of
    # the window it closes.
    if month is None:
        month = "12" if end_of_day else "1"
    month_number = min(max(int(month), 1), 12)

    try:
        last_day = calendar.monthrange(year, month_number)[1]
    except ValueError:
        return None
    if day is None:
        day = str(last_day) if end_of_day else "1"
    day_number = min(max(int(day), 1), last_day)

    boundary = END_OF_DAY if end_of_day else START_OF_DAY
    return f"{year:04d}{month_number:02d}{day_number:02d}{boundary}"


def _submitted_date_range(filters: dict[str, Any]) -> str | None:
    """Build the ``submittedDate:[...]`` clause for the requested window.

    An open-ended bound falls back to a sentinel stamp: ``date_from`` only
    constrains the lower bound, ``date_to`` only constrains the upper bound.
    ``None`` is returned when neither bound is usable, leaving the query shape
    untouched.
    """
    start = None
    if filters.get("date_from"):
        start = _submitted_date(filters["date_from"], end_of_day=False)
    end = None
    if filters.get("date_to"):
        end = _submitted_date(filters["date_to"], end_of_day=True)

    if start is None and end is None:
        return None
    return f"submittedDate:[{start or OPEN_START} TO {end or OPEN_END}]"


class ArxivAdapter(SourceAdapter):
    """Adapter for the arXiv API.

    Includes rate limiting and retry policies (Phase E reliability) while
    preserving fixture-backed search/normalise behaviour.
    """

    source_name = "arxiv"

    def __init__(self, rate_limiter: RateLimiter | None = None) -> None:
        self.rate_limiter = rate_limiter
        self.retry_policy = RetryPolicy(
            max_retries=3,
            base_delay=1.0,
            retryable_exceptions=(RetryableError,),
        )

    def _build_url(self, query: SearchQuery) -> str:
        from urllib.parse import urlencode

        search_query = f"all:{query.query}"
        date_range = _submitted_date_range(query.filters)
        if date_range:
            search_query = f"{search_query} AND {date_range}"

        params: dict[str, str] = {
            "search_query": search_query,
            "start": str((query.page - 1) * query.page_size),
            "max_results": str(query.page_size),
        }
        if date_range:
            # A date window is only meaningful chronologically, so sort by the
            # submission date. The lower bound picks the direction, which keeps
            # ``date_to`` from clobbering the order chosen for ``date_from``.
            params["sortBy"] = "submittedDate"
            params["sortOrder"] = (
                "ascending" if query.filters.get("date_from") else "descending"
            )

        return f"{BASE_URL}?{urlencode(params)}"

    def _parse_paper(self, entry: dict[str, Any]) -> Paper | None:
        from collections.abc import Sequence

        title = entry.get("title", "")
        title_text: str | None = None
        if isinstance(title, str):
            title_text = title
        elif isinstance(title, Sequence) and not isinstance(title, (bytes, bytearray)):
            first = title[0] if title else None
            if isinstance(first, str):
                title_text = first
        if not title_text:
            return None
        title = title_text.strip()

        authors: list[Author] = []
        for name in entry.get("authors", []):
            authors.append(Author(full_name=name.get("name", "Unknown")))

        published = entry.get("published", "")
        year: int | None = None
        if published:
            with contextlib.suppress(ValueError, TypeError):
                year = int(published[:4])

        arxiv_id = entry.get("id", "")
        summary = entry.get("summary", "")

        return Paper(
            title=title,
            authors=authors,
            year=year,
            arxiv_id=arxiv_id.replace("http://arxiv.org/abs/", "")
            .replace("https://arxiv.org/abs/", "")
            .strip(),
            source_id=entry.get("id"),
            abstract=summary,
            url=entry.get("id"),
            retrieval_status="retrieved",
            processing_status="pending",
            metadata={"arxiv_entry": entry.get("id")},
        )

    def search(self, query: SearchQuery) -> list[dict[str, Any]]:
        """Execute search against arXiv API (Atom XML)."""
        if self.rate_limiter:
            self.rate_limiter.acquire()

        def _do_search() -> list[dict[str, Any]]:
            url = self._build_url(query)

            fixture = os.environ.get("ARXIV_FIXTURE")
            if fixture:
                try:
                    import json

                    with open(fixture) as f:
                        data = json.load(f)
                    entries = cast(list[dict[str, Any]], data.get("entries", []))
                    start = (query.page - 1) * query.page_size
                    end = start + query.page_size
                    return entries[start:end]
                except FileNotFoundError:
                    pass

            client = get_http_client(self.source_name)
            resp = http_get(client, url, source_name=self.source_name)

            ns = {
                "atom": "http://www.w3.org/2005/Atom",
                "arxiv": "http://arxiv.org/schemas/atom",
            }
            root = ET.fromstring(resp.content)
            entries_raw = root.findall("atom:entry", ns)

            total = root.find("atom:totalResults", ns)
            if total is not None and total.text is not None:
                query.results_count = int(total.text)

            parsed_entries: list[dict[str, Any]] = []
            for entry in entries_raw:
                record: dict[str, Any] = {}
                record["title"] = entry.findtext("atom:title", "", ns).strip()
                record["id"] = entry.findtext("atom:id", "", ns)
                record["summary"] = entry.findtext("atom:summary", "", ns).strip()
                record["published"] = entry.findtext("atom:published", "", ns)
                authors_el = entry.findall("atom:author", ns)
                record["authors"] = [
                    {"name": a.findtext("atom:name", "", ns)} for a in authors_el
                ]
                parsed_entries.append(record)
            return parsed_entries

        return self.retry_policy.execute(_do_search)

    def normalize(self, raw: dict[str, Any]) -> Paper | None:
        if isinstance(raw, dict):
            return self._parse_paper(raw)
        return None

    def get_paper(self, arxiv_id: str) -> Paper | None:
        """Retrieve a specific paper by arXiv ID."""
        if self.rate_limiter:
            self.rate_limiter.acquire()

        def _do_get() -> Paper | None:
            return None

        return self.retry_policy.execute(_do_get)
