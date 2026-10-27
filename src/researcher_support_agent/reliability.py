"""Reliability utilities for the research pipeline.

Provides:
- Retry policy with exponential backoff
- API rate limiting (token bucket)
- Per-paper error isolation
- Token/cost tracking
- PDF text sanitization (treat as untrusted content)
- Checkpoint persistence with resume support
"""

from __future__ import annotations

import hashlib
import json
import os
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any, TypeVar

from .logging_config import get_logger

logger = get_logger(__name__)

T = TypeVar("T")


# ---------------------------------------------------------------------------
# Retry policy
# ---------------------------------------------------------------------------


class RetryableError(Exception):
    """Error that should be retried (transient)."""

    pass


class NonRetryableError(Exception):
    """Error that should NOT be retried (permanent)."""

    pass


@dataclass
class RetryPolicy:
    """Configurable retry policy with exponential backoff.

    Args:
        max_retries: Maximum number of retry attempts.
        base_delay: Base delay in seconds before the first retry.
        max_delay: Maximum delay between retries (caps exponential growth).
        multiplier: Exponential backoff multiplier.
        retryable_exceptions: Tuple of exception types considered transient.
    """

    max_retries: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0
    multiplier: float = 2.0
    retryable_exceptions: tuple[type[Exception], ...] = (RetryableError,)

    def execute(self, fn: Callable[..., T], *args: Any, **kwargs: T) -> T:
        """Execute ``fn`` with retry logic.

        Raises the last exception if all retries are exhausted.
        """
        last_exc: Exception | None = None
        for attempt in range(1, self.max_retries + 1):
            try:
                return fn(*args, **kwargs)
            except NonRetryableError:
                raise
            except self.retryable_exceptions as exc:
                last_exc = exc
                if attempt < self.max_retries:
                    delay = min(
                        self.base_delay * (self.multiplier ** (attempt - 1)),
                        self.max_delay,
                    )
                    logger.warning(
                        "retry_attempt attempt=%d/%d error=%s delay=%.2fs",
                        attempt,
                        self.max_retries,
                        exc,
                        delay,
                    )
                    time.sleep(delay)
                else:
                    logger.error(
                        "retries_exhausted max_retries=%d error=%s",
                        self.max_retries,
                        exc,
                    )
            except Exception as exc:
                # Non-expected exceptions are treated as non-retryable
                raise NonRetryableError(
                    f"Unexpected error (non-retryable): {exc}"
                ) from exc
        assert last_exc is not None
        raise last_exc


# ---------------------------------------------------------------------------
# Rate limiter (token bucket)
# ---------------------------------------------------------------------------


class RateLimiter:
    """Simple token-bucket rate limiter for API calls.

    Args:
        tokens: Maximum burst size.
        refill_rate: Tokens added per second.
    """

    def __init__(self, tokens: int = 10, refill_rate: float = 1.0) -> None:
        self.tokens = tokens
        self.refill_rate = refill_rate
        self._tokens = float(tokens)
        self._last_refill = time.monotonic()

    def acquire(self) -> None:
        """Wait until a token is available, then consume one."""
        self._refill()
        if self._tokens < 1.0:
            wait_time = (1.0 - self._tokens) / self.refill_rate
            logger.info("rate_limiter_throttling wait=%.3fs", wait_time)
            time.sleep(wait_time)
            self._refill()
        self._tokens -= 1.0

    def _refill(self) -> None:
        now = time.monotonic()
        elapsed = now - self._last_refill
        self._tokens = min(self.tokens, self._tokens + elapsed * self.refill_rate)
        self._last_refill = now


# ---------------------------------------------------------------------------
# Per-paper error isolation
# ---------------------------------------------------------------------------


@dataclass
class PaperResult:
    """Result of processing a single paper.

    Attributes:
        paper_id: Stable identifier for the paper.
        success: Whether processing succeeded.
        data: Processed data on success (None on failure).
        error: Error message on failure (None on success).
    """

    paper_id: str
    success: bool
    data: Any = None
    error: str | None = None


