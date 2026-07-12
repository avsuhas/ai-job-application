"""Ranking domain models (docs/02D, docs/05 Task Contract: Job Ranking)."""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field

from job_platform.jobs.models import Job, JobAnalysis


class Recommendation(StrEnum):
    APPLY_IMMEDIATELY = "apply_immediately"
    EXCELLENT_MATCH = "excellent_match"
    STRONG_MATCH = "strong_match"
    GOOD_MATCH = "good_match"
    POSSIBLE_MATCH = "possible_match"
    LOW_PRIORITY = "low_priority"
    IGNORE = "ignore"
    INELIGIBLE = "ineligible"


def recommendation_for_score(score: int) -> Recommendation:
    """Deterministic score → recommendation mapping (docs/02D Match Score)."""
    if score >= 95:
        return Recommendation.APPLY_IMMEDIATELY
    if score >= 90:
        return Recommendation.EXCELLENT_MATCH
    if score >= 80:
        return Recommendation.STRONG_MATCH
    if score >= 70:
        return Recommendation.GOOD_MATCH
    if score >= 60:
        return Recommendation.POSSIBLE_MATCH
    if score >= 40:
        return Recommendation.LOW_PRIORITY
    return Recommendation.IGNORE


class JobMatchResult(BaseModel):
    """Provider output for one job ranking task. Validated per docs/05."""

    match_score: int = Field(ge=0, le=100)
    matched_required_qualifications: list[str] = Field(default_factory=list)
    matched_preferred_qualifications: list[str] = Field(default_factory=list)
    missing_required_qualifications: list[str] = Field(default_factory=list)
    missing_preferred_qualifications: list[str] = Field(default_factory=list)
    transferable_experience: list[str] = Field(default_factory=list)
    eligibility_concerns: list[str] = Field(default_factory=list)
    preference_alignment: list[str] = Field(default_factory=list)
    suggested_resume: str = ""
    reasoning: str = ""
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)


class RankedJob(BaseModel):
    """Final ranking engine output: job + analysis + match + recommendation."""

    job: Job
    analysis: JobAnalysis | None = None
    match: JobMatchResult | None = None
    recommendation: Recommendation
    eligibility_flags: list[str] = Field(default_factory=list)
    error: str | None = None

    @property
    def score(self) -> int:
        return self.match.match_score if self.match else 0
