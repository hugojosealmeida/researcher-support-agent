"""Tests for all 8 pipeline agents."""

import importlib.util
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
from research_pipeline.state import (
    Paper,
    PipelineState,
    ReviewComment,
    SearchItem,
    Summary,
)

# ------------------------------------------------------------------ #
#  PlanningAgent                                                       #
# ------------------------------------------------------------------ #


class TestPlanningAgent:
    def test_empty_agent_leaves_state_unchanged(self) -> None:
        agent = PlanningAgent()
        state = PipelineState(topic="Existing")
        result = agent.run(state)
        assert result.topic == "Existing"

    def test_agent_sets_values(self) -> None:
        agent = PlanningAgent(
            topic="Gene Editing",
            research_questions=["Q1?", "Q2?"],
            inclusion_criteria=["peer-reviewed", "post-2015"],
            search_strategy="PubMed + Scopus",
        )
        state = PipelineState()
        result = agent.run(state)
        assert result.topic == "Gene Editing"
        assert result.research_questions == ["Q1?", "Q2?"]
        assert result.inclusion_criteria == ["peer-reviewed", "post-2015"]
        assert result.search_strategy == "PubMed + Scopus"

    def test_agent_merges_with_existing_state(self) -> None:
        state = PipelineState(topic="Old Topic", scope={"year_range": "2010-2020"})
        agent = PlanningAgent(topic="New Topic", scope={"year_range": "2015-2025"})
        result = agent.run(state)
        assert result.topic == "New Topic"
        assert result.scope == {"year_range": "2015-2025"}


# ------------------------------------------------------------------ #
#  LiteratureSearchAgent                                               #
# ------------------------------------------------------------------ #


class TestLiteratureSearchAgent:
    def test_agent_sets_results(self) -> None:
        papers = [
            SearchItem(title="A", authors=["X"], year=2023, venue="J1", doi="1"),
            SearchItem(title="B", authors=["Y"], year=2024, venue="J2"),
        ]
        agent = LiteratureSearchAgent(search_results=papers)
        state = PipelineState()
        result = agent.run(state)
        assert len(result.search_results) == 2
        assert result.search_results[0].doi == "1"

    def test_agent_sets_excluded(self) -> None:
        excluded = [SearchItem(title="X", authors=[], year=2020, venue="Bad")]
        agent = LiteratureSearchAgent(excluded_papers=excluded)
        state = PipelineState()
        result = agent.run(state)
        assert len(result.excluded_papers) == 1

    def test_agent_preserves_existing_search_results(self) -> None:
        state = PipelineState(
            search_results=[SearchItem(title="Old", authors=[], year=2019, venue="V")]
        )
        agent = LiteratureSearchAgent()
        result = agent.run(state)
        assert len(result.search_results) == 1
        assert result.search_results[0].title == "Old"


# ------------------------------------------------------------------ #
#  PaperIngestionAgent                                                 #
# ------------------------------------------------------------------ #


class TestPaperIngestionAgent:
    def test_agent_sets_papers(self) -> None:
        papers = [
            Paper(
                title="Paper A", authors=["A"], year=2023, venue="J", md_path="/a.md"
            ),
        ]
        agent = PaperIngestionAgent(papers=papers)
        state = PipelineState()
        result = agent.run(state)
        assert len(result.papers) == 1
        assert result.papers[0].md_path == "/a.md"

    def test_empty_agent(self) -> None:
        state = PipelineState(
            papers=[Paper(title="Existing", authors=[], year=2023, venue="V")]
        )
        result = PaperIngestionAgent().run(state)
        assert len(result.papers) == 1


# ------------------------------------------------------------------ #
#  PaperSummarizationAgent                                             #
# ------------------------------------------------------------------ #


class TestPaperSummarizationAgent:
    def test_agent_sets_summaries(self) -> None:
        summaries = [
            Summary(
                title="A",
                doi="1",
                key_findings=["F1", "F2"],
                methods=["M1"],
                limitations=["L1"],
            ),
        ]
        agent = PaperSummarizationAgent(summaries=summaries)
        state = PipelineState()
        result = agent.run(state)
        assert len(result.summaries) == 1
        assert result.summaries[0].key_findings == ["F1", "F2"]

    def test_empty_agent(self) -> None:
        state = PipelineState(summaries=[Summary(title="Existing")])
        result = PaperSummarizationAgent().run(state)
        assert len(result.summaries) == 1


# ------------------------------------------------------------------ #
#  LiteratureSynthesisAgent                                            #
# ------------------------------------------------------------------ #


class TestLiteratureSynthesisAgent:
    def test_agent_sets_synthesis(self) -> None:
        synthesis = {
            "methods_compared": ["RCT", "cohort"],
            "gaps": ["no longitudinal data"],
        }
        agent = LiteratureSynthesisAgent(synthesis=synthesis)
        state = PipelineState()
        result = agent.run(state)
        assert result.synthesis["gaps"] == ["no longitudinal data"]

    def test_empty_agent(self) -> None:
        state = PipelineState(synthesis={"existing": True})
        result = LiteratureSynthesisAgent().run(state)
        assert result.synthesis == {"existing": True}


# ------------------------------------------------------------------ #
#  ReviewPaperWriterAgent                                              #
# ------------------------------------------------------------------ #


