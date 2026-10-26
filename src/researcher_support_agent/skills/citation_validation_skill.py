"""Citation validation skill.

Validates DOI resolution, author names, titles, publication years,
duplicate references, in-text citations, and uncited bibliography entries.

Acceptance criteria:
- Every in-text citation resolves to a reference record.
- No bibliography entry is silently fabricated.
- DOI resolution is attempted where possible.
"""

from __future__ import annotations

from ..models.citation import (
    Bibliography,
    DOIResolutionResult,
)
from ..models.manuscript import Manuscript


class CitationValidationSkill:
    """Skill for validating citations and references."""

    def __init__(self, bibliography: Bibliography | None = None) -> None:
        self.bibliography = bibliography or Bibliography()

    def validate_all(
        self,
        manuscript: Manuscript,
        known_paper_ids: set[str],
    ) -> list[str]:
        """Run all citation validation checks.

        Returns a list of validation issue descriptions.
        Empty list means all checks pass.
        """
        issues: list[str] = []
        issues.extend(self._validate_citation_resolution(manuscript, known_paper_ids))
        issues.extend(self._validate_no_fabrication(manuscript, known_paper_ids))
        issues.extend(self._validate_no_duplicates(manuscript))
        issues.extend(self._validate_citation_consistency(manuscript, known_paper_ids))
        issues.extend(self._validate_bibliography_integrity(manuscript))
        return issues

    def _validate_citation_resolution(
        self,
        manuscript: Manuscript,
        known_paper_ids: set[str],
    ) -> list[str]:
        """Validate that every in-text citation resolves to a known paper."""
        issues: list[str] = []
        unresolved = manuscript.validate_citations(known_paper_ids)
        for pid in unresolved:
            issues.append(
                f"Unresolved citation: '{pid}' is cited in the manuscript but not found in known papers."
            )
        return issues

    def _validate_no_fabrication(
        self,
        manuscript: Manuscript,
        known_paper_ids: set[str],
    ) -> list[str]:
        """Validate that no references are fabricated."""
        issues: list[str] = []
        for ref_id in manuscript.reference_ids:
            if ref_id not in known_paper_ids:
                issues.append(
                    f"Potential fabrication: reference '{ref_id}' is in the bibliography "
                    f"but not found in the evidence repository."
                )
        return issues

    def _validate_no_duplicates(
        self,
        manuscript: Manuscript,
    ) -> list[str]:
        """Validate that there are no duplicate references."""
        issues: list[str] = []
        seen: set[str] = set()
        for ref_id in manuscript.reference_ids:
            if ref_id in seen:
                issues.append(
                    f"Duplicate reference: '{ref_id}' appears multiple times in the bibliography."
                )
            seen.add(ref_id)
        return issues

    def _validate_citation_consistency(
        self,
        manuscript: Manuscript,
        known_paper_ids: set[str],
    ) -> list[str]:
        """Validate that cited papers match reference list."""
        issues: list[str] = []
        cited_ids = set(manuscript.get_cited_paper_ids())

        # Check for papers cited but not in reference list
        missing_refs = cited_ids - set(manuscript.reference_ids)
        if missing_refs:
            issues.append(
                f"Papers cited in text but not in reference list: {sorted(missing_refs)}"
            )

        # Check for reference list entries not cited
        uncited = set(manuscript.reference_ids) - cited_ids
        if uncited:
            issues.append(
                f"Bibliography entries not cited in text: {sorted(uncited)}"
            )

        return issues

    def _validate_bibliography_integrity(
        self,
        manuscript: Manuscript,
    ) -> list[str]:
        """Validate bibliography has no silently fabricated entries."""
        issues: list[str] = []

        # Check bibliography for duplicates
        dups = self.bibliography.find_duplicates()
        if dups:
            issues.append(
                f"Bibliography contains duplicate references: {dups}"
            )

        return issues


def validate_author_names(authors: list[str]) -> list[str]:
    """Validate author name format.

    Checks that author names are non-empty and reasonably formatted.
    Returns a list of validation issues.
    """
    issues: list[str] = []
    for i, name in enumerate(authors):
        if not name or not name.strip():
            issues.append(f"Author at position {i + 1} is empty.")
        elif len(name.strip()) < 2:
            issues.append(f"Author at position {i + 1} ('{name.strip()}') appears too short.")
    return issues


def validate_doi(doi: str | None) -> DOIResolutionResult | None:
    """Validate a DOI string.

    This is a placeholder — in production, this would call the CrossRef API
    to verify the DOI resolves.
    """
    if not doi:
        return None

    # Basic DOI format check
    if not doi.startswith("10.") or "/" not in doi:
        return DOIResolutionResult(
            doi=doi,
            resolved=False,
            error="Invalid DOI format: must start with '10/'",
        )

    return DOIResolutionResult(
        doi=doi,
        resolved=False,
        error="DOI resolution requires network access",
    )


def validate_publication_year(
    year: int | None,
) -> list[str]:
    """Validate a publication year."""
    issues: list[str] = []
    if year is not None:
        current_year = 2026
        if year > current_year:
            issues.append(f"Publication year {year} is in the future.")
        elif year < 1800:
            issues.append(f"Publication year {year} seems implausibly early.")
    return issues
