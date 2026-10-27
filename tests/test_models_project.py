<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
"""Tests for project models: ResearchProject, ResearchQuestion."""

import json

import pytest

from researcher_support_agent.models import (
    ResearchProject,
    ResearchQuestion,
    Status,
)


class TestResearchQuestion:
    def test_valid_creation(self):
        q = ResearchQuestion(question="What is X?")
        assert q.question == "What is X?"
        assert q.status == Status.PENDING

    def test_empty_question_raises(self):
        with pytest.raises(ValueError):
            ResearchQuestion(question="")

    def test_whitespace_question_raises(self):
        with pytest.raises(ValueError):
            ResearchQuestion(question="   ")

    def test_serialization(self):
        q = ResearchQuestion(
            question="What is X?",
            inclusion_criteria=["A", "B"],
            metadata={"custom": 42},
        )
        data = json.loads(q.model_dump_json())
        assert data["question"] == "What is X?"
        assert data["inclusion_criteria"] == ["A", "B"]


class TestResearchProject:
    def test_valid_creation(self):
        p = ResearchProject(title="My Project", description="A test project")
        assert p.title == "My Project"
        assert p.status == Status.PENDING

    def test_empty_title_raises(self):
        with pytest.raises(ValueError):
            ResearchProject(title="")

    def test_add_question(self):
        p = ResearchProject(title="Project")
        q = ResearchQuestion(question="Q1?")
        p.add_question(q)
        assert len(p.questions) == 1
        assert p.questions[0].question == "Q1?"

    def test_set_status(self):
        p = ResearchProject(title="Project")
        p.set_status(Status.COMPLETED)
        assert p.status == Status.COMPLETED

    def test_update(self):
        p = ResearchProject(title="Project")
        p.update(description="Updated")
        assert p.description == "Updated"

    def test_full_serialization(self):
        p = ResearchProject(
            title="Test Project",
            description="Desc",
            questions=[ResearchQuestion(question="Q1?")],
        )
        data = json.loads(p.model_dump_json())
        assert data["title"] == "Test Project"
        assert len(data["questions"]) == 1
=======
=======
>>>>>>> 1123db3 (fix: Phase C — Evidence extraction and synthesis (#4))
"""Tests for project and query models."""

import pytest
=======
"""Tests for project model."""

>>>>>>> 10d6757 (fix: Phase D — Manuscript production and quality control (#5))
=======
"""Tests for project model."""

>>>>>>> 3eda405 (fix: Phase E — Reliability, Git integration and release (#6))

from researcher_support_agent.models.project import ProjectStatus, ResearchProject


<<<<<<< HEAD
<<<<<<< HEAD
class TestProjectStatus:
    def test_status_values(self):
        assert ProjectStatus.DRAFT.value == "draft"
        assert ProjectStatus.ACTIVE.value == "active"
        assert ProjectStatus.COMPLETED.value == "completed"
        assert ProjectStatus.ARCHIVED.value == "archived"


class TestResearchProject:
    def test_default_status(self):
        p = ResearchProject(title="Test")
        assert p.status == ProjectStatus.DRAFT

    def test_set_status(self):
        p = ResearchProject(title="Test", status=ProjectStatus.ACTIVE)
        assert p.status == ProjectStatus.ACTIVE

    def test_serialization_roundtrip(self):
        p = ResearchProject(
            title="Test",
            description="A test project",
            questions=["Q1", "Q2"],
            status=ProjectStatus.ACTIVE,
        )
        data = p.model_dump()
        p2 = ResearchProject(**data)
        assert p2.title == p.title
        assert p2.questions == p.questions
        assert p2.status == p.status

    def test_validation_rejects_empty_title(self):
        with pytest.raises(Exception):
            ResearchProject(title="")

    def test_validation_rejects_empty_description(self):
        p = ResearchProject(title="Test", description="")
        assert p.description == ""  # description is optional with default

    def test_timestamps_auto_populated(self):
        p = ResearchProject(title="Test")
        assert p.created_at is not None
        assert p.updated_at is not None

    def test_questions_default_empty(self):
        p = ResearchProject(title="Test")
        assert p.questions == []
<<<<<<< HEAD
>>>>>>> e45cda7 (fix: Phase B — Literature discovery and ingestion (#3))
=======
>>>>>>> 1123db3 (fix: Phase C — Evidence extraction and synthesis (#4))
=======
=======
>>>>>>> 3eda405 (fix: Phase E — Reliability, Git integration and release (#6))
class TestResearchProject:
    def test_minimal(self):
        p = ResearchProject(title="Test Project")
        assert p.title == "Test Project"
        assert p.status == ProjectStatus.ACTIVE

    def test_with_description(self):
        p = ResearchProject(title="Test", description="A test project")
        assert p.description == "A test project"

    def test_status_values(self):
        assert ProjectStatus.ACTIVE == "active"
        assert ProjectStatus.COMPLETED == "completed"
<<<<<<< HEAD
>>>>>>> 10d6757 (fix: Phase D — Manuscript production and quality control (#5))
=======
>>>>>>> 3eda405 (fix: Phase E — Reliability, Git integration and release (#6))
