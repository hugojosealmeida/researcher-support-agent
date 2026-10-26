"""Tests for research plan model."""

from researcher_support_agent.models.research_plan import ResearchPlan, ResearchQuestion


class TestResearchQuestion:
    def test_minimal(self):
        q = ResearchQuestion(question="What is X?")
        assert q.question == "What is X?"

    def test_full(self):
        q = ResearchQuestion(
            question="What is the effect of X on Y?",
            pco="Population: adults, Intervention: X, Comparison: Y",
            inclusion_criteria="RCTs",
            exclusion_criteria="Non-English",
        )
        assert q.question == "What is the effect of X on Y?"
        assert q.inclusion_criteria == "RCTs"


class TestResearchPlan:
    def test_minimal(self):
        p = ResearchPlan(title="Test Review")
        assert p.title == "Test Review"
        assert p.questions == []

    def test_full(self):
        p = ResearchPlan(
            title="Systematic Review",
            questions=[
                ResearchQuestion(question="What is X?"),
            ],
            databases=["PubMed"],
        )
        assert len(p.questions) == 1
        assert "PubMed" in p.databases
