"""Review-mode end-to-end release test (docs/17 Phase 10 acceptance).

Runs the complete workflow twice: prepare → review → readiness → queue
(review-mode execution) → user approval → submit → verify → history, then
proves the second identical job is blocked as a duplicate. Real Chromium.
"""

import json

import pytest

from job_platform.candidate.loader import load_candidate_bundle
from job_platform.orchestration.admission import QueueAdmissionController
from job_platform.orchestration.locks import LockManager
from job_platform.orchestration.models import QueueItemStatus, QueueStatus, WorkflowStatus
from job_platform.orchestration.queue import QueueManager
from job_platform.orchestration.workflow import ApplicationWorkflow
from job_platform.packages.models import PackageStatus
from job_platform.packages.store import PackageStore
from job_platform.preparation.service import PreparationService
from job_platform.providers.mock import MockReasoningProvider
from job_platform.readiness.service import ReadinessService
from job_platform.review.approval import create_approval, verify_approval
from job_platform.review.service import ReviewService
from job_platform.shared.config import Settings
from job_platform.storage.tracker import ApplicationTracker
from job_platform.submission.history import ApplicationHistoryService
from job_platform.submission.service import SubmissionService
from tests.browser.conftest import page_url
from tests.unit.test_review import make_ranked

GH_URL = page_url("greenhouse_application.html")


@pytest.fixture
def release_env(candidate_dir, tmp_path, chromium_available):
    settings = Settings(
        reasoning={"provider": "mock"},
        browser={"headless": True, "default_timeout_ms": 10_000, "max_retries": 1},
        paths={"data_root": tmp_path / "user_data"},
    )
    bundle = load_candidate_bundle(candidate_dir)
    store = PackageStore(settings.paths.packages_dir)
    tracker = ApplicationTracker(settings.paths.tracker_path)
    history = ApplicationHistoryService(
        tracker, settings.paths.applications_dir / "history_events.jsonl",
        settings.paths.applications_dir / "tracker.xlsx",
    )
    reviewer = ReviewService(store, known_companies=["ExampleCo"])
    readiness = ReadinessService(store, tracker=tracker)
    locks = LockManager(settings.paths.packages_dir, settings.paths.browser_profile_dir)
    prep = PreparationService(MockReasoningProvider(), store, settings, tracker=tracker)
    submission = SubmissionService(store, tracker, history)
    return locals()


def build_workflow(env, manifest, queue_id="", submit=False):
    return ApplicationWorkflow(
        manifest=manifest,
        bundle=env["bundle"],
        store=env["store"],
        provider=MockReasoningProvider(),
        registry=__import__(
            "job_platform.ats.greenhouse", fromlist=["default_registry"]
        ).default_registry(),
        readiness=env["readiness"],
        locks=env["locks"],
        settings=env["settings"],
        queue_id=queue_id,
        submit_mode=submit,
        submission_service=env["submission"] if submit else None,
    )


async def run_full_loop(env, job_id):
    """One complete review-mode loop; returns the final workflow state."""
    store, bundle = env["store"], env["bundle"]
    manifest = await env["prep"].prepare(
        make_ranked(url=GH_URL, title="Backend Engineer", company="ExampleCo",
                    job_id=job_id, id=f"job_{job_id}"),
        bundle,
    )
    env["reviewer"].review(manifest, bundle)

    # Queue admission + review-mode execution through the queue manager
    admission = QueueAdmissionController(store, env["readiness"], env["locks"])

    async def review_runner(package_id, queue_id):
        m = store.load_manifest(package_id)
        return await build_workflow(env, m, queue_id).run()

    manager = QueueManager(
        env["settings"].paths.queues_dir, store, admission, env["locks"], review_runner
    )
    queue = manager.create([manifest.package_id], bundle)
    assert queue.status == QueueStatus.READY
    finished = await manager.run(queue.queue_id)
    assert finished.item_for(manifest.package_id).status == QueueItemStatus.WAITING_FOR_REVIEW

    # User sees the filled form and approves; approval binds artifact versions
    manifest = store.load_manifest(manifest.package_id)
    approval = create_approval(store, manifest)
    assert verify_approval(store, manifest).approval_id == approval.approval_id

    # Submit: approval check → refill → final click → verify → history
    submit_state = await build_workflow(env, manifest, submit=True).run()
    return manifest, submit_state


class TestReviewModeRelease:
    async def test_end_to_end_loop_runs_and_records_history(self, release_env):
        env = release_env
        manifest, state = await run_full_loop(env, job_id="4001")

        assert state.status == WorkflowStatus.SUBMITTED
        # Stages include approval check and final submission
        stages = [r.stage.value for r in state.stage_results]
        assert "user_approval_check" in stages
        assert "final_submission" in stages

        # Submission verified with confirmation number
        result = json.loads(
            env["store"].read_artifact(manifest.package_id, "submission/result.json")
        )
        assert result["confirmation_number"]["value"] == "GH-483726"

        # Application recorded in history (CSV + XLSX + events)
        records = env["tracker"].records()
        assert len(records) == 1
        assert records[0].status == "submitted"
        assert env["history"]._xlsx_path.exists()
        types = [e.event_type for e in env["history"].events(package_id=manifest.package_id)]
        assert "submitted" in types
        assert env["store"].load_manifest(manifest.package_id).status == PackageStatus.SUBMITTED

    async def test_repeated_loop_blocks_duplicate(self, release_env):
        env = release_env
        # First job completes end to end
        await run_full_loop(env, job_id="4001")

        # A second, identical job (same company/title) must be blocked as a
        # duplicate at queue admission — no wrong-company leakage, no dup click.
        manifest2 = await env["prep"].prepare(
            make_ranked(url=GH_URL, title="Backend Engineer", company="ExampleCo",
                        job_id="4001", id="job_dup"),
            env["bundle"],
        )
        assert manifest2.status == PackageStatus.ALREADY_APPLIED

    async def test_submit_without_approval_is_refused(self, release_env):
        env = release_env
        store, bundle = env["store"], env["bundle"]
        manifest = await env["prep"].prepare(
            make_ranked(url=GH_URL, title="Backend Engineer", company="ExampleCo",
                        job_id="5001", id="job_5001"),
            bundle,
        )
        env["reviewer"].review(manifest, bundle)

        async def review_runner(package_id, queue_id):
            return await build_workflow(env, store.load_manifest(package_id), queue_id).run()

        admission = QueueAdmissionController(store, env["readiness"], env["locks"])
        manager = QueueManager(
            env["settings"].paths.queues_dir, store, admission, env["locks"], review_runner
        )
        queue = manager.create([manifest.package_id], bundle)
        await manager.run(queue.queue_id)

        # Submit without ever approving → workflow fails at approval check
        state = await build_workflow(env, store.load_manifest(manifest.package_id),
                                     submit=True).run()
        assert state.status == WorkflowStatus.FAILED
        approval_stage = next(
            r for r in state.stage_results if r.stage.value == "user_approval_check"
        )
        assert "approval" in approval_stage.error.lower()
        # Nothing submitted, no history row
        assert env["tracker"].records() == []
