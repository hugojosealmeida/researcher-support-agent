"""Researcher Support Agent — main entry point."""

from __future__ import annotations

import typer

from researcher_support_agent import __version__
from researcher_support_agent.commands.doctor import doctor
from researcher_support_agent.commands.run import app as run_app
from researcher_support_agent.commands.run import list_phases as _list_phases
from researcher_support_agent.logging_config import configure_logging

app = typer.Typer(
    name="research",
    help="An intelligent research support agent that guides users through systematic literature reviews.",
    add_help_option=True,
    invoke_without_command=True,
)

app.add_typer(run_app, name="run")


@app.command("doctor")
def _doctor(
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed output."),
) -> None:
    """Run a health check on the research environment."""
    doctor(verbose=verbose)


app.command("list-phases")(_list_phases)


@app.callback()
def _main_callback(
    ctx: typer.Context,
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose logging."),
    version: bool = typer.Option(False, "--version", is_eager=True, help="Show version and exit."),
) -> None:
    configure_logging(level="DEBUG" if verbose else "INFO")
    if version:
        typer.echo(f"researcher-support-agent {__version__}")
        raise typer.Exit()


@app.command(name="version")
def version() -> None:
    """Print the version."""
    typer.echo(f"researcher-support-agent {__version__}")


def main() -> None:
    """Entry point."""
    app()


if __name__ == "__main__":
    main()
