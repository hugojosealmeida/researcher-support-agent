# Researcher Support Agent

An intelligent research support agent that guides users through systematic
literature reviews, built on an 8-phase academic research pipeline with
independently runnable agents.

## Features

- **Typed data models** with Pydantic — validated, serializable, and reusable
- **CLI with Typer** — intuitive commands for running phases and checking system health
- **Structured logging** via structlog — console and file output with ISO timestamps
- **Workflow orchestrator** — owns phase order, retries, state transitions, and checkpoints
- **Phase independence** — any phase can run standalone; failed phases resume without repeating completed work
- **Stable identifiers** — papers track DOI, PMID, arXiv ID, and source-specific IDs
- **Reliability** — rate limiting and retry policies for external scholarly APIs

## Pipeline Phases

| # | Phase | Description |
|---|-------|-------------|
| 1 | **Research Topic & Planning** | Defines research questions, scope, inclusion criteria and search strategy |
| 2 | **Literature Search** | Searches scholarly databases, discovers papers and records metadata |
| 3 | **Paper Ingestion & Markdown** | Downloads permitted full texts, extracts content and creates structured Markdown files |
| 4 | **Paper Summarization** | Produces evidence-grounded summaries and structured research notes |
| 5 | **Literature Synthesis** | Compares methods, findings, disagreements, limitations and research gaps |
| 6 | **Review Paper Writing** | Drafts the review manuscript from the approved evidence base |
| 7 | **Academic Review** | Audits claims, abstract, structure, citations, bibliography and academic quality |
| 8 | **Revision & Release** | Addresses reviewer comments, validates the final manuscript and publishes a versioned result |

## Installation

```bash
# Create a virtual environment
uv venv
source .venv/bin/activate

# Install in development mode with test dependencies
uv pip install -e ".[dev]"
```

## Usage

### CLI

Verify your environment, dependencies, and models:

```bash
research doctor
research doctor -v  # verbose: shows JSON serialization sample
```

Execute the research pipeline:

```bash
research run                    # Run all phases
research run --phase search     # Run a single phase
research run --from synthesize  # Resume from a specific phase
research run --state state.json # Use a custom state file
research run --dry-run          # Validate without executing
```

List phases:

```bash
research run list-phases
```

Version:

```bash
research version
```

### Python API

```python
from research_pipeline import Pipeline
from research_pipeline.agents import (
    PlanningAgent,
    LiteratureSearchAgent,
    PaperIngestionAgent,
    PaperSummarizationAgent,
    LiteratureSynthesisAgent,
    ReviewPaperWriterAgent,
    AcademicReviewerAgent,
    RevisionReleaseAgent,
)

pipeline = Pipeline(state_file="pipeline_state.json")

pipeline.register_agent(PlanningAgent(
    topic="CRISPR gene editing in agriculture",
    research_questions=["What are the efficacy outcomes?"],
))
pipeline.register_agent(LiteratureSearchAgent())
pipeline.register_agent(PaperIngestionAgent())
pipeline.register_agent(PaperSummarizationAgent())
pipeline.register_agent(LiteratureSynthesisAgent())
pipeline.register_agent(ReviewPaperWriterAgent())
pipeline.register_agent(AcademicReviewerAgent())
pipeline.register_agent(RevisionReleaseAgent())

state = pipeline.run_full()
```

## Architecture

```
research_pipeline/
├── __init__.py           # Public API exports
├── state.py              # Data models: PipelineState, SearchItem, Paper, Summary, ReviewComment
├── agent_base.py         # Abstract PipelineAgent base class
├── pipeline.py           # Pipeline orchestrator
└── agents/               # Eight phase agent implementations
    ├── __init__.py       # Re-exports PipelineAgent and all phase agents
    ├── planning_agent.py
    ├── literature_search_agent.py
    ├── paper_ingestion_agent.py
    ├── paper_summarization_agent.py
    ├── literature_synthesis_agent.py
    ├── review_paper_writer_agent.py
    ├── academic_reviewer_agent.py
    └── revision_release_agent.py
```

The `researcher_support_agent` package provides the Pydantic data models, CLI,
orchestrator, and reliability layer used by the pipeline.

## Testing

```bash
pytest tests/ -v
pytest tests/ --cov=researcher_support_agent
```

## Linting

```bash
ruff check .
ruff format .
```

## License

MIT
