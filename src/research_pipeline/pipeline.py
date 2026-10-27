"""Pipeline orchestrator."""

from __future__ import annotations

from typing import TYPE_CHECKING

from research_pipeline.agent_base import PipelineAgent
from research_pipeline.state import PipelineState

if TYPE_CHECKING:
    pass  # no extra imports needed


class Pipeline:
    """Orchestrates the 8-phase research pipeline.

    Parameters
    ----------
    state : PipelineState | None
        Optional pre-existing state (e.g. loaded from a previous run).
    state_file : str | None
        Path to the JSON state file.  If ``None`` state is ephemeral.
    """

    VALID_PHASES: list[str] = [
        "planning",
        "literature_search",
        "paper_ingestion",
        "paper_summarization",
        "literature_synthesis",
        "review_paper_writing",
        "academic_review",
        "revision_release",
    ]

    def __init__(
        self,
        state: PipelineState | None = None,
        state_file: str | None = "pipeline_state.json",
    ) -> None:
        self._state = state or PipelineState()
        self._agents: dict[str, PipelineAgent] = {}
        self._state_file = state_file

    # ---- registration ---- #

    def register_agent(self, agent: PipelineAgent) -> None:
        """Register an agent under its ``name`` attribute."""
        self._agents[agent.name] = agent

    def _ensure_state_file(self) -> None:
        if self._state_file and not self._state_file.startswith("None"):
            self._state.save(self._state_file)

    # ---- execution ---- #

    def run_phase(
        self, phase_name: str, state: PipelineState | None = None
    ) -> PipelineState:
        """Run a single named phase.

        Parameters
        ----------
        phase_name : str
            One of the eight phase identifiers.
        state : PipelineState | None
            Optional external state override.  If ``None``, uses internal
            state (potentially loaded from *state_file*).

        Returns
        -------
        PipelineState
            The updated state after the phase completes.
        """
        if phase_name not in self.VALID_PHASES:
            raise ValueError(
                f"Unknown phase '{phase_name}'. "
                f"Valid phases: {self.VALID_PHASES}"
            )

        if state is not None:
            self._state = state

        agent = self._agents.get(phase_name)
        if agent is None:
            raise RuntimeError(f"No agent registered for phase '{phase_name}'")

        updated = agent.run(self._state)
        self._state = updated

        if phase_name not in self._state.completed_phases:
            self._state.completed_phases.append(phase_name)

        self._ensure_state_file()
        return self._state

    def run_full(self, state: PipelineState | None = None) -> PipelineState:
        """Execute all phases in order."""
        if state is not None:
            self._state = state

        for phase_name in self.VALID_PHASES:
            self._state = self.run_phase(phase_name)

        self._ensure_state_file()
        return self._state

    def run_from(
        self,
        phase_name: str,
        state: PipelineState | None = None,
    ) -> PipelineState:
        """Run all phases starting at *phase_name* through completion.

        Useful when state from earlier phases already exists and you
        want to regenerate downstream results (e.g. re-summarize papers
        after changing a prompt).
        """
        if state is not None:
            self._state = state

        if phase_name not in self.VALID_PHASES:
            raise ValueError(
                f"Unknown phase '{phase_name}'. "
                f"Valid phases: {self.VALID_PHASES}"
            )

        start_idx = self.VALID_PHASES.index(phase_name)
        for phase_name in self.VALID_PHASES[start_idx:]:
            self._state = self.run_phase(phase_name)

        self._ensure_state_file()
        return self._state

    # ---- state access ---- #

    @property
    def state(self) -> PipelineState:
        return self._state

    @state.setter
    def state(self, value: PipelineState) -> None:
        self._state = value

    def save_state(self) -> None:
        """Write current state to the configured state file."""
        self._ensure_state_file()

    def load_state(self) -> PipelineState:
        """Load state from the configured file and return it."""
        self._state = PipelineState.load(self._state_file)
        return self._state
