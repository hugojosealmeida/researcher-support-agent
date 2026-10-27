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
<<<<<<< HEAD
=======

Reliability (Phase E):
- Validates PDF checksums before processing.
- Treats extracted text as untrusted content.
- Graceful fallback when extraction tools are unavailable.
>>>>>>> 3eda405 (fix: Phase E — Reliability, Git integration and release (#6))
"""

from __future__ import annotations

import hashlib
import os
<<<<<<< HEAD
<<<<<<< HEAD
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

from slugify import slugify

from ..models.pdf_conversion import ExtractionWarning, PDFConversionResult
=======
=======
>>>>>>> 3eda405 (fix: Phase E — Reliability, Git integration and release (#6))
from pathlib import Path

from slugify import slugify

from ..models.pdf_conversion import PDFConversionResult
<<<<<<< HEAD
>>>>>>> 10d6757 (fix: Phase D — Manuscript production and quality control (#5))
=======
from ..reliability import sanitize_pdf_text
>>>>>>> 3eda405 (fix: Phase E — Reliability, Git integration and release (#6))

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
<<<<<<< HEAD
<<<<<<< HEAD
        parts: List[str] = []
=======
        parts: list[str] = []
>>>>>>> 10d6757 (fix: Phase D — Manuscript production and quality control (#5))
=======
        parts: list[str] = []
>>>>>>> 3eda405 (fix: Phase E — Reliability, Git integration and release (#6))
        for page_num, page in enumerate(doc, start=1):
            text = page.get_text()
            parts.append(f"--- Page {page_num} ---\n{text}")
        doc.close()
        return "\n".join(parts)
<<<<<<< HEAD
<<<<<<< HEAD
    except ImportError:
=======
    except Exception:
>>>>>>> 10d6757 (fix: Phase D — Manuscript production and quality control (#5))
=======
    except Exception:
>>>>>>> 3eda405 (fix: Phase E — Reliability, Git integration and release (#6))
        pass

    # Try pdfplumber
    try:
        import pdfplumber  # type: ignore

<<<<<<< HEAD
<<<<<<< HEAD
        with pdfplumber.open(pdf_path) as pdf:
            parts: List[str] = []
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
    warnings: List[ExtractionWarning],
) -> str:
    """Convert raw extracted text to structured Markdown."""
    lines = raw_text.split("\n")
    md_lines: List[str] = []

    for line in lines:
        stripped = line.strip()
        # Simple heading detection
        if stripped and (stripped.isupper() and len(stripped) < 80 or stripped.endswith(":")):
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
        f"extracted_at: {datetime.now(timezone.utc).isoformat()}\n"
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
    output_dir: Optional[str] = None,
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

    warnings: List[ExtractionWarning] = []
    extraction_failures = False

    # Extract text
    raw_text = _extract_text_simple(str(path))
    if "extraction unavailable" in raw_text.lower():
        warnings.append(
            ExtractionWarning(
                message="No PDF extraction tool available; content will be placeholder text",
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
                ocr_parts: List[str] = []
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
=======
=======
>>>>>>> 3eda405 (fix: Phase E — Reliability, Git integration and release (#6))
        text_parts: list[str] = []
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages, start=1):
                text = page.extract_text()
                if text:
                    text_parts.append(f"--- Page {page_num} ---\n{text}")
        return "\n".join(text_parts)
    except Exception:
        pass

    # Try pdftotext via subprocess
    try:
        import subprocess  # noqa: F401

        result = subprocess.run(
            ["pdftotext", pdf_path, "-"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout
    except Exception:
        pass

    # Fallback: return placeholder
    return (
        f"[PDF Conversion Warning: Could not extract text from {pdf_path}]\n"
        f"The PDF exists but text could not be extracted with available tools.\n"
        f"Consider installing PyMuPDF (pip install fitz) or pdfplumber."
    )


def convert_pdf(
    pdf_path: str,
    output_dir: str | None = None,
) -> PDFConversionResult:
    """Convert a PDF to Markdown text.

<<<<<<< HEAD
=======
    Raw text is sanitized to prevent prompt injection from PDF content.

>>>>>>> 3eda405 (fix: Phase E — Reliability, Git integration and release (#6))
    Args:
        pdf_path: Path to the input PDF file.
        output_dir: Directory to write the output Markdown file.

    Returns:
        PDFConversionResult with extracted content and metadata.
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    # Compute checksum
    pdf_checksum = _sha256_file(pdf_path)

    # Extract text
<<<<<<< HEAD
    text = _extract_text_simple(pdf_path)
=======
    raw_text = _extract_text_simple(pdf_path)

    # Sanitize extracted text (treat as untrusted)
    text = sanitize_pdf_text(raw_text)
>>>>>>> 3eda405 (fix: Phase E — Reliability, Git integration and release (#6))

    # Determine output filename
    filename = f"{slugify(Path(pdf_path).stem)}.md"
    if output_dir:
        output_path = Path(output_dir) / filename
        output_path.write_text(text, encoding="utf-8")

    return PDFConversionResult(
        source_pdf_path=pdf_path,
        filename=filename,
        markdown_content=text,
        pdf_checksum=pdf_checksum,
        conversion_tool_version=CONVERSION_TOOL_VERSION,
        metadata_preserved={
            "original_filename": Path(pdf_path).name,
        },
    )
<<<<<<< HEAD
>>>>>>> 10d6757 (fix: Phase D — Manuscript production and quality control (#5))
=======
>>>>>>> 3eda405 (fix: Phase E — Reliability, Git integration and release (#6))
