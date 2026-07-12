"""End-to-end orchestration tests with real workflows and Chromium against
the Greenhouse fixture (docs/17 Phase 8 acceptance and exit gate)."""

import json

import pytest

from job_platform.ats.greenhouse import default_registry
from job_platform.browser.models import ActionStatus
from job_platform.candidate.loader import load_candidate_bundle
from job_platform.orchestration.admission import QueueAdmissionController
from job_platform.orchestration.locks import LockManager
from job_platform.orchestration.models import (
    QueueItemStatus,
    QueueStatus,
    WorkflowStatus,
)
from job_platform.orchestration.queue import QueueManager
from job_platform.orchestration.workflow import ApplicationWorkflow
from job_platform.packages.store import PackageStore
from job_platform.preparation.service import PreparationService
from job_platform.providers.mock import MockReasoningProvider
from job_platform.readiness.service import ReadinessService
from job_platform.review.service import ReviewService
from job_platform.shared.config import Settings
from job_platform.storage.tracker import ApplicationTracker
from tests.browser.conftest import page_url
from tests.unit.test_review import make_ranked

GH_URL = page_url("greenhouse_application.html")


@pytest.fixture
def orchestration_env(candidate_dir, tmp_path, chromium_available):
    settings = Settings(
        reasoning={"provider": "mock"},
        browser={"headless": True, "default_timeout_ms": 10_000, "max_retries": 1},
        paths={"data_root": tmp_path / "user_data"},
    )
    bundle = load_candidate_bundle(candidate_dir)
    store = PackageStore(settings.paths.packages_dir)
    tracker = ApplicationTracker(settings.paths.tracker_path)
    prep = PreparationService(MockReasoningProvider(), store, settings, tracker=tracker)
    reviewer = ReviewService(store, known_companies=["ExampleCo"])
    readiness = ReadinessService(store, tracker=tracker)
    locks = LockManager(settings.paths.packages_dir, settings.paths.browser_profile_dir)
    return settings, bundle, store, tracker, prep, reviewer, readiness, locks


async def ready_package(prep, reviewer, bundle, **overrides):
    defaults = dict(url=GH_URL, title="Backend Engineer", company="ExampleCo", job_id="")
    defaults.update(overrides)
    manifest = await prep.prepare(make_ranked(**defaults), bundle)
    reviewer.review(manifest, bundle)
    return manifest


def make_workflow(env, manifest, queue_id=""):
    settings, bundle, store, tracker, prep, reviewer, readiness, locks = env
    return ApplicationWorkflow(
        manifest=manifest,
        bundle=bundle,
        store=store,
        provider=MockReasoningProvider(),
        registry=default_registry(),
        readiness=readiness,
        locks=locks,
        settings=settings,
        queue_id=queue_id,
    )


class TestSingleWorkflow:
    async def test_workflow_reaches_waiting_for_review(self, orchestration_env):
        settings, bundle, store, *_ = orchestration_env
        _, _, _, _, prep, reviewer, _, _ = orchestration_env
        manifest = await ready_package(prep, reviewer, bundle)
        state = await make_workflow(orchestration_env, manifest).run()

        assert state.status == WorkflowStatus.WAITING_FOR_REVIEW
        assert state.ats_adapter == "greenhouse"
        assert state.engine_status in ("stopped_before_submit", "ready_for_review")

        # Durable state persisted after every stage
        package_dir = store.package_dir(manifest.package_id)
        persisted = json.loads((package_dir / "execution/state.json").read_text())
        assert persisted["status"] == "waiting_for_review"
        stages = [r["stage"] for r in persisted["stage_results"]]
        assert stages[:3] == ["queue_validation", "package_lock", "pre_execution_readiness"]
        assert "form_execution" in stages
        # Engine report and step state stored in the package
        assert (package_dir / "execution/form_execution_report.json").exists()
        assert (package_dir / "execution/browser_steps.json").exists()
        # Lock released after cleanup
        assert not (package_dir / "execution/package.lock").exists()

    async def test_identity_mismatch_blocks(self, orchestration_env):
        settings, bundle, store, tracker, prep, reviewer, _, _ = orchestration_env
        manifest = await ready_package(
            prep, reviewer, bundle, title="Data Scientist", job_id="99",
        )
        state = await make_workflow(orchestration_env, manifest).run()
        assert state.status == WorkflowStatus.BLOCKED
        identity_stage = next(
            r for r in state.stage_results
            if r.stage.value == "application_identity_check"
        )
        assert "mismatch" in identity_stage.error

    async def test_crash_recovery_skips_completed_actions(self, orchestration_env):
        settings, bundle, store, tracker, prep, reviewer, _, _ = orchestration_env
        manifest = await ready_package(prep, reviewer, bundle)

        first = await make_workflow(orchestration_env, manifest).run()
        assert first.status == WorkflowStatus.WAITING_FOR_REVIEW

        # Simulate a crash: mark the persisted state as still running
        package_dir = store.package_dir(manifest.package_id)
        state_path = package_dir / "execution/state.json"
        crashed = json.loads(state_path.read_text())
        crashed["status"] = "running"
        state_path.write_text(json.dumps(crashed))

        second = await make_workflow(orchestration_env, manifest).run()
        assert second.status == WorkflowStatus.WAITING_FOR_REVIEW
        assert second.attempt_count == crashed["attempt_count"] + 1

        # Completed actions were skipped, not repeated (Phase 8 exit gate)
        report = json.loads(
            (package_dir / "execution/form_execution_report.json").read_text()
        )
        statuses = {
            r["status"]
            for page in report["pages"]
            for r in page["action_results"]
        }
        assert "skipped" in statuses
        assert "failed" not in statuses


