"""Tests for the application readiness service (docs/07D-2)."""

import json

import pytest

from job_platform.candidate.loader import load_candidate_bundle
from job_platform.packages.store import PackageStore
from job_platform.preparation.service import PreparationService
from job_platform.providers.mock import MockReasoningProvider
from job_platform.readiness.models import CheckStatus, ReadinessStage, ReadinessStatus
from job_platform.readiness.service import ReadinessService
from job_platform.review.service import ReviewService
from job_platform.shared.config import Settings
from job_platform.storage.tracker import ApplicationRecord, ApplicationTracker
from tests.unit.test_review import make_ranked


@pytest.fixture
def readiness_env(candidate_dir, tmp_path):
    bundle = load_candidate_bundle(candidate_dir)
    store = PackageStore(tmp_path / "packages")
    tracker = ApplicationTracker(tmp_path / "tracker.csv")
    prep = PreparationService(MockReasoningProvider(), store, Settings(), tracker=tracker)
    reviewer = ReviewService(store, known_companies=["ExampleCo"])
    readiness = ReadinessService(store, tracker=tracker)
    return bundle, store, prep, reviewer, readiness, tracker, candidate_dir


async def prepared_and_reviewed(prep, reviewer, bundle):
    manifest = await prep.prepare(make_ranked(), bundle)
    reviewer.review(manifest, bundle)
    return manifest


class TestReadinessService:
    async def test_reviewed_package_is_ready(self, readiness_env):
        bundle, store, prep, reviewer, readiness, _, _ = readiness_env
        manifest = await prepared_and_reviewed(prep, reviewer, bundle)
        report = readiness.evaluate(manifest, bundle, ReadinessStage.MANUAL_COMPLETION)
        # Fixture profile leaves optional questions blank -> warnings allowed
        assert report.status in (
            ReadinessStatus.READY,
            ReadinessStatus.READY_WITH_WARNINGS,
        )
        assert report.next_allowed_action == "manual_completion"
        assert "readiness/readiness_report.json" in manifest.artifacts

    async def test_unreviewed_package_is_not_ready(self, readiness_env):
        bundle, store, prep, _, readiness, _, _ = readiness_env
        manifest = await prep.prepare(make_ranked(), bundle)
        report = readiness.evaluate(manifest, bundle)
        assert report.status == ReadinessStatus.BLOCKED
        assert report.next_allowed_action == "run_review"
        check = next(c for c in report.checks if c.check_id == "review_completed")
        assert check.status == CheckStatus.FAILED

    async def test_blocked_review_blocks_readiness(self, readiness_env):
        bundle, store, prep, reviewer, readiness, _, _ = readiness_env
        manifest = await prep.prepare(make_ranked(), bundle)
        # Tamper so review blocks, then evaluate
        path = store.package_dir(manifest.package_id) / "answers/prepared_answers.json"
        path.write_text('{"answers": []}')
        reviewer.review(manifest, bundle)
        report = readiness.evaluate(manifest, bundle)
        assert report.status == ReadinessStatus.BLOCKED
        assert report.blocking_issues

    async def test_duplicate_application_detected(self, readiness_env):
        bundle, store, prep, reviewer, readiness, tracker, _ = readiness_env
        manifest = await prepared_and_reviewed(prep, reviewer, bundle)
        tracker.add(ApplicationRecord.from_job(make_ranked().job))
        report = readiness.evaluate(manifest, bundle)
        assert report.status == ReadinessStatus.ALREADY_APPLIED
        assert report.next_allowed_action == "none"

    async def test_stale_candidate_data_requires_refresh(self, readiness_env):
        bundle, store, prep, reviewer, readiness, _, candidate_dir = readiness_env
        manifest = await prepared_and_reviewed(prep, reviewer, bundle)
        (candidate_dir / "profile" / "preferences.md").write_text("Salary: 500000")
        updated = load_candidate_bundle(candidate_dir)
        report = readiness.evaluate(manifest, updated)
        assert report.status == ReadinessStatus.REFRESH_REQUIRED
        assert report.next_allowed_action == "re_prepare_package"
        assert report.refresh_reasons

    async def test_missing_required_answers_need_user_action(
        self, readiness_env, candidate_dir
    ):
        (candidate_dir / "profile" / "candidate.json").write_text("{}")
        bundle = load_candidate_bundle(candidate_dir)
        _, store, prep, reviewer, readiness, _, _ = readiness_env
        manifest = await prep.prepare(make_ranked(), bundle)
        reviewer.review(manifest, bundle)
        report = readiness.evaluate(manifest, bundle)
        assert report.status == ReadinessStatus.USER_ACTION_REQUIRED
        assert report.next_allowed_action == "resolve_user_actions"
        assert any("personal.first_name" in a for a in report.required_user_actions)

    async def test_tampered_artifact_blocks(self, readiness_env):
        bundle, store, prep, reviewer, readiness, _, _ = readiness_env
        manifest = await prepared_and_reviewed(prep, reviewer, bundle)
        path = store.package_dir(manifest.package_id) / "job/job.json"
        path.write_text('{"company": "Tampered"}')
        report = readiness.evaluate(manifest, bundle)
        assert report.status == ReadinessStatus.BLOCKED
        check = next(c for c in report.checks if c.check_id == "artifact_hashes")
        assert check.status == CheckStatus.FAILED
        assert "job/job.json" in check.evidence

    async def test_report_is_persisted(self, readiness_env):
        bundle, store, prep, reviewer, readiness, _, _ = readiness_env
        manifest = await prepared_and_reviewed(prep, reviewer, bundle)
        readiness.evaluate(manifest, bundle)
        raw = json.loads(
            store.read_artifact(manifest.package_id, "readiness/readiness_report.json")
        )
        assert raw["package_id"] == manifest.package_id
        assert raw["stage"] == "manual_completion"
