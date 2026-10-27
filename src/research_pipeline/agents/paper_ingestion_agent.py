"""Phase 3 — Paper Ingestion & Markdown Skill."""

from __future__ import annotations

from research_pipeline.agent_base import PipelineAgent
from research_pipeline.state import Paper, PipelineState


class PaperIngestionAgent(PipelineAgent):
    """Downloads permitted full texts, extracts content and creates structured
    Markdown files."""

    name = "paper_ingestion"

    def __init__(self, papers: list[Paper] | None = None) -> None:
        self.papers = papers or []

    def run(self, state: PipelineState) -> PipelineState:
        if self.papers:
            state.papers = self.papers

        return state
