"""Tests for the research planner agent."""

from researcher_support_agent.agents.research_planner import (
    ResearchPlannerConfig,
    build_research_plan,
    generate_research_questions,
)
from researcher_support_agent.models.research_plan import ResearchPlan


class TestResearchQuestions:
    def test_generate_questions(self):
        questions = generate_research_questions("deep learning")
        assert len(questions) > 0
        for q in questions:
            assert q.question
            assert "deep learning" in q.question.lower()

    def test_max_questions_limit(self):
        questions = generate_research_questions(
            "test", config=ResearchPlannerConfig(max_questions=1)
        )
        assert len(questions) == 1

    def test_questions_have_fields(self):
        questions = generate_research_questions("test")
        q = questions[0]
        assert q.search_terms
        assert q.synonyms
        assert isinstance(q.inclusion_criteria, list)
        assert isinstance(q.exclusion_criteria, list)

    def test_custom_criteria(self):
        config = ResearchPlannerConfig(
            max_questions=1,
            default_inclusion_criteria=["peer-reviewed", "english"],
            default_exclusion_criteria=["conference only"],
        )
        questions = generate_research_questions("test", config)
        q = questions[0]
        assert "peer-reviewed" in q.inclusion_criteria


class TestResearchPlan:
    def test_build_plan(self):
        plan = build_research_plan(
            topic="Climate Change",
            project_id="proj-1",
            config=ResearchPlannerConfig(max_questions=2),
        )
        assert plan.project_id == "proj-1"
        assert plan.topic == "Climate Change"
        assert len(plan.research_questions) == 2
        assert plan.protocol_approved is False
        assert plan.approval is None

    def test_plan_format_is_structured(self):
        """Acceptance: outputs a validated research plan in a stable format,
        rather than an unstructured paragraph."""
        plan = build_research_plan(topic="AI", project_id="p1")
        data = plan.model_dump()
        assert isinstance(data["research_questions"], list)
        for rq in data["research_questions"]:
            assert isinstance(rq["search_terms"], list)
            assert isinstance(rq["synonyms"], dict)

    def test_approve(self):
        plan = build_research_plan(topic="test", project_id="p1")
        assert plan.needs_approval() is True
        plan.approve(by="reviewer1", comments="Looks good")
        assert plan.protocol_approved is True
        assert plan.approval is not None
        assert plan.approval.approved_by == "reviewer1"
        assert plan.needs_approval() is False

    def test_approve_updates_timestamp(self):
        import time

        plan = build_research_plan(topic="test", project_id="p1")
        before = plan.updated_at
        time.sleep(0.01)
        plan.approve(by="reviewer1")
        assert plan.updated_at > before


class TestProtocolApproval:
    def test_default_approval(self):
        from researcher_support_agent.models.research_plan import ProtocolApproval

        approval = ProtocolApproval(approved=True, approved_by="user")
        assert approval.comments == ""
