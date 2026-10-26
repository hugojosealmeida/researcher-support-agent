"""Workflow orchestrator — owns phase order, retries, state, and checkpoints."""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Protocol

from pydantic import BaseModel, Field

from .models.common import Status

# ── Phase types ──────────────────────────────────────────────────────


class PhaseResult(BaseModel):
    """Result returned by a phase execution."""

    phase: str
    status: Status = Status.COMPLETED
    message: str = ""
    artifacts: dict[str, Any] = Field(default_factory=dict)
    error: str | None = None


# ── Protocol ─────────────────────────────────────────────────────────


class Phase(Protocol):
    """Interface for a single pipeline phase."""

    name: str

    def execute(self, state: OrchestratorState, **kwargs: Any) -> PhaseResult:
        """Run this phase. Must not mutate state outside returned artifacts."""
        ...


# ── State ────────────────────────────────────────────────────────────


@dataclass
class Checkpoint:
    """A saved point in the pipeline execution."""

    id: str
    timestamp: str
    phase_results: dict[str, PhaseResult]
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "timestamp": self.timestamp,
            "phase_results": {k: v.model_dump() for k, v in self.phase_results.items()},
            "metadata": self.metadata,
        }

    @staticmethod
    def from_dict(d: dict[str, Any]) -> Checkpoint:
        results = {k: PhaseResult(**v) for k, v in d["phase_results"].items()}
        return Checkpoint(
            id=d["id"],
            timestamp=d["timestamp"],
            phase_results=results,
            metadata=d.get("metadata", {}),
        )


@dataclass
class OrchestratorState:
    """Shared mutable state passed through all phases."""

    project_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    _phase_results: dict[str, PhaseResult] = field(default_factory=dict)
    _checkpoints: list[Checkpoint] = field(default_factory=list)
    _started_at: str | None = None

    @property
    def started_at(self) -> str:
        if self._started_at is None:
            self._started_at = datetime.now(UTC).isoformat()
        return self._started_at

    @property
    def phase_results(self) -> dict[str, PhaseResult]:
        return self._phase_results

    @property
    def checkpoints(self) -> list[Checkpoint]:
        return self._checkpoints

    def get_phase_result(self, phase: str) -> PhaseResult | None:
        """Return the result for a phase, or None if not run."""
        return self._phase_results.get(phase)

    def phase_has_artifact(self, phase: str, artifact_key: str) -> bool:
        """Check if a phase has already produced a given artifact."""
        result = self.get_phase_result(phase)
        return result is not None and artifact_key in result.artifacts

    def save_phase_result(self, result: PhaseResult) -> None:
        """Store a phase result in state."""
        self._phase_results[result.phase] = result

    def checkpoint(self, metadata: dict[str, Any] | None = None) -> Checkpoint:
        """Create and persist a checkpoint."""
        cp = Checkpoint(
            id=str(uuid.uuid4())[:8],
            timestamp=datetime.now(UTC).isoformat(),
            phase_results=dict(self._phase_results),
            metadata=metadata or {},
        )
        self._checkpoints.append(cp)
        return cp

    def save_state(self, path: Path) -> None:
        """Serialize state to a JSON file."""
        data = {
            "project_id": self.project_id,
            "started_at": self._started_at,
            "metadata": self.metadata,
            "phase_results": {
                k: v.model_dump() for k, v in self._phase_results.items()
            },
            "checkpoints": [cp.to_dict() for cp in self._checkpoints],
        }
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, indent=2, default=str))

    @staticmethod
    def load_state(path: Path) -> OrchestratorState:
        """Deserialize state from a JSON file."""
        data = json.loads(path.read_text())
        state = OrchestratorState(
            project_id=data.get("project_id"),
            metadata=data.get("metadata", {}),
            _started_at=data.get("started_at"),
        )
        state._phase_results = {
            k: PhaseResult(**v) for k, v in data.get("phase_results", {}).items()
        }
        state._checkpoints = [
            Checkpoint.from_dict(cp) for cp in data.get("checkpoints", [])
        ]
        return state


# ── Orchestrator ─────────────────────────────────────────────────────


