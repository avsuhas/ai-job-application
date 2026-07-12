"""Application Package domain models (docs/07A).

A package is the self-contained, versioned unit holding everything needed to
apply to one job: immutable job/candidate snapshots plus generated materials.
"""

from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum

from pydantic import BaseModel, Field

SCHEMA_VERSION = "1.0"


class PackageStatus(StrEnum):
    CREATED = "created"
    COLLECTING_CONTEXT = "collecting_context"
    SELECTING_RESUME = "selecting_resume"
    GENERATING_MATERIALS = "generating_materials"
    VALIDATING = "validating"
    NEEDS_ATTENTION = "needs_attention"
    READY = "ready"
    SUBMITTED = "submitted"
    FAILED = "failed"
    CANCELLED = "cancelled"
    ALREADY_APPLIED = "already_applied"


class ArtifactRecord(BaseModel):
    """Fingerprint and version for one file inside the package."""

    path: str
    sha256: str
    version: int = 1
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class PackageJobSummary(BaseModel):
    company: str
    title: str
    job_id: str = ""
    application_url: str = ""


class AttentionItem(BaseModel):
    code: str
    message: str
    blocking: bool = True


class PackageManifest(BaseModel):
    """package.json — the main package manifest (docs/07A)."""

    package_id: str
    schema_version: str = SCHEMA_VERSION
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    status: PackageStatus = PackageStatus.CREATED
    candidate_profile_id: str = "default"
    job: PackageJobSummary
    match_score: int | None = None
    recommendation: str = ""
    expected_ats: str = ""
    automation_mode: str = "review"
    selected_resume: str | None = None
    cover_letter: str | None = None
    answers_file: str | None = None
    artifacts: dict[str, ArtifactRecord] = Field(default_factory=dict)
    # Hashes of the candidate source files used at preparation time; a change
    # in any of them means the package is stale (docs/17 Phase 3 acceptance).
    source_fingerprints: dict[str, str] = Field(default_factory=dict)
    attention_items: list[AttentionItem] = Field(default_factory=list)

    def touch(self) -> None:
        self.updated_at = datetime.now(UTC)

    @property
    def blocking_attention_items(self) -> list[AttentionItem]:
        return [item for item in self.attention_items if item.blocking]
