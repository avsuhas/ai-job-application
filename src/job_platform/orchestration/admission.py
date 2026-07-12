"""Queue admission (docs/08).

A package enters the executable queue only when it is genuinely safe to run:
prepared, reviewed, ready, unlocked, not a duplicate, with a usable URL and
no unresolved prior execution. Everything else is rejected with a reason.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime

from job_platform.candidate.models import CandidateBundle
from job_platform.orchestration.locks import LockManager
from job_platform.orchestration.models import AdmissionResult, AdmissionStatus
from job_platform.packages.models import PackageStatus
from job_platform.packages.store import PackageStore
from job_platform.readiness.models import ReadinessStage, ReadinessStatus
from job_platform.readiness.service import ReadinessService
from job_platform.shared.errors import StorageError
from job_platform.shared.logging import get_logger

logger = get_logger("orchestration.admission")


class QueueAdmissionController:
    def __init__(
        self,
        store: PackageStore,
        readiness: ReadinessService,
        locks: LockManager,
        allow_ready_with_warnings: bool = True,
    ) -> None:
        self._store = store
        self._readiness = readiness
        self._locks = locks
        self._allow_warnings = allow_ready_with_warnings

    def _prior_submission_unknown(self, package_id: str) -> bool:
        try:
            raw = self._store.read_artifact(package_id, "execution/state.json")
        except StorageError:
            return False
        try:
            state = json.loads(raw)
        except json.JSONDecodeError:
            return True  # unreadable prior state is treated as unresolved
        return state.get("status") == "submission_unknown"

    def evaluate(self, package_id: str, bundle: CandidateBundle) -> AdmissionResult:
        def rejected(status: AdmissionStatus, reason: str) -> AdmissionResult:
            logger.info("Package %s not admitted: %s", package_id, reason)
            return AdmissionResult(package_id=package_id, status=status, reasons=[reason])

        try:
            manifest = self._store.load_manifest(package_id)
        except StorageError as exc:
            return rejected(AdmissionStatus.REJECTED_NOT_READY, exc.message)

        if manifest.status == PackageStatus.ALREADY_APPLIED:
            return rejected(
                AdmissionStatus.REJECTED_DUPLICATE,
                "This job is already recorded in the application tracker.",
            )
        if manifest.status != PackageStatus.READY:
            return rejected(
                AdmissionStatus.REJECTED_NOT_READY,
                f"Package status is '{manifest.status.value}', not 'ready'.",
            )
        if not manifest.job.application_url:
            return rejected(
                AdmissionStatus.REJECTED_NO_URL,
                "The package has no application URL for browser execution.",
            )
        if self._locks.is_package_locked(package_id):
            return rejected(
                AdmissionStatus.REJECTED_LOCKED,
                "The package is locked by another execution.",
            )
        if self._prior_submission_unknown(package_id):
            return rejected(
                AdmissionStatus.REJECTED_SUBMISSION_UNKNOWN,
                "A prior execution ended in an unknown submission state; "
                "resolve it before re-queuing.",
            )

        report = self._readiness.evaluate(manifest, bundle, ReadinessStage.MANUAL_COMPLETION)
        if report.status == ReadinessStatus.ALREADY_APPLIED:
            return rejected(
                AdmissionStatus.REJECTED_DUPLICATE,
                "The duplicate check matched an existing application.",
            )
        if report.status == ReadinessStatus.READY:
            pass
        elif report.status == ReadinessStatus.READY_WITH_WARNINGS and self._allow_warnings:
            pass
        else:
            return AdmissionResult(
                package_id=package_id,
                status=AdmissionStatus.REJECTED_NOT_READY,
                reasons=report.blocking_issues
                or report.required_user_actions
                or report.refresh_reasons
                or [f"Readiness status is '{report.status.value}'."],
            )

        return AdmissionResult(
            package_id=package_id,
            status=AdmissionStatus.ADMITTED,
            warnings=report.warnings,
            admitted_at=datetime.now(UTC),
        )


def order_items(items: list, ordering: str) -> list:
    """Stable queue ordering (docs/08): ties keep insertion order."""
    if ordering == "highest_match_first":
        return sorted(
            items, key=lambda i: -(i.match_score if i.match_score is not None else -1)
        )
    return list(items)  # selected_order
