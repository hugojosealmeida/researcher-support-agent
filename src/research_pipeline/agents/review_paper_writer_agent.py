"""Phase 6 — Review Paper Writer Agent."""

from __future__ import annotations

from research_pipeline.agent_base import PipelineAgent
from research_pipeline.state import PipelineState


class ReviewPaperWriterAgent(PipelineAgent):
    """Drafts the review manuscript from the approved evidence base."""

    name = "review_paper_writing"

    def __init__(self, manuscript: str = "") -> None:
        self.manuscript = manuscript

    def run(self, state: PipelineState) -> PipelineState:
        if self.manuscript:
            state.manuscript = self.manuscript

        return state
