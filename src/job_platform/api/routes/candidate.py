"""Candidate Knowledge Base endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from job_platform.api.deps import AppState, get_state
from job_platform.candidate.validator import validate_candidate_dir

router = APIRouter(tags=["candidate"])


def _status_payload(state: AppState) -> dict:
    report = validate_candidate_dir(state.settings.paths.candidate_dir)
    bundle = state.candidate_bundle() if report.ok else None
    return {
        "ok": report.ok,
        "errors": [issue.model_dump() for issue in report.errors],
        "warnings": [issue.model_dump() for issue in report.warnings],
        "resumes": (
            [
                {"id": r.id, "name": r.name, "format": r.format, "has_text": bool(r.text)}
                for r in bundle.resumes
            ]
            if bundle
            else []
        ),
        "documents": sorted(bundle.documents) if bundle else [],
    }


@router.get("/api/candidate/status")
def candidate_status(state: AppState = Depends(get_state)) -> dict:
    return _status_payload(state)


@router.post("/api/candidate/reload")
def candidate_reload(state: AppState = Depends(get_state)) -> dict:
    state.candidate_bundle(reload=True)
    return _status_payload(state)
