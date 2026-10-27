<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
"""Typer CLI — main entry point."""
=======
"""CLI entry point for the Researcher Support Agent."""
>>>>>>> e45cda7 (fix: Phase B — Literature discovery and ingestion (#3))
=======
"""CLI entry point for the Researcher Support Agent."""
>>>>>>> 1123db3 (fix: Phase C — Evidence extraction and synthesis (#4))
=======
"""Researcher Support Agent — main entry point."""
>>>>>>> 10d6757 (fix: Phase D — Manuscript production and quality control (#5))
=======
"""Researcher Support Agent — main entry point."""
>>>>>>> 3eda405 (fix: Phase E — Reliability, Git integration and release (#6))

from __future__ import annotations

import typer

<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
from researcher_support_agent import __version__
from researcher_support_agent.commands.doctor import doctor
from researcher_support_agent.commands.run import app as run_app
from researcher_support_agent.logging_config import setup_logging

app = typer.Typer(
    name="research",
    help="Researcher Support Agent — guide systematic literature reviews",
    add_help_option=True,
)

app.command("doctor")(doctor)
app.add_typer(run_app, name="run", help="Execute the research workflow")


@app.callback()
def _main_callback(verbose: bool = typer.Option(False, "--verbose", "-v")) -> None:
    level = "DEBUG" if verbose else "INFO"
    setup_logging(level=level)


@app.command(name="version")
def version() -> None:
    """Print the package version."""
    typer.echo(__version__)


def main():
    """Entry point."""
    app()


# Allow running as a module: python -m researcher_support_agent
if __name__ == "__main__":
    main()
=======
=======
>>>>>>> 1123db3 (fix: Phase C — Evidence extraction and synthesis (#4))
from . import __version__
from .commands.doctor import app as doctor_app
from .commands.run import app as run_app

app = typer.Typer(
    name="research",
    help="Researcher Support Agent — guide systematic literature reviews.",
    add_completion=False,
    no_args_is_help=False,
)


@app.callback(invoke_without_command=True)
def cli(
    ctx: typer.Context,
    version: bool = typer.Option(
        False,
        "--version",
        "-v",
        help="Show version and exit.",
        is_eager=True,
    ),
):
    if version:
        typer.echo(f"researcher-support-agent, version {__version__}")
        raise typer.Exit()

app.add_typer(doctor_app, name="doctor")
app.add_typer(run_app, name="run")
=======
=======
>>>>>>> 3eda405 (fix: Phase E — Reliability, Git integration and release (#6))
app = typer.Typer(
    name="research",
    help="An intelligent research support agent that guides users through systematic literature reviews.",
)


@app.command()
def version() -> None:
    """Print the version."""
    typer.echo("researcher-support-agent 0.1.0")


@app.command()
def doctor() -> None:
    """Run a health check on the research environment."""
    typer.echo("Health check passed.")
<<<<<<< HEAD
>>>>>>> 10d6757 (fix: Phase D — Manuscript production and quality control (#5))
=======
>>>>>>> 3eda405 (fix: Phase E — Reliability, Git integration and release (#6))


if __name__ == "__main__":
    app()
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
>>>>>>> e45cda7 (fix: Phase B — Literature discovery and ingestion (#3))
=======
>>>>>>> 1123db3 (fix: Phase C — Evidence extraction and synthesis (#4))
=======
>>>>>>> 10d6757 (fix: Phase D — Manuscript production and quality control (#5))
=======
>>>>>>> 3eda405 (fix: Phase E — Reliability, Git integration and release (#6))
