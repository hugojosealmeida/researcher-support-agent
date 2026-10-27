<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
"""Evidence and review models."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

from .common import Status, generate_id


class Evidence(BaseModel):
    """A piece of evidence extracted from one or more papers."""

    model_config = ConfigDict(validate_default=True)

    id: str = Field(default_factory=generate_id)
    claim: str = Field(..., min_length=1, description="The claim or finding")
    supporting_paper_ids: list[str] = Field(default_factory=list)
    strength: str | None = None  # e.g. "strong", "moderate", "weak"
    context: str | None = None
    confidence: float | None = Field(None, ge=0.0, le=1.0)
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @field_validator("claim")
    @classmethod
    def claim_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("claim must not be blank")
        return v


class ReviewFinding(BaseModel):
    """A finding from the academic review / quality audit phase."""

    model_config = ConfigDict(validate_default=True)

    id: str = Field(default_factory=generate_id)
    category: str = Field(..., min_length=1)  # e.g. "abstract", "citations", "claims"
    severity: str = Field(
        ..., min_length=1
    )  # "critical", "major", "minor", "suggestion"
    description: str = Field(..., min_length=1)
    location: str | None = None  # section or paragraph reference
    resolution: str | None = None
    status: Status = Status.PENDING
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @field_validator("category")
    @classmethod
    def category_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("category must not be blank")
        return v

    @field_validator("severity")
    @classmethod
    def severity_valid(cls, v: str) -> str:
        valid = {"critical", "major", "minor", "suggestion"}
        if v not in valid:
            raise ValueError(f"severity must be one of {valid}")
        return v
=======
"""Evidence and review finding models."""

from __future__ import annotations

=======
=======
>>>>>>> 10d6757 (fix: Phase D — Manuscript production and quality control (#5))
=======
>>>>>>> 3eda405 (fix: Phase E — Reliability, Git integration and release (#6))
"""Evidence and review finding models.

