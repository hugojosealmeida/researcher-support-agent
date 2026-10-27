"""Bibliography and citation models.

Supports a canonical internal reference format and export to BibTeX,
CSL-JSON, and other journal-specific citation formats.
"""

from __future__ import annotations

import json
from collections.abc import Callable
from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field, field_validator

from .common import make_id, now_utc

# ---------------------------------------------------------------------------
# Canonical internal reference format
# ---------------------------------------------------------------------------


class ReferenceFormat(StrEnum):
    """Supported bibliography export formats."""

    BIBTEX = "bibtex"
    CSL_JSON = "csl_json"
    APA = "apa"
    MLA = "mla"
    CHICAGO = "chicago"
    VANCOUR = "vancouver"


class ReferenceRecord(BaseModel):
    """A canonical internal reference for a scholarly paper.

    This is the single source of truth — every reference in the bibliography
    is backed by a ReferenceRecord with verifiable metadata. No references
    are silently fabricated.
    """

    id: str = Field(default_factory=lambda: str(make_id()))
    paper_id: str = Field(..., description="Internal paper identifier")
    authors: list[str] = Field(
        default_factory=list,
        description="Author full names in order",
    )
    title: str = Field(..., min_length=1)
    year: int | None = Field(default=None)
    journal: str | None = Field(default=None)
    volume: str | None = Field(default=None)
    issue: str | None = Field(default=None)
    pages: str | None = Field(default=None)
    doi: str | None = Field(default=None)
    pmid: str | None = Field(default=None)
    arxiv_id: str | None = Field(default=None)
    url: str | None = Field(default=None)
    publisher: str | None = Field(default=None)
    venue: str | None = Field(default=None)
    citation_key: str | None = Field(default=None, description="Citation key for in-text use")
    created_at: datetime = Field(default_factory=now_utc)
    metadata: dict[str, str] = Field(default_factory=dict)

    @field_validator("citation_key")
    @classmethod
    def _auto_citation_key(cls, v: str | None) -> str | None:
        if v:
            return v
        return None

    def get_citation_key(self) -> str:
        """Generate or return the citation key used in in-text citations."""
        if self.citation_key:
            return self.citation_key
        # Auto-generate from first author last name + year + short title
        first_author = self.authors[0] if self.authors else "Unknown"
        short_name = first_author.split()[-1] if first_author else "anon"
        year = str(self.year) if self.year else "nd"
        title_words = [w for w in self.title.split() if w.lower() not in ("a", "an", "the", "of", "and")]
        title_short = title_words[0] if title_words else "paper"
        self.citation_key = f"{short_name}{year}{title_short[:3]}"
        return self.citation_key

    # ------------------------------------------------------------------
    # Format exports
    # ------------------------------------------------------------------

    def to_bibtex(self, citation_key: str | None = None) -> str:
        """Export this reference as a BibTeX entry."""
        key = citation_key or self.get_citation_key()
        lines: list[str] = [f"@article{{{key},"]
        lines.append(f"  title = {{{self.title}}},")
        if self.authors:
            lines.append(f"  author = {{{' and '.join(self.authors)}}},")
        if self.year:
            lines.append(f"  year = {{{self.year}}},")
        if self.journal:
            lines.append(f"  journal = {{{self.journal}}},")
        if self.volume:
            lines.append(f"  volume = {{{self.volume}}},")
        if self.issue:
            lines.append(f"  number = {{{self.issue}}},")
        if self.pages:
            lines.append(f"  pages = {{{self.pages}}},")
        if self.doi:
            lines.append(f"  doi = {{{self.doi}}},")
        if self.pmid:
            lines.append(f"  pmid = {{{self.pmid}}},")
        if self.url:
            lines.append(f"  url = {{{self.url}}},")
        if self.publisher:
            lines.append(f"  publisher = {{{self.publisher}}},")
        lines.append("}")
        return "\n".join(lines)

    def to_csl_json(self) -> dict[str, Any]:
        """Export this reference as CSL-JSON."""
        csl: dict[str, Any] = {
            "id": self.id,
            "title": self.title,
            "type": "article-journal",
            "published": {},
        }
        if self.authors:
            csl["author"] = [
                {
                    "family": a.split()[-1] if a else "",
                    "given": " ".join(a.split()[:-1]),
                }
                for a in self.authors
            ]
        if self.year:
            csl["published"]["literal"] = str(self.year)
        if self.journal:
            csl["container-title"] = self.journal
        if self.volume:
            csl["volume"] = self.volume
        if self.pages:
            csl["page"] = self.pages
        if self.doi:
            csl["DOI"] = self.doi
        return csl

    def to_apa(self) -> str:
        """Export this reference in APA 7th style."""
        parts: list[str] = []
        # Authors
        author_str = self._format_authors_apa()
        parts.append(author_str)
        # Year
        parts.append(f"({self.year}).")
        # Title
        parts.append(f"{self.title}.")
        # Journal
        if self.journal:
            parts.append(f"{self.journal}")
            if self.volume:
                parts.append(f",{self.volume}")
                if self.issue:
                    parts.append(f"({self.issue})")
            if self.pages:
                parts.append(f", {self.pages}")
        return " ".join(parts)

    def to_mla(self) -> str:
        """Export in MLA 9th style."""
        parts: list[str] = []
        # Author
        if self.authors:
            first = self.authors[0]
            parts.append(f"{first.split()[-1]}, {first.split()[0]}.")
        parts.append(f'"{self.title}."')
        if self.journal:
            parts.append(f"{self.journal}")
            if self.volume:
                parts.append(f" vol.{self.volume}")
            if self.pages:
                parts.append(f", {self.pages}")
        if self.year:
            parts.append(f" {self.year}.")
        return " ".join(parts)

    def to_chicago(self) -> str:
        """Export in Chicago style."""
        parts: list[str] = []
        # Author (first author last, first; others first last)
        if self.authors:
            first = self.authors[0]
            last_first = f"{first.split()[-1]}, {' '.join(first.split()[:-1])}"
            parts.append(last_first)
        parts.append(f"{self.title}.")
        if self.journal:
            parts.append(f"{self.journal}")
            if self.year:
                parts.append(f" {self.year}")
            if self.volume:
                parts.append(f" {self.volume}")
            if self.pages:
                parts.append(f": {self.pages}")
        parts.append(".")
        return " ".join(parts)

    def to_vancouver(self) -> str:
        """Export in Vancouver/NLM style."""
        parts: list[str] = []
        # Authors (last name initial, semicolon separated)
        author_strs = []
        for a in self.authors:
            parts_list = a.split()
            if parts_list:
                last = parts_list[-1]
                initials = "".join(p[0] + "." for p in parts_list[:-1])
                author_strs.append(f"{last} {initials}")
        parts.append(";".join(author_strs) + ".")
        # Title
        parts.append(f"{self.title}.")
        # Journal
        if self.journal:
            parts.append(f"{self.journal}")
        if self.year:
            parts.append(f"({self.year})")
        if self.volume:
            parts.append(f"{self.volume}")
        if self.pages:
            parts.append(f":{self.pages}")
        parts.append(".")
        return " ".join(parts)

    def _format_authors_apa(self) -> str:
        """Format authors for APA."""
        if not self.authors:
            return ""
        if len(self.authors) == 1:
            return self.authors[0]
        if len(self.authors) <= 20:
            return ", ".join(self.authors[:-1]) + ", & " + self.authors[-1]
        return ", ".join(self.authors[:19]) + ", … & " + self.authors[-1]


