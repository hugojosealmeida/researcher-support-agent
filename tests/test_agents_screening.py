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
