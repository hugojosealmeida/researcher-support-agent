# Researcher Support Agent

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

## Installation

```bash
pip install -e .
```

With test dependencies:

```bash
pip install -e ".[test]"
```

## Usage

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
```

## Architecture

```
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

## Testing

```bash
pip install -e ".[test]"
pytest tests/
```

## License

MIT
