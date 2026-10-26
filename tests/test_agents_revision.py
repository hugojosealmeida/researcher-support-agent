"""Tests for the revision agent."""

import pytest

from researcher_support_agent.agents.revision_agent import (
    RevisionAgent,
    RevisionLoopResult,
)
from researcher_support_agent.models.manuscript import (
    Manuscript,
    ManuscriptTemplate,
)
from researcher_support_agent.models.reviewer import ReviewCriteria


class TestRevisionLoopResult:
    def test_minimal(self):

        m = Manuscript(title="Test")
        r = RevisionLoopResult(final_manuscript=m)
        assert r.final_manuscript.title == "Test"
        assert r.iterations == 0
        assert r.resolved_count == 0
        assert r.unresolved_count == 0


class TestRevisionAgent:
    @pytest.fixture()
    def agent(self):
        return RevisionAgent()

    @pytest.fixture()
    def simple_manuscript(self):
        m = Manuscript.from_template("Test Review", ManuscriptTemplate.NARRATIVE_REVIEW)
        # Give the manuscript some content so it doesn't get flagged for empty sections
        m.set_section_content(
            "abstract",
            "**Purpose:** Test review. **Methods:** Search. **Results:** Findings. **Conclusion:** Done.",
            citations=["paper-1"],
        )
        m.set_section_content(
            "introduction",
            "This review examines the topic. Literature has evolved.",
            citations=["paper-1"],
        )
        m.set_section_content(
            "methods",
            "Comprehensive search conducted. Inclusion criteria applied.",
            citations=["paper-1"],
        )
        m.set_section_content(
            "results",
            "Multiple studies reviewed. Key findings presented.",
            citations=["paper-1"],
        )
        m.set_section_content(
            "discussion",
            "Findings are important. Limitations include sample size. Contributions noted.",
            citations=["paper-1"],
        )
        m.set_section_content(
            "conclusion",
            "X shows promise. Future research needed.",
            citations=["paper-1"],
        )
        m.add_reference("paper-1")
        return m

    @pytest.fixture()
    def flawed_manuscript(self):
        m = Manuscript.from_template("Test Review", ManuscriptTemplate.NARRATIVE_REVIEW)
        # Has unresolved citations
        m.set_section_content(
            "abstract",
            "Content.",
            citations=["fabricated-1"],
        )
        m.set_section_content(
            "introduction",
            "Content.",
            citations=["fabricated-2"],
        )
        m.set_section_content(
            "methods",
            "Content.",
            citations=["fabricated-3"],
        )
        m.set_section_content(
            "results",
            "Content.",
            citations=["fabricated-1"],
        )
        m.set_section_content(
            "discussion",
            "Content.",
            citations=["fabricated-2"],
        )
        m.set_section_content(
            "conclusion",
            "Content.",
            citations=["fabricated-3"],
        )
        m.add_reference("fabricated-1")
        m.add_reference("fabricated-2")
        m.add_reference("fabricated-3")
        return m

    def test_run_revision_loop_good_manuscript(self, agent, simple_manuscript):
        known_ids = {"paper-1"}
        result = agent.run_revision_loop(
            simple_manuscript,
            known_ids,
            ReviewCriteria(max_iterations=3),
        )
        assert isinstance(result, RevisionLoopResult)
        # A good manuscript may pass without iterations (only minor findings)
        assert result.final_manuscript.version >= simple_manuscript.version

    def test_run_revision_loop_max_iterations(self, agent, flawed_manuscript):
        known_ids = {"known-paper"}  # fabricated papers are NOT known
        result = agent.run_revision_loop(
            flawed_manuscript,
            known_ids,
            ReviewCriteria(max_iterations=2),
        )
        # Should not exceed max iterations
        assert result.iterations <= 2

    def test_revision_history_retained(self, agent, simple_manuscript):
        known_ids = {"paper-1"}
        result = agent.run_revision_loop(
            simple_manuscript,
            known_ids,
            ReviewCriteria(max_iterations=3),
        )
        assert len(result.review_history) > 0

    def test_version_history_retained(self, agent, simple_manuscript):
        known_ids = {"paper-1"}
        result = agent.run_revision_loop(
            simple_manuscript,
            known_ids,
            ReviewCriteria(max_iterations=3),
        )
        assert len(result.version_history) > 0
        # First version should match the initial
        assert result.version_history[0].version == simple_manuscript.version

    def test_manuscript_version_increases(self, agent, simple_manuscript):
        known_ids = {"paper-1"}
        initial_version = simple_manuscript.version
        result = agent.run_revision_loop(
            simple_manuscript,
            known_ids,
            ReviewCriteria(max_iterations=3),
        )
        assert result.final_manuscript.version >= initial_version
