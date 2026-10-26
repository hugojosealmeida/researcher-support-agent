"""Doctor command — verify environment and dependencies."""

from __future__ import annotations

import importlib
import sys
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