def process_papers_isolated(
    papers: list[Any],
    processor: Callable[[Any], Any],
    paper_id_fn: Callable[[Any], str],
    max_failures: int | None = None,
) -> list[PaperResult]:
    """Process each paper independently; failures don't affect others.

    Args:
        papers: List of paper objects to process.
        processor: Callable that processes a single paper.
        paper_id_fn: Extracts a stable ID from a paper.
        max_failures: If set, stop after this many failures.

    Returns:
        A list of PaperResult (one per input paper).
    """
    results: list[PaperResult] = []
    failure_count = 0

    for paper in papers:
        pid = paper_id_fn(paper)
        try:
            data = processor(paper)
            results.append(PaperResult(paper_id=pid, success=True, data=data))
        except NonRetryableError as exc:
            results.append(PaperResult(paper_id=pid, success=False, error=str(exc)))
            failure_count += 1
            if max_failures is not None and failure_count >= max_failures:
                logger.warning(
                    "max_paper_failures_reached max=%d paper=%s",
                    max_failures,
                    pid,
                )
                # Mark remaining papers as skipped
                remaining = papers[len(results) :]
                for p in remaining:
                    results.append(
                        PaperResult(
                            paper_id=paper_id_fn(p),
                            success=False,
                            error="Pipeline stopped due to max failures",
                        )
                    )
                break
        except Exception as exc:
            results.append(PaperResult(paper_id=pid, success=False, error=str(exc)))
            failure_count += 1
            if max_failures is not None and failure_count >= max_failures:
                logger.warning(
                    "max_paper_failures_reached max=%d paper=%s",
                    max_failures,
                    pid,
                )
                remaining = papers[len(results) :]
                for p in remaining:
                    results.append(
                        PaperResult(
                            paper_id=paper_id_fn(p),
                            success=False,
                            error="Pipeline stopped due to max failures",
                        )
                    )
                break

    return results


# ---------------------------------------------------------------------------
# Token / cost tracking
# ---------------------------------------------------------------------------


class TokenTracker:
    """Track API token usage and approximate cost.

    Args:
        token_cost_per_million: Cost in USD per million output tokens.
        input_cost_per_million: Cost in USD per million input tokens.
            Defaults to ``token_cost_per_million`` when not provided.
    """

    def __init__(
        self,
        token_cost_per_million: float = 0.0,
        input_cost_per_million: float | None = None,
    ) -> None:
        self.input_tokens: int = 0
        self.output_tokens: int = 0
        self.token_cost_per_million = token_cost_per_million
        self.input_cost_per_million = (
            token_cost_per_million
            if input_cost_per_million is None
            else input_cost_per_million
        )

    def record_input(self, tokens: int) -> None:
        """Record input tokens used."""
        self.input_tokens += tokens

    def record_output(self, tokens: int) -> None:
        """Record output tokens used."""
        self.output_tokens += tokens

    @property
    def total_input(self) -> int:
        return self.input_tokens

    @property
    def total_output(self) -> int:
        return self.output_tokens

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens

    @property
    def estimated_cost(self) -> float:
        """Estimate cost in USD, accounting for both input and output tokens."""
        cost = 0.0
        if self.input_cost_per_million > 0:
            cost += (self.input_tokens / 1_000_000) * self.input_cost_per_million
        if self.token_cost_per_million > 0:
            cost += (self.output_tokens / 1_000_000) * self.token_cost_per_million
        return cost

    def to_dict(self) -> dict[str, Any]:
        return {
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "total_tokens": self.total_tokens,
            "estimated_cost_usd": round(self.estimated_cost, 6),
        }


# ---------------------------------------------------------------------------
# PDF text sanitization
# ---------------------------------------------------------------------------


