"""Screening models for Phase B."""

from __future__ import annotations

from datetime import UTC, datetime
from enum import Enum

from pydantic import BaseModel, Field


class ScreeningDecision(str, Enum):
    """Screening decision for a paper."""

    INCLUDE = "include"
    EXCLUDE = "exclude"
    MAYBE = "maybe"


class ScreeningResult(BaseModel):
    """Result of screening a single paper."""

    paper_id: str = Field(..., description="The paper being screened")
    decision: ScreeningDecision = Field(..., description="Include/exclude decision")
    reason: str = Field(default="", min_length=0, description="Reason for the decision")
    scored_by: str | None = Field(default=None)
    scored_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
