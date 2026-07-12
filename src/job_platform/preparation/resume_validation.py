"""Deterministic factual validation of tailored resumes (docs/07B, docs/17).

Runs in code, independent of the provider, so a hallucinated change cannot
reach browser execution. Checks are conservative: they compare the tailored
output against the base resume and structured candidate facts.

A resume with blocking issues must not be used for submission (docs/07A).
"""

from __future__ import annotations

import re

from pydantic import BaseModel, Field

from job_platform.candidate.models import CandidateBundle
from job_platform.providers.tasks import ResumeTailoringResult

_YEAR = re.compile(r"\b(?:19|20)\d{2}\b")
_METRIC = re.compile(r"\b\d+(?:\.\d+)?\s*(?:%|percent\b|x\b)", re.IGNORECASE)


class ResumeValidationReport(BaseModel):
    status: str = "passed"  # passed | failed
    blocking_issues: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    unsupported_claims: list[str] = Field(default_factory=list)

    @property
    def passed(self) -> bool:
        return not self.blocking_issues


def validate_tailored_resume(
    tailored_text: str,
    base_text: str,
    plan: ResumeTailoringResult,
    bundle: CandidateBundle,
) -> ResumeValidationReport:
    report = ResumeValidationReport()
    base_lower = base_text.lower()
    tailored_lower = tailored_text.lower()

    # Candidate name must be present and correct (docs/17).
    full_name = bundle.profile.personal.full_name
    if full_name and full_name.lower() not in tailored_lower:
        report.blocking_issues.append(
            f"Candidate name '{full_name}' is missing from the tailored resume."
        )

    # Employment dates unchanged: no year may appear that the base lacks,
    # and no year from the base may disappear (docs/07B Prohibited Changes).
    base_years = set(_YEAR.findall(base_text))
    tailored_years = set(_YEAR.findall(tailored_text))
    invented = tailored_years - base_years
    if invented:
        report.blocking_issues.append(
            f"Tailored resume introduces years not present in the base resume: "
            f"{sorted(invented)}."
        )
    removed = base_years - tailored_years
    if removed:
        report.blocking_issues.append(
            f"Tailored resume dropped employment years from the base resume: "
            f"{sorted(removed)}."
        )

    # Every reordered skill must be supported by the base resume or CKB.
    candidate_text = " ".join(
        [base_lower] + [doc.lower() for doc in bundle.documents.values()]
    )
    for skill in plan.skills_order:
        if skill.lower() not in candidate_text:
            report.blocking_issues.append(
                f"Skill '{skill}' in the tailored skills list is not supported by "
                "the base resume or candidate files."
            )

    # Revised bullets must trace to real base content and not invent metrics.
    for bullet in plan.revised_bullets:
        if bullet.original and bullet.original not in base_text:
            report.warnings.append(
                f"Revised bullet original was not found in the base resume "
                f"(change skipped): {bullet.original[:80]}"
            )
            continue
        base_metrics = set(m.lower() for m in _METRIC.findall(bullet.original))
        new_metrics = set(m.lower() for m in _METRIC.findall(bullet.revised))
        invented_metrics = new_metrics - base_metrics
        if invented_metrics:
            report.blocking_issues.append(
                f"Revised bullet introduces unsupported metrics {sorted(invented_metrics)}: "
                f"{bullet.revised[:80]}"
            )
        if not bullet.supporting_sources:
            report.warnings.append(
                f"Revised bullet has no supporting sources: {bullet.revised[:80]}"
            )

    # The provider must not have flagged its own unsupported claims.
    if plan.unsupported_claims:
        report.unsupported_claims = list(plan.unsupported_claims)
        report.warnings.append(
            "The tailoring plan reported unsupported claims; they were not applied."
        )

    # The summary must not introduce metrics absent from the base resume.
    if plan.professional_summary:
        summary_metrics = set(m.lower() for m in _METRIC.findall(plan.professional_summary))
        base_metrics_all = set(m.lower() for m in _METRIC.findall(base_text))
        invented_summary = summary_metrics - base_metrics_all
        if invented_summary:
            report.blocking_issues.append(
                f"Professional summary introduces unsupported metrics: "
                f"{sorted(invented_summary)}."
            )

    report.status = "passed" if report.passed else "failed"
    return report
