"""Manuscript model with section templates, citation tracking, and versioning.

Supports narrative reviews, systematic reviews, scoping reviews,
and discipline-specific formats. Every section has an explicit purpose.
Citations resolve to known papers; references are never fabricated.
"""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field, field_validator

from .common import Status, now_utc

# ---------------------------------------------------------------------------
# Manuscript template types
# ---------------------------------------------------------------------------


class ManuscriptTemplate(StrEnum):
    """Predefined manuscript section templates."""

    NARRATIVE_REVIEW = "narrative_review"
    SYSTEMATIC_REVIEW = "systematic_review"
    SCOPING_REVIEW = "scoping_review"
    DISCIPLINE_SPECIFIC = "discipline_specific"

    def get_sections(self) -> list[SectionTemplate]:
        """Return the default sections for this template type."""
        section_map: dict[ManuscriptTemplate, list[SectionTemplate]] = {
            ManuscriptTemplate.NARRATIVE_REVIEW: [
                SectionTemplate(
                    name="abstract",
                    purpose="State the review question, scope, methods, key findings, and conclusions.",
                ),
                SectionTemplate(
                    name="introduction",
                    purpose="Frame the research question, review scope, and rationale.",
                ),
                SectionTemplate(
                    name="methods",
                    purpose="Describe search strategy, inclusion/exclusion criteria, and analysis approach.",
                ),
                SectionTemplate(
                    name="results",
                    purpose="Synthesize findings across papers, noting consensus and contradictions.",
                ),
                SectionTemplate(
                    name="discussion",
                    purpose="Interpret findings, discuss limitations, and suggest implications.",
                ),
                SectionTemplate(
                    name="conclusion",
                    purpose="Summarize key contributions and identify future research directions.",
                ),
            ],
            ManuscriptTemplate.SYSTEMATIC_REVIEW: [
                SectionTemplate(
                    name="abstract",
                    purpose="State the review question, methods, results, and conclusions per PRISMA.",
                ),
                SectionTemplate(
                    name="introduction",
                    purpose="Frame the PICO question and rationale.",
                ),
                SectionTemplate(
                    name="methods",
                    purpose="Detail protocol, search strategy, screening process, quality assessment.",
                ),
                SectionTemplate(
                    name="results",
                    purpose="PRISMA flow, study characteristics, risk-of-bias, synthesis of results.",
                ),
                SectionTemplate(
                    name="discussion",
                    purpose="Interpret findings in context, discuss limitations and implications.",
                ),
                SectionTemplate(
                    name="conclusion",
                    purpose="State evidence-based conclusions and practice/research implications.",
                ),
            ],
            ManuscriptTemplate.SCOPING_REVIEW: [
                SectionTemplate(
                    name="abstract",
                    purpose="State the scoping question, aims, and key findings.",
                ),
                SectionTemplate(
                    name="introduction",
                    purpose="Frame the scope of the mapping exercise and its need.",
                ),
                SectionTemplate(
                    name="methods",
                    purpose="Describe the scoping methodology (e.g., JBI or Arksey & O'Brien).",
                ),
                SectionTemplate(
                    name="results",
                    purpose="Characterize the literature landscape, themes, and gaps.",
                ),
                SectionTemplate(
                    name="discussion",
                    purpose="Interpret the landscape, identify gaps, suggest future work.",
                ),
                SectionTemplate(
                    name="conclusion",
                    purpose="Summarize the state of the field and next steps.",
                ),
            ],
            ManuscriptTemplate.DISCIPLINE_SPECIFIC: [
                SectionTemplate(
                    name="abstract",
                    purpose="Provide a concise summary tailored to the discipline.",
                ),
                SectionTemplate(
                    name="introduction",
                    purpose="Set context and frame the disciplinary question.",
                ),
                SectionTemplate(
                    name="methods",
                    purpose="Describe the analytical or empirical approach.",
                ),
                SectionTemplate(
                    name="results",
                    purpose="Present findings without interpretation.",
                ),
                SectionTemplate(
                    name="discussion",
                    purpose="Interpret within disciplinary conventions and theory.",
                ),
                SectionTemplate(
                    name="conclusion",
                    purpose="State contributions and implications for the discipline.",
                ),
            ],
        }
        return section_map.get(self, section_map[ManuscriptTemplate.NARRATIVE_REVIEW])


# ---------------------------------------------------------------------------
# Section model
# ---------------------------------------------------------------------------


class SectionTemplate(BaseModel):
    """A template defining the purpose of a manuscript section."""

    name: str = Field(..., min_length=1, description="Section name (e.g., 'introduction')")
    purpose: str = Field(..., min_length=1, description="Why this section exists in the manuscript")


