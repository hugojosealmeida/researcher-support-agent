"""Run command — execute pipeline phases."""

from __future__ import annotations

import typer

from ..agents.research_planner import ResearchPlannerConfig, build_research_plan
from ..logging_config import configure_logging, get_logger
from ..orchestrator import Orchestrator, Phase

logger = get_logger(__name__)

app = typer.Typer(help="Run the research pipeline.")


@app.command()
def run(
    topic: str = typer.Option(..., "--topic", "-t", help="Research topic"),
    phase: str | None = typer.Option(
        None, "--phase", "-p", help="Run a single phase only"
    ),
    from_phase: str | None = typer.Option(
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
            typer.echo(
                "ERROR: Protocol not approved. "
                "Run with --approve flag or approve manually."
            )
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
