"""Tests for the Application Package store (docs/07A)."""

from datetime import UTC, datetime

import pytest

from job_platform.candidate.loader import load_candidate_bundle
from job_platform.packages.models import PackageJobSummary, PackageManifest, PackageStatus
from job_platform.packages.store import (
    PackageStore,
    candidate_source_fingerprints,
    make_package_id,
)
from job_platform.shared.errors import StorageError


def make_manifest(package_id: str = "exampleco_42_20260712T120000") -> PackageManifest:
    return PackageManifest(
        package_id=package_id,
        job=PackageJobSummary(company="ExampleCo", title="Backend Engineer", job_id="42"),
    )


class TestPackageId:
    def test_uses_job_id_when_present(self):
        now = datetime(2026, 7, 10, 22, 15, 0, tzinfo=UTC)
        assert make_package_id("Google", "123456", "SWE", now) == "google_123456_20260710T221500"

    def test_uses_title_hash_when_no_job_id(self):
        now = datetime(2026, 7, 10, 22, 15, 0, tzinfo=UTC)
        package_id = make_package_id("Microsoft", "", "Senior Engineer", now)
        assert package_id.startswith("microsoft_")
        assert package_id.endswith("_20260710T221500")
        # deterministic middle hash
        assert package_id == make_package_id("Microsoft", "", "Senior Engineer", now)


class TestPackageStore:
    def test_manifest_roundtrip(self, tmp_path):
        store = PackageStore(tmp_path)
        manifest = make_manifest()
        store.save_manifest(manifest)
        loaded = store.load_manifest(manifest.package_id)
        assert loaded.job.company == "ExampleCo"
        assert loaded.status == PackageStatus.CREATED
        assert loaded.schema_version == "1.0"

    def test_missing_package_raises(self, tmp_path):
        with pytest.raises(StorageError):
            PackageStore(tmp_path).load_manifest("nope_1_2")

    def test_write_artifact_records_fingerprint_and_version(self, tmp_path):
        store = PackageStore(tmp_path)
        manifest = make_manifest()
        record = store.write_artifact(manifest, "job/job.json", '{"a": 1}')
        assert record.version == 1
        assert len(record.sha256) == 64

        # Same content -> same version; new content -> bumped version
        same = store.write_artifact(manifest, "job/job.json", '{"a": 1}')
        assert same.version == 1
        changed = store.write_artifact(manifest, "job/job.json", '{"a": 2}')
        assert changed.version == 2

        on_disk = store.read_artifact(manifest.package_id, "job/job.json")
        assert on_disk == '{"a": 2}'

    def test_read_missing_artifact_raises(self, tmp_path):
        store = PackageStore(tmp_path)
        manifest = make_manifest()
        store.save_manifest(manifest)
        with pytest.raises(StorageError):
            store.read_artifact(manifest.package_id, "resume/none.md")

    def test_list_package_ids(self, tmp_path):
        store = PackageStore(tmp_path)
        manifest = make_manifest()
        store.save_manifest(manifest)
        assert store.list_package_ids() == [manifest.package_id]


class TestStaleness:
    def test_fresh_package_reports_no_stale_sources(self, candidate_dir, tmp_path):
        bundle = load_candidate_bundle(candidate_dir)
        manifest = make_manifest()
        manifest.source_fingerprints = candidate_source_fingerprints(bundle)
        assert PackageStore(tmp_path).stale_sources(manifest, bundle) == []

    def test_changed_candidate_file_is_detected(self, candidate_dir, tmp_path):
        bundle = load_candidate_bundle(candidate_dir)
        manifest = make_manifest()
        manifest.source_fingerprints = candidate_source_fingerprints(bundle)

        (candidate_dir / "profile" / "rules.md").write_text("New rule: never travel.")
        updated = load_candidate_bundle(candidate_dir)
        stale = PackageStore(tmp_path).stale_sources(manifest, updated)
        assert stale == ["profile/rules"]

    def test_deleted_resume_is_detected(self, candidate_dir, tmp_path):
        bundle = load_candidate_bundle(candidate_dir)
        manifest = make_manifest()
        manifest.source_fingerprints = candidate_source_fingerprints(bundle)

        (candidate_dir / "resume" / "Backend.txt").unlink()
        updated = load_candidate_bundle(candidate_dir)
        stale = PackageStore(tmp_path).stale_sources(manifest, updated)
        assert stale == ["resume/Backend.txt"]
