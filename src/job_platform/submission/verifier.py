"""Submission verification (docs/10).

Collects graded evidence from the post-click page and classifies the outcome.
The bar is deliberately conservative: only conclusive/strong evidence with
verified job identity yields Submitted; contradictory evidence yields Failed;
anything weaker becomes the protected Submission Unknown state.
"""

from __future__ import annotations

import re

from job_platform.ats.base import ATSAdapter
from job_platform.browser.models import PageSnapshot
from job_platform.packages.models import PackageJobSummary
from job_platform.submission.models import (
    ConfirmationNumber,
    Evidence,
    EvidenceStrength,
    SubmissionOutcome,
    VerificationResult,
)

_SUCCESS_MARKERS = (
    "application submitted",
    "application has been submitted",
    "thank you for applying",
    "application has been received",
    "we have received your application",
    "successfully submitted",
)

_ALREADY_APPLIED_MARKERS = (
    "already applied",
    "already submitted an application",
    "previously applied",
)

_CLOSED_MARKERS = (
    "no longer open",
    "job closed",
    "position has been filled",
    "no longer accepting applications",
)

_FAILURE_MARKERS = (
    "something went wrong",
    "could not be submitted",
    "submission failed",
    "error processing your application",
)

_CONFIRMATION_URL_HINTS = ("confirmation", "thank", "success", "submitted")

_CONFIRMATION_NUMBER = re.compile(
    r"(confirmation number|application number|candidate application id|"
    r"submission id|reference number|application reference)\s*[:#]?\s*"
    r"([A-Z0-9][A-Z0-9\-_/]{3,})",
    re.IGNORECASE,
)


def extract_confirmation_number(text: str) -> ConfirmationNumber | None:
    match = _CONFIRMATION_NUMBER.search(text)
    if not match:
        return None
    return ConfirmationNumber(
        label=match.group(1).strip().title(),
        value=match.group(2).strip(),
        confidence=95,
    )


