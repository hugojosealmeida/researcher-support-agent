"""Tests for the Pipeline orchestrator."""

from pathlib import Path

import pytest

from research_pipeline.agents import (
    AcademicReviewerAgent,
    LiteratureSearchAgent,
    LiteratureSynthesisAgent,
    PaperIngestionAgent,
    PaperSummarizationAgent,
    PlanningAgent,
    ReviewPaperWriterAgent,
    RevisionReleaseAgent,
)
from research_pipeline.pipeline import Pipeline
from research_pipeline.state import (
    PipelineState,
)

# ------------------------------------------------------------------ #
#  Helpers — lightweight agents that just set state for testing        #
# ------------------------------------------------------------------ #


class _DummyAgent:
    """Minimal agent that writes to state for testing."""

    def __init__(self, name: str, *, set_topic: str = "") -> None:
        self.name = name
        self.set_topic = set_topic

    def run(self, state: PipelineState) -> PipelineState:
        if self.set_topic:
            state.topic = self.set_topic
        return state


# ------------------------------------------------------------------ #
#  Tests                                                               #
# ------------------------------------------------------------------ #


class TestPipelineRegistration:
    def test_register_and_run_phase(self, tmp_path: Path) -> None:
        agent = _DummyAgent("planning", set_topic="CRISPR")
        pipeline = Pipeline(state_file=str(tmp_path / "state.json"))
        pipeline.register_agent(agent)

        state = pipeline.run_phase("planning")
        assert state.topic == "CRISPR"
        assert "planning" in state.completed_phases

    def test_unknown_phase_raises(self) -> None:
        pipeline = Pipeline()
        with pytest.raises(ValueError, match="Unknown phase"):
            pipeline.run_phase("nonexistent")

    def test_unregistered_phase_raises(self) -> None:
        pipeline = Pipeline()
        with pytest.raises(RuntimeError, match="No agent registered"):
            pipeline.run_phase("planning")


class TestPipelineFullWorkflow:
    def _build_pipeline(self, state_file: Path) -> Pipeline:
        p = Pipeline(state_file=str(state_file))
        p.register_agent(PlanningAgent(topic="Gene Therapy"))
        p.register_agent(LiteratureSearchAgent())
        p.register_agent(PaperIngestionAgent())
        p.register_agent(PaperSummarizationAgent())
        p.register_agent(LiteratureSynthesisAgent())
        p.register_agent(ReviewPaperWriterAgent())
        p.register_agent(AcademicReviewerAgent())
        p.register_agent(RevisionReleaseAgent())
        return p

    def test_run_full_executes_all_phases(self, tmp_path: Path) -> None:
        p = self._build_pipeline(tmp_path / "state.json")
        result = p.run_full()
        assert result.topic == "Gene Therapy"
        assert result.completed_phases == Pipeline.VALID_PHASES

    def test_run_from_executes_subset(self, tmp_path: Path) -> None:
        p = self._build_pipeline(tmp_path / "state.json")

        # First run planning only
        p.run_phase("planning")
        assert p.state.completed_phases == ["planning"]

        # Then run from paper_summarization onward
        result = p.run_from("paper_summarization")
        remaining = [
            "paper_summarization",
            "literature_synthesis",
            "review_paper_writing",
            "academic_review",
            "revision_release",
        ]
        assert result.completed_phases == ["planning", *remaining]

    def test_run_full_overrides_external_state(self, tmp_path: Path) -> None:
        p = self._build_pipeline(tmp_path / "state.json")
        ext = PipelineState()
        ext.topic = "External"
        ext.completed_phases = ["planning"]

        result = p.run_full(state=ext)
        assert result.topic == "Gene Therapy"  # overwritten by PlanningAgent
        assert result.completed_phases == Pipeline.VALID_PHASES

    def test_run_full_writes_only_configured_state_file(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """State goes to the configured ``state_file`` only — never to a
        hardcoded ``pipeline_state.json`` in the CWD (issue #39)."""
        cwd = tmp_path / "cwd"
        cwd.mkdir()
        monkeypatch.chdir(cwd)
        state_file = tmp_path / "custom.json"

        p = self._build_pipeline(state_file)
        p.run_full()

        assert state_file.exists()
        assert not (cwd / "pipeline_state.json").exists()

    def test_run_phase_writes_only_configured_state_file(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        cwd = tmp_path / "cwd"
        cwd.mkdir()
        monkeypatch.chdir(cwd)
        state_file = tmp_path / "custom.json"

        p = Pipeline(state_file=str(state_file))
        p.register_agent(PlanningAgent(topic="Gene Therapy"))
        p.run_phase("planning")

        assert state_file.exists()
        assert not (cwd / "pipeline_state.json").exists()


class TestPipelineStatePersistence:
    def test_state_saved_after_phase(self, tmp_path: Path) -> None:
        p = Pipeline(state_file=str(tmp_path / "state.json"))
        agent = _DummyAgent("planning", set_topic="Persisted")
        p.register_agent(agent)
        p.run_phase("planning")

        content = (tmp_path / "state.json").read_text()
        assert "Persisted" in content

    def test_ephemeral_pipeline_writes_no_state_file(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """``state_file=None`` means state is ephemeral: nothing hits disk."""
        cwd = tmp_path / "cwd"
        cwd.mkdir()
        monkeypatch.chdir(cwd)

        p = Pipeline(state_file=None)
        p.register_agent(PlanningAgent(topic="Gene Therapy"))
        p.register_agent(LiteratureSearchAgent())
        p.register_agent(PaperIngestionAgent())
        p.register_agent(PaperSummarizationAgent())
        p.register_agent(LiteratureSynthesisAgent())
        p.register_agent(ReviewPaperWriterAgent())
        p.register_agent(AcademicReviewerAgent())
        p.register_agent(RevisionReleaseAgent())
        result = p.run_full()

        assert result.topic == "Gene Therapy"
        assert list(cwd.iterdir()) == []

    def test_state_loaded_into_pipeline(self, tmp_path: Path) -> None:
        # Create initial state file
        initial = PipelineState()
        initial.topic = "LoadedTopic"
        initial.save(str(tmp_path / "state.json"))

        # Load into a new pipeline
        p = Pipeline(state_file=str(tmp_path / "state.json"))
        p.load_state()
        assert p.state.topic == "LoadedTopic"


class TestPipelineStateProperty:
    def test_state_property(self) -> None:
        state = PipelineState(topic="PropTest")
        p = Pipeline(state=state)
        assert p.state.topic == "PropTest"

    def test_state_setter(self) -> None:
        p = Pipeline()
        new_state = PipelineState(topic="New")
        p.state = new_state
        assert p.state.topic == "New"


class TestPipelineSaveState:
    def test_save_state_writes_file(self, tmp_path: Path) -> None:
        p = Pipeline(state_file=str(tmp_path / "state.json"))
        p._state.topic = "SaveTest"
        p.save_state()
        assert (tmp_path / "state.json").exists()
