"""Operational endpoints: backups and audit integrity (docs/17 Phase 10)."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from job_platform.api.deps import AppState, get_state
from job_platform.operations.audit import verify_event_log
from job_platform.operations.backup import create_backup, list_backups

router = APIRouter(tags=["operations"])


@router.post("/api/system/backup", status_code=201)
def backup(state: AppState = Depends(get_state)) -> dict:
    return create_backup(state.settings).model_dump(mode="json")


@router.get("/api/system/backups")
def backups(state: AppState = Depends(get_state)) -> dict:
    items = list_backups(state.settings)
    return {"count": len(items), "backups": items}


@router.get("/api/system/audit")
def audit(state: AppState = Depends(get_state)) -> dict:
    report = verify_event_log(
        state.settings.paths.applications_dir / "history_events.jsonl",
        store=state.package_store,
    )
    return report.model_dump()
