"""Research-planner agent.

Turns a topic into research questions, search terms, synonyms, date
limits, inclusion/exclusion criteria, and an initial protocol.
"""

from __future__ import annotations

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
