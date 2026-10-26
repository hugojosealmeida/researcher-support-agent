"""Paper, Author, Citation, and PaperSummary models."""

from __future__ import annotations

from pydantic import BaseModel, Field


class Author(BaseModel):
    """A paper author."""

    full_name: str = Field(..., min_length=1)
    orcid: str | None = Field(default=None)
    affiliation: str | None = Field(default=None)


class Citation(BaseModel):
    """A bibliographic citation string."""

    key: str = Field(..., min_length=1)
    raw: str = Field(..., min_length=1)
    year: int | None = Field(default=None)
    title: str | None = Field(default=None)


class PaperSummary(BaseModel):
    """A brief analytical summary of a single paper."""

    paper_id: str = Field(..., description="Unique identifier for the paper")
    key_findings: list[str] = Field(default_factory=list)
    methods: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)
    relevance_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Relevance to research question")


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
    year: int | None = Field(default=None)
    venue: str | None = Field(default=None)
    doi: str | None = Field(default=None)
    pmid: str | None = Field(default=None)
    arxiv_id: str | None = Field(default=None)
    source_id: str | None = Field(default=None)  # source-specific ID
    abstract: str | None = Field(default=None)
    url: str | None = Field(default=None)
    retrieval_status: str = Field(default=PaperStatus.RETRIEVED)
    processing_status: str = Field(default=PaperStatus.PENDING)
    summary: PaperSummary | None = Field(default=None)
    citations: list[Citation] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict, description="Raw or supplemental metadata from source")

    def get_identifier(self) -> str | None:
        """Return the best available stable identifier."""
        if self.doi:
            return self.doi
        if self.pmid:
            return self.pmid
        if self.arxiv_id:
            return self.arxiv_id
        return None
