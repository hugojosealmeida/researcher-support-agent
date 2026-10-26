"""Structured logging configuration using structlog."""

import contextlib
import logging
import sys
from pathlib import Path

import structlog

_LOG_DIR = Path.home() / ".research-agent" / "logs"
_LOG_FILE = _LOG_DIR / "research.log"

_HANDLERS: list[logging.Handler] = []


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
    Path(_LOG_FILE).parent.mkdir(parents=True, exist_ok=True)

    level_num = getattr(logging, level.upper(), logging.INFO)

    # Standard library root logger — remove only handlers we created before
    # (preserves handlers installed by other code, e.g. pytest caplog).
    root = logging.getLogger()
    global _HANDLERS
    for handler in list(_HANDLERS):
        root.removeHandler(handler)
        with contextlib.suppress(Exception):  # pragma: no cover - best effort
            handler.close()
    _HANDLERS.clear()
    root.setLevel(level_num)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level_num)

    handlers: list[logging.Handler] = [console_handler]

    if enable_file:
        file_handler = logging.FileHandler(_LOG_FILE, mode="a", encoding="utf-8")
        file_handler.setLevel(level_num)
        handlers.append(file_handler)

    # structlog renders the event dict via ProcessorFormatter on each handler.
    formatter = structlog.stdlib.ProcessorFormatter(
        processor=structlog.dev.ConsoleRenderer(colors=False),
        foreign_pre_chain=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso", utc=True),
        ],
    )
    for handler in handlers:
        handler.setFormatter(formatter)
        root.addHandler(handler)
    _HANDLERS.extend(handlers)

    # Wire structlog to the standard library logger so records reach handlers.
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.dev.set_exc_info,
            structlog.processors.TimeStamper(fmt="iso", utc=True),
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        context_class=dict,
        cache_logger_on_first_use=False,
    )


def get_logger(name: str = __name__):
    """Return a structured logger bound to *name*."""
    return structlog.get_logger(name)
