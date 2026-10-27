"""PDF conversion model."""

from __future__ import annotations

from datetime import UTC, datetime

from pydantic import BaseModel, Field


class ExtractionWarning(BaseModel):
    """A warning from the PDF extraction process."""

    message: str = Field(..., min_length=1)
    page: int | None = Field(default=None)


class PDFConversionResult(BaseModel):
    """Result of a PDF-to-text conversion."""

    source_pdf_path: str = Field(..., description="Path to the original PDF")
    filename: str = Field(..., description="Name of the output file")
    markdown_content: str = Field(..., description="Extracted Markdown content")
    pdf_checksum: str = Field(..., description="SHA-256 checksum of the source PDF")
    conversion_tool_version: str = Field(
        ..., description="Version of the conversion tool"
    )
    converted_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    extraction_warnings: list[ExtractionWarning] = Field(default_factory=list)
    metadata_preserved: dict[str, str] = Field(default_factory=dict)
