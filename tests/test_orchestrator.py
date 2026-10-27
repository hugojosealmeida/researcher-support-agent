<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
"""Tests for orchestrator module."""

from pathlib import Path
=======
=======
>>>>>>> 1123db3 (fix: Phase C — Evidence extraction and synthesis (#4))
"""Tests for the orchestrator."""

import os
import tempfile
<<<<<<< HEAD
>>>>>>> e45cda7 (fix: Phase B — Literature discovery and ingestion (#3))
=======
>>>>>>> 1123db3 (fix: Phase C — Evidence extraction and synthesis (#4))
=======
"""Tests for the orchestrator."""

import os
>>>>>>> 10d6757 (fix: Phase D — Manuscript production and quality control (#5))
=======
"""Tests for the orchestrator."""

import os
>>>>>>> 3eda405 (fix: Phase E — Reliability, Git integration and release (#6))

import pytest

from researcher_support_agent.orchestrator import (
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
    Orchestrator,
    OrchestratorState,
    PhaseResult,
    Status,
)

# ── Dummy phase for testing ──────────────────────────────────────────


class DummyPhase:
    """A test phase that can be configured to succeed or fail."""

    def __init__(
        self,
        name: str,
        should_fail: bool = False,
        fail_count: int = 0,
        artifacts: dict | None = None,
    ):
        self.name = name
        self._should_fail = should_fail
        self._fail_count = fail_count
        self._current_failures = 0
        self._artifacts = artifacts or {}

    def execute(self, state, **kwargs):
        if self._should_fail and self._current_failures < self._fail_count:
            self._current_failures += 1
            raise RuntimeError(f"Simulated failure #{self._current_failures}")
        return PhaseResult(
            phase=self.name,
            status=Status.COMPLETED,
            artifacts=self._artifacts,
        )


# ── Tests ────────────────────────────────────────────────────────────


class TestPhaseResult:
    def test_defaults(self):
        r = PhaseResult(phase="test")
        assert r.status == Status.COMPLETED

    def test_failed(self):
        r = PhaseResult(phase="test", status=Status.FAILED, error="boom")
        assert r.status == Status.FAILED
        assert r.error == "boom"

    def test_serialization(self):
        r = PhaseResult(
            phase="search",
            status=Status.COMPLETED,
            artifacts={"papers": ["p1"]},
        )
        d = r.model_dump()
        assert d["phase"] == "search"
        assert d["artifacts"] == {"papers": ["p1"]}


class TestOrchestratorState:
    def test_save_and_load(self, tmp_dir: Path):
        state = OrchestratorState(project_id="proj-1")
        path = tmp_dir / "state.json"
        state.save_state(path)
        loaded = OrchestratorState.load_state(path)
        assert loaded.project_id == "proj-1"

    def test_save_load_preserves_phase_results(self, tmp_dir: Path):
        state = OrchestratorState()
        state.save_phase_result(PhaseResult(phase="search", status=Status.COMPLETED))
        path = tmp_dir / "state.json"
        state.save_state(path)
        loaded = OrchestratorState.load_state(path)
        result = loaded.get_phase_result("search")
        assert result is not None
        assert result.status == Status.COMPLETED

    def test_phase_has_artifact(self):
        state = OrchestratorState()
        state.save_phase_result(
            PhaseResult(phase="search", artifacts={"papers": ["p1"]})
        )
        assert state.phase_has_artifact("search", "papers")
        assert not state.phase_has_artifact("search", "missing")
        assert not state.phase_has_artifact("unknown", "papers")

    def test_checkpoint_roundtrip(self, tmp_dir: Path):
        state = OrchestratorState()
        state.checkpoint({"key": "value"})
        path = tmp_dir / "state.json"
        state.save_state(path)
        loaded = OrchestratorState.load_state(path)
        assert len(loaded.checkpoints) == 1
        assert loaded.checkpoints[0].metadata.get("key") == "value"


class TestOrchestrator:
    def test_register_and_run_phase(self):
        phase = DummyPhase(name="search")
        orch = Orchestrator([phase])
        result = orch.run_phase("search")
        assert result.status == Status.COMPLETED
        assert result.phase == "search"

    def test_unknown_phase_raises(self):
        orch = Orchestrator([])
        with pytest.raises(ValueError, match="Unknown phase"):
            orch.run_phase("nonexistent")

    def test_retry_on_failure(self):
        phase = DummyPhase(name="search", should_fail=True, fail_count=1)
        orch = Orchestrator([phase], max_retries=3)
        result = orch.run_phase("search")
        assert result.status == Status.COMPLETED

    def test_retry_exhausted_raises(self):
        phase = DummyPhase(name="search", should_fail=True, fail_count=10)
        orch = Orchestrator([phase], max_retries=2)
        with pytest.raises(RuntimeError):
            orch.run_phase("search")

    def test_skip_completed_phase(self):
        phase = DummyPhase(name="search")
        orch = Orchestrator([phase])
        r1 = orch.run_phase("search")
        assert r1.status == Status.COMPLETED
        # Run again — should be skipped
        r2 = orch.run_phase("search")
        assert r2.status == Status.COMPLETED

    def test_run_full(self):
        p1 = DummyPhase(name="search")
        p2 = DummyPhase(name="synthesize")
        orch = Orchestrator([p1, p2])
        results = orch.run_full()
        assert "search" in results
        assert "synthesize" in results
        assert len(results) == 2

    def test_run_from(self):
        p1 = DummyPhase(name="search")
        p2 = DummyPhase(name="synthesize")
        p3 = DummyPhase(name="write")
        orch = Orchestrator([p1, p2, p3])
        # Skip search (already completed)
        orch.run_phase("search")
        # Run from synthesize
        results = orch.run_from("synthesize")
        assert "search" in results
        assert "synthesize" in results
        assert "write" in results

    def test_state_persistence(self, tmp_dir: Path):
        p1 = DummyPhase(name="search")
        state_path = str(tmp_dir / "state.json")
        orch = Orchestrator([p1], state_path=state_path)
        orch.run_phase("search")
        assert Path(state_path).exists()

    def test_resume_from_checkpoint(self):
        p1 = DummyPhase(name="search")
        orch = Orchestrator([p1])
        orch.run_full()
        # One checkpoint created after the single phase
        assert len(orch.state.checkpoints) >= 1

    def test_run_from_invalid_phase_raises(self):
        orch = Orchestrator([DummyPhase(name="a")])
        with pytest.raises(ValueError, match="Unknown phase"):
            orch.run_from("nonexistent")
=======
=======
>>>>>>> 1123db3 (fix: Phase C — Evidence extraction and synthesis (#4))
    Phase,
    PhaseState,
    Orchestrator,
    OrchestratorState,
=======
=======
>>>>>>> 3eda405 (fix: Phase E — Reliability, Git integration and release (#6))
    Orchestrator,
    OrchestratorState,
    Phase,
    PhaseState,
<<<<<<< HEAD
>>>>>>> 10d6757 (fix: Phase D — Manuscript production and quality control (#5))
=======
>>>>>>> 3eda405 (fix: Phase E — Reliability, Git integration and release (#6))
)


class TestOrchestratorState:
    def test_default_state(self):
        s = OrchestratorState(project_id="test")
        assert s.project_id == "test"
        assert s.phases == {}

    def test_set_and_check_phase(self):
        s = OrchestratorState(project_id="test")
        s.set_phase(Phase.PLAN, PhaseState.COMPLETED)
        assert s.is_phase_done(Phase.PLAN)
        assert not s.is_phase_done(Phase.SEARCH)

    def test_serialization(self):
        s = OrchestratorState(
            project_id="test",
            phases={Phase.PLAN.value: PhaseState.COMPLETED},
        )
        data = s.model_dump()
        s2 = OrchestratorState(**data)
        assert s2.project_id == s.project_id
        assert s2.is_phase_done(Phase.PLAN)


class TestOrchestrator:
    def test_dry_run(self, tmp_dir):
        sf = os.path.join(tmp_dir, "state.json")
        orch = Orchestrator(state_file=sf)
        result = orch.dry_run()
        assert result[Phase.PLAN.value] is False

    def test_run_phase_success(self, tmp_dir):
        sf = os.path.join(tmp_dir, "state.json")
        orch = Orchestrator(state_file=sf)
        executed = []

        def handler(phase, state):
            executed.append(phase)

        orch.run_phase(Phase.PLAN, handler)
        assert Phase.PLAN in executed
        assert orch.state.is_phase_done(Phase.PLAN)

    def test_run_phase_failure(self, tmp_dir):
        sf = os.path.join(tmp_dir, "state.json")
        orch = Orchestrator(state_file=sf, max_retries=1)

        def handler(phase, state):
            raise RuntimeError("test error")

        with pytest.raises(RuntimeError):
            orch.run_phase(Phase.PLAN, handler)
        assert orch.state.phases.get(Phase.PLAN) == PhaseState.FAILED

    def test_state_persistence(self, tmp_dir):
        sf = os.path.join(tmp_dir, "state.json")
        orch1 = Orchestrator(state_file=sf)
        orch1.run_phase(Phase.PLAN, lambda *a: None)

<<<<<<< HEAD
<<<<<<< HEAD
        # Reload from file
=======
>>>>>>> 10d6757 (fix: Phase D — Manuscript production and quality control (#5))
=======
>>>>>>> 3eda405 (fix: Phase E — Reliability, Git integration and release (#6))
        orch2 = Orchestrator(state_file=sf)
        assert orch2.state.is_phase_done(Phase.PLAN)

    def test_skip_done_phases(self, tmp_dir):
        sf = os.path.join(tmp_dir, "state.json")
        orch = Orchestrator(state_file=sf)
        orch.run_phase(Phase.PLAN, lambda *a: None)

        remaining = orch._get_phase_order()
        assert Phase.PLAN not in remaining
        assert Phase.SEARCH in remaining
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
>>>>>>> e45cda7 (fix: Phase B — Literature discovery and ingestion (#3))
=======
>>>>>>> 1123db3 (fix: Phase C — Evidence extraction and synthesis (#4))
=======
>>>>>>> 10d6757 (fix: Phase D — Manuscript production and quality control (#5))
=======
>>>>>>> 3eda405 (fix: Phase E — Reliability, Git integration and release (#6))
