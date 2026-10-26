"""Manuscript model."""

from __future__ import annotations

from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class Manuscript(BaseModel):
    """A research manuscript with sections and version tracking."""

    sections: dict[str, str] = Field(
        default_factory=dict, description="Section name -> Markdown content"
    )
    version: int = Field(default=1, ge=1)
    references: list[str] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)

    def bump_version(self) -> int:
        """Increment the version number."""
        self.version += 1
        return self.version