Extended with paper summaries, extracted claims, citation records,
and synthesis models for Phase C (evidence extraction and synthesis).
"""

from __future__ import annotations

<<<<<<< HEAD
<<<<<<< HEAD
from datetime import datetime, timezone
from enum import Enum
>>>>>>> 1123db3 (fix: Phase C — Evidence extraction and synthesis (#4))
from typing import List, Optional
=======
from datetime import UTC, datetime
from enum import Enum
>>>>>>> 10d6757 (fix: Phase D — Manuscript production and quality control (#5))
=======
from datetime import UTC, datetime
from enum import Enum
>>>>>>> 3eda405 (fix: Phase E — Reliability, Git integration and release (#6))

from pydantic import BaseModel, Field


<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
=======
=======
>>>>>>> 10d6757 (fix: Phase D — Manuscript production and quality control (#5))
=======
>>>>>>> 3eda405 (fix: Phase E — Reliability, Git integration and release (#6))
class EvidenceStrength(str, Enum):
    STRONG = "strong"
    MODERATE = "moderate"
    WEAK = "weak"


<<<<<<< HEAD
<<<<<<< HEAD
>>>>>>> 1123db3 (fix: Phase C — Evidence extraction and synthesis (#4))
=======
>>>>>>> 10d6757 (fix: Phase D — Manuscript production and quality control (#5))
=======
>>>>>>> 3eda405 (fix: Phase E — Reliability, Git integration and release (#6))
class Evidence(BaseModel):
    """A piece of evidence linking a claim to supporting papers."""

    claim: str = Field(..., min_length=1)
    supporting_paper_ids: list[str] = Field(default_factory=list)
    strength: str = Field(default="weak")
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)


class ReviewFinding(BaseModel):
    """A finding from a quality or bias review."""

    category: str = Field(..., min_length=1)
    severity: str = Field(default="low")
    description: str = Field(..., min_length=1)
<<<<<<< HEAD
<<<<<<< HEAD
    resolution: Optional[str] = Field(default=None)
<<<<<<< HEAD
>>>>>>> e45cda7 (fix: Phase B — Literature discovery and ingestion (#3))
=======
    paper_id: Optional[str] = Field(default=None)
=======
    resolution: str | None = Field(default=None)
    paper_id: str | None = Field(default=None)
>>>>>>> 10d6757 (fix: Phase D — Manuscript production and quality control (#5))
=======
    resolution: str | None = Field(default=None)
    paper_id: str | None = Field(default=None)
>>>>>>> 3eda405 (fix: Phase E — Reliability, Git integration and release (#6))


# ---------------------------------------------------------------------------
# Paper Summary (Phase C)
# ---------------------------------------------------------------------------


class EvidencePointer(BaseModel):
    """Points to a specific location within a paper."""

    paper_id: str = Field(..., description="The paper this pointer references")
<<<<<<< HEAD
<<<<<<< HEAD
    section: Optional[str] = Field(default=None)
    page: Optional[int] = Field(default=None)
    table: Optional[str] = Field(default=None)
    figure: Optional[str] = Field(default=None)
=======
=======
>>>>>>> 3eda405 (fix: Phase E — Reliability, Git integration and release (#6))
    section: str | None = Field(default=None)
    page: int | None = Field(default=None)
    table: str | None = Field(default=None)
    figure: str | None = Field(default=None)
<<<<<<< HEAD
>>>>>>> 10d6757 (fix: Phase D — Manuscript production and quality control (#5))
=======
>>>>>>> 3eda405 (fix: Phase E — Reliability, Git integration and release (#6))
    description: str = Field(
        ..., min_length=1, description="What this pointer points to"
    )


class ResearchNote(BaseModel):
    """A consistent research note for a single paper.

    Acceptance criteria:
    - Distinguishes author-reported findings from the agent's interpretation.
    - Missing information is marked as "Unknown" rather than invented.
    - Includes evidence pointers to sections, pages, tables, or figures.
    """

    paper_id: str = Field(..., description="Unique identifier for the paper")
    title: str = Field(..., min_length=1)
<<<<<<< HEAD
<<<<<<< HEAD
    year: Optional[int] = Field(default=None)
=======
    year: int | None = Field(default=None)
>>>>>>> 10d6757 (fix: Phase D — Manuscript production and quality control (#5))
=======
    year: int | None = Field(default=None)
>>>>>>> 3eda405 (fix: Phase E — Reliability, Git integration and release (#6))

    # --- Author-reported content (extracted from the paper) ---
    research_question: str = Field(
        default="Unknown", description="The paper's stated research question"
    )
    motivation: str = Field(
        default="Unknown", description="Why the authors undertook this work"
    )
    methodology: str = Field(
        default="Unknown", description="Methods used by the authors"
    )
    data_and_sample: str = Field(
        default="Unknown", description="Data sources and sample description"
    )
    main_results: str = Field(
        default="Unknown", description="Key findings reported by the authors"
    )
    quantitative_findings: str = Field(
        default="Unknown", description="Specific numerical/statistical results"
    )
    contributions: str = Field(
        default="Unknown", description="Authors' claimed contributions"
    )
    limitations: str = Field(
        default="Unknown", description="Authors' stated limitations"
    )

    # --- Agent interpretation (clearly separated) ---
    open_questions: str = Field(
        default="Unknown", description="Open questions identified by the agent"
    )
    relevance_to_review: str = Field(
        default="Unknown", description="Agent's assessment of relevance to the review"
    )
    agent_interpretation: str = Field(
        default="Unknown", description="Agent's own interpretation of the paper"
    )

    # --- Evidence pointers ---
    evidence_pointers: list[EvidencePointer] = Field(
        default_factory=list,
        description="Pointers to specific sections/pages/tables/figures",
    )

    # --- Metadata ---
    created_at: datetime = Field(
<<<<<<< HEAD
<<<<<<< HEAD
        default_factory=lambda: datetime.now(timezone.utc)
=======
        default_factory=lambda: datetime.now(UTC)
>>>>>>> 10d6757 (fix: Phase D — Manuscript production and quality control (#5))
=======
        default_factory=lambda: datetime.now(UTC)
>>>>>>> 3eda405 (fix: Phase E — Reliability, Git integration and release (#6))
    )

    def to_markdown(self) -> str:
        """Render the research note as a Markdown string."""
        lines = [
            f"## {self.title}",
            f"**Paper ID:** {self.paper_id}",
            f"**Year:** {self.year or 'Unknown'}",
            "",
            "### Research Question and Motivation (Author-reported)",
            f"**Research Question:** {self.research_question}",
            f"**Motivation:** {self.motivation}",
            "",
            "### Methodology, Data, and Sample (Author-reported)",
            f"**Methodology:** {self.methodology}",
            f"**Data and Sample:** {self.data_and_sample}",
            "",
            "### Main Results and Quantitative Findings (Author-reported)",
            f"**Main Results:** {self.main_results}",
            f"**Quantitative Findings:** {self.quantitative_findings}",
            "",
            "### Contributions and Limitations (Author-reported)",
            f"**Contributions:** {self.contributions}",
            f"**Limitations:** {self.limitations}",
            "",
            "### Open Questions and Relevance (Agent interpretation)",
            f"**Open Questions:** {self.open_questions}",
            f"**Relevance to Review:** {self.relevance_to_review}",
            "",
            "### Agent Interpretation",
            self.agent_interpretation,
        ]
        if self.evidence_pointers:
            lines.append("")
            lines.append("### Evidence Pointers")
            for ptr in self.evidence_pointers:
                location_parts = []
                if ptr.section:
                    location_parts.append(f"Section: {ptr.section}")
                if ptr.page:
                    location_parts.append(f"Page: {ptr.page}")
                if ptr.table:
                    location_parts.append(f"Table: {ptr.table}")
                if ptr.figure:
                    location_parts.append(f"Figure: {ptr.figure}")
                location = ", ".join(location_parts) if location_parts else "N/A"
                lines.append(f"- **{ptr.description}** [{location}] (Paper: {ptr.paper_id})")

        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Extracted Claims (Phase C)
# ---------------------------------------------------------------------------


class ClaimType(str, Enum):
    EMPIRICAL = "empirical"
    THEORETICAL = "theoretical"
    METHODODOGICAL = "methodological"
    CLAIMS = "claims"


class ExtractedClaim(BaseModel):
    """A claim extracted from a paper that can be traced back to source evidence.

    Acceptance criteria:
    - Every substantive statement can be traced back to its supporting paper(s).
    """

    claim_text: str = Field(..., min_length=1, description="The substantive claim")
    claim_type: ClaimType = Field(
        default=ClaimType.EMPIRICAL, description="Type of the claim"
    )
    paper_id: str = Field(
        ..., description="The paper from which this claim was extracted"
    )
    supporting_evidence: list[str] = Field(
        default_factory=list,
        description="Direct quotes or references that support this claim",
    )
    confidence: float = Field(
        default=0.0, ge=0.0, le=1.0, description="Confidence in this claim"
    )


# ---------------------------------------------------------------------------
# Citation Records (Phase C)
# ---------------------------------------------------------------------------


class CitationRecord(BaseModel):
    """A record of a citation relationship between papers."""

    citing_paper_id: str = Field(..., description="The paper that cites")
    cited_paper_id: str = Field(..., description="The paper being cited")
    context: str = Field(
        default="", min_length=0, description="Context in which the citation appears"
    )
<<<<<<< HEAD
<<<<<<< HEAD
>>>>>>> 1123db3 (fix: Phase C — Evidence extraction and synthesis (#4))
=======
>>>>>>> 10d6757 (fix: Phase D — Manuscript production and quality control (#5))
=======
>>>>>>> 3eda405 (fix: Phase E — Reliability, Git integration and release (#6))
