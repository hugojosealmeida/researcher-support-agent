"""Tests for the literature synthesis agent."""

import pytest

from researcher_support_agent.agents.literature_synthesis import (
    LiteratureSynthesisAgent,
    SynthesisFindingType,
)
from researcher_support_agent.models.evidence import ResearchNote


def _make_notes(years):
    notes = []
    for i, year in enumerate(years):
        notes.append(
            ResearchNote(
                paper_id=f"paper-{i}",
                title=f"Paper {i}",
                year=year,
                main_results=f"Result {i}",
                methodology=f"Method {i}",
            )
        )
    return notes


class TestIdentifyGaps:
    def test_temporal_gap_with_search_metadata(self):
        agent = LiteratureSynthesisAgent()
        notes = _make_notes([2018, 2023])
        search_metadata = {
            "queries": ["machine learning"],
            "sources": ["openalex", "crossref"],
        }
        gaps = agent._identify_gaps(notes, search_metadata)
        assert len(gaps) == 1
        gap = gaps[0]
        assert gap["title"] == "Temporal gap between 2018 and 2023"
        assert gap["confidence"] == 0.4
        assert "machine learning" in gap["evidence_base"] or "openalex" in gap["evidence_base"]
        assert "No papers found" in gap["description"]

    def test_temporal_gap_without_search_metadata(self):
        agent = LiteratureSynthesisAgent()
        notes = _make_notes([2018, 2023])
        gaps = agent._identify_gaps(notes, None)
        assert len(gaps) == 1
        gap = gaps[0]
        assert gap["title"] == "Potential temporal gap between 2018 and 2023"
        assert gap["confidence"] == 0.2
        assert "NOT established" in gap["description"] or "not be treated as established" in gap["evidence_base"]
        assert "WARNING" in gap["evidence_base"]

    def test_no_gap_when_years_adjacent(self):
        agent = LiteratureSynthesisAgent()
        notes = _make_notes([2020, 2021, 2022])
        gaps = agent._identify_gaps(notes, {"queries": ["q"], "sources": ["s"]})
        assert gaps == []

    def test_no_gap_with_single_year(self):
        agent = LiteratureSynthesisAgent()
        notes = _make_notes([2020])
        gaps = agent._identify_gaps(notes, None)
        assert gaps == []

    def test_gap_not_nameerror_with_search_metadata(self):
        # Regression: previously referenced undefined has_search_metadata
        agent = LiteratureSynthesisAgent()
        notes = _make_notes([2015, 2020])
        # Should not raise
        gaps = agent._identify_gaps(notes, {"queries": [], "sources": []})
        assert len(gaps) == 1

    def test_synthesize_includes_gap_finding(self):
        agent = LiteratureSynthesisAgent()
        notes = _make_notes([2018, 2023])
        result = agent.synthesize(notes, [], search_metadata={"queries": ["q"], "sources": ["s"]})
        gap_findings = [f for f in result.findings if f.finding_type == SynthesisFindingType.GAP]
        assert len(gap_findings) >= 1


class TestContradictions:
    def test_same_results_not_contradiction(self):
        agent = LiteratureSynthesisAgent()
        notes = [
            ResearchNote(paper_id="p1", title="P1", main_results="X improves Y", methodology="survey"),
            ResearchNote(paper_id="p2", title="P2", main_results="X improves Y", methodology="experiment"),
        ]
        contras = agent._find_contradictions(notes)
        assert contras == []

    def test_conflicting_results_flagged(self):
        agent = LiteratureSynthesisAgent()
        notes = [
            ResearchNote(paper_id="p1", title="P1", main_results="Treatment is effective", methodology="survey"),
            ResearchNote(paper_id="p2", title="P2", main_results="Treatment is ineffective", methodology="experiment"),
        ]
        contras = agent._find_contradictions(notes)
        assert len(contras) == 1

    def test_different_methodology_same_results_not_flagged(self):
        agent = LiteratureSynthesisAgent()
        notes = [
            ResearchNote(paper_id="p1", title="P1", main_results="X improves Y", methodology="survey"),
            ResearchNote(paper_id="p2", title="P2", main_results="X improves Y", methodology="experiment"),
        ]
        contras = agent._find_contradictions(notes)
        assert contras == []
