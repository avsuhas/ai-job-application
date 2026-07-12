"""Reasoning provider abstraction (docs/05).

Business logic depends only on this interface; Claude SDK objects never leave
the Claude provider module. Additional task methods (resume tailoring, answer
generation, form resolution) will be added in later phases.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from pydantic import BaseModel

from job_platform.jobs.models import Job, JobAnalysis
from job_platform.ranking.models import JobMatchResult


class JobRankingRequest(BaseModel):
    job: Job
    analysis: JobAnalysis
    candidate_context: str
    resume_inventory: str = "No resumes available."


class ReasoningProvider(ABC):
    """Task-based reasoning contracts. One method per task, typed in and out."""

    name: str = "base"

    @abstractmethod
    async def analyze_job(self, job: Job) -> JobAnalysis:
        """Convert a job description into a structured requirement model."""

    @abstractmethod
    async def rank_job(self, request: JobRankingRequest) -> JobMatchResult:
        """Evaluate candidate fit for an analyzed job."""
