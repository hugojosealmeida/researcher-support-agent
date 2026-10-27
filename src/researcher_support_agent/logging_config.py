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
        force=True,
    )


def setup_logging(level: str = "INFO") -> None:
    """Backwards-compatible alias for :func:`configure_logging`."""
    configure_logging(level=level)
