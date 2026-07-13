"""Application history service (docs/10).

The CSV tracker is the source of truth; the XLSX workbook is a derived view
rebuilt from it on every sync (which also makes a corrupt XLSX recoverable).
Every state change is appended to an immutable event log. Synchronization is
idempotent: syncing the same submission twice changes nothing, and a tracker
failure can never trigger a resubmission — submission truth lives in the
attempt records, not the history files.
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from openpyxl import Workbook
from pydantic import BaseModel, Field

from job_platform.shared.errors import DuplicateApplicationError
from job_platform.shared.ids import new_id
from job_platform.shared.logging import get_logger
from job_platform.storage.tracker import ApplicationRecord, ApplicationTracker

logger = get_logger("submission.history")


class HistoryEvent(BaseModel):
    """docs/10 History Event Model (append-only audit)."""

    event_id: str = Field(default_factory=lambda: new_id("history"))
    package_id: str = ""
    event_type: str
    message: str = ""
    data: dict = Field(default_factory=dict)
    at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class ApplicationHistoryService:
    def __init__(
        self,
        tracker: ApplicationTracker,
        events_path: Path,
        xlsx_path: Path | None = None,
    ) -> None:
        self._tracker = tracker
        self._events_path = events_path
        self._xlsx_path = xlsx_path

    # -- append-only events -------------------------------------------------- #

    def record_event(self, event_type: str, package_id: str = "",
                     message: str = "", data: dict | None = None) -> HistoryEvent:
        event = HistoryEvent(
            package_id=package_id,
            event_type=event_type,
            message=message,
            data=data or {},
        )
        self._events_path.parent.mkdir(parents=True, exist_ok=True)
        with self._events_path.open("a", encoding="utf-8") as handle:
            handle.write(event.model_dump_json() + "\n")
        return event

    def events(self, package_id: str | None = None, limit: int = 200) -> list[HistoryEvent]:
        if not self._events_path.exists():
            return []
        events = [
            HistoryEvent.model_validate_json(line)
            for line in self._events_path.read_text(encoding="utf-8").splitlines()
        ]
        if package_id is not None:
            events = [e for e in events if e.package_id == package_id]
        return events[-limit:]

    # -- idempotent synchronization ------------------------------------------ #

    def sync_submission(self, record: ApplicationRecord, package_id: str = "") -> bool:
        """Record one submitted application idempotently.

        Returns True when the tracker row was added, False when it already
        existed. Failures are logged and re-raised by callers only for
        retryable sync — never to re-run a submission.
        """
        added = True
        try:
            self._tracker.add(record)
        except DuplicateApplicationError:
            added = False  # already synchronized — idempotent no-op
        self.record_event(
            "history_synced" if added else "history_already_synced",
            package_id=package_id,
            message=f"{record.company} — {record.job_title}",
            data={"status": record.status},
        )
        self.rebuild_xlsx()
        return added

    # -- XLSX (derived view; docs/10 XLSX Requirements) ------------------------ #

    def rebuild_xlsx(self) -> Path | None:
        """Regenerate the workbook from the CSV source of truth. Also the
        recovery path for a corrupt workbook."""
        if self._xlsx_path is None:
            return None
        records = self._tracker.records()
        workbook = Workbook()

        sheet = workbook.active
        sheet.title = "Applications"
        headers = [
            "Company", "Job Title", "Job ID", "Application URL", "Date Posted",
            "Date Applied", "Country", "Resume Used", "Status", "Notes",
        ]
        sheet.append(headers)
        for record in records:
            sheet.append([
                record.company, record.job_title, record.job_id,
                record.application_url, record.date_posted, record.date_applied,
                record.country, record.resume_used, record.status, record.notes,
            ])
        for column_cells in sheet.columns:
            width = max((len(str(c.value or "")) for c in column_cells), default=10)
            sheet.column_dimensions[column_cells[0].column_letter].width = min(width + 2, 60)

        summary = workbook.create_sheet("Status Summary")
        summary.append(["Status", "Count"])
        counts: dict[str, int] = {}
        for record in records:
            counts[record.status] = counts.get(record.status, 0) + 1
        for status, count in sorted(counts.items()):
            summary.append([status, count])
        summary.append(["total", len(records)])

        self._xlsx_path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self._xlsx_path.with_suffix(".xlsx.tmp")
        workbook.save(tmp)
        tmp.replace(self._xlsx_path)
        logger.info("Rebuilt XLSX history with %d record(s)", len(records))
        return self._xlsx_path
