"""Application Review domain models (docs/07D-1)."""

from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum

from pydantic import BaseModel, Field

from job_platform.shared.ids import new_id


class ReviewStatus(StrEnum):
    APPROVED = "approved"
    APPROVED_WITH_WARNINGS = "approved_with_warnings"
    CHANGES_REQUIRED = "changes_required"
    USER_INPUT_REQUIRED = "user_input_required"
    MANUAL_REVIEW_REQUIRED = "manual_review_required"
    BLOCKED = "blocked"
    FAILED = "failed"


class Severity(StrEnum):
    BLOCKING = "blocking"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFORMATIONAL = "informational"


class ReviewFinding(BaseModel):
    """docs/07D-1 Finding Model."""

    finding_id: str = Field(default_factory=lambda: new_id("finding"))
    category: str
    severity: Severity
    artifact: str = ""
    message: str
    evidence: list[str] = Field(default_factory=list)
    recommended_action: str = ""
    automatically_correctable: bool = False
    requires_user_input: bool = False


class ReviewReport(BaseModel):
    """docs/07D-1 Review Output."""

    review_id: str = Field(default_factory=lambda: new_id("review"))
    package_id: str
    review_stage: str = "preparation"
    status: ReviewStatus = ReviewStatus.APPROVED
    findings: list[ReviewFinding] = Field(default_factory=list)
    required_user_actions: list[str] = Field(default_factory=list)
    auto_corrections: list[str] = Field(default_factory=list)
    reviewed_artifacts: list[str] = Field(default_factory=list)
    reviewed_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @property
    def blocking_findings(self) -> list[ReviewFinding]:
        return [f for f in self.findings if f.severity == Severity.BLOCKING]

    @property
    def warnings(self) -> list[ReviewFinding]:
        return [
            f
            for f in self.findings
            if f.severity in (Severity.HIGH, Severity.MEDIUM, Severity.LOW)
        ]

    def derive_status(self, block_on_high_severity: bool = True) -> ReviewStatus:
        """Compute the report status from its findings (docs/07D-1 statuses).

        Findings that need user input map to ``user_input_required`` rather
        than ``blocked``; ``changes_required`` applies only when every
        submission-stopping finding is automatically correctable.
        """

        def stops_submission(finding: ReviewFinding) -> bool:
            return finding.severity == Severity.BLOCKING or (
                block_on_high_severity and finding.severity == Severity.HIGH
            )

        blocking = [
            f for f in self.findings if stops_submission(f) and not f.requires_user_input
        ]
        if blocking:
            if all(f.automatically_correctable for f in blocking):
                return ReviewStatus.CHANGES_REQUIRED
            return ReviewStatus.BLOCKED
        if any(f.requires_user_input for f in self.findings):
            return ReviewStatus.USER_INPUT_REQUIRED
        if self.warnings:
            return ReviewStatus.APPROVED_WITH_WARNINGS
        return ReviewStatus.APPROVED
