"""Application Readiness service (docs/07D-2).

Evaluates whether a package may progress to the next stage. Readiness never
mutates materials — it only gates. Checks (docs/17 Phase 4): required
artifacts exist, hashes match, candidate snapshot valid, required answers
resolved, review completed, duplicate check current, staleness, and manual
handoff files available.
"""

from __future__ import annotations

import json

from job_platform.candidate.models import CandidateBundle
from job_platform.jobs.models import Job
from job_platform.packages.models import PackageManifest, PackageStatus
from job_platform.packages.store import PackageStore
from job_platform.readiness.models import (
    CheckStatus,
    ReadinessCheck,
    ReadinessReport,
    ReadinessStage,
    ReadinessStatus,
)
from job_platform.review.models import ReviewStatus
from job_platform.review.service import REVIEW_REPORT_PATH
from job_platform.shared.ids import sha256_text
from job_platform.shared.logging import get_logger
from job_platform.storage.tracker import ApplicationTracker

logger = get_logger("readiness.service")

READINESS_REPORT_PATH = "readiness/readiness_report.json"

_REQUIRED_ARTIFACTS = [
    "job/job.json",
    "candidate/context.json",
    "answers/prepared_answers.json",
    "plan/application_plan.json",
]

_ACCEPTABLE_REVIEW_STATUSES = {
    ReviewStatus.APPROVED.value,
    ReviewStatus.APPROVED_WITH_WARNINGS.value,
}


