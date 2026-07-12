"""Reasoning provider abstraction (docs/05).

Business logic depends only on this interface; Claude SDK objects never leave
the Claude provider module. Additional task methods (resume tailoring, answer
generation, form resolution) will be added in later phases.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from pydantic import BaseModel

from job_platform.jobs.models import Job, JobAnalysis
from job_platform.providers.tasks import (
    CoverLetterDraft,
    CoverLetterRequest,
    NarrativeAnswerRequest,
    NarrativeAnswerResult,
    ResumeSelectionRequest,
    ResumeSelectionResult,
    ResumeTailoringRequest,
    ResumeTailoringResult,
)
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

    @abstractmethod
    async def select_resume(self, request: ResumeSelectionRequest) -> ResumeSelectionResult:
        """Select the strongest base resume for a job."""

    @abstractmethod
    async def tailor_resume(self, request: ResumeTailoringRequest) -> ResumeTailoringResult:
        """Produce an evidence-backed tailoring plan for the base resume."""

    @abstractmethod
    async def generate_cover_letter(self, request: CoverLetterRequest) -> CoverLetterDraft:
        """Generate a concise, factually grounded cover letter draft."""

    @abstractmethod
    async def generate_application_answer(
        self, request: NarrativeAnswerRequest
    ) -> NarrativeAnswerResult:
        """Generate one narrative application answer from approved facts."""
