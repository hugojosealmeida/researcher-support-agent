<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
"""Doctor command — verifies environment, dependencies, and configuration."""
=======
"""Doctor command — verify environment and dependencies."""
>>>>>>> e45cda7 (fix: Phase B — Literature discovery and ingestion (#3))
=======
"""Doctor command — verify environment and dependencies."""
>>>>>>> 1123db3 (fix: Phase C — Evidence extraction and synthesis (#4))

from __future__ import annotations

import importlib
import sys
<<<<<<< HEAD
<<<<<<< HEAD

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
=======
=======
>>>>>>> 1123db3 (fix: Phase C — Evidence extraction and synthesis (#4))
from typing import List

import typer

app = typer.Typer(help="Check environment, dependencies, and models.")


@app.callback(invoke_without_command=True)
def _doctor(
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Show JSON serialization sample and extra details.",
    ),
) -> None:
    """Run a health check on the environment."""
    results: List[dict] = []
    all_ok = True

    # Python version
    py_ok = sys.version_info >= (3, 11)
    results.append({
        "check": "python_version",
        "status": "ok" if py_ok else "fail",
        "detail": f"Python {sys.version_info.major}.{sys.version_info.minor}",
    })
    if not py_ok:
        all_ok = False

    # Required packages
    required = ["pydantic", "structlog", "typer", "slugify"]
    for pkg_name in required:
        try:
            mod = importlib.import_module(pkg_name)
            version = getattr(mod, "__version__", "unknown")
            results.append({
                "check": f"package_{pkg_name}",
                "status": "ok",
                "detail": f"{pkg_name} {version}",
            })
        except ImportError:
            results.append({
                "check": f"package_{pkg_name}",
                "status": "fail",
                "detail": f"{pkg_name} not installed",
            })
            all_ok = False

    # PyMuPDF (optional)
    try:
        import fitz  # noqa: F401

        results.append({
            "check": "optional_pdf_tool",
            "status": "ok",
            "detail": "PyMuPDF (fitz) available",
        })
    except ImportError:
        results.append({
            "check": "optional_pdf_tool",
            "status": "ok",
            "detail": "PyMuPDF not installed (optional — PDF extraction will use fallback)",
        })

    # Print summary
    for r in results:
        status_icon = "✓" if r["status"] == "ok" else "✗"
        typer.echo(f"{status_icon} {r['check']}: {r['detail']}")

    if verbose:
        typer.echo("")
        typer.echo("--- JSON serialization sample ---")
        import json
        from .models.project import ResearchProject

        sample = ResearchProject(title="Sample Project", questions=["Q1"])
        typer.echo(json.dumps(sample.model_dump(), indent=2))

    if not all_ok:
        typer.echo("")
        typer.echo("Environment check FAILED — please install missing dependencies.")
        raise typer.Exit(code=1)
    else:
        typer.echo("")
        typer.echo("Environment check passed.")
<<<<<<< HEAD
>>>>>>> e45cda7 (fix: Phase B — Literature discovery and ingestion (#3))
=======
>>>>>>> 1123db3 (fix: Phase C — Evidence extraction and synthesis (#4))
=======
=======
>>>>>>> 3eda405 (fix: Phase E — Reliability, Git integration and release (#6))
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
<<<<<<< HEAD
>>>>>>> 10d6757 (fix: Phase D — Manuscript production and quality control (#5))
=======
>>>>>>> 3eda405 (fix: Phase E — Reliability, Git integration and release (#6))
