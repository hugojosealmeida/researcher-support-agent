"""Run command — executes the workflow pipeline."""

from __future__ import annotations

import typer

from researcher_support_agent.logging_config import get_logger


def run(
    phase: str | None = typer.Option(
        None, "--phase", "-p", help="Run a single phase by name."
    ),
    from_phase: str | None = typer.Option(
        None, "--from", "-f", help="Run from this phase onward."
    ),
    state: str = typer.Option(
        "state.json", "--state", "-s", help="Path to state file."
    ),
    max_retries: int = typer.Option(
        3, "--retries", "-r", help="Max retries per phase."
    ),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Validate phases without executing."
    ),
) -> None:
    """Run the research pipeline.

    Without arguments, runs all phases in order. Use --phase for a single
    phase or --from to resume from a specific phase.
    """
    logger = get_logger("researcher_support_agent.commands.run")
    logger.info("run_command", phase=phase, from_phase=from_phase, state=state)

    if dry_run:
        typer.echo("Dry run mode — no phases will execute.")
        return

    if phase and from_phase:
        typer.echo("Error: cannot specify both --phase and --from")
        raise typer.Exit(1)

    if phase:
        typer.echo(f"Running phase: {phase}")
    elif from_phase:
        typer.echo(f"Resuming from phase: {from_phase}")
    else:
        typer.echo("Running full pipeline")

    state_path = state
    logger.info("pipeline_started", state_path=state_path)
    typer.echo(f"State file: {state_path}")


def list_phases() -> None:
    """List available phases (placeholder — populated once phases are registered)."""
    typer.echo("Available phases (placeholder):")
    typer.echo("  (register phases with the orchestrator to see them here)")
