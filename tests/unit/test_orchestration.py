"""Unit tests for orchestration: locks, admission, queue manager (docs/08).
Workflows are stubbed — real browser execution is covered in tests/browser."""

import json

import pytest

from job_platform.candidate.loader import load_candidate_bundle
from job_platform.orchestration.admission import QueueAdmissionController, order_items
from job_platform.orchestration.locks import FileLock, LockManager, LockUnavailableError
from job_platform.orchestration.models import (
    AdmissionStatus,
    QueueItem,
    QueueItemStatus,
    QueueStatus,
    WorkflowState,
    WorkflowStatus,
)
from job_platform.orchestration.queue import QueueManager
from job_platform.packages.store import PackageStore
from job_platform.preparation.service import PreparationService
from job_platform.providers.mock import MockReasoningProvider
from job_platform.readiness.service import ReadinessService
from job_platform.review.service import ReviewService
from job_platform.shared.config import Settings
from job_platform.shared.errors import StorageError
from job_platform.storage.tracker import ApplicationRecord, ApplicationTracker
from tests.unit.test_review import make_ranked


@pytest.fixture
def env(candidate_dir, tmp_path):
    bundle = load_candidate_bundle(candidate_dir)
    store = PackageStore(tmp_path / "packages")
    tracker = ApplicationTracker(tmp_path / "tracker.csv")
    prep = PreparationService(MockReasoningProvider(), store, Settings(), tracker=tracker)
    reviewer = ReviewService(store, known_companies=["ExampleCo"])
    readiness = ReadinessService(store, tracker=tracker)
    locks = LockManager(tmp_path / "packages", tmp_path / "profiles")
    admission = QueueAdmissionController(store, readiness, locks)
    return bundle, store, tracker, prep, reviewer, readiness, locks, admission, tmp_path


async def make_ready_package(prep, reviewer, bundle, **job_overrides):
    manifest = await prep.prepare(make_ranked(**job_overrides), bundle)
    reviewer.review(manifest, bundle)
    return manifest


class TestFileLock:
    def test_acquire_and_release(self, tmp_path):
        lock = FileLock(tmp_path / "a.lock")
        with lock:
            assert lock.held
            assert (tmp_path / "a.lock").exists()
        assert not (tmp_path / "a.lock").exists()

    def test_same_process_reacquire_is_reentrant(self, tmp_path):
        first = FileLock(tmp_path / "a.lock")
        first.acquire()
        second = FileLock(tmp_path / "a.lock")
        second.acquire()  # same pid -> allowed
        assert second.held

    def test_foreign_live_lock_blocks(self, tmp_path):
        path = tmp_path / "a.lock"
        path.write_text(json.dumps({"pid": 1, "acquired_at": "2099-01-01T00:00:00+00:00"}))
        with pytest.raises(LockUnavailableError):
            FileLock(path).acquire()

    def test_stale_dead_pid_lock_reclaimed(self, tmp_path):
        path = tmp_path / "a.lock"
        path.write_text(
            json.dumps({"pid": 99999999, "acquired_at": "2020-01-01T00:00:00+00:00"})
        )
        lock = FileLock(path)
        lock.acquire()
        assert lock.held

    def test_corrupt_lock_reclaimed(self, tmp_path):
        path = tmp_path / "a.lock"
        path.write_text("not json")
        lock = FileLock(path)
        lock.acquire()
        assert lock.held


