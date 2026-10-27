<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
"""Shared enums and types used across all models."""

from __future__ import annotations

import uuid
from enum import StrEnum


class Status(StrEnum):
    """Processing status for papers and phases."""
=======
=======
>>>>>>> 1123db3 (fix: Phase C — Evidence extraction and synthesis (#4))
=======
>>>>>>> 10d6757 (fix: Phase D — Manuscript production and quality control (#5))
=======
>>>>>>> 3eda405 (fix: Phase E — Reliability, Git integration and release (#6))
"""Common base types shared across models."""

from __future__ import annotations

<<<<<<< HEAD
<<<<<<< HEAD
from datetime import datetime, timezone
from enum import Enum
from typing import Optional
=======
from datetime import UTC, datetime
from enum import Enum
>>>>>>> 10d6757 (fix: Phase D — Manuscript production and quality control (#5))
=======
from datetime import UTC, datetime
from enum import Enum
>>>>>>> 3eda405 (fix: Phase E — Reliability, Git integration and release (#6))
from uuid import UUID, uuid4


class Status(str, Enum):
    """Generic status enum used by many models."""
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
>>>>>>> e45cda7 (fix: Phase B — Literature discovery and ingestion (#3))
=======
>>>>>>> 1123db3 (fix: Phase C — Evidence extraction and synthesis (#4))
=======
>>>>>>> 10d6757 (fix: Phase D — Manuscript production and quality control (#5))
=======
>>>>>>> 3eda405 (fix: Phase E — Reliability, Git integration and release (#6))

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD


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
=======
=======
>>>>>>> 1123db3 (fix: Phase C — Evidence extraction and synthesis (#4))
=======
>>>>>>> 10d6757 (fix: Phase D — Manuscript production and quality control (#5))
=======
>>>>>>> 3eda405 (fix: Phase E — Reliability, Git integration and release (#6))
    NEEDS_REVIEW = "needs_review"


def now_utc() -> datetime:
    """Return the current UTC timestamp."""
<<<<<<< HEAD
<<<<<<< HEAD
    return datetime.now(timezone.utc)
=======
    return datetime.now(UTC)
>>>>>>> 10d6757 (fix: Phase D — Manuscript production and quality control (#5))
=======
    return datetime.now(UTC)
>>>>>>> 3eda405 (fix: Phase E — Reliability, Git integration and release (#6))


def make_id() -> UUID:
    """Return a new UUID4 string for use as a stable identifier."""
    return uuid4()
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
>>>>>>> e45cda7 (fix: Phase B — Literature discovery and ingestion (#3))
=======
>>>>>>> 1123db3 (fix: Phase C — Evidence extraction and synthesis (#4))
=======
>>>>>>> 10d6757 (fix: Phase D — Manuscript production and quality control (#5))
=======
>>>>>>> 3eda405 (fix: Phase E — Reliability, Git integration and release (#6))
