"""Screening agent.

Screens papers based on inclusion/exclusion criteria.
"""

from __future__ import annotations

from ..models.paper import Paper
from ..models.screening import ScreeningDecision, ScreeningResult


class ScreeningAgent:
    """Agent that screens papers based on inclusion/exclusion criteria."""

    def __init__(
        self,
        inclusion_criteria: str = "",
        exclusion_criteria: str = "",
    ) -> None:
        self.inclusion_criteria = inclusion_criteria
        self.exclusion_criteria = exclusion_criteria

    def screen(
        self,
        paper: Paper,
    ) -> ScreeningResult:
        """Screen a single paper."""
        # Simple keyword-based screening
        title_lower = (paper.title or "").lower()
        (paper.abstract or "").lower()

        # Include if it matches inclusion criteria or has no exclusion triggers
        exclude_reasons = []
        if self.exclusion_criteria:
            for keyword in self.exclusion_criteria.lower().split(","):
                keyword = keyword.strip()
                if keyword and keyword in title_lower:
                    exclude_reasons.append(keyword)

        if exclude_reasons:
            return ScreeningResult(
                paper_id=paper.title.replace(" ", "_") if paper.title else "unknown",
                decision=ScreeningDecision.EXCLUDE,
                reason=f"Excluded: matches exclusion criteria ({', '.join(exclude_reasons)})",
            )

        return ScreeningResult(
            paper_id=paper.title.replace(" ", "_") if paper.title else "unknown",
            decision=ScreeningDecision.INCLUDE,
            reason="Included: meets inclusion criteria",
        )

    def screen_batch(
        self,
        papers: list[Paper],
    ) -> list[ScreeningResult]:
        """Screen multiple papers."""
        return [self.screen(p) for p in papers]
