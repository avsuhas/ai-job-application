"""ATS adapter endpoints (docs/09 Adapter Registry)."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from job_platform.api.deps import AppState, get_state

router = APIRouter(tags=["ats"])


@router.get("/api/ats/adapters")
def list_adapters(state: AppState = Depends(get_state)) -> list[dict]:
    return [
        adapter.metadata.model_dump(mode="json")
        for adapter in state.ats_registry.list_adapters()
    ]
