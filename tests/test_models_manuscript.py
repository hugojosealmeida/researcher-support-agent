"""Tests for manuscript model."""

import pytest

from researcher_support_agent.models import Manuscript


class TestManuscript:
    def test_valid_creation(self):
        m = Manuscript(title="Draft Title")
        assert m.title == "Draft Title"
        assert m.version == 1

    def test_empty_title_raises(self):
        with pytest.raises(ValueError):
            Manuscript(title="")

    def test_update_section(self):
        m = Manuscript(title="Title")
        m.update_section("introduction", "This is the intro.")
        assert "introduction" in m.sections

    def test_bump_version(self):
        m = Manuscript(title="Title")
        m.bump_version()
        assert m.version == 2

    def test_get_full_text(self):
        m = Manuscript(title="Title")
        m.update_section("introduction", "Intro text")
        m.update_section("methods", "Methods text")
        full = m.get_full_text()
        assert "## introduction" in full
        assert "Intro text" in full
        assert "## methods" in full

    def test_empty_sections(self):
        m = Manuscript(title="Title")
        assert m.get_full_text() == ""
