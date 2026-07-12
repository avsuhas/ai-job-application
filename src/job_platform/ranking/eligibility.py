"""Deterministic eligibility checks (docs/02D Eligibility Analysis, docs/04 Phase 3).

These run in code, not in the model, so hard conflicts are flagged even if the
provider misses them. Checks are conservative: they only flag conflicts that
follow directly from structured candidate facts.
"""

from __future__ import annotations

from job_platform.candidate.models import CandidateBundle
from job_platform.jobs.models import JobAnalysis

_CITIZENSHIP_MARKERS = ("citizen", "citizenship", "permanent resident", "green card")
_NO_SPONSORSHIP_MARKERS = (
    "no sponsorship",
    "not offer sponsorship",
    "without sponsorship",
    "unable to sponsor",
    "will not sponsor",
    "sponsorship is not available",
)


def eligibility_flags(analysis: JobAnalysis, bundle: CandidateBundle) -> list[str]:
    flags: list[str] = []
    auth = bundle.profile.work_authorization
    requirements = [
        r.lower()
        for r in (analysis.work_authorization_requirements + analysis.hard_requirements)
    ]

    if auth.authorized_to_work is False:
        flags.append("Candidate is not authorized to work in the target country.")

    if auth.requires_sponsorship:
        if any(m in r for r in requirements for m in _CITIZENSHIP_MARKERS):
            flags.append(
                "Job requires citizenship or permanent residency but the candidate "
                "requires sponsorship."
            )
        elif any(m in r for r in requirements for m in _NO_SPONSORSHIP_MARKERS):
            flags.append(
                "Job does not offer visa sponsorship but the candidate requires it."
            )

    if analysis.security_clearance_requirements:
        candidate_text = " ".join(
            [bundle.notes.lower(), bundle.answers.lower(), bundle.rules.lower()]
        )
        if "clearance" not in candidate_text:
            flags.append(
                "Job requires a security clearance that is not recorded in the "
                "candidate knowledge base."
            )
    return flags