class TestReviewPaperWriterAgent:
    def test_agent_sets_manuscript(self) -> None:
        manuscript = "# Introduction\n\nSome text..."
        agent = ReviewPaperWriterAgent(manuscript=manuscript)
        state = PipelineState()
        result = agent.run(state)
        assert result.manuscript == manuscript

    def test_empty_agent(self) -> None:
        state = PipelineState(manuscript="Existing draft")
        result = ReviewPaperWriterAgent().run(state)
        assert result.manuscript == "Existing draft"


# ------------------------------------------------------------------ #
#  AcademicReviewerAgent                                               #
# ------------------------------------------------------------------ #


class TestAcademicReviewerAgent:
    def test_agent_sets_comments_and_passed(self) -> None:
        comments = [
            ReviewComment(
                section="Abstract", severity="critical", comment="Missing key refs"
            ),
        ]
        agent = AcademicReviewerAgent(comments=comments, passed=False)
        state = PipelineState()
        result = agent.run(state)
        assert len(result.review_comments) == 1
        assert result.review_comments[0].severity == "critical"
        assert result.review_passed is False

    def test_agent_passes(self) -> None:
        agent = AcademicReviewerAgent(passed=True)
        state = PipelineState()
        result = agent.run(state)
        assert result.review_passed is True

    def test_empty_agent(self) -> None:
        state = PipelineState(
            review_comments=[ReviewComment(section="X", severity="minor", comment="o")]
        )
        result = AcademicReviewerAgent().run(state)
        assert len(result.review_comments) == 1


# ------------------------------------------------------------------ #
#  RevisionReleaseAgent                                                #
# ------------------------------------------------------------------ #


class TestRevisionReleaseAgent:
    def test_agent_sets_final(self) -> None:
        agent = RevisionReleaseAgent(
            final_manuscript="Final text",
            version="2.0",
            published=True,
        )
        state = PipelineState()
        result = agent.run(state)
        assert result.final_manuscript == "Final text"
        assert result.version == "2.0"
        assert result.published is True

    def test_empty_agent(self) -> None:
        state = PipelineState(
            final_manuscript="Old final",
            version="1.0",
            published=False,
        )
        result = RevisionReleaseAgent().run(state)
        assert result.final_manuscript == "Old final"
        assert result.version == "1.0"
        assert result.published is False


# ------------------------------------------------------------------ #
#  Persistence ownership (issue #39)                                   #
# ------------------------------------------------------------------ #


ALL_AGENTS = [
    PlanningAgent(topic="T"),
    LiteratureSearchAgent(),
    PaperIngestionAgent(),
    PaperSummarizationAgent(),
    LiteratureSynthesisAgent(),
    ReviewPaperWriterAgent(),
    AcademicReviewerAgent(),
    RevisionReleaseAgent(),
]


class TestAgentsDoNotPersistState:
    """Agents must not write state files; ``Pipeline`` owns persistence
    honouring its configured ``state_file``."""

    @pytest.mark.parametrize("agent", ALL_AGENTS, ids=lambda a: a.name)
    def test_run_writes_no_files(
        self, agent, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        cwd = tmp_path / "cwd"
        cwd.mkdir()
        monkeypatch.chdir(cwd)

        agent.run(PipelineState())

        assert list(cwd.iterdir()) == []


# ------------------------------------------------------------------ #
#  agents package layout (issue #45)                                   #
# ------------------------------------------------------------------ #


class TestAgentsPackageLayout:
    """``research_pipeline.agents`` must resolve to the package only.

    A stale ``agents.py`` module once sat next to the package; it was
    unreachable (packages win over modules during import) and shadowed
    the documented ``PipelineAgent`` re-export. The package now owns
    that public path.
    """

    def test_agents_resolves_to_a_package(self) -> None:
        spec = importlib.util.find_spec("research_pipeline.agents")
        assert spec is not None
        # Packages expose submodule search locations; plain modules do not.
        assert spec.submodule_search_locations is not None

    def test_no_shadowing_agents_module_exists(self) -> None:
        import research_pipeline

        package_dir = Path(research_pipeline.__file__).resolve().parent
        assert not (package_dir / "agents.py").exists()

    def test_pipeline_agent_is_reexported_from_package(self) -> None:
        from research_pipeline.agent_base import PipelineAgent as BaseAgent
        from research_pipeline.agents import PipelineAgent

        assert PipelineAgent is BaseAgent

    def test_package_exports_all_documented_symbols(self) -> None:
        import research_pipeline.agents as agents_pkg

        assert set(agents_pkg.__all__) == {
            "AcademicReviewerAgent",
            "LiteratureSearchAgent",
            "LiteratureSynthesisAgent",
            "PaperIngestionAgent",
            "PaperSummarizationAgent",
            "PipelineAgent",
            "PlanningAgent",
            "ReviewPaperWriterAgent",
            "RevisionReleaseAgent",
        }

    def test_readme_documents_real_file_layout(self) -> None:
        readme = (Path(__file__).resolve().parent.parent / "README.md").read_text(
            encoding="utf-8"
        )
        # The unreachable module must not be documented...
        assert "├── agents.py" not in readme
        # ...while the real locations must be.
        assert "agent_base.py" in readme
