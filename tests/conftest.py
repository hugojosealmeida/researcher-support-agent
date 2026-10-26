"""Shared test fixtures."""

import pytest
from pathlib import Path

from research_pipeline.state import PipelineState, SearchItem, Paper, Summary


@pytest.fixture()
def state_file(tmp_path: Path) -> Path:
    """Return a path to a temp JSON file for state persistence tests."""
    return tmp_path / "pipeline_state.json"


@pytest.fixture()
def sample_search_item() -> SearchItem:
    return SearchItem(
        title="Sample Paper",
        authors=["A. Author"],
        year=2024,
        venue="Test Journal",
        doi="10.1234/sample",
        abstract="A test abstract.",
    )


@pytest.fixture()
def sample_paper() -> Paper:
    return Paper(
        title="Sample Paper",
        authors=["A. Author"],
        year=2024,
        venue="Test Journal",
        doi="10.1234/sample",
        md_path="/tmp/sample.md",
        content="# Sample\n\nContent.",
    )


@pytest.fixture()
def sample_summary() -> Summary:
    return Summary(
        title="Sample Paper",
        doi="10.1234/sample",
        key_findings=["Finding A"],
        methods=["Method B"],
        limitations=["Limit C"],
    )
