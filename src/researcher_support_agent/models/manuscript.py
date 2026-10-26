"""Manuscript model."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

from .common import Status, generate_id


class Manuscript(BaseModel):
    """A draft or final review manuscript."""

    model_config = ConfigDict(validate_default=True)

    id: str = Field(default_factory=generate_id)
    title: str = Field(..., min_length=1)
    sections: dict[str, str] = Field(default_factory=dict)
    status: Status = Status.PENDING
    version: int = Field(default=1, ge=1)
    references: list[str] = Field(default_factory=list)  # citation keys
    generated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("title")
    @classmethod
    def title_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("title must not be blank")
        return v

    def bump_version(self) -> None:
        """Increment version and update timestamp."""
        self.version += 1
        self.updated_at = datetime.now(UTC)

    def update_section(self, name: str, content: str) -> None:
        """Update a section of the manuscript."""
        self.sections[name] = content
        self.updated_at = datetime.now(UTC)

    def get_full_text(self) -> str:
        """Return the manuscript as a single markdown string."""
        parts: list[str] = []
        for section_name, content in self.sections.items():
            parts.append(f"## {section_name}\n\n{content}")
        return "\n\n".join(parts)
