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

from enum import Enum

from pydantic import BaseModel, Field

from ..models.evidence import ResearchNote
from ..models.paper import Paper


class SynthesisFindingType(str, Enum):
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

    title: str = Field(..., min_length=1)
    sections: list[ProposedSection] = Field(default_factory=list)
    notes: str = Field(default="", description="Additional notes about the outline")


class SynthesisResult(BaseModel):
    """The result of a literature synthesis."""

    findings: list[SynthesisFinding] = Field(default_factory=list)
    outline: ProposedOutline = Field(default_factory=lambda: ProposedOutline(title=""))
    synthesis_matrix: str = Field(
        default="",
        description="Markdown table comparing papers across key dimensions",
    )


class LiteratureSynthesisAgent:
    """Agent that synthesizes findings across a set of research papers."""

    def __init__(self) -> None:
        pass

    def synthesize(
        self,
        papers: list[Paper],
        notes: list[ResearchNote],
    ) -> SynthesisResult:
        """Perform literature synthesis on the given papers and their notes."""
        findings: list[SynthesisFinding] = []
        paper_ids = [n.paper_id for n in notes]

        # Identify consensus: papers that report similar main results
        consensus_results = self._find_consensus(notes)
        for desc, supporting in consensus_results:
            findings.append(
                SynthesisFinding(
                    finding_type=SynthesisFindingType.CONSENSUS,
                    title=f"Consensus: {desc}",
                    description=desc,
                    supporting_paper_ids=supporting,
                    confidence=0.7,
                )
            )

        # Identify contradictions
        contradictions = self._find_contradictions(notes)
        for desc, supporting, conflicting in contradictions:
            findings.append(
                SynthesisFinding(
                    finding_type=SynthesisFindingType.CONTRADICTION,
                    title=f"Contradiction: {desc}",
                    description=desc,
                    supporting_paper_ids=supporting,
                    conflicting_paper_ids=conflicting,
                    confidence=0.5,
                    notes="Further investigation recommended",
                )
            )

        # Identify evidence gaps
        gaps = self._find_evidence_gaps(notes)
        for desc in gaps:
            findings.append(
                SynthesisFinding(
                    finding_type=SynthesisFindingType.GAP,
                    title=f"Gap: {desc}",
                    description=desc,
                    confidence=0.6,
                    notes="No direct evidence found in the reviewed literature",
                )
            )

        # Build outline from findings
        sections = [
            ProposedSection(
                title="Introduction",
                description="Frame the review question and scope",
            ),
            ProposedSection(
                title="Methods",
                description="Describe search strategy and analysis approach",
            ),
            ProposedSection(
                title="Synthesis Findings",
                description="Present key findings organized by theme",
                subsections=[f.title for f in findings],
            ),
            ProposedSection(
                title="Discussion",
                description="Interpret findings and discuss implications",
            ),
            ProposedSection(
                title="Conclusion",
                description="Summarize contributions and future directions",
            ),
        ]

        return SynthesisResult(
            findings=findings,
            outline=ProposedOutline(
                title="Synthesis Manuscript",
                sections=sections,
            ),
            synthesis_matrix=self._build_matrix(notes),
        )

    def _find_consensus(self, notes: list[ResearchNote]) -> list[tuple[str, list[str]]]:
        """Find areas where papers agree on main results."""
        results: dict[str, list[str]] = {}
        for note in notes:
            main = note.main_results
            if main and main != "Unknown":
                # Simple keyword-based consensus detection
                for keyword in ["improves", "effective", "significant", "positive", "reduces"]:
                    if keyword in main.lower():
                        results.setdefault(f"Papers report {keyword} effects", []).append(
                            note.paper_id
                        )
        return [
            (desc, pids)
            for desc, pids in results.items()
            if len(pids) >= 2
        ]

    def _find_contradictions(self, notes: list[ResearchNote]) -> list[tuple[str, list[str], list[str]]]:
        """Find areas where papers disagree."""
        positive: list[str] = []
        negative: list[str] = []
        for note in notes:
            main = note.main_results
            if main and main != "Unknown":
                if any(w in main.lower() for w in ["positive", "improves", "effective"]):
                    positive.append(note.paper_id)
                elif any(w in main.lower() for w in ["negative", "worsens", "ineffective", "no effect"]):
                    negative.append(note.paper_id)
        if positive and negative:
            return [
                ("Conflicting effects on outcome", positive, negative)
            ]
        return []

    def _find_evidence_gaps(self, notes: list[ResearchNote]) -> list[str]:
        """Identify potential evidence gaps."""
        gaps: list[str] = []
        for note in notes:
            if note.open_questions and note.open_questions != "Unknown":
                gaps.append(note.open_questions)
        return gaps[:5]  # Limit to top 5

    def _build_matrix(self, notes: list[ResearchNote]) -> str:
        """Build a synthesis matrix comparing papers."""
        lines = [
            "| Paper | Methodology | Main Results | Limitations |",
            "|---|---|---|---|",
        ]
        for note in notes:
            lines.append(
                f"| {note.title} | {note.methodology[:30]} | {note.main_results[:30]} | {note.limitations[:30]} |"
            )
        return "\n".join(lines)
