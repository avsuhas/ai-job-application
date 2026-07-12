"""ATS adapter contract (docs/09).

A dedicated adapter contributes ATS-specific knowledge on top of the Generic
Form Engine: reliable detection, page classification, exact field semantics,
job-identity extraction, submission-control identification, and confirmation
verification. Adapters never bypass the engine's safety rules — submission
stays simulated until later phases.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from enum import StrEnum

from pydantic import BaseModel, Field

from job_platform.browser.models import FormAction, FormField, PageSnapshot
from job_platform.forms.semantic import SemanticClassification


class AdapterStatus(StrEnum):
    EXPERIMENTAL = "experimental"
    BETA = "beta"
    STABLE = "stable"
    DEGRADED = "degraded"
    DISABLED = "disabled"
    UNSUPPORTED = "unsupported"


class CapabilityLevel(StrEnum):
    SUPPORTED = "supported"
    PARTIAL = "partial"
    SIMULATED_ONLY = "simulated_only"
    UNSUPPORTED = "unsupported"


class AdapterMetadata(BaseModel):
    """docs/09 Adapter Metadata."""

    adapter_id: str
    display_name: str
    adapter_version: str = "1.0.0"
    schema_version: str = "1.0"
    enabled: bool = True
    status: AdapterStatus = AdapterStatus.EXPERIMENTAL
    supported_domains: list[str] = Field(default_factory=list)
    capabilities: dict[str, CapabilityLevel] = Field(default_factory=dict)
    generic_fallback_allowed: bool = True


class PageType(StrEnum):
    JOB_DETAIL = "job_detail"
    APPLICATION_FORM = "application_form"
    LOGIN = "login"
    REVIEW = "review"
    CONFIRMATION = "confirmation"
    APPLICATION_CLOSED = "application_closed"
    CAPTCHA = "captcha"
    ERROR = "error"
    UNKNOWN = "unknown"


class PageClassification(BaseModel):
    """docs/09 Page Classification Result."""

    page_type: PageType = PageType.UNKNOWN
    confidence: int = 0
    step_label: str = ""
    warnings: list[str] = Field(default_factory=list)


class JobIdentity(BaseModel):
    company: str = ""
    title: str = ""
    job_id: str = ""
    confidence: int = 0


class ATSDetectionResult(BaseModel):
    """docs/09 ATS Detection Result."""

    detected_ats: str = ""
    confidence: int = 0
    detection_methods: list[str] = Field(default_factory=list)
    matched_adapter: str | None = None
    generic_fallback_allowed: bool = True
    warnings: list[str] = Field(default_factory=list)


class ConfirmationResult(BaseModel):
    confirmed: bool = False
    method: str = ""
    evidence: list[str] = Field(default_factory=list)


class ATSAdapter(ABC):
    """Dedicated adapter interface (pragmatic subset of docs/09)."""

    @property
    @abstractmethod
    def metadata(self) -> AdapterMetadata: ...

    @abstractmethod
    def detect(self, url: str, snapshot: PageSnapshot | None = None) -> ATSDetectionResult:
        """Score how confident this adapter is that it owns the page."""

    @abstractmethod
    def classify_page(self, snapshot: PageSnapshot) -> PageClassification:
        """Normalize the page into a common page type."""

    @abstractmethod
    def extract_job_identity(self, snapshot: PageSnapshot) -> JobIdentity:
        """Extract company/title/job id so the wrong job is never filled."""

    def classify_field(self, field: FormField) -> SemanticClassification | None:
        """ATS-specific semantic mapping; None defers to generic rules."""
        return None

    @abstractmethod
    def identify_submission_control(self, snapshot: PageSnapshot) -> FormAction | None:
        """The final-submission control, which must never be auto-clicked."""

    @abstractmethod
    def verify_confirmation(self, snapshot: PageSnapshot) -> ConfirmationResult:
        """Verify a (simulated or user-performed) submission confirmation."""
