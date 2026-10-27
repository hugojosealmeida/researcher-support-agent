"""research-pipeline: an 8-phase academic research pipeline.

Phases
------
1. Research Topic & Planning
2. Literature Search
3. Paper Ingestion & Markdown
4. Paper Summarization
5. Literature Synthesis
6. Review Paper Writing
7. Academic Review
8. Revision & Release

Usage
-----
    from research_pipeline import Pipeline

    pipeline = Pipeline()
    # Run a single phase
    pipeline.run_phase("literature_search", context=research_context)

    # Run the full workflow
    pipeline.run_full(research_context)

    # Resume from a specific phase
    pipeline.run_from("paper_summarization", context=research_context)
"""

from research_pipeline.agent_base import PipelineAgent
from research_pipeline.pipeline import Pipeline
from research_pipeline.state import PipelineState

__all__ = [
    "Pipeline",
    "PipelineAgent",
    "PipelineState",
]
