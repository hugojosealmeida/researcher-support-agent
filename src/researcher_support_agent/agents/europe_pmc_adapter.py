"""Europe PMC adapter for biomedical literature."""

from __future__ import annotations

import contextlib
from typing import Any

from ..models.paper import Author, Paper
from ..models.query import SearchQuery
from .paper_search import SourceAdapter

BASE_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest"


class EuropePMCAdapter(SourceAdapter):
    source_name = "europe_pmc"

    def _build_url(self, query: SearchQuery) -> str:
        from urllib.parse import urlencode

        params: dict[str, str] = {
            "query": query.query,
            "resultType": "core",
            "pageSize": str(query.page_size),
            "page": str(query.page),
        }
        if query.filters.get("date_from"):
            params["fromDate"] = query.filters["date_from"]
        if query.filters.get("date_to"):
            params["toDate"] = query.filters["date_to"]

        return f"{BASE_URL}/search?{urlencode(params)}"

    def _parse_paper(self, record: dict[str, Any]) -> Paper | None:
        title = record.get("title")
        if not title:
            return None
        if isinstance(title, str):
            title_text = title
        elif isinstance(title, list):
            title_text = title[0] if title else None
        else:
            title_text = None
        if not title_text or not isinstance(title_text, str):
            return None
        title_text = title_text.strip()

        authors: list[Author] = []
        for author in record.get("authorList", {}).get("author", [])[:20]:
            full = f"{author.get('forename', '')} {author.get('surname', '')}".strip()
            authors.append(Author(full_name=full or "Unknown"))

        pmid = record.get("pmid")
        pmcid = record.get("pmcid")
        doi = record.get("doi")

        pub_date = record.get("publishDate")
        year: int | None = None
        if pub_date:
            with contextlib.suppress(ValueError, TypeError):
                year = int(pub_date[:4])

        journal_title = record.get("journalTitle")
        abstract = record.get("abstractText")
        if abstract == "":
            abstract = None

        return Paper(
            title=title_text,
            authors=authors,
            year=year,
            venue=journal_title,
            doi=doi,
            pmid=pmid,
            source_id=pmcid or pmid,
            abstract=abstract,
            url=(
                f"https://www.ebi.ac.uk/europepmc/abstract/MED/{pmid}"
                if pmid
                else None
            ),
            retrieval_status="retrieved",
            processing_status="pending",
            metadata={"europe_pmc_id": pmcid or pmid},
        )

    def search(self, query: SearchQuery) -> list[dict[str, Any]]:
        """Execute search against Europe PMC API."""
        import os

        url = self._build_url(query)

        fixture = os.environ.get("EUROPEPMC_FIXTURE")
        if fixture:
            try:
                import json

                with open(fixture) as f:
                    data = json.load(f)
                results = data.get("resultList", {}).get("result", [])
                start = (query.page - 1) * query.page_size
                end = start + query.page_size
                return results[start:end]
            except FileNotFoundError:
                pass

        try:
            import requests

            resp = requests.get(url, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            query.results_count = int(data.get("resultCount", 0))
            return data.get("resultList", {}).get("result", [])
        except ImportError:
            return []

    def normalize(self, raw: dict[str, Any]) -> Paper | None:
        if isinstance(raw, dict):
            return self._parse_paper(raw)
        return None
