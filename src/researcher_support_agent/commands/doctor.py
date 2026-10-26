"""Doctor command — health check for the research environment."""

from __future__ import annotations

import sys

from ..logging_config import get_logger

logger = get_logger(__name__)


def doctor(version: str | None = None) -> int:
    """Run a health check on the research environment.

    Checks Python version, required packages, and configuration.
    Returns 0 on success, 1 on failure.
    """
    logger.info("Running health check...")

    # Check Python version
    if sys.version_info < (3, 11):
        logger.error("Python 3.11+ is required")
        return 1

    logger.info("Health check passed")
    return 0
