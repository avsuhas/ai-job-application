"""Ranking engine (docs/02D): analyze each job, check eligibility, score with
the reasoning provider, and return jobs sorted by match score.

Each job is one small task contract (analysis, then ranking) rather than one
giant prompt, per docs/05 Task-Based Reasoning Contracts.
"""

from __future__ import annotations

import asyncio

from job_platform.candidate.context import build_candidate_context, resume_inventory
from job_platform.candidate.models import CandidateBundle
from job_platform.jobs.models import Job
from job_platform.providers.base import JobRankingRequest, ReasoningProvider
from job_platform.ranking.eligibility import eligibility_flags
from job_platform.ranking.models import (
    RankedJob,
    Recommendation,
    recommendation_for_score,
)
from job_platform.shared.errors import ProviderError
from job_platform.shared.logging import get_logger

logger = get_logger("ranking.ranker")


class RankingEngine:
    def __init__(self, provider: ReasoningProvider, max_parallel: int = 5) -> None:
        self._provider = provider
        self._semaphore = asyncio.Semaphore(max_parallel)

    async def _rank_one(
        self, job: Job, bundle: CandidateBundle, candidate_context: str, resumes: str
    ) -> RankedJob:
        async with self._semaphore:
            try:
                analysis = await self._provider.analyze_job(job)
                flags = eligibility_flags(analysis, bundle)
                match = await self._provider.rank_job(
                    JobRankingRequest(
                        job=job,
                        analysis=analysis,
                        candidate_context=candidate_context,
                        resume_inventory=resumes,
                    )
                )
            except ProviderError as exc:
                logger.warning("Ranking failed for %s (%s): %s", job.title, job.id, exc.message)
                return RankedJob(
                    job=job,
                    recommendation=Recommendation.LOW_PRIORITY,
                    error=exc.message,
                )
        recommendation = (
            Recommendation.INELIGIBLE if flags else recommendation_for_score(match.match_score)
        )
        return RankedJob(
            job=job,
            analysis=analysis,
            match=match,
            recommendation=recommendation,
            eligibility_flags=flags,
        )

    async def rank_jobs(self, jobs: list[Job], bundle: CandidateBundle) -> list[RankedJob]:
        """Rank all jobs against the candidate, best match first."""
        # Ranking needs the candidate's actual experience, so include a base
        # resume in the trusted context (docs/05 Context for Job Ranking).
        base_resume = bundle.resumes[0] if bundle.resumes else None
        candidate_context = build_candidate_context(bundle, resume=base_resume)
        resumes = resume_inventory(bundle)
        ranked = await asyncio.gather(
            *(self._rank_one(job, bundle, candidate_context, resumes) for job in jobs)
        )
        return sorted(ranked, key=lambda r: r.score, reverse=True)
