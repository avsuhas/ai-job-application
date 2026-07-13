"""Submission service — the irreversible-action boundary (docs/10).

Order of operations is the safety mechanism:

1. Refuse when a prior attempt is unresolved (click happened or unknown).
2. Duplicate check immediately before submission.
3. Explicit user approval required (review mode is the default).
4. Pre-submission snapshot and screenshot written durably.
5. Submission lock acquired (never removed just because a process died —
   it is reconciled against attempt records).
6. Attempt record persisted BEFORE the click.
7. The final click happens at most once; a click failure is never retried.
8. Verification grades evidence; weak evidence becomes Submission Unknown.
9. History sync is idempotent and can never trigger a resubmission.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime

from job_platform.ats.base import ATSAdapter
from job_platform.browser.models import FormAction, PageSnapshot
from job_platform.browser.service import BrowserSession
from job_platform.packages.models import PackageManifest, PackageStatus
from job_platform.packages.store import PackageStore
from job_platform.shared.errors import JobPlatformError, StorageError
from job_platform.shared.files import atomic_write_text
from job_platform.shared.ids import sha256_text
from job_platform.shared.logging import get_logger
from job_platform.storage.tracker import ApplicationRecord, ApplicationTracker
from job_platform.submission.history import ApplicationHistoryService
from job_platform.submission.models import (
    AttemptStatus,
    BrowserActionResult,
    ClickStatus,
    PreSubmissionSnapshot,
    SubmissionAttempt,
    SubmissionOutcome,
    UnknownOutcome,
    UnknownResolution,
    VerificationResult,
)
from job_platform.submission.verifier import SubmissionVerifier

logger = get_logger("submission.service")

ATTEMPTS_DIR = "submission/attempts"
SNAPSHOT_PATH = "submission/pre_submission_snapshot.json"
LOCK_PATH = "submission/.submission.lock"
UNKNOWN_PATH = "submission/unknown_outcome.json"
RESOLUTION_PATH = "submission/unknown_resolution.json"
RESULT_PATH = "submission/result.json"


class SubmissionBlockedError(JobPlatformError):
    code = "submission_blocked"


class SubmissionService:
    def __init__(
        self,
        store: PackageStore,
        tracker: ApplicationTracker,
        history: ApplicationHistoryService,
    ) -> None:
        self._store = store
        self._tracker = tracker
        self._history = history

    # -- attempt persistence -------------------------------------------------- #

    def _attempts_dir(self, package_id: str):
        return self._store.package_dir(package_id) / ATTEMPTS_DIR

    def load_attempts(self, package_id: str) -> list[SubmissionAttempt]:
        directory = self._attempts_dir(package_id)
        if not directory.exists():
            return []
        attempts = []
        for path in sorted(directory.glob("submission_attempt_*.json")):
            attempts.append(SubmissionAttempt.model_validate_json(path.read_text()))
        return attempts

    def _persist_attempt(self, attempt: SubmissionAttempt) -> None:
        path = self._attempts_dir(attempt.package_id) / f"{attempt.attempt_id}.json"
        atomic_write_text(path, attempt.model_dump_json(indent=2))

    def load_unknown_outcome(self, package_id: str) -> UnknownOutcome | None:
        path = self._store.package_dir(package_id) / UNKNOWN_PATH
        if not path.exists():
            return None
        return UnknownOutcome.model_validate_json(path.read_text(encoding="utf-8"))

    # -- lock (docs/10 Submission Lock Rules) ---------------------------------- #

    def _acquire_submission_lock(self, package_id: str, attempt_id: str) -> None:
        lock_path = self._store.package_dir(package_id) / LOCK_PATH
        if lock_path.exists():
            # Reconcile with attempt records — never reclaim while any attempt
            # is unresolved (docs/10: a lock is not removed merely because the
            # browser process ended).
            attempts = self.load_attempts(package_id)
            unresolved = [
                a for a in attempts
                if not a.status.terminal and a.status != AttemptStatus.SUBMISSION_UNKNOWN
            ]
            unknown = [a for a in attempts if a.status == AttemptStatus.SUBMISSION_UNKNOWN]
            if unresolved or unknown:
                raise SubmissionBlockedError(
                    "A submission lock exists with unresolved attempts; refusing "
                    "to submit again.",
                    details={"package_id": package_id},
                )
            logger.warning("Reclaiming submission lock after terminal attempts.")
        atomic_write_text(
            lock_path,
            json.dumps(
                {
                    "lock_type": "final_submission",
                    "package_id": package_id,
                    "attempt_id": attempt_id,
                    "acquired_at": datetime.now(UTC).isoformat(),
                }
            ),
        )

    def _release_submission_lock(self, package_id: str) -> None:
        (self._store.package_dir(package_id) / LOCK_PATH).unlink(missing_ok=True)

    # -- guards ------------------------------------------------------------------ #

    def _guard_new_attempt(self, manifest: PackageManifest, approved: bool) -> None:
        if not approved:
            raise SubmissionBlockedError(
                "Final submission requires explicit user approval.",
                details={"package_id": manifest.package_id},
            )
        if self.load_unknown_outcome(manifest.package_id) is not None:
            raise SubmissionBlockedError(
                "A prior attempt ended in Submission Unknown; resolve it before "
                "attempting again.",
                details={"package_id": manifest.package_id},
            )
        for attempt in self.load_attempts(manifest.package_id):
            if attempt.status == AttemptStatus.SUBMITTED:
                raise SubmissionBlockedError(
                    "This package was already submitted.",
                    details={"attempt_id": attempt.attempt_id},
                )
            if attempt.status.click_happened_or_uncertain and not attempt.status.terminal:
                raise SubmissionBlockedError(
                    "A prior attempt clicked submit without a resolved outcome; "
                    "refusing to click again.",
                    details={"attempt_id": attempt.attempt_id},
                )
        # Duplicate check immediately before submission (docs/17 Phase 9).
        job_summary = manifest.job
        from job_platform.jobs.models import Job

        probe = Job(
            id="submission_check",
            company=job_summary.company,
            title=job_summary.title,
            job_id=job_summary.job_id,
            url=job_summary.application_url,
        )
        if self._tracker.is_duplicate(probe):
            raise SubmissionBlockedError(
                "The tracker already records an application for this job.",
                details={"package_id": manifest.package_id},
            )

    # -- the boundary ------------------------------------------------------------ #

    async def submit(
        self,
        session: BrowserSession,
        manifest: PackageManifest,
        snapshot: PageSnapshot,
        adapter: ATSAdapter | None = None,
        approved: bool = False,
        workflow_id: str = "",
    ) -> SubmissionAttempt:
        package_id = manifest.package_id
        self._guard_new_attempt(manifest, approved)

        # Identify the final control unambiguously.
        control: FormAction | None = None
        if adapter is not None:
            control = adapter.identify_submission_control(snapshot)
        if control is None:
            submits = [a for a in snapshot.actions if a.type == "submit"]
            control = submits[0] if len(submits) == 1 else None
        if control is None or not control.selector:
            raise SubmissionBlockedError(
                "No unambiguous final submission control was found; manual "
                "submission is required.",
                details={"package_id": package_id},
            )

        attempt_number = len(self.load_attempts(package_id)) + 1
        attempt = SubmissionAttempt(
            attempt_id=f"submission_attempt_{attempt_number:03d}",
            package_id=package_id,
            workflow_id=workflow_id,
            attempt_number=attempt_number,
            page_url_before=snapshot.url,
            submit_control_label=control.label,
        )

        screenshot_before = await session.capture_screenshot("pre_submission")
        attempt.screenshot_before = str(screenshot_before)
        pre_snapshot = PreSubmissionSnapshot(
            package_id=package_id,
            workflow_id=workflow_id,
            company=manifest.job.company,
            job_title=manifest.job.title,
            job_id=manifest.job.job_id,
            application_url=manifest.job.application_url,
            browser_url=snapshot.url,
            ats_platform=manifest.expected_ats,
            active_resume={"reference": manifest.selected_resume or ""},
            active_cover_letter=(
                {"reference": manifest.cover_letter} if manifest.cover_letter else None
            ),
            submit_control={"label": control.label, "selector": control.selector},
            screenshot_path=str(screenshot_before),
        )
        atomic_write_text(
            self._store.package_dir(package_id) / SNAPSHOT_PATH,
            pre_snapshot.model_dump_json(indent=2),
        )

        self._acquire_submission_lock(package_id, attempt.attempt_id)
        # Durable attempt BEFORE the click (docs/10 Submit Action Boundary).
        self._persist_attempt(attempt)
        self._history.record_event(
            "submission_attempt_created",
            package_id=package_id,
            message=f"attempt {attempt.attempt_number} for {manifest.job.title}",
        )

        action_result = BrowserActionResult(
            target_label=control.label,
            target_verified=True,
            started_at=datetime.now(UTC),
        )
        attempt.status = AttemptStatus.CLICK_INITIATED
        attempt.click_initiated_at = action_result.started_at
        self._persist_attempt(attempt)
        try:
            locator = session.page.locator(control.selector).first
            await locator.click()
            action_result.status = ClickStatus.PERFORMED
        except Exception as exc:  # noqa: BLE001 - never retry the final click
            action_result.status = ClickStatus.DISPATCH_UNCERTAIN
            action_result.browser_exception = str(exc)
            logger.warning("Final click dispatch uncertain: %s", exc)
        action_result.completed_at = datetime.now(UTC)
        attempt.browser_action_result = action_result
        self._persist_attempt(attempt)

        return await self._verify_and_finalize(session, manifest, attempt, snapshot, adapter)

    async def _verify_and_finalize(
        self,
        session: BrowserSession,
        manifest: PackageManifest,
        attempt: SubmissionAttempt,
        before: PageSnapshot,
        adapter: ATSAdapter | None,
    ) -> SubmissionAttempt:
        attempt.status = AttemptStatus.VERIFICATION_PENDING
        self._persist_attempt(attempt)
        try:
            await session._wait_for_stability()
            after = await session.inspect_page()
            screenshot_after = await session.capture_screenshot("post_submission")
            attempt.screenshot_after = str(screenshot_after)
            attempt.page_url_after = after.url
        except Exception as exc:  # noqa: BLE001 - crash after click → unknown
            logger.warning("Post-click inspection failed: %s", exc)
            return self._finalize_unknown(
                manifest, attempt,
                reason=f"The page could not be inspected after the click: {exc}",
                missing=["confirmation_page"],
            )

        verifier = SubmissionVerifier(adapter)
        verification = verifier.classify(
            attempt.attempt_id, before, after, manifest.job
        )
        attempt.verification_result = verification
        attempt.verification_completed_at = datetime.now(UTC)

        if verification.outcome == SubmissionOutcome.SUBMITTED:
            attempt.status = AttemptStatus.SUBMITTED
            self._persist_attempt(attempt)
            self._finalize_submitted(manifest, attempt, verification)
        elif verification.outcome == SubmissionOutcome.ALREADY_APPLIED:
            attempt.status = AttemptStatus.ALREADY_APPLIED
            self._persist_attempt(attempt)
            self._release_submission_lock(manifest.package_id)
        elif verification.outcome == SubmissionOutcome.APPLICATION_CLOSED:
            attempt.status = AttemptStatus.APPLICATION_CLOSED
            self._persist_attempt(attempt)
            self._release_submission_lock(manifest.package_id)
        elif verification.outcome == SubmissionOutcome.FAILED:
            attempt.status = AttemptStatus.FAILED_AFTER_CLICK
            self._persist_attempt(attempt)
            self._history.record_event(
                "submission_failed",
                package_id=manifest.package_id,
                message=verification.notes,
            )
            self._release_submission_lock(manifest.package_id)
        else:
            return self._finalize_unknown(
                manifest, attempt,
                reason=verification.notes,
                missing=["conclusive_confirmation"],
                evidence=verification,
            )
        return attempt

    def _finalize_submitted(
        self,
        manifest: PackageManifest,
        attempt: SubmissionAttempt,
        verification: VerificationResult,
    ) -> None:
        package_id = manifest.package_id
        result = {
            "method": "browser",
            "attempt_id": attempt.attempt_id,
            "submitted_at": datetime.now(UTC).isoformat(),
            "confirmation_number": (
                verification.confirmation_number.model_dump()
                if verification.confirmation_number
                else None
            ),
            "confirmation_message": verification.confirmation_message,
            "confidence": verification.confidence,
        }
        atomic_write_text(
            self._store.package_dir(package_id) / RESULT_PATH,
            json.dumps(result, indent=2),
        )
        manifest.status = PackageStatus.SUBMITTED
        self._store.save_manifest(manifest)
        self._history.record_event(
            "submitted",
            package_id=package_id,
            message=verification.confirmation_message,
            data={"confidence": verification.confidence},
        )
        # History sync is idempotent; a failure here must never resubmit
        # (docs/10) — the attempt record already holds the truth.
        try:
            self._history.sync_submission(
                ApplicationRecord(
                    company=manifest.job.company,
                    job_title=manifest.job.title,
                    job_id=manifest.job.job_id,
                    application_url=manifest.job.application_url,
                    resume_used=manifest.selected_resume or "",
                    status="submitted",
                    notes=f"browser submission via {attempt.attempt_id}"
                    + (
                        f" — {verification.confirmation_number.label} "
                        f"{verification.confirmation_number.value}"
                        if verification.confirmation_number
                        else ""
                    ),
                ),
                package_id=package_id,
            )
        except Exception:  # noqa: BLE001
            logger.exception(
                "History sync failed for %s; the submission itself is recorded "
                "in the attempt and can be re-synced.",
                package_id,
            )
        self._release_submission_lock(package_id)

    def _finalize_unknown(
        self,
        manifest: PackageManifest,
        attempt: SubmissionAttempt,
        reason: str,
        missing: list[str],
        evidence: VerificationResult | None = None,
    ) -> SubmissionAttempt:
        attempt.status = AttemptStatus.SUBMISSION_UNKNOWN
        self._persist_attempt(attempt)
        unknown = UnknownOutcome(
            package_id=manifest.package_id,
            attempt_id=attempt.attempt_id,
            reason=reason,
            known_evidence=evidence.evidence if evidence else [],
            missing_evidence=missing,
            required_actions=[
                "Open the ATS or your email and verify whether the application "
                "was received, then resolve this outcome."
            ],
        )
        atomic_write_text(
            self._store.package_dir(manifest.package_id) / UNKNOWN_PATH,
            unknown.model_dump_json(indent=2),
        )
        self._history.record_event(
            "submission_unknown",
            package_id=manifest.package_id,
            message=reason,
        )
        # The submission lock intentionally stays in place (docs/10).
        logger.warning(
            "Submission Unknown for %s: %s", manifest.package_id, reason
        )
        return attempt

    # -- unknown resolution (docs/10) --------------------------------------------- #

    def resolve_unknown(
        self,
        manifest: PackageManifest,
        resolved_status: SubmissionOutcome,
        resolution_source: str,
        notes: str = "",
    ) -> UnknownResolution:
        unknown = self.load_unknown_outcome(manifest.package_id)
        if unknown is None:
            raise StorageError(
                "This package has no unresolved submission outcome.",
                details={"package_id": manifest.package_id},
            )
        if resolved_status not in (
            SubmissionOutcome.SUBMITTED,
            SubmissionOutcome.FAILED,
            SubmissionOutcome.ALREADY_APPLIED,
            SubmissionOutcome.APPLICATION_CLOSED,
        ):
            raise StorageError(
                f"'{resolved_status.value}' is not a valid resolution.",
                details={"package_id": manifest.package_id},
            )

        attempts = {a.attempt_id: a for a in self.load_attempts(manifest.package_id)}
        attempt = attempts.get(unknown.attempt_id)
        resolution = UnknownResolution(
            package_id=manifest.package_id,
            attempt_id=unknown.attempt_id,
            resolved_status=resolved_status,
            resolution_source=resolution_source,
            notes=notes,
        )
        atomic_write_text(
            self._store.package_dir(manifest.package_id) / RESOLUTION_PATH,
            resolution.model_dump_json(indent=2),
        )
        if attempt is not None:
            attempt.status = {
                SubmissionOutcome.SUBMITTED: AttemptStatus.SUBMITTED,
                SubmissionOutcome.FAILED: AttemptStatus.FAILED_AFTER_CLICK,
                SubmissionOutcome.ALREADY_APPLIED: AttemptStatus.ALREADY_APPLIED,
                SubmissionOutcome.APPLICATION_CLOSED: AttemptStatus.APPLICATION_CLOSED,
            }[resolved_status]
            self._persist_attempt(attempt)
        (self._store.package_dir(manifest.package_id) / UNKNOWN_PATH).unlink(missing_ok=True)
        self._release_submission_lock(manifest.package_id)

        self._history.record_event(
            "unknown_resolved",
            package_id=manifest.package_id,
            message=f"resolved to {resolved_status.value} via {resolution_source}",
        )
        if resolved_status == SubmissionOutcome.SUBMITTED:
            manifest.status = PackageStatus.SUBMITTED
            self._store.save_manifest(manifest)
            self._history.sync_submission(
                ApplicationRecord(
                    company=manifest.job.company,
                    job_title=manifest.job.title,
                    job_id=manifest.job.job_id,
                    application_url=manifest.job.application_url,
                    resume_used=manifest.selected_resume or "",
                    status="submitted",
                    notes=f"resolved from submission_unknown via {resolution_source}",
                ),
                package_id=manifest.package_id,
            )
        return resolution


def submission_status(store: PackageStore, service: SubmissionService, package_id: str) -> dict:
    attempts = service.load_attempts(package_id)
    unknown = service.load_unknown_outcome(package_id)
    snapshot_hash = None
    snapshot_path = store.package_dir(package_id) / SNAPSHOT_PATH
    if snapshot_path.exists():
        snapshot_hash = sha256_text(snapshot_path.read_text(encoding="utf-8"))[:12]
    return {
        "package_id": package_id,
        "attempts": [a.model_dump(mode="json") for a in attempts],
        "unknown_outcome": unknown.model_dump(mode="json") if unknown else None,
        "pre_submission_snapshot_hash": snapshot_hash,
        "lock_present": (store.package_dir(package_id) / LOCK_PATH).exists(),
    }
