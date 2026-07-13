"""User approval bound to exact artifact versions (docs/17 Phase 10).

An approval captures the fingerprints of every package artifact plus the
form-execution report hash at approval time. Final submission verifies these
fingerprints again immediately before submitting — if anything changed after
the user approved, the approval is stale and submission refuses.
"""

from __future__ import annotations

from datetime import UTC, datetime

from pydantic import BaseModel, Field

from job_platform.orchestration.workflow import read_workflow_state
from job_platform.packages.models import PackageManifest
from job_platform.packages.store import PackageStore
from job_platform.shared.errors import JobPlatformError, StorageError
from job_platform.shared.files import atomic_write_text
from job_platform.shared.ids import new_id, sha256_text

APPROVAL_PATH = "review/approval.json"
EXECUTION_REPORT_PATH = "execution/form_execution_report.json"

_APPROVABLE_ENGINE_STATUSES = ("stopped_before_submit", "ready_for_review")


class ApprovalError(JobPlatformError):
    code = "approval_error"


class ApprovalRecord(BaseModel):
    approval_id: str = Field(default_factory=lambda: new_id("approval"))
    package_id: str
    workflow_id: str = ""
    approved_by: str = "user"
    engine_status: str = ""
    artifact_fingerprints: dict[str, str] = Field(default_factory=dict)
    form_report_hash: str = ""
    approved_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


def _current_fingerprints(manifest: PackageManifest) -> dict[str, str]:
    # Exclude artifacts that are either derived after approval (readiness,
    # manual handoff, the approval record itself) or bound separately — the
    # form execution report is verified by its own hash below.
    return {
        path: record.sha256
        for path, record in manifest.artifacts.items()
        if not path.startswith(("review/approval", "readiness/", "manual/", "execution/"))
    }


def create_approval(
    store: PackageStore, manifest: PackageManifest, approved_by: str = "user"
) -> ApprovalRecord:
    """Approve the package for final submission (docs/17: approval is bound
    to the form snapshot the user actually reviewed)."""
    state = read_workflow_state(store, manifest.package_id)
    if state is None or state.status.value != "waiting_for_review":
        raise ApprovalError(
            "Approval requires a completed review-mode execution "
            "(status waiting_for_review); run the application first.",
            details={"package_id": manifest.package_id},
        )
    if state.engine_status not in _APPROVABLE_ENGINE_STATUSES:
        raise ApprovalError(
            f"The last execution ended with '{state.engine_status}', which is "
            "not an approvable state.",
            details={"package_id": manifest.package_id},
        )
    try:
        report_text = store.read_artifact(manifest.package_id, EXECUTION_REPORT_PATH)
    except StorageError as exc:
        raise ApprovalError(
            "No form execution report exists to approve.",
            details={"package_id": manifest.package_id},
        ) from exc

    approval = ApprovalRecord(
        package_id=manifest.package_id,
        workflow_id=state.workflow_id,
        approved_by=approved_by,
        engine_status=state.engine_status,
        artifact_fingerprints=_current_fingerprints(manifest),
        form_report_hash=sha256_text(report_text),
    )
    atomic_write_text(
        store.package_dir(manifest.package_id) / APPROVAL_PATH,
        approval.model_dump_json(indent=2),
    )
    return approval


def load_approval(store: PackageStore, package_id: str) -> ApprovalRecord | None:
    path = store.package_dir(package_id) / APPROVAL_PATH
    if not path.exists():
        return None
    return ApprovalRecord.model_validate_json(path.read_text(encoding="utf-8"))


def verify_approval(store: PackageStore, manifest: PackageManifest) -> ApprovalRecord:
    """Confirm the approval is present and still matches the artifacts —
    called immediately before final submission."""
    approval = load_approval(store, manifest.package_id)
    if approval is None:
        raise ApprovalError(
            "Final submission requires user approval; approve the reviewed "
            "application first.",
            details={"package_id": manifest.package_id},
        )
    current = _current_fingerprints(manifest)
    changed = sorted(
        path
        for path in set(approval.artifact_fingerprints) | set(current)
        if approval.artifact_fingerprints.get(path) != current.get(path)
    )
    if changed:
        raise ApprovalError(
            "Package artifacts changed after approval; review and approve "
            f"again. Changed: {', '.join(changed[:5])}",
            details={"package_id": manifest.package_id, "changed": changed},
        )
    try:
        report_text = store.read_artifact(manifest.package_id, EXECUTION_REPORT_PATH)
    except StorageError as exc:
        raise ApprovalError(
            "The approved form execution report is missing.",
            details={"package_id": manifest.package_id},
        ) from exc
    if sha256_text(report_text) != approval.form_report_hash:
        raise ApprovalError(
            "The form execution report changed after approval; review and "
            "approve again.",
            details={"package_id": manifest.package_id},
        )
    return approval


def revoke_approval(store: PackageStore, package_id: str) -> None:
    (store.package_dir(package_id) / APPROVAL_PATH).unlink(missing_ok=True)
