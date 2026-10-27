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

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field

from .common import make_id, now_utc

# ---------------------------------------------------------------------------
# Severity and pass categories
# ---------------------------------------------------------------------------


class Severity(str, Enum):
    """Severity of a review finding."""

    CRITICAL = "critical"
    MAJOR = "major"
    MINOR = "minor"
    SUGGESTION = "suggestion"


class ReviewPass(str, Enum):
    """Review passes performed by the academic reviewer."""

    ABSTRACT = "abstract"
    STRUCTURE = "structure"
    EVIDENCE = "evidence"
    BIBLIOGRAPHY = "bibliography"
    ACADEMIC_QUALITY = "academic_quality"
    RESEARCH_INTEGRITY = "research_integrity"


# ---------------------------------------------------------------------------
# Review finding
# ---------------------------------------------------------------------------


class ReviewFinding(BaseModel):
    """A single finding from an academic review pass.

    Each finding is prioritized and includes enough information for the
    revision agent to address it.
    """

    id: str = Field(default_factory=lambda: str(make_id()))
    pass_name: ReviewPass = Field(..., description="Which review pass identified this")
    location: str = Field(
        ...,
        description="Where in the manuscript: section name or 'abstract' or 'bibliography'",
    )
    severity: Severity = Field(default=Severity.MINOR)
    title: str = Field(..., min_length=1, description="Short title of the finding")
    rationale: str = Field(
        ...,
        min_length=1,
        description="Why this is a problem (the reviewer's reasoning)",
    )
    evidence: str = Field(
        default="",
        description="Supporting evidence or quote from the manuscript",
    )
    suggested_correction: str = Field(
        default="",
        description="What the author should change",
    )
    resolved: bool = Field(default=False, description="Whether this finding has been addressed")
    resolution_note: str | None = Field(default=None)
    created_at: datetime = Field(default_factory=now_utc)

    def mark_resolved(self, note: str | None = None) -> None:
        """Mark this finding as resolved."""
        self.resolved = True
        self.resolution_note = note

    def _priority_value(self) -> int:
        """Lower value = higher priority."""
        severity_order = {
            Severity.CRITICAL: 0,
            Severity.MAJOR: 1,
            Severity.MINOR: 2,
            Severity.SUGGESTION: 3,
        }
        return severity_order.get(self.severity, 99)

    def __lt__(self, other: ReviewFinding) -> bool:
        return self._priority_value() < other._priority_value()


# ---------------------------------------------------------------------------
# Review report
# ---------------------------------------------------------------------------


class ReviewReport(BaseModel):
    """A complete academic review report with multiple passes."""

    title: str = Field(..., description="Title of the manuscript reviewed")
    findings: list[ReviewFinding] = Field(default_factory=list)
    review_date: datetime = Field(default_factory=now_utc)
    passes_performed: list[ReviewPass] = Field(default_factory=list)

    def add_finding(self, finding: ReviewFinding) -> None:
        """Add a finding to the report."""
        self.findings.append(finding)

    def get_unresolved(self) -> list[ReviewFinding]:
        """Return all unresolved findings."""
        return [f for f in self.findings if not f.resolved]

    def get_critical_findings(self) -> list[ReviewFinding]:
        """Return all critical severity findings."""
        return [f for f in self.findings if f.severity == Severity.CRITICAL]

    def get_findings_by_pass(self, pass_name: ReviewPass) -> list[ReviewFinding]:
        """Return findings from a specific review pass."""
        return [f for f in self.findings if f.pass_name == pass_name]

    def mark_all_resolved(self) -> int:
        """Mark all findings as resolved (used after verification)."""
        count = sum(1 for f in self.findings if not f.resolved)
        for f in self.findings:
            f.mark_resolved("Verified in subsequent review pass")
        return count

    def to_markdown(self) -> str:
        """Render the review report as Markdown."""
        lines = [f"# Review Report: {self.title}", f"Date: {self.review_date.strftime('%Y-%m-%d')}", ""]

        # Summary
        total = len(self.findings)
        unresolved = len(self.get_unresolved())
        critical = len(self.get_critical_findings())
        lines.append(f"**Total findings:** {total} | **Unresolved:** {unresolved} | **Critical:** {critical}")
        lines.append("")

        # Group by pass
        for pass_name in ReviewPass:
            pass_findings = self.get_findings_by_pass(pass_name)
            if not pass_findings:
                continue
            lines.append(f"## {pass_name.value.title()} Review")
            lines.append("")
            for f in sorted(pass_findings):
                status = "RESOLVED" if f.resolved else "OPEN"
                lines.append(f"### [{status}] {f.severity.value.upper()}: {f.title}")
                lines.append(f"**Location:** {f.location}")
                lines.append(f"**Rationale:** {f.rationale}")
                if f.evidence:
                    lines.append(f"**Evidence:** {f.evidence}")
                if f.suggested_correction:
                    lines.append(f"**Suggested correction:** {f.suggested_correction}")
                if f.resolution_note:
                    lines.append(f"**Resolution:** {f.resolution_note}")
                lines.append("")

        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Review criteria
# ---------------------------------------------------------------------------


class ReviewCriteria(BaseModel):
    """Configurable criteria for the academic reviewer."""

    max_severity_to_accept: Severity = Field(
        default=Severity.MINOR,
        description="Maximum severity level that can be auto-accepted (everything below is OK)",
    )
    require_human_approval_for: list[Severity] = Field(
        default_factory=lambda: [Severity.CRITICAL, Severity.MAJOR],
        description="Severities that require human approval before acceptance",
    )
    max_iterations: int = Field(
        default=5, ge=1, le=50,
        description="Maximum number of revision+review cycles",
    )
    require_all_critical_resolved: bool = Field(
        default=True,
        description="Whether all critical findings must be resolved to pass",
    )
    require_all_major_resolved: bool = Field(
        default=False,
        description="Whether all major findings must be resolved to pass",
    )

    def would_pass(self, report: ReviewReport) -> bool:
        """Determine whether the manuscript passes the review criteria."""
        unresolved = report.get_unresolved()
        if not unresolved:
            return True
        critical = [f for f in unresolved if f.severity == Severity.CRITICAL]
        if self.require_all_critical_resolved and critical:
            return False
        major = [f for f in unresolved if f.severity == Severity.MAJOR]
        if self.require_all_major_resolved and major:
            return False
        # Check against max_severity_to_accept
        acceptable_severities = {
            Severity.CRITICAL, Severity.MAJOR, Severity.MINOR, Severity.SUGGESTION
        }
        too_high = self.max_severity_to_accept
        severity_order = {
            Severity.SUGGESTION: 0,
            Severity.MINOR: 1,
            Severity.MAJOR: 2,
            Severity.CRITICAL: 3,
        }
        threshold = severity_order.get(too_high, 1)
        for f in unresolved:
            if severity_order.get(f.severity, 99) > threshold:
                return False
        return True

    def requires_human_approval(self, report: ReviewReport) -> bool:
        """Check if human approval is needed before accepting."""
        unresolved = report.get_unresolved()
        for f in unresolved:
            if f.severity in self.require_human_approval_for:
                return True
        return False
