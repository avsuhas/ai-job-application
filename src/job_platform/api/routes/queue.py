"""Queue orchestration endpoints (docs/08).

POST /api/queue creates a queue with admission results. Running executes
sequentially through the local browser; ``wait=true`` blocks (tests/scripts),
otherwise the run continues in the background and clients poll GET.
"""

from __future__ import annotations

import asyncio

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field

from job_platform.api.deps import AppState, get_state
from job_platform.orchestration.models import QueueModel
from job_platform.shared.logging import get_logger

router = APIRouter(tags=["queue"])
logger = get_logger("api.queue")

_background_tasks: set[asyncio.Task] = set()


class QueueCreateRequest(BaseModel):
    package_ids: list[str] = Field(min_length=1)
    ordering: str = Field(default="selected_order",
                          pattern="^(selected_order|highest_match_first)$")


def _queue_payload(queue: QueueModel, state: AppState) -> dict:
    payload = queue.model_dump(mode="json")
    payload["events"] = [
        e.model_dump(mode="json")
        for e in state.queue_manager().events(queue.queue_id, limit=50)
    ]
    return payload


@router.post("/api/queue", status_code=201)
def create_queue(request: QueueCreateRequest, state: AppState = Depends(get_state)) -> dict:
    queue = state.queue_manager().create(
        request.package_ids, state.candidate_bundle(), request.ordering
    )
    return _queue_payload(queue, state)


@router.get("/api/queue")
def list_queues(state: AppState = Depends(get_state)) -> dict:
    manager = state.queue_manager()
    queues = [manager.load(queue_id) for queue_id in manager.list_queue_ids()]
    queues.sort(key=lambda q: q.created_at, reverse=True)
    return {
        "count": len(queues),
        "queues": [q.model_dump(mode="json") for q in queues],
    }


@router.get("/api/queue/{queue_id}")
def get_queue(queue_id: str, state: AppState = Depends(get_state)) -> dict:
    return _queue_payload(state.queue_manager().load(queue_id), state)


@router.post("/api/queue/{queue_id}/run")
async def run_queue(
    queue_id: str,
    wait: bool = Query(default=False),
    resume: bool = Query(default=False),
    state: AppState = Depends(get_state),
) -> dict:
    manager = state.queue_manager()
    if wait:
        queue = await manager.run(queue_id, resume=resume)
        return _queue_payload(queue, state)
    manager.load(queue_id)  # validate existence before backgrounding

    async def _run() -> None:
        try:
            await manager.run(queue_id, resume=resume)
        except Exception:  # noqa: BLE001 - background failures land in events/log
            logger.exception("Queue run failed for %s", queue_id)

    task = asyncio.create_task(_run())
    _background_tasks.add(task)
    task.add_done_callback(_background_tasks.discard)
    return {"queue_id": queue_id, "status": "running"}


@router.post("/api/queue/{queue_id}/pause")
def pause_queue(queue_id: str, state: AppState = Depends(get_state)) -> dict:
    manager = state.queue_manager()
    manager.load(queue_id)
    manager.request_pause(queue_id)
    return {"queue_id": queue_id, "pause_requested": True}


@router.post("/api/queue/{queue_id}/cancel")
def cancel_queue(queue_id: str, state: AppState = Depends(get_state)) -> dict:
    manager = state.queue_manager()
    manager.load(queue_id)
    manager.request_cancel(queue_id)
    return {"queue_id": queue_id, "cancel_requested": True}


@router.post("/api/queue/{queue_id}/items/{package_id}/skip")
def skip_item(
    queue_id: str, package_id: str, state: AppState = Depends(get_state)
) -> dict:
    queue = state.queue_manager().skip_item(queue_id, package_id)
    return _queue_payload(queue, state)
