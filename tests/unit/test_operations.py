"""Tests for Phase 11 operations hardening: restore, migrations rollback,
disk guard, and hash-chained audit."""

import json

import pytest

from job_platform.operations.audit import verify_event_log
from job_platform.operations.backup import create_backup, restore_backup
from job_platform.operations.disk import check_disk
from job_platform.operations.migrations import (
    MigrationStep,
    current_version,
    run_migrations,
)
from job_platform.shared.config import Settings
from job_platform.shared.errors import StorageError
from job_platform.storage.tracker import ApplicationTracker
from job_platform.submission.history import ApplicationHistoryService


def make_settings(tmp_path):
    return Settings(paths={"data_root": tmp_path / "user_data"})


def seed_data(settings):
    profile = settings.paths.profile_dir
    profile.mkdir(parents=True, exist_ok=True)
    (profile / "candidate.json").write_text('{"personal": {"first_name": "Alex"}}')
    settings.paths.applications_dir.mkdir(parents=True, exist_ok=True)
    (settings.paths.tracker_path).write_text("company,job_title\nExampleCo,Engineer\n")


class TestRestore:
    def test_restore_recovers_deleted_data(self, tmp_path):
        settings = make_settings(tmp_path)
        seed_data(settings)
        backup = create_backup(settings)

        # Corrupt/delete the candidate file, then restore
        (settings.paths.profile_dir / "candidate.json").write_text("CORRUPTED")
        result = restore_backup(settings, backup.path.split("/")[-1])
        assert result.file_count >= 2
        assert result.safety_copy  # a pre-restore snapshot was taken
        assert '"first_name": "Alex"' in (
            settings.paths.profile_dir / "candidate.json"
        ).read_text()

    def test_restore_missing_backup_raises(self, tmp_path):
        settings = make_settings(tmp_path)
        seed_data(settings)
        with pytest.raises(StorageError):
            restore_backup(settings, "backup_nope.zip")

    def test_restore_corrupt_backup_raises(self, tmp_path):
        settings = make_settings(tmp_path)
        seed_data(settings)
        backups_dir = settings.paths.data_root / "backups"
        backups_dir.mkdir(parents=True, exist_ok=True)
        (backups_dir / "backup_bad.zip").write_text("not a zip")
        with pytest.raises(StorageError):
            restore_backup(settings, "backup_bad.zip")


class TestMigrations:
    def test_no_pending_migrations_is_noop(self, tmp_path):
        settings = make_settings(tmp_path)
        seed_data(settings)
        result = run_migrations(settings, migrations=[])
        assert result.applied == []
        assert not result.rolled_back

    def test_successful_migration_advances_version(self, tmp_path):
        settings = make_settings(tmp_path)
        seed_data(settings)
        marks = []
        migs = [
            (MigrationStep(version=1, name="first"), lambda s: marks.append(1)),
            (MigrationStep(version=2, name="second"), lambda s: marks.append(2)),
        ]
        result = run_migrations(settings, migs)
        assert result.applied == ["first", "second"]
        assert result.to_version == 2
        assert current_version(settings) == 2
        # Re-running applies nothing (idempotent)
        assert run_migrations(settings, migs).applied == []

    def test_failed_migration_rolls_back(self, tmp_path):
        settings = make_settings(tmp_path)
        seed_data(settings)

        def bad(s):
            (s.paths.profile_dir / "candidate.json").write_text("HALF-MIGRATED")
            raise RuntimeError("migration exploded")

        migs = [(MigrationStep(version=1, name="broken"), bad)]
        result = run_migrations(settings, migs)
        assert result.rolled_back
        assert result.to_version == 0
        assert current_version(settings) == 0
        # Data restored to pre-migration state
        assert '"first_name": "Alex"' in (
            settings.paths.profile_dir / "candidate.json"
        ).read_text()


class TestDiskGuard:
    def test_healthy_disk_is_safe(self, tmp_path):
        status = check_disk(tmp_path, min_free_bytes=1)
        assert status.safe_to_write
        assert status.free_bytes > 0

    def test_low_disk_blocks_writes(self, tmp_path):
        status = check_disk(tmp_path, min_free_bytes=10**18)  # impossibly high
        assert not status.safe_to_write
        assert "blocked" in status.message


class TestAuditHashChain:
    def _history(self, tmp_path):
        tracker = ApplicationTracker(tmp_path / "tracker.csv")
        return ApplicationHistoryService(tracker, tmp_path / "events.jsonl")

    def test_valid_chain_passes(self, tmp_path):
        history = self._history(tmp_path)
        for i in range(4):
            history.record_event("submitted", package_id=f"p{i}")
        report = verify_event_log(tmp_path / "events.jsonl")
        assert report.ok
        assert report.chain_valid
        assert report.events_checked == 4

    def test_tampered_event_content_detected(self, tmp_path):
        history = self._history(tmp_path)
        history.record_event("submitted", package_id="p1", message="original")
        history.record_event("submitted", package_id="p2")

        # Tamper with the first event's message, keeping its stored hash
        path = tmp_path / "events.jsonl"
        lines = path.read_text().splitlines()
        first = json.loads(lines[0])
        first["message"] = "TAMPERED"
        lines[0] = json.dumps(first)
        path.write_text("\n".join(lines) + "\n")

        report = verify_event_log(path)
        assert not report.ok
        assert not report.chain_valid
        assert any("tampered" in i.lower() for i in report.issues)

    def test_removed_event_breaks_chain(self, tmp_path):
        history = self._history(tmp_path)
        for i in range(3):
            history.record_event("submitted", package_id=f"p{i}")
        path = tmp_path / "events.jsonl"
        lines = path.read_text().splitlines()
        # Delete the middle event
        path.write_text(lines[0] + "\n" + lines[2] + "\n")
        report = verify_event_log(path)
        assert not report.chain_valid
        assert any("hash chain" in i for i in report.issues)
