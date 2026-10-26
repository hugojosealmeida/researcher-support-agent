"""Run command — execute the research pipeline."""

from __future__ import annotations

from ..logging_config import get_logger
from ..orchestrator import Orchestrator

logger = get_logger(__name__)


def run(state_file: str | None = None, max_retries: int = 3) -> None:
    """Run the research pipeline.

    Args:
        state_file: Path to the state file for persistence.
        max_retries: Maximum retries per phase.
    """
    orch = Orchestrator(state_file=state_file, max_retries=max_retries)
    logger.info("Starting research pipeline")
    result = orch.run_all()
    logger.info("Pipeline complete", status=result)
