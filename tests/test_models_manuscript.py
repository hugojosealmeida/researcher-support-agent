"""Tests for manuscript model."""

import pytest

from researcher_support_agent.models.manuscript import Manuscript


class TestManuscript:
    def test_minimal(self):
        m = Manuscript()
        assert m.sections == {}
        assert m.version == 1
        assert m.references == []

    def test_with_content(self):
        m = Manuscript(
            sections={"intro": "# Introduction\n\nThis is the intro."},
            version=2,
            references=["ref1", "ref2"],
        )
        assert m.sections["intro"] == "# Introduction\n\nThis is the intro."
        assert m.version == 2
        assert len(m.references) == 2

    def test_bump_version(self):
        m = Manuscript()
        for expected in [2, 3, 4]:
            new_v = m.bump_version()
            assert new_v == expected
            assert m.version == expected

    def test_validation_min_version(self):
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            Manuscript(version=0)
