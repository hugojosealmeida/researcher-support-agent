"""Search query model."""

from __future__ import annotations

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
