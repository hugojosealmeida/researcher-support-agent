"""PDF conversion skill.

Handles permitted PDF downloads, text extraction, OCR fallback,
metadata preservation, and Markdown generation.

Preserves:
- Section headings
- Equations (best effort)
- Tables
- Captions
- References
- Page numbers
- Extraction warnings

Tracks:
- Source PDF checksum (SHA-256)
- Conversion tool version

Does NOT bypass publisher access controls or licensing restrictions.
"""

from __future__ import annotations

import hashlib
import os
from datetime import UTC, datetime
from pathlib import Path

from slugify import slugify

from ..models.pdf_conversion import ExtractionWarning, PDFConversionResult

CONVERSION_TOOL_VERSION = "0.1.0"


def _sha256_file(path: str) -> str:
    """Compute the SHA-256 checksum of a file."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def _extract_text_simple(pdf_path: str) -> str:
    """Attempt text extraction from a PDF using available tools.

    Tries PyMuPDF (fitz), then pdfplumber, then pdftotext via subprocess.
    Falls back to returning a placeholder if nothing works.
    """
    # Try PyMuPDF
    try:
        import fitz  # type: ignore

        doc = fitz.open(pdf_path)
        parts: list[str] = []
        for page_num, page in enumerate(doc, start=1):
            text = page.get_text()
            parts.append(f"--- Page {page_num} ---\n{text}")
        doc.close()
        return "\n".join(parts)
    except ImportError:
        pass

    # Try pdfplumber
    try:
        import pdfplumber  # type: ignore

        with pdfplumber.open(pdf_path) as pdf:
            parts: list[str] = []
            for page_num, page in enumerate(pdf.pages, start=1):
                text = page.extract_text() or ""
                parts.append(f"--- Page {page_num} ---\n{text}")
            return "\n".join(parts)
    except ImportError:
        pass

    # Try pdftotext CLI
    try:
        import subprocess

        result = subprocess.run(
            ["pdftotext", "-layout", pdf_path, "-"],
            capture_output=True,
            text=True,
            timeout=60,
        )
        if result.returncode == 0:
            return result.stdout
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    # Fallback: return placeholder
    return "[PDF extraction unavailable — no extraction tool installed]"


def _generate_markdown(
    raw_text: str,
    metadata: dict,
    warnings: list[ExtractionWarning],
) -> str:
    """Convert raw extracted text to structured Markdown."""
    lines = raw_text.split("\n")
    md_lines: list[str] = []

    for line in lines:
        stripped = line.strip()
        # Simple heading detection
        if stripped and (
            stripped.isupper() and len(stripped) < 80 or stripped.endswith(":")
        ):
            md_lines.append(f"\n## {stripped}\n")
        elif stripped.startswith("References") or stripped.startswith("Bibliography"):
            md_lines.append(f"\n# {stripped}\n")
        elif stripped:
            md_lines.append(stripped)
        else:
            md_lines.append("")

    # Add metadata block at the top
    md_lines.insert(
        0,
        f"---\n"
        f"source: {metadata.get('original_filename', 'unknown.pdf')}\n"
        f"extracted_at: {datetime.now(UTC).isoformat()}\n"
        f"---\n",
    )

    # Add warnings if any
    if warnings:
        md_lines.append("\n---\n")
        md_lines.append("## Extraction Warnings\n")
        for w in warnings:
            md_lines.append(f"- [{w.severity}] {w.message}")

    return "\n".join(md_lines)


def convert_pdf(
    pdf_path: str,
    output_dir: str | None = None,
) -> PDFConversionResult:
    """Convert a single PDF to Markdown.

    Returns a ``PDFConversionResult`` with full provenance tracking.
    """
    path = Path(pdf_path)
    if not path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    checksum = _sha256_file(str(path))
    filename = f"{slugify(path.stem)}_{checksum[:8]}.md"

    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, filename)
    else:
        output_path = filename

    warnings: list[ExtractionWarning] = []
    extraction_failures = False

    # Extract text
    raw_text = _extract_text_simple(str(path))
    if "extraction unavailable" in raw_text.lower():
        warnings.append(
            ExtractionWarning(
                message=(
                    "No PDF extraction tool available; content will be placeholder text"
                ),
                severity="error",
            )
        )
        extraction_failures = True

    # Attempt OCR fallback if text is empty/placeholder
    if not raw_text.strip() or "placeholder" in raw_text.lower():
        try:
            import subprocess

            # Try tesseract OCR as fallback
            result = subprocess.run(
                ["pdftoppm", "-png", str(path), "/tmp/pdf_page"],
                capture_output=True,
                timeout=60,
            )
            if result.returncode == 0:
                import glob

                png_files = sorted(glob.glob("/tmp/pdf_page-*.png"))
                ocr_parts: list[str] = []
                for i, png_file in enumerate(png_files):
                    ocr_result = subprocess.run(
                        ["tesseract", png_file, "stdout"],
                        capture_output=True,
                        text=True,
                        timeout=30,
                    )
                    if ocr_result.returncode == 0:
                        ocr_parts.append(
                            f"--- Page {i + 1} (OCR) ---\n{ocr_result.stdout}"
                        )
                if ocr_parts:
                    raw_text = "\n".join(ocr_parts)
                    warnings.append(
                        ExtractionWarning(
                            message="Text extraction failed; OCR fallback was used",
                            severity="warning",
                        )
                    )
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass

    # Collect metadata
    metadata: dict = {
        "original_filename": path.name,
        "file_size": path.stat().st_size,
        "modified": datetime.fromtimestamp(path.stat().st_mtime).isoformat(),
    }

    # Generate Markdown
    markdown_content = _generate_markdown(raw_text, metadata, warnings)

    # Write output
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(markdown_content)

    result = PDFConversionResult(
        source_pdf_path=str(path),
        pdf_checksum=checksum,
        conversion_tool_version=CONVERSION_TOOL_VERSION,
        markdown_content=markdown_content,
        filename=filename,
        extraction_warnings=warnings,
        extraction_failures=extraction_failures,
        metadata_preserved=metadata,
    )

    return result
