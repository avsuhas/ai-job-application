"""End-to-end submission tests over local fixtures with real Chromium
(docs/17 Phase 9 acceptance and the Submission Safety Gate)."""

import json

import pytest

from job_platform.ats.greenhouse import GreenhouseAdapter
from job_platform.candidate.loader import load_candidate_bundle
from job_platform.forms.engine import GenericFormEngine
from job_platform.orchestration.admission import QueueAdmissionController
from job_platform.orchestration.locks import LockManager
from job_platform.orchestration.models import AdmissionStatus
from job_platform.packages.models import PackageStatus
from job_platform.packages.store import PackageStore
from job_platform.preparation.service import PreparationService
from job_platform.providers.mock import MockReasoningProvider
from job_platform.readiness.service import ReadinessService
from job_platform.review.service import ReviewService
from job_platform.shared.config import Settings
from job_platform.storage.tracker import ApplicationTracker
from job_platform.submission.history import ApplicationHistoryService
from job_platform.submission.models import AttemptStatus
from job_platform.submission.service import SubmissionBlockedError, SubmissionService
from tests.browser.conftest import page_url
from tests.browser.test_form_engine import ANSWERS, RESUME_PATH
from tests.unit.test_review import make_ranked


@pytest.fixture
async def submission_env(candidate_dir, tmp_path, chromium_available):
    settings = Settings(reasoning={"provider": "mock"})
    bundle = load_candidate_bundle(candidate_dir)
    store = PackageStore(tmp_path / "packages")
    tracker = ApplicationTracker(tmp_path / "tracker.csv")
    history = ApplicationHistoryService(
        tracker, tmp_path / "history_events.jsonl", tmp_path / "tracker.xlsx"
    )
    prep = PreparationService(MockReasoningProvider(), store, settings, tracker=tracker)
    service = SubmissionService(store, tracker, history)
    return bundle, store, tracker, history, prep, service


async def prepare_and_fill(session, prep, bundle, url):
    manifest = await prep.prepare(
        make_ranked(url=url, title="Backend Engineer", company="ExampleCo", job_id=""),
        bundle,
    )
    snapshot = await session.open_page(url)
    engine = GenericFormEngine(
        session, MockReasoningProvider(), ANSWERS,
        documents={"documents.resume": RESUME_PATH},
        adapter=GreenhouseAdapter(),
    )
    await engine.run_review_mode(snapshot)
    return manifest, await session.inspect_page()


class TestVerifiedSubmission:
    async def test_full_submission_with_confirmation_number(
        self, session, submission_env
    ):
        bundle, store, tracker, history, prep, service = submission_env
        manifest, snapshot = await prepare_and_fill(
            session, prep, bundle, page_url("greenhouse_application.html")
        )
        attempt = await service.submit(
            session, manifest, snapshot,
            adapter=GreenhouseAdapter(), approved=True,
        )

        assert attempt.status == AttemptStatus.SUBMITTED
        verification = attempt.verification_result
        assert verification.outcome.value == "submitted"
        assert verification.confidence >= 95
        assert verification.confirmation_number.value == "GH-483726"
        assert verification.job_identity_verified

        # Durable artifacts: snapshot, attempt, result; lock released
        package_dir = store.package_dir(manifest.package_id)
        assert (package_dir / "submission/pre_submission_snapshot.json").exists()
        assert (package_dir / "submission/attempts/submission_attempt_001.json").exists()
        result = json.loads((package_dir / "submission/result.json").read_text())
        assert result["confirmation_number"]["value"] == "GH-483726"
        assert not (package_dir / "submission/.submission.lock").exists()

        # History synced idempotently: CSV row + XLSX workbook
        assert len(tracker.records()) == 1
        assert tracker.records()[0].status == "submitted"
        assert (history._xlsx_path).exists()
        assert store.load_manifest(manifest.package_id).status == PackageStatus.SUBMITTED

    async def test_second_submit_blocked_after_success(self, session, submission_env):
        bundle, store, tracker, history, prep, service = submission_env
        manifest, snapshot = await prepare_and_fill(
            session, prep, bundle, page_url("greenhouse_application.html")
        )
        await service.submit(
            session, manifest, snapshot, adapter=GreenhouseAdapter(), approved=True
        )
        with pytest.raises(SubmissionBlockedError):
            await service.submit(
                session, manifest, snapshot, adapter=GreenhouseAdapter(), approved=True
            )
        # Exactly one click, one attempt, one tracker row — idempotency gate
        attempts = service.load_attempts(manifest.package_id)
        assert len(attempts) == 1
        assert len(tracker.records()) == 1


class TestWeakEvidence:
    async def test_weak_redirect_becomes_submission_unknown(
        self, session, submission_env
    ):
        bundle, store, tracker, history, prep, service = submission_env
        manifest, snapshot = await prepare_and_fill(
            session, prep, bundle, page_url("weak_submit.html")
        )
        attempt = await service.submit(
            session, manifest, snapshot, adapter=GreenhouseAdapter(), approved=True
        )

        assert attempt.status == AttemptStatus.SUBMISSION_UNKNOWN
        unknown = service.load_unknown_outcome(manifest.package_id)
        assert unknown is not None
        assert unknown.automatic_retry_allowed is False
        # No tracker row: submission truth was not established
        assert tracker.records() == []
        # The submission lock is intentionally preserved
        package_dir = store.package_dir(manifest.package_id)
        assert (package_dir / "submission/.submission.lock").exists()

    async def test_unknown_blocks_new_attempt_and_queue_admission(
        self, session, submission_env, tmp_path
    ):
        bundle, store, tracker, history, prep, service = submission_env
        manifest, snapshot = await prepare_and_fill(
            session, prep, bundle, page_url("weak_submit.html")
        )
        await service.submit(
            session, manifest, snapshot, adapter=GreenhouseAdapter(), approved=True
        )

        # Never a second click while unknown (docs/10: crash/unknown never retries)
        with pytest.raises(SubmissionBlockedError) as excinfo:
            await service.submit(
                session, manifest, snapshot, adapter=GreenhouseAdapter(), approved=True
            )
        assert "Submission Unknown" in excinfo.value.message
        assert len(service.load_attempts(manifest.package_id)) == 1

        # Queue admission rejects the package until resolved
        reviewer = ReviewService(store, known_companies=["ExampleCo"])
        reviewer.review(manifest, bundle)
        readiness = ReadinessService(store, tracker=tracker)
        locks = LockManager(tmp_path / "packages", tmp_path / "profiles")
        admission = QueueAdmissionController(store, readiness, locks)
        result = admission.evaluate(manifest.package_id, bundle)
        assert result.status == AdmissionStatus.REJECTED_SUBMISSION_UNKNOWN

    async def test_unknown_resolution_reopens_or_records(
        self, session, submission_env
    ):
        from job_platform.submission.models import SubmissionOutcome

        bundle, store, tracker, history, prep, service = submission_env
        manifest, snapshot = await prepare_and_fill(
            session, prep, bundle, page_url("weak_submit.html")
        )
        await service.submit(
            session, manifest, snapshot, adapter=GreenhouseAdapter(), approved=True
        )
        service.resolve_unknown(
            manifest, SubmissionOutcome.SUBMITTED, "ats_dashboard",
            notes="dashboard shows Submitted",
        )
        assert service.load_unknown_outcome(manifest.package_id) is None
        assert len(tracker.records()) == 1
        assert store.load_manifest(manifest.package_id).status == PackageStatus.SUBMITTED
