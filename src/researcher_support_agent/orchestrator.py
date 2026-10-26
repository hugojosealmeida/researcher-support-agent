"""Workflow orchestrator.

Owns phase order, retries, state transitions, and checkpoints.
"""

from __future__ import annotations

import json
import os
from datetime import UTC, datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from .logging_config import get_logger

logger = get_logger(__name__)


class Phase(str, Enum):
    """Pipeline phases in execution order."""

    PLAN = "plan"
    SEARCH = "search"
    SCREEN = "screen"
    RETRIEVE = "retrieve"
    SYNTHESIZE = "synthesize"
    MANUSCRIPT = "manuscript"


# Canonical phase order
PHASE_ORDER = [
    Phase.PLAN,
    Phase.SEARCH,
    Phase.SCREEN,
    Phase.RETRIEVE,
    Phase.SYNTHESIZE,
    Phase.MANUSCRIPT,
]


class PhaseState(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class OrchestratorState(BaseModel):
    """Persistable orchestrator state."""

    project_id: str = Field(..., description="Project identifier")
    phases: dict[str, PhaseState] = Field(
        default_factory=dict, description="Phase name -> status"
    )
    metadata: dict[str, Any] = Field(default_factory=dict)
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    def phase_statuses(self) -> dict[str, str]:
        """Return phase statuses as a simple dict."""
        return dict(self.phases)

    def is_phase_done(self, phase: Phase) -> bool:
        return self.phases.get(phase.value) == PhaseState.COMPLETED

    def set_phase(self, phase: Phase, state: PhaseState) -> None:
        self.phases[phase.value] = state
        self.updated_at = datetime.now(UTC)


class Orchestrator:
    """Manages the research pipeline lifecycle."""

    def __init__(
        self,
        state_file: str | None = None,
        max_retries: int = 3,
    ) -> None:
        self.state_file = state_file or "state.json"
        self.max_retries = max_retries
        self.state = OrchestratorState(project_id="default")
        self._load_state()

    def _load_state(self) -> None:
        if os.path.exists(self.state_file):
            with open(self.state_file) as f:
                self.state = OrchestratorState(**json.load(f))
            logger.info("state_loaded: %s", self.state_file)

    def save_state(self) -> None:
        with open(self.state_file, "w") as f:
            json.dump(self.state.model_dump(), f, indent=2, default=str)
        logger.info("state_saved: %s", self.state_file)

    def _get_phase_order(self) -> list[Phase]:
        """Return phases to run, skipping already completed ones."""
        return [p for p in PHASE_ORDER if not self.state.is_phase_done(p)]

    def run_phase(self, phase: Phase, handler) -> bool:
        """Execute a single phase with retry logic.

        ``handler`` is a callable(phase: Phase, state: OrchestratorState).
        Returns True on success.
        """
        for attempt in range(1, self.max_retries + 1):
            self.state.set_phase(phase, PhaseState.IN_PROGRESS)
            self.save_state()
            try:
                handler(phase, self.state)
                self.state.set_phase(phase, PhaseState.COMPLETED)
                self.save_state()
                logger.info(
                    "phase_completed: phase=%s attempt=%s", phase.value, attempt
                )
                return True
            except Exception as exc:
                logger.warning(
                    "phase_failed: phase=%s attempt=%s error=%s",
                    phase.value,
                    attempt,
                    str(exc),
                )
                if attempt < self.max_retries:
                    continue
                self.state.set_phase(phase, PhaseState.FAILED)
                self.save_state()
                raise

    def run_all(self) -> dict[str, PhaseState]:
        """Run all remaining phases in order."""
        phases = self._get_phase_order()
        if not phases:
            logger.info("all_phases_complete")
            return self.state.phase_statuses()

        logger.info("phase_run: phases=%s", [p.value for p in phases])

        phase_handlers: dict[Phase, Any] = {
            Phase.PLAN: self._handle_plan,
            Phase.SEARCH: self._handle_search,
            Phase.SCREEN: self._handle_screen,
            Phase.RETRIEVE: self._handle_retrieve,
            Phase.SYNTHESIZE: self._handle_synthesize,
            Phase.MANUSCRIPT: self._handle_manuscript,
        }

        for phase in phases:
            handler = phase_handlers.get(phase)
            if handler:
                self.run_phase(phase, handler)

        return self.state.phase_statuses()

    # Default phase handlers (subclasses or callers can override)
    def _handle_plan(self, phase: Phase, state: OrchestratorState) -> None:
        logger.info("plan_phase: state=%s", state.phase_statuses())

    def _handle_search(self, phase: Phase, state: OrchestratorState) -> None:
        logger.info("search_phase: state=%s", state.phase_statuses())

    def _handle_screen(self, phase: Phase, state: OrchestratorState) -> None:
        logger.info("screen_phase: state=%s", state.phase_statuses())

    def _handle_retrieve(self, phase: Phase, state: OrchestratorState) -> None:
        logger.info("retrieve_phase: state=%s", state.phase_statuses())

    def _handle_synthesize(self, phase: Phase, state: OrchestratorState) -> None:
        logger.info("synthesize_phase: state=%s", state.phase_statuses())

    def _handle_manuscript(
        self, phase: Phase, state: OrchestratorState
    ) -> None:
        logger.info("manuscript_phase: state=%s", state.phase_statuses())

    def dry_run(self) -> dict[str, bool]:
        """Validate state without executing."""
        result: dict[str, bool] = {}
        for phase in PHASE_ORDER:
            done = self.state.is_phase_done(phase)
            result[phase.value] = done
        return result
