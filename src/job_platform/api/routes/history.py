"""Application history endpoints (FR-061..FR-064)."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from job_platform.api.deps import AppState, get_state
from job_platform.storage.tracker import ApplicationRecord

router = APIRouter(tags=["history"])


@router.get("/api/history")
def list_history(state: AppState = Depends(get_state)) -> dict:
    records = state.tracker.records()
    return {
        "count": len(records),
        "tracker_path": str(state.settings.paths.tracker_path),
        "applications": [record.model_dump() for record in records],
    }


@router.post("/api/history", status_code=201)
def record_application(record: ApplicationRecord, state: AppState = Depends(get_state)) -> dict:
    """Record a (manually or automatically) submitted application.

    Duplicate submissions are rejected with 409.
    """
    state.tracker.add(record)
    return {"recorded": True, "company": record.company, "job_title": record.job_title}


@router.get("/api/history/export")
def export_history(state: AppState = Depends(get_state)) -> dict:
    """Rebuild the XLSX workbook from the CSV source of truth (docs/10)."""
    path = state.history_service().rebuild_xlsx()
    return {"format": "xlsx", "path": str(path), "records": len(state.tracker.records())}


@router.get("/api/history/events")
def history_events(
    package_id: str | None = None, state: AppState = Depends(get_state)
) -> dict:
    events = state.history_service().events(package_id=package_id)
    return {"count": len(events), "events": [e.model_dump(mode="json") for e in events]}
