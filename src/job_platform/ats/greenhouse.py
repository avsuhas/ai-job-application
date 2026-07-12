"""Greenhouse ATS adapter (docs/09 Greenhouse Adapter Considerations).

Status: beta — review mode only; automatic submission remains unavailable.
Handles hosted job-board forms (single page with sections), the standard
Greenhouse field ids, resume/cover-letter uploads, employer custom questions
(deferred to generic classification), demographic sections, and confirmation
pages. Falls back to the Generic Form Engine for anything unrecognized.
"""

from __future__ import annotations

import re
from urllib.parse import urlparse

from job_platform.ats.base import (
    AdapterMetadata,
    AdapterStatus,
    ATSAdapter,
    ATSDetectionResult,
    CapabilityLevel,
    ConfirmationResult,
    JobIdentity,
    PageClassification,
    PageType,
)
from job_platform.browser.models import FormAction, FormField, PageSnapshot
from job_platform.forms.engine import is_review_page
from job_platform.forms.semantic import SemanticClassification

_DOMAINS = ("greenhouse.io",)

# Standard Greenhouse application field ids → canonical families. Exact id
# matches earn near-certain confidence (docs/09 exact known label mapping).
_KNOWN_FIELD_IDS = {
    "first_name": "personal.first_name",
    "last_name": "personal.last_name",
    "email": "personal.email",
    "phone": "personal.phone",
    "resume": "documents.resume",
    "cover_letter": "documents.cover_letter",
    "job_application_location": "personal.city",
    "candidate-location": "personal.city",
    "gender": "demographic.gender",
    "hispanic_ethnicity": "demographic.race_ethnicity",
    "race": "demographic.race_ethnicity",
    "veteran_status": "demographic.veteran_status",
    "disability_status": "demographic.disability_status",
}

_TITLE_PATTERN = re.compile(
    r"job application for (?P<title>.+?) at (?P<company>.+)", re.IGNORECASE
)

_CONFIRMATION_MARKERS = (
    "thank you for applying",
    "application has been submitted",
    "application submitted",
    "application has been received",
    "we have received your application",
)

_CLOSED_MARKERS = ("job is no longer open", "position has been filled", "job closed")

_SUBMIT_LABELS = ("submit application", "submit your application")


def _host(url: str) -> str:
    return (urlparse(url).hostname or "").lower()


