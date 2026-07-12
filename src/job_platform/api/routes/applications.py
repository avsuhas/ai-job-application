"""Application package endpoints (docs/04 Applications API, docs/07A)."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from job_platform.api.deps import AppState, get_state
from job_platform.packages.models import PackageManifest
from job_platform.preparation.service import PreparationOptions
from job_platform.shared.errors import StorageError

router = APIRouter(tags=["applications"])


class PrepareRequest(BaseModel):
    search_id: str
    job_id: str = Field(description="Internal job id from the search results")
    tailor_resume: bool | None = None
    generate_cover_letter: bool | None = None
    include_narrative_answers: bool = True


def _manifest_summary(manifest: PackageManifest) -> dict:
    return {
        "package_id": manifest.package_id,
        "status": manifest.status.value,
        "company": manifest.job.company,
        "title": manifest.job.title,
        "application_url": manifest.job.application_url,
        "match_score": manifest.match_score,
        "recommendation": manifest.recommendation,
        "selected_resume": manifest.selected_resume,
        "cover_letter": manifest.cover_letter,
        "created_at": manifest.created_at,
        "updated_at": manifest.updated_at,
        "attention_items": [item.model_dump() for item in manifest.attention_items],
    }


@router.post("/api/applications/prepare", status_code=201)
async def prepare_application(
    request: PrepareRequest, state: AppState = Depends(get_state)
) -> dict:
    record = state.search_store.load(request.search_id)
    ranked = next((r for r in record.ranked_jobs if r.job.id == request.job_id), None)
    if ranked is None:
        raise StorageError(
            f"Job '{request.job_id}' was not found in search '{request.search_id}'. "
            "Only ranked jobs can be prepared.",
            details={"search_id": request.search_id, "job_id": request.job_id},
        )
    options = PreparationOptions(
        tailor_resume=request.tailor_resume,
        generate_cover_letter=request.generate_cover_letter,
        include_narrative_answers=request.include_narrative_answers,
    )
    manifest = await state.preparation_service().prepare(
        ranked, state.candidate_bundle(), options
    )
    return _manifest_summary(manifest)


@router.get("/api/applications")
def list_applications(state: AppState = Depends(get_state)) -> dict:
    manifests = [
        state.package_store.load_manifest(package_id)
        for package_id in state.package_store.list_package_ids()
    ]
    manifests.sort(key=lambda m: m.created_at, reverse=True)
    return {"count": len(manifests), "applications": [_manifest_summary(m) for m in manifests]}


@router.get("/api/applications/{package_id}")
def get_application(package_id: str, state: AppState = Depends(get_state)) -> dict:
    manifest = state.package_store.load_manifest(package_id)
    stale = state.package_store.stale_sources(manifest, state.candidate_bundle())
    payload = _manifest_summary(manifest)
    payload["artifacts"] = {
        path: record.model_dump() for path, record in sorted(manifest.artifacts.items())
    }
    payload["stale_sources"] = stale
    payload["is_stale"] = bool(stale)
    return payload


@router.get("/api/applications/{package_id}/artifacts/{artifact_path:path}")
def get_artifact(
    package_id: str, artifact_path: str, state: AppState = Depends(get_state)
) -> dict:
    content = state.package_store.read_artifact(package_id, artifact_path)
    return {"package_id": package_id, "path": artifact_path, "content": content}
