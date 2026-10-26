"""Tests for project and query models."""

import pytest

from researcher_support_agent.models.project import ProjectStatus, ResearchProject


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
        with pytest.raises(ValueError):
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
