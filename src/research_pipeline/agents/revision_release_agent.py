"""Phase 8 — Revision & Release Agent."""

from __future__ import annotations

from research_pipeline.agent_base import PipelineAgent
from research_pipeline.state import PipelineState


class RevisionReleaseAgent(PipelineAgent):
    """Addresses reviewer comments, validates the final manuscript and
    publishes a versioned result."""

    name = "revision_release"

    def __init__(
        self,
        final_manuscript: str = "",
        version: str = "1.0",
        published: bool = False,
    ) -> None:
        self.final_manuscript = final_manuscript
        self.version = version
        self.published = published

    def run(self, state: PipelineState) -> PipelineState:
        if self.final_manuscript:
            state.final_manuscript = self.final_manuscript
        if self.version:
            state.version = self.version
        if isinstance(self.published, bool):
            state.published = self.published

        state.save("pipeline_state.json")
        return state
