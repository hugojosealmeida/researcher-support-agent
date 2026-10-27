"""Tests for the screening agent."""

from researcher_support_agent.agents.screening_agent import ScreeningAgent
from researcher_support_agent.models.paper import Author, Paper
from researcher_support_agent.models.screening import ScreeningDecision


class TestScreeningAgent:
    def test_include_default(self):
        agent = ScreeningAgent()
        paper = Paper(
            title="Test Paper on X",
            authors=[Author(full_name="Alice")],
            year=2023,
        )
        result = agent.screen(paper)
        assert result.decision == ScreeningDecision.INCLUDE

    def test_exclude_with_criteria(self):
        agent = ScreeningAgent(exclusion_criteria="review, meta-analysis")
        paper = Paper(
            title="A Systematic Review of X",
            authors=[Author(full_name="Alice")],
            year=2023,
        )
        result = agent.screen(paper)
        assert result.decision == ScreeningDecision.EXCLUDE
        assert "Excluded" in result.reason

    def test_include_with_exclusion_not_matching(self):
        agent = ScreeningAgent(exclusion_criteria="animal study")
        paper = Paper(
            title="Clinical Trial of X",
            authors=[Author(full_name="Alice")],
            year=2023,
        )
        result = agent.screen(paper)
        assert result.decision == ScreeningDecision.INCLUDE

    def test_screen_batch(self):
        agent = ScreeningAgent()
        papers = [
            Paper(title="Paper A", authors=[Author(full_name="A")]),
            Paper(title="Paper B", authors=[Author(full_name="B")]),
        ]
        results = agent.screen_batch(papers)
        assert len(results) == 2

    def test_include_with_criteria(self):
        agent = ScreeningAgent(inclusion_criteria="randomized")
        paper = Paper(
            title="A Randomized Trial of X",
            authors=[Author(full_name="Alice")],
        )
        result = agent.screen(paper)
        assert result.decision == ScreeningDecision.INCLUDE


class TestScreeningAgentInclusionAndStableId:
    def test_exclude_keyword_in_abstract(self):
        agent = ScreeningAgent(exclusion_criteria="animal")
        paper = Paper(
            title="Clinical Trial of X",
            authors=[Author(full_name="Alice")],
            abstract="This is an animal study.",
        )
        result = agent.screen(paper)
        assert result.decision == ScreeningDecision.EXCLUDE
        assert "Excluded" in result.reason

    def test_inclusion_enforced_when_not_met(self):
        agent = ScreeningAgent(inclusion_criteria="randomized")
        paper = Paper(
            title="Observational Study",
            authors=[Author(full_name="Alice")],
            abstract="No randomization performed.",
        )
        result = agent.screen(paper)
        assert result.decision == ScreeningDecision.EXCLUDE

    def test_inclusion_in_abstract(self):
        agent = ScreeningAgent(inclusion_criteria="randomized")
        paper = Paper(
            title="Trial",
            authors=[Author(full_name="Alice")],
            abstract="A randomized controlled trial.",
        )
        result = agent.screen(paper)
        assert result.decision == ScreeningDecision.INCLUDE

    def test_paper_id_uses_stable_identifier(self):
        agent = ScreeningAgent()
        paper = Paper(
            title="Test Paper",
            authors=[Author(full_name="Alice")],
            doi="10.1234/test",
        )
        result = agent.screen(paper)
        assert result.paper_id == "10.1234/test"

    def test_paper_id_falls_back_to_title_slug(self):
        agent = ScreeningAgent()
        paper = Paper(
            title="Test Paper",
            authors=[Author(full_name="Alice")],
        )
        result = agent.screen(paper)
        assert result.paper_id == "Test_Paper"
