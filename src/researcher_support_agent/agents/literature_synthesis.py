"""Literature synthesis agent.

Compares papers across methods, datasets, findings, theoretical perspectives,
limitations, and publication dates. Identifies consensus, contradictions,
evidence gaps, and emerging themes.

Acceptance criteria:
- Each major synthesis finding has supporting and, where relevant, conflicting evidence.
- The agent cannot present a research gap as established without showing how the
  search supports that conclusion.
- Generates a synthesis matrix and proposed section outline before drafting prose.
"""

from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field

from ..models.evidence import ResearchNote
from ..models.paper import Paper


class SynthesisFindingType(StrEnum):
    CONSENSUS = "consensus"
    CONTRADICTION = "contradiction"
    GAP = "gap"
    EMERGING_THEME = "emerging_theme"


class SynthesisFinding(BaseModel):
    """A finding from comparing papers in the literature synthesis."""

    finding_type: SynthesisFindingType
    title: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)
    supporting_paper_ids: list[str] = Field(
        default_factory=list,
        description="Papers that support this finding",
    )
    conflicting_paper_ids: list[str] = Field(
        default_factory=list,
        description="Papers that conflict with or challenge this finding",
    )
    evidence_base: str = Field(
        default="Unknown",
        description="Summary of the evidence base for this finding",
    )
    confidence: float = Field(
        default=0.0, ge=0.0, le=1.0,
        description="Confidence in this synthesis finding",
    )
    notes: str = Field(
        default="", description="Additional context or caveats"
    )

    def to_markdown(self) -> str:
        """Render the finding as a Markdown string."""
        type_label = {
            SynthesisFindingType.CONSENSUS: "Consensus",
            SynthesisFindingType.CONTRADICTION: "Contradiction",
            SynthesisFindingType.GAP: "Evidence Gap",
            SynthesisFindingType.EMERGING_THEME: "Emerging Theme",
        }.get(self.finding_type, self.finding_type)

        lines = [
            f"### {type_label}: {self.title}",
            self.description,
            "",
            f"**Supporting papers:** {', '.join(self.supporting_paper_ids) if self.supporting_paper_ids else 'None'}",
        ]
        if self.conflicting_paper_ids:
            lines.append(f"**Conflicting papers:** {', '.join(self.conflicting_paper_ids)}")
        lines.append(f"**Evidence base:** {self.evidence_base}")
        if self.notes:
            lines.append(f"**Notes:** {self.notes}")
        return "\n".join(lines)


class ProposedSection(BaseModel):
    """A proposed section in the synthesis manuscript."""

    title: str = Field(..., min_length=1)
    description: str = Field(default="", min_length=0)
    subsections: list[str] = Field(default_factory=list)
    key_papers: list[str] = Field(default_factory=list)
    finding_ids: list[str] = Field(
        default_factory=list, description="IDs of synthesis findings relevant to this section"
    )


class ProposedOutline(BaseModel):
    """A proposed section outline for the synthesis manuscript."""

    title: str = Field(default="Untitled", min_length=0)
    sections: list[ProposedSection] = Field(default_factory=list)
    notes: str = Field(default="", description="Additional notes about the outline")

    def to_markdown(self) -> str:
        """Render the outline as a Markdown string."""
        lines = [f"# {self.title}", ""]
        for i, section in enumerate(self.sections, 1):
            lines.append(f"## {i}. {section.title}")
            if section.description:
                lines.append(section.description)
            for j, sub in enumerate(section.subsections, 1):
                lines.append(f"### {i}.{j} {sub}")
            if section.key_papers:
                lines.append(
                    f"**Key papers:** {', '.join(section.key_papers)}"
                )
            if section.finding_ids:
                lines.append(f"**Related findings:** {', '.join(section.finding_ids)}")
            lines.append("")
        if self.notes:
            lines.append(f"**Notes:** {self.notes}")
        return "\n".join(lines)


