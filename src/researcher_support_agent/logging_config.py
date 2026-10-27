"""Logging configuration for the Researcher Support Agent."""

from __future__ import annotations

import json
from typing import Any

import structlog


def configure_logging(
    verbose: bool = False,
    log_file: str | None = None,
) -> None:
    """Configure structlog for console (and optionally file) output."""
    processors = [
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    if verbose:
        # Structured JSON for verbose mode
        processors.append(structlog.processors.JSONRenderer())
    else:
        # Human-readable console
        processors.append(structlog.dev.ConsoleRenderer())

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(
            "DEBUG" if verbose else "INFO"
        ),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )

    if log_file:
        file_processors = [
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.add_log_level,
            structlog.processors.JSONRenderer(),
        ]
        file_logger = structlog.make_filtering_bound_logger("DEBUG")
        file_logger._logger = structlog.BoundLogger(
            processors=file_processors,
            wrapper_class=structlog.dev.ConsoleRenderer,  # type: ignore
            context_class=dict,
            logger=structlog.PrintLoggerFactory(log_file)(),  # type: ignore
        )


def get_logger(name: str | None = None) -> Any:
    """Get a logger instance."""
    return structlog.get_logger(name)


def serialize_for_logging(obj: Any) -> str:
    """Safely serialize an object for logging."""
    try:
        if hasattr(obj, "model_dump"):
            return json.dumps(obj.model_dump(), indent=2, default=str)
        if hasattr(obj, "dict"):
            return json.dumps(obj.dict(), indent=2, default=str)
        return json.dumps(obj, default=str, indent=2)
    except (TypeError, ValueError):
        return str(obj)
