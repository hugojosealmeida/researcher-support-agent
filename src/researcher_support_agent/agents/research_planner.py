<<<<<<< HEAD
<<<<<<< HEAD
"""Research-planner agent.

Turns a topic into research questions, search terms, synonyms, date
limits, inclusion/exclusion criteria, and an initial protocol.
=======
=======
>>>>>>> 3eda405 (fix: Phase E — Reliability, Git integration and release (#6))
"""Research planner agent.

Plans the systematic review: defines research questions, search strings,
inclusion/exclusion criteria, and database selection.
<<<<<<< HEAD
>>>>>>> 10d6757 (fix: Phase D — Manuscript production and quality control (#5))
=======
>>>>>>> 3eda405 (fix: Phase E — Reliability, Git integration and release (#6))
"""

from __future__ import annotations

<<<<<<< HEAD
<<<<<<< HEAD
from typing import Optional

from pydantic import BaseModel, Field

from ..models.research_plan import ResearchPlan, ResearchQuestion


class ResearchPlannerConfig(BaseModel):
    """Configuration for the research-planner agent."""

    max_questions: int = Field(default=5, ge=1, le=20)
    include_synonyms: bool = Field(default=True)
    default_date_from: str | None = Field(default=None)
    default_date_to: str | None = Field(default=None)
    default_inclusion_criteria: list[str] = Field(default_factory=list)
    default_exclusion_criteria: list[str] = Field(default_factory=list)


def generate_research_questions(
    topic: str,
    config: ResearchPlannerConfig | None = None,
) -> list[ResearchQuestion]:
    """Generate a set of research questions from a topic.

    In a production system this would call an LLM.  For now we return
    a deterministic template set that satisfies the acceptance criteria
    (structured, stable-format output).
    """
    if config is None:
        config = ResearchPlannerConfig()

    questions: list[ResearchQuestion] = [
        ResearchQuestion(
            question=f"What is the current state of research on {topic}?",
            search_terms=[topic],
            synonyms={topic: [topic]},
            date_from=config.default_date_from,
            date_to=config.default_date_to,
            inclusion_criteria=config.default_inclusion_criteria,
            exclusion_criteria=config.default_exclusion_criteria,
        ),
        ResearchQuestion(
            question=f"What methodologies are commonly used to study {topic}?",
            search_terms=[topic, "methodology", "method"],
            synonyms={topic: [topic]},
            date_from=config.default_date_from,
            date_to=config.default_date_to,
            inclusion_criteria=config.default_inclusion_criteria,
            exclusion_criteria=config.default_exclusion_criteria,
        ),
        ResearchQuestion(
            question=f"What are the key findings and gaps in {topic} research?",
            search_terms=[topic, "findings", "gap", "review"],
            synonyms={topic: [topic]},
            date_from=config.default_date_from,
            date_to=config.default_date_to,
            inclusion_criteria=config.default_inclusion_criteria,
            exclusion_criteria=config.default_exclusion_criteria,
        ),
    ]
    return questions[: config.max_questions]


def build_research_plan(
    topic: str,
    project_id: str,
    config: ResearchPlannerConfig | None = None,
) -> ResearchPlan:
    """Build a complete, validated ResearchPlan for the given topic.

    Returns a structured ``ResearchPlan`` — not an unstructured paragraph.
    """
    questions = generate_research_questions(topic, config)
    plan = ResearchPlan(
        project_id=project_id,
        topic=topic,
        research_questions=questions,
    )
    return plan
=======
=======
>>>>>>> 3eda405 (fix: Phase E — Reliability, Git integration and release (#6))
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
<<<<<<< HEAD
>>>>>>> 10d6757 (fix: Phase D — Manuscript production and quality control (#5))
=======
>>>>>>> 3eda405 (fix: Phase E — Reliability, Git integration and release (#6))
