"""OpenAlex adapter for scholarly works."""

from __future__ import annotations

import contextlib
from typing import Any

from ..models.paper import Author, Paper
from ..models.query import SearchQuery
from .paper_search import SourceAdapter

BASE_URL = "https://api.openalex.org"


class OpenAlexAdapter(SourceAdapter):
    source_name = "openalex"

    def _build_url(self, query: SearchQuery) -> str:
        params: dict[str, str] = {
            "search": query.query,
            "per_page": str(query.page_size),
            "page": str(query.page),
        }
        filter_parts: list[str] = []
        if query.filters.get("date_from"):
            filter_parts.append(f"from_publication_date:{query.filters['date_from']}")
        if query.filters.get("date_to"):
            filter_parts.append(f"to_publication_date:{query.filters['date_to']}")
        if filter_parts:
            params["filter"] = ";".join(filter_parts)
        from urllib.parse import urlencode

        return f"{BASE_URL}/works?{urlencode(params)}"

    def _parse_paper(self, record: dict[str, Any]) -> Paper | None:
        title = record.get("title")
        # Handle both string and list title formats (Crossref uses lists)
        if isinstance(title, list):
            title = title[0] if title else None
        if not title or not isinstance(title, str):
            return None
        title = title.strip()

        authors: list[Author] = []
        author_display_names = record.get("authorships", [])
        if not author_display_names:
            # Crossref format uses "author" key instead
            for author in record.get("author", [])[:20]:
                given = author.get("given", "")
                family = author.get("family", "")
                name = f"{given} {family}".strip() or "Unknown"
                authors.append(Author(full_name=name, orcid=author.get("ORCID")))
        else:
            for authorship in author_display_names[:20]:  # cap at 20
                author = authorship.get("author", {})
                aff = (
                    author.get("affiliations", [{}])[0].get("institution", {})
                    if author.get("affiliations")
                    else {}
                )
                authors.append(
                    Author(
                        full_name=author.get("display_name", "Unknown"),
                        orcid=author.get("orcid", None),
                        affiliation=aff.get("display_name"),
                    )
                )

        doi = record.get("doi")
        if doi and isinstance(doi, str):
            doi = doi.replace("https://doi.org/", "")

        publication_date = record.get("publication_date")
        year: int | None = None
        if publication_date:
            with contextlib.suppress(ValueError, TypeError):
                year = int(publication_date[:4])

        venue = None
        primary_location = record.get("primary_location", {}) or {}
        source_info = primary_location.get("source", {}) or {}
        if source_info:
            venue = source_info.get("display_name")

        # OpenAlex abstract_inverted_index is a dict; convert to string
        abstract_raw = record.get("abstract_inverted_index")
        abstract: str | None = None
        if isinstance(abstract_raw, dict):
            try:
                positions: list[tuple[int, str]] = []
                for word, pos_list in abstract_raw.items():
                    if not isinstance(pos_list, list):
                        continue
                    for pos in pos_list:
                        positions.append((int(pos), str(word)))
                positions.sort(key=lambda pair: pair[0])
                abstract = " ".join(word for _, word in positions)
                if abstract == "":
                    abstract = None
            except (AttributeError, TypeError, ValueError):
                abstract = None

        return Paper(
            title=title,
            authors=authors,
            year=year,
            venue=venue,
            doi=doi,
            source_id=record.get("id"),
            abstract=abstract,
            url=(
                f"https://openalex.org/{record.get('id', '')}"
                if record.get("id")
                else None
            ),
            retrieval_status="retrieved",
            processing_status="pending",
            metadata={"openalex_id": record.get("id")},
        )

    def search(self, query: SearchQuery) -> list[dict[str, Any]]:
        """Execute search against OpenAlex API."""
        import os

        fixture = os.environ.get("OPENALEX_FIXTURE")
        if fixture:
            try:
                import json

                with open(fixture) as f:
                    data = json.load(f)
                start = (query.page - 1) * query.page_size
                end = start + query.page_size
                return data.get("results", [])[start:end]
            except FileNotFoundError:
                pass

        # Production: fetch from API
        try:
            import requests

            url = self._build_url(query)
            resp = requests.get(url, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            query.results_count = data.get("count", 0)
            return data.get("results", [])
        except ImportError:
            # requests not installed — return empty (tests mock this)
            return []

    def normalize(self, raw: dict[str, Any]) -> Paper | None:
        if isinstance(raw, dict):
            return self._parse_paper(raw)
        return None
