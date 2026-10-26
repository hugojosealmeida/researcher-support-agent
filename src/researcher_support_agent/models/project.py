"""Research project model."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class ProjectStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class ResearchProject(BaseModel):
    """Top-level container for a research project."""

    title: str = Field(..., min_length=1, description="Project title")
    description: str = Field(
        default="", description="Long-form description of the project"
    )
    questions: List[str] = Field(
        default_factory=list, description="High-level research questions"
    )
    status: ProjectStatus = Field(
        default=ProjectStatus.DRAFT, description="Current project status"
    )
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def touch(self) -> None:
        """Update the ``updated_at`` timestamp."""
        self.updated_at = datetime.now(timezone.utc)
