<<<<<<< HEAD
<<<<<<< HEAD
"""Paper summarization agent.

Produces a consistent research note for each paper with:
- Research question and motivation (author-reported).
- Methodology, data, and sample (author-reported).
- Main results and quantitative findings (author-reported).
- Contributions and limitations (author-reported).
- Open questions and relevance to the review (agent interpretation).
- Evidence pointers to sections, pages, tables, or figures.

Acceptance criteria:
- Summaries distinguish author-reported findings from the agent's interpretation.
- Missing information is marked as "Unknown" rather than invented.
=======
=======
>>>>>>> 3eda405 (fix: Phase E — Reliability, Git integration and release (#6))
"""Paper summarizer agent.

Extracts structured research notes from paper metadata and optional
raw text. Separates author-reported content from agent interpretation
to reduce the risk of unsupported claims.

Acceptance criteria:
- Distinguishes author-reported findings from the agent's interpretation.
- Missing information is marked as "Unknown" rather than invented.
- Includes evidence pointers to sections, pages, tables, or figures when available.
<<<<<<< HEAD
>>>>>>> 10d6757 (fix: Phase D — Manuscript production and quality control (#5))
=======

Reliability (Phase E):
- Sanitizes raw PDF text to prevent prompt injection.
- Per-paper error isolation: failures in one paper do not affect others.
>>>>>>> 3eda405 (fix: Phase E — Reliability, Git integration and release (#6))
"""

from __future__ import annotations

<<<<<<< HEAD
<<<<<<< HEAD
from typing import List

=======
>>>>>>> 10d6757 (fix: Phase D — Manuscript production and quality control (#5))
=======
>>>>>>> 3eda405 (fix: Phase E — Reliability, Git integration and release (#6))
from pydantic import BaseModel, Field

from ..models.evidence import EvidencePointer, ResearchNote
from ..models.paper import Paper
<<<<<<< HEAD


class PaperSummaryConfig(BaseModel):
<<<<<<< HEAD
    """Configuration for the paper summarization agent."""

    include_quantitative_findings: bool = Field(
        default=True, description="Extract specific numerical results"
    )
    include_evidence_pointers: bool = Field(
        default=True, description="Add pointers to sections/pages/tables/figures"
    )
    include_agent_interpretation: bool = Field(
        default=True, description="Include agent's own interpretation"
    )


def _unknown(value: str) -> str:
    """Return the value or 'Unknown' if empty/whitespace."""
    if not value or not value.strip():
        return "Unknown"
    return value.strip()


def _extract_section(
    text: str, section_name: str, section_headers: List[str] | None = None
) -> str:
    """Extract content for a given section from raw paper text.

    Falls back to searching for common section headers.
    Returns 'Unknown' if the section is not found.
    """
    if not text:
        return "Unknown"

    # Normalize section name for matching
    normalized = section_name.lower()

    # Try to find section by common header patterns
    for header in section_headers or [
        f"{section_name}:",
        f"## {section_name}",
        f"### {section_name}",
        section_name.upper(),
    ]:
        header_lower = header.lower()
        if header_lower in text.lower():
            idx = text.lower().find(header_lower)
            # Find the end of this section
            next_section = None
            for other in section_headers or [
                "Methodology",
                "Methods",
                "Data",
                "Sample",
                "Results",
                "Findings",
                "Discussion",
                "Limitations",
                "Conclusion",
                "Contributions",
                "Open Questions",
                "References",
                "Bibliography",
            ]:
                other_lower = other.lower()
                other_idx = text.lower().find(other_lower, idx + len(header_lower))
                if other_idx != -1 and (
                    next_section is None or other_idx < next_section
                ):
                    next_section = other_idx
            if next_section:
                content = text[idx + len(header_lower) : next_section].strip()
            else:
                content = text[idx + len(header_lower) :].strip()
            return _unknown(content)

    return "Unknown"


def summarize_paper(
    paper: Paper,
    raw_text: str = "",
    config: PaperSummaryConfig | None = None,
    section_headers: List[str] | None = None,
) -> ResearchNote:
    """Generate a structured research note for a single paper.

    Distinguishes author-reported content from agent interpretation.
    Missing information is marked as "Unknown" rather than invented.

    Args:
        paper: The Paper object with metadata and abstract.
        raw_text: Optional raw paper text for deeper extraction.
        config: Configuration for the summarization.
        section_headers: Known section headers in the paper.

    Returns:
        A ResearchNote with all required fields.
    """
    if config is None:
        config = PaperSummaryConfig()

    # Author-reported sections
    research_question = _unknown(
        _extract_section(raw_text, "Research Question", section_headers)
    ) if raw_text else "Unknown"
    motivation = _unknown(
        _extract_section(raw_text, "Motivation", section_headers)
    ) if raw_text else "Unknown"

    # Extract from abstract as fallback for methodology
    abstract = paper.abstract or ""
    if raw_text:
        methodology = _unknown(
            _extract_section(raw_text, "Methodology", section_headers)
            or _extract_section(raw_text, "Methods", section_headers)
        )
        data_and_sample = _unknown(
            _extract_section(raw_text, "Data", section_headers)
            or _extract_section(raw_text, "Sample", section_headers)
        )
        main_results = _unknown(
            _extract_section(raw_text, "Results", section_headers)
            or _extract_section(raw_text, "Findings", section_headers)
        )
        contributions = _unknown(
            _extract_section(raw_text, "Contributions", section_headers)
        )
        limitations = _unknown(
            _extract_section(raw_text, "Limitations", section_headers)
        )
        quantitative_findings = _unknown(
            _extract_section(raw_text, "Quantitative Findings", section_headers)
        ) if config.include_quantitative_findings else "Unknown"
    else:
        # Fallback: use abstract
        methodology = f"Abstract states: {abstract[:200]}" if abstract else "Unknown"
        data_and_sample = "Information not available in abstract" if not raw_text else "Unknown"
        main_results = abstract[:500] if abstract else "Unknown"
        contributions = "Information not available in abstract" if not raw_text else "Unknown"
        limitations = "Information not available in abstract" if not raw_text else "Unknown"
        quantitative_findings = "Information not available in abstract" if not raw_text else "Unknown"

    # Agent interpretation (clearly separated from author-reported content)
    open_questions = (
        "Based on the paper's content, further investigation is needed into areas not fully explored."
        if not raw_text
        else "Unknown"
    )
    relevance_to_review = (
        "This paper addresses the topic through its stated research question and findings."
        if not raw_text
        else "Unknown"
    )
    agent_interpretation = (
        f"This paper by {', '.join(a.full_name for a in paper.authors[:3])} "
        f"({paper.year or 'n.d.'}) contributes to the field of "
        f"{paper.venue or paper.title.split()[0] if paper.title else 'the field'}."
    )

    note = ResearchNote(
        paper_id=paper.get_identifier() or paper.title[:50].replace(" ", "_"),
        title=paper.title,
        year=paper.year,
        research_question=research_question,
        motivation=motivation,
        methodology=methodology,
        data_and_sample=data_and_sample,
        main_results=main_results,
        quantitative_findings=quantitative_findings,
        contributions=contributions,
        limitations=limitations,
        open_questions=open_questions,
        relevance_to_review=relevance_to_review,
        agent_interpretation=agent_interpretation,
    )

    # Add evidence pointers if raw text is available
    if config.include_evidence_pointers and raw_text:
        note.evidence_pointers = _extract_evidence_pointers(
            paper, raw_text, section_headers
        )

    return note
=======
=======
from ..reliability import sanitize_pdf_text


class PaperSummaryConfig(BaseModel):
>>>>>>> 3eda405 (fix: Phase E — Reliability, Git integration and release (#6))
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
<<<<<<< HEAD
    """Summarize a single paper into a structured ResearchNote."""
    config = config or PaperSummaryConfig()

    # Parse raw text sections if provided
    sections: dict[str, str] = {}
    if raw_text:
        current_section = ""
        current_content: list[str] = []
        for line in raw_text.split("\n"):
=======
    """Summarize a single paper into a structured ResearchNote.

    Raw text is sanitized to treat PDF content as untrusted input.
    """
    config = config or PaperSummaryConfig()

    # Sanitize raw text (treat as untrusted)
    safe_text = sanitize_pdf_text(raw_text) if raw_text else None

    # Parse raw text sections if provided
    sections: dict[str, str] = {}
    if safe_text:
        current_section = ""
        current_content: list[str] = []
        for line in safe_text.split("\n"):
>>>>>>> 3eda405 (fix: Phase E — Reliability, Git integration and release (#6))
            stripped = line.strip()
            if stripped.startswith("#"):
                # Save previous section
                if current_section:
                    sections[current_section] = "\n".join(current_content).strip()
                current_section = stripped.lstrip("#").strip()
                current_content = []
<<<<<<< HEAD
            elif current_section:
                current_content.append(line)
        if current_section:
=======
            elif not stripped:
                # Blank line: end current section if we have content
                if current_section and current_content:
                    sections[current_section] = "\n".join(current_content).strip()
                    current_section = ""
                    current_content = []
            elif current_section:
                current_content.append(line)
            elif stripped and not current_section:
                # No current section and we see a non-blank line
                # Heuristic: if it's a short line (potential heading),
                # start a new section; otherwise treat as content of an
                # implicit "general" section.
                if len(stripped) < 60 and not stripped[0].islower():
                    # Likely a section heading
                    current_section = stripped
                    current_content = []
                elif current_section:
                    current_content.append(line)
                else:
                    # First line without a heading: skip or collect
                    pass
        if current_section and current_content:
>>>>>>> 3eda405 (fix: Phase E — Reliability, Git integration and release (#6))
            sections[current_section] = "\n".join(current_content).strip()

    # Extract evidence pointers if configured
    evidence_pointers: list[EvidencePointer] = []
<<<<<<< HEAD
    if config.include_evidence_pointers and raw_text:
=======
    if config.include_evidence_pointers and safe_text:
>>>>>>> 3eda405 (fix: Phase E — Reliability, Git integration and release (#6))
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
<<<<<<< HEAD
>>>>>>> 10d6757 (fix: Phase D — Manuscript production and quality control (#5))
=======
>>>>>>> 3eda405 (fix: Phase E — Reliability, Git integration and release (#6))


def summarize_papers(
    papers: list[Paper],
    raw_texts: dict[str, str] | None = None,
    config: PaperSummaryConfig | None = None,
) -> list[ResearchNote]:
<<<<<<< HEAD
<<<<<<< HEAD
    """Generate research notes for multiple papers.

    Args:
        papers: List of Paper objects.
        raw_texts: Optional dict mapping paper identifiers to raw text.
        config: Configuration for the summarization.

    Returns:
        List of ResearchNote objects.
    """
    if raw_texts is None:
        raw_texts = {}
    if config is None:
        config = PaperSummaryConfig()

    notes: list[ResearchNote] = []
    for paper in papers:
        paper_id = paper.get_identifier() or paper.title[:50].replace(" ", "_")
        raw = raw_texts.get(paper_id, "")
        note = summarize_paper(paper, raw_text=raw, config=config)
        notes.append(note)
    return notes


def _extract_evidence_pointers(
    paper: Paper,
    raw_text: str,
    section_headers: List[str] | None = None,
) -> list[EvidencePointer]:
    """Extract evidence pointers from raw paper text."""
    pointers: list[EvidencePointer] = []
    paper_id = paper.get_identifier() or paper.title[:50].replace(" ", "_")

    # Look for section headers as evidence pointers
    default_headers = [
        "Introduction",
        "Related Work",
        "Background",
        "Methodology",
        "Methods",
        "Data and Sample",
        "Results",
        "Findings",
        "Discussion",
        "Limitations",
        "Conclusion",
        "References",
    ]

    for header in section_headers or default_headers:
        header_lower = header.lower()
        lines = raw_text.split("\n")
        for i, line in enumerate(lines):
            if header_lower in line.lower():
                # Determine page number from context
                page_num = None
                for j in range(max(0, i - 10), i):
                    if "Page" in lines[j] or "page" in lines[j]:
                        try:
                            parts = lines[j].split()
                            for p in parts:
                                if p.isdigit():
                                    page_num = int(p)
                                    break
                        except (ValueError, IndexError):
                            pass
                        break

                pointers.append(EvidencePointer(
                    paper_id=paper_id,
                    section=header,
                    page=page_num,
                    description=f"Section: {header}",
                ))

    # Look for tables
    table_lines = [i for i, l in enumerate(raw_text.split("\n")) if "Table" in l]
    for i in table_lines[:5]:  # Limit to 5 tables
        pointers.append(EvidencePointer(
            paper_id=paper_id,
            table=f"Table {i // 5 + 1}",
            description="Table reference found in document",
        ))

    return pointers
=======
=======
>>>>>>> 3eda405 (fix: Phase E — Reliability, Git integration and release (#6))
    """Summarize multiple papers."""
    raw_texts = raw_texts or {}
    config = config or PaperSummaryConfig()
    return [
        summarize_paper(p, raw_texts.get(p.title.replace(" ", "_")), config)
        for p in papers
    ]
<<<<<<< HEAD
>>>>>>> 10d6757 (fix: Phase D — Manuscript production and quality control (#5))
=======
>>>>>>> 3eda405 (fix: Phase E — Reliability, Git integration and release (#6))
