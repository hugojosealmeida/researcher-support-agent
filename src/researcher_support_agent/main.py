"""CLI entry point for the Researcher Support Agent."""

from __future__ import annotations

import typer

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


if __name__ == "__main__":
    app()
