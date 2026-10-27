"""Run command — execute the research pipeline."""

from __future__ import annotations

import typer

from ..logging_config import configure_logging, get_logger
from ..models.research_plan import ResearchQuestion
from ..orchestrator import PHASE_ORDER, Orchestrator, Phase

logger = get_logger(__name__)

app = typer.Typer(
    help="Run the research pipeline.",
    invoke_without_command=True,
)


def _print_phase_list() -> None:
    typer.echo("Available phases:")
    for i, phase in enumerate(PHASE_ORDER, 1):
        typer.echo(f"  {i}. {phase.value}")


def list_phases() -> None:
    """List available pipeline phases."""
    _print_phase_list()


def _execute_run(
    *,
    topic: str | None = None,
    phase: str | None = None,
    from_phase: str | None = None,
    state: str = "state.json",
    dry_run: bool = False,
    retries: int = 3,
    verbose: bool = False,
) -> None:
    """Core implementation shared by the callback and subcommands."""
    configure_logging(level="DEBUG" if verbose else "INFO")

    state_file = state
    orchestrator = Orchestrator(state_file=state_file, max_retries=retries)

    if phase and from_phase:
        typer.echo("Error: cannot specify both --phase and --from")
        raise typer.Exit(1)

    if dry_run:
        typer.echo("Dry run — validating phases without executing.")
        result = orchestrator.dry_run()
        for name, done in result.items():
            status = "done" if done else "pending"
            typer.echo(f"  {name}: {status}")
        return

    if phase:
        typer.echo(f"Running phase: {phase}")
        try:
            target = Phase(phase)
        except ValueError:
            typer.echo(f"Unknown phase: {phase}")
            raise typer.Exit(1) from None
        if topic and target == Phase.PLAN:
            from ..agents.research_planner import ResearchPlanner

            plan = ResearchPlanner().plan(topic, [ResearchQuestion(question=topic)])
            typer.echo(f"Research plan built with {len(plan.questions)} questions")
            typer.echo(f"  Topic: {plan.topic if hasattr(plan, 'topic') else plan.title}")
            for i, question in enumerate(plan.questions, 1):
                typer.echo(f"  Q{i}: {question.question}")
        handler = getattr(orchestrator, f"_handle_{target.value}", None)
        if handler is None:
            def handler(_phase: Phase, _state: object) -> None:
                return None
        orchestrator.run_phase(target, handler)
        typer.echo("Pipeline complete.")
        return

    if from_phase:
        typer.echo(f"Resuming from phase: {from_phase}")
        try:
            target = Phase(from_phase)
        except ValueError:
            typer.echo(f"Unknown phase: {from_phase}")
            raise typer.Exit(1) from None
        start_index = PHASE_ORDER.index(target)
        for current in PHASE_ORDER[start_index:]:
            handler = getattr(orchestrator, f"_handle_{current.value}", None)
            if handler is None:
                def handler(_phase: Phase, _state: object) -> None:
                    return None
            orchestrator.run_phase(current, handler)
        typer.echo("Pipeline complete.")
        return

    typer.echo("Running full pipeline")
    typer.echo(f"State file: {state_file}")
    orchestrator.run_all()
    typer.echo("Pipeline complete.")


@app.callback(invoke_without_command=True)
def _callback(
    ctx: typer.Context,
    topic: str | None = typer.Option(None, "--topic", "-t", help="Research topic."),
    phase: str | None = typer.Option(None, "--phase", "-p", help="Run a single phase by name."),
    from_phase: str | None = typer.Option(None, "--from", "-f", help="Resume from this phase onward."),
    state: str = typer.Option("state.json", "--state", "-s", help="Path to state file."),
    dry_run: bool = typer.Option(False, "--dry-run", help="Validate phases without executing."),
    retries: int = typer.Option(3, "--retries", "-r", help="Max retries per phase."),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose logging."),
) -> None:
    if ctx.invoked_subcommand is not None:
        return
    _execute_run(
        topic=topic,
        phase=phase,
        from_phase=from_phase,
        state=state,
        dry_run=dry_run,
        retries=retries,
        verbose=verbose,
    )


@app.command(name="run")
def run_command(
    topic: str | None = typer.Option(None, "--topic", "-t", help="Research topic."),
    phase: str | None = typer.Option(None, "--phase", "-p", help="Run a single phase by name."),
    from_phase: str | None = typer.Option(None, "--from", "-f", help="Resume from this phase onward."),
    state: str = typer.Option("state.json", "--state", "-s", help="Path to state file."),
    dry_run: bool = typer.Option(False, "--dry-run", help="Validate phases without executing."),
    retries: int = typer.Option(3, "--retries", "-r", help="Max retries per phase."),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose logging."),
) -> None:
    """Run the research pipeline."""
    _execute_run(
        topic=topic,
        phase=phase,
        from_phase=from_phase,
        state=state,
        dry_run=dry_run,
        retries=retries,
        verbose=verbose,
    )


@app.command(name="list-phases")
def list_phases_command() -> None:
    """List available pipeline phases."""
    _print_phase_list()
