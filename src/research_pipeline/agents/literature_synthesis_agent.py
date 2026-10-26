"""Phase 5 — Literature Synthesis Agent."""

from __future__ import annotations

from typing import Any

from research_pipeline.agent_base import PipelineAgent
from research_pipeline.state import PipelineState


class LiteratureSynthesisAgent(PipelineAgent):
    """Compares methods, findings, disagreements, limitations and research gaps."""

    name = "literature_synthesis"

    def __init__(
        self,
        synthesis: dict[str, Any] | None = None,
    ) -> None:
        self.synthesis = synthesis or {}

    def run(self, state: PipelineState) -> PipelineState:
        if self.synthesis:
            state.synthesis = self.synthesis

        state.save("pipeline_state.json")
        return state
