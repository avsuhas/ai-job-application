"""Job deduplication (FR-017, FR-063).

Comparison order: external job id → application URL → company+title+location.
The first occurrence wins; later duplicates are dropped.
"""

from __future__ import annotations

from job_platform.jobs.models import Job
from job_platform.shared.ids import stable_hash


def _keys(job: Job) -> list[str]:
    keys = []
    if job.job_id:
        keys.append(f"jid:{job.company.lower()}:{job.job_id.lower()}")
    if job.url:
        keys.append(f"url:{job.url.lower().rstrip('/')}")
    keys.append("ctl:" + stable_hash(job.company, job.title, job.location))
    return keys


def deduplicate(jobs: list[Job]) -> list[Job]:
    seen: set[str] = set()
    unique: list[Job] = []
    for job in jobs:
        keys = _keys(job)
        if any(key in seen for key in keys):
            continue
        seen.update(keys)
        unique.append(job)
    return unique
