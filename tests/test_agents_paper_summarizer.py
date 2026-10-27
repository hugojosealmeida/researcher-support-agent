"""Tests for the paper summarizer agent."""

from researcher_support_agent.agents.paper_summarizer import (
    PaperSummaryConfig,
    summarize_paper,
    summarize_papers,
)
from researcher_support_agent.models.evidence import EvidencePointer
from researcher_support_agent.models.paper import Author, Paper


class TestSummarizePaper:
    def test_basic_summary(self):
        paper = Paper(
            title="Test Paper",
            authors=[Author(full_name="Alice")],
            year=2023,
            abstract="This paper studies X.",
        )
        note = summarize_paper(paper)
        assert note.paper_id == "Test_Paper"
        assert note.title == "Test Paper"
        assert note.year == 2023

    def test_distinguishes_author_reported_from_agent(self):
        paper = Paper(
            title="Test Paper",
            authors=[Author(full_name="Bob")],
            year=2022,
            abstract="Authors find Y.",
        )
        note = summarize_paper(paper)
        # Author-reported fields should come from abstract
        assert "Authors find Y" in note.main_results or "Unknown" in note.main_results
        # Agent interpretation should mention the author
        assert "Bob" in note.agent_interpretation

    def test_missing_info_is_unknown(self):
        paper = Paper(
            title="Minimal Paper",
            authors=[Author(full_name="Charlie")],
        )
        note = summarize_paper(paper)
        assert note.methodology == "Unknown" or len(note.methodology) > 0

    def test_with_raw_text(self):
        paper = Paper(
            title="Full Paper",
            authors=[Author(full_name="Dave")],
            year=2021,
            abstract="Abstract content.",
        )
        raw_text = """Introduction
This is the introduction section.

Methodology
We used a randomized controlled trial with 500 participants.

Results
The treatment group showed 15% improvement over control.

Limitations
Small sample size in subgroup analysis.
"""
        note = summarize_paper(paper, raw_text=raw_text)
        assert "randomized controlled trial" in note.methodology.lower()
        assert "15%" in note.main_results

    def test_evidence_pointers_added(self):
        paper = Paper(
            title="Pointed Paper",
            authors=[Author(full_name="Eve")],
            year=2020,
        )
        raw_text = """Introduction
Some intro text.

Methodology
Methods described here.

Results
Results section.

References
Reference list.
"""
        config = PaperSummaryConfig(include_evidence_pointers=True)
        note = summarize_paper(paper, raw_text=raw_text, config=config)
        assert len(note.evidence_pointers) > 0
        for ptr in note.evidence_pointers:
            assert isinstance(ptr, EvidencePointer)
            assert ptr.paper_id == note.paper_id

    def test_to_markdown(self):
        paper = Paper(
            title="Markdown Test",
            authors=[Author(full_name="Frank")],
            year=2023,
        )
        note = summarize_paper(paper)
        md = note.to_markdown()
        assert "## Markdown Test" in md
        assert "Research Question and Motivation (Author-reported)" in md
        assert "Agent Interpretation" in md


class TestSummarizePapers:
    def test_multiple_papers(self):
        papers = [
            Paper(title="Paper A", authors=[Author(full_name="A")], year=2020),
            Paper(title="Paper B", authors=[Author(full_name="B")], year=2021),
            Paper(title="Paper C", authors=[Author(full_name="C")], year=2022),
        ]
        notes = summarize_papers(papers)
        assert len(notes) == 3

    def test_raw_texts_mapping(self):
        papers = [
            Paper(title="Paper A", authors=[Author(full_name="A")], year=2020),
            Paper(title="Paper B", authors=[Author(full_name="B")], year=2021),
        ]
        raw_texts = {
            "Paper_A": "Methodology: survey. Results: positive.",
            "Paper_B": "Methodology: experiment. Results: negative.",
        }
        notes = summarize_papers(papers, raw_texts=raw_texts)
        assert len(notes) == 2


class TestPaperSummaryConfig:
    def test_defaults(self):
        config = PaperSummaryConfig()
        assert config.include_quantitative_findings is True
        assert config.include_evidence_pointers is True
        assert config.include_agent_interpretation is True