class ReadinessService:
    def __init__(
        self,
        store: PackageStore,
        tracker: ApplicationTracker | None = None,
        allow_ready_with_warnings: bool = True,
        block_stale_packages: bool = True,
    ) -> None:
        self._store = store
        self._tracker = tracker
        self._allow_ready_with_warnings = allow_ready_with_warnings
        self._block_stale_packages = block_stale_packages

    def evaluate(
        self,
        manifest: PackageManifest,
        bundle: CandidateBundle,
        stage: ReadinessStage = ReadinessStage.MANUAL_COMPLETION,
    ) -> ReadinessReport:
        report = ReadinessReport(package_id=manifest.package_id, stage=stage)
        try:
            self._check_package_state(manifest, report)
            self._check_required_artifacts(manifest, report)
            self._check_artifact_hashes(manifest, report)
            self._check_candidate_snapshot(manifest, report)
            self._check_required_answers(manifest, report)
            self._check_review(manifest, report)
            self._check_duplicate(manifest, report)
            self._check_staleness(manifest, bundle, report)
            if stage == ReadinessStage.MANUAL_COMPLETION:
                self._check_manual_handoff(manifest, report)
            report.status = self._derive_status(report)
        except Exception as exc:  # noqa: BLE001 - a broken package must fail evaluation
            logger.exception("Readiness evaluation failed for %s", manifest.package_id)
            report.blocking_issues.append(f"Readiness evaluation failed: {exc}")
            report.status = ReadinessStatus.FAILED
        report.next_allowed_action = self._next_action(report)

        self._store.write_artifact(
            manifest, READINESS_REPORT_PATH, report.model_dump_json(indent=2)
        )
        self._store.save_manifest(manifest)
        return report

    # ------------------------------------------------------------------ #

    def _derive_status(self, report: ReadinessReport) -> ReadinessStatus:
        if any(c.check_id == "duplicate_application" and c.status == CheckStatus.FAILED
               for c in report.checks):
            return ReadinessStatus.ALREADY_APPLIED
        if report.blocking_issues:
            return ReadinessStatus.BLOCKED
        if report.refresh_reasons and self._block_stale_packages:
            return ReadinessStatus.REFRESH_REQUIRED
        if report.required_user_actions:
            return ReadinessStatus.USER_ACTION_REQUIRED
        if report.warnings:
            return (
                ReadinessStatus.READY_WITH_WARNINGS
                if self._allow_ready_with_warnings
                else ReadinessStatus.NOT_READY
            )
        return ReadinessStatus.READY

    def _next_action(self, report: ReadinessReport) -> str:
        if report.status in (ReadinessStatus.READY, ReadinessStatus.READY_WITH_WARNINGS):
            return (
                "manual_completion"
                if report.stage == ReadinessStage.MANUAL_COMPLETION
                else "evaluate_manual_completion"
            )
        if report.status == ReadinessStatus.REFRESH_REQUIRED:
            return "re_prepare_package"
        if report.status == ReadinessStatus.USER_ACTION_REQUIRED:
            return "resolve_user_actions"
        if report.status == ReadinessStatus.ALREADY_APPLIED:
            return "none"
        if any("review" in issue.lower() for issue in report.blocking_issues):
            return "run_review"
        return "fix_blocking_issues"

    def _check_package_state(self, manifest: PackageManifest, report: ReadinessReport) -> None:
        usable = manifest.status not in (
            PackageStatus.FAILED,
            PackageStatus.CANCELLED,
            PackageStatus.ALREADY_APPLIED,
        )
        report.add(
            ReadinessCheck(
                check_id="package_state",
                category="package",
                status=CheckStatus.PASSED if usable else CheckStatus.FAILED,
                message=(
                    f"Package status is '{manifest.status.value}'."
                    if usable
                    else f"Package is in terminal status '{manifest.status.value}'."
                ),
            )
        )

    def _check_required_artifacts(
        self, manifest: PackageManifest, report: ReadinessReport
    ) -> None:
        missing = [p for p in _REQUIRED_ARTIFACTS if p not in manifest.artifacts]
        report.add(
            ReadinessCheck(
                check_id="required_artifacts",
                category="artifacts",
                status=CheckStatus.FAILED if missing else CheckStatus.PASSED,
                message=(
                    f"Required artifacts missing from the manifest: {missing}."
                    if missing
                    else "All required artifacts are present."
                ),
                evidence=_REQUIRED_ARTIFACTS,
            )
        )

    def _check_artifact_hashes(self, manifest: PackageManifest, report: ReadinessReport) -> None:
        package_dir = self._store.package_dir(manifest.package_id)
        mismatched: list[str] = []
        for path, record in manifest.artifacts.items():
            if path in (READINESS_REPORT_PATH, REVIEW_REPORT_PATH):
                continue
            file_path = package_dir / path
            if not file_path.exists() or (
                sha256_text(file_path.read_text(encoding="utf-8")) != record.sha256
            ):
                mismatched.append(path)
        report.add(
            ReadinessCheck(
                check_id="artifact_hashes",
                category="integrity",
                status=CheckStatus.FAILED if mismatched else CheckStatus.PASSED,
                message=(
                    f"Artifacts changed or missing since preparation: {mismatched}."
                    if mismatched
                    else "All artifact hashes match the manifest."
                ),
                evidence=mismatched,
            )
        )

    def _check_candidate_snapshot(
        self, manifest: PackageManifest, report: ReadinessReport
    ) -> None:
        status = CheckStatus.PASSED
        message = "Candidate context snapshot is valid."
        try:
            snapshot = json.loads(
                self._store.read_artifact(manifest.package_id, "candidate/context.json")
            )
            if "profile" not in snapshot:
                status, message = (
                    CheckStatus.FAILED,
                    "Candidate context snapshot has no profile section.",
                )
        except Exception:  # noqa: BLE001
            status, message = (
                CheckStatus.FAILED,
                "Candidate context snapshot is missing or unreadable.",
            )
        report.add(
            ReadinessCheck(
                check_id="candidate_snapshot",
                category="candidate",
                status=status,
                message=message,
            )
        )

    def _check_required_answers(
        self, manifest: PackageManifest, report: ReadinessReport
    ) -> None:
        try:
            unresolved = json.loads(
                self._store.read_artifact(
                    manifest.package_id, "answers/unresolved_questions.json"
                )
            ).get("questions", [])
        except Exception:  # noqa: BLE001
            unresolved = []
        required = [q for q in unresolved if q.get("required_for_readiness")]
        optional = [q for q in unresolved if not q.get("required_for_readiness")]
        if required:
            report.add(
                ReadinessCheck(
                    check_id="required_answers",
                    category="answers",
                    status=CheckStatus.USER_ACTION_REQUIRED,
                    message=(
                        "Required answers are unresolved: "
                        + ", ".join(q.get("question_family", "?") for q in required)
                    ),
                    recommended_action="Provide the missing answers, then re-evaluate.",
                )
            )
        else:
            report.add(
                ReadinessCheck(
                    check_id="required_answers",
                    category="answers",
                    status=(
                        CheckStatus.PASSED_WITH_WARNING if optional else CheckStatus.PASSED
                    ),
                    message=(
                        "All required answers are resolved"
                        + (
                            f"; {len(optional)} optional question(s) remain blank."
                            if optional
                            else "."
                        )
                    ),
                )
            )

    def _check_review(self, manifest: PackageManifest, report: ReadinessReport) -> None:
        if REVIEW_REPORT_PATH not in manifest.artifacts:
            report.add(
                ReadinessCheck(
                    check_id="review_completed",
                    category="review",
                    status=CheckStatus.FAILED,
                    message="No review has been run for this package.",
                    recommended_action="Run the application review.",
                )
            )
            return
        review = json.loads(
            self._store.read_artifact(manifest.package_id, REVIEW_REPORT_PATH)
        )
        status = review.get("status", "")
        if status in _ACCEPTABLE_REVIEW_STATUSES:
            report.add(
                ReadinessCheck(
                    check_id="review_completed",
                    category="review",
                    status=CheckStatus.PASSED,
                    message=f"Review completed with status '{status}'.",
                )
            )
        elif status == ReviewStatus.USER_INPUT_REQUIRED.value:
            report.add(
                ReadinessCheck(
                    check_id="review_completed",
                    category="review",
                    status=CheckStatus.USER_ACTION_REQUIRED,
                    message="The review requires user input before this package can proceed.",
                    evidence=review.get("required_user_actions", []),
                )
            )
        else:
            report.add(
                ReadinessCheck(
                    check_id="review_completed",
                    category="review",
                    status=CheckStatus.FAILED,
                    message=f"The review finished with status '{status}'.",
                    recommended_action="Resolve the review findings and re-run review.",
                )
            )

    def _check_duplicate(self, manifest: PackageManifest, report: ReadinessReport) -> None:
        if self._tracker is None:
            report.add(
                ReadinessCheck(
                    check_id="duplicate_application",
                    category="history",
                    status=CheckStatus.NOT_APPLICABLE,
                    required=False,
                    message="No tracker configured; duplicate check skipped.",
                )
            )
            return
        job = Job(
            id="readiness_check",
            company=manifest.job.company,
            title=manifest.job.title,
            job_id=manifest.job.job_id,
            url=manifest.job.application_url,
            country="",
        )
        duplicate = self._tracker.is_duplicate(job)
        report.add(
            ReadinessCheck(
                check_id="duplicate_application",
                category="history",
                status=CheckStatus.FAILED if duplicate else CheckStatus.PASSED,
                message=(
                    "This job is already recorded in the application tracker."
                    if duplicate
                    else "No duplicate application found in the tracker."
                ),
            )
        )

    def _check_staleness(
        self, manifest: PackageManifest, bundle: CandidateBundle, report: ReadinessReport
    ) -> None:
        stale = self._store.stale_sources(manifest, bundle)
        report.add(
            ReadinessCheck(
                check_id="package_freshness",
                category="staleness",
                status=CheckStatus.STALE if stale else CheckStatus.PASSED,
                message=(
                    "Candidate sources changed since preparation: " + ", ".join(stale)
                    if stale
                    else "The package matches current candidate data."
                ),
                evidence=stale,
                recommended_action="Re-prepare the package." if stale else None,
            )
        )

    def _check_manual_handoff(self, manifest: PackageManifest, report: ReadinessReport) -> None:
        problems: list[str] = []
        if not manifest.job.application_url:
            problems.append("no application URL")
        if not manifest.selected_resume:
            problems.append("no selected resume")
        report.add(
            ReadinessCheck(
                check_id="manual_handoff_files",
                category="handoff",
                status=CheckStatus.FAILED if problems else CheckStatus.PASSED,
                message=(
                    "Manual handoff is incomplete: " + ", ".join(problems) + "."
                    if problems
                    else "Application URL, resume, and answers are available for handoff."
                ),
            )
        )
