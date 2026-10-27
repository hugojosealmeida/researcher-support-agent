"""Agents package."""

from .academic_reviewer import AcademicReviewer
from .literature_synthesis import (
    LiteratureSynthesisAgent,
    SynthesisFinding,
    SynthesisFindingType,
    SynthesisMatrix,
    SynthesisResult,
)
from .manuscript_writer import ManuscriptWriter, ManuscriptWritingResult
from .paper_search import (
    PaperSearchAgent,
    PaperSearchResult,
    SourceAdapter,
    deduplicate_papers,
)
from .paper_summarizer import PaperSummaryConfig, summarize_paper, summarize_papers
from .research_planner import ResearchPlanner
from .revision_agent import RevisionAgent, RevisionLoopResult
from .screening_agent import ScreeningAgent
