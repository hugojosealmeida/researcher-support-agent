"""Paper, Author, Citation, and PaperSummary models."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class Author(BaseModel):
    """A paper author."""

    full_name: str = Field(..., min_length=1)
    orcid: Optional[str] = Field(default=None)
    affiliation: Optional[str] = Field(default=None)


class Citation(BaseModel):
    """A bibliographic citation string."""

    key: str = Field(..., min_length=1)
    raw: str = Field(..., min_length=1)
    year: Optional[int] = Field(default=None)
    title: Optional[str] = Field(default=None)


class PaperSummary(BaseModel):
    """A brief analytical summary of a single paper."""

    paper_id: str = Field(..., description="Unique identifier for the paper")
    key_findings: list[str] = Field(default_factory=list)
    methods: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)
    relevance_score: float = Field(
        default=0.0, ge=0.0, le=1.0, description="Relevance to research question"
    )


class PaperStatus(str):
    """Enumeration of possible paper processing statuses."""

    RETRIEVED = "retrieved"
    SCREENED = "screened"
    EXCLUDED = "excluded"
    INCLUDED = "included"
    CONSUMED = "consumed"
    PENDING = "pending"


class Paper(BaseModel):
    """A scholarly work with bibliographic metadata."""

    title: str = Field(..., min_length=1)
    authors: list[Author] = Field(default_factory=list)
    year: Optional[int] = Field(default=None)
    venue: Optional[str] = Field(default=None)
    doi: Optional[str] = Field(default=None)
    pmid: Optional[str] = Field(default=None)
    arxiv_id: Optional[str] = Field(default=None)
    source_id: Optional[str] = Field(default=None)  # source-specific ID
    abstract: Optional[str] = Field(default=None)
    url: Optional[str] = Field(default=None)
    retrieval_status: str = Field(default=PaperStatus.RETRIEVED)
    processing_status: str = Field(default=PaperStatus.PENDING)
    summary: Optional[PaperSummary] = Field(default=None)
    citations: list[Citation] = Field(default_factory=list)
    metadata: dict = Field(
        default_factory=dict, description="Raw or supplemental metadata from source"
    )

    def get_identifier(self) -> Optional[str]:
        """Return the best available stable identifier."""
        if self.doi:
            return self.doi
        if self.pmid:
            return self.pmid
        if self.arxiv_id:
            return self.arxiv_id
        return None
