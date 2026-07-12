"""Candidate domain models (Candidate Knowledge Base).

The CKB is user-owned and intentionally flexible (docs/02C): candidate.json
holds structured facts while Markdown files hold preferences, rules, reusable
answers, and notes. Models therefore allow extra fields rather than enforcing
one rigid schema.
"""

from __future__ import annotations

from enum import StrEnum
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field


class PersonalInfo(BaseModel):
    model_config = ConfigDict(extra="allow")

    first_name: str = ""
    last_name: str = ""
    email: str = ""
    phone: str = ""
    address: str = ""
    city: str = ""
    state: str = ""
    country: str = ""
    postal_code: str = ""

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()


class EmploymentInfo(BaseModel):
    model_config = ConfigDict(extra="allow")

    current_company: str = ""
    current_title: str = ""
    years_of_experience: float = 0


class WorkAuthorization(BaseModel):
    model_config = ConfigDict(extra="allow")

    authorized_to_work: bool | None = None
    requires_sponsorship: bool | None = None
    visa_status: str = ""


class EducationInfo(BaseModel):
    model_config = ConfigDict(extra="allow")

    highest_degree: str = ""
    university: str = ""


class CandidateProfile(BaseModel):
    """Structured facts from candidate.json."""

    model_config = ConfigDict(extra="allow")

    personal: PersonalInfo = Field(default_factory=PersonalInfo)
    employment: EmploymentInfo = Field(default_factory=EmploymentInfo)
    work_authorization: WorkAuthorization = Field(default_factory=WorkAuthorization)
    education: EducationInfo = Field(default_factory=EducationInfo)


class ResumeDocument(BaseModel):
    """A base resume file plus its extracted text."""

    id: str
    name: str
    path: Path
    format: str
    text: str = ""
    text_extraction_error: str | None = None


class CandidateBundle(BaseModel):
    """Everything loaded from the Candidate Knowledge Base.

    Free-form documents are keyed by filename stem (``rules``, ``answers`` …)
    so future files such as ``publications.md`` load without code changes.
    """

    profile: CandidateProfile = Field(default_factory=CandidateProfile)
    documents: dict[str, str] = Field(default_factory=dict)
    resumes: list[ResumeDocument] = Field(default_factory=list)
    source_dir: Path | None = None

    @property
    def rules(self) -> str:
        return self.documents.get("rules", "")

    @property
    def preferences(self) -> str:
        return self.documents.get("preferences", "")

    @property
    def answers(self) -> str:
        return self.documents.get("answers", "")

    @property
    def notes(self) -> str:
        return self.documents.get("notes", "")

    def resume_by_id(self, resume_id: str) -> ResumeDocument | None:
        for resume in self.resumes:
            if resume.id == resume_id:
                return resume
        return None


class IssueSeverity(StrEnum):
    ERROR = "error"
    WARNING = "warning"


class ValidationIssue(BaseModel):
    severity: IssueSeverity
    code: str
    message: str
    path: str | None = None


class CandidateValidationReport(BaseModel):
    issues: list[ValidationIssue] = Field(default_factory=list)

    @property
    def errors(self) -> list[ValidationIssue]:
        return [i for i in self.issues if i.severity == IssueSeverity.ERROR]

    @property
    def warnings(self) -> list[ValidationIssue]:
        return [i for i in self.issues if i.severity == IssueSeverity.WARNING]

    @property
    def ok(self) -> bool:
        return not self.errors
