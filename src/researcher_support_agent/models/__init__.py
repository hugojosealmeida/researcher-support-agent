"""Data models package."""

from .citation import (
    Bibliography,
    DOIResolutionResult,
    ReferenceFormat,
    ReferenceRecord,
)
from .common import Status, make_id, now_utc
from .evidence import (
    Evidence,
    EvidencePointer,
    EvidenceStrength,
    ExtractedClaim,
    ResearchNote,
    ReviewFinding,
)
from .evidence_store import EvidenceRepository
from .manuscript import (
    Manuscript,
    ManuscriptSection,
    ManuscriptTemplate,
    SectionTemplate,
)
from .paper import Author, Citation, Paper, PaperStatus, PaperSummary
from .project import ProjectStatus, ResearchProject
from .query import SearchQuery
from .reviewer import (
    ReviewCriteria,
    ReviewPass,
    ReviewReport,
    Severity,
)
from .reviewer import (
    ReviewFinding as AcademicReviewFinding,
)
from .screening import ScreeningDecision, ScreeningResult
