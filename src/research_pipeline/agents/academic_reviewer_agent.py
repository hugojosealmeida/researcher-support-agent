"""Phase 7 — Academic Reviewer Agent."""

from __future__ import annotations

from research_pipeline.agent_base import PipelineAgent
from research_pipeline.state import PipelineState, ReviewComment


class AcademicReviewerAgent(PipelineAgent):
    """Audits claims, abstract, structure, citations, bibliography and
    academic quality."""

    name = "academic_review"

    def __init__(
        self,
        comments: list[ReviewComment] | None = None,
        passed: bool | None = None,
    ) -> None:
        self.comments = comments or []
        self.passed = passed

    def run(self, state: PipelineState) -> PipelineState:
        if self.comments:
            state.review_comments = self.comments
        if self.passed is not None:
            state.review_passed = self.passed

        return state