"""Base resume selection and tailored resume rendering (docs/07B).

Selection priority: ranking suggestion (validated) → single available resume →
provider selection. Tailoring applies only provider-planned bullet rewrites on
top of the unchanged base text, then prepends summary/skills sections — the
MVP produces ATS-readable plain text, not visual redesign (docs/17 Phase 3).
"""

from __future__ import annotations

from pydantic import BaseModel

from job_platform.candidate.context import resume_inventory
from job_platform.candidate.models import CandidateBundle, ResumeDocument
from job_platform.jobs.models import Job, JobAnalysis
from job_platform.providers.base import ReasoningProvider
from job_platform.providers.tasks import (
    ResumeSelectionRequest,
    ResumeSelectionResult,
    ResumeTailoringResult,
)
from job_platform.shared.errors import CandidateDataError
from job_platform.shared.logging import get_logger

logger = get_logger("preparation.resume")


class ResumeSelection(BaseModel):
    resume_id: str
    resume_name: str
    reason: str
    confidence: float = 0.0
    method: str  # ranking_suggestion | only_resume | provider


async def select_base_resume(
    bundle: CandidateBundle,
    job: Job,
    analysis: JobAnalysis,
    provider: ReasoningProvider,
    suggested_resume_id: str = "",
) -> tuple[ResumeSelection, ResumeDocument]:
    if not bundle.resumes:
        raise CandidateDataError(
            "No resumes are available in the Candidate Knowledge Base; add one "
            "to user_data/candidate/resume/ before preparing applications."
        )

    suggested = bundle.resume_by_id(suggested_resume_id) if suggested_resume_id else None
    if suggested is not None:
        return (
            ResumeSelection(
                resume_id=suggested.id,
                resume_name=suggested.name,
                reason="Suggested by the job ranking result.",
                confidence=0.8,
                method="ranking_suggestion",
            ),
            suggested,
        )

    if len(bundle.resumes) == 1:
        only = bundle.resumes[0]
        return (
            ResumeSelection(
                resume_id=only.id,
                resume_name=only.name,
                reason="Only one base resume is available.",
                confidence=1.0,
                method="only_resume",
            ),
            only,
        )

    result: ResumeSelectionResult = await provider.select_resume(
        ResumeSelectionRequest(
            job=job,
            analysis=analysis,
            resume_inventory=resume_inventory(bundle),
            candidate_rules=bundle.rules,
        )
    )
    chosen = bundle.resume_by_id(result.selected_resume_id)
    if chosen is None:
        logger.warning(
            "Provider selected unknown resume id '%s'; falling back to first resume.",
            result.selected_resume_id,
        )
        chosen = bundle.resumes[0]
    return (
        ResumeSelection(
            resume_id=chosen.id,
            resume_name=chosen.name,
            reason=result.reasoning or "Selected by the reasoning provider.",
            confidence=result.confidence,
            method="provider",
        ),
        chosen,
    )


def render_tailored_resume(base_text: str, plan: ResumeTailoringResult) -> str:
    """Apply approved bullet rewrites to the base text and prepend tailored
    summary/skills sections. Employment history text is otherwise unchanged."""
    body = base_text
    for bullet in plan.revised_bullets:
        if bullet.original and bullet.original in body and bullet.revised:
            body = body.replace(bullet.original, bullet.revised, 1)
        elif bullet.original and bullet.original not in body:
            logger.warning(
                "Tailoring bullet original not found in base resume; skipping: %.60s",
                bullet.original,
            )

    sections: list[str] = []
    if plan.professional_summary:
        sections.append(f"PROFESSIONAL SUMMARY\n{plan.professional_summary}")
    if plan.skills_order:
        sections.append("KEY SKILLS\n" + ", ".join(plan.skills_order))
    if sections:
        return "\n\n".join(sections) + "\n\n" + body
    return body
