# Researcher Support Agent

<<<<<<< HEAD
<<<<<<< HEAD
An 8-phase academic research pipeline with independently runnable agents. Each phase can be executed in isolation or as part of the full workflow.

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
=======
An intelligent research support agent that guides users through systematic literature reviews.

## Features

- **Typed data models** with Pydantic — validated, serializable, and reusable
- **CLI with Typer** — intuitive commands for running phases and checking system health
- **Structured logging** via structlog — console and file output with ISO timestamps
- **Workflow orchestrator** — owns phase order, retries, state transitions, and checkpoints
- **Phase independence** — any phase can run standalone; failed phases resume without repeating completed work
- **Stable identifiers** — papers track DOI, PMID, arXiv ID, and source-specific IDs
>>>>>>> 2ff0702 (fix: Phase A — Foundation and architecture (#2))

## Installation

```bash
<<<<<<< HEAD
pip install -e .
```

With test dependencies:

```bash
pip install -e ".[test]"
=======
# Create a virtual environment
uv venv
source .venv/bin/activate

# Install in development mode with test dependencies
uv pip install -e ".[dev]"
>>>>>>> 2ff0702 (fix: Phase A — Foundation and architecture (#2))
```

## Usage

<<<<<<< HEAD
### Running the full pipeline

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

### Running a single phase

```python
state = pipeline.run_phase("literature_search")
```

### Running from a specific phase onward

Useful when state from earlier phases already exists and you want to regenerate downstream results (e.g. re-summarize papers after changing a prompt).

```python
state = pipeline.run_from("paper_summarization")
```

### Manual state persistence

State is automatically saved to the configured JSON file after each phase. You can also manage it manually:

```python
pipeline.save_state()          # write current state to file
state = pipeline.load_state()  # load state from file
```

### Direct state access

```python
from research_pipeline.state import PipelineState

state = PipelineState(topic="My Topic")
state.save("my_state.json")

loaded = PipelineState.load("my_state.json")
=======
### Doctor command

Verify your environment, dependencies, and models:

```bash
research doctor
research doctor -v  # verbose: shows JSON serialization sample
```

### Run command

Execute the research pipeline:

```bash
research run                    # Run all phases
research run --phase search     # Run a single phase
research run --from synthesize  # Resume from a specific phase
research run --state state.json # Use a custom state file
research run --dry-run          # Validate without executing
```

### List phases

```bash
research run list-phases
```

### Version

```bash
research version
>>>>>>> 2ff0702 (fix: Phase A — Foundation and architecture (#2))
```

## Architecture

```
<<<<<<< HEAD
research_pipeline/
├── __init__.py           # Public API exports
├── state.py              # Data models: PipelineState, SearchItem, Paper, Summary, ReviewComment
├── pipeline.py           # Pipeline orchestrator
├── agents.py             # Abstract PipelineAgent base class
└── agents/
    ├── __init__.py
    ├── planning_agent.py
    ├── literature_search_agent.py
    ├── paper_ingestion_agent.py
    ├── paper_summarization_agent.py
    ├── literature_synthesis_agent.py
    ├── review_paper_writer_agent.py
    ├── academic_reviewer_agent.py
    └── revision_release_agent.py
```

### State model

`PipelineState` is a mutable dataclass that flows through every phase. Each agent reads from it, performs its work, and writes results back. The shared state is persisted to JSON after every phase so that any phase can be re-run without repeating earlier work.

### Extending the pipeline

To add a new agent:

1. Create a subclass of `PipelineAgent` in `src/research_pipeline/agents/`.
2. Implement `run(self, state: PipelineState) -> PipelineState`.
3. Add the phase name to `VALID_PHASES` in `Pipeline`.
4. Register the agent with `pipeline.register_agent(my_agent)`.
=======
┌──────────────────────────────────────────────────┐
│                    CLI (Typer)                    │
│  ┌──────────┐  ┌──────────────┐  ┌───────────┐  │
│  │  doctor  │  │     run      │  │  version  │  │
│  └────┬─────┘  └──────┬───────┘  └───────────┘  │
└───────┼───────────────┼─────────────────────────┘
        │               │
        ▼               ▼
┌──────────────────────────────────────────────────┐
│              Workflow Orchestrator                │
│  ┌────────┐  ┌──────────┐  ┌────────────────┐   │
│  │ Phases  │  │ Retries  │  │ State / Check  │   │
│  │ Ordered │  │ Config   │  │ point / Persist│   │
│  └────────┘  └──────────┘  └────────────────┘   │
└──────────────────────────────────────────────────┘
        │
        ▼
┌──────────────────────────────────────────────────┐
│             Pydantic Data Models                  │
│  ResearchProject ─→ ResearchQuestion              │
│  Paper ─→ Author, Citation, PaperSummary          │
│  Evidence ─→ ReviewFinding                        │
│  Manuscript ─→ sections, version                  │
│  SearchQuery                                      │
└──────────────────────────────────────────────────┘
```

### Key design decisions

- **Orchestrator owns control flow** — agents are dumb; the orchestrator manages retries, state, and checkpoints.
- **State persistence** — `OrchestratorState` saves/loads from JSON so work is never lost.
- **No LLM coupling** — the foundation works without any model provider. LLM integration comes in later phases.

## Data Models

| Model | Key fields |
|-------|-----------|
| `ResearchProject` | title, description, questions, status |
| `ResearchQuestion` | question, inclusion/exclusion criteria |
| `Paper` | title, authors, year, venue, DOI/PMID/arXiv, retrieval status, processing status |
| `Author` | full_name, orcid, affiliation |
| `Citation` | key, raw string, year, title |
| `PaperSummary` | paper_id, key_findings, methods, limitations, relevance_score |
| `Evidence` | claim, supporting_paper_ids, strength, confidence |
| `ReviewFinding` | category, severity, description, resolution |
| `Manuscript` | sections, version, references |
| `SearchQuery` | query, database, filters, results_count |
>>>>>>> 2ff0702 (fix: Phase A — Foundation and architecture (#2))

## Testing

```bash
<<<<<<< HEAD
pip install -e ".[test]"
pytest tests/
```

## License

MIT
=======
pytest tests/ -v
pytest tests/ --cov=researcher_support_agent
```

## Linting

```bash
ruff check .
ruff format .
```
>>>>>>> 2ff0702 (fix: Phase A — Foundation and architecture (#2))
=======
Researcher Support Agent
>>>>>>> 1123db3 (fix: Phase C — Evidence extraction and synthesis (#4))
