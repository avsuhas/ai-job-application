"""Application Readiness domain models (docs/07D-2)."""

from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum

from pydantic import BaseModel, Field

from job_platform.shared.ids import new_id


class ReadinessStage(StrEnum):
    PREPARATION = "preparation"
    MANUAL_COMPLETION = "manual_completion"
    # browser_execution / submission stages arrive with the browser engine


class ReadinessStatus(StrEnum):
    READY = "ready"
    READY_WITH_WARNINGS = "ready_with_warnings"
    NOT_READY = "not_ready"
    USER_ACTION_REQUIRED = "user_action_required"
    REFRESH_REQUIRED = "refresh_required"
    BLOCKED = "blocked"
    ALREADY_APPLIED = "already_applied"
    FAILED = "failed"


class CheckStatus(StrEnum):
    PASSED = "passed"
    PASSED_WITH_WARNING = "passed_with_warning"
    FAILED = "failed"
    NOT_APPLICABLE = "not_applicable"
    USER_ACTION_REQUIRED = "user_action_required"
    STALE = "stale"


class ReadinessCheck(BaseModel):
    """docs/07D-2 Readiness Check Model."""

    check_id: str
    category: str
    status: CheckStatus
    required: bool = True
    message: str
    evidence: list[str] = Field(default_factory=list)
    recommended_action: str | None = None


class ReadinessReport(BaseModel):
    """docs/07D-2 Readiness Result Model."""

    readiness_id: str = Field(default_factory=lambda: new_id("readiness"))
    package_id: str
    stage: ReadinessStage
    status: ReadinessStatus = ReadinessStatus.NOT_READY
    evaluated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    checks: list[ReadinessCheck] = Field(default_factory=list)
    blocking_issues: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    required_user_actions: list[str] = Field(default_factory=list)
    refresh_reasons: list[str] = Field(default_factory=list)
    next_allowed_action: str = ""

    def add(self, check: ReadinessCheck) -> None:
        self.checks.append(check)
        if check.status == CheckStatus.FAILED and check.required:
            self.blocking_issues.append(check.message)
        elif check.status == CheckStatus.USER_ACTION_REQUIRED:
            self.required_user_actions.append(check.message)
        elif check.status == CheckStatus.STALE:
            self.refresh_reasons.append(check.message)
        elif check.status in (CheckStatus.PASSED_WITH_WARNING,) or (
            check.status == CheckStatus.FAILED and not check.required
        ):
            self.warnings.append(check.message)
