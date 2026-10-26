"""Evidence and review models."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

from .common import Status, generate_id


class Evidence(BaseModel):
    """A piece of evidence extracted from one or more papers."""

    model_config = ConfigDict(validate_default=True)

    id: str = Field(default_factory=generate_id)
    claim: str = Field(..., min_length=1, description="The claim or finding")
    supporting_paper_ids: list[str] = Field(default_factory=list)
    strength: str | None = None  # e.g. "strong", "moderate", "weak"
    context: str | None = None
    confidence: float | None = Field(None, ge=0.0, le=1.0)
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @field_validator("claim")
    @classmethod
    def claim_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("claim must not be blank")
        return v


class ReviewFinding(BaseModel):
    """A finding from the academic review / quality audit phase."""

    model_config = ConfigDict(validate_default=True)

    id: str = Field(default_factory=generate_id)
    category: str = Field(..., min_length=1)  # e.g. "abstract", "citations", "claims"
    severity: str = Field(
        ..., min_length=1
    )  # "critical", "major", "minor", "suggestion"
    description: str = Field(..., min_length=1)
    location: str | None = None  # section or paragraph reference
    resolution: str | None = None
    status: Status = Status.PENDING
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @field_validator("category")
    @classmethod
    def category_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("category must not be blank")
        return v

    @field_validator("severity")
    @classmethod
    def severity_valid(cls, v: str) -> str:
        valid = {"critical", "major", "minor", "suggestion"}
        if v not in valid:
            raise ValueError(f"severity must be one of {valid}")
        return v
