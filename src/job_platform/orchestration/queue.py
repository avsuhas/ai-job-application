"""Queue manager (docs/08).

Sequential execution of admitted packages through one browser profile.
Package failures are isolated (the queue continues); user-action pauses stop
the queue; every transition is persisted and emitted as an event so the UI
can poll progress. Restart recovery re-enters interrupted workflows without
repeating completed actions (the workflow and engine own that guarantee).
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from pathlib import Path

from job_platform.candidate.models import CandidateBundle
from job_platform.orchestration.admission import QueueAdmissionController, order_items
from job_platform.orchestration.locks import LockManager
from job_platform.orchestration.models import (
    AdmissionStatus,
    QueueEvent,
    QueueItem,
    QueueItemStatus,
    QueueModel,
    QueueStatus,
    WorkflowState,
    WorkflowStatus,
)
from job_platform.packages.store import PackageStore
from job_platform.shared.errors import StorageError
from job_platform.shared.files import atomic_write_text, ensure_dir
from job_platform.shared.logging import get_logger

logger = get_logger("orchestration.queue")

_WORKFLOW_TO_ITEM = {
    WorkflowStatus.COMPLETED: QueueItemStatus.COMPLETED,
    WorkflowStatus.WAITING_FOR_REVIEW: QueueItemStatus.WAITING_FOR_REVIEW,
    WorkflowStatus.WAITING_FOR_USER: QueueItemStatus.WAITING_FOR_USER,
    WorkflowStatus.BLOCKED: QueueItemStatus.BLOCKED,
    WorkflowStatus.FAILED: QueueItemStatus.FAILED,
    WorkflowStatus.CANCELLED: QueueItemStatus.CANCELLED,
}

# Item states that pause the whole queue (docs/17 Phase 8 MVP policy).
_PAUSING_ITEM_STATUSES = {QueueItemStatus.WAITING_FOR_USER}

WorkflowRunner = Callable[[str, str], Awaitable[WorkflowState]]
"""(package_id, queue_id) -> final WorkflowState"""


class QueueManager:
    def __init__(
        self,
        queues_dir: Path,
        package_store: PackageStore,
        admission: QueueAdmissionController,
        locks: LockManager,
        workflow_runner: WorkflowRunner,
        browser_profile: str = "default",
    ) -> None:
        self._dir = queues_dir
        self._store = package_store
        self._admission = admission
        self._locks = locks
        self._run_workflow = workflow_runner
        self._profile = browser_profile
        self._control: dict[str, str] = {}  # queue_id -> "pause" | "cancel"

    # -- persistence -------------------------------------------------------- #

    def _queue_path(self, queue_id: str) -> Path:
        safe = "".join(c for c in queue_id if c.isalnum() or c == "_")
        return self._dir / f"{safe}.json"

    def save(self, queue: QueueModel) -> None:
        atomic_write_text(self._queue_path(queue.queue_id), queue.model_dump_json(indent=2))

    def load(self, queue_id: str) -> QueueModel:
        path = self._queue_path(queue_id)
        if not path.exists():
            raise StorageError(
                f"Queue '{queue_id}' was not found.", details={"queue_id": queue_id}
            )
        return QueueModel.model_validate_json(path.read_text(encoding="utf-8"))

    def list_queue_ids(self) -> list[str]:
        if not self._dir.exists():
            return []
        return sorted(p.stem for p in self._dir.glob("queue_*.json"))

    def _emit(self, queue: QueueModel, event_type: str, message: str = "",
              package_id: str | None = None) -> QueueEvent:
        event = QueueEvent(
            queue_id=queue.queue_id,
            package_id=package_id,
            event_type=event_type,
            message=message,
        )
        ensure_dir(self._dir)
        events_path = self._dir / f"{queue.queue_id}.events.jsonl"
        with events_path.open("a", encoding="utf-8") as handle:
            handle.write(event.model_dump_json() + "\n")
        logger.info("queue event %s: %s %s", event_type, package_id or "", message)
        return event

    def events(self, queue_id: str, limit: int = 100) -> list[QueueEvent]:
        path = self._dir / f"{queue_id}.events.jsonl"
        if not path.exists():
            return []
        lines = path.read_text(encoding="utf-8").splitlines()[-limit:]
        return [QueueEvent.model_validate_json(line) for line in lines]

    # -- creation and admission -------------------------------------------- #

    def create(
        self,
        package_ids: list[str],
        bundle: CandidateBundle,
        ordering: str = "selected_order",
    ) -> QueueModel:
        queue = QueueModel(ordering=ordering)
        for package_id in package_ids:
            item = QueueItem(package_id=package_id)
            try:
                manifest = self._store.load_manifest(package_id)
                item.match_score = manifest.match_score
            except StorageError:
                pass
            queue.items.append(item)

        queue.items = order_items(queue.items, ordering)
        for position, item in enumerate(queue.items, start=1):
            item.position = position
            admission = self._admission.evaluate(item.package_id, bundle)
            item.admission = admission
            if admission.status == AdmissionStatus.ADMITTED:
                item.status = QueueItemStatus.ADMITTED
            elif admission.status == AdmissionStatus.REJECTED_DUPLICATE:
                item.status = QueueItemStatus.ALREADY_APPLIED
            else:
                item.status = QueueItemStatus.REJECTED
                item.error = "; ".join(admission.reasons)

        queue.status = (
            QueueStatus.READY
            if any(i.status == QueueItemStatus.ADMITTED for i in queue.items)
            else QueueStatus.FAILED
        )
        self.save(queue)
        self._emit(
            queue,
            "queue_created",
            f"{len(queue.items)} item(s), "
            f"{sum(1 for i in queue.items if i.status == QueueItemStatus.ADMITTED)} admitted",
        )
        return queue

    # -- control -------------------------------------------------------------- #

    def request_pause(self, queue_id: str) -> None:
        self._control[queue_id] = "pause"

    def request_cancel(self, queue_id: str) -> None:
        self._control[queue_id] = "cancel"

    def skip_item(self, queue_id: str, package_id: str) -> QueueModel:
        queue = self.load(queue_id)
        item = queue.item_for(package_id)
        if item is None:
            raise StorageError(f"Package '{package_id}' is not in this queue.")
        if item.status == QueueItemStatus.EXECUTING:
            raise StorageError(
                "The package is currently executing and cannot be skipped; "
                "pause the queue first."
            )
        if item.status in (QueueItemStatus.ADMITTED, QueueItemStatus.WAITING):
            item.status = QueueItemStatus.SKIPPED
            self.save(queue)
            self._emit(queue, "item_skipped", package_id=package_id)
        return queue

    # -- execution -------------------------------------------------------------- #

    async def run(self, queue_id: str, resume: bool = False) -> QueueModel:
        queue = self.load(queue_id)
        if queue.status not in (QueueStatus.READY, QueueStatus.PAUSED):
            raise StorageError(
                f"Queue is '{queue.status.value}' and cannot be "
                + ("resumed." if resume else "started.")
            )
        self._control.pop(queue_id, None)
        queue.status = QueueStatus.RUNNING
        self.save(queue)
        self._emit(queue, "queue_resumed" if resume else "queue_started")

        profile_lock = self._locks.profile_lock(self._profile)
        profile_lock.acquire()
        try:
            for item in list(queue.items):
                if item.status not in (
                    QueueItemStatus.ADMITTED,
                    QueueItemStatus.WAITING,
                    QueueItemStatus.RETRY_SCHEDULED,
                ):
                    continue
                control = self._control.get(queue_id)
                if control == "cancel":
                    item.status = QueueItemStatus.CANCELLED
                    self._emit(queue, "item_cancelled", package_id=item.package_id)
                    continue
                if control == "pause":
                    queue.status = QueueStatus.PAUSED
                    self.save(queue)
                    self._emit(queue, "queue_paused")
                    return queue

                item.status = QueueItemStatus.EXECUTING
                self.save(queue)
                self._emit(queue, "item_started", package_id=item.package_id)
                try:
                    state = await self._run_workflow(item.package_id, queue.queue_id)
                    item.workflow_id = state.workflow_id
                    item.engine_status = state.engine_status
                    item.status = _WORKFLOW_TO_ITEM.get(
                        state.status, QueueItemStatus.FAILED
                    )
                    failed_stages = [
                        r.error for r in state.stage_results if r.error
                    ]
                    if item.status == QueueItemStatus.FAILED and failed_stages:
                        item.error = failed_stages[-1]
                except Exception as exc:  # noqa: BLE001 - isolate package failures
                    logger.exception("Workflow crashed for %s", item.package_id)
                    item.status = QueueItemStatus.FAILED
                    item.error = str(exc)
                self.save(queue)
                self._emit(
                    queue,
                    "item_finished",
                    message=item.status.value,
                    package_id=item.package_id,
                )

                if item.status in _PAUSING_ITEM_STATUSES:
                    queue.status = QueueStatus.PAUSED
                    self.save(queue)
                    self._emit(
                        queue,
                        "queue_paused",
                        message=f"waiting for user on {item.package_id}",
                    )
                    return queue
        finally:
            profile_lock.release()

        if self._control.get(queue_id) == "cancel":
            queue.status = QueueStatus.CANCELLED
        elif any(
            i.status in (QueueItemStatus.FAILED, QueueItemStatus.BLOCKED)
            for i in queue.items
        ):
            queue.status = QueueStatus.COMPLETED_WITH_ERRORS
        else:
            queue.status = QueueStatus.COMPLETED
        self.save(queue)
        self._emit(queue, "queue_finished", message=queue.status.value)
        return queue

    # -- restart recovery -------------------------------------------------------- #

    def recover_interrupted(self) -> list[str]:
        """After a process restart, park interrupted queues in Paused so the
        user can resume; interrupted items return to the runnable pool and
        their workflows resume from durable state (docs/08)."""
        recovered = []
        for queue_id in self.list_queue_ids():
            queue = self.load(queue_id)
            if queue.status != QueueStatus.RUNNING:
                continue
            for item in queue.items:
                if item.status == QueueItemStatus.EXECUTING:
                    item.status = QueueItemStatus.WAITING
            queue.status = QueueStatus.PAUSED
            self.save(queue)
            self._emit(queue, "queue_recovered", "interrupted by restart; paused")
            recovered.append(queue_id)
        return recovered
