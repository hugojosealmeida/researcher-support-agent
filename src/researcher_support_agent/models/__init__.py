"""Model package — re-exports all domain models for convenient imports."""

from .common import (
    IdentifierType,
    RetrievalStatus,
    Status,
    generate_id,
    normalize_arxiv_id,
    normalize_doi,
)
from .evidence import Evidence, ReviewFinding
from .manuscript import Manuscript
from .paper import Author, Citation, Paper, PaperSummary
from .project import ResearchProject, ResearchQuestion
from .query import SearchQuery

__all__ = [
    "Author",
    "Citation",
    "Evidence",
    "IdentifierType",
    "Manuscript",
    "Paper",
    "PaperSummary",
    "ResearchProject",
    "ResearchQuestion",
    "RetrievalStatus",
    "ReviewFinding",
    "SearchQuery",
    "Status",
    "generate_id",
    "normalize_arxiv_id",
    "normalize_doi",
]
