"""Tests for the application tracker and search result storage."""

import csv

import pytest

from job_platform.jobs.models import Job
from job_platform.jobs.service import DiscoveryResult, SearchFilters
from job_platform.shared.errors import DuplicateApplicationError, StorageError
from job_platform.storage.search_store import SearchRecord, SearchStore
from job_platform.storage.tracker import ApplicationRecord, ApplicationTracker


def make_job(**kw) -> Job:
    defaults = dict(
        id="job_1", company="ExampleCo", title="Backend Engineer", job_id="42",
        url="https://example.com/jobs/42", country="United States",
    )
    defaults.update(kw)
    return Job(**defaults)


class TestTracker:
    def test_initialize_creates_csv_with_headers(self, tmp_path):
        tracker = ApplicationTracker(tmp_path / "tracker.csv")
        tracker.initialize()
        with (tmp_path / "tracker.csv").open() as handle:
            header = next(csv.reader(handle))
        assert header[:3] == ["company", "job_title", "job_id"]

    def test_add_and_read_back(self, tmp_path):
        tracker = ApplicationTracker(tmp_path / "tracker.csv")
        tracker.add(ApplicationRecord.from_job(make_job(), resume_used="Backend.pdf"))
        records = tracker.records()
        assert len(records) == 1
        assert records[0].company == "ExampleCo"
        assert records[0].resume_used == "Backend.pdf"
        assert records[0].status == "submitted"
        assert records[0].date_applied  # auto-filled

    def test_duplicate_by_job_id_rejected(self, tmp_path):
        tracker = ApplicationTracker(tmp_path / "tracker.csv")
        tracker.add(ApplicationRecord.from_job(make_job()))
        with pytest.raises(DuplicateApplicationError):
            tracker.add(ApplicationRecord.from_job(make_job(url="https://other/url")))

    def test_duplicate_by_url_rejected(self, tmp_path):
        tracker = ApplicationTracker(tmp_path / "tracker.csv")
        tracker.add(ApplicationRecord.from_job(make_job()))
        duplicate = make_job(job_id="", url="https://example.com/jobs/42/", title="Renamed")
        with pytest.raises(DuplicateApplicationError):
            tracker.add(ApplicationRecord.from_job(duplicate))

    def test_duplicate_by_company_title_rejected(self, tmp_path):
        tracker = ApplicationTracker(tmp_path / "tracker.csv")
        tracker.add(ApplicationRecord.from_job(make_job()))
        duplicate = make_job(job_id="", url="https://elsewhere/1")
        with pytest.raises(DuplicateApplicationError):
            tracker.add(ApplicationRecord.from_job(duplicate))

    def test_is_duplicate_checks_job(self, tmp_path):
        tracker = ApplicationTracker(tmp_path / "tracker.csv")
        tracker.add(ApplicationRecord.from_job(make_job()))
        assert tracker.is_duplicate(make_job())
        assert not tracker.is_duplicate(
            make_job(job_id="99", url="https://example.com/jobs/99", title="SRE")
        )

    def test_different_companies_not_duplicates(self, tmp_path):
        tracker = ApplicationTracker(tmp_path / "tracker.csv")
        tracker.add(ApplicationRecord.from_job(make_job()))
        other = make_job(company="OtherCorp", url="https://other/42")
        tracker.add(ApplicationRecord.from_job(other))
        assert len(tracker.records()) == 2


class TestSearchStore:
    def test_save_and_load_roundtrip(self, tmp_path):
        store = SearchStore(tmp_path)
        record = SearchRecord(
            status="complete",
            filters=SearchFilters(keywords=["backend"]),
            source_ids=["exampleco"],
            discovery=DiscoveryResult(jobs=[make_job()]),
        )
        store.save(record)
        loaded = store.load(record.search_id)
        assert loaded.status == "complete"
        assert loaded.filters.keywords == ["backend"]
        assert loaded.discovery.jobs[0].company == "ExampleCo"

    def test_load_missing_search_raises(self, tmp_path):
        with pytest.raises(StorageError):
            SearchStore(tmp_path).load("search_missing")

    def test_list_ids(self, tmp_path):
        store = SearchStore(tmp_path)
        record = SearchRecord()
        store.save(record)
        assert store.list_ids() == [record.search_id]
