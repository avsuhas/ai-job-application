"""Tests for the application review service (docs/07D-1)."""

import json

import pytest

from job_platform.candidate.loader import load_candidate_bundle
from job_platform.jobs.models import Job, JobAnalysis
from job_platform.packages.store import PackageStore
from job_platform.preparation.service import PreparationOptions, PreparationService
from job_platform.providers.mock import MockReasoningProvider
from job_platform.ranking.models import JobMatchResult, RankedJob, Recommendation
from job_platform.review.models import ReviewStatus, Severity
from job_platform.review.service import ReviewService
from job_platform.shared.config import Settings


def make_ranked(**job_overrides) -> RankedJob:
    defaults = dict(
        id="job_1",
        company="ExampleCo",
        title="Backend Engineer",
        job_id="42",
        url="https://example.com/jobs/42",
        description="Python and Kafka work.",
        ats="greenhouse",
    )
    defaults.update(job_overrides)
    job = Job(**defaults)
    return RankedJob(
        job=job,
        analysis=JobAnalysis(job_family="Backend", required_skills=["python"]),
        match=JobMatchResult(match_score=85, suggested_resume="backend", confidence=0.8),
        recommendation=Recommendation.STRONG_MATCH,
    )


@pytest.fixture
def review_env(candidate_dir, tmp_path):
    bundle = load_candidate_bundle(candidate_dir)
    store = PackageStore(tmp_path / "packages")
    prep = PreparationService(MockReasoningProvider(), store, Settings())
    reviewer = ReviewService(store, known_companies=["ExampleCo", "OtherCorp", "MegaCorp"])
    return bundle, store, prep, reviewer, candidate_dir


async def prepare(prep, bundle, **kwargs):
    options = PreparationOptions(**kwargs) if kwargs else None
    return await prep.prepare(make_ranked(), bundle, options)


