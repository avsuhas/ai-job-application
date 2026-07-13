"""Application analytics (docs/17 Phase 13 improved analytics).

Read-only rollups over the application tracker and history event log — no new
storage. Everything is derived on demand from the existing durable records so
analytics can never drift from the source of truth.
"""

from __future__ import annotations

from collections import Counter

from pydantic import BaseModel, Field

from job_platform.storage.tracker import ApplicationTracker
from job_platform.submission.history import HistoryEvent

# History events that mark a stage of the discover → submit funnel.
_FUNNEL_EVENTS = {
    "submission_attempt_created": "attempted",
    "submitted": "submitted",
    "auto_submitted": "auto_submitted",
    "submission_unknown": "unknown",
    "auto_downgraded": "downgraded",
}


class ApplicationAnalytics(BaseModel):
    total_applications: int = 0
    by_status: dict[str, int] = Field(default_factory=dict)
    by_company: dict[str, int] = Field(default_factory=dict)
    by_date: dict[str, int] = Field(default_factory=dict)
    funnel: dict[str, int] = Field(default_factory=dict)
    top_companies: list[dict] = Field(default_factory=list)


def compute_analytics(
    tracker: ApplicationTracker, events: list[HistoryEvent] | None = None
) -> ApplicationAnalytics:
    records = tracker.records()
    status = Counter(r.status for r in records)
    company = Counter(r.company for r in records)
    by_date = Counter(r.date_applied for r in records if r.date_applied)

    funnel: Counter = Counter()
    for event in events or []:
        stage = _FUNNEL_EVENTS.get(event.event_type)
        if stage:
            funnel[stage] += 1

    top = [
        {"company": name, "count": count}
        for name, count in company.most_common(5)
    ]
    return ApplicationAnalytics(
        total_applications=len(records),
        by_status=dict(status),
        by_company=dict(company),
        by_date=dict(sorted(by_date.items())),
        funnel=dict(funnel),
        top_companies=top,
    )
