"""Screening agent.

Screens papers based on inclusion/exclusion criteria.
"""

from __future__ import annotations

from typing import Any

from ..models.paper import Paper
from ..models.screening import ScreeningDecision, ScreeningResult


class ScreeningAgent:
    """Agent that screens papers based on inclusion/exclusion criteria."""

    def __init__(
        self,
        inclusion_criteria: str | list[str] | None = "",
        exclusion_criteria: str | list[str] | None = "",
    ) -> None:
        self.inclusion_criteria = inclusion_criteria
        self.exclusion_criteria = exclusion_criteria

    @staticmethod
    def _to_keywords(criteria: Any) -> list[str]:
        """Normalize criteria (str or list) into a list of keywords."""
        if not criteria:
            return []
        if isinstance(criteria, str):
            return [kw.strip().lower() for kw in criteria.split(",") if kw.strip()]
        return [str(kw).strip().lower() for kw in criteria if str(kw).strip()]

    def screen(
        self,
        paper: Paper,
    ) -> ScreeningResult:
        """Screen a single paper."""
        title_lower = (paper.title or "").lower()
        abstract_lower = (paper.abstract or "").lower()
        text = f"{title_lower} {abstract_lower}"

        paper_id = paper.get_paper_id()

        exclusion_keywords = self._to_keywords(self.exclusion_criteria)
        inclusion_keywords = self._to_keywords(self.inclusion_criteria)

        # Exclusion criteria: any matching keyword excludes the paper.
        exclude_reasons = [kw for kw in exclusion_keywords if kw in text]
        if exclude_reasons:
            return ScreeningResult(
                paper_id=paper_id,
                decision=ScreeningDecision.EXCLUDE,
                reason=f"Excluded: matches exclusion criteria ({', '.join(exclude_reasons)})",
            )

        # Inclusion criteria: when provided, require at least one match.
        if inclusion_keywords:
            matched = [kw for kw in inclusion_keywords if kw in text]
            if not matched:
                return ScreeningResult(
                    paper_id=paper_id,
                    decision=ScreeningDecision.EXCLUDE,
                    reason=(
                        "Excluded: does not match inclusion criteria "
                        f"({', '.join(inclusion_keywords)})"
                    ),
                )

        return ScreeningResult(
            paper_id=paper_id,
            decision=ScreeningDecision.INCLUDE,
            reason="Included: meets inclusion criteria",
        )

    def screen_batch(
        self,
        papers: list[Paper],
    ) -> list[ScreeningResult]:
        """Screen multiple papers."""
        return [self.screen(p) for p in papers]
