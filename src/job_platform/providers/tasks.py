"""Typed request/response contracts for preparation reasoning tasks
(docs/05 Task Contracts, docs/07B, docs/07C-1, docs/07C-2)."""

from __future__ import annotations

from pydantic import BaseModel, Field

from job_platform.jobs.models import Job, JobAnalysis


class ResumeSelectionRequest(BaseModel):
    job: Job
    analysis: JobAnalysis
    resume_inventory: str
    candidate_rules: str = ""


class ResumeSelectionResult(BaseModel):
    """docs/05 Task Contract: Resume Selection."""

    selected_resume_id: str
    reasoning: str = ""
    alternatives: list[str] = Field(default_factory=list)
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)


class RevisedBullet(BaseModel):
    original: str
    revised: str
    supporting_sources: list[str] = Field(default_factory=list)
    reason: str = ""


class ResumeTailoringRequest(BaseModel):
    job: Job
    analysis: JobAnalysis
    resume_text: str
    candidate_context: str
    candidate_rules: str = ""


class ResumeTailoringResult(BaseModel):
    """docs/05 Task Contract: Resume Tailoring."""

    professional_summary: str = ""
    skills_order: list[str] = Field(default_factory=list)
    section_order: list[str] = Field(default_factory=list)
    revised_bullets: list[RevisedBullet] = Field(default_factory=list)
    removed_content: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    unsupported_claims: list[str] = Field(default_factory=list)


class CoverLetterRequest(BaseModel):
    job: Job
    analysis: JobAnalysis
    candidate_context: str
    template: str = ""
    max_words: int = 400
    excluded_topics: list[str] = Field(default_factory=list)


class CoverLetterDraft(BaseModel):
    """docs/07C-1 Draft Output Contract."""

    status: str = "generated"
    greeting: str = "Dear Hiring Team,"
    body_paragraphs: list[str] = Field(default_factory=list)
    closing: str = "Sincerely,"
    signature_name: str = ""
    word_count: int = 0
    candidate_sources: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    unsupported_claims: list[str] = Field(default_factory=list)

    def render(self) -> str:
        parts = [self.greeting, ""]
        for paragraph in self.body_paragraphs:
            parts.extend([paragraph, ""])
        parts.extend([self.closing, self.signature_name])
        return "\n".join(parts).strip() + "\n"


class NarrativeAnswerRequest(BaseModel):
    job: Job
    canonical_question: str
    question_family: str
    candidate_context: str
    character_limit: int | None = None


class NarrativeAnswerResult(BaseModel):
    """docs/05 answer-generation contract (narrative subset)."""

    answer: str
    candidate_sources: list[str] = Field(default_factory=list)
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    warnings: list[str] = Field(default_factory=list)
