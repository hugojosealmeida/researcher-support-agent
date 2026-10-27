"""Screening decision models."""

from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class ScreeningDecision(StrEnum):
    ACCEPT = "accept"
    EXCLUDE = "exclude"
    BORDERLINE = "borderline"


class ScreeningResult(BaseModel):
    """A single screening decision for one paper.

    Every decision is traceable; excluded papers are retained in the
    screening log, not silently discarded.  Borderline cases are flagged
    for human review.
    """

    paper_id: str = Field(..., description="Identifier of the paper being screened")
    decision: ScreeningDecision = Field(...)
    reason: str = Field(..., min_length=1, description="Why this decision was made")
    uncertainty: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Confidence in the decision (1.0 = certain)",
    )
    criteria_matched: list[str] = Field(
        default_factory=list, description="Which inclusion/exclusion criteria matched"
    )
    flagged_for_review: bool = Field(
        default=False, description="True for borderline cases needing human review"
    )
    screened_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC)
    )
    source: str = Field(
        default="automated", description="Agent or human that performed screening"
    )
