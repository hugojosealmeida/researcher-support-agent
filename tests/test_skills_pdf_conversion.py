"""Tests for the PDF conversion skill."""

import hashlib
import os

import pytest

<<<<<<< HEAD
<<<<<<< HEAD
from researcher_support_agent.models.pdf_conversion import ExtractionWarning
=======
>>>>>>> 10d6757 (fix: Phase D — Manuscript production and quality control (#5))
=======
>>>>>>> 3eda405 (fix: Phase E — Reliability, Git integration and release (#6))
from researcher_support_agent.skills.pdf_conversion_skill import (
    CONVERSION_TOOL_VERSION,
    _sha256_file,
    convert_pdf,
)


class TestSHA256File:
    def test_known_hash(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_text("hello world")
        h = _sha256_file(str(f))
        assert h == hashlib.sha256(b"hello world").hexdigest()

    def test_different_content_different_hash(self, tmp_path):
        f1 = tmp_path / "a.txt"
        f1.write_text("aaa")
        f2 = tmp_path / "b.txt"
        f2.write_text("bbb")
        assert _sha256_file(str(f1)) != _sha256_file(str(f2))


class TestPDFConversion:
    def test_converts_valid_pdf(self, sample_pdf, tmp_dir):
        output_path = tmp_dir
        result = convert_pdf(str(sample_pdf), output_dir=output_path)
        assert result.source_pdf_path == str(sample_pdf)
        assert result.pdf_checksum  # non-empty
        assert result.conversion_tool_version == CONVERSION_TOOL_VERSION
        assert result.filename  # non-empty
        assert result.markdown_content  # has content
        assert result.source_pdf_path == str(sample_pdf)

    def test_checksum_matches_file(self, sample_pdf):
        result = convert_pdf(str(sample_pdf))
        expected = _sha256_file(str(sample_pdf))
        assert result.pdf_checksum == expected

    def test_extraction_warning_on_minimal_pdf(self, sample_pdf):
<<<<<<< HEAD
<<<<<<< HEAD
        """A minimal 1-pixel PDF has no real text content."""
        result = convert_pdf(str(sample_pdf))
        # Should complete without raising
        assert result is not None

    def test_file_not_found(self):
        from pathlib import Path

=======
=======
>>>>>>> 3eda405 (fix: Phase E — Reliability, Git integration and release (#6))
        result = convert_pdf(str(sample_pdf))
        assert result is not None

    def test_file_not_found(self):
<<<<<<< HEAD
>>>>>>> 10d6757 (fix: Phase D — Manuscript production and quality control (#5))
=======
>>>>>>> 3eda405 (fix: Phase E — Reliability, Git integration and release (#6))
        with pytest.raises(FileNotFoundError):
            convert_pdf("/nonexistent/path.pdf")

    def test_output_file_created(self, sample_pdf, tmp_dir):
        result = convert_pdf(str(sample_pdf), output_dir=tmp_dir)
<<<<<<< HEAD
<<<<<<< HEAD
        import os

=======
>>>>>>> 10d6757 (fix: Phase D — Manuscript production and quality control (#5))
=======
>>>>>>> 3eda405 (fix: Phase E — Reliability, Git integration and release (#6))
        output_path = os.path.join(tmp_dir, result.filename)
        assert os.path.exists(output_path)

    def test_metadata_preserved(self, sample_pdf):
        result = convert_pdf(str(sample_pdf))
        assert "original_filename" in result.metadata_preserved

    def test_provenance_tracking(self, sample_pdf, tmp_dir):
        result = convert_pdf(str(sample_pdf), output_dir=tmp_dir)
<<<<<<< HEAD
<<<<<<< HEAD
        assert result.pdf_checksum  # checksum tracked
        assert result.conversion_tool_version  # tool version tracked
        assert result.converted_at is not None  # timestamp tracked
=======
        assert result.pdf_checksum
        assert result.conversion_tool_version
        assert result.converted_at is not None
>>>>>>> 10d6757 (fix: Phase D — Manuscript production and quality control (#5))
=======
        assert result.pdf_checksum
        assert result.conversion_tool_version
        assert result.converted_at is not None
>>>>>>> 3eda405 (fix: Phase E — Reliability, Git integration and release (#6))
