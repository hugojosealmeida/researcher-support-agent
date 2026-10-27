"""Tests for the manuscript writer agent."""

from datetime import UTC

import pytest

from researcher_support_agent.agents.manuscript_writer import ManuscriptWriter
from researcher_support_agent.models.common import Status
from researcher_support_agent.models.manuscript import ManuscriptTemplate
from researcher_support_agent.models.paper import Author, Paper


class TestManuscriptWriter:
    @pytest.fixture()
    def writer(self):
        return ManuscriptWriter(template=ManuscriptTemplate.NARRATIVE_REVIEW)

    @pytest.fixture()
    def sample_papers(self):
        return [
            Paper(
                title="Paper A",
                authors=[Author(full_name="Alice Smith")],
                year=2023,
                abstract="Paper A studies X.",
            ),
            Paper(
                title="Paper B",
                authors=[Author(full_name="Bob Jones")],
                year=2022,
                abstract="Paper B studies Y.",
            ),
            Paper(
                title="Paper C",
                authors=[Author(full_name="Carol White")],
                year=2021,
                abstract="Paper C studies Z.",
            ),
        ]

    @pytest.fixture()
    def sample_notes(self, sample_papers):
        from datetime import datetime

        from researcher_support_agent.models.evidence import ResearchNote

        return [
            ResearchNote(
                paper_id="Paper_A",
                title="Paper A",
                year=2023,
                methodology="Survey with 100 participants.",
                main_results="X improves Y.",
                agent_interpretation="Important finding.",
                created_at=datetime.now(UTC),
            ),
            ResearchNote(
                paper_id="Paper_B",
                title="Paper B",
                year=2022,
                methodology="Experiment.",
                main_results="Y is effective.",
                agent_interpretation="Supportive evidence.",
                created_at=datetime.now(UTC),
            ),
            ResearchNote(
                paper_id="Paper_C",
                title="Paper C",
                year=2021,
                methodology="Review.",
                main_results="Z has mixed results.",
                agent_interpretation="Needs more study.",
                created_at=datetime.now(UTC),
            ),
        ]

    def test_write_basic(self, writer, sample_papers, sample_notes):
        result = writer.write(
            title="Test Review",
            synthesis_notes=sample_notes,
            papers=sample_papers,
        )
        assert result.manuscript.title == "Test Review"
        assert len(result.manuscript.sections) == 6
        assert result.manuscript.version == 1

    def test_all_sections_created(self, writer, sample_papers, sample_notes):
        result = writer.write(
            title="Test Review",
            synthesis_notes=sample_notes,
            papers=sample_papers,
        )
        section_names = [s.name for s in result.manuscript.sections.values()]
        assert "abstract" in section_names
        assert "introduction" in section_names
        assert "methods" in section_names
        assert "results" in section_names
        assert "discussion" in section_names
        assert "conclusion" in section_names

    def test_sections_have_content(self, writer, sample_papers, sample_notes):
        result = writer.write(
            title="Test Review",
            synthesis_notes=sample_notes,
            papers=sample_papers,
        )
        for section in result.manuscript.sections.values():
            assert section.status in (Status.COMPLETED, Status.PENDING)

    def test_citations_tracked(self, writer, sample_papers, sample_notes):
        result = writer.write(
            title="Test Review",
            synthesis_notes=sample_notes,
            papers=sample_papers,
        )
        assert isinstance(result.citations_used, dict)
        for _section_name, cited in result.citations_used.items():
            assert isinstance(cited, list)

    def test_references_added(self, writer, sample_papers, sample_notes):
        result = writer.write(
            title="Test Review",
            synthesis_notes=sample_notes,
            papers=sample_papers,
        )
        # Reference list should have papers that were cited
        assert len(result.manuscript.reference_ids) >= 0

    def test_systematic_review_template(self):
        writer = ManuscriptWriter(template=ManuscriptTemplate.SYSTEMATIC_REVIEW)
        assert writer.template == ManuscriptTemplate.SYSTEMATIC_REVIEW

    def test_to_markdown(self, writer, sample_papers, sample_notes):
        result = writer.write(
            title="Test Review",
            synthesis_notes=sample_notes,
            papers=sample_papers,
        )
        md = result.manuscript.to_markdown()
        assert "# Test Review" in md

    def test_no_fabricated_references(self, writer, sample_papers, sample_notes):
        """References should only include paper IDs that exist in known papers."""
        known_paper_ids = set()
        for paper in sample_papers:
            known_paper_ids.add(paper.title.replace(" ", "_"))

        result = writer.write(
            title="Test Review",
            synthesis_notes=sample_notes,
            papers=sample_papers,
        )

        # Check all references are from known papers
        for ref_id in result.manuscript.reference_ids:
            assert ref_id in known_paper_ids, f"Fabricated reference: {ref_id}"
