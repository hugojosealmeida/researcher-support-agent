"""Phase 4 — Paper Summarization Agent."""

from __future__ import annotations

from research_pipeline.agent_base import PipelineAgent
from research_pipeline.state import PipelineState, Summary


class PaperSummarizationAgent(PipelineAgent):
    """Produces evidence-grounded summaries and structured research notes."""

    name = "paper_summarization"

    def __init__(self, summaries: list[Summary] | None = None) -> None:
        self.summaries = summaries or []

    def run(self, state: PipelineState) -> PipelineState:
        if self.summaries:
            state.summaries = self.summaries

        return state
