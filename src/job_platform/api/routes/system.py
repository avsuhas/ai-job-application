"""System endpoints: health and non-secret settings."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from job_platform.api.deps import AppState, get_state
from job_platform.version import __version__

router = APIRouter(tags=["system"])


@router.get("/api/health")
def health(state: AppState = Depends(get_state)) -> dict:
    return {
        "status": "ok",
        "version": __version__,
        "provider": state.provider.name,
        "companies_configured": len(state.companies),
    }


@router.get("/api/settings")
def get_settings(state: AppState = Depends(get_state)) -> dict:
    settings = state.settings
    # Never expose secrets through the API.
    return settings.model_dump(mode="json", exclude={"anthropic_api_key"})
