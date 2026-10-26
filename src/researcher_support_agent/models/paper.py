"""Paper-level models: Author, Citation, Paper, PaperSummary."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from .common import (
    IdentifierType,
    RetrievalStatus,
    Status,
    generate_id,
    normalize_arxiv_id,
    normalize_doi,
)


class Author(BaseModel):
    """An author of a paper."""

    model_config = ConfigDict(validate_default=True)

    full_name: str = Field(..., min_length=1)
    orcid: str | None = None
    affiliation: str | None = None
    email: str | None = None

    @field_validator("full_name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("full_name must not be blank")
        return v


class Citation(BaseModel):
    """A citation reference string."""

    model_config = ConfigDict(validate_default=True)

    key: str = Field(..., min_length=1)
    raw: str = Field(..., min_length=1)
    authors: list[str] = Field(default_factory=list)
    year: int | None = None
    title: str | None = None

    def __str__(self) -> str:
        return self.raw


class Paper(BaseModel):
    """A discovered research paper with stable identifiers."""

    model_config = ConfigDict(validate_default=True)

    id: str = Field(default_factory=generate_id)
    title: str = Field(..., min_length=1)
    authors: list[Author] = Field(default_factory=list)
    year: int | None = None
    venue: str | None = None  # journal, conference, preprint server
    doi: str | None = None
    pmid: str | None = None
    arxiv_id: str | None = None
    source_id: str | None = None  # database-specific identifier
    source_url: str | None = None
    abstract: str | None = None
    full_text_path: str | None = None
    retrieval_status: RetrievalStatus = RetrievalStatus.NOT_RETRIEVED
    processing_status: Status = Status.PENDING
    citations: list[Citation] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    retrieved_at: datetime | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @field_validator("title")
    @classmethod
    def title_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("title must not be blank")
        return v

    @field_validator("doi")
    @classmethod
    def normalize_doi_field(cls, v: str | None) -> str | None:
        if v is not None:
            return normalize_doi(v)
        return v

    @field_validator("arxiv_id")
    @classmethod
    def normalize_arxiv_field(cls, v: str | None) -> str | None:
        if v is not None:
            return normalize_arxiv_id(v)
        return v

    @field_validator("pmid")
    @classmethod
    def normalize_pmid_field(cls, v: str | None) -> str | None:
        if v is not None:
            return v.strip()
        return v

    @model_validator(mode="after")
    def set_retrieval_timestamp(self) -> Paper:
        if self.retrieval_status != RetrievalStatus.NOT_RETRIEVED:
            self.retrieved_at = datetime.now(UTC)
        return self

    def get_stable_id(self) -> str | None:
        """Return the first available stable identifier, or None."""
        if self.doi:
            return self.doi
        if self.pmid:
            return self.pmid
        if self.arxiv_id:
            return self.arxiv_id
        return None

    def get_identifier_type(self) -> IdentifierType | None:
        """Return the type of the first available stable identifier."""
        if self.doi:
            return IdentifierType.DOI
        if self.pmid:
            return IdentifierType.PMID
        if self.arxiv_id:
            return IdentifierType.ARXIV
        if self.source_id:
            return IdentifierType.OTHER
        return None

    def is_duplicate_of(self, other: Paper) -> bool:
        """Check if this paper is the same as *other* by stable IDs."""
        my_id = self.get_stable_id()
        other_id = other.get_stable_id()
        if my_id and other_id:
            return my_id.lower() == other_id.lower()
        # Fall back to title+year+author matching
        if (
            self.title
            and other.title
            and self.title.lower() == other.title.lower()
            and self.year
            and other.year
            and self.year == other.year
        ):
            my_names = {a.full_name.lower() for a in self.authors}
            other_names = {a.full_name.lower() for a in other.authors}
            if my_names and other_names and my_names == other_names:
                return True
        return False


class PaperSummary(BaseModel):
    """Structured summary of a paper."""

    model_config = ConfigDict(validate_default=True)

    paper_id: str = Field(..., min_length=1)
    title: str | None = None
    key_findings: list[str] = Field(default_factory=list)
    methods: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)
    relevance_score: float | None = Field(None, ge=0.0, le=1.0)
    notes: str = ""
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
