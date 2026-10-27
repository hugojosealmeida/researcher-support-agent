"""Researcher Support Agent — main entry point."""

from __future__ import annotations

import typer

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


if __name__ == "__main__":
    app()
