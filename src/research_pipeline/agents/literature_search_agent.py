"""Phase 2 — Literature Search Agent."""

from __future__ import annotations

from research_pipeline.agent_base import PipelineAgent
from research_pipeline.state import PipelineState, SearchItem


class LiteratureSearchAgent(PipelineAgent):
    """Searches scholarly databases, discovers papers and records metadata."""

    name = "literature_search"

    def __init__(
        self,
        search_results: list[SearchItem] | None = None,
        excluded_papers: list[SearchItem] | None = None,
    ) -> None:
        self.search_results = search_results or []
        self.excluded_papers = excluded_papers or []

    def run(self, state: PipelineState) -> PipelineState:
        if self.search_results:
            state.search_results = self.search_results
        if self.excluded_papers:
            state.excluded_papers = self.excluded_papers

        state.save("pipeline_state.json")
        return state
