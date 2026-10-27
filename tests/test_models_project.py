"""Tests for project model."""

from researcher_support_agent.models.project import ProjectStatus, ResearchProject


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
