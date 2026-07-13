"""Operational endpoints: backups, restore, audit, disk, health, diagnostics
(docs/17 Phases 10–11)."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from job_platform.api.deps import AppState, get_state
from job_platform.operations.audit import verify_event_log
from job_platform.operations.backup import create_backup, list_backups, restore_backup
from job_platform.operations.disk import check_disk
from job_platform.operations.health import diagnostic_bundle, system_health

router = APIRouter(tags=["operations"])


@router.post("/api/system/backup", status_code=201)
def backup(state: AppState = Depends(get_state)) -> dict:
    return create_backup(state.settings).model_dump(mode="json")


@router.get("/api/system/backups")
def backups(state: AppState = Depends(get_state)) -> dict:
    items = list_backups(state.settings)
    return {"count": len(items), "backups": items}


class RestoreRequest(BaseModel):
    backup_name: str


@router.post("/api/system/restore")
def restore(request: RestoreRequest, state: AppState = Depends(get_state)) -> dict:
    result = restore_backup(state.settings, request.backup_name)
    state.candidate_bundle(reload=True)
    return result.model_dump(mode="json")


@router.get("/api/system/audit")
def audit(state: AppState = Depends(get_state)) -> dict:
    report = verify_event_log(
        state.settings.paths.applications_dir / "history_events.jsonl",
        store=state.package_store,
    )
    return report.model_dump()


@router.get("/api/system/disk")
def disk(state: AppState = Depends(get_state)) -> dict:
    return check_disk(state.settings.paths.data_root).model_dump()


@router.get("/api/system/health")
def health(state: AppState = Depends(get_state)) -> dict:
    return system_health(state.settings, state.provider.name).model_dump(mode="json")


@router.get("/api/system/diagnostics")
def diagnostics(state: AppState = Depends(get_state)) -> dict:
    return diagnostic_bundle(state.settings, state.provider.name)
