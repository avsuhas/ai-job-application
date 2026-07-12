"""Manual submission recording (docs/17 Phase 4).

The user completed the application themselves; this records that fact
accurately: a submission result inside the package (method=manual) and a
tracker row so duplicate detection covers manually-submitted jobs.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime

from job_platform.packages.models import PackageManifest, PackageStatus
from job_platform.packages.store import PackageStore
from job_platform.shared.logging import get_logger
from job_platform.storage.tracker import ApplicationRecord, ApplicationTracker

logger = get_logger("submission.manual")

RESULT_PATH = "submission/result.json"


def record_manual_submission(
    manifest: PackageManifest,
    store: PackageStore,
    tracker: ApplicationTracker,
    notes: str = "",
    resume_used: str = "",
) -> ApplicationRecord:
    """Record a manual submission; raises DuplicateApplicationError if the
    tracker already holds this job."""
    submitted_at = datetime.now(UTC)
    record = ApplicationRecord(
        company=manifest.job.company,
        job_title=manifest.job.title,
        job_id=manifest.job.job_id,
        application_url=manifest.job.application_url,
        date_applied=submitted_at.date().isoformat(),
        resume_used=resume_used or (manifest.selected_resume or ""),
        status="submitted",
        notes=f"manual submission via package {manifest.package_id}"
        + (f" — {notes}" if notes else ""),
    )
    # Tracker first: it enforces duplicate rejection before any state changes.
    tracker.add(record)

    result = {
        "method": "manual",
        "submitted_at": submitted_at.isoformat(),
        "package_id": manifest.package_id,
        "recorded_by": "user",
        "notes": notes,
    }
    store.write_artifact(manifest, RESULT_PATH, json.dumps(result, indent=2))
    manifest.status = PackageStatus.SUBMITTED
    store.save_manifest(manifest)
    logger.info(
        "Manual submission recorded for %s (%s at %s)",
        manifest.package_id,
        manifest.job.title,
        manifest.job.company,
    )
    return record
