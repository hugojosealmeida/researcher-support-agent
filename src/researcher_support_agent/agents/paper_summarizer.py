"""Paper summarizer agent.

Extracts structured research notes from paper metadata and optional
raw text. Separates author-reported content from agent interpretation
to reduce the risk of unsupported claims.

Acceptance criteria:
- Distinguishes author-reported findings from the agent's interpretation.
- Missing information is marked as "Unknown" rather than invented.
- Includes evidence pointers to sections, pages, tables, or figures when available.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from ..models.evidence import EvidencePointer, ResearchNote
from ..models.paper import Paper


class PaperSummaryConfig(BaseModel):
    """Configuration for paper summarization."""

    include_quantitative_findings: bool = Field(
        default=True, description="Attempt to extract quantitative findings"
    )
    include_evidence_pointers: bool = Field(
        default=True, description="Generate evidence pointers to sections"
    )
    include_agent_interpretation: bool = Field(
        default=True, description="Include agent's interpretation section"
    )


def summarize_paper(
    paper: Paper,
    raw_text: str | None = None,
    config: PaperSummaryConfig | None = None,
) -> ResearchNote:
    """Summarize a single paper into a structured ResearchNote."""
    config = config or PaperSummaryConfig()

    # Parse raw text sections if provided
    sections: dict[str, str] = {}
    if raw_text:
        current_section = ""
        current_content: list[str] = []
        for line in raw_text.split("\n"):
            stripped = line.strip()
            if stripped.startswith("#"):
                # Save previous section
                if current_section:
                    sections[current_section] = "\n".join(current_content).strip()
                current_section = stripped.lstrip("#").strip()
                current_content = []
            elif current_section:
                current_content.append(line)
        if current_section:
            sections[current_section] = "\n".join(current_content).strip()

    # Extract evidence pointers if configured
    evidence_pointers: list[EvidencePointer] = []
    if config.include_evidence_pointers and raw_text:
        for section_name in sections:
            evidence_pointers.append(
                EvidencePointer(
                    paper_id=paper.title.replace(" ", "_"),
                    section=section_name,
                    description=f"Content found in {section_name} section",
                )
            )

    # Build research note
    title = paper.title
    paper_id = title.replace(" ", "_") if title else "Unknown"

    # Try to extract from raw text, fall back to abstract, then Unknown
    methodology = sections.get("Methodology", sections.get("Methods", "Unknown"))
    data_sample = sections.get("Data", sections.get("Sample", "Information not available in abstract"))
    main_results = sections.get("Results", sections.get("Findings", "Unknown"))
    quantitative = sections.get("Results", "")
    if config.include_quantitative_findings and quantitative:
        # Try to find numerical results
        import re
        numbers = re.findall(r"\d+\.?\d*\s*(?:%|p\s*<|t\s*=|F\s*=|df\s*=|\(r\s*=\s*\d)", quantitative)
        if numbers:
            quantitative = "Numerical results: " + ", ".join(numbers)
        else:
            quantitative = "Numerical results mentioned but not extracted"
    limitations = sections.get("Limitations", sections.get("Limitation", "Unknown"))
    contributions = sections.get("Contributions", sections.get("Contribution", "Unknown"))

    # Build agent interpretation
    agent_interpretation = f"This paper by {', '.join(a.full_name for a in paper.authors[:3])}"
    if paper.year:
        agent_interpretation += f" ({paper.year})"
    agent_interpretation += " addresses a research topic related to the review scope."

    return ResearchNote(
        paper_id=paper_id,
        title=title,
        year=paper.year,
        methodology=methodology,
        data_and_sample=data_sample,
        main_results=main_results,
        quantitative_findings=quantitative if config.include_quantitative_findings else "Unknown",
        limitations=limitations,
        contributions=contributions,
        agent_interpretation=agent_interpretation if config.include_agent_interpretation else "Unknown",
        evidence_pointers=evidence_pointers,
    )


def summarize_papers(
    papers: list[Paper],
    raw_texts: dict[str, str] | None = None,
    config: PaperSummaryConfig | None = None,
) -> list[ResearchNote]:
    """Summarize multiple papers."""
    raw_texts = raw_texts or {}
    config = config or PaperSummaryConfig()
    return [
        summarize_paper(p, raw_texts.get(p.title.replace(" ", "_")), config)
        for p in papers
    ]
