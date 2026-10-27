<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
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
=======
"""Data models package."""

from .common import Status, make_id, now_utc
from .evidence import Evidence, ReviewFinding
from .manuscript import Manuscript
from .paper import (
    Author,
    Citation,
    Paper,
    PaperStatus,
    PaperSummary,
)
from .pdf_conversion import (
    ExtractionWarning,
    PDFConversionResult,
)
from .project import ProjectStatus, ResearchProject
from .query import SearchQuery
from .research_plan import (
    ProtocolApproval,
    ResearchPlan,
    ResearchQuestion,
)
from .screening import ScreeningDecision, ScreeningResult
>>>>>>> e45cda7 (fix: Phase B — Literature discovery and ingestion (#3))

__all__ = [
    "Author",
    "Citation",
    "Evidence",
<<<<<<< HEAD
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
=======
    "ExtractionWarning",
    "Manuscript",
    "Paper",
    "PaperStatus",
    "PaperSummary",
    "PDFConversionResult",
    "ProjectStatus",
    "ProtocolApproval",
    "ResearchPlan",
    "ResearchProject",
    "ResearchQuestion",
    "ReviewFinding",
    "ScreeningDecision",
    "ScreeningResult",
    "SearchQuery",
    "Status",
    "make_id",
    "now_utc",
>>>>>>> e45cda7 (fix: Phase B — Literature discovery and ingestion (#3))
]
=======
"""Data models package."""

=======
=======
>>>>>>> 3eda405 (fix: Phase E — Reliability, Git integration and release (#6))
"""Data models package."""

from .citation import (
    Bibliography,
    DOIResolutionResult,
    ReferenceFormat,
    ReferenceRecord,
)
from .common import Status, make_id, now_utc
<<<<<<< HEAD
>>>>>>> 10d6757 (fix: Phase D — Manuscript production and quality control (#5))
=======
>>>>>>> 3eda405 (fix: Phase E — Reliability, Git integration and release (#6))
from .evidence import (
    Evidence,
    EvidencePointer,
    EvidenceStrength,
    ExtractedClaim,
    ResearchNote,
    ReviewFinding,
)
from .evidence_store import EvidenceRepository
<<<<<<< HEAD
<<<<<<< HEAD
from .paper import Author, Citation, Paper, PaperStatus, PaperSummary
from .project import ProjectStatus, ResearchProject
from .query import SearchQuery
from .screening import ScreeningDecision, ScreeningResult
>>>>>>> 1123db3 (fix: Phase C — Evidence extraction and synthesis (#4))
=======
=======
>>>>>>> 3eda405 (fix: Phase E — Reliability, Git integration and release (#6))
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
<<<<<<< HEAD
>>>>>>> 10d6757 (fix: Phase D — Manuscript production and quality control (#5))
=======
>>>>>>> 3eda405 (fix: Phase E — Reliability, Git integration and release (#6))
