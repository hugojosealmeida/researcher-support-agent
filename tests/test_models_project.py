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
