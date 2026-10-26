"""Shared enums and types used across all models."""

from __future__ import annotations

import uuid
from enum import StrEnum


class Status(StrEnum):
    """Processing status for papers and phases."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class RetrievalStatus(StrEnum):
    """How a paper was retrieved."""

    NOT_RETRIEVED = "not_retrieved"
    METADATA_ONLY = "metadata_only"
    FULL_TEXT = "full_text"
    FULL_TEXT_PARTIAL = "full_text_partial"


class IdentifierType(StrEnum):
    """Types of stable identifiers for papers."""

    DOI = "doi"
    PMID = "pmid"
    ARXIV = "arxiv"
    HAL = "hal"
    OTHER = "other"


def generate_id() -> str:
    """Generate a short UUID4 identifier."""
    return str(uuid.uuid4())[:8]


def normalize_doi(doi: str) -> str:
    """Normalize a DOI to its canonical form."""
    return doi.strip().lower().removeprefix("https://doi.org/").removeprefix("doi:")


def normalize_arxiv_id(arxiv_id: str) -> str:
    """Normalize an arXiv ID (e.g. 2101.12345v2 -> 2101.12345v2)."""
    return arxiv_id.strip().lower().removeprefix("arxiv:").removeprefix("abs/")
