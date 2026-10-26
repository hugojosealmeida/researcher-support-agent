"""Agents package."""

from .academic_reviewer import AcademicReviewer
from .literature_synthesis import LiteratureSynthesisAgent, SynthesisResult
from .manuscript_writer import ManuscriptWriter, ManuscriptWritingResult
from .paper_search import PaperSearchAgent, PaperSearchResult
from .paper_summarizer import PaperSummaryConfig, summarize_paper, summarize_papers
from .research_planner import ResearchPlanner
from .revision_agent import RevisionAgent, RevisionLoopResult
from .screening_agent import ScreeningAgent
