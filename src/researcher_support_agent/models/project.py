"""Project-level models: ResearchProject and ResearchQuestion."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

from .common import Status, generate_id


class ResearchQuestion(BaseModel):
    """A single research question within a project."""

    model_config = ConfigDict(validate_default=True)

    id: str = Field(default_factory=generate_id)
    question: str = Field(..., min_length=1, description="The research question text")
    inclusion_criteria: list[str] = Field(default_factory=list)
    exclusion_criteria: list[str] = Field(default_factory=list)
    status: Status = Status.PENDING
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("question")
    @classmethod
    def question_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("question must not be blank")
        return v


class ResearchProject(BaseModel):
    """The top-level research project container."""

    model_config = ConfigDict(validate_default=True)

    id: str = Field(default_factory=generate_id)
    title: str = Field(..., min_length=1)
    description: str = Field(default="", max_length=5000)
    questions: list[ResearchQuestion] = Field(default_factory=list)
    status: Status = Status.PENDING
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("title")
    @classmethod
    def title_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("title must not be blank")
        return v

    def add_question(self, question: ResearchQuestion) -> None:
        """Add a question to this project."""
        self.questions.append(question)
        self.updated_at = datetime.now(UTC)

    def set_status(self, status: Status) -> None:
        """Update project status and timestamp."""
        self.status = status
        self.updated_at = datetime.now(UTC)

    def update(self, **fields: Any) -> None:
        """Update fields and refresh the timestamp."""
        for name, value in fields.items():
            if hasattr(self, name):
                setattr(self, name, value)
        self.updated_at = datetime.now(UTC)
