"""Unit tests for approval binding, backups, and audit integrity (Phase 10)."""

import json
from pathlib import Path

import pytest

from job_platform.candidate.loader import load_candidate_bundle
from job_platform.operations.audit import verify_event_log
from job_platform.operations.backup import create_backup, list_backups, verify_backup
from job_platform.orchestration.models import WorkflowState, WorkflowStatus
from job_platform.orchestration.workflow import STATE_PATH
from job_platform.packages.store import PackageStore
from job_platform.preparation.service import PreparationService
from job_platform.providers.mock import MockReasoningProvider
from job_platform.review.approval import (
    ApprovalError,
    create_approval,
    load_approval,
    verify_approval,
)
from job_platform.shared.config import Settings
from job_platform.shared.files import atomic_write_text
from job_platform.storage.tracker import ApplicationTracker
from job_platform.submission.history import ApplicationHistoryService
from tests.unit.test_review import make_ranked


async def prepared_package(store, bundle, settings=None):
    prep = PreparationService(MockReasoningProvider(), store, settings or Settings())
    return await prep.prepare(make_ranked(), bundle)


def write_state(store, manifest, status, engine_status="stopped_before_submit"):
    state = WorkflowState(
        package_id=manifest.package_id, status=status, engine_status=engine_status
    )
    atomic_write_text(
        store.package_dir(manifest.package_id) / STATE_PATH,
        state.model_dump_json(indent=2),
    )


def write_execution_report(store, manifest, content='{"status": "stopped_before_submit"}'):
    store.write_artifact(manifest, "execution/form_execution_report.json", content)
    store.save_manifest(manifest)


class TestApproval:
    async def test_approval_requires_waiting_for_review(self, candidate_dir, tmp_path):
        bundle = load_candidate_bundle(candidate_dir)
        store = PackageStore(tmp_path / "packages")
        manifest = await prepared_package(store, bundle)
        write_execution_report(store, manifest)
        # No workflow state yet
        with pytest.raises(ApprovalError):
            create_approval(store, manifest)

    async def test_approval_created_and_verified(self, candidate_dir, tmp_path):
        bundle = load_candidate_bundle(candidate_dir)
        store = PackageStore(tmp_path / "packages")
        manifest = await prepared_package(store, bundle)
        write_execution_report(store, manifest)
        write_state(store, manifest, WorkflowStatus.WAITING_FOR_REVIEW)

        approval = create_approval(store, manifest)
        assert approval.artifact_fingerprints
        assert approval.form_report_hash
        assert load_approval(store, manifest.package_id).approval_id == approval.approval_id
        # Verify passes while nothing changed
        assert verify_approval(store, manifest).approval_id == approval.approval_id

    async def test_changed_artifact_invalidates_approval(self, candidate_dir, tmp_path):
        bundle = load_candidate_bundle(candidate_dir)
        store = PackageStore(tmp_path / "packages")
        manifest = await prepared_package(store, bundle)
        write_execution_report(store, manifest)
        write_state(store, manifest, WorkflowStatus.WAITING_FOR_REVIEW)
        create_approval(store, manifest)

        # Mutate a bound artifact after approval
        store.write_artifact(manifest, "answers/prepared_answers.json", '{"answers": []}')
        store.save_manifest(manifest)
        with pytest.raises(ApprovalError) as excinfo:
            verify_approval(store, manifest)
        assert "changed after approval" in excinfo.value.message

    async def test_changed_form_report_invalidates_approval(self, candidate_dir, tmp_path):
        bundle = load_candidate_bundle(candidate_dir)
        store = PackageStore(tmp_path / "packages")
        manifest = await prepared_package(store, bundle)
        write_execution_report(store, manifest)
        write_state(store, manifest, WorkflowStatus.WAITING_FOR_REVIEW)
        create_approval(store, manifest)

        write_execution_report(store, manifest, '{"status": "ready_for_review", "x": 1}')
        with pytest.raises(ApprovalError) as excinfo:
            verify_approval(store, manifest)
        assert "report changed" in excinfo.value.message

    async def test_verify_without_approval_raises(self, candidate_dir, tmp_path):
        bundle = load_candidate_bundle(candidate_dir)
        store = PackageStore(tmp_path / "packages")
        manifest = await prepared_package(store, bundle)
        with pytest.raises(ApprovalError) as excinfo:
            verify_approval(store, manifest)
        assert "requires user approval" in excinfo.value.message


class TestBackup:
    async def test_backup_includes_data_excludes_profiles(self, candidate_dir, tmp_path):
        data_root = tmp_path / "user_data"
        (data_root / "candidate" / "profile").mkdir(parents=True)
        (data_root / "candidate" / "profile" / "candidate.json").write_text('{"a": 1}')
        (data_root / "applications").mkdir(parents=True)
        (data_root / "applications" / "tracker.csv").write_text("company\n")
        (data_root / "browser" / "profiles" / "default").mkdir(parents=True)
        (data_root / "browser" / "profiles" / "default" / "cookies").write_text("secret")

        settings = Settings(paths={"data_root": data_root})
        result = create_backup(settings)
        assert verify_backup(Path(result.path))

        import zipfile
        with zipfile.ZipFile(result.path) as archive:
            names = archive.namelist()
        assert any("candidate.json" in n for n in names)
        assert any("tracker.csv" in n for n in names)
        assert not any("browser" in n for n in names)  # profiles excluded

        assert list_backups(settings)[0]["name"] == Path(result.path).name

    def test_corrupt_backup_fails_verification(self, tmp_path):
        bad = tmp_path / "backup_bad.zip"
        bad.write_text("not a zip")
        assert not verify_backup(bad)


class TestAudit:
    def _history(self, tmp_path):
        tracker = ApplicationTracker(tmp_path / "tracker.csv")
        return ApplicationHistoryService(tracker, tmp_path / "events.jsonl")

    def test_clean_log_passes(self, tmp_path):
        history = self._history(tmp_path)
        history.record_event("submitted", package_id="p1")
        history.record_event("submitted", package_id="p2")
        report = verify_event_log(tmp_path / "events.jsonl")
        assert report.ok
        assert report.events_checked == 2

    def test_empty_log_is_consistent(self, tmp_path):
        assert verify_event_log(tmp_path / "nope.jsonl").ok

    def test_corrupt_line_flagged(self, tmp_path):
        history = self._history(tmp_path)
        history.record_event("submitted")
        with (tmp_path / "events.jsonl").open("a") as handle:
            handle.write("not json\n")
        report = verify_event_log(tmp_path / "events.jsonl")
        assert not report.ok
        assert any("not a valid" in i for i in report.issues)

    def test_backwards_timestamp_flagged(self, tmp_path):
        events = tmp_path / "events.jsonl"
        events.write_text(
            json.dumps({"event_id": "history_1", "event_type": "x",
                        "at": "2026-07-12T10:00:00+00:00"}) + "\n" +
            json.dumps({"event_id": "history_2", "event_type": "x",
                        "at": "2026-07-12T09:00:00+00:00"}) + "\n"
        )
        report = verify_event_log(events)
        assert not report.ok
        assert any("backwards" in i for i in report.issues)

    def test_duplicate_event_id_flagged(self, tmp_path):
        events = tmp_path / "events.jsonl"
        line = json.dumps({"event_id": "history_dup", "event_type": "x",
                           "at": "2026-07-12T10:00:00+00:00"})
        events.write_text(line + "\n" + line + "\n")
        report = verify_event_log(events)
        assert not report.ok
        assert any("duplicate event id" in i for i in report.issues)
