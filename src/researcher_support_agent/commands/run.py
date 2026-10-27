<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
"""Run command — executes the workflow pipeline."""

from __future__ import annotations

import typer

from researcher_support_agent.logging_config import get_logger, setup_logging

app = typer.Typer(help="Execute the research workflow.")


@app.callback()
def _run_callback() -> None:
    setup_logging()
=======
=======
>>>>>>> 1123db3 (fix: Phase C — Evidence extraction and synthesis (#4))
"""Run command — execute pipeline phases."""

from __future__ import annotations

from typing import List, Optional

import typer

from ..agents.research_planner import ResearchPlannerConfig, build_research_plan
from ..logging_config import configure_logging, get_logger
from ..models.project import ResearchProject
from ..orchestrator import Phase, Orchestrator

logger = get_logger(__name__)

app = typer.Typer(help="Run the research pipeline.")
<<<<<<< HEAD
>>>>>>> e45cda7 (fix: Phase B — Literature discovery and ingestion (#3))
=======
>>>>>>> 1123db3 (fix: Phase C — Evidence extraction and synthesis (#4))


@app.command()
def run(
<<<<<<< HEAD
<<<<<<< HEAD
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


@app.command(name="list-phases")
def list_phases() -> None:
    """List available phases (placeholder — populated once phases are registered)."""
    typer.echo("Available phases (placeholder):")
    typer.echo("  (register phases with the orchestrator to see them here)")
=======
=======
>>>>>>> 1123db3 (fix: Phase C — Evidence extraction and synthesis (#4))
    topic: str = typer.Option(..., "--topic", "-t", help="Research topic"),
    phase: Optional[str] = typer.Option(
        None, "--phase", "-p", help="Run a single phase only"
    ),
    from_phase: Optional[str] = typer.Option(
        None, "--from", help="Resume from a specific phase"
    ),
    state_file: str = typer.Option(
        "state.json", "--state", "-s", help="Path to state file"
    ),
    dry_run: bool = typer.Option(
        False, "--dry-run", "-d", help="Validate without executing"
    ),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose logging"),
) -> None:
    """Execute the research pipeline."""
    configure_logging(verbose=verbose)

    orchestrator = Orchestrator(state_file=state_file)

    if dry_run:
        result = orchestrator.dry_run()
        for p, done in result.items():
            status = "done" if done else "pending"
            typer.echo(f"  {p}: {status}")
        return

    # Build research plan (always runs first if not already done)
    plan_handler = None

    def _handle_plan(ph: Phase, state) -> None:
        nonlocal plan_handler
        plan = build_research_plan(
            topic=topic,
            project_id=state.project_id,
            config=ResearchPlannerConfig(max_questions=3),
        )
        typer.echo(f"Research plan built with {len(plan.research_questions)} questions")
        typer.echo(f"  Topic: {plan.topic}")
        for i, rq in enumerate(plan.research_questions, 1):
            typer.echo(f"  Q{i}: {rq.question}")
        typer.echo(
            "  ⚠ Protocol requires explicit approval before search runs."
        )
        plan_handler = plan
        state.metadata["plan"] = plan.model_dump()

    def _handle_search(ph: Phase, state) -> None:
        if plan_handler and plan_handler.needs_approval():
            typer.echo("ERROR: Protocol not approved. Run with --approve flag or approve manually.")
            raise RuntimeError("Protocol approval required before search")
        typer.echo("Search phase: no adapters configured in default handler")

    def _handle_screen(ph: Phase, state) -> None:
        typer.echo("Screen phase: no plan loaded for screening")

    orchestrator.run_phase(Phase.PLAN, _handle_plan)

    if phase:
        target = Phase(phase)
        if target == Phase.PLAN:
            return

        handlers = {
            Phase.SEARCH: _handle_search,
            Phase.SCREEN: _handle_screen,
        }
        handler = handlers.get(target)
        if handler:
            orchestrator.run_phase(target, handler)
        return

    # Run remaining phases
    for p in [Phase.SEARCH, Phase.SCREEN]:
        handler_map = {Phase.SEARCH: _handle_search, Phase.SCREEN: _handle_screen}
        orchestrator.run_phase(p, handler_map.get(p, lambda *a: None))

    typer.echo("Pipeline complete.")


@app.command()
def list_phases() -> None:
    """List available pipeline phases."""
    from ..orchestrator import PHASE_ORDER

    typer.echo("Available phases:")
    for i, p in enumerate(PHASE_ORDER, 1):
        typer.echo(f"  {i}. {p.value}")
<<<<<<< HEAD
>>>>>>> e45cda7 (fix: Phase B — Literature discovery and ingestion (#3))
=======
>>>>>>> 1123db3 (fix: Phase C — Evidence extraction and synthesis (#4))
=======
=======
>>>>>>> 3eda405 (fix: Phase E — Reliability, Git integration and release (#6))
"""Run command — execute the research pipeline."""

from __future__ import annotations

from ..logging_config import get_logger
from ..orchestrator import Orchestrator

logger = get_logger(__name__)


def run(state_file: str | None = None, max_retries: int = 3) -> None:
    """Run the research pipeline.

    Args:
        state_file: Path to the state file for persistence.
        max_retries: Maximum retries per phase.
    """
    orch = Orchestrator(state_file=state_file, max_retries=max_retries)
    logger.info("Starting research pipeline")
    result = orch.run_all()
    logger.info("Pipeline complete", status=result)
<<<<<<< HEAD
>>>>>>> 10d6757 (fix: Phase D — Manuscript production and quality control (#5))
=======
>>>>>>> 3eda405 (fix: Phase E — Reliability, Git integration and release (#6))
