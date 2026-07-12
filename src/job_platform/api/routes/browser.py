"""Browser subsystem endpoints (docs/06 startup validation)."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from job_platform.api.deps import AppState, get_state
from job_platform.browser.service import check_browser_health

router = APIRouter(tags=["browser"])


@router.get("/api/browser/health")
async def browser_health(state: AppState = Depends(get_state)) -> dict:
    health = await check_browser_health(
        state.settings.paths.browser_profile_dir,
        state.settings.paths.screenshots_dir,
    )
    return health.model_dump()
