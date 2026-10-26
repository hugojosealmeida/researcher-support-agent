"""Common base types shared across models."""

from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from uuid import UUID, uuid4


class Status(StrEnum):
    """Generic status enum used by many models."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    NEEDS_REVIEW = "needs_review"


def now_utc() -> datetime:
    """Return the current UTC timestamp."""
    return datetime.now(UTC)


def make_id() -> UUID:
    """Return a new UUID4 string for use as a stable identifier."""
    return uuid4()