class TestReviewService:
    async def test_clean_package_is_approved(self, review_env):
        bundle, store, prep, reviewer, _ = review_env
        manifest = await prepare(prep, bundle)
        report = reviewer.review(manifest, bundle)
        # Narrative answers await approval -> approved_with_warnings at best
        assert report.status in (
            ReviewStatus.APPROVED,
            ReviewStatus.APPROVED_WITH_WARNINGS,
        )
        assert report.blocking_findings == []
        assert "review/review_report.json" in manifest.artifacts

    async def test_tampered_artifact_is_blocking(self, review_env):
        bundle, store, prep, reviewer, _ = review_env
        manifest = await prepare(prep, bundle)
        # Tamper with an artifact outside the application
        path = store.package_dir(manifest.package_id) / "answers/prepared_answers.json"
        path.write_text('{"answers": []}')
        report = reviewer.review(manifest, bundle)
        assert report.status == ReviewStatus.BLOCKED
        assert any(f.category == "package_integrity" for f in report.blocking_findings)

    async def test_missing_artifact_is_blocking(self, review_env):
        bundle, store, prep, reviewer, _ = review_env
        manifest = await prepare(prep, bundle)
        (store.package_dir(manifest.package_id) / "job/job.json").unlink()
        report = reviewer.review(manifest, bundle)
        assert report.status == ReviewStatus.BLOCKED

    async def test_stale_candidate_data_requires_changes(self, review_env):
        bundle, store, prep, reviewer, candidate_dir = review_env
        manifest = await prepare(prep, bundle)
        (candidate_dir / "profile" / "notes.md").write_text("Changed after preparation.")
        updated = load_candidate_bundle(candidate_dir)
        report = reviewer.review(manifest, updated)
        stale = [f for f in report.findings if f.category == "stale_package"]
        assert stale and stale[0].automatically_correctable
        assert report.status == ReviewStatus.CHANGES_REQUIRED

    async def test_cross_company_contamination_blocks(self, review_env):
        bundle, store, prep, reviewer, _ = review_env
        manifest = await prepare(prep, bundle, generate_cover_letter=True)
        letter = store.read_artifact(manifest.package_id, "cover_letter/cover_letter.md")
        store.write_artifact(
            manifest,
            "cover_letter/cover_letter.md",
            letter + "\nI have always wanted to join MegaCorp.",
        )
        store.save_manifest(manifest)
        report = reviewer.review(manifest, bundle)
        contamination = [
            f for f in report.findings if f.category == "cross_company_contamination"
        ]
        assert contamination
        assert contamination[0].severity == Severity.BLOCKING
        assert "MegaCorp" in contamination[0].message

    async def test_candidate_employer_mention_is_not_contamination(
        self, review_env, candidate_dir
    ):
        bundle, store, prep, reviewer, _ = review_env
        # OtherCorp is a known company AND appears in the candidate's resume
        resume = candidate_dir / "resume" / "Backend.txt"
        resume.write_text(resume.read_text() + "\nPreviousCo was acquired by OtherCorp.")
        bundle = load_candidate_bundle(candidate_dir)
        manifest = await prepare(prep, bundle, generate_cover_letter=True)
        letter = store.read_artifact(manifest.package_id, "cover_letter/cover_letter.md")
        store.write_artifact(
            manifest,
            "cover_letter/cover_letter.md",
            letter + "\nAt OtherCorp I built billing systems.",
        )
        store.save_manifest(manifest)
        report = reviewer.review(manifest, bundle)
        assert not [
            f for f in report.findings if f.category == "cross_company_contamination"
        ]

    async def test_candidate_fact_drift_detected(self, review_env):
        bundle, store, prep, reviewer, _ = review_env
        manifest = await prepare(prep, bundle)
        answers = json.loads(
            store.read_artifact(manifest.package_id, "answers/prepared_answers.json")
        )
        for answer in answers["answers"]:
            if answer["question_family"] == "personal.email":
                answer["answer"] = "wrong@example.com"
        store.write_artifact(
            manifest, "answers/prepared_answers.json", json.dumps(answers, indent=2)
        )
        store.save_manifest(manifest)
        report = reviewer.review(manifest, bundle)
        mismatches = [f for f in report.findings if f.category == "candidate_fact_mismatch"]
        assert mismatches
        assert "personal.email" in mismatches[0].message

    async def test_work_authorization_contradiction_needs_user_input(
        self, review_env, candidate_dir
    ):
        (candidate_dir / "profile" / "candidate.json").write_text(
            json.dumps(
                {
                    "personal": {"first_name": "Alex", "last_name": "Sample",
                                 "email": "a@example.com", "phone": "1"},
                    "work_authorization": {
                        "authorized_to_work": False,
                        "requires_sponsorship": False,
                    },
                }
            )
        )
        bundle = load_candidate_bundle(candidate_dir)
        _, _, prep, reviewer, _ = review_env
        manifest = await prepare(prep, bundle)
        report = reviewer.review(manifest, bundle)
        contradictions = [
            f
            for f in report.findings
            if f.category == "work_authorization" and "Contradiction" in f.message
        ]
        assert contradictions
        assert contradictions[0].requires_user_input

    async def test_unresolved_required_answer_requires_user_input(
        self, review_env, candidate_dir
    ):
        (candidate_dir / "profile" / "candidate.json").write_text("{}")
        bundle = load_candidate_bundle(candidate_dir)
        _, store, prep, reviewer, _ = review_env
        manifest = await prepare(prep, bundle)
        report = reviewer.review(manifest, bundle)
        assert report.status == ReviewStatus.USER_INPUT_REQUIRED
        assert any("personal.first_name" in a for a in report.required_user_actions)

    async def test_report_persisted_and_reloadable(self, review_env):
        bundle, store, prep, reviewer, _ = review_env
        manifest = await prepare(prep, bundle)
        reviewer.review(manifest, bundle)
        raw = store.read_artifact(manifest.package_id, "review/review_report.json")
        persisted = json.loads(raw)
        assert persisted["package_id"] == manifest.package_id
        assert persisted["review_stage"] == "preparation"
