"""Queue and workflow orchestration models (docs/08)."""

from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum

from pydantic import BaseModel, Field

from job_platform.shared.ids import new_id


def _now() -> datetime:
    return datetime.now(UTC)


class QueueStatus(StrEnum):
    CREATED = "created"
    READY = "ready"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    COMPLETED_WITH_ERRORS = "completed_with_errors"
    CANCELLED = "cancelled"
    FAILED = "failed"


class QueueItemStatus(StrEnum):
    PENDING = "pending"
    ADMITTED = "admitted"
    REJECTED = "rejected"
    WAITING = "waiting"
    EXECUTING = "executing"
    WAITING_FOR_USER = "waiting_for_user"
    WAITING_FOR_REVIEW = "waiting_for_review"
    RETRY_SCHEDULED = "retry_scheduled"
    SUBMITTED = "submitted"
    SUBMISSION_UNKNOWN = "submission_unknown"
    ALREADY_APPLIED = "already_applied"
    SKIPPED = "skipped"
    CANCELLED = "cancelled"
    BLOCKED = "blocked"
    FAILED = "failed"
    COMPLETED = "completed"


class AdmissionStatus(StrEnum):
    ADMITTED = "admitted"
    REJECTED_NOT_READY = "rejected_not_ready"
    REJECTED_DUPLICATE = "rejected_duplicate"
    REJECTED_LOCKED = "rejected_locked"
    REJECTED_SUBMISSION_UNKNOWN = "rejected_submission_unknown"
    REJECTED_NO_URL = "rejected_no_url"
    MANUAL_COMPLETION_ONLY = "manual_completion_only"


class AdmissionResult(BaseModel):
    """docs/08 Queue Admission Result."""

    package_id: str
    status: AdmissionStatus
    reasons: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    admitted_at: datetime | None = None


class WorkflowStage(StrEnum):
    QUEUE_VALIDATION = "queue_validation"
    PACKAGE_LOCK = "package_lock"
    PRE_EXECUTION_READINESS = "pre_execution_readiness"
    USER_APPROVAL_CHECK = "user_approval_check"
    BROWSER_SESSION_START = "browser_session_start"
    APPLICATION_NAVIGATION = "application_navigation"
    APPLICATION_IDENTITY_CHECK = "application_identity_check"
    FORM_EXECUTION = "form_execution"
    FINAL_SUBMISSION = "final_submission"
    CLEANUP = "cleanup"


class StageStatus(StrEnum):
    SUCCESS = "success"
    SUCCESS_WITH_WARNINGS = "success_with_warnings"
    RETRYABLE_FAILURE = "retryable_failure"
    NON_RETRYABLE_FAILURE = "non_retryable_failure"
    WAITING_FOR_USER = "waiting_for_user"
    WAITING_FOR_REVIEW = "waiting_for_review"
    CANCELLED = "cancelled"
    SUBMISSION_UNKNOWN = "submission_unknown"


class StageResult(BaseModel):
    """docs/08 Stage Result Model."""

    stage: WorkflowStage
    status: StageStatus
    started_at: datetime = Field(default_factory=_now)
    completed_at: datetime | None = None
    retryable: bool = False
    warnings: list[str] = Field(default_factory=list)
    error: str | None = None
    checkpoint_written: bool = False


class WorkflowStatus(StrEnum):
    INITIALIZED = "initialized"
    RUNNING = "running"
    WAITING_FOR_USER = "waiting_for_user"
    WAITING_FOR_REVIEW = "waiting_for_review"
    RECOVERING = "recovering"
    SUBMITTED = "submitted"
    SUBMISSION_UNKNOWN = "submission_unknown"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    FAILED = "failed"
    CANCELLED = "cancelled"


class WorkflowState(BaseModel):
    """docs/08 Workflow State Model — persisted to execution/state.json."""

    workflow_id: str = Field(default_factory=lambda: new_id("workflow"))
    package_id: str
    queue_id: str = ""
    status: WorkflowStatus = WorkflowStatus.INITIALIZED
    current_stage: WorkflowStage | None = None
    last_completed_stage: WorkflowStage | None = None
    attempt_count: int = 1
    browser_profile: str = "default"
    ats_adapter: str | None = None
    engine_status: str = ""
    stage_results: list[StageResult] = Field(default_factory=list)
    started_at: datetime = Field(default_factory=_now)
    updated_at: datetime = Field(default_factory=_now)

    def record(self, result: StageResult) -> None:
        result.completed_at = _now()
        self.stage_results.append(result)
        self.current_stage = None
        if result.status in (StageStatus.SUCCESS, StageStatus.SUCCESS_WITH_WARNINGS):
            self.last_completed_stage = result.stage
        self.updated_at = _now()


class Checkpoint(BaseModel):
    """docs/08 Checkpoint — enough to resume safely."""

    checkpoint_id: str = Field(default_factory=lambda: new_id("checkpoint"))
    package_id: str = ""
    workflow_id: str = ""
    stage: str = ""
    page_number: int = 0
    page_url: str = ""
    completed_step_ids: list[str] = Field(default_factory=list)
    uploaded_files: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=_now)


class QueueItem(BaseModel):
    """docs/08 Queue Item Model."""

    package_id: str
    position: int = 0
    status: QueueItemStatus = QueueItemStatus.PENDING
    admission: AdmissionResult | None = None
    workflow_id: str | None = None
    engine_status: str = ""
    error: str | None = None
    match_score: int | None = None


class QueueModel(BaseModel):
    """docs/08 Queue Model — persisted per queue."""

    queue_id: str = Field(default_factory=lambda: new_id("queue"))
    status: QueueStatus = QueueStatus.CREATED
    ordering: str = "selected_order"
    items: list[QueueItem] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=_now)
    updated_at: datetime = Field(default_factory=_now)

    def item_for(self, package_id: str) -> QueueItem | None:
        for item in self.items:
            if item.package_id == package_id:
                return item
        return None

    @property
    def runnable_items(self) -> list[QueueItem]:
        return [
            i
            for i in self.items
            if i.status in (QueueItemStatus.ADMITTED, QueueItemStatus.WAITING,
                            QueueItemStatus.RETRY_SCHEDULED)
        ]


class QueueEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: new_id("event"))
    queue_id: str
    package_id: str | None = None
    event_type: str
    message: str = ""
    at: datetime = Field(default_factory=_now)