class TestAdmission:
    async def test_ready_reviewed_package_admitted(self, env):
        bundle, store, tracker, prep, reviewer, *_, admission, _ = env
        manifest = await make_ready_package(prep, reviewer, bundle)
        result = admission.evaluate(manifest.package_id, bundle)
        assert result.status == AdmissionStatus.ADMITTED
        assert result.admitted_at is not None

    async def test_unreviewed_package_rejected(self, env):
        bundle, store, tracker, prep, _, _, _, admission, _ = env
        manifest = await prep.prepare(make_ranked(), bundle)
        result = admission.evaluate(manifest.package_id, bundle)
        assert result.status == AdmissionStatus.REJECTED_NOT_READY

    async def test_duplicate_rejected(self, env):
        bundle, store, tracker, prep, reviewer, *_, admission, _ = env
        manifest = await make_ready_package(prep, reviewer, bundle)
        tracker.add(ApplicationRecord.from_job(make_ranked().job))
        result = admission.evaluate(manifest.package_id, bundle)
        assert result.status == AdmissionStatus.REJECTED_DUPLICATE

    async def test_locked_package_rejected(self, env):
        bundle, store, tracker, prep, reviewer, readiness, locks, admission, _ = env
        manifest = await make_ready_package(prep, reviewer, bundle)
        lock_path = (
            store.package_dir(manifest.package_id) / "execution" / "package.lock"
        )
        lock_path.parent.mkdir(parents=True, exist_ok=True)
        lock_path.write_text(
            json.dumps({"pid": 1, "acquired_at": "2099-01-01T00:00:00+00:00"})
        )
        result = admission.evaluate(manifest.package_id, bundle)
        assert result.status == AdmissionStatus.REJECTED_LOCKED

    async def test_prior_submission_unknown_rejected(self, env):
        bundle, store, tracker, prep, reviewer, *_, admission, _ = env
        manifest = await make_ready_package(prep, reviewer, bundle)
        state_path = store.package_dir(manifest.package_id) / "execution" / "state.json"
        state_path.parent.mkdir(parents=True, exist_ok=True)
        state_path.write_text(json.dumps({"status": "submission_unknown"}))
        # register artifact read path via store API
        result = admission.evaluate(manifest.package_id, bundle)
        assert result.status == AdmissionStatus.REJECTED_SUBMISSION_UNKNOWN

    async def test_missing_url_rejected(self, env):
        bundle, store, tracker, prep, reviewer, *_, admission, _ = env
        manifest = await make_ready_package(prep, reviewer, bundle)
        manifest.job.application_url = ""
        store.save_manifest(manifest)
        result = admission.evaluate(manifest.package_id, bundle)
        assert result.status == AdmissionStatus.REJECTED_NO_URL

    def test_ordering_stability(self):
        items = [
            QueueItem(package_id="a", match_score=70),
            QueueItem(package_id="b", match_score=90),
            QueueItem(package_id="c", match_score=90),
            QueueItem(package_id="d", match_score=None),
        ]
        by_match = order_items(items, "highest_match_first")
        assert [i.package_id for i in by_match] == ["b", "c", "a", "d"]  # stable tie
        selected = order_items(items, "selected_order")
        assert [i.package_id for i in selected] == ["a", "b", "c", "d"]


class ScriptedRunner:
    """Stub workflow runner returning scripted statuses per package."""

    def __init__(self, outcomes: dict[str, WorkflowStatus]):
        self.outcomes = outcomes
        self.calls: list[str] = []

    async def __call__(self, package_id: str, queue_id: str) -> WorkflowState:
        self.calls.append(package_id)
        return WorkflowState(
            package_id=package_id,
            queue_id=queue_id,
            status=self.outcomes.get(package_id, WorkflowStatus.WAITING_FOR_REVIEW),
        )


@pytest.fixture
async def two_package_queue(env):
    bundle, store, tracker, prep, reviewer, readiness, locks, admission, tmp = env
    m1 = await make_ready_package(prep, reviewer, bundle)
    m2 = await make_ready_package(
        prep, reviewer, bundle, id="job_2", job_id="43",
        url="https://example.com/jobs/43", title="Platform Engineer",
    )
    def manager(runner):
        return QueueManager(
            tmp / "queues", store, admission, locks, runner
        )
    return bundle, manager, m1, m2


