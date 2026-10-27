"""Research planner agent.

Plans the systematic review: defines research questions, search strings,
inclusion/exclusion criteria, and database selection.
"""

from __future__ import annotations

from ..models.research_plan import ResearchPlan, ResearchQuestion


class ResearchPlanner:
    """Agent that plans the systematic review process."""

    def __init__(self) -> None:
        pass

    def plan(
        self,
        topic: str,
        questions: list[ResearchQuestion],
    ) -> ResearchPlan:
        """Create a research plan for the given topic and questions."""
        return ResearchPlan(
            title=f"Systematic Review: {topic}",
            questions=questions,
            search_strings=self._generate_search_strings(questions),
            databases=["PubMed", "Scopus", "Web of Science"],
            notes=f"Plan generated for topic: {topic}",
        )

    def _generate_search_strings(self, questions: list[ResearchQuestion]) -> list[str]:
        """Generate search strings from research questions."""
        strings: list[str] = []
        for q in questions:
            # Simple keyword-based search string generation
            terms = q.question.replace("?", "").split()
            if len(terms) <= 5:
                strings.append(" AND ".join(terms))
            else:
                strings.append(" AND ".join(terms[:3]))
        return strings
