"""Application package endpoints (docs/04 Applications API, docs/07A-07D)."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from job_platform.api.deps import AppState, get_state
from job_platform.packages.models import PackageManifest
from job_platform.preparation.answers import edit_prepared_answer
from job_platform.preparation.service import PreparationOptions
from job_platform.readiness.handoff import build_manual_completion_package
from job_platform.readiness.models import ReadinessStage
from job_platform.shared.errors import StorageError
from job_platform.submission.manual import record_manual_submission

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


# --- Phase 4: review, readiness, manual handoff (docs/07D) ----------------- #


@router.post("/api/applications/{package_id}/review")
def run_review(package_id: str, state: AppState = Depends(get_state)) -> dict:
    manifest = state.package_store.load_manifest(package_id)
    report = state.review_service().review(manifest, state.candidate_bundle())
    return report.model_dump(mode="json")


@router.get("/api/applications/{package_id}/review")
def get_review(package_id: str, state: AppState = Depends(get_state)) -> dict:
    import json

    content = state.package_store.read_artifact(package_id, "review/review_report.json")
    return json.loads(content)


@router.post("/api/applications/{package_id}/readiness")
def evaluate_readiness(
    package_id: str,
    stage: ReadinessStage = ReadinessStage.MANUAL_COMPLETION,
    state: AppState = Depends(get_state),
) -> dict:
    manifest = state.package_store.load_manifest(package_id)
    report = state.readiness_service().evaluate(manifest, state.candidate_bundle(), stage)
    return report.model_dump(mode="json")


@router.get("/api/applications/{package_id}/manual-package")
def get_manual_package(package_id: str, state: AppState = Depends(get_state)) -> dict:
    manifest = state.package_store.load_manifest(package_id)
    package = build_manual_completion_package(manifest, state.package_store)
    payload = package.model_dump(mode="json")
    payload["markdown"] = package.render()
    return payload


class AnswerEdit(BaseModel):
    answer: str
    question: str = ""
    save_for_reuse: bool = False


@router.put("/api/applications/{package_id}/answers/{answer_id}")
def edit_answer(
    package_id: str,
    answer_id: str,
    edit: AnswerEdit,
    state: AppState = Depends(get_state),
) -> dict:
    manifest = state.package_store.load_manifest(package_id)
    edited = edit_prepared_answer(
        state.package_store,
        manifest,
        answer_id,
        edit.answer,
        question=edit.question,
        save_for_reuse=edit.save_for_reuse,
        candidate_profile_dir=state.settings.paths.profile_dir,
    )
    if edit.save_for_reuse:
        state.candidate_bundle(reload=True)
    return edited.model_dump(mode="json")


class ManualSubmission(BaseModel):
    notes: str = ""


class ApprovalRequest(BaseModel):
    approved_by: str = "user"


@router.post("/api/applications/{package_id}/approve", status_code=201)
def approve_application(
    package_id: str,
    request: ApprovalRequest,
    state: AppState = Depends(get_state),
) -> dict:
    from job_platform.review.approval import create_approval

    manifest = state.package_store.load_manifest(package_id)
    approval = create_approval(state.package_store, manifest, request.approved_by)
    return approval.model_dump(mode="json")


@router.delete("/api/applications/{package_id}/approve")
def revoke_application_approval(
    package_id: str, state: AppState = Depends(get_state)
) -> dict:
    from job_platform.review.approval import revoke_approval

    state.package_store.load_manifest(package_id)
    revoke_approval(state.package_store, package_id)
    return {"package_id": package_id, "approval_revoked": True}


@router.post("/api/applications/{package_id}/submit")
async def submit_application(
    package_id: str, state: AppState = Depends(get_state)
) -> dict:
    """Run the approved-submission workflow: approval check → refill →
    final click → verification → history (docs/17 Phase 10)."""
    state.package_store.load_manifest(package_id)
    workflow_state = await state.run_submission_workflow(package_id)
    return {
        "package_id": package_id,
        "workflow_id": workflow_state.workflow_id,
        "status": workflow_state.status.value,
        "engine_status": workflow_state.engine_status,
        "errors": [r.error for r in workflow_state.stage_results if r.error],
    }


@router.get("/api/applications/{package_id}/submission")
def get_submission_status(package_id: str, state: AppState = Depends(get_state)) -> dict:
    from job_platform.submission.service import submission_status

    state.package_store.load_manifest(package_id)  # 404 on unknown package
    return submission_status(
        state.package_store, state.submission_service(), package_id
    )


class UnknownResolutionRequest(BaseModel):
    resolved_status: str = Field(
        pattern="^(submitted|failed|already_applied|application_closed)$"
    )
    resolution_source: str = "user_confirmation"
    notes: str = ""


@router.post("/api/applications/{package_id}/submission/resolve")
def resolve_submission_unknown(
    package_id: str,
    request: UnknownResolutionRequest,
    state: AppState = Depends(get_state),
) -> dict:
    from job_platform.submission.models import SubmissionOutcome

    manifest = state.package_store.load_manifest(package_id)
    resolution = state.submission_service().resolve_unknown(
        manifest,
        SubmissionOutcome(request.resolved_status),
        request.resolution_source,
        notes=request.notes,
    )
    return resolution.model_dump(mode="json")


@router.post("/api/applications/{package_id}/mark-submitted", status_code=201)
def mark_submitted(
    package_id: str,
    submission: ManualSubmission,
    state: AppState = Depends(get_state),
) -> dict:
    manifest = state.package_store.load_manifest(package_id)
    record = record_manual_submission(
        manifest, state.package_store, state.tracker, notes=submission.notes
    )
    return {
        "recorded": True,
        "package_id": package_id,
        "status": "submitted",
        "tracker_record": record.model_dump(),
    }
