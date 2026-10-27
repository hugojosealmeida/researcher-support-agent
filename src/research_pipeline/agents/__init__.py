"""Agent package — exposes the base class and all phase agents."""

from research_pipeline.agent_base import PipelineAgent
from research_pipeline.agents.academic_reviewer_agent import AcademicReviewerAgent
from research_pipeline.agents.literature_search_agent import LiteratureSearchAgent
from research_pipeline.agents.literature_synthesis_agent import LiteratureSynthesisAgent
from research_pipeline.agents.paper_ingestion_agent import PaperIngestionAgent
from research_pipeline.agents.paper_summarization_agent import PaperSummarizationAgent
from research_pipeline.agents.planning_agent import PlanningAgent
from research_pipeline.agents.review_paper_writer_agent import ReviewPaperWriterAgent
from research_pipeline.agents.revision_release_agent import RevisionReleaseAgent

__all__ = [
    "AcademicReviewerAgent",
    "LiteratureSearchAgent",
    "LiteratureSynthesisAgent",
    "PaperIngestionAgent",
    "PaperSummarizationAgent",
    "PipelineAgent",
    "PlanningAgent",
    "ReviewPaperWriterAgent",
    "RevisionReleaseAgent",
]
