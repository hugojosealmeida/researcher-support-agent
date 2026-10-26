"""Typer CLI — main entry point."""

from __future__ import annotations

import typer

from researcher_support_agent import __version__
from researcher_support_agent.commands.doctor import doctor
from researcher_support_agent.commands.run import list_phases, run
from researcher_support_agent.logging_config import setup_logging

app = typer.Typer(
    name="research",
    help="Researcher Support Agent — guide systematic literature reviews",
    add_help_option=True,
)

app.command("doctor")(doctor)
app.command("run")(run)
app.command("list-phases")(list_phases)


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
