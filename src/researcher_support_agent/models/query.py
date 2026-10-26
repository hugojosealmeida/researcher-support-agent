"""Search query model."""

from __future__ import annotations

from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class SearchQuery(BaseModel):
    """Represents a search query sent to a scholarly database."""

    query: str = Field(..., min_length=1, description="The search string")
    database: str = Field(
        ..., description="Target database or source name (e.g. 'openalex', 'crossref')"
    )
    filters: Dict[str, str] = Field(
        default_factory=dict, description="Additional filter parameters"
    )
    results_count: int = Field(default=0, description="Number of results returned")
    page: int = Field(default=1, description="Current page number")
    page_size: int = Field(default=25, description="Results per page")