def sanitize_pdf_text(text: str) -> str:
    """Sanitize PDF-extracted text to prevent prompt injection / instruction leakage.

    PDF text is treated as untrusted content. This function:
    - Strips potential instruction-like patterns (e.g. "ignore previous instructions").
    - Limits the maximum length to prevent context overflow.
    - Removes control characters that could disrupt downstream processing.
    """
    if not text:
        return ""

    # Remove control characters except common whitespace
    cleaned = "".join(
        ch for ch in text if ch in "\n\r\t" or (ord(ch) >= 0x20 and ord(ch) != 0x7F)
    )

    # Strip known instruction-injection patterns (case-insensitive)
    injection_patterns = [
        r"(?i)(?:ignore\s+(?:all|previous|earlier)\s+instructions?)",
        r"(?i)(?:system|assistant|user):\s*",
        r"(?i)(?:you are an? \w+)",
        r"(?i)(?:as an? \w+,)",
        r"(?i)(?:do not follow)",
    ]
    for pattern in injection_patterns:
        if os.environ.get("SANITIZE_PDF", "1") != "0":
            cleaned = _strip_patterns(cleaned, [pattern])

    # Cap length to prevent context overflow
    max_length = int(os.environ.get("PDF_MAX_LENGTH", "50000"))
    if len(cleaned) > max_length:
        logger.warning(
            "pdf_text_truncated original=%d max=%d",
            len(text),
            max_length,
        )
        cleaned = cleaned[:max_length] + "\n... [truncated]"

    return cleaned


def _strip_patterns(text: str, patterns: list[str]) -> str:
    """Strip lines matching any of the given regex patterns."""
    import re

    lines = text.split("\n")
    result: list[str] = []
    for line in lines:
        if not any(re.search(p, line) for p in patterns):
            result.append(line)
    return "\n".join(result)


# ---------------------------------------------------------------------------
# Checkpointing
# ---------------------------------------------------------------------------

CHECKPOINT_FILE = "checkpoint.json"


@dataclass
class Checkpoint:
    """Persistable checkpoint for resumable runs.

    Tracks which papers have been processed so far, allowing
    interrupted runs to resume without re-processing completed papers.
    """

    project_id: str
    processed_paper_ids: set[str] = field(default_factory=set)
    completed_phases: set[str] = field(default_factory=set)
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)

    def is_paper_processed(self, paper_id: str) -> bool:
        return paper_id in self.processed_paper_ids

    def mark_paper_processed(self, paper_id: str) -> None:
        self.processed_paper_ids.add(paper_id)
        self.updated_at = time.time()

    def mark_phase_completed(self, phase: str) -> None:
        self.completed_phases.add(phase)
        self.updated_at = time.time()

    def to_dict(self) -> dict[str, Any]:
        return {
            "project_id": self.project_id,
            "processed_paper_ids": sorted(self.processed_paper_ids),
            "completed_phases": sorted(self.completed_phases),
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Checkpoint:
        return cls(
            project_id=data["project_id"],
            processed_paper_ids=set(data.get("processed_paper_ids", [])),
            completed_phases=set(data.get("completed_phases", [])),
            created_at=data.get("created_at", time.time()),
            updated_at=data.get("updated_at", time.time()),
        )


def load_checkpoint(project_id: str, checkpoint_dir: str | None = None) -> Checkpoint:
    """Load a checkpoint from disk, or create a fresh one."""
    base = checkpoint_dir or os.getcwd()
    path = os.path.join(base, CHECKPOINT_FILE)
    if os.path.exists(path):
        with open(path) as f:
            data = json.load(f)
        checkpoint = Checkpoint.from_dict(data)
        if checkpoint.project_id != project_id:
            raise ValueError(
                f"Checkpoint project_id mismatch: expected {project_id!r}, got {checkpoint.project_id!r}"
            )
        logger.info("checkpoint_loaded project=%s", project_id)
        return checkpoint
    checkpoint = Checkpoint(project_id=project_id)
    save_checkpoint(checkpoint, checkpoint_dir)
    return checkpoint


def save_checkpoint(checkpoint: Checkpoint, checkpoint_dir: str | None = None) -> None:
    """Write the checkpoint to disk."""
    base = checkpoint_dir or os.getcwd()
    path = os.path.join(base, CHECKPOINT_FILE)
    with open(path, "w") as f:
        json.dump(checkpoint.to_dict(), f, indent=2)
    logger.info("checkpoint_saved project=%s", checkpoint.project_id)


# ---------------------------------------------------------------------------
# PDF checksum cache
# ---------------------------------------------------------------------------


def compute_pdf_checksum(pdf_path: str) -> str:
    """Compute SHA-256 checksum of a PDF file."""
    h = hashlib.sha256()
    with open(pdf_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()
