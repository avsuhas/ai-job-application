"""Tests for application analytics rollups (docs/17 Phase 13)."""

from job_platform.storage.analytics import compute_analytics
from job_platform.storage.tracker import ApplicationRecord, ApplicationTracker
from job_platform.submission.history import HistoryEvent


def tracker_with(tmp_path, records):
    tracker = ApplicationTracker(tmp_path / "tracker.csv")
    for r in records:
        tracker.add(r)
    return tracker


def rec(company, title, status="submitted", date="2026-07-13", job_id=None):
    return ApplicationRecord(
        company=company, job_title=title, job_id=job_id or title,
        application_url=f"https://x/{company}/{title}", status=status,
        date_applied=date,
    )


class TestAnalytics:
    def test_empty_tracker(self, tmp_path):
        stats = compute_analytics(ApplicationTracker(tmp_path / "t.csv"))
        assert stats.total_applications == 0
        assert stats.by_status == {}

    def test_counts_by_status_company_and_date(self, tmp_path):
        tracker = tracker_with(tmp_path, [
            rec("Acme", "Backend", date="2026-07-12"),
            rec("Acme", "Platform", date="2026-07-13"),
            rec("Globex", "SRE", status="pending", date="2026-07-13"),
        ])
        stats = compute_analytics(tracker)
        assert stats.total_applications == 3
        assert stats.by_status == {"submitted": 2, "pending": 1}
        assert stats.by_company == {"Acme": 2, "Globex": 1}
        assert stats.by_date == {"2026-07-12": 1, "2026-07-13": 2}
        assert stats.top_companies[0] == {"company": "Acme", "count": 2}

    def test_funnel_from_events(self, tmp_path):
        tracker = tracker_with(tmp_path, [rec("Acme", "Backend")])
        events = [
            HistoryEvent(event_type="submission_attempt_created"),
            HistoryEvent(event_type="submitted"),
            HistoryEvent(event_type="auto_downgraded"),
            HistoryEvent(event_type="history_synced"),  # not a funnel stage
        ]
        stats = compute_analytics(tracker, events)
        assert stats.funnel["attempted"] == 1
        assert stats.funnel["submitted"] == 1
        assert stats.funnel["downgraded"] == 1
        assert "history_synced" not in stats.funnel
