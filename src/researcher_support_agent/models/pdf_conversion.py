<<<<<<< HEAD
<<<<<<< HEAD
"""PDF conversion result model."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Optional
=======
=======
>>>>>>> 3eda405 (fix: Phase E — Reliability, Git integration and release (#6))
"""PDF conversion model."""

from __future__ import annotations

from datetime import UTC, datetime
<<<<<<< HEAD
>>>>>>> 10d6757 (fix: Phase D — Manuscript production and quality control (#5))
=======
>>>>>>> 3eda405 (fix: Phase E — Reliability, Git integration and release (#6))

from pydantic import BaseModel, Field


class ExtractionWarning(BaseModel):
<<<<<<< HEAD
<<<<<<< HEAD
    """A warning produced during PDF text extraction."""

    page: Optional[int] = Field(default=None)
    message: str = Field(..., min_length=1)
    severity: str = Field(default="warning")


class PDFConversionResult(BaseModel):
    """Result of converting a PDF to Markdown.

    Every converted document has provenance, a reproducible filename,
    and a clear indication of extraction failures.
    """

    source_pdf_path: str = Field(..., description="Path to the original PDF")
    pdf_checksum: str = Field(..., description="SHA-256 checksum of the PDF")
    conversion_tool_version: str = Field(
        ..., description="Version of the tool used for conversion"
    )
    markdown_content: str = Field(
        ..., description="Extracted Markdown text"
    )
    filename: str = Field(..., description="Reproducible output filename")
    extraction_warnings: list[ExtractionWarning] = Field(
        default_factory=list
    )
    extraction_failures: bool = Field(
        default=False, description="True if any content was lost"
    )
    converted_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    metadata_preserved: dict = Field(
        default_factory=dict, description="Preserved PDF metadata"
    )
=======
=======
>>>>>>> 3eda405 (fix: Phase E — Reliability, Git integration and release (#6))
    """A warning from the PDF extraction process."""

    message: str = Field(..., min_length=1)
    page: int | None = Field(default=None)


class PDFConversionResult(BaseModel):
    """Result of a PDF-to-text conversion."""

    source_pdf_path: str = Field(..., description="Path to the original PDF")
    filename: str = Field(..., description="Name of the output file")
    markdown_content: str = Field(..., description="Extracted Markdown content")
    pdf_checksum: str = Field(..., description="SHA-256 checksum of the source PDF")
    conversion_tool_version: str = Field(..., description="Version of the conversion tool")
    converted_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    extraction_warnings: list[ExtractionWarning] = Field(default_factory=list)
    metadata_preserved: dict[str, str] = Field(default_factory=dict)
<<<<<<< HEAD
>>>>>>> 10d6757 (fix: Phase D — Manuscript production and quality control (#5))
=======
>>>>>>> 3eda405 (fix: Phase E — Reliability, Git integration and release (#6))
