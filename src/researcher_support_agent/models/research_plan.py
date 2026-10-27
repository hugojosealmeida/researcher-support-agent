"""Research plan model for Phase A/B."""

from __future__ import annotations

from pydantic import BaseModel, Field


class ResearchQuestion(BaseModel):
    """A single research question in the review protocol."""

    question: str = Field(..., min_length=1)
    pco: str = Field(
        default="", description="Population, Intervention/Exposure, Comparison, Outcome"
    )
    inclusion_criteria: str = Field(default="")
    exclusion_criteria: str = Field(default="")


class ResearchPlan(BaseModel):
    """A structured research plan for a systematic review."""

    title: str = Field(..., min_length=1)
    questions: list[ResearchQuestion] = Field(default_factory=list)
    search_strings: list[str] = Field(default_factory=list)
    databases: list[str] = Field(default_factory=list)
    inclusion_criteria: str = Field(default="")
    exclusion_criteria: str = Field(default="")
    notes: str = Field(default="", description="Additional planning notes")
