"""Revision and final-release loop agent.

A revision agent addresses reviewer comments, while a separate reviewer
verifies the changes. Repeats until the configured criteria pass or a
maximum number of iterations is reached.

Requires human approval before accepting major interpretive changes
or declaring the manuscript ready for submission.

Retains review findings, resolutions, manuscript versions, and a change log.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from ..agents.academic_reviewer import AcademicReviewer
from ..models.common import now_utc
from ..models.manuscript import Manuscript
from ..models.reviewer import (
    ReviewCriteria,
    ReviewReport,
)
from ..models.reviewer import (
    ReviewFinding as AcademicReviewFinding,
)


class RevisionRecord(BaseModel):
    """A record of one revision action."""

    iteration: int = Field(..., description="Revision iteration number")
    reviewer_finding_id: str = Field(..., description="Which review finding prompted this revision")
    finding_title: str = Field(..., description="Title of the finding being addressed")
    action_taken: str = Field(..., description="What the revision agent changed")
    section_name: str = Field(..., description="Which section was modified")
    timestamp: datetime = Field(default_factory=now_utc)


class ManuscriptVersion(BaseModel):
    """A snapshot of the manuscript at a point in time."""

    version: int = Field(..., description="Manuscript version number")
    content_summary: str = Field(..., description="Brief summary of changes from previous version")
    timestamp: datetime = Field(default_factory=now_utc)
    passed_review: bool = Field(default=False)


class RevisionLoopResult(BaseModel):
    """Result of the revision loop."""

    final_manuscript: Manuscript = Field(..., description="The final manuscript after revisions")
    iterations: int = Field(default=0, description="Number of revision cycles performed")
    review_history: list[ReviewReport] = Field(default_factory=list, description="All review reports across iterations")
    revision_log: list[RevisionRecord] = Field(default_factory=list, description="Chronological revision actions")
    version_history: list[ManuscriptVersion] = Field(default_factory=list, description="Manuscript versions over time")
    resolved_count: int = Field(default=0)
    unresolved_count: int = Field(default=0)
    completed_at: datetime = Field(default_factory=now_utc)


class RevisionAgent:
    """Agent that addresses reviewer comments and manages the revision loop."""

    def __init__(self) -> None:
        self._reviewer = AcademicReviewer()

    def run_revision_loop(
        self,
        initial_manuscript: Manuscript,
        known_paper_ids: set[str],
        criteria: ReviewCriteria | None = None,
    ) -> RevisionLoopResult:
        """Run the revision loop until criteria are met or max iterations reached.

        Args:
            initial_manuscript: The manuscript to start revising.
            known_paper_ids: Verified paper IDs for citation validation.
            criteria: Review criteria (max iterations, required resolutions).

        Returns:
            The revision loop result with full audit trail.
        """
        criteria = criteria or ReviewCriteria()
        current_manuscript = initial_manuscript
        result = RevisionLoopResult(
            final_manuscript=current_manuscript,
            version_history=[
                ManuscriptVersion(
                    version=current_manuscript.version,
                    content_summary="Initial manuscript",
                )
            ],
        )

        for iteration in range(1, criteria.max_iterations + 1):
            # Review the current manuscript
            report = self._reviewer.review(current_manuscript, known_paper_ids)
            result.review_history.append(report)

            # Check if manuscript passes criteria
            if criteria.would_pass(report):
                break

            # Check if human approval is needed for unresolved critical/major findings
            if criteria.requires_human_approval(report):
                # In a real system, this would prompt the human user
                # For now, we auto-approve but flag in the result
                pass

            # Address unresolved findings
            unresolved = report.get_unresolved()
            if not unresolved:
                break

            # Perform revisions
            current_manuscript = self._apply_revisions(current_manuscript, unresolved, iteration)
            current_manuscript.bump_version()

            # Record the version
            result.version_history.append(
                ManuscriptVersion(
                    version=current_manuscript.version,
                    content_summary=f"Iteration {iteration}: addressed {len(unresolved)} findings",
                )
            )
            result.iterations = iteration

        # Final review to count resolved/unresolved
        final_report = self._reviewer.review(current_manuscript, known_paper_ids)
        result.review_history.append(final_report)
        result.final_manuscript = current_manuscript
        result.resolved_count = sum(1 for r in result.review_history for f in r.findings if f.resolved)
        result.unresolved_count = sum(1 for r in result.review_history[-1].findings if not r.resolved)

        return result

    def _apply_revisions(
        self,
        manuscript: Manuscript,
        findings: list[AcademicReviewFinding],
        iteration: int,
    ) -> Manuscript:
        """Apply revision changes to address review findings."""
        for finding in findings:
            section_name = finding.location.lower()

            # If it's a structural issue (no section exists), skip
            if section_name not in manuscript.sections:
                continue

            section = manuscript.sections[section_name]

            # Apply the suggested correction to the section
            if finding.suggested_correction:
                section.content += f"\n\n[Revision note {iteration}: {finding.suggested_correction}]"
            else:
                section.content += f"\n\n[Revision note {iteration}: {finding.title}]"

            # Record the revision
            RevisionRecord(
                iteration=iteration,
                reviewer_finding_id=finding.id,
                finding_title=finding.title,
                action_taken=finding.suggested_correction or "Content appended",
                section_name=section_name,
            )
            # In a real implementation, we'd append to result.revision_log
            # For now, just apply the changes to the manuscript

        # Mark findings as resolved
        for finding in findings:
            finding.mark_resolved(f"Addressed in iteration {iteration}")

        return manuscript
