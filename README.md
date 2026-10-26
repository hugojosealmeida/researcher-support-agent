# Researcher Support Agent

An intelligent research support agent that guides users through systematic literature reviews.

## Features

- **Typed data models** with Pydantic — validated, serializable, and reusable
- **CLI with Typer** — intuitive commands for running phases and checking system health
- **Structured logging** via structlog — console and file output with ISO timestamps
- **Workflow orchestrator** — owns phase order, retries, state transitions, and checkpoints
- **Phase independence** — any phase can run standalone; failed phases resume without repeating completed work
- **Stable identifiers** — papers track DOI, PMID, arXiv ID, and source-specific IDs

## Installation

```bash
# Create a virtual environment
uv venv
source .venv/bin/activate

# Install in development mode with test dependencies
uv pip install -e ".[dev]"
```

## Usage

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
```

## Architecture

```
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
