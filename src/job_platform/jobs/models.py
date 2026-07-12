"""Job domain models (docs/02D, docs/16).

A ``Job`` is the canonical normalized record every adapter must produce.
Raw ATS payloads are preserved under ``raw`` (FR-020).
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field


def _now() -> datetime:
    return datetime.now(UTC)


class Job(BaseModel):
    id: str
    company: str
    title: str
    job_id: str = ""
    location: str = ""
    country: str = ""
    url: str = ""
    description: str = ""
    department: str = ""
    employment_type: str = ""
    remote_status: str = "unknown"
    date_posted: datetime | None = None
    date_discovered: datetime = Field(default_factory=_now)
    date_updated: datetime | None = None
    ats: str = ""
    source: str = ""
    raw: dict[str, Any] = Field(default_factory=dict)


class JobAnalysis(BaseModel):
    """Structured requirement model produced by the reasoning provider
    (docs/05 Task Contract: Job Analysis)."""

    job_family: str = ""
    seniority: str = ""
    required_skills: list[str] = Field(default_factory=list)
    preferred_skills: list[str] = Field(default_factory=list)
    required_experience_years: float | None = None
    required_education: list[str] = Field(default_factory=list)
    preferred_education: list[str] = Field(default_factory=list)
    responsibilities: list[str] = Field(default_factory=list)
    leadership_requirements: list[str] = Field(default_factory=list)
    work_authorization_requirements: list[str] = Field(default_factory=list)
    security_clearance_requirements: list[str] = Field(default_factory=list)
    travel_requirements: list[str] = Field(default_factory=list)
    employment_type: str = ""
    remote_status: str = ""
    hard_requirements: list[str] = Field(default_factory=list)
    ambiguities: list[str] = Field(default_factory=list)
