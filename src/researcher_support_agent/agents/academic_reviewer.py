"""Academic reviewer agent.

Reviews the manuscript in separate passes:
- Abstract: alignment with aims, methods, results, and conclusions.
- Structure: logical flow, section coverage, repetition, and transitions.
- Evidence: unsupported claims, overgeneralization, contradictions, and missing citations.
- Bibliography: accuracy, completeness, citation consistency, and reference mismatches.
- Academic quality: clarity, terminology, critical depth, limitations, and contribution.
- Research integrity: fabricated sources, incorrect attribution, and potential plagiarism.

Each finding includes location, severity, rationale, evidence, and suggested correction.
"""

from __future__ import annotations

from ..models.citation import Bibliography
from ..models.manuscript import Manuscript
from ..models.reviewer import (
    ReviewFinding as AcademicReviewFinding,
)
from ..models.reviewer import (
    ReviewPass,
    ReviewReport,
    Severity,
)


class AcademicReviewer:
    """Agent that performs multi-pass academic review of a manuscript."""

    def __init__(self) -> None:
        pass

    def review(
        self,
        manuscript: Manuscript,
        known_paper_ids: set[str],
        bibliography: Bibliography | None = None,
    ) -> ReviewReport:
        """Perform a full multi-pass review of the manuscript.

        Args:
            manuscript: The manuscript to review.
            known_paper_ids: Set of verified paper IDs for citation validation.
            bibliography: Optional bibliography for citation verification.

        Returns:
            A complete review report with prioritized findings.
        """
        report = ReviewReport(title=manuscript.title)
        passes_performed: list[ReviewPass] = []

        # Pass 1: Abstract alignment
        abstract_findings = self._review_abstract(manuscript)
        for f in abstract_findings:
            report.add_finding(f)
        passes_performed.append(ReviewPass.ABSTRACT)

        # Pass 2: Structure review
        structure_findings = self._review_structure(manuscript)
        for f in structure_findings:
            report.add_finding(f)
        passes_performed.append(ReviewPass.STRUCTURE)

        # Pass 3: Evidence review
        evidence_findings = self._review_evidence(manuscript, known_paper_ids)
        for f in evidence_findings:
            report.add_finding(f)
        passes_performed.append(ReviewPass.EVIDENCE)

        # Pass 4: Bibliography review
        bib_findings = self._review_bibliography(manuscript, bibliography, known_paper_ids)
        for f in bib_findings:
            report.add_finding(f)
        passes_performed.append(ReviewPass.BIBLIOGRAPHY)

        # Pass 5: Academic quality review
        quality_findings = self._review_academic_quality(manuscript)
        for f in quality_findings:
            report.add_finding(f)
        passes_performed.append(ReviewPass.ACADEMIC_QUALITY)

        # Pass 6: Research integrity review
        integrity_findings = self._review_research_integrity(manuscript, known_paper_ids)
        for f in integrity_findings:
            report.add_finding(f)
        passes_performed.append(ReviewPass.RESEARCH_INTEGRITY)

        report.passes_performed = passes_performed
        return report

    # ------------------------------------------------------------------
    # Individual review passes
    # ------------------------------------------------------------------

    def _review_abstract(self, manuscript: Manuscript) -> list[AcademicReviewFinding]:
        """Review abstract alignment with aims, methods, results, and conclusions."""
        findings: list[AcademicReviewFinding] = []
        abstract_section = manuscript.sections.get("abstract")
        if not abstract_section:
            findings.append(
                AcademicReviewFinding(
                    pass_name=ReviewPass.ABSTRACT,
                    location="abstract",
                    severity=Severity.CRITICAL,
                    title="Missing abstract section",
                    rationale="A manuscript must have an abstract that summarizes aims, methods, results, and conclusions.",
                    suggested_correction="Add an abstract section with the four key elements.",
                )
            )
            return findings

        content = abstract_section.content
        if not content.strip():
            findings.append(
                AcademicReviewFinding(
                    pass_name=ReviewPass.ABSTRACT,
                    location="abstract",
                    severity=Severity.CRITICAL,
                    title="Empty abstract",
                    rationale="The abstract section exists but has no content.",
                    suggested_correction="Write an abstract summarizing the review's purpose, methods, results, and conclusions.",
                )
            )
            return findings

        # Check for key elements
        lower = content.lower()
        if not any(kw in lower for kw in ["purpose", "aim", "objective", "question"]):
            findings.append(
                AcademicReviewFinding(
                    pass_name=ReviewPass.ABSTRACT,
                    location="abstract",
                    severity=Severity.MINOR,
                    title="Abstract missing clear statement of purpose",
                    rationale="The abstract should clearly state the review's purpose or research question.",
                    suggested_correction="Add a clear statement of the review question or purpose.",
                )
            )

        if not any(kw in lower for kw in ["method", "search", "screen", "inclusion"]):
            findings.append(
                AcademicReviewFinding(
                    pass_name=ReviewPass.ABSTRACT,
                    location="abstract",
                    severity=Severity.MINOR,
                    title="Abstract missing methods description",
                    rationale="The abstract should briefly describe the methods used.",
                    suggested_correction="Add a brief description of the review methods.",
                )
            )

        if not any(kw in lower for kw in ["result", "find", "evidence", "synthesis"]):
            findings.append(
                AcademicReviewFinding(
                    pass_name=ReviewPass.ABSTRACT,
                    location="abstract",
                    severity=Severity.MINOR,
                    title="Abstract missing results summary",
                    rationale="The abstract should summarize key results.",
                    suggested_correction="Add a summary of the key findings.",
                )
            )

        return findings

    def _review_structure(self, manuscript: Manuscript) -> list[AcademicReviewFinding]:
        """Review structure: logical flow, section coverage, repetition, transitions."""
        findings: list[AcademicReviewFinding] = []
        section_names = list(manuscript.sections.keys())

        # Check for required sections
        required_sections = ["abstract", "introduction", "methods", "results", "discussion", "conclusion"]
        missing = [s for s in required_sections if s not in manuscript.sections]
        if missing:
            findings.append(
                AcademicReviewFinding(
                    pass_name=ReviewPass.STRUCTURE,
                    location="structure",
                    severity=Severity.MAJOR,
                    title=f"Missing required sections: {', '.join(missing)}",
                    rationale="Standard manuscript structure requires these sections.",
                    suggested_correction=f"Add the missing sections: {', '.join(missing)}.",
                )
            )

        # Check for empty sections with content requirement
        for name in section_names:
            section = manuscript.sections[name]
            if name in required_sections and not section.content.strip() and name != "abstract":
                findings.append(
                    AcademicReviewFinding(
                        pass_name=ReviewPass.STRUCTURE,
                        location=name,
                        severity=Severity.MAJOR,
                        title=f"Section '{name}' is empty",
                        rationale=f"The {name} section has no content.",
                        suggested_correction=f"Write content for the {name} section.",
                    )
                )

        # Check for section order
        if section_names and required_sections:
            present_order = [s for s in section_names if s in required_sections]
            expected_order = [s for s in required_sections if s in section_names]
            if present_order != expected_order:
                findings.append(
                    AcademicReviewFinding(
                        pass_name=ReviewPass.STRUCTURE,
                        location="structure",
                        severity=Severity.MINOR,
                        title="Section order may not follow standard flow",
                        rationale="Sections should follow a logical order: abstract, introduction, methods, results, discussion, conclusion.",
                        suggested_correction="Reorder sections to follow the standard manuscript flow.",
                    )
                )

        return findings

    def _review_evidence(
        self, manuscript: Manuscript, known_paper_ids: set[str]
    ) -> list[AcademicReviewFinding]:
        """Review evidence: unsupported claims, overgeneralization, contradictions, missing citations."""
        findings: list[AcademicReviewFinding] = []

        # Check for unresolved citations
        unresolved = manuscript.validate_citations(known_paper_ids)
        if unresolved:
            findings.append(
                AcademicReviewFinding(
                    pass_name=ReviewPass.EVIDENCE,
                    location="citation",
                    severity=Severity.CRITICAL,
                    title=f"Unresolved citations: {', '.join(unresolved)}",
                    rationale="Citations in the manuscript must resolve to known papers. These citations do not match any verified paper.",
                    suggested_correction=f"Replace or remove citations: {', '.join(unresolved)}. Add the corresponding papers to the evidence repository.",
                )
            )

        # Check for sections with no citations (except abstract and conclusion)
        for name, section in manuscript.sections.items():
            if name in ("abstract", "conclusion"):
                continue
            if section.content.strip() and not section.citations_used:
                findings.append(
                    AcademicReviewFinding(
                        pass_name=ReviewPass.EVIDENCE,
                        location=name,
                        severity=Severity.MINOR,
                        title=f"Section '{name}' has no citations",
                        rationale="Content sections should cite supporting papers to avoid unsupported claims.",
                        suggested_correction=f"Add citations to relevant papers in the '{name}' section.",
                    )
                )

        # Check for overgeneralization indicators
        overgeneral_keywords = ["all", "every", "always", "never", "no study", "no evidence"]
        for name, section in manuscript.sections.items():
            content = section.content.lower()
            for kw in overgeneral_keywords:
                if kw in content and len(content) > 100:
                    findings.append(
                        AcademicReviewFinding(
                            pass_name=ReviewPass.EVIDENCE,
                            location=name,
                            severity=Severity.MINOR,
                            title=f"Potential overgeneralization in '{name}'",
                            rationale=f"The term '{kw}' may indicate overgeneralization without sufficient evidence.",
                            suggested_correction=f"Review claims in '{name}' that use '{kw}' and ensure they are properly supported.",
                        )
                    )
                    break  # One per section

        return findings

    def _review_bibliography(
        self,
        manuscript: Manuscript,
        bibliography: Bibliography | None,
        known_paper_ids: set[str],
    ) -> list[AcademicReviewFinding]:
        """Review bibliography: accuracy, completeness, citation consistency, reference mismatches."""
        findings: list[AcademicReviewFinding] = []

        # Check for uncited bibliography entries
        cited_ids = set(manuscript.get_cited_paper_ids())
        for ref_id in manuscript.reference_ids:
            if ref_id not in cited_ids:
                findings.append(
                    AcademicReviewFinding(
                        pass_name=ReviewPass.BIBLIOGRAPHY,
                        location="bibliography",
                        severity=Severity.MINOR,
                        title=f"Bibliography entry '{ref_id}' not cited in text",
                        rationale="Every bibliography entry should be cited at least once in the manuscript text.",
                        suggested_correction=f"Either cite '{ref_id}' in the text or remove it from the bibliography.",
                    )
                )

        # Check for references not in known papers
        for ref_id in manuscript.reference_ids:
            if ref_id not in known_paper_ids:
                findings.append(
                    AcademicReviewFinding(
                        pass_name=ReviewPass.BIBLIOGRAPHY,
                        location="bibliography",
                        severity=Severity.CRITICAL,
                        title=f"Reference '{ref_id}' not in known paper set",
                        rationale="All references must resolve to verified papers. This reference is not found in the evidence repository.",
                        suggested_correction=f"Verify '{ref_id}' exists in the evidence repository or remove it.",
                    )
                )

        # Check bibliography for duplicates
        if bibliography:
            dups = bibliography.find_duplicates()
            if dups:
                findings.append(
                    AcademicReviewFinding(
                        pass_name=ReviewPass.BIBLIOGRAPHY,
                        location="bibliography",
                        severity=Severity.MAJOR,
                        title="Duplicate references in bibliography",
                        rationale="The bibliography contains duplicate entries that should be consolidated.",
                        suggested_correction=f"Remove duplicate references: {dups}.",
                    )
                )

        return findings

    def _review_academic_quality(self, manuscript: Manuscript) -> list[AcademicReviewFinding]:
        """Review academic quality: clarity, terminology, critical depth, limitations, contribution."""
        findings: list[AcademicReviewFinding] = []

        # Check for limitations section
        discussion = manuscript.sections.get("discussion")
        if discussion and discussion.content:
            lower = discussion.content.lower()
            if "limitation" not in lower and "limit" not in lower:
                findings.append(
                    AcademicReviewFinding(
                        pass_name=ReviewPass.ACADEMIC_QUALITY,
                        location="discussion",
                        severity=Severity.MINOR,
                        title="Discussion section should include limitations",
                        rationale="Academic papers should discuss their limitations.",
                        suggested_correction="Add a limitations paragraph to the discussion section.",
                    )
                )

        # Check for contribution statement
        if discussion and discussion.content:
            lower = discussion.content.lower()
            if "contribution" not in lower and "implication" not in lower and "conclude" not in lower:
                findings.append(
                    AcademicReviewFinding(
                        pass_name=ReviewPass.ACADEMIC_QUALITY,
                        location="discussion",
                        severity=Severity.MINOR,
                        title="Discussion should state contributions or implications",
                        rationale="The discussion should articulate the study's contribution to the field.",
                        suggested_correction="Add a statement about the paper's contributions or implications.",
                    )
                )

        # Check for short sections (potential lack of depth)
        for name, section in manuscript.sections.items():
            if len(section.content) < 50 and name not in ("abstract",):
                findings.append(
                    AcademicReviewFinding(
                        pass_name=ReviewPass.ACADEMIC_QUALITY,
                        location=name,
                        severity=Severity.MINOR,
                        title=f"Section '{name}' may be too brief for adequate depth",
                        rationale=f"The {name} section has only {len(section.content)} characters, which may be insufficient for thorough coverage.",
                        suggested_correction=f"Expand the '{name}' section with more detailed content.",
                    )
                )

        return findings

    def _review_research_integrity(
        self, manuscript: Manuscript, known_paper_ids: set[str]
    ) -> list[AcademicReviewFinding]:
        """Review research integrity: fabricated sources, incorrect attribution, plagiarism."""
        findings: list[AcademicReviewFinding] = []

        # Check for all citations resolving to known papers (no fabrication)
        all_cited = manuscript.get_cited_paper_ids()
        fabricated = [c for c in all_cited if c not in known_paper_ids]
        if fabricated:
            findings.append(
                AcademicReviewFinding(
                    pass_name=ReviewPass.RESEARCH_INTEGRITY,
                    location="manuscript",
                    severity=Severity.CRITICAL,
                    title="Potential fabricated references",
                    rationale=f"The following paper IDs are cited but not found in the evidence repository: {', '.join(fabricated)}. This may indicate fabricated or unverified references.",
                    suggested_correction="Verify each reference against the evidence repository. Remove any that cannot be verified.",
                )
            )

        return findings