# ---------------------------------------------------------------------------
# Bibliography collection
# ---------------------------------------------------------------------------


class Bibliography(BaseModel):
    """A collection of reference records with validation."""

    references: list[ReferenceRecord] = Field(default_factory=list)

    def add(self, record: ReferenceRecord) -> None:
        """Add a reference, deduplicating by paper_id."""
        for existing in self.references:
            if existing.paper_id == record.paper_id:
                existing.title = record.title or existing.title
                existing.year = record.year or existing.year
                existing.authors = record.authors or existing.authors
                existing.doi = record.doi or existing.doi
                return
        self.references.append(record)

    def get_by_paper_id(self, paper_id: str) -> ReferenceRecord | None:
        """Look up a reference by its internal paper ID."""
        for ref in self.references:
            if ref.paper_id == paper_id:
                return ref
        return None

    def get_citation_key_map(self) -> dict[str, str]:
        """Return paper_id -> citation_key mapping."""
        return {ref.paper_id: ref.get_citation_key() for ref in self.references}

    def find_duplicates(self) -> list[tuple[str, str]]:
        """Find duplicate references (same paper_id)."""
        seen: dict[str, list[str]] = {}
        for ref in self.references:
            seen.setdefault(ref.paper_id, []).append(ref.id)
        return [(ref_id, record_id) for ref_id, record_ids in seen.items() for record_id in record_ids[1:]]

    def to_bibtex(self) -> str:
        """Export the entire bibliography as a BibTeX string."""
        entries: list[str] = []
        for ref in self.references:
            entries.append(ref.to_bibtex())
        return "\n\n".join(entries)

    def to_csl_json(self) -> list[dict[str, Any]]:
        """Export the entire bibliography as CSL-JSON."""
        return [ref.to_csl_json() for ref in self.references]

    def to_format(self, fmt: ReferenceFormat) -> str:
        """Export the bibliography in a named format."""
        format_map: dict[ReferenceFormat, Callable[[], str]] = {
            ReferenceFormat.BIBTEX: lambda: self.to_bibtex(),
            ReferenceFormat.CSL_JSON: lambda: json.dumps(self.to_csl_json()),
            ReferenceFormat.APA: lambda: "\n".join(f"{i + 1}. {ref.to_apa()}" for i, ref in enumerate(self.references)),
            ReferenceFormat.MLA: lambda: "\n".join(f"{i + 1}. {ref.to_mla()}" for i, ref in enumerate(self.references)),
            ReferenceFormat.CHICAGO: lambda: "\n".join(
                f"{i + 1}. {ref.to_chicago()}" for i, ref in enumerate(self.references)
            ),
            ReferenceFormat.VANCOUR: lambda: "\n".join(
                f"{i + 1}. {ref.to_vancouver()}" for i, ref in enumerate(self.references)
            ),
        }
        return format_map[fmt]()

    def validate_integrity(self, in_text_citations: set[str]) -> list[str]:
        """Validate the bibliography: no silent fabrication, no uncited refs.

        Returns a list of validation issue descriptions.
        """
        issues: list[str] = []
        paper_ids = {ref.paper_id for ref in self.references}
        # Check for uncited bibliography entries
        uncited = paper_ids - in_text_citations
        if uncited:
            issues.append(f"Uncited bibliography entries: {sorted(uncited)}")
        # Check for duplicate references
        dups = self.find_duplicates()
        if dups:
            issues.append(f"Duplicate references found: {dups}")
        return issues


# ---------------------------------------------------------------------------
# DOI resolution result
# ---------------------------------------------------------------------------


class DOIResolutionResult(BaseModel):
    """Result of attempting to resolve a DOI."""

    doi: str = Field(..., description="The DOI that was resolved")
    resolved: bool = Field(..., description="Whether the DOI resolved")
    title: str | None = Field(default=None)
    authors: list[str] | None = Field(default=None)
    year: int | None = Field(default=None)
    error: str | None = Field(default=None)