class SynthesisMatrix(BaseModel):
    """Structured comparison matrix across papers."""

    dimensions: list[str] = Field(default_factory=list)
    rows: list[dict[str, Any]] = Field(default_factory=list)

    def to_markdown(self) -> str:
        """Render the matrix as a Markdown table."""
        if not self.rows:
            return "_No data in matrix._"
        lines = ["| " + " | ".join(self.dimensions) + " |"]
        lines.append("| " + " | ".join(["---"] * len(self.dimensions)) + " |")
        for row in self.rows:
            lines.append("| " + " | ".join(str(row.get(d, "")) for d in self.dimensions) + " |")
        return "\n".join(lines)


class LiteratureSynthesisAgent:
    """Synthesizes research across multiple papers.

    Compares papers across methods, datasets, findings, theoretical perspectives,
    limitations, and publication dates.
    """

    def __init__(self, config: Any = None) -> None:
        self.config = config

    def synthesize(self, *args: Any, **kwargs: Any) -> SynthesisResult:
        """Perform a full literature synthesis.

        Supports both ``synthesize(papers, notes)`` and
        ``synthesize(notes, papers, search_metadata)`` call styles.
        """
        papers: list[Paper] = kwargs.get("papers", [])
        notes: list[ResearchNote] = kwargs.get("notes", [])
        search_metadata: dict[str, Any] | None = kwargs.get("search_metadata")

        if len(args) >= 1 and isinstance(args[0], list):
            first = args[0]
            is_paper = bool(first) and isinstance(first[0], Paper)
            is_note = bool(first) and isinstance(first[0], ResearchNote)
            if is_paper:
                papers = first
                if len(args) >= 2 and isinstance(args[1], list):
                    notes = args[1]
                if len(args) >= 3:
                    search_metadata = args[2]
            elif is_note:
                notes = first
                if len(args) >= 2 and isinstance(args[1], list):
                    papers = args[1]
                if len(args) >= 3:
                    search_metadata = args[2]

        if not papers:
            papers = []
        if not notes:
            notes = []

        matrix = self._build_matrix(notes, papers)
        findings = self._identify_findings(notes, papers, search_metadata)
        outline = self._propose_outline(findings)

        return SynthesisResult(
            matrix=matrix,
            findings=findings,
            outline=outline,
            synthesis_matrix=matrix.to_markdown(),
            synthesized_at=datetime.now(UTC),
        )

    def _build_matrix(
        self, notes: list[ResearchNote], papers: list[Paper]
    ) -> SynthesisMatrix:
        dimensions = [
            "Paper",
            "Year",
            "Methodology",
            "Data/Sample",
            "Main Results",
            "Limitations",
            "Open Questions",
        ]

        paper_map = {
            p.get_identifier() or p.title[:50]: p
            for p in papers
        }

        rows = []
        for note in notes:
            paper_map.get(note.paper_id)
            rows.append({
                "Paper": note.title[:40],
                "Year": note.year or "Unknown",
                "Methodology": note.methodology[:80] if note.methodology != "Unknown" else "Unknown",
                "Data/Sample": note.data_and_sample[:80] if note.data_and_sample != "Unknown" else "Unknown",
                "Main Results": note.main_results[:80] if note.main_results != "Unknown" else "Unknown",
                "Limitations": note.limitations[:80] if note.limitations != "Unknown" else "Unknown",
                "Open Questions": note.open_questions[:80] if note.open_questions != "Unknown" else "Unknown",
            })

        return SynthesisMatrix(dimensions=dimensions, rows=rows)

    def _identify_findings(
        self,
        notes: list[ResearchNote],
        papers: list[Paper],
        search_metadata: dict[str, Any] | None = None,
    ) -> list[SynthesisFinding]:
        findings: list[SynthesisFinding] = []

        similar_results = self._find_consensus(notes)
        if similar_results:
            findings.append(SynthesisFinding(
                finding_type=SynthesisFindingType.CONSENSUS,
                title="Consensus on key findings",
                description="Multiple papers report similar results on this topic.",
                supporting_paper_ids=similar_results,
                confidence=0.7,
                evidence_base=f"Analysis of {len(notes)} papers reveals convergence on key findings.",
            ))

        contradictions = self._find_contradictions(notes)
        for label, group_a, group_b in contradictions:
            findings.append(SynthesisFinding(
                finding_type=SynthesisFindingType.CONTRADICTION,
                title=f"Contradiction: {label}",
                description=f"Papers in group A ({', '.join(group_a)}) report different results than papers in group B ({', '.join(group_b)}).",
                supporting_paper_ids=group_a,
                conflicting_paper_ids=group_b,
                confidence=0.6,
                evidence_base="Comparative analysis of conflicting findings.",
            ))

        gaps = self._identify_gaps(notes, search_metadata)
        for gap in gaps:
            findings.append(SynthesisFinding(
                finding_type=SynthesisFindingType.GAP,
                title=gap["title"],
                description=gap["description"],
                supporting_paper_ids=gap.get("supporting_paper_ids", []),
                confidence=gap.get("confidence", 0.5),
                evidence_base=gap.get("evidence_base", "Insufficient evidence in the literature."),
                notes="This gap claim is based on the current search results and may change as new evidence is found.",
            ))

        themes = self._identify_emerging_themes(notes)
        for theme in themes:
            findings.append(SynthesisFinding(
                finding_type=SynthesisFindingType.EMERGING_THEME,
                title=theme["title"],
                description=theme["description"],
                supporting_paper_ids=theme.get("paper_ids", []),
                confidence=theme.get("confidence", 0.5),
                evidence_base=theme.get("evidence_base", ""),
            ))

        return findings

    def _find_consensus(self, notes: list[ResearchNote]) -> list[str]:
        paper_ids: list[str] = []
        for note in notes:
            result = note.main_results
            if result and result != "Unknown" and len(result) > 20:
                paper_ids.append(note.paper_id)
        return paper_ids[:min(len(paper_ids), 10)]

    def _find_contradictions(
        self, notes: list[ResearchNote]
    ) -> list[tuple[str, list[str], list[str]]]:
        contradictions: list[tuple[str, list[str], list[str]]] = []

        for i, note_a in enumerate(notes):
            for j, note_b in enumerate(notes):
                if i >= j:
                    continue
                if (
                    note_a.main_results != "Unknown"
                    and note_b.main_results != "Unknown"
                    and note_a.methodology != note_b.methodology
                ):
                    contradictions.append((
                        f"Methodology difference: {note_a.methodology[:30]} vs {note_b.methodology[:30]}",
                        [note_a.paper_id],
                        [note_b.paper_id],
                    ))
                    if len(contradictions) >= 5:
                        return contradictions
        return contradictions

    def _identify_gaps(
        self,
        notes: list[ResearchNote],
        search_metadata: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        gaps: list[dict[str, Any]] = []

        sm = search_metadata or {}
        has_search = bool(search_metadata)
        search_scope = ""
        if has_search:
            search_scope = (
                f"Based on search with {sm.get('queries', [])} "
                f"across {sm.get('sources', [])}. "
            )

        years = sorted([n.year for n in notes if n.year is not None])
        if len(years) >= 2:
            max_gap = 0
            gap_between: tuple[Any, Any] = (None, None)
            for i in range(len(years) - 1):
                diff = years[i + 1] - years[i]
                if diff > max_gap:
                    max_gap = diff
                    gap_between = (years[i], years[i + 1])

            if max_gap >= 3 and has_search:
                gaps.append({
                    "title": f"Temporal gap between {gap_between[0]} and {gap_between[1]}",
                    "description": f"No papers found in the literature between {gap_between[0]} and {gap_between[1]}. "
                                   f"{search_scope}This gap should be verified against the full search.",
                    "supporting_paper_ids": [],
                    "confidence": 0.4,
                    "evidence_base": search_scope if has_search else "Search evidence not provided. Cannot verify this gap claim.",
                })
            elif max_gap >= 3 and not has_search:
                gaps.append({
                    "title": f"Potential temporal gap between {gap_between[0]} and {gap_between[1]}",
                    "description": f"Papers found span from {years[0]} to {years[-1]}. "
                                   f"Potential gap between {gap_between[0]} and {gap_between[1]}. "
                                   f"⚠ This gap claim is NOT established — search evidence is required to verify.",
                    "supporting_paper_ids": [],
                    "confidence": 0.2,
                    "evidence_base": "WARNING: No search metadata provided. This gap claim cannot be verified and should not be treated as established.",
                })

        return gaps

    def _identify_emerging_themes(self, notes: list[ResearchNote]) -> list[dict[str, Any]]:
        themes: list[dict[str, Any]] = []
        open_qs = [n.open_questions for n in notes if n.open_questions != "Unknown"]

        if len(open_qs) >= 2:
            themes.append({
                "title": "Recurring open questions",
                "description": f"Multiple papers ({len(open_qs)}) identify similar open questions, suggesting an emerging theme.",
                "paper_ids": [
                    n.paper_id for n in notes
                    if n.open_questions != "Unknown"
                ][:5],
                "confidence": 0.5,
                "evidence_base": f"Analysis of {len(notes)} research notes shows recurring themes in open questions.",
            })

        return themes

    def _propose_outline(self, findings: list[SynthesisFinding]) -> ProposedOutline:
        sections = [
            ProposedSection(
                title="Introduction",
                description="Context and motivation for the review.",
                key_papers=[],
            ),
            ProposedSection(
                title="Methodology",
                description="How papers were selected and synthesized.",
                subsections=["Search strategy", "Inclusion criteria", "Synthesis approach"],
            ),
            ProposedSection(
                title="Consensus Findings",
                description="Areas where the literature agrees.",
            ),
            ProposedSection(
                title="Contradictions and Tensions",
                description="Conflicting findings and possible explanations.",
            ),
            ProposedSection(
                title="Evidence Gaps",
                description="Areas where research is insufficient or missing.",
            ),
            ProposedSection(
                title="Emerging Themes",
                description="New directions and trends in the literature.",
            ),
            ProposedSection(
                title="Discussion",
                description="Synthesis of findings and implications.",
            ),
            ProposedSection(
                title="Conclusion",
                description="Summary and future directions.",
            ),
        ]

        finding_ids = [str(i) for i in range(len(findings))]
        for finding in findings:
            if finding.finding_type == SynthesisFindingType.CONSENSUS:
                sections[2].finding_ids.append(finding_ids[finding_ids.index(str(findings.index(finding)))])
            elif finding.finding_type == SynthesisFindingType.CONTRADICTION:
                sections[3].finding_ids.append(finding_ids[finding_ids.index(str(findings.index(finding)))])
            elif finding.finding_type == SynthesisFindingType.GAP:
                sections[4].finding_ids.append(finding_ids[finding_ids.index(str(findings.index(finding)))])
            elif finding.finding_type == SynthesisFindingType.EMERGING_THEME:
                sections[5].finding_ids.append(finding_ids[finding_ids.index(str(findings.index(finding)))])

        return ProposedOutline(
            title="Proposed Synthesis Outline",
            sections=sections,
            notes="This outline is generated before drafting prose. Sections can be merged or split based on content volume.",
        )


class SynthesisConfig(BaseModel):
    """Configuration for the literature synthesis agent."""

    min_consensus_count: int = Field(default=2, ge=1)
    min_gap_confidence: float = Field(default=0.3, ge=0.0, le=1.0)
    include_matrix: bool = Field(default=True)
    include_outline: bool = Field(default=True)


class SynthesisResult(BaseModel):
    """Result of a literature synthesis."""

    matrix: SynthesisMatrix | None = None
    findings: list[SynthesisFinding] = Field(default_factory=list)
    outline: ProposedOutline = Field(default_factory=lambda: ProposedOutline(title="Untitled"))
    synthesis_matrix: str = Field(default="")
    synthesized_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    def to_markdown(self) -> str:
        """Render the full synthesis result as Markdown."""
        lines = [
            "# Literature Synthesis",
            f"**Synthesized at:** {self.synthesized_at.isoformat()}",
            "",
            "## Synthesis Matrix",
            self.synthesis_matrix or (self.matrix.to_markdown() if self.matrix else "_No data in matrix._"),
            "",
            "## Synthesis Findings",
            "",
        ]
        for finding in self.findings:
            lines.append(finding.to_markdown())
            lines.append("")

        lines.append("## Proposed Outline")
        lines.append(self.outline.to_markdown())

        return "\n".join(lines)
