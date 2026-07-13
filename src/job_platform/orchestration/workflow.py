"""Application workflow state machine (docs/08 Execution Orchestrator).

Runs one package through durable stages: validation → lock → readiness →
browser start → navigation → identity check → form execution → cleanup.
State persists to ``execution/state.json`` after every stage; retryable
stages (browser start, navigation) retry with a bounded count; the form
engine's own step state prevents repeating completed actions after a crash.

Final submission is not a stage — that boundary arrives with Phase 9.
"""

from __future__ import annotations

import json
from pathlib import Path

from job_platform.ats.registry import ATSAdapterRegistry
from job_platform.browser.navigation import NavigationPolicy
from job_platform.browser.service import BrowserSession
from job_platform.candidate.context import build_candidate_context
from job_platform.candidate.models import CandidateBundle
from job_platform.forms.engine import (
    EngineStatus,
    GenericFormEngine,
    documents_for_package,
    load_prepared_answers,
    store_execution_report,
)
from job_platform.orchestration.locks import LockManager, LockUnavailableError
from job_platform.orchestration.models import (
    StageResult,
    StageStatus,
    WorkflowStage,
    WorkflowState,
    WorkflowStatus,
)
from job_platform.packages.models import PackageManifest, PackageStatus
from job_platform.packages.store import PackageStore
from job_platform.readiness.models import ReadinessStage, ReadinessStatus
from job_platform.readiness.service import ReadinessService
from job_platform.shared.config import Settings
from job_platform.shared.errors import BrowserError, NavigationBlockedError
from job_platform.shared.files import atomic_write_text
from job_platform.shared.logging import get_logger

logger = get_logger("orchestration.workflow")

STATE_PATH = "execution/state.json"
BROWSER_STEPS_PATH = "execution/browser_steps.json"

_ENGINE_TO_WORKFLOW = {
    EngineStatus.READY_FOR_REVIEW: WorkflowStatus.WAITING_FOR_REVIEW,
    EngineStatus.STOPPED_BEFORE_SUBMIT: WorkflowStatus.WAITING_FOR_REVIEW,
    EngineStatus.PAUSED_CAPTCHA: WorkflowStatus.WAITING_FOR_USER,
    EngineStatus.PAUSED_LOGIN: WorkflowStatus.WAITING_FOR_USER,
    EngineStatus.PAUSED_MFA: WorkflowStatus.WAITING_FOR_USER,
    EngineStatus.CONFIRMATION_DETECTED: WorkflowStatus.COMPLETED,
    EngineStatus.APPLICATION_CLOSED: WorkflowStatus.BLOCKED,
    EngineStatus.NO_APPLICATION_FORM: WorkflowStatus.FAILED,
    EngineStatus.STOPPED_ACTION_FAILED: WorkflowStatus.FAILED,
    EngineStatus.STOPPED_NO_PROGRESSION: WorkflowStatus.FAILED,
    EngineStatus.MAX_PAGES_REACHED: WorkflowStatus.FAILED,
}


