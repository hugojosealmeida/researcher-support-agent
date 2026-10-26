"""Tests for the orchestrator."""

import os

import pytest

from researcher_support_agent.orchestrator import (
    Orchestrator,
    OrchestratorState,
    Phase,
    PhaseState,
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

        # Reload from file
        orch2 = Orchestrator(state_file=sf)
        assert orch2.state.is_phase_done(Phase.PLAN)

    def test_skip_done_phases(self, tmp_dir):
        sf = os.path.join(tmp_dir, "state.json")
        orch = Orchestrator(state_file=sf)
        orch.run_phase(Phase.PLAN, lambda *a: None)

        remaining = orch._get_phase_order()
        assert Phase.PLAN not in remaining
        assert Phase.SEARCH in remaining
