"""Tests for the research planner agent."""

from researcher_support_agent.agents.research_planner import ResearchPlanner
from researcher_support_agent.models.research_plan import ResearchQuestion


class TestResearchPlanner:
    def test_plan(self):
        planner = ResearchPlanner()
        questions = [
            ResearchQuestion(
                question="What is the effect of X on Y?",
                inclusion_criteria="Randomized controlled trials",
            ),
        ]
        plan = planner.plan("Effect of X on Y", questions)
        assert plan.title == "Systematic Review: Effect of X on Y"
        assert len(plan.questions) == 1
        assert len(plan.search_strings) > 0
        assert "PubMed" in plan.databases

    def test_search_string_generation(self):
        planner = ResearchPlanner()
        questions = [
            ResearchQuestion(question="What is X and Y?"),
        ]
        plan = planner.plan("Test", questions)
        assert len(plan.search_strings) == 1
        search = plan.search_strings[0]
        assert "AND" in search
