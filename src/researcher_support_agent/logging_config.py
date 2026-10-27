<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
"""Structured logging configuration using structlog."""

import logging
import sys
from pathlib import Path

import structlog

_LOG_DIR = Path.home() / ".research-agent" / "logs"
_LOG_FILE = _LOG_DIR / "research.log"


def setup_logging(
    *,
    level: str = "INFO",
    enable_file: bool = True,
) -> None:
    """Configure structlog with both console and file handlers.

    Parameters
    ----------
    level:
        Log level string (DEBUG, INFO, WARNING, ERROR, CRITICAL).
    enable_file:
        If True, also write logs to ~/.research-agent/logs/research.log.
    """
    _LOG_DIR.mkdir(parents=True, exist_ok=True)

    # Standard library logger
    std_logger = logging.getLogger()
    std_logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(
        logging.Formatter("[%(levelname)s] %(message)s"),
    )
    std_logger.addHandler(console_handler)

    if enable_file and not std_logger.handlers:
        file_handler = logging.FileHandler(_LOG_FILE)
        file_formatter = logging.Formatter(
            "%(asctime)s %(levelname)-8s %(message)s",
        )
        file_handler.setFormatter(file_formatter)
        std_logger.addHandler(file_handler)

    # Wire structlog to the standard library logger
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.dev.set_exc_info,
            structlog.processors.TimeStamper(fmt="iso", utc=True),
            structlog.dev.ConsoleRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, level.upper(), logging.INFO),
        ),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=False,
    )


def get_logger(name: str = __name__):
    """Return a structured logger bound to *name*."""
    return structlog.get_logger(name)
=======
=======
>>>>>>> 1123db3 (fix: Phase C — Evidence extraction and synthesis (#4))
"""Logging configuration for the Researcher Support Agent."""

from __future__ import annotations

import json
import sys
from typing import Any, Dict

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
<<<<<<< HEAD
>>>>>>> e45cda7 (fix: Phase B — Literature discovery and ingestion (#3))
=======
>>>>>>> 1123db3 (fix: Phase C — Evidence extraction and synthesis (#4))
=======
=======
>>>>>>> 3eda405 (fix: Phase E — Reliability, Git integration and release (#6))
"""Logging configuration."""

from __future__ import annotations

import logging
import sys


def get_logger(name: str | None = None) -> logging.Logger:
    """Get a configured logger."""
    logger = logging.getLogger(name or "researcher_support_agent")
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger


def configure_logging(
    level: str = "INFO",
    json_output: bool = False,
) -> None:
    """Configure the global logging settings."""
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    logging.basicConfig(
        level=numeric_level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        stream=sys.stdout,
    )
<<<<<<< HEAD
>>>>>>> 10d6757 (fix: Phase D — Manuscript production and quality control (#5))
=======
>>>>>>> 3eda405 (fix: Phase E — Reliability, Git integration and release (#6))
