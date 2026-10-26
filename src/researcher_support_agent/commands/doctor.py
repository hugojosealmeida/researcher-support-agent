"""Doctor command — verifies environment, dependencies, and configuration."""

from __future__ import annotations

import importlib
import logging
import sys

import typer

from researcher_support_agent.logging_config import setup_logging
from researcher_support_agent.models import (
    Author,
    Evidence,
    Manuscript,
    Paper,
    PaperSummary,
    ResearchProject,
    ResearchQuestion,
    ReviewFinding,
    SearchQuery,
)


def doctor(
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Show detailed output."
    ),
) -> None:
    """Verify dependencies, model configuration, and database access."""
    # Honour the global verbose flag (set by the main callback) instead of
    # unconditionally overriding the log level. Only lower verbosity when the
    # user has not requested debug output.
    if verbose:
        setup_logging(level="DEBUG")
    elif logging.getLogger().level != logging.DEBUG:
        setup_logging(level="WARNING")
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
    model_checks = [
        ("ResearchProject", lambda: ResearchProject(title="Test", description="Desc")),
        ("ResearchQuestion", lambda: ResearchQuestion(question="What is X?")),
        ("Paper", lambda: Paper(title="Test Paper", year=2024)),
        ("Author", lambda: Author(full_name="Jane Doe")),
        ("SearchQuery", lambda: SearchQuery(query="test", database="PubMed")),
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
        except Exception as exc:
            results.append((f"Model: {name}", False, str(exc)))

    # 4. Logging
    try:
        from researcher_support_agent.logging_config import get_logger

        log = get_logger("doctor")
        log.info("doctor test", message="logging works")
        results.append(("Logging", True, "OK"))
    except Exception as exc:
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
        typer.echo("Models serialize to JSON:")
        sample = ResearchProject(title="Sample", description="A sample project")
        typer.echo(f"  {sample.model_dump_json(indent=2)}")

    if all_ok:
        typer.echo()
        typer.echo("All checks passed. ✅")
    else:
        typer.echo()
        typer.echo("Some checks failed. ❌")
        raise typer.Exit(1)