class SubmissionVerifier:
    def __init__(self, adapter: ATSAdapter | None = None) -> None:
        self._adapter = adapter

    def _job_identity_verified(
        self, snapshot: PageSnapshot, job: PackageJobSummary
    ) -> bool:
        """A generic success message is not enough (docs/10): the page must
        reference the intended company, title, or job id."""
        haystack = " ".join(
            [snapshot.heading, snapshot.title, snapshot.text_excerpt]
        ).lower()
        checks = []
        if job.company:
            checks.append(job.company.lower() in haystack)
        if job.title:
            checks.append(job.title.lower() in haystack)
        if job.job_id:
            checks.append(job.job_id.lower() in haystack)
        return any(checks) if checks else False

    def collect_evidence(
        self,
        before: PageSnapshot,
        after: PageSnapshot,
        job: PackageJobSummary,
    ) -> list[Evidence]:
        evidence: list[Evidence] = []
        text = " ".join([after.heading, after.title, after.text_excerpt]).lower()
        identity_ok = self._job_identity_verified(after, job)

        # Contradictory signals first — they are decisive (docs/10).
        for marker in _FAILURE_MARKERS:
            if marker in text:
                evidence.append(
                    Evidence(
                        source="page_content",
                        signal_type="explicit_failure_message",
                        value=marker,
                        strength=EvidenceStrength.CONTRADICTORY,
                    )
                )
        if after.validation_errors:
            evidence.append(
                Evidence(
                    source="page_content",
                    signal_type="validation_errors_present",
                    value="; ".join(after.validation_errors[:3]),
                    strength=EvidenceStrength.CONTRADICTORY,
                )
            )
        for marker in _ALREADY_APPLIED_MARKERS:
            if marker in text:
                evidence.append(
                    Evidence(
                        source="page_content",
                        signal_type="already_applied_message",
                        value=marker,
                        strength=EvidenceStrength.CONTRADICTORY,
                    )
                )
        for marker in _CLOSED_MARKERS:
            if marker in text:
                evidence.append(
                    Evidence(
                        source="page_content",
                        signal_type="application_closed_message",
                        value=marker,
                        strength=EvidenceStrength.CONTRADICTORY,
                    )
                )

        # Success signals.
        confirmation = extract_confirmation_number(after.text_excerpt)
        if confirmation is not None:
            evidence.append(
                Evidence(
                    source="confirmation_page",
                    signal_type="confirmation_number",
                    value=f"{confirmation.label}: {confirmation.value}",
                    strength=EvidenceStrength.CONCLUSIVE
                    if identity_ok
                    else EvidenceStrength.SUPPORTING,
                )
            )
        for marker in _SUCCESS_MARKERS:
            if marker in text:
                evidence.append(
                    Evidence(
                        source="confirmation_page",
                        signal_type="explicit_success_message",
                        value=marker,
                        strength=EvidenceStrength.STRONG
                        if identity_ok
                        else EvidenceStrength.WEAK,
                    )
                )
                break
        if self._adapter is not None:
            adapter_result = self._adapter.verify_confirmation(after)
            if adapter_result.confirmed:
                evidence.append(
                    Evidence(
                        source="ats_adapter",
                        signal_type="adapter_confirmation",
                        value="; ".join(adapter_result.evidence[:2]),
                        strength=EvidenceStrength.STRONG
                        if identity_ok
                        else EvidenceStrength.WEAK,
                    )
                )

        # URL and structural signals — never sufficient alone (docs/10).
        after_path = after.url.lower()
        if any(hint in after_path for hint in _CONFIRMATION_URL_HINTS):
            evidence.append(
                Evidence(
                    source="url",
                    signal_type="confirmation_url_pattern",
                    value=after.url,
                    strength=EvidenceStrength.SUPPORTING,
                )
            )
        elif after.url != before.url:
            evidence.append(
                Evidence(
                    source="url",
                    signal_type="url_changed",
                    value=after.url,
                    strength=EvidenceStrength.WEAK,
                )
            )
        before_fields = sum(1 for f in before.fields if f.visible)
        after_fields = sum(1 for f in after.fields if f.visible)
        if before_fields >= 3 and after_fields == 0:
            evidence.append(
                Evidence(
                    source="page_structure",
                    signal_type="application_form_disappeared",
                    value=f"{before_fields} fields -> 0",
                    strength=EvidenceStrength.SUPPORTING,
                )
            )
        return evidence

    def classify(
        self,
        attempt_id: str,
        before: PageSnapshot,
        after: PageSnapshot,
        job: PackageJobSummary,
    ) -> VerificationResult:
        evidence = self.collect_evidence(before, after, job)
        identity_ok = self._job_identity_verified(after, job)
        by_type = {e.signal_type for e in evidence}

        def result(outcome: SubmissionOutcome, confidence: int, notes: str) -> VerificationResult:
            confirmation = extract_confirmation_number(after.text_excerpt)
            message = after.heading or after.title
            return VerificationResult(
                attempt_id=attempt_id,
                outcome=outcome,
                confidence=confidence,
                evidence=evidence,
                confirmation_number=confirmation
                if outcome == SubmissionOutcome.SUBMITTED
                else None,
                confirmation_message=message
                if outcome == SubmissionOutcome.SUBMITTED
                else "",
                job_identity_verified=identity_ok,
                notes=notes,
            )

        if "already_applied_message" in by_type:
            return result(
                SubmissionOutcome.ALREADY_APPLIED, 90,
                "The page reports an existing application.",
            )
        if "application_closed_message" in by_type:
            return result(
                SubmissionOutcome.APPLICATION_CLOSED, 90, "The job is closed."
            )
        if "explicit_failure_message" in by_type or "validation_errors_present" in by_type:
            return result(
                SubmissionOutcome.FAILED, 85,
                "The page shows an explicit failure or unresolved validation errors.",
            )

        strengths = {e.strength for e in evidence}
        if EvidenceStrength.CONCLUSIVE in strengths:
            return result(
                SubmissionOutcome.SUBMITTED, 98,
                "Conclusive evidence: confirmation number with verified job identity.",
            )
        if EvidenceStrength.STRONG in strengths:
            return result(
                SubmissionOutcome.SUBMITTED, 92,
                "Strong evidence: explicit confirmation with verified job identity.",
            )
        # Supporting/weak evidence only → protected unknown (docs/10).
        return result(
            SubmissionOutcome.SUBMISSION_UNKNOWN, 40,
            "Evidence is insufficient to prove or disprove submission; "
            "automatic retry is not allowed.",
        )
