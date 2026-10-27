<<<<<<< HEAD
<<<<<<< HEAD
"""Tests for the research plan models."""

from datetime import datetime, timezone

from researcher_support_agent.models.research_plan import (
    ProtocolApproval,
    ResearchPlan,
    ResearchQuestion,
)
=======
=======
>>>>>>> 3eda405 (fix: Phase E — Reliability, Git integration and release (#6))
"""Tests for research plan model."""


from researcher_support_agent.models.research_plan import ResearchPlan, ResearchQuestion
<<<<<<< HEAD
>>>>>>> 10d6757 (fix: Phase D — Manuscript production and quality control (#5))
=======
>>>>>>> 3eda405 (fix: Phase E — Reliability, Git integration and release (#6))


class TestResearchQuestion:
    def test_minimal(self):
<<<<<<< HEAD
<<<<<<< HEAD
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
            approved=True, approved_by="reviewer", comments="Approved with minor changes"
        )
        assert approval.comments == "Approved with minor changes"
=======
=======
>>>>>>> 3eda405 (fix: Phase E — Reliability, Git integration and release (#6))
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
<<<<<<< HEAD
>>>>>>> 10d6757 (fix: Phase D — Manuscript production and quality control (#5))
=======
>>>>>>> 3eda405 (fix: Phase E — Reliability, Git integration and release (#6))


class TestResearchPlan:
    def test_minimal(self):
<<<<<<< HEAD
<<<<<<< HEAD
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
=======
=======
>>>>>>> 3eda405 (fix: Phase E — Reliability, Git integration and release (#6))
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
<<<<<<< HEAD
>>>>>>> 10d6757 (fix: Phase D — Manuscript production and quality control (#5))
=======
>>>>>>> 3eda405 (fix: Phase E — Reliability, Git integration and release (#6))
