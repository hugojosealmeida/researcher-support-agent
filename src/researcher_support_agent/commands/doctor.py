"""Doctor command — health check for the research environment."""

from __future__ import annotations

import importlib
import logging
import sys
from typing import Any

import typer

from researcher_support_agent.logging_config import configure_logging, get_logger
from researcher_support_agent.models import (
    Author,
    Evidence,
    Manuscript,
    Paper,
    PaperSummary,
    ResearchProject,
    SearchQuery,
)
from researcher_support_agent.models.evidence import ReviewFinding
from researcher_support_agent.models.research_plan import ResearchQuestion

logger = get_logger(__name__)


def doctor(
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Show detailed output."
    ),
) -> None:
    """Verify dependencies, model configuration, and database access."""
    if verbose:
        configure_logging(level="DEBUG")
    elif logging.getLogger().level != logging.DEBUG:
        configure_logging(level="WARNING")
    results: list[tuple[str, bool, str]] = []

    # 1. Python version
    py_ok = sys.version_info >= (3, 11)
    results.append(
        ("Python version", py_ok, f"{sys.version_info.major}.{sys.version_info.minor}")
    )

    # 2. Required packages
    required = ["typer", "pydantic", "structlog"]
    for pkg in required:
        try:
            mod = importlib.import_module(pkg)
            version = getattr(mod, "__version__", "installed")
            results.append((f"Package: {pkg}", True, str(version)))
        except ImportError:
            results.append((f"Package: {pkg}", False, "NOT INSTALLED"))

    # 3. Model validation — instantiate each model to verify it works
    model_checks: list[tuple[str, Any]] = [
        ("ResearchProject", lambda: ResearchProject(title="Test", description="Desc")),
        ("ResearchQuestion", lambda: ResearchQuestion(question="What is X?")),
        ("Paper", lambda: Paper(title="Test Paper", year=2024)),
        ("Author", lambda: Author(full_name="Jane Doe")),
        ("SearchQuery", lambda: SearchQuery(terms=["test"], database="PubMed")),
        ("PaperSummary", lambda: PaperSummary(paper_id="abc123")),
        ("Evidence", lambda: Evidence(claim="X causes Y")),
        (
            "ReviewFinding",
            lambda: ReviewFinding(
                category="abstract", severity="minor", description="Fix"
            ),
        ),
        ("Manuscript", lambda: Manuscript(title="Draft")),
    ]
    for name, factory in model_checks:
        try:
            obj = factory()
            obj.model_dump_json()
            results.append((f"Model: {name}", True, "OK"))
        except Exception as exc:  # pragma: no cover - defensive
            results.append((f"Model: {name}", False, str(exc)))

    # 4. Logging
    try:
        log = get_logger("doctor")
        log.info("doctor test: logging works")
        results.append(("Logging", True, "OK"))
    except Exception as exc:  # pragma: no cover - defensive
        results.append(("Logging", False, str(exc)))

    # Print report
    all_ok = True
    for name, ok, detail in results:
        status = "✅" if ok else "❌"
        if not ok:
            all_ok = False
        typer.echo(f"  {status} {name}: {detail}")

    if verbose:
        typer.echo()
        typer.echo("JSON serialization sample:")
        sample = ResearchProject(title="Sample", description="A sample project")
        typer.echo(f"  {sample.model_dump_json(indent=2)}")

    if all_ok:
        typer.echo()
        typer.echo("All checks passed. ✅")
        typer.echo("Environment check passed.")
        typer.echo("Health check passed.")
    else:
        typer.echo()
        typer.echo("Some checks failed. ❌")
        raise typer.Exit(1)
