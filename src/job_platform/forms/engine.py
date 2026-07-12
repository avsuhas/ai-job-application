"""Generic Form Engine (docs/09).

Drives one application through unknown-but-accessible forms in Review mode:
select the application form, classify fields, map prepared answers, execute
verified actions, re-inspect for dynamic fields, progress through pages, and
stop safely at review pages, safety challenges, or ambiguous final controls.

The engine never clicks submit-type controls (docs/17 Phase 6 exit gate:
"Generic engine never guesses final submission").
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from enum import StrEnum
from typing import TYPE_CHECKING

from pydantic import BaseModel, Field

from job_platform.browser.models import ActionResult, ActionStatus, PageSnapshot

if TYPE_CHECKING:  # avoid a runtime import cycle with the ats package
    from job_platform.ats.base import ATSAdapter, ConfirmationResult
from job_platform.browser.service import BrowserSession, snapshot_requires_pause
from job_platform.candidate.models import CandidateBundle
from job_platform.forms.boundary import detect_form_boundary
from job_platform.forms.mapper import FormPlan, PlanEntry, build_form_plan
from job_platform.forms.semantic import classify_field_with_provider
from job_platform.packages.models import PackageManifest
from job_platform.packages.store import PackageStore
from job_platform.preparation.answers import PreparedAnswer, PreparedAnswerSet
from job_platform.providers.base import ReasoningProvider
from job_platform.shared.errors import BrowserError, StorageError
from job_platform.shared.logging import get_logger

logger = get_logger("forms.engine")

EXECUTION_REPORT_PATH = "execution/form_execution_report.json"

_EDITABLE_TYPES = {"text", "textarea", "email", "phone", "number", "url", "date",
                   "select", "radio", "checkbox", "file"}


class EngineStatus(StrEnum):
    READY_FOR_REVIEW = "ready_for_review"
    PAUSED_CAPTCHA = "paused_captcha"
    PAUSED_LOGIN = "paused_login"
    PAUSED_MFA = "paused_mfa"
    STOPPED_BEFORE_SUBMIT = "stopped_before_submit"
    STOPPED_ACTION_FAILED = "stopped_action_failed"
    STOPPED_NO_PROGRESSION = "stopped_no_progression"
    NO_APPLICATION_FORM = "no_application_form"
    MAX_PAGES_REACHED = "max_pages_reached"
    CONFIRMATION_DETECTED = "confirmation_detected"
    APPLICATION_CLOSED = "application_closed"


class PageResult(BaseModel):
    page_number: int
    url: str
    heading: str = ""
    page_type: str = ""
    entries: list[PlanEntry] = Field(default_factory=list)
    action_results: list[ActionResult] = Field(default_factory=list)
    validation_errors: list[str] = Field(default_factory=list)
    dynamic_rounds: int = 0
    submission_control: str | None = None


class FormExecutionReport(BaseModel):
    """Generic-form diagnostics (docs/09) persisted inside the package."""

    package_id: str = ""
    adapter_id: str | None = None
    status: EngineStatus
    pages: list[PageResult] = Field(default_factory=list)
    screenshot: str | None = None
    confirmation: dict | None = None
    started_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    finished_at: datetime | None = None

    @property
    def fields_needing_user(self) -> list[PlanEntry]:
        wanted = {"unknown_field", "no_stored_answer", "option_mismatch",
                  "unsupported_widget", "sensitive_skipped"}
        return [
            entry
            for page in self.pages
            for entry in page.entries
            if entry.status.value in wanted
        ]


def is_review_page(snapshot: PageSnapshot) -> bool:
    """docs/09 review-page detection: review language plus few editable fields."""
    text = f"{snapshot.heading} {snapshot.title}".lower()
    if "review" not in text and "summary" not in text:
        return False
    editable = [
        f for f in snapshot.fields
        if f.visible and f.enabled and f.field_type.value in _EDITABLE_TYPES
    ]
    return len(editable) <= 2


def load_prepared_answers(store: PackageStore, manifest: PackageManifest) -> PreparedAnswerSet:
    raw = json.loads(store.read_artifact(manifest.package_id, "answers/prepared_answers.json"))
    return PreparedAnswerSet(
        answers=[PreparedAnswer.model_validate(a) for a in raw.get("answers", [])]
    )


def documents_for_package(
    manifest: PackageManifest, store: PackageStore, bundle: CandidateBundle
) -> dict[str, str]:
    """Absolute file paths for upload fields, resolved from the package."""
    documents: dict[str, str] = {}
    package_dir = store.package_dir(manifest.package_id)
    if manifest.selected_resume:
        if manifest.selected_resume.startswith("resume/"):
            documents["documents.resume"] = str(package_dir / manifest.selected_resume)
        elif manifest.selected_resume.startswith("candidate resume: "):
            name = manifest.selected_resume.removeprefix("candidate resume: ")
            for resume in bundle.resumes:
                if resume.name == name:
                    documents["documents.resume"] = str(resume.path)
    if manifest.cover_letter:
        documents["documents.cover_letter"] = str(package_dir / manifest.cover_letter)
    return documents


class GenericFormEngine:
    def __init__(
        self,
        session: BrowserSession,
        provider: ReasoningProvider,
        answers: PreparedAnswerSet,
        documents: dict[str, str] | None = None,
        candidate_context: str = "",
        max_pages: int = 8,
        max_dynamic_rounds: int = 3,
        adapter: ATSAdapter | None = None,
    ) -> None:
        self._session = session
        self._provider = provider
        self._answers = answers
        self._documents = documents or {}
        self._candidate_context = candidate_context
        self._max_pages = max_pages
        self._max_dynamic_rounds = max_dynamic_rounds
        self._adapter = adapter

    async def _plan_for_fields(self, fields, heading: str) -> FormPlan:
        classifications = {}
        for field in fields:
            # ATS-specific field knowledge wins over generic rules (docs/09
            # Semantic Classification Priority: ATS mapping before synonyms).
            ats_classification = (
                self._adapter.classify_field(field) if self._adapter else None
            )
            if ats_classification is not None:
                classifications[field.field_id] = ats_classification
                continue
            classifications[field.field_id] = await classify_field_with_provider(
                field,
                self._provider,
                candidate_context=self._candidate_context,
                page_heading=heading,
            )
        return build_form_plan(fields, classifications, self._answers, self._documents)

    def _adapter_page_check(
        self, snapshot: PageSnapshot, report: FormExecutionReport
    ) -> EngineStatus | None:
        """Adapter page classification that ends the run (docs/09)."""
        if self._adapter is None:
            return None
        classification = self._adapter.classify_page(snapshot)
        if classification.page_type.value == "confirmation":
            confirmation: ConfirmationResult = self._adapter.verify_confirmation(snapshot)
            report.confirmation = confirmation.model_dump()
            return EngineStatus.CONFIRMATION_DETECTED
        if classification.page_type.value == "application_closed":
            return EngineStatus.APPLICATION_CLOSED
        if classification.page_type.value == "review":
            return EngineStatus.READY_FOR_REVIEW
        return None

    @staticmethod
    def _pause_status(snapshot: PageSnapshot) -> EngineStatus:
        if snapshot.signals.captcha:
            return EngineStatus.PAUSED_CAPTCHA
        if snapshot.signals.mfa:
            return EngineStatus.PAUSED_MFA
        return EngineStatus.PAUSED_LOGIN

    def _select_fields(self, snapshot: PageSnapshot):
        """Boundary detection with a single-form fallback (docs/09)."""
        boundary = detect_form_boundary(snapshot.fields, snapshot.actions)
        if boundary.selected_form_id is not None:
            return (
                boundary.selected_fields(snapshot.fields),
                boundary.selected_actions(snapshot.actions),
                True,
            )
        form_ids = {f.form_id for f in snapshot.fields if f.visible}
        if len(form_ids) == 1:
            return (
                [f for f in snapshot.fields if f.visible],
                snapshot.actions,
                True,
            )
        return [], [], False

    async def run_review_mode(self, snapshot: PageSnapshot) -> FormExecutionReport:
        report = FormExecutionReport(
            status=EngineStatus.MAX_PAGES_REACHED,
            adapter_id=self._adapter.metadata.adapter_id if self._adapter else None,
        )
        processed: set[str] = set()

        for page_number in range(1, self._max_pages + 1):
            if snapshot_requires_pause(snapshot):
                report.status = self._pause_status(snapshot)
                report.screenshot = str(await self._session.capture_screenshot("paused"))
                break
            adapter_status = self._adapter_page_check(snapshot, report)
            if adapter_status is not None:
                report.status = adapter_status
                report.screenshot = str(
                    await self._session.capture_screenshot(adapter_status.value)
                )
                logger.info("Adapter classified page as terminal: %s", adapter_status.value)
                break
            if is_review_page(snapshot):
                report.status = EngineStatus.READY_FOR_REVIEW
                report.screenshot = str(
                    await self._session.capture_screenshot("review_page")
                )
                logger.info("Review page reached; stopping before submission.")
                break

            fields, actions, form_found = self._select_fields(snapshot)
            if not form_found:
                report.status = EngineStatus.NO_APPLICATION_FORM
                break

            page_result = PageResult(
                page_number=page_number, url=snapshot.url, heading=snapshot.heading
            )
            if self._adapter is not None:
                page_result.page_type = self._adapter.classify_page(snapshot).page_type.value
                control = self._adapter.identify_submission_control(snapshot)
                if control is not None:
                    page_result.submission_control = control.action_id
            report.pages.append(page_result)

            fillable = [f for f in fields if f.visible and f.field_id not in processed]
            form_plan = await self._plan_for_fields(fillable, snapshot.heading)
            page_result.entries.extend(form_plan.entries)
            results = await self._session.execute_plan(form_plan.plan, snapshot)
            page_result.action_results.extend(results)
            processed.update(
                r.field_id for r in results if r.status == ActionStatus.SUCCESS
            )
            if any(r.status == ActionStatus.FAILED for r in results):
                report.status = EngineStatus.STOPPED_ACTION_FAILED
                report.screenshot = str(
                    await self._session.capture_screenshot("action_failed")
                )
                break

            # Dynamic field detection (docs/09): conditional fields may have
            # appeared after the actions above — re-inspect and fill them.
            for _ in range(self._max_dynamic_rounds):
                snapshot = await self._session.inspect_page()
                fields, actions, _ = self._select_fields(snapshot)
                new_fields = [
                    f for f in fields if f.visible and f.field_id not in processed
                ]
                if not new_fields:
                    break
                page_result.dynamic_rounds += 1
                extra_plan = await self._plan_for_fields(new_fields, snapshot.heading)
                page_result.entries.extend(extra_plan.entries)
                extra_results = await self._session.execute_plan(extra_plan.plan, snapshot)
                page_result.action_results.extend(extra_results)
                processed.update(
                    r.field_id for r in extra_results if r.status == ActionStatus.SUCCESS
                )
                if not extra_plan.plan.steps:
                    break

            page_result.validation_errors = snapshot.validation_errors

            next_actions = [a for a in actions if a.type == "next"]
            if not next_actions:
                # Ambiguous-final-action protection: a submit-like control is
                # never clicked automatically (docs/09, docs/17 Phase 6).
                has_submit = any(a.type == "submit" for a in actions) or any(
                    a.type == "submit" for a in snapshot.actions
                )
                report.status = (
                    EngineStatus.STOPPED_BEFORE_SUBMIT
                    if has_submit
                    else EngineStatus.STOPPED_NO_PROGRESSION
                )
                report.screenshot = str(
                    await self._session.capture_screenshot("stopped")
                )
                break

            try:
                progressed, snapshot = await self._session.click_action(next_actions[0])
            except BrowserError as exc:
                logger.warning("Progression click failed: %s", exc.message)
                report.status = EngineStatus.STOPPED_ACTION_FAILED
                break
            if not progressed:
                snapshot = await self._session.inspect_page()
                page_result.validation_errors = snapshot.validation_errors
                report.status = EngineStatus.STOPPED_NO_PROGRESSION
                break
            processed.clear()  # new page, new field namespace

        report.finished_at = datetime.now(UTC)
        return report


def store_execution_report(
    store: PackageStore, manifest: PackageManifest, report: FormExecutionReport
) -> None:
    report.package_id = manifest.package_id
    try:
        store.write_artifact(
            manifest, EXECUTION_REPORT_PATH, report.model_dump_json(indent=2)
        )
        store.save_manifest(manifest)
    except StorageError:
        logger.warning("Could not persist the form execution report.")
