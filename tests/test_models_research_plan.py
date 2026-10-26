"""Tests for the research plan models."""


from researcher_support_agent.models.research_plan import (
    ProtocolApproval,
    ResearchPlan,
    ResearchQuestion,
)


class TestResearchQuestion:
    def test_minimal(self):
        rq = ResearchQuestion(question="What is X?")
        assert rq.search_terms == []
        assert rq.synonyms == {}
        assert rq.date_from is None
        assert rq.inclusion_criteria == []

    def test_full(self):
        rq = ResearchQuestion(
            question="What is X?",
            search_terms=["x", "y", "z"],
            synonyms={"x": ["a", "b"]},
            date_from="2020-01-01",
            date_to="2024-12-31",
            inclusion_criteria=["peer-reviewed"],
            exclusion_criteria=["conference"],
        )
        assert rq.date_from == "2020-01-01"
        assert rq.date_to == "2024-12-31"
        assert "peer-reviewed" in rq.inclusion_criteria
        assert "conference" in rq.exclusion_criteria


class TestProtocolApproval:
    def test_minimal(self):
        approval = ProtocolApproval(approved=True, approved_by="reviewer")
        assert approval.approved is True
        assert approval.approved_by == "reviewer"
        assert approval.approved_at is not None

    def test_with_comments(self):
        approval = ProtocolApproval(
            approved=True,
            approved_by="reviewer",
            comments="Approved with minor changes",
        )
        assert approval.comments == "Approved with minor changes"


class TestResearchPlan:
    def test_minimal(self):
        plan = ResearchPlan(project_id="p1", topic="test topic")
        assert plan.project_id == "p1"
        assert plan.topic == "test topic"
        assert plan.research_questions == []
        assert plan.protocol_approved is False
        assert plan.approval is None
        assert plan.created_at is not None
        assert plan.needs_approval() is True

    def test_with_questions(self):
        plan = ResearchPlan(
            project_id="p1",
            topic="test",
            research_questions=[
                ResearchQuestion(question="Q1?", search_terms=["q1"]),
            ],
        )
        assert len(plan.research_questions) == 1
        assert plan.research_questions[0].question == "Q1?"

    def test_approve(self):
        plan = ResearchPlan(project_id="p1", topic="test")
        plan.approve(by="alice", comments="Good plan")
        assert plan.protocol_approved is True
        assert plan.approval is not None
        assert plan.approval.approved_by == "alice"
        assert plan.approval.comments == "Good plan"
        assert plan.needs_approval() is False

    def test_needs_approval_false_after_approve(self):
        plan = ResearchPlan(project_id="p1", topic="test")
        assert plan.needs_approval() is True
        plan.approve(by="alice")
        assert plan.needs_approval() is False

    def test_serialization(self):
        plan = ResearchPlan(
            project_id="p1",
            topic="test",
            research_questions=[
                ResearchQuestion(question="Q1?"),
            ],
        )
        plan.approve(by="reviewer")
        data = plan.model_dump()
        assert data["project_id"] == "p1"
        assert data["topic"] == "test"
        assert data["protocol_approved"] is True
        assert data["approval"]["approved_by"] == "reviewer"
        assert len(data["research_questions"]) == 1

    def test_roundtrip_serialization(self):
        plan = ResearchPlan(
            project_id="p1",
            topic="test",
            research_questions=[
                ResearchQuestion(
                    question="Q1?",
                    search_terms=["test"],
                    synonyms={"test": ["t"]},
                    date_from="2020-01-01",
                    inclusion_criteria=["peer-reviewed"],
                )
            ],
        )
        plan.approve(by="reviewer")
        data = plan.model_dump()
        plan2 = ResearchPlan(**data)
        assert plan2.project_id == plan.project_id
        assert plan2.protocol_approved is True
        assert len(plan2.research_questions) == 1
