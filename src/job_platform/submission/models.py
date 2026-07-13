"""Submission domain models (docs/10).

Submission is the only irreversible action in the system, so its state is
modeled explicitly: a durable attempt exists before any click, evidence is
graded by strength, and insufficient evidence lands in the protected
Submission Unknown state rather than an optimistic success.
"""

from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum

from pydantic import BaseModel, Field

from job_platform.shared.ids import new_id


def _now() -> datetime:
    return datetime.now(UTC)


class SubmissionOutcome(StrEnum):
    SUBMITTED = "submitted"
    FAILED = "failed"
    ALREADY_APPLIED = "already_applied"
    APPLICATION_CLOSED = "application_closed"
    CANCELLED = "cancelled"
    SUBMISSION_UNKNOWN = "submission_unknown"


class AttemptStatus(StrEnum):
    ATTEMPT_CREATED = "attempt_created"
    CLICK_INITIATED = "click_initiated"
    VERIFICATION_PENDING = "verification_pending"
    SUBMITTED = "submitted"
    FAILED_BEFORE_CLICK = "failed_before_click"
    FAILED_AFTER_CLICK = "failed_after_click"
    ALREADY_APPLIED = "already_applied"
    APPLICATION_CLOSED = "application_closed"
    CANCELLED_BEFORE_CLICK = "cancelled_before_click"
    SUBMISSION_UNKNOWN = "submission_unknown"

    @property
    def terminal(self) -> bool:
        return self in (
            AttemptStatus.SUBMITTED,
            AttemptStatus.FAILED_BEFORE_CLICK,
            AttemptStatus.FAILED_AFTER_CLICK,
            AttemptStatus.ALREADY_APPLIED,
            AttemptStatus.APPLICATION_CLOSED,
            AttemptStatus.CANCELLED_BEFORE_CLICK,
        )

    @property
    def click_happened_or_uncertain(self) -> bool:
        return self not in (
            AttemptStatus.ATTEMPT_CREATED,
            AttemptStatus.FAILED_BEFORE_CLICK,
            AttemptStatus.CANCELLED_BEFORE_CLICK,
        )


class ClickStatus(StrEnum):
    NOT_PERFORMED = "not_performed"
    PERFORMED = "performed"
    FAILED_BEFORE_DISPATCH = "failed_before_dispatch"
    DISPATCH_UNCERTAIN = "dispatch_uncertain"


class BrowserActionResult(BaseModel):
    """docs/10 Browser Action Result for the final click."""

    action: str = "click_submit"
    status: ClickStatus = ClickStatus.NOT_PERFORMED
    target_label: str = ""
    target_verified: bool = False
    started_at: datetime | None = None
    completed_at: datetime | None = None
    browser_exception: str | None = None


class EvidenceStrength(StrEnum):
    CONCLUSIVE = "conclusive"
    STRONG = "strong"
    SUPPORTING = "supporting"
    WEAK = "weak"
    CONTRADICTORY = "contradictory"


class Evidence(BaseModel):
    """docs/10 Evidence Model."""

    evidence_id: str = Field(default_factory=lambda: new_id("evidence"))
    source: str
    signal_type: str
    value: str = ""
    strength: EvidenceStrength
    captured_at: datetime = Field(default_factory=_now)


class ConfirmationNumber(BaseModel):
    """docs/10 Confirmation Number Result."""

    label: str
    value: str
    source: str = "confirmation_page"
    confidence: int = 0


class VerificationResult(BaseModel):
    """docs/10 Verification Result Model."""

    attempt_id: str = ""
    outcome: SubmissionOutcome
    confidence: int = 0
    evidence: list[Evidence] = Field(default_factory=list)
    confirmation_number: ConfirmationNumber | None = None
    confirmation_message: str = ""
    job_identity_verified: bool = False
    notes: str = ""
    verified_at: datetime = Field(default_factory=_now)


class PreSubmissionSnapshot(BaseModel):
    """docs/10 Pre-Submission Snapshot — written before the final click."""

    package_id: str
    workflow_id: str = ""
    queue_id: str = ""
    company: str = ""
    job_title: str = ""
    job_id: str = ""
    application_url: str = ""
    browser_url: str = ""
    ats_platform: str = ""
    active_resume: dict = Field(default_factory=dict)
    active_cover_letter: dict | None = None
    submit_control: dict = Field(default_factory=dict)
    screenshot_path: str = ""
    created_at: datetime = Field(default_factory=_now)


class SubmissionAttempt(BaseModel):
    """docs/10 Submission Attempt Model — durable before the click."""

    attempt_id: str
    package_id: str
    workflow_id: str = ""
    attempt_number: int = 1
    status: AttemptStatus = AttemptStatus.ATTEMPT_CREATED
    created_at: datetime = Field(default_factory=_now)
    click_initiated_at: datetime | None = None
    verification_completed_at: datetime | None = None
    page_url_before: str = ""
    page_url_after: str | None = None
    submit_control_label: str = ""
    screenshot_before: str = ""
    screenshot_after: str | None = None
    browser_action_result: BrowserActionResult | None = None
    verification_result: VerificationResult | None = None


class UnknownOutcome(BaseModel):
    """docs/10 Unknown Outcome Record — a protected state."""

    package_id: str
    attempt_id: str
    status: str = "submission_unknown"
    reason: str
    known_evidence: list[Evidence] = Field(default_factory=list)
    missing_evidence: list[str] = Field(default_factory=list)
    automatic_retry_allowed: bool = False
    required_actions: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=_now)


class UnknownResolution(BaseModel):
    """docs/10 Unknown Outcome Resolution Model."""

    package_id: str
    attempt_id: str
    previous_status: str = "submission_unknown"
    resolved_status: SubmissionOutcome
    resolution_source: str  # ats_dashboard | user_confirmation | ...
    notes: str = ""
    resolved_by: str = "user"
    resolved_at: datetime = Field(default_factory=_now)
