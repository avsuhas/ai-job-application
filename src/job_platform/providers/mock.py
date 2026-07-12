"""Deterministic mock provider for tests and offline development.

Produces plausible, repeatable analyses/rankings from simple keyword matching
so the full workflow can run without network access or an API key.
"""

from __future__ import annotations

import re

from job_platform.jobs.models import Job, JobAnalysis
from job_platform.providers.base import JobRankingRequest, ReasoningProvider
from job_platform.ranking.models import JobMatchResult

_KNOWN_SKILLS = [
    "python", "go", "java", "c++", "rust", "typescript", "javascript", "react",
    "fastapi", "django", "flask", "kubernetes", "docker", "terraform", "aws",
    "gcp", "azure", "kafka", "redis", "postgresql", "mysql", "spark", "pytorch",
    "tensorflow", "cuda", "linux", "sql", "graphql", "grpc",
]

_YEARS = re.compile(r"(\d+)\+?\s*(?:or more\s*)?years", re.IGNORECASE)


class MockReasoningProvider(ReasoningProvider):
    name = "mock"

    async def analyze_job(self, job: Job) -> JobAnalysis:
        text = f"{job.title}\n{job.description}".lower()
        skills = [s for s in _KNOWN_SKILLS if s in text]
        years_match = _YEARS.search(job.description)
        hard: list[str] = []
        if "clearance" in text:
            hard.append("Security clearance required")
        if "us citizen" in text or "u.s. citizen" in text:
            hard.append("US citizenship required")
        return JobAnalysis(
            job_family=job.title.split(",")[0][:60],
            seniority="senior" if "senior" in text else "",
            required_skills=skills[:6],
            preferred_skills=skills[6:10],
            required_experience_years=float(years_match.group(1)) if years_match else None,
            employment_type=job.employment_type,
            remote_status=job.remote_status,
            hard_requirements=hard,
        )

    async def rank_job(self, request: JobRankingRequest) -> JobMatchResult:
        context = request.candidate_context.lower()
        required = request.analysis.required_skills
        matched = [s for s in required if s.lower() in context]
        missing = [s for s in required if s.lower() not in context]
        if required:
            score = int(30 + 65 * (len(matched) / len(required)))
        else:
            score = 50
        first_resume = ""
        for line in request.resume_inventory.splitlines():
            if "id=" in line:
                first_resume = line.split("id=")[1].split()[0]
                break
        return JobMatchResult(
            match_score=score,
            matched_required_qualifications=matched,
            missing_required_qualifications=missing,
            eligibility_concerns=list(request.analysis.hard_requirements),
            suggested_resume=first_resume,
            reasoning=(
                f"Mock ranking: matched {len(matched)}/{len(required)} required "
                "skills against the candidate context."
            ),
            confidence=0.5,
        )
