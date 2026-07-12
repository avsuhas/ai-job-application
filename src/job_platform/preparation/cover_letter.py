"""Cover letter requirement detection, generation, and validation (docs/07C-1).

Decision order (simplified for the preparation MVP — form-detected required
fields arrive with the form engine in a later phase):
explicit user instruction → candidate rule → global setting → default no.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from job_platform.candidate.context import build_candidate_context
from job_platform.candidate.models import CandidateBundle
from job_platform.jobs.models import Job, JobAnalysis
from job_platform.providers.base import ReasoningProvider
from job_platform.providers.tasks import CoverLetterDraft, CoverLetterRequest
from job_platform.shared.config import Settings

_GENERIC_FLATTERY = (
    "world-renowned",
    "global leader",
    "industry leader",
    "prestigious company",
    "dream company",
)


class CoverLetterDecision(BaseModel):
    status: str  # required | optional | not_requested | disabled
    generate: bool
    reason: str
    source: str


class CoverLetterValidation(BaseModel):
    status: str = "passed"
    blocking_issues: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)

    @property
    def passed(self) -> bool:
        return not self.blocking_issues


def decide_cover_letter(
    settings: Settings, bundle: CandidateBundle, explicit_request: bool | None = None
) -> CoverLetterDecision:
    if explicit_request is True:
        return CoverLetterDecision(
            status="required",
            generate=True,
            reason="The user requested a cover letter for this application.",
            source="user_instruction",
        )
    if explicit_request is False:
        return CoverLetterDecision(
            status="disabled",
            generate=False,
            reason="The user disabled the cover letter for this application.",
            source="user_instruction",
        )

    for line in bundle.rules.lower().splitlines():
        if "cover letter" not in line:
            continue
        if "never" in line or "no cover letter" in line or "don't" in line:
            return CoverLetterDecision(
                status="disabled",
                generate=False,
                reason=f"Candidate rule: {line.strip()}",
                source="candidate_rule",
            )
        if "always" in line:
            return CoverLetterDecision(
                status="required",
                generate=True,
                reason=f"Candidate rule: {line.strip()}",
                source="candidate_rule",
            )

    if settings.applications.generate_cover_letter:
        return CoverLetterDecision(
            status="optional",
            generate=True,
            reason="Cover letter generation is enabled in application settings.",
            source="global_setting",
        )
    return CoverLetterDecision(
        status="not_requested",
        generate=False,
        reason="No rule or setting requests a cover letter; defaulting to none.",
        source="default",
    )


def validate_cover_letter(
    draft: CoverLetterDraft, job: Job, max_words: int = 400
) -> CoverLetterValidation:
    validation = CoverLetterValidation()
    text = draft.render()
    text_lower = text.lower()

    if job.company.lower() not in text_lower:
        validation.blocking_issues.append(
            f"The cover letter never mentions the company '{job.company}'."
        )
    if job.title and job.title.lower() not in text_lower:
        validation.warnings.append(
            f"The cover letter does not mention the role title '{job.title}'."
        )
    if draft.unsupported_claims:
        validation.blocking_issues.append(
            f"The draft reports unsupported claims: {draft.unsupported_claims}."
        )

    word_count = sum(len(p.split()) for p in draft.body_paragraphs)
    if word_count > max_words:
        validation.warnings.append(
            f"Cover letter body is {word_count} words (maximum {max_words})."
        )
    for phrase in _GENERIC_FLATTERY:
        if phrase in text_lower:
            validation.warnings.append(f"Generic flattery detected: '{phrase}'.")

    validation.status = "passed" if validation.passed else "failed"
    return validation


async def prepare_cover_letter(
    provider: ReasoningProvider,
    job: Job,
    analysis: JobAnalysis,
    bundle: CandidateBundle,
    max_words: int = 400,
) -> tuple[CoverLetterDraft, CoverLetterValidation]:
    draft = await provider.generate_cover_letter(
        CoverLetterRequest(
            job=job,
            analysis=analysis,
            candidate_context=build_candidate_context(
                bundle, resume=bundle.resumes[0] if bundle.resumes else None
            ),
            template=bundle.documents.get("cover_letter_template", ""),
            max_words=max_words,
        )
    )
    return draft, validate_cover_letter(draft, job, max_words)
