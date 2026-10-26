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
