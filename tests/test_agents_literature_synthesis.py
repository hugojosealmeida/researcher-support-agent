"""Tests for the literature synthesis agent."""

from datetime import UTC

import pytest

from researcher_support_agent.agents.literature_synthesis import (
    LiteratureSynthesisAgent,
    SynthesisFinding,
    SynthesisFindingType,
    SynthesisResult,
)
from researcher_support_agent.models.evidence import ResearchNote
from researcher_support_agent.models.paper import Author, Paper


class TestSynthesisFinding:
    def test_minimal(self):
        f = SynthesisFinding(
            finding_type=SynthesisFindingType.CONSENSUS,
            title="Test finding",
            description="Test description",
        )
        assert f.finding_type == SynthesisFindingType.CONSENSUS
        assert f.supporting_paper_ids == []

    def test_to_markdown(self):
        f = SynthesisFinding(
            finding_type=SynthesisFindingType.CONSENSUS,
            title="Consensus on X",
            description="All papers agree on X.",
            supporting_paper_ids=["p1", "p2"],
        )
        md = f.to_markdown()
        assert "Consensus" in md
        assert "p1" in md
        assert "Consensus on X" in md


class TestLiteratureSynthesisAgent:
    @pytest.fixture()
    def agent(self):
        return LiteratureSynthesisAgent()

    @pytest.fixture()
    def sample_notes(self):
        from datetime import datetime
        return [
            ResearchNote(
                paper_id="Paper_A",
                title="Paper A",
                year=2023,
                methodology="Survey",
                main_results="X improves Y.",
                agent_interpretation="Positive effect.",
                open_questions="Generalizability?",
                created_at=datetime.now(UTC),
            ),
            ResearchNote(
                paper_id="Paper_B",
                title="Paper B",
                year=2022,
                methodology="Experiment",
                main_results="X is effective for Z.",
                agent_interpretation="Supportive.",
                created_at=datetime.now(UTC),
            ),
            ResearchNote(
                paper_id="Paper_C",
                title="Paper C",
                year=2021,
                methodology="Review",
                main_results="Mixed results on X.",
                agent_interpretation="Needs more study.",
                open_questions="Under which conditions?",
                created_at=datetime.now(UTC),
            ),
        ]

    def test_synthesize(self, agent, sample_notes):
        papers = [
            Paper(title="Paper A", authors=[Author(full_name="Alice")], year=2023),
            Paper(title="Paper B", authors=[Author(full_name="Bob")], year=2022),
            Paper(title="Paper C", authors=[Author(full_name="Carol")], year=2021),
        ]
        result = agent.synthesize(papers, sample_notes)
        assert isinstance(result, SynthesisResult)
        assert isinstance(result.outline.title, str)

    def test_synthesis_findings(self, agent, sample_notes):
        papers = [
            Paper(title="Paper A", authors=[Author(full_name="Alice")], year=2023),
            Paper(title="Paper B", authors=[Author(full_name="Bob")], year=2022),
        ]
        result = agent.synthesize(papers, sample_notes[:2])
        assert isinstance(result.findings, list)

    def test_synthesis_matrix(self, agent, sample_notes):
        papers = [
            Paper(title="Paper A", authors=[Author(full_name="Alice")], year=2023),
        ]
        result = agent.synthesize(papers, sample_notes[:1])
        assert "Paper A" in result.synthesis_matrix
