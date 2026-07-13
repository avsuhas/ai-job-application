"""Automatic-mode kill switch, submission limits, and metrics (docs/17 Phase 12).

The kill switch is a persistent file: while present, every automatic
submission is denied regardless of settings. Daily and per-company limits are
counted from the durable application tracker, so they survive restarts and
cannot be bypassed by re-running the queue.
"""

from __future__ import annotations

from datetime import UTC, date, datetime
from pathlib import Path

from pydantic import BaseModel, Field

from job_platform.shared.files import atomic_write_text
from job_platform.shared.logging import get_logger
from job_platform.storage.tracker import ApplicationTracker

logger = get_logger("orchestration.automatic")

KILL_SWITCH_FILE = "automatic_mode.killed"


class KillSwitch:
    def __init__(self, data_root: Path) -> None:
        self._path = data_root / KILL_SWITCH_FILE

    @property
    def engaged(self) -> bool:
        return self._path.exists()

    def engage(self, reason: str = "") -> None:
        atomic_write_text(
            self._path,
            f"engaged_at={datetime.now(UTC).isoformat()}\nreason={reason}\n",
        )
        logger.warning("Automatic-mode kill switch engaged: %s", reason or "(no reason)")

    def release(self) -> None:
        self._path.unlink(missing_ok=True)
        logger.info("Automatic-mode kill switch released")

    def reason(self) -> str:
        if not self._path.exists():
            return ""
        for line in self._path.read_text(encoding="utf-8").splitlines():
            if line.startswith("reason="):
                return line.split("=", 1)[1]
        return ""


class SubmissionLimits(BaseModel):
    daily_used: int = 0
    daily_limit: int = 0
    company_used: int = 0
    per_company_limit: int = 0

    @property
    def daily_exceeded(self) -> bool:
        return self.daily_used >= self.daily_limit

    @property
    def company_exceeded(self) -> bool:
        return self.company_used >= self.per_company_limit


def _submitted_today(tracker: ApplicationTracker, today: date) -> list:
    return [
        r
        for r in tracker.records()
        if r.status == "submitted" and r.date_applied == today.isoformat()
    ]


def check_limits(
    tracker: ApplicationTracker,
    company: str,
    daily_limit: int,
    per_company_limit: int,
    today: date | None = None,
) -> SubmissionLimits:
    today = today or datetime.now(UTC).date()
    submitted = _submitted_today(tracker, today)
    company_count = sum(1 for r in submitted if r.company.lower() == company.lower())
    return SubmissionLimits(
        daily_used=len(submitted),
        daily_limit=daily_limit,
        company_used=company_count,
        per_company_limit=per_company_limit,
    )


class AutomaticMetrics(BaseModel):
    auto_submitted: int = 0
    downgraded_to_review: int = 0
    blocked: int = 0
    unknown_outcomes: int = 0
    events: list[dict] = Field(default_factory=list)


def compute_metrics(history_events: list) -> AutomaticMetrics:
    """Roll up automatic-mode outcomes from the history event log."""
    metrics = AutomaticMetrics()
    for event in history_events:
        etype = event.event_type if hasattr(event, "event_type") else event.get("event_type")
        if etype == "auto_submitted":
            metrics.auto_submitted += 1
        elif etype == "auto_downgraded":
            metrics.downgraded_to_review += 1
        elif etype == "auto_blocked":
            metrics.blocked += 1
        elif etype == "auto_unknown":
            metrics.unknown_outcomes += 1
    return metrics