class Orchestrator:
    """Runs phases in order with retries, state management, and checkpoints.

    The orchestrator owns:
    - Phase ordering and dependency tracking
    - Retry logic with configurable max attempts
    - State persistence (save/load)
    - Checkpoint creation
    - Resume capability (skip completed phases)
    """

    def __init__(
        self,
        phases: list[Phase],
        *,
        max_retries: int = 3,
        state_path: str | None = None,
    ):
        self._phases = phases
        self._phase_map: dict[str, Phase] = {p.name: p for p in phases}
        self.max_retries = max_retries
        self._state = OrchestratorState()
        self._state_path = state_path
        self._results: dict[str, PhaseResult] = {}

        if state_path:
            state_file = Path(state_path)
            if state_file.exists():
                self._state = OrchestratorState.load_state(state_file)
                self._results = dict(self._state.phase_results)

    @property
    def state(self) -> OrchestratorState:
        return self._state

    @property
    def results(self) -> dict[str, PhaseResult]:
        return self._results

    @property
    def phase_names(self) -> list[str]:
        return [p.name for p in self._phases]

    # ── Execution ──────────────────────────────────────────────────

    def run_phase(
        self,
        phase_name: str,
        *,
        skip_if_complete: bool = True,
        max_retries: int | None = None,
        **kwargs: Any,
    ) -> PhaseResult:
        """Run a single phase by name.

        If *skip_if_complete* is True and the phase already has a
        COMPLETED result in state, the phase is skipped.
        """
        phase = self._phase_map.get(phase_name)
        if phase is None:
            raise ValueError(f"Unknown phase: {phase_name!r}")

        retries = max_retries if max_retries is not None else self.max_retries

        # Check if we can skip (already completed)
        if skip_if_complete:
            existing = self._state.get_phase_result(phase_name)
            if existing and existing.status == Status.COMPLETED:
                return existing

        last_error: Exception | None = None
        for attempt in range(1, retries + 1):
            try:
                result = phase.execute(self._state, **kwargs)
                self._state.save_phase_result(result)
                self._results[phase_name] = result
                if self._state_path:
                    self._state.save_state(Path(self._state_path))
                return result
            except Exception as exc:
                last_error = exc
                result = PhaseResult(
                    phase=phase_name,
                    status=Status.FAILED,
                    error=str(exc),
                )
                self._state.save_phase_result(result)
                self._results[phase_name] = result
                if attempt < retries:
                    # Exponential backoff placeholder
                    pass

        # All retries exhausted
        if last_error:
            raise last_error
        return result

    def run_full(self, **kwargs: Any) -> dict[str, PhaseResult]:
        """Execute all phases in registration order."""
        for phase in self._phases:
            self.run_phase(phase.name, **kwargs)
            self._state.checkpoint()
            if self._state_path:
                self._state.save_state(Path(self._state_path))
        return dict(self._results)

    def run_from(
        self,
        phase_name: str,
        *,
        max_retries: int | None = None,
        **kwargs: Any,
    ) -> dict[str, PhaseResult]:
        """Run from a given phase onward, skipping already-completed phases."""
        phase_indices = [p.name for p in self._phases]
        if phase_name not in phase_indices:
            raise ValueError(f"Unknown phase: {phase_name!r}")
        start = phase_indices.index(phase_name)
        for phase in self._phases[start:]:
            self.run_phase(phase.name, max_retries=max_retries, **kwargs)
            self._state.checkpoint()
            if self._state_path:
                self._state.save_state(Path(self._state_path))
        return dict(self._results)

    def save(self, path: str | None = None) -> None:
        """Persist state to disk."""
        p = path or self._state_path
        if p:
            self._state.save_state(Path(p))

    def resume_from_checkpoint(self, checkpoint_id: str | None = None) -> None:
        """Reset state to a saved checkpoint (or the latest)."""
        checkpoints = self._state.checkpoints
        if not checkpoints:
            raise RuntimeError("No checkpoints available to resume from")
        if checkpoint_id is None:
            cp = checkpoints[-1]
        else:
            cp = next((c for c in checkpoints if c.id == checkpoint_id), None)
            if cp is None:
                raise ValueError(f"Checkpoint {checkpoint_id} not found")
        self._state = OrchestratorState(
            project_id=self._state.project_id,
            metadata=cp.metadata.copy(),
            _started_at=cp.timestamp,
        )
        self._state._phase_results = dict(cp.phase_results)
        self._results = dict(cp.phase_results)
        self._state.checkpoint()
