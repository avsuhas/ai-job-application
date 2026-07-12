"""Local application history tracker (FR-061..FR-064).

A plain CSV the user can open in Excel, Google Sheets, or LibreOffice.
Duplicates are checked in the order job id → URL → company+title+location
(FR-063). Writes are atomic so a crash cannot corrupt the history.
"""

from __future__ import annotations

import csv
import io
from datetime import UTC, datetime
from pathlib import Path

from pydantic import BaseModel, Field

from job_platform.jobs.models import Job
from job_platform.shared.errors import DuplicateApplicationError
from job_platform.shared.files import atomic_write_text
from job_platform.shared.ids import stable_hash

COLUMNS = [
    "company",
    "job_title",
    "job_id",
    "application_url",
    "date_posted",
    "date_applied",
    "country",
    "resume_used",
    "status",
    "notes",
]


class ApplicationRecord(BaseModel):
    company: str
    job_title: str
    job_id: str = ""
    application_url: str = ""
    date_posted: str = ""
    date_applied: str = Field(
        default_factory=lambda: datetime.now(UTC).date().isoformat()
    )
    country: str = ""
    resume_used: str = ""
    status: str = "submitted"
    notes: str = ""

    @classmethod
    def from_job(cls, job: Job, resume_used: str = "", status: str = "submitted") -> ApplicationRecord:
        return cls(
            company=job.company,
            job_title=job.title,
            job_id=job.job_id,
            application_url=job.url,
            date_posted=job.date_posted.date().isoformat() if job.date_posted else "",
            country=job.country,
            resume_used=resume_used,
            status=status,
        )


def _duplicate_keys(company: str, title: str, location_or_country: str, job_id: str, url: str) -> list[str]:
    keys = []
    if job_id:
        keys.append(f"jid:{company.lower()}:{job_id.lower()}")
    if url:
        keys.append(f"url:{url.lower().rstrip('/')}")
    keys.append("ctl:" + stable_hash(company, title, location_or_country))
    return keys


class ApplicationTracker:
    def __init__(self, path: Path) -> None:
        self._path = path

    def records(self) -> list[ApplicationRecord]:
        if not self._path.exists():
            return []
        with self._path.open(newline="", encoding="utf-8") as handle:
            return [ApplicationRecord.model_validate(row) for row in csv.DictReader(handle)]

    def _write_all(self, records: list[ApplicationRecord]) -> None:
        buffer = io.StringIO()
        writer = csv.DictWriter(buffer, fieldnames=COLUMNS)
        writer.writeheader()
        for record in records:
            writer.writerow(record.model_dump())
        atomic_write_text(self._path, buffer.getvalue())

    def initialize(self) -> None:
        """Create an empty tracker with headers if none exists."""
        if not self._path.exists():
            self._write_all([])

    def _existing_keys(self) -> set[str]:
        keys: set[str] = set()
        for record in self.records():
            keys.update(
                _duplicate_keys(
                    record.company,
                    record.job_title,
                    record.country,
                    record.job_id,
                    record.application_url,
                )
            )
        return keys

    def is_duplicate(self, job: Job) -> bool:
        """True when this job was already applied to (FR-063)."""
        existing = self._existing_keys()
        candidate = _duplicate_keys(job.company, job.title, job.country, job.job_id, job.url)
        return any(key in existing for key in candidate)

    def add(self, record: ApplicationRecord) -> None:
        """Append one application; refuses duplicates."""
        records = self.records()
        existing = self._existing_keys()
        new_keys = _duplicate_keys(
            record.company,
            record.job_title,
            record.country,
            record.job_id,
            record.application_url,
        )
        if any(key in existing for key in new_keys):
            raise DuplicateApplicationError(
                f"An application to {record.company} for '{record.job_title}' is "
                "already recorded in the tracker.",
                details={"company": record.company, "job_title": record.job_title},
            )
        records.append(record)
        self._write_all(records)
