"""Search query model."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class SearchQuery(BaseModel):
    """A search query for the literature discovery phase."""

    terms: list[str] = Field(..., min_length=1, description="Search terms")
    databases: list[str] = Field(
        default_factory=list, description="Databases to search (e.g., PubMed, Scopus)"
    )
    date_from: str | None = Field(default=None)
    date_to: str | None = Field(default=None)
    limit: int | None = Field(default=None)
    # Adapter-oriented fields (used by source adapters)
    query: str = Field(default="")
    database: str = Field(default="")
    page: int = Field(default=1)
    page_size: int = Field(default=25)
    filters: dict[str, Any] = Field(default_factory=dict)
    results_count: int = Field(default=0)
