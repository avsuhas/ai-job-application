"""Browser automation domain models (docs/06).

These models are the boundary between the browser engine and the rest of the
application: business logic sees snapshots, plans, and results — never
Playwright objects.
"""

from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class PageState(StrEnum):
    READY = "ready"
    ERROR = "error"
    LOGIN_REQUIRED = "login_required"
    CAPTCHA_DETECTED = "captcha_detected"
    MFA_REQUIRED = "mfa_required"
    BLOCKED_NAVIGATION = "blocked_navigation"


class FieldType(StrEnum):
    TEXT = "text"
    TEXTAREA = "textarea"
    EMAIL = "email"
    PHONE = "phone"
    NUMBER = "number"
    URL = "url"
    PASSWORD = "password"
    DATE = "date"
    SELECT = "select"
    RADIO = "radio"
    CHECKBOX = "checkbox"
    FILE = "file"
    HIDDEN = "hidden"
    UNKNOWN = "unknown"


class FormField(BaseModel):
    """docs/06 Form Field Model (deterministic extraction subset)."""

    field_id: str
    label: str = ""
    field_type: FieldType = FieldType.UNKNOWN
    input_type: str = ""
    required: bool = False
    current_value: str = ""
    options: list[str] = Field(default_factory=list)
    placeholder: str = ""
    help_text: str = ""
    section: str = ""
    selector: str
    visible: bool = True
    enabled: bool = True
    read_only: bool = False


class FormAction(BaseModel):
    action_id: str
    type: str = "unknown"  # next | submit | back | unknown
    label: str = ""
    selector: str


class SafetySignals(BaseModel):
    captcha: bool = False
    login: bool = False
    mfa: bool = False


class PageSnapshot(BaseModel):
    """docs/06 Page Inspection Output."""

    url: str
    title: str = ""
    heading: str = ""
    state: PageState = PageState.READY
    fields: list[FormField] = Field(default_factory=list)
    actions: list[FormAction] = Field(default_factory=list)
    signals: SafetySignals = Field(default_factory=SafetySignals)
    validation_errors: list[str] = Field(default_factory=list)
    captured_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    def field(self, field_id: str) -> FormField | None:
        for field in self.fields:
            if field.field_id == field_id:
                return field
        return None


class BrowserAction(StrEnum):
    FILL = "fill"
    SELECT_OPTION = "select_option"
    SELECT_RADIO = "select_radio"
    SET_CHECKBOX = "set_checkbox"
    UPLOAD_FILE = "upload_file"


class InteractionStep(BaseModel):
    step_id: str
    field_id: str
    action: BrowserAction
    value: str


class InteractionPlan(BaseModel):
    page_id: str = ""
    steps: list[InteractionStep] = Field(default_factory=list)


class ActionStatus(StrEnum):
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"


class ActionResult(BaseModel):
    """Outcome of one verified browser action. Never contains the value
    itself — logs and results must not expose candidate data (docs/17)."""

    step_id: str
    field_id: str
    action: BrowserAction
    status: ActionStatus
    verified: bool = False
    message: str = ""


class ExecutionState(BaseModel):
    """Persisted progress for crash recovery (docs/06, docs/17 Phase 5)."""

    package_id: str = ""
    current_url: str = ""
    completed_step_ids: list[str] = Field(default_factory=list)
    last_saved: datetime = Field(default_factory=lambda: datetime.now(UTC))


class BrowserHealth(BaseModel):
    healthy: bool
    playwright_installed: bool = False
    chromium_installed: bool = False
    profile_dir_writable: bool = False
    screenshots_dir_writable: bool = False
    problems: list[str] = Field(default_factory=list)
