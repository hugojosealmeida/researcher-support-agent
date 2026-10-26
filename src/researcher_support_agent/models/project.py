"""Research project model."""

from __future__ import annotations

from datetime import UTC, datetime
from enum import Enum

from pydantic import BaseModel, Field


class ProjectStatus(str, Enum):
    """Status of a research project."""

    ACTIVE = "active"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ResearchProject(BaseModel):
    """A research project tracking the systematic review process."""

    title: str = Field(..., min_length=1)
    description: str = Field(default="", min_length=0)
    status: ProjectStatus = Field(default=ProjectStatus.ACTIVE)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    metadata: dict[str, str] = Field(default_factory=dict)
    tags: list[str] = Field(default_factory=list)