class TestQueueManager:
    async def test_create_admits_ready_packages(self, two_package_queue):
        bundle, manager_for, m1, m2 = two_package_queue
        runner = ScriptedRunner({})
        manager = manager_for(runner)
        queue = manager.create([m1.package_id, m2.package_id], bundle)
        assert queue.status == QueueStatus.READY
        assert all(i.status == QueueItemStatus.ADMITTED for i in queue.items)
        assert [i.position for i in queue.items] == [1, 2]

    async def test_sequential_run_completes_queue(self, two_package_queue):
        bundle, manager_for, m1, m2 = two_package_queue
        runner = ScriptedRunner(
            {
                m1.package_id: WorkflowStatus.WAITING_FOR_REVIEW,
                m2.package_id: WorkflowStatus.WAITING_FOR_REVIEW,
            }
        )
        manager = manager_for(runner)
        queue = manager.create([m1.package_id, m2.package_id], bundle)
        finished = await manager.run(queue.queue_id)
        assert runner.calls == [m1.package_id, m2.package_id]  # sequential, stable
        assert finished.status == QueueStatus.COMPLETED
        assert all(
            i.status == QueueItemStatus.WAITING_FOR_REVIEW for i in finished.items
        )

    async def test_failure_isolated_queue_continues(self, two_package_queue):
        bundle, manager_for, m1, m2 = two_package_queue
        runner = ScriptedRunner(
            {
                m1.package_id: WorkflowStatus.FAILED,
                m2.package_id: WorkflowStatus.WAITING_FOR_REVIEW,
            }
        )
        manager = manager_for(runner)
        queue = manager.create([m1.package_id, m2.package_id], bundle)
        finished = await manager.run(queue.queue_id)
        assert runner.calls == [m1.package_id, m2.package_id]
        assert finished.status == QueueStatus.COMPLETED_WITH_ERRORS
        assert finished.item_for(m1.package_id).status == QueueItemStatus.FAILED
        assert (
            finished.item_for(m2.package_id).status == QueueItemStatus.WAITING_FOR_REVIEW
        )

    async def test_waiting_for_user_pauses_queue(self, two_package_queue):
        bundle, manager_for, m1, m2 = two_package_queue
        runner = ScriptedRunner({m1.package_id: WorkflowStatus.WAITING_FOR_USER})
        manager = manager_for(runner)
        queue = manager.create([m1.package_id, m2.package_id], bundle)
        paused = await manager.run(queue.queue_id)
        assert paused.status == QueueStatus.PAUSED
        assert runner.calls == [m1.package_id]  # second package not started
        assert paused.item_for(m2.package_id).status == QueueItemStatus.ADMITTED

    async def test_workflow_crash_is_isolated(self, two_package_queue):
        bundle, manager_for, m1, m2 = two_package_queue

        class CrashingRunner(ScriptedRunner):
            async def __call__(self, package_id, queue_id):
                if package_id == m1.package_id:
                    raise RuntimeError("boom")
                return await super().__call__(package_id, queue_id)

        runner = CrashingRunner({m2.package_id: WorkflowStatus.WAITING_FOR_REVIEW})
        manager = manager_for(runner)
        queue = manager.create([m1.package_id, m2.package_id], bundle)
        finished = await manager.run(queue.queue_id)
        assert finished.item_for(m1.package_id).status == QueueItemStatus.FAILED
        assert "boom" in finished.item_for(m1.package_id).error
        assert finished.status == QueueStatus.COMPLETED_WITH_ERRORS

    async def test_skip_item(self, two_package_queue):
        bundle, manager_for, m1, m2 = two_package_queue
        runner = ScriptedRunner({})
        manager = manager_for(runner)
        queue = manager.create([m1.package_id, m2.package_id], bundle)
        manager.skip_item(queue.queue_id, m1.package_id)
        finished = await manager.run(queue.queue_id)
        assert runner.calls == [m2.package_id]
        assert finished.item_for(m1.package_id).status == QueueItemStatus.SKIPPED

    async def test_cancel_between_items(self, two_package_queue):
        bundle, manager_for, m1, m2 = two_package_queue

        class CancellingRunner(ScriptedRunner):
            def __init__(self, manager_ref, outcomes):
                super().__init__(outcomes)
                self.manager_ref = manager_ref

            async def __call__(self, package_id, queue_id):
                result = await super().__call__(package_id, queue_id)
                self.manager_ref["m"].request_cancel(queue_id)
                return result

        ref = {}
        runner = CancellingRunner(ref, {m1.package_id: WorkflowStatus.WAITING_FOR_REVIEW})
        manager = manager_for(runner)
        ref["m"] = manager
        queue = manager.create([m1.package_id, m2.package_id], bundle)
        finished = await manager.run(queue.queue_id)
        assert runner.calls == [m1.package_id]
        assert finished.item_for(m2.package_id).status == QueueItemStatus.CANCELLED
        assert finished.status == QueueStatus.CANCELLED

    async def test_events_recorded(self, two_package_queue):
        bundle, manager_for, m1, m2 = two_package_queue
        runner = ScriptedRunner({})
        manager = manager_for(runner)
        queue = manager.create([m1.package_id], bundle)
        await manager.run(queue.queue_id)
        events = manager.events(queue.queue_id)
        types = [e.event_type for e in events]
        assert "queue_created" in types
        assert "item_started" in types
        assert "item_finished" in types
        assert "queue_finished" in types

    async def test_restart_recovery_parks_queue_paused(self, two_package_queue):
        bundle, manager_for, m1, m2 = two_package_queue
        runner = ScriptedRunner({})
        manager = manager_for(runner)
        queue = manager.create([m1.package_id, m2.package_id], bundle)
        # Simulate a crash mid-run: persist running status + executing item
        queue.status = QueueStatus.RUNNING
        queue.items[0].status = QueueItemStatus.EXECUTING
        manager.save(queue)

        recovered = manager.recover_interrupted()
        assert queue.queue_id in recovered
        reloaded = manager.load(queue.queue_id)
        assert reloaded.status == QueueStatus.PAUSED
        assert reloaded.items[0].status == QueueItemStatus.WAITING

        # Resume finishes both items
        finished = await manager.run(queue.queue_id, resume=True)
        assert finished.status == QueueStatus.COMPLETED
        assert runner.calls == [m1.package_id, m2.package_id]

    async def test_running_queue_cannot_be_started_twice(self, two_package_queue):
        bundle, manager_for, m1, _ = two_package_queue
        manager = manager_for(ScriptedRunner({}))
        queue = manager.create([m1.package_id], bundle)
        queue.status = QueueStatus.RUNNING
        manager.save(queue)
        with pytest.raises(StorageError):
            await manager.run(queue.queue_id)
