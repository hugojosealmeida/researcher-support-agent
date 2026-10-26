"""Phase 1 — Research Topic & Planning Agent."""

from __future__ import annotations

from typing import Any

from research_pipeline.agent_base import PipelineAgent
from research_pipeline.state import PipelineState


class PlanningAgent(PipelineAgent):
    """Defines research questions, scope, inclusion criteria and search strategy."""

    name = "planning"

    def __init__(
        self,
        topic: str = "",
        research_questions: list[str] | None = None,
        scope: dict[str, Any] | None = None,
        inclusion_criteria: list[str] | None = None,
        search_strategy: str = "",
    ) -> None:
        self.topic = topic
        self.research_questions = research_questions or []
        self.scope = scope or {}
        self.inclusion_criteria = inclusion_criteria or []
        self.search_strategy = search_strategy

    def run(self, state: PipelineState) -> PipelineState:
        if self.topic:
            state.topic = self.topic
        if self.research_questions:
            state.research_questions = self.research_questions
        if self.scope:
            state.scope = self.scope
        if self.inclusion_criteria:
            state.inclusion_criteria = self.inclusion_criteria
        if self.search_strategy:
            state.search_strategy = self.search_strategy

        return state
