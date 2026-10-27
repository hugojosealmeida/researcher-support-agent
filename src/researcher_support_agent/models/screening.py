<<<<<<< HEAD
<<<<<<< HEAD
"""Screening decision models."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Optional
=======
=======
>>>>>>> 3eda405 (fix: Phase E — Reliability, Git integration and release (#6))
"""Screening models for Phase B."""

from __future__ import annotations

from datetime import UTC, datetime
from enum import Enum
<<<<<<< HEAD
>>>>>>> 10d6757 (fix: Phase D — Manuscript production and quality control (#5))
=======
>>>>>>> 3eda405 (fix: Phase E — Reliability, Git integration and release (#6))

from pydantic import BaseModel, Field


class ScreeningDecision(str, Enum):
<<<<<<< HEAD
<<<<<<< HEAD
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
        default_factory=lambda: datetime.now(timezone.utc)
    )
    source: str = Field(
        default="automated", description="Agent or human that performed screening"
    )
=======
=======
>>>>>>> 3eda405 (fix: Phase E — Reliability, Git integration and release (#6))
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
<<<<<<< HEAD
>>>>>>> 10d6757 (fix: Phase D — Manuscript production and quality control (#5))
=======
>>>>>>> 3eda405 (fix: Phase E — Reliability, Git integration and release (#6))
