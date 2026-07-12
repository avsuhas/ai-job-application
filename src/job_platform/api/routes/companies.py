"""Company source endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from job_platform.api.deps import AppState, get_state
from job_platform.jobs.sources import detect_ats

router = APIRouter(tags=["companies"])


@router.get("/api/companies")
def list_companies(state: AppState = Depends(get_state)) -> list[dict]:
    result = []
    for source in state.companies:
        ats, _ = detect_ats(source.career_url)
        payload = source.model_dump()
        payload["detected_ats"] = ats or source.expected_ats or "unsupported"
        result.append(payload)
    return result
