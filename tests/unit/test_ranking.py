"""Tests for eligibility checks and the ranking engine."""

import pytest

from job_platform.candidate.loader import load_candidate_bundle
from job_platform.jobs.models import Job, JobAnalysis
from job_platform.providers.base import JobRankingRequest
from job_platform.providers.mock import MockReasoningProvider
from job_platform.ranking.eligibility import eligibility_flags
from job_platform.ranking.models import (
    JobMatchResult,
    Recommendation,
    recommendation_for_score,
)
from job_platform.ranking.ranker import RankingEngine
from job_platform.shared.errors import ProviderError
from tests.conftest import StubProvider


def make_job(i: int, description: str = "Python, Kafka, AWS work") -> Job:
    return Job(
        id=f"job_{i}", company="ExampleCo", title=f"Backend Engineer {i}",
        description=description, url=f"https://x/{i}",
    )


class TestRecommendationMapping:
    @pytest.mark.parametrize(
        ("score", "expected"),
        [
            (97, Recommendation.APPLY_IMMEDIATELY),
            (92, Recommendation.EXCELLENT_MATCH),
            (85, Recommendation.STRONG_MATCH),
            (75, Recommendation.GOOD_MATCH),
            (65, Recommendation.POSSIBLE_MATCH),
            (50, Recommendation.LOW_PRIORITY),
            (20, Recommendation.IGNORE),
        ],
    )
    def test_score_bands(self, score, expected):
        assert recommendation_for_score(score) == expected


class TestEligibility:
    def test_no_flags_for_authorized_candidate(self, candidate_dir):
        bundle = load_candidate_bundle(candidate_dir)
        analysis = JobAnalysis(required_skills=["python"])
        assert eligibility_flags(analysis, bundle) == []

    def test_flags_unauthorized_candidate(self, candidate_dir):
        (candidate_dir / "profile" / "candidate.json").write_text(
            '{"work_authorization": {"authorized_to_work": false}}'
        )
        bundle = load_candidate_bundle(candidate_dir)
        flags = eligibility_flags(JobAnalysis(), bundle)
        assert any("not authorized" in f for f in flags)

    def test_flags_sponsorship_conflict(self, candidate_dir):
        (candidate_dir / "profile" / "candidate.json").write_text(
            '{"work_authorization": {"authorized_to_work": true, "requires_sponsorship": true}}'
        )
        bundle = load_candidate_bundle(candidate_dir)
        analysis = JobAnalysis(work_authorization_requirements=["Must be a US Citizen"])
        flags = eligibility_flags(analysis, bundle)
        assert any("citizenship" in f.lower() for f in flags)

    def test_flags_missing_clearance(self, candidate_dir):
        bundle = load_candidate_bundle(candidate_dir)
        analysis = JobAnalysis(security_clearance_requirements=["TS/SCI"])
        flags = eligibility_flags(analysis, bundle)
        assert any("clearance" in f for f in flags)

    def test_clearance_in_notes_suppresses_flag(self, candidate_dir):
        (candidate_dir / "profile" / "notes.md").write_text("I hold an active TS clearance.")
        bundle = load_candidate_bundle(candidate_dir)
        analysis = JobAnalysis(security_clearance_requirements=["TS/SCI"])
        assert eligibility_flags(analysis, bundle) == []


class FailingProvider(StubProvider):
    name = "failing"

    async def analyze_job(self, job):
        raise ProviderError("simulated outage")

    async def rank_job(self, request):
        raise AssertionError("should not be called")


class ScriptedProvider(StubProvider):
    """Returns fixed scores per job id so sorting can be asserted."""

    name = "scripted"

    def __init__(self, scores: dict[str, int]):
        self.scores = scores

    async def analyze_job(self, job):
        return JobAnalysis(required_skills=["python"])

    async def rank_job(self, request: JobRankingRequest):
        return JobMatchResult(match_score=self.scores[request.job.id], confidence=0.9)


class TestRankingEngine:
    async def test_ranks_and_sorts_jobs(self, candidate_dir):
        bundle = load_candidate_bundle(candidate_dir)
        provider = ScriptedProvider({"job_1": 60, "job_2": 90, "job_3": 75})
        engine = RankingEngine(provider)
        ranked = await engine.rank_jobs([make_job(1), make_job(2), make_job(3)], bundle)
        assert [r.job.id for r in ranked] == ["job_2", "job_3", "job_1"]
        assert ranked[0].recommendation == Recommendation.EXCELLENT_MATCH

    async def test_mock_provider_end_to_end(self, candidate_dir):
        bundle = load_candidate_bundle(candidate_dir)
        engine = RankingEngine(MockReasoningProvider())
        ranked = await engine.rank_jobs([make_job(1)], bundle)
        assert ranked[0].match is not None
        assert ranked[0].match.suggested_resume == "backend"
        assert ranked[0].score > 50  # candidate context contains python/kafka/aws

    async def test_provider_failure_is_recorded_not_raised(self, candidate_dir):
        bundle = load_candidate_bundle(candidate_dir)
        engine = RankingEngine(FailingProvider())
        ranked = await engine.rank_jobs([make_job(1)], bundle)
        assert ranked[0].error == "simulated outage"
        assert ranked[0].recommendation == Recommendation.LOW_PRIORITY

    async def test_eligibility_conflict_marks_ineligible(self, candidate_dir):
        (candidate_dir / "profile" / "candidate.json").write_text(
            '{"work_authorization": {"authorized_to_work": false}}'
        )
        bundle = load_candidate_bundle(candidate_dir)
        provider = ScriptedProvider({"job_1": 95})
        ranked = await RankingEngine(provider).rank_jobs([make_job(1)], bundle)
        assert ranked[0].recommendation == Recommendation.INELIGIBLE
        assert ranked[0].eligibility_flags
        assert ranked[0].score == 95  # score preserved for transparency
