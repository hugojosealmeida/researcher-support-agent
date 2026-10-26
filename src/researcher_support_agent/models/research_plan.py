"""Research plan models for the research-planner agent."""

from __future__ import annotations

from datetime import UTC, datetime

from pydantic import BaseModel, Field


class ResearchQuestion(BaseModel):
    """A specific research question derived from the project topic."""

    question: str = Field(..., min_length=1, description="The research question")
    search_terms: list[str] = Field(
        default_factory=list, description="Keywords/phrases for database search"
    )
    synonyms: dict[str, list[str]] = Field(
        default_factory=dict,
        description="Mappings from concept -> synonym list",
    )
    date_from: str | None = Field(
        default=None, description="Start date filter (YYYY-MM-DD)"
    )
    date_to: str | None = Field(
        default=None, description="End date filter (YYYY-MM-DD)"
    )
    inclusion_criteria: list[str] = Field(
        default_factory=list, description="Inclusion criteria for screening"
    )
    exclusion_criteria: list[str] = Field(
        default_factory=list, description="Exclusion criteria for screening"
    )


class ProtocolApproval(BaseModel):
    """Tracks explicit approval of a research protocol."""

    approved: bool = Field(..., description="Whether the protocol was approved")
    approved_by: str = Field(..., description="Who approved it")
    approved_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC)
    )
    comments: str = Field(default="", description="Reviewer comments")


class ResearchPlan(BaseModel):
    """A validated research plan output by the research-planner agent.

    This is the stable, structured output format — not an unstructured paragraph.
    """

    project_id: str = Field(..., description="Parent project identifier")
    topic: str = Field(..., min_length=1, description="Research topic")
    research_questions: list[ResearchQuestion] = Field(
        default_factory=list, description="Derived research questions"
    )
    protocol_approved: bool = Field(
        default=False, description="Whether the protocol received explicit approval"
    )
    approval: ProtocolApproval | None = Field(
        default=None, description="Approval record if approved"
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC)
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC)
    )

    def approve(self, by: str, comments: str = "") -> None:
        """Record explicit approval of this plan."""
        self.protocol_approved = True
        self.approval = ProtocolApproval(
            approved=True, approved_by=by, comments=comments
        )
        self.updated_at = datetime.now(UTC)

    def needs_approval(self) -> bool:
        """Return True if the plan still requires explicit approval."""
        return not self.protocol_approved