class GreenhouseAdapter(ATSAdapter):
    _metadata = AdapterMetadata(
        adapter_id="greenhouse",
        display_name="Greenhouse",
        adapter_version="1.0.0",
        status=AdapterStatus.BETA,
        supported_domains=["boards.greenhouse.io", "job-boards.greenhouse.io"],
        capabilities={
            "form_completion": CapabilityLevel.SUPPORTED,
            "resume_upload": CapabilityLevel.SUPPORTED,
            "custom_questions": CapabilityLevel.PARTIAL,
            "review_extraction": CapabilityLevel.SUPPORTED,
            "submission": CapabilityLevel.SIMULATED_ONLY,
            "confirmation_verification": CapabilityLevel.SUPPORTED,
        },
    )

    @property
    def metadata(self) -> AdapterMetadata:
        return self._metadata

    # -- detection (docs/09 Detection Signals) --------------------------- #

    def detect(self, url: str, snapshot: PageSnapshot | None = None) -> ATSDetectionResult:
        methods: list[str] = []
        confidence = 0

        host = _host(url)
        if any(host == d or host.endswith("." + d) for d in _DOMAINS):
            methods.append("domain_pattern")
            confidence = 95

        if snapshot is not None:
            frames = " ".join(snapshot.frames).lower()
            if "greenhouse.io" in frames:
                methods.append("embedded_iframe")
                confidence = max(confidence, 85)

            field_ids = {f.field_id for f in snapshot.fields}
            known_hits = len(field_ids & {"first_name", "last_name", "email", "phone"})
            title = snapshot.title.lower()
            if known_hits >= 3 and _TITLE_PATTERN.search(title):
                methods.append("page_signature")
                confidence = max(confidence, 90)
            elif known_hits >= 3 and "application" in title:
                methods.append("field_id_signature")
                confidence = max(confidence, 65)

        return ATSDetectionResult(
            detected_ats="greenhouse" if confidence else "",
            confidence=confidence,
            detection_methods=methods,
            matched_adapter="greenhouse" if confidence else None,
            generic_fallback_allowed=True,
        )

    # -- page classification ---------------------------------------------- #

    def classify_page(self, snapshot: PageSnapshot) -> PageClassification:
        text = f"{snapshot.heading} {snapshot.title}".lower()
        if any(marker in text for marker in _CONFIRMATION_MARKERS):
            return PageClassification(page_type=PageType.CONFIRMATION, confidence=95)
        if any(marker in text for marker in _CLOSED_MARKERS):
            return PageClassification(
                page_type=PageType.APPLICATION_CLOSED, confidence=90
            )
        if snapshot.signals.captcha:
            return PageClassification(page_type=PageType.CAPTCHA, confidence=95)
        if snapshot.signals.login:
            return PageClassification(page_type=PageType.LOGIN, confidence=90)
        if is_review_page(snapshot):
            return PageClassification(page_type=PageType.REVIEW, confidence=85)

        field_ids = {f.field_id for f in snapshot.fields if f.visible}
        if {"first_name", "last_name", "email"} <= field_ids:
            return PageClassification(
                page_type=PageType.APPLICATION_FORM,
                confidence=90,
                step_label=snapshot.heading,
            )
        if "apply" in text and not field_ids:
            return PageClassification(page_type=PageType.JOB_DETAIL, confidence=70)
        return PageClassification(page_type=PageType.UNKNOWN, confidence=30)

    # -- job identity (docs/09 Application Identity Preservation) --------- #

    def extract_job_identity(self, snapshot: PageSnapshot) -> JobIdentity:
        match = _TITLE_PATTERN.search(snapshot.title)
        if match:
            job_id = ""
            url_match = re.search(r"/jobs/(\d+)", snapshot.url)
            if url_match:
                job_id = url_match.group(1)
            return JobIdentity(
                company=match.group("company").strip(),
                title=match.group("title").strip(),
                job_id=job_id,
                confidence=90,
            )
        if snapshot.heading:
            return JobIdentity(title=snapshot.heading.strip(), confidence=40)
        return JobIdentity()

    # -- field semantics ---------------------------------------------------- #

    def classify_field(self, field: FormField) -> SemanticClassification | None:
        family = _KNOWN_FIELD_IDS.get(field.field_id)
        if family is None:
            return None  # employer custom questions defer to generic rules
        return SemanticClassification(
            field_id=field.field_id,
            semantic_type=family,
            confidence=98,
            method="ats_known_field_id",
        )

    # -- submission and confirmation --------------------------------------- #

    def identify_submission_control(self, snapshot: PageSnapshot) -> FormAction | None:
        for action in snapshot.actions:
            lowered = action.label.lower()
            if action.action_id == "submit_app" or any(
                marker in lowered for marker in _SUBMIT_LABELS
            ):
                return action
        return next((a for a in snapshot.actions if a.type == "submit"), None)

    def verify_confirmation(self, snapshot: PageSnapshot) -> ConfirmationResult:
        text = f"{snapshot.heading} {snapshot.title}".lower()
        for marker in _CONFIRMATION_MARKERS:
            if marker in text:
                return ConfirmationResult(
                    confirmed=True,
                    method="confirmation_text",
                    evidence=[f"Page text contains {marker!r}", snapshot.url],
                )
        return ConfirmationResult(
            confirmed=False,
            method="confirmation_text",
            evidence=["No Greenhouse confirmation markers found on the page."],
        )


def default_registry():
    """Registry with all built-in adapters registered."""
    from job_platform.ats.registry import ATSAdapterRegistry

    registry = ATSAdapterRegistry()
    registry.register(GreenhouseAdapter())
    return registry