class TestQueueEndToEnd:
    def manager(self, env):
        settings, bundle, store, tracker, prep, reviewer, readiness, locks = env

        async def run_workflow(package_id: str, queue_id: str):
            manifest = store.load_manifest(package_id)
            return await make_workflow(env, manifest, queue_id).run()

        admission = QueueAdmissionController(store, readiness, locks)
        return QueueManager(
            settings.paths.queues_dir, store, admission, locks, run_workflow
        )

    async def test_two_packages_execute_sequentially(self, orchestration_env):
        settings, bundle, store, tracker, prep, reviewer, _, _ = orchestration_env
        m1 = await ready_package(prep, reviewer, bundle)
        m2 = await ready_package(
            prep, reviewer, bundle,
            id="job_2", url=page_url("job_page_multi_form.html"),
            title="Backend Engineer", job_id="43",
        )
        manager = self.manager(orchestration_env)
        queue = manager.create([m1.package_id, m2.package_id], bundle)
        assert queue.status == QueueStatus.READY

        finished = await manager.run(queue.queue_id)
        assert finished.status == QueueStatus.COMPLETED
        assert (
            finished.item_for(m1.package_id).status == QueueItemStatus.WAITING_FOR_REVIEW
        )
        assert (
            finished.item_for(m2.package_id).status == QueueItemStatus.WAITING_FOR_REVIEW
        )
        types = [e.event_type for e in manager.events(queue.queue_id)]
        assert types.count("item_finished") == 2

    async def test_package_failure_does_not_stop_queue(self, orchestration_env):
        settings, bundle, store, tracker, prep, reviewer, _, _ = orchestration_env
        broken = await ready_package(
            prep, reviewer, bundle,
            id="job_broken", url=page_url("does_not_exist.html"), job_id="66",
        )
        good = await ready_package(
            prep, reviewer, bundle, id="job_good", job_id="77",
        )
        manager = self.manager(orchestration_env)
        queue = manager.create([broken.package_id, good.package_id], bundle)
        finished = await manager.run(queue.queue_id)

        assert finished.status == QueueStatus.COMPLETED_WITH_ERRORS
        assert finished.item_for(broken.package_id).status == QueueItemStatus.FAILED
        assert (
            finished.item_for(good.package_id).status == QueueItemStatus.WAITING_FOR_REVIEW
        )

    async def test_action_results_all_verified_or_skipped(self, orchestration_env):
        settings, bundle, store, tracker, prep, reviewer, _, _ = orchestration_env
        manifest = await ready_package(prep, reviewer, bundle)
        manager = self.manager(orchestration_env)
        queue = manager.create([manifest.package_id], bundle)
        await manager.run(queue.queue_id)

        report = json.loads(
            store.read_artifact(manifest.package_id, "execution/form_execution_report.json")
        )
        for page in report["pages"]:
            for result in page["action_results"]:
                assert result["status"] in (
                    ActionStatus.SUCCESS.value,
                    ActionStatus.SKIPPED.value,
                )
                assert result["verified"] is True
