"""PDF conversion result model."""

from __future__ import annotations

from datetime import UTC, datetime

from pydantic import BaseModel, Field


class ExtractionWarning(BaseModel):
    """A warning produced during PDF text extraction."""

    page: int | None = Field(default=None)
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
        default_factory=lambda: datetime.now(UTC)
    )
    metadata_preserved: dict = Field(
        default_factory=dict, description="Preserved PDF metadata"
    )
