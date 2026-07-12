"""Candidate Knowledge Base validation.

Missing optional information produces warnings; only unusable data (invalid
JSON, no readable resume when required) produces errors (docs/02C, FR-006).
"""

from __future__ import annotations

from pathlib import Path

from job_platform.candidate.loader import load_candidate_bundle
from job_platform.candidate.models import (
    CandidateBundle,
    CandidateValidationReport,
    IssueSeverity,
    ValidationIssue,
)
from job_platform.shared.errors import CandidateDataError


def _warn(code: str, message: str, path: str | None = None) -> ValidationIssue:
    return ValidationIssue(
        severity=IssueSeverity.WARNING, code=code, message=message, path=path
    )


def _error(code: str, message: str, path: str | None = None) -> ValidationIssue:
    return ValidationIssue(severity=IssueSeverity.ERROR, code=code, message=message, path=path)


def validate_bundle(bundle: CandidateBundle) -> CandidateValidationReport:
    issues: list[ValidationIssue] = []
    profile = bundle.profile

    if not profile.personal.full_name:
        issues.append(
            _warn("missing_name", "candidate.json has no first_name/last_name set.")
        )
    if not profile.personal.email:
        issues.append(_warn("missing_email", "candidate.json has no email set."))
    if "@" in profile.personal.email and profile.personal.email.count("@") != 1:
        issues.append(_warn("malformed_email", "candidate.json email looks malformed."))

    auth = profile.work_authorization
    if auth.authorized_to_work is None:
        issues.append(
            _warn(
                "missing_work_authorization",
                "work_authorization.authorized_to_work is not set; sponsorship "
                "questions cannot be answered truthfully without it.",
            )
        )
    if auth.authorized_to_work is False and auth.requires_sponsorship is False:
        issues.append(
            _warn(
                "contradictory_work_authorization",
                "authorized_to_work is false but requires_sponsorship is also "
                "false; these answers usually conflict.",
            )
        )

    if not bundle.resumes:
        issues.append(
            _warn(
                "no_resumes",
                "No resumes found in the resume folder. Job ranking can run, "
                "but applications cannot be prepared without one.",
            )
        )
    for resume in bundle.resumes:
        if resume.text_extraction_error:
            issues.append(
                _warn("resume_text_extraction", resume.text_extraction_error, str(resume.path))
            )
        elif not resume.text:
            issues.append(
                _warn(
                    "empty_resume_text",
                    f"No text could be extracted from {resume.name}.",
                    str(resume.path),
                )
            )

    for name in ("rules", "preferences", "answers"):
        if name not in bundle.documents:
            issues.append(
                _warn(f"missing_{name}", f"Optional profile document {name}.md is missing.")
            )

    return CandidateValidationReport(issues=issues)


def validate_candidate_dir(candidate_dir: Path) -> CandidateValidationReport:
    """Load and validate the CKB, converting load failures into report errors."""
    if not candidate_dir.exists():
        return CandidateValidationReport(
            issues=[
                _error(
                    "missing_candidate_dir",
                    f"Candidate directory {candidate_dir} does not exist. Run "
                    "scripts/initialize_user_data.py first.",
                    str(candidate_dir),
                )
            ]
        )
    try:
        bundle = load_candidate_bundle(candidate_dir)
    except CandidateDataError as exc:
        return CandidateValidationReport(
            issues=[_error(exc.code, exc.message, str(exc.details.get("path", "")))]
        )
    return validate_bundle(bundle)