class ApplicationWorkflow:
    def __init__(
        self,
        manifest: PackageManifest,
        bundle: CandidateBundle,
        store: PackageStore,
        provider,
        registry: ATSAdapterRegistry,
        readiness: ReadinessService,
        locks: LockManager,
        settings: Settings,
        queue_id: str = "",
        headless: bool | None = None,
        submit_mode: bool = False,
        submission_service=None,
        automatic_mode: bool = False,
        eligibility=None,
        history=None,
    ) -> None:
        self._manifest = manifest
        self._bundle = bundle
        self._store = store
        self._provider = provider
        self._registry = registry
        self._readiness = readiness
        self._locks = locks
        self._settings = settings
        self._queue_id = queue_id
        self._headless = headless
        # Automatic mode is a submit mode gated by the eligibility engine
        # instead of a user approval record.
        self._automatic_mode = automatic_mode
        self._submit_mode = submit_mode or automatic_mode
        self._submission_service = submission_service
        self._eligibility = eligibility
        self._history = history
        if self._submit_mode and submission_service is None:
            raise ValueError("submit/automatic mode requires a submission_service")
        if automatic_mode and eligibility is None:
            raise ValueError("automatic_mode requires an eligibility engine")
        self._session: BrowserSession | None = None
        self._package_lock = None
        self._snapshot = None
        self._adapter = None
        self._submission_outcome: str = ""

    # -- durable state ---------------------------------------------------- #

    def _state_path(self) -> Path:
        return self._store.package_dir(self._manifest.package_id) / STATE_PATH

    def _persist(self, state: WorkflowState) -> None:
        atomic_write_text(self._state_path(), state.model_dump_json(indent=2))

    def load_existing_state(self) -> WorkflowState | None:
        path = self._state_path()
        if not path.exists():
            return None
        try:
            return WorkflowState.model_validate_json(path.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001 - unreadable state is treated as absent
            logger.warning("Existing workflow state unreadable for %s",
                           self._manifest.package_id)
            return None

    # -- run ---------------------------------------------------------------- #

    async def run(self) -> WorkflowState:
        previous = self.load_existing_state()
        if previous is not None and previous.status in (
            WorkflowStatus.RUNNING,
            WorkflowStatus.RECOVERING,
            WorkflowStatus.WAITING_FOR_USER,
        ):
            state = previous
            state.status = WorkflowStatus.RECOVERING
            state.attempt_count += 1
            logger.info(
                "Recovering workflow %s (attempt %d)",
                state.workflow_id,
                state.attempt_count,
            )
        else:
            state = WorkflowState(
                package_id=self._manifest.package_id, queue_id=self._queue_id
            )
        state.status = (
            WorkflowStatus.RUNNING
            if state.status != WorkflowStatus.RECOVERING
            else WorkflowStatus.RECOVERING
        )
        self._persist(state)

        stages = [
            (WorkflowStage.QUEUE_VALIDATION, self._stage_validation, 1),
            (WorkflowStage.PACKAGE_LOCK, self._stage_lock, 1),
            (WorkflowStage.PRE_EXECUTION_READINESS, self._stage_readiness, 1),
        ]
        if self._automatic_mode:
            # Cheap pre-browser gate (enabled + kill switch) before launching.
            stages.append(
                (WorkflowStage.USER_APPROVAL_CHECK, self._stage_automatic_precheck, 1)
            )
        elif self._submit_mode:
            # Approval is verified before any browser work (docs/17 Phase 10:
            # approval bound to the reviewed snapshot).
            stages.append(
                (WorkflowStage.USER_APPROVAL_CHECK, self._stage_approval_check, 1)
            )
        stages += [
            (
                WorkflowStage.BROWSER_SESSION_START,
                self._stage_browser_start,
                1 + self._settings.browser.max_retries,
            ),
            (
                WorkflowStage.APPLICATION_NAVIGATION,
                self._stage_navigation,
                1 + self._settings.browser.max_retries,
            ),
            (WorkflowStage.APPLICATION_IDENTITY_CHECK, self._stage_identity, 1),
            (WorkflowStage.FORM_EXECUTION, self._stage_form_execution, 1),
        ]
        if self._submit_mode:
            stages.append(
                (WorkflowStage.FINAL_SUBMISSION, self._stage_final_submission, 1)
            )
        try:
            for stage, handler, max_attempts in stages:
                result = await self._run_stage(state, stage, handler, max_attempts)
                if result.status in (StageStatus.SUCCESS, StageStatus.SUCCESS_WITH_WARNINGS):
                    continue
                if result.status == StageStatus.WAITING_FOR_REVIEW:
                    state.status = WorkflowStatus.WAITING_FOR_REVIEW
                elif result.status == StageStatus.WAITING_FOR_USER:
                    state.status = WorkflowStatus.WAITING_FOR_USER
                elif result.status == StageStatus.SUBMISSION_UNKNOWN:
                    state.status = WorkflowStatus.SUBMISSION_UNKNOWN
                elif result.stage == WorkflowStage.APPLICATION_IDENTITY_CHECK:
                    state.status = WorkflowStatus.BLOCKED
                else:
                    state.status = WorkflowStatus.FAILED
                break
            else:
                if state.status in (WorkflowStatus.RUNNING, WorkflowStatus.RECOVERING):
                    state.status = (
                        WorkflowStatus.SUBMITTED
                        if self._submit_mode and self._submission_outcome == "submitted"
                        else WorkflowStatus.COMPLETED
                    )
        finally:
            await self._cleanup(state)
            self._persist(state)
        return state

    async def _run_stage(
        self, state: WorkflowState, stage: WorkflowStage, handler, max_attempts: int
    ) -> StageResult:
        attempts = 0
        while True:
            attempts += 1
            state.current_stage = stage
            self._persist(state)
            result = StageResult(stage=stage, status=StageStatus.SUCCESS)
            try:
                await handler(state, result)
            except LockUnavailableError as exc:
                result.status = StageStatus.NON_RETRYABLE_FAILURE
                result.error = exc.message
            except NavigationBlockedError as exc:
                result.status = StageStatus.NON_RETRYABLE_FAILURE
                result.error = exc.message
            except BrowserError as exc:
                result.status = StageStatus.RETRYABLE_FAILURE
                result.retryable = True
                result.error = exc.message
            except Exception as exc:  # noqa: BLE001 - stage failures must not crash the queue
                logger.exception("Stage %s crashed", stage.value)
                result.status = StageStatus.NON_RETRYABLE_FAILURE
                result.error = str(exc)

            state.record(result)
            self._persist(state)
            if result.status == StageStatus.RETRYABLE_FAILURE and attempts < max_attempts:
                logger.warning(
                    "Retrying stage %s (attempt %d/%d): %s",
                    stage.value,
                    attempts + 1,
                    max_attempts,
                    result.error,
                )
                continue
            return result

    # -- stages ---------------------------------------------------------------- #

    async def _stage_validation(self, state: WorkflowState, result: StageResult) -> None:
        manifest = self._store.load_manifest(self._manifest.package_id)
        if manifest.status not in (PackageStatus.READY,):
            result.status = StageStatus.NON_RETRYABLE_FAILURE
            result.error = f"Package status is '{manifest.status.value}', not 'ready'."

    async def _stage_lock(self, state: WorkflowState, result: StageResult) -> None:
        self._package_lock = self._locks.package_lock(self._manifest.package_id)
        self._package_lock.acquire()

    async def _stage_readiness(self, state: WorkflowState, result: StageResult) -> None:
        report = self._readiness.evaluate(
            self._manifest, self._bundle, ReadinessStage.MANUAL_COMPLETION
        )
        if report.status not in (
            ReadinessStatus.READY,
            ReadinessStatus.READY_WITH_WARNINGS,
        ):
            result.status = StageStatus.NON_RETRYABLE_FAILURE
            result.error = (
                "Pre-execution readiness failed: "
                + "; ".join(report.blocking_issues or [report.status.value])
            )
        result.warnings = report.warnings

    async def _stage_browser_start(self, state: WorkflowState, result: StageResult) -> None:
        url = self._manifest.job.application_url
        policy = NavigationPolicy.for_application(
            url, allow_local_files=url.startswith("file:")
        )
        package_dir = self._store.package_dir(self._manifest.package_id)
        settings = self._settings.browser.model_copy(
            update={"headless": self._headless}
        ) if self._headless is not None else self._settings.browser
        self._session = BrowserSession(
            profile_dir=self._settings.paths.browser_profile_dir / state.browser_profile,
            screenshots_dir=package_dir / "screenshots",
            policy=policy,
            settings=settings,
            allowed_upload_roots=[package_dir, self._settings.paths.candidate_dir],
        )
        await self._session.start()

    async def _stage_navigation(self, state: WorkflowState, result: StageResult) -> None:
        self._snapshot = await self._session.open_page(self._manifest.job.application_url)

    async def _stage_identity(self, state: WorkflowState, result: StageResult) -> None:
        resolution = self._registry.resolve(self._snapshot.url, self._snapshot)
        state.ats_adapter = resolution.adapter_id
        if resolution.adapter_id is None:
            result.status = StageStatus.SUCCESS_WITH_WARNINGS
            result.warnings.append(
                "No dedicated adapter matched; job identity could not be "
                "verified beyond the trusted URL."
            )
            return
        self._adapter = self._registry.get_adapter(resolution.adapter_id)
        identity = self._adapter.extract_job_identity(self._snapshot)
        expected_title = self._manifest.job.title.lower()
        found_title = identity.title.lower()
        title_matches = (
            not found_title
            or expected_title in found_title
            or found_title in expected_title
        )
        job_id_matches = (
            not identity.job_id
            or not self._manifest.job.job_id
            or identity.job_id == self._manifest.job.job_id
        )
        if not (title_matches and job_id_matches):
            result.status = StageStatus.NON_RETRYABLE_FAILURE
            result.error = (
                f"Job identity mismatch: page shows {identity.title!r} "
                f"(job_id={identity.job_id!r}) but the package targets "
                f"{self._manifest.job.title!r} (job_id={self._manifest.job.job_id!r})."
            )

    async def _stage_approval_check(self, state: WorkflowState, result: StageResult) -> None:
        from job_platform.review.approval import ApprovalError, verify_approval

        try:
            approval = verify_approval(self._store, self._manifest)
        except ApprovalError as exc:
            result.status = StageStatus.NON_RETRYABLE_FAILURE
            result.error = exc.message
            return
        result.warnings.append(
            f"Approved by {approval.approved_by} at {approval.approved_at.isoformat()}"
        )

    async def _stage_automatic_precheck(
        self, state: WorkflowState, result: StageResult
    ) -> None:
        """Cheap pre-browser gate for automatic mode. A blocked gate downgrades
        the run to review (fill only, no submit) rather than failing."""
        gate = self._eligibility.quick_gate(self._manifest)
        if not gate.automatic:
            self._downgrade("; ".join(gate.reasons))
            result.status = StageStatus.NON_RETRYABLE_FAILURE
            result.error = "Automatic mode unavailable: " + "; ".join(gate.reasons)

    def _final_control_confidence(self) -> int:
        """Confidence that the identified control is the true final submission
        control (docs/17: final control confidence must exceed threshold)."""
        if self._adapter is None:
            return 0
        control = self._adapter.identify_submission_control(self._snapshot)
        if control is None:
            return 0
        # Adapter-identified by exact id/label is high confidence; a generic
        # type=="submit" match is lower.
        return 95 if control.type == "submit" and control.action_id else 80

    def _downgrade(self, reason: str) -> None:
        if self._history is not None:
            self._history.record_event(
                "auto_downgraded", package_id=self._manifest.package_id, message=reason
            )

    def _review_status(self):
        from job_platform.review.models import ReviewStatus

        report = self._read_package_json("review/review_report.json")
        return ReviewStatus(report["status"]) if report else ReviewStatus.BLOCKED

    def _review_warning_count(self) -> int:
        report = self._read_package_json("review/review_report.json")
        if not report:
            return 999
        return sum(
            1 for f in report.get("findings", [])
            if f.get("severity") in ("high", "medium", "low")
        )

    def _readiness_status(self):
        from job_platform.readiness.models import ReadinessStatus

        report = self._read_package_json("readiness/readiness_report.json")
        return ReadinessStatus(report["status"]) if report else ReadinessStatus.NOT_READY

    def _read_package_json(self, relative_path: str) -> dict | None:
        from job_platform.shared.errors import StorageError

        try:
            return json.loads(
                self._store.read_artifact(self._manifest.package_id, relative_path)
            )
        except (StorageError, ValueError):
            return None

    async def _stage_form_execution(self, state: WorkflowState, result: StageResult) -> None:
        answers = load_prepared_answers(self._store, self._manifest)
        documents = documents_for_package(self._manifest, self._store, self._bundle)
        package_dir = self._store.package_dir(self._manifest.package_id)
        state_file = package_dir / BROWSER_STEPS_PATH
        if self._submit_mode:
            # A submission run is a deliberate fresh execution: the approval
            # validated the recorded materials; the page must be refilled, so
            # crash-recovery skip state from the review run must not apply.
            state_file.unlink(missing_ok=True)
        engine = GenericFormEngine(
            self._session,
            self._provider,
            answers,
            documents=documents,
            candidate_context=build_candidate_context(
                self._bundle,
                resume=self._bundle.resumes[0] if self._bundle.resumes else None,
            ),
            adapter=self._adapter,
            state_file=state_file,
        )
        report = await engine.run_review_mode(self._snapshot)
        # Automatic mode always keeps the report so a downgrade leaves a
        # reviewable filled form behind.
        if not self._submit_mode or self._automatic_mode:
            store_execution_report(self._store, self._manifest, report)
        state.engine_status = report.status.value

        workflow_status = _ENGINE_TO_WORKFLOW.get(report.status, WorkflowStatus.FAILED)
        if workflow_status == WorkflowStatus.WAITING_FOR_REVIEW:
            if self._submit_mode:
                self._snapshot = await self._session.inspect_page()
                if self._automatic_mode:
                    # Full eligibility gate with the now-known adapter, control
                    # confidence, and form-fill signals (docs/17 downgrade
                    # conditions). Any surfaced field or failed gate downgrades.
                    if report.fields_needing_user:
                        self._downgrade(
                            "Fields require the user: "
                            + ", ".join(
                                e.field_id for e in report.fields_needing_user[:5]
                            )
                        )
                        result.status = StageStatus.WAITING_FOR_REVIEW
                        return
                    verdict = self._eligibility.evaluate(
                        self._manifest,
                        self._bundle,
                        self._adapter,
                        self._review_status(),
                        self._review_warning_count(),
                        self._readiness_status(),
                        self._final_control_confidence(),
                    )
                    if not verdict.automatic:
                        self._downgrade("; ".join(verdict.reasons))
                        result.status = StageStatus.WAITING_FOR_REVIEW
                        return
                # Submit (approved submit mode, or automatic mode that passed).
                return
            result.status = StageStatus.WAITING_FOR_REVIEW
        elif workflow_status == WorkflowStatus.WAITING_FOR_USER:
            result.status = StageStatus.WAITING_FOR_USER
        elif workflow_status == WorkflowStatus.BLOCKED:
            result.status = StageStatus.NON_RETRYABLE_FAILURE
            result.error = f"The application page is not usable: {report.status.value}."
        elif workflow_status == WorkflowStatus.FAILED:
            result.status = StageStatus.NON_RETRYABLE_FAILURE
            result.error = f"Form execution ended with '{report.status.value}'."
        elif self._submit_mode:
            result.status = StageStatus.NON_RETRYABLE_FAILURE
            result.error = (
                f"Submission requires a filled form awaiting the final control, "
                f"but the run ended with '{report.status.value}'."
            )

    async def _stage_final_submission(self, state: WorkflowState, result: StageResult) -> None:
        from job_platform.submission.models import SubmissionOutcome
        from job_platform.submission.service import SubmissionBlockedError

        try:
            attempt = await self._submission_service.submit(
                self._session,
                self._manifest,
                self._snapshot,
                adapter=self._adapter,
                approved=True,
                workflow_id=state.workflow_id,
            )
        except SubmissionBlockedError as exc:
            result.status = StageStatus.NON_RETRYABLE_FAILURE
            result.error = exc.message
            return
        verification = attempt.verification_result
        outcome = verification.outcome if verification else SubmissionOutcome.SUBMISSION_UNKNOWN
        self._submission_outcome = outcome.value
        state.engine_status = f"submission_{outcome.value}"
        if self._automatic_mode and self._history is not None:
            event = {
                SubmissionOutcome.SUBMITTED: "auto_submitted",
                SubmissionOutcome.SUBMISSION_UNKNOWN: "auto_unknown",
            }.get(outcome, "auto_blocked")
            self._history.record_event(
                event,
                package_id=self._manifest.package_id,
                message=f"{self._manifest.job.company} — {self._manifest.job.title}",
            )
        if outcome == SubmissionOutcome.SUBMITTED:
            return
        if outcome == SubmissionOutcome.SUBMISSION_UNKNOWN:
            result.status = StageStatus.SUBMISSION_UNKNOWN
            result.error = verification.notes if verification else "outcome unknown"
            return
        result.status = StageStatus.NON_RETRYABLE_FAILURE
        result.error = f"Submission ended with '{outcome.value}'."

    async def _cleanup(self, state: WorkflowState) -> None:
        if self._session is not None:
            try:
                await self._session.close()
            except Exception:  # noqa: BLE001
                logger.warning("Browser session close failed during cleanup.")
            self._session = None
        if self._package_lock is not None:
            self._package_lock.release()
            self._package_lock = None


def read_workflow_state(store: PackageStore, package_id: str) -> WorkflowState | None:
    path = store.package_dir(package_id) / STATE_PATH
    if not path.exists():
        return None
    try:
        return WorkflowState.model_validate_json(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def has_unresolved_execution(store: PackageStore, package_id: str) -> bool:
    """True when a prior run ended in a state that must be resolved first."""
    state = read_workflow_state(store, package_id)
    if state is None:
        return False
    return state.status.value == "submission_unknown"


def workflow_state_json(store: PackageStore, package_id: str) -> dict | None:
    state = read_workflow_state(store, package_id)
    return json.loads(state.model_dump_json()) if state else None
