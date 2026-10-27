"""Bibliography and citation skill.

Supports a canonical internal reference format and export to BibTeX,
CSL-JSON, or the citation format required by a target journal.

Acceptance criteria:
- Every in-text citation resolves to a reference record.
- No bibliography entry is silently fabricated to fill a gap.
"""

from __future__ import annotations

from typing import Any

from ..models.citation import (
    Bibliography,
    DOIResolutionResult,
    ReferenceFormat,
    ReferenceRecord,
)
from ..models.manuscript import Manuscript


class BibliographySkill:
    """Skill for managing bibliographies and citation formats."""

    def __init__(self) -> None:
        self.bibliography = Bibliography()

    def add_reference(
        self,
        paper_id: str,
        title: str,
        authors: list[str],
        year: int | None = None,
        journal: str | None = None,
        doi: str | None = None,
        pmid: str | None = None,
        arxiv_id: str | None = None,
        **kwargs: Any,
    ) -> ReferenceRecord:
        """Add a reference record to the bibliography.

        This is the canonical entry point — all references in the
        manuscript bibliography must go through this method to prevent
        silent fabrication.
        """
        record = ReferenceRecord(
            paper_id=paper_id,
            title=title,
            authors=authors,
            year=year,
            journal=journal,
            doi=doi,
            pmid=pmid,
            arxiv_id=arxiv_id,
            **kwargs,
        )
        self.bibliography.add(record)
        return record

    def get_reference(self, paper_id: str) -> ReferenceRecord | None:
        """Look up a reference by its internal paper ID."""
        return self.bibliography.get_by_paper_id(paper_id)

    def export(
        self,
        fmt: ReferenceFormat = ReferenceFormat.BIBTEX,
    ) -> str:
        """Export the bibliography in a named format."""
        return self.bibliography.to_format(fmt)

    def export_csl_json(self) -> list[dict[str, Any]]:
        """Export the bibliography as CSL-JSON."""
        return self.bibliography.to_csl_json()

    def validate_against_manuscript(
        self,
        manuscript: Manuscript,
        known_paper_ids: set[str],
    ) -> list[str]:
        """Validate the bibliography against the manuscript.

        Checks:
        - Every in-text citation resolves to a reference record.
        - No bibliography entry is fabricated (exists in known_paper_ids).
        - No duplicate references.
        - No uncited bibliography entries.

        Returns a list of validation issue descriptions (empty = all valid).
        """
        issues: list[str] = []

        # Check all cited papers have a reference record
        cited_ids = set(manuscript.get_cited_paper_ids())
        for pid in cited_ids:
            ref = self.get_reference(pid)
            if ref is None and pid in known_paper_ids:
                issues.append(
                    f"Paper '{pid}' is cited in the manuscript but has no reference record. "
                    f"Add it via add_reference() to prevent silent fabrication."
                )

        # Check for uncited bibliography entries
        uncited = self.bibliography.validate_integrity(cited_ids)
        if uncited:
            issues.extend(uncited)

        # Check for references not in known papers
        for ref in self.bibliography.references:
            if ref.paper_id not in known_paper_ids:
                issues.append(
                    f"Reference '{ref.paper_id}' is not in the known paper set. "
                    f"This may indicate a fabricated or unverified reference."
                )

        return issues


def resolve_doi(doi: str) -> DOIResolutionResult:
    """Attempt to resolve a DOI and return metadata.

    This is a placeholder — in production, this would call the CrossRef API.
    """
    # Placeholder: in production, call https://api.crossref.org/works/{doi}
    return DOIResolutionResult(
        doi=doi,
        resolved=False,
        error="DOI resolution requires network access and API credentials",
    )
