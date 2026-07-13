"""Lever ATS adapter (docs/09 Lever Adapter Considerations).

Status: beta — review mode only. Handles Lever's compact hosted application
forms: a single ``name`` field, email/phone, current company (``org``),
resume upload, profile links (``urls[...]``), employer custom cards (deferred
to generic classification), and confirmation pages.

Per the Phase 13 Expansion Rule this adapter carries its own detection,
mapping, and confirmation logic and passes its own independent test gate — it
does not inherit trust from the Greenhouse adapter.
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

_DOMAINS = ("lever.co",)

# Lever's stable form field names → canonical families. Lever uses a single
# full-name field and bracketed link fields.
_KNOWN_FIELD_IDS = {
    "name": "personal.full_name",
    "email": "personal.email",
    "phone": "personal.phone",
    "org": "employment.current_company",
    "resume": "documents.resume",
    "urls[LinkedIn]": "links.linkedin",
    "urls[GitHub]": "links.github",
    "urls[Portfolio]": "links.portfolio",
    "urls[Other]": "links.website",
}

# "AcmeCorp - Backend Engineer" (Lever posting/application page title).
_TITLE_PATTERN = re.compile(r"(?P<company>.+?)\s+[-–]\s+(?P<title>.+)")
# jobs.lever.co/{org}/{uuid}
_POSTING_URL = re.compile(r"lever\.co/(?P<org>[^/]+)/(?P<uuid>[0-9a-f-]{16,})", re.IGNORECASE)

_CONFIRMATION_MARKERS = (
    "thank you for applying",
    "application submitted",
    "your application has been submitted",
    "we've received your application",
    "we have received your application",
    "application received",
)

_CLOSED_MARKERS = ("no longer accepting applications", "position is closed", "job closed")

_SUBMIT_LABELS = ("submit application", "submit your application")
_SUBMIT_IDS = ("btn-submit", "submit-btn", "template-btn-submit")


def _host(url: str) -> str:
    return (urlparse(url).hostname or "").lower()


def _titleize(org: str) -> str:
    return re.sub(r"[-_]+", " ", org).strip().title()


class LeverAdapter(ATSAdapter):
    _metadata = AdapterMetadata(
        adapter_id="lever",
        display_name="Lever",
        adapter_version="1.0.0",
        status=AdapterStatus.BETA,
        supported_domains=["jobs.lever.co", "jobs.eu.lever.co"],
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

    # -- detection --------------------------------------------------------- #

    def detect(self, url: str, snapshot: PageSnapshot | None = None) -> ATSDetectionResult:
        methods: list[str] = []
        confidence = 0

        host = _host(url)
        if any(host == d or host.endswith("." + d) for d in _DOMAINS):
            methods.append("domain_pattern")
            confidence = 95

        if snapshot is not None:
            frames = " ".join(snapshot.frames).lower()
            if "lever.co" in frames:
                methods.append("embedded_iframe")
                confidence = max(confidence, 85)

            field_ids = {f.field_id for f in snapshot.fields}
            # Lever's signature: a single full-name field plus email + resume,
            # which the Greenhouse signature (first_name/last_name) never matches.
            has_lever_fields = "name" in field_ids and "email" in field_ids
            control = self.identify_submission_control(snapshot)
            if has_lever_fields and (
                "resume" in field_ids or any("urls[" in f for f in field_ids)
            ):
                methods.append("page_signature")
                confidence = max(confidence, 90)
            elif has_lever_fields and control is not None:
                methods.append("field_id_signature")
                confidence = max(confidence, 65)

        return ATSDetectionResult(
            detected_ats="lever" if confidence else "",
            confidence=confidence,
            detection_methods=methods,
            matched_adapter="lever" if confidence else None,
            generic_fallback_allowed=True,
        )

    # -- page classification ----------------------------------------------- #

    def classify_page(self, snapshot: PageSnapshot) -> PageClassification:
        text = f"{snapshot.heading} {snapshot.title}".lower()
        if any(marker in text for marker in _CONFIRMATION_MARKERS):
            return PageClassification(page_type=PageType.CONFIRMATION, confidence=95)
        if any(marker in text for marker in _CLOSED_MARKERS):
            return PageClassification(page_type=PageType.APPLICATION_CLOSED, confidence=90)
        if snapshot.signals.captcha:
            return PageClassification(page_type=PageType.CAPTCHA, confidence=95)
        if snapshot.signals.login:
            return PageClassification(page_type=PageType.LOGIN, confidence=90)
        if is_review_page(snapshot):
            return PageClassification(page_type=PageType.REVIEW, confidence=85)

        field_ids = {f.field_id for f in snapshot.fields if f.visible}
        if {"name", "email"} <= field_ids:
            return PageClassification(
                page_type=PageType.APPLICATION_FORM,
                confidence=90,
                step_label=snapshot.heading,
            )
        if "apply" in text and not field_ids:
            return PageClassification(page_type=PageType.JOB_DETAIL, confidence=70)
        return PageClassification(page_type=PageType.UNKNOWN, confidence=30)

    # -- job identity ------------------------------------------------------- #

    def extract_job_identity(self, snapshot: PageSnapshot) -> JobIdentity:
        url_match = _POSTING_URL.search(snapshot.url)
        job_id = url_match.group("uuid") if url_match else ""
        company_from_url = _titleize(url_match.group("org")) if url_match else ""

        title_match = _TITLE_PATTERN.search(snapshot.title)
        if title_match:
            return JobIdentity(
                company=company_from_url or title_match.group("company").strip(),
                title=title_match.group("title").strip(),
                job_id=job_id,
                confidence=90 if company_from_url else 80,
            )
        if snapshot.heading:
            return JobIdentity(
                company=company_from_url,
                title=snapshot.heading.strip(),
                job_id=job_id,
                confidence=55 if company_from_url else 40,
            )
        return JobIdentity(company=company_from_url, job_id=job_id,
                           confidence=30 if company_from_url else 0)

    # -- field semantics ---------------------------------------------------- #

    def classify_field(self, field: FormField) -> SemanticClassification | None:
        family = _KNOWN_FIELD_IDS.get(field.field_id)
        if family is None:
            return None  # employer custom cards defer to generic rules
        return SemanticClassification(
            field_id=field.field_id,
            semantic_type=family,
            confidence=98,
            method="ats_known_field_id",
        )

    # -- submission and confirmation ---------------------------------------- #

    def identify_submission_control(self, snapshot: PageSnapshot) -> FormAction | None:
        for action in snapshot.actions:
            if action.action_id in _SUBMIT_IDS or any(
                marker in action.label.lower() for marker in _SUBMIT_LABELS
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
            evidence=["No Lever confirmation markers found on the page."],
        )
