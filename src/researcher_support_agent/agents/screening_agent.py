"""Screening agent.

<<<<<<< HEAD
<<<<<<< HEAD
Screens titles and abstracts against the approved inclusion/exclusion
criteria.  Records the decision, reason, and uncertainty for every
paper.  Flag borderline cases for human review.

Every excluded paper is retained in the screening log, not silently
discarded.
=======
Screens papers based on inclusion/exclusion criteria.
>>>>>>> 10d6757 (fix: Phase D — Manuscript production and quality control (#5))
=======
Screens papers based on inclusion/exclusion criteria.
>>>>>>> 3eda405 (fix: Phase E — Reliability, Git integration and release (#6))
"""

from __future__ import annotations

<<<<<<< HEAD
<<<<<<< HEAD
import re

from ..models.paper import Paper
from ..models.research_plan import ResearchPlan
from ..models.screening import ScreeningDecision, ScreeningResult


def _simple_match(text: str, term: str) -> bool:
    """Case-insensitive substring match with word boundary awareness."""
    if not text or not term:
        return False
    pattern = r"\b" + re.escape(term.lower()) + r"\b"
    return bool(re.search(pattern, (text or "").lower()))


def _evaluate_criteria(
    paper: Paper,
    inclusion_criteria: list[str],
    exclusion_criteria: list[str],
) -> tuple[bool, list[str]]:
    """Evaluate a paper against inclusion/exclusion criteria.

    Returns (is_included, matched_criteria).
    """
    text_to_check = f"{paper.title} {paper.abstract or ''}".lower()
    matched: list[str] = []

    # Check exclusion criteria first — if any match, exclude
    for criterion in exclusion_criteria:
        # Simple keyword-based matching; could be enhanced with LLM later
        words = criterion.lower().split()
        if any(_simple_match(text_to_check, w) for w in words if len(w) > 2):
            matched.append(f"EXCLUDED: {criterion}")
            return False, matched

    # Check inclusion criteria
    for criterion in inclusion_criteria:
        if _simple_match(text_to_check, criterion):
            matched.append(f"INCLUDED: {criterion}")

    # Include if at least one inclusion criterion matched and no exclusions
    return bool(matched), matched


def screen_papers(
    papers: list[Paper],
    plan: ResearchPlan,
) -> list[ScreeningResult]:
    """Screen a list of papers against the research plan criteria.

    Every paper gets a ScreeningResult, even excluded ones.
    """
    results: list[ScreeningResult] = []

    # Collect all criteria from all research questions
    all_inclusion: list[str] = []
    all_exclusion: list[str] = []
    for rq in plan.research_questions:
        all_inclusion.extend(rq.inclusion_criteria)
        all_exclusion.extend(rq.exclusion_criteria)
    # Deduplicate while preserving order
    all_inclusion = list(dict.fromkeys(all_inclusion))
    all_exclusion = list(dict.fromkeys(all_exclusion))

    for paper in papers:
        paper_id = paper.get_identifier() or paper.title[:50]
        is_included, matched = _evaluate_criteria(
            paper, all_inclusion, all_exclusion
        )

        if is_included:
            decision = ScreeningDecision.ACCEPT
            reason = "Met inclusion criteria"
            flagged = False
        elif all_exclusion:
            decision = ScreeningDecision.EXCLUDE
            reason = f"Failed criteria: {', '.join(all_exclusion[:3])}"
            flagged = False
        else:
            # No clear criteria — borderline
            decision = ScreeningDecision.BORDERLINE
            reason = "Insufficient criteria for decision"
            flagged = True

        uncertainty = 0.0
        if decision == ScreeningDecision.BORDERLINE:
            uncertainty = 0.5
        elif not is_included and not all_exclusion:
            uncertainty = 0.7

        result = ScreeningResult(
            paper_id=paper_id,
            decision=decision,
            reason=reason,
            uncertainty=uncertainty,
            criteria_matched=matched,
            flagged_for_review=flagged,
            source="screening_agent",
        )
        results.append(result)

        # Update paper processing status
        if decision == ScreeningDecision.ACCEPT:
            paper.processing_status = "included"
        elif decision == ScreeningDecision.EXCLUDE:
            paper.processing_status = "excluded"
        else:
            paper.processing_status = "needs_review"

    return results
=======
=======
>>>>>>> 3eda405 (fix: Phase E — Reliability, Git integration and release (#6))
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
        abstract_lower = (paper.abstract or "").lower()

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
<<<<<<< HEAD
>>>>>>> 10d6757 (fix: Phase D — Manuscript production and quality control (#5))
=======
>>>>>>> 3eda405 (fix: Phase E — Reliability, Git integration and release (#6))
