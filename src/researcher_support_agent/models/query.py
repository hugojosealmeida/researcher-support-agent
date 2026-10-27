"""Search query model."""

from __future__ import annotations

<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

from .common import Status, generate_id


class SearchQuery(BaseModel):
    """A scholarly search query and its results."""

    model_config = ConfigDict(validate_default=True)

    id: str = Field(default_factory=generate_id)
    query: str = Field(..., min_length=1)
    database: str = Field(..., min_length=1)  # e.g. "PubMed", "Scopus", "arXiv"
    filters: dict[str, Any] = Field(default_factory=dict)
    status: Status = Status.PENDING
    results_count: int = 0
    paper_ids: list[str] = Field(default_factory=list)
    error: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    completed_at: datetime | None = None

    @field_validator("query")
    @classmethod
    def query_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("query must not be blank")
        return v
=======
=======
>>>>>>> 1123db3 (fix: Phase C — Evidence extraction and synthesis (#4))
from typing import Dict, List, Optional

=======
>>>>>>> 10d6757 (fix: Phase D — Manuscript production and quality control (#5))
=======
>>>>>>> 3eda405 (fix: Phase E — Reliability, Git integration and release (#6))
from pydantic import BaseModel, Field


class SearchQuery(BaseModel):
<<<<<<< HEAD
<<<<<<< HEAD
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
<<<<<<< HEAD
>>>>>>> e45cda7 (fix: Phase B — Literature discovery and ingestion (#3))
=======
>>>>>>> 1123db3 (fix: Phase C — Evidence extraction and synthesis (#4))
=======
=======
>>>>>>> 3eda405 (fix: Phase E — Reliability, Git integration and release (#6))
    """A search query for the literature discovery phase."""

    terms: list[str] = Field(..., min_length=1, description="Search terms")
    databases: list[str] = Field(
        default_factory=list, description="Databases to search (e.g., PubMed, Scopus)"
    )
    date_from: str | None = Field(default=None)
    date_to: str | None = Field(default=None)
    limit: int | None = Field(default=None)
<<<<<<< HEAD
>>>>>>> 10d6757 (fix: Phase D — Manuscript production and quality control (#5))
=======
>>>>>>> 3eda405 (fix: Phase E — Reliability, Git integration and release (#6))