class ManuscriptSection(BaseModel):
    """A single section of a manuscript with provenance tracking."""

    name: str = Field(..., min_length=1, description="Section name")
    purpose: str = Field(..., min_length=1, description="Purpose of this section")
    content: str = Field(default="", min_length=0, description="Section markdown content")
    citations_used: list[str] = Field(
        default_factory=list,
        description="Paper IDs referenced in this section",
    )
    status: Status = Field(default=Status.PENDING, description="Section draft status")
    completed_at: datetime | None = Field(default=None)

    def mark_completed(self) -> None:
        """Mark this section as complete."""
        self.status = Status.COMPLETED
        self.completed_at = now_utc()


# ---------------------------------------------------------------------------
# Manuscript model
# ---------------------------------------------------------------------------


class Manuscript(BaseModel):
    """A research manuscript with sections, version tracking, and citation integrity.

    Every in-text citation must resolve to a known paper ID.
    References are never fabricated.
    """

    title: str = Field(..., min_length=1)
    template: ManuscriptTemplate = Field(
        default=ManuscriptTemplate.NARRATIVE_REVIEW,
        description="Section template to use",
    )
    sections: dict[str, ManuscriptSection] = Field(default_factory=dict, description="Section name -> section data")
    version: int = Field(default=1, ge=1)
    reference_ids: list[str] = Field(
        default_factory=list,
        description="Unique paper IDs in the bibliography (never fabricated)",
    )
    status: Status = Field(default=Status.PENDING)
    metadata: dict[str, str] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=now_utc)
    updated_at: datetime = Field(default_factory=now_utc)

    @field_validator("reference_ids")
    @classmethod
    def _deduplicate_references(cls, v: list[str]) -> list[str]:
        seen: set[str] = set()
        unique: list[str] = []
        for r in v:
            if r not in seen:
                seen.add(r)
                unique.append(r)
        return unique

    # ------------------------------------------------------------------
    # Section management
    # ------------------------------------------------------------------

    @classmethod
    def from_template(
        cls,
        title: str,
        template: ManuscriptTemplate,
    ) -> Manuscript:
        """Create a manuscript pre-populated from a template."""
        sections: dict[str, ManuscriptSection] = {}
        for st in template.get_sections():
            sections[st.name] = ManuscriptSection(
                name=st.name,
                purpose=st.purpose,
            )
        return cls(title=title, template=template, sections=sections)

    def add_section(self, name: str, purpose: str, content: str = "") -> ManuscriptSection:
        """Add a custom section to the manuscript."""
        section = ManuscriptSection(name=name, purpose=purpose, content=content)
        self.sections[name] = section
        return section

    def set_section_content(self, name: str, content: str, citations: list[str] | None = None) -> None:
        """Set the content of a named section and record its citations."""
        if name not in self.sections:
            raise KeyError(f"Section '{name}' does not exist in this manuscript")
        section = self.sections[name]
        section.content = content
        if citations:
            section.citations_used = list(set(section.citations_used) | set(citations))
        section.mark_completed()

    # ------------------------------------------------------------------
    # Citation integrity
    # ------------------------------------------------------------------

    def add_reference(self, paper_id: str) -> None:
        """Add a paper ID to the reference list. Deduplicates."""
        if paper_id not in self.reference_ids:
            self.reference_ids.append(paper_id)

    def validate_citations(self, known_paper_ids: set[str]) -> list[str]:
        """Check every citation in the manuscript against known papers.

        Returns a list of unresolved citation IDs (empty list means all valid).
        """
        unresolved: set[str] = set()
        for section in self.sections.values():
            for cid in section.citations_used:
                if cid not in known_paper_ids:
                    unresolved.add(cid)
        # Also check reference_ids are a subset
        for rid in self.reference_ids:
            if rid not in known_paper_ids:
                unresolved.add(rid)
        return sorted(unresolved)

    def get_cited_paper_ids(self) -> list[str]:
        """Return all unique paper IDs cited in manuscript sections."""
        ids: set[str] = set()
        for section in self.sections.values():
            ids.update(section.citations_used)
        return sorted(ids)

    def has_uncited_bibliography(self) -> bool:
        """Check if any bibliography entries are not cited in text."""
        cited = set(self.get_cited_paper_ids())
        return any(rid not in cited for rid in self.reference_ids)

    # ------------------------------------------------------------------
    # Versioning
    # ------------------------------------------------------------------

    def bump_version(self) -> int:
        """Increment the version number and update timestamp."""
        self.version += 1
        self.updated_at = now_utc()
        return self.version

    # ------------------------------------------------------------------
    # Serialisation
    # ------------------------------------------------------------------

    def to_markdown(self) -> str:
        """Render the manuscript as Markdown."""
        parts: list[str] = [f"# {self.title}", ""]
        for section in self.sections.values():
            if section.content:
                parts.append(f"## {section.name.title()}")
                parts.append("")
                parts.append(section.content)
                parts.append("")
        return "\n".join(parts)
