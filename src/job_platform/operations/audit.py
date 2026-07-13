"""Audit-trail integrity checks (docs/17 Phase 10; hash chains arrive with
Phase 11).

Verifies the append-only history event log: every line parses, timestamps
are monotonically non-decreasing, event ids are unique, and every referenced
package still resolves to a manifest on disk.
"""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, Field

from job_platform.packages.store import PackageStore
from job_platform.submission.history import HistoryEvent


class AuditReport(BaseModel):
    ok: bool = True
    events_checked: int = 0
    issues: list[str] = Field(default_factory=list)


def verify_event_log(events_path: Path, store: PackageStore | None = None) -> AuditReport:
    report = AuditReport()
    if not events_path.exists():
        return report  # an empty audit trail is trivially consistent

    seen_ids: set[str] = set()
    last_timestamp = None
    for line_number, line in enumerate(
        events_path.read_text(encoding="utf-8").splitlines(), start=1
    ):
        try:
            event = HistoryEvent.model_validate_json(line)
        except ValueError:
            report.issues.append(f"Line {line_number} is not a valid history event.")
            continue
        report.events_checked += 1
        if event.event_id in seen_ids:
            report.issues.append(
                f"Line {line_number}: duplicate event id {event.event_id}."
            )
        seen_ids.add(event.event_id)
        if last_timestamp is not None and event.at < last_timestamp:
            report.issues.append(
                f"Line {line_number}: timestamp goes backwards "
                f"({event.at.isoformat()} after {last_timestamp.isoformat()})."
            )
        last_timestamp = event.at
        if store is not None and event.package_id:
            manifest_path = store.package_dir(event.package_id) / "package.json"
            if not manifest_path.exists():
                report.issues.append(
                    f"Line {line_number}: package {event.package_id} no longer exists."
                )

    report.ok = not report.issues
    return report
