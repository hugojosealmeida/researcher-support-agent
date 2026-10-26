"""Search query model."""

from __future__ import annotations

from pydantic import BaseModel, Field


class SearchQuery(BaseModel):
    """A search query for the literature discovery phase."""

    terms: list[str] = Field(..., min_length=1, description="Search terms")
    databases: list[str] = Field(default_factory=list, description="Databases to search (e.g., PubMed, Scopus)")
    date_from: str | None = Field(default=None)
    date_to: str | None = Field(default=None)
    limit: int | None = Field(default=None)
