"""Tests for PipelineState serialization and helpers."""

import json
import pytest
from pathlib import Path

from research_pipeline.state import (
    PipelineState,
    SearchItem,
    Paper,
    Summary,
    ReviewComment,
    _serialize,
    _deserialize,
    _as_dataclass,
)


class TestPipelineStateSaveLoad:
    def test_save_and_load_round_trip(self, tmp_path: Path) -> None:
        state = PipelineState()
        state.topic = "CRISPR in agriculture"
        state.research_questions = ["What are the ethical implications?"]
        state.search_results = [
            SearchItem(
                title="Gene editing crops",
                authors=["A. Smith"],
                year=2023,
                venue="Nature",
                doi="10.1234/test",
                abstract="Test abstract",
            )
        ]
        state.papers = [
            Paper(
                title="Gene editing crops",
                authors=["A. Smith"],
                year=2023,
                venue="Nature",
                doi="10.1234/test",
                md_path="/tmp/test.md",
                content="# Content",
            )
        ]
        state.summaries = [
            Summary(
                title="Gene editing crops",
                doi="10.1234/test",
                key_findings=["Increased yield"],
                methods=["Field trials"],
            )
        ]
        state.review_comments = [
            ReviewComment(
                section="Methods",
                severity="major",
                comment="Need more detail",
                suggested_fix="Add subsection",
            )
        ]
        state.manuscript = "Draft manuscript text"
        state.final_manuscript = "Final manuscript text"
        state.version = "2.0"
        state.published = True
        state.completed_phases = ["planning", "literature_search"]

        fpath = tmp_path / "state.json"
        state.save(fpath)
        loaded = PipelineState.load(fpath)

        assert loaded.topic == "CRISPR in agriculture"
        assert loaded.research_questions == ["What are the ethical implications?"]
        assert len(loaded.search_results) == 1
        assert loaded.search_results[0].title == "Gene editing crops"
        assert loaded.search_results[0].doi == "10.1234/test"
        assert len(loaded.papers) == 1
        assert loaded.papers[0].md_path == "/tmp/test.md"
        assert len(loaded.summaries) == 1
        assert loaded.summaries[0].key_findings == ["Increased yield"]
        assert len(loaded.review_comments) == 1
        assert loaded.review_comments[0].severity == "major"
        assert loaded.manuscript == "Draft manuscript text"
        assert loaded.final_manuscript == "Final manuscript text"
        assert loaded.version == "2.0"
        assert loaded.published is True
        assert "planning" in loaded.completed_phases

    def test_load_nonexistent_returns_empty(self, tmp_path: Path) -> None:
        state = PipelineState.load(tmp_path / "missing.json")
        assert state.topic == ""
        assert state.search_results == []
        assert state.completed_phases == []

    def test_phase_has_data_true(self) -> None:
        state = PipelineState()
        assert state.phase_has_data("planning") is False
        state.topic = "test"
        assert state.phase_has_data("planning") is True

    def test_phase_has_data_false(self) -> None:
        state = PipelineState()
        assert state.phase_has_data("literature_search") is False
        state.search_results = []
        assert state.phase_has_data("literature_search") is False

    def test_phase_has_data_for_papers(self) -> None:
        state = PipelineState()
        assert state.phase_has_data("paper_ingestion") is False
        state.papers = [Paper(title="A", authors=[], year=2023, venue="V")]
        assert state.phase_has_data("paper_ingestion") is True

    def test_phase_has_data_for_bool(self) -> None:
        state = PipelineState()
        assert state.phase_has_data("academic_review") is False
        state.review_passed = True
        assert state.phase_has_data("academic_review") is True
        state.review_passed = False
        assert state.phase_has_data("academic_review") is False

    def test_phase_order(self) -> None:
        state = PipelineState()
        order = state.get_phase_order()
        expected = [
            "planning",
            "literature_search",
            "paper_ingestion",
            "paper_summarization",
            "literature_synthesis",
            "review_paper_writing",
            "academic_review",
            "revision_release",
        ]
        assert order == expected


class TestSerializationHelpers:
    def test_serialize_dataclass(self) -> None:
        item = SearchItem(
            title="T", authors=["A"], year=2023, venue="V", doi="1"
        )
        result = _serialize(item)
        assert isinstance(result, dict)
        assert result["title"] == "T"

    def test_serialize_list_of_dataclasses(self) -> None:
        items = [
            SearchItem(title="T1", authors=[], year=2023, venue="V"),
            SearchItem(title="T2", authors=["B"], year=2024, venue="W"),
        ]
        result = _serialize(items)
        assert len(result) == 2
        assert result[1]["title"] == "T2"
