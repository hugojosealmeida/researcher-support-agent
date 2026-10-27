"""Evidence and review finding models."""

from __future__ import annotations

from pydantic import BaseModel, Field


class Evidence(BaseModel):
    """A piece of evidence linking a claim to supporting papers."""

    claim: str = Field(..., min_length=1)
    supporting_paper_ids: list[str] = Field(default_factory=list)
    strength: str = Field(default="weak")
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)


class ReviewFinding(BaseModel):
    """A finding from a quality or bias review."""

    category: str = Field(..., min_length=1)
    severity: str = Field(default="low")
    description: str = Field(..., min_length=1)
    resolution: str | None = Field(default=None)
