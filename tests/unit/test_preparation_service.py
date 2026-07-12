"""Tests for the end-to-end preparation service (docs/07A, docs/17 Phase 3)."""

import json

import pytest

from job_platform.candidate.loader import load_candidate_bundle
from job_platform.jobs.models import Job, JobAnalysis
from job_platform.packages.models import PackageStatus
from job_platform.packages.store import PackageStore
from job_platform.preparation.service import PreparationOptions, PreparationService
from job_platform.providers.mock import MockReasoningProvider
from job_platform.ranking.models import JobMatchResult, RankedJob, Recommendation
from job_platform.shared.config import Settings
from job_platform.shared.errors import ProviderError
from job_platform.storage.tracker import ApplicationRecord, ApplicationTracker
from tests.conftest import StubProvider


def make_ranked(score: int = 85) -> RankedJob:
    job = Job(
        id="job_1",
        company="ExampleCo",
        title="Backend Engineer",
        job_id="42",
        url="https://example.com/jobs/42",
        description="Python and Kafka work. 5+ years.",
        ats="greenhouse",
    )
    return RankedJob(
        job=job,
        analysis=JobAnalysis(job_family="Backend", required_skills=["python", "kafka"]),
        match=JobMatchResult(match_score=score, suggested_resume="backend", confidence=0.8),
        recommendation=Recommendation.STRONG_MATCH,
    )


@pytest.fixture
def service_env(candidate_dir, tmp_path):
    bundle = load_candidate_bundle(candidate_dir)
    store = PackageStore(tmp_path / "packages")
    tracker = ApplicationTracker(tmp_path / "tracker.csv")
    settings = Settings(reasoning={"provider": "mock"})
    service = PreparationService(MockReasoningProvider(), store, settings, tracker=tracker)
    return service, store, bundle, tracker


class TestPreparationService:
    async def test_prepares_ready_package_with_all_artifacts(self, service_env):
        service, store, bundle, _ = service_env
        manifest = await service.prepare(make_ranked(), bundle)

        assert manifest.status == PackageStatus.READY
        assert manifest.package_id.startswith("exampleco_42_")
        artifacts = set(manifest.artifacts)
        assert {
            "job/job.json",
            "job/raw_description.txt",
            "job/analysis.json",
            "job/ranking.json",
            "candidate/context.json",
            "candidate/rules_snapshot.md",
            "resume/base_resume_reference.json",
            "resume/tailoring_plan.json",
            "resume/validation_report.json",
            "resume/tailored_resume.md",
            "cover_letter/metadata.json",
            "answers/prepared_answers.json",
            "answers/unresolved_questions.json",
            "plan/application_plan.json",
        } <= artifacts
        # Every artifact is fingerprinted and versioned
        assert all(len(r.sha256) == 64 and r.version >= 1 for r in manifest.artifacts.values())
        assert manifest.source_fingerprints  # staleness detection enabled
        assert manifest.selected_resume == "resume/tailored_resume.md"

    async def test_snapshots_are_reloadable_without_regeneration(self, service_env):
        service, store, bundle, _ = service_env
        manifest = await service.prepare(make_ranked(), bundle)
        job_snapshot = json.loads(store.read_artifact(manifest.package_id, "job/job.json"))
        assert job_snapshot["company"] == "ExampleCo"
        reloaded = store.load_manifest(manifest.package_id)
        assert reloaded.status == PackageStatus.READY

    async def test_cover_letter_generated_when_requested(self, service_env):
        service, store, bundle, _ = service_env
        manifest = await service.prepare(
            make_ranked(), bundle, PreparationOptions(generate_cover_letter=True)
        )
        assert manifest.cover_letter == "cover_letter/cover_letter.md"
        letter = store.read_artifact(manifest.package_id, "cover_letter/cover_letter.md")
        assert "ExampleCo" in letter
        metadata = json.loads(
            store.read_artifact(manifest.package_id, "cover_letter/metadata.json")
        )
        assert metadata["decision"]["generate"] is True
        assert metadata["validation"]["status"] == "passed"

    async def test_no_cover_letter_by_default(self, service_env):
        service, store, bundle, _ = service_env
        manifest = await service.prepare(make_ranked(), bundle)
        assert manifest.cover_letter is None
        metadata = json.loads(
            store.read_artifact(manifest.package_id, "cover_letter/metadata.json")
        )
        assert metadata["decision"]["generate"] is False

    async def test_already_applied_job_short_circuits(self, service_env):
        service, _, bundle, tracker = service_env
        ranked = make_ranked()
        tracker.add(ApplicationRecord.from_job(ranked.job))
        manifest = await service.prepare(ranked, bundle)
        assert manifest.status == PackageStatus.ALREADY_APPLIED
        assert manifest.artifacts == {}

    async def test_unresolved_required_answers_need_attention(
        self, candidate_dir, tmp_path
    ):
        (candidate_dir / "profile" / "candidate.json").write_text("{}")
        bundle = load_candidate_bundle(candidate_dir)
        store = PackageStore(tmp_path / "packages")
        service = PreparationService(MockReasoningProvider(), store, Settings())
        manifest = await service.prepare(make_ranked(), bundle)
        assert manifest.status == PackageStatus.NEEDS_ATTENTION
        codes = {item.code for item in manifest.attention_items}
        assert "unresolved:personal.first_name" in codes

    async def test_tailoring_failure_falls_back_to_base_resume(self, service_env):
        service, store, bundle, _ = service_env

        class TailoringFails(MockReasoningProvider):
            async def tailor_resume(self, request):
                raise ProviderError("tailoring outage")

        service._provider = TailoringFails()
        manifest = await service.prepare(make_ranked(), bundle)
        assert manifest.status == PackageStatus.READY  # non-blocking fallback
        assert manifest.selected_resume.startswith("candidate resume:")
        assert any(i.code == "tailoring_failed" for i in manifest.attention_items)

    async def test_total_failure_marks_package_failed(self, candidate_dir, tmp_path):
        bundle = load_candidate_bundle(candidate_dir)
        store = PackageStore(tmp_path / "packages")
        service = PreparationService(StubProvider(), store, Settings())
        manifest = await service.prepare(make_ranked(), bundle)
        assert manifest.status == PackageStatus.FAILED
        # Failure is persisted for inspection
        reloaded = store.load_manifest(manifest.package_id)
        assert reloaded.status == PackageStatus.FAILED
