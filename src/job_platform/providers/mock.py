"""Deterministic mock provider for tests and offline development.

Produces plausible, repeatable analyses/rankings from simple keyword matching
so the full workflow can run without network access or an API key.
"""

from __future__ import annotations

import re

from job_platform.jobs.models import Job, JobAnalysis
from job_platform.providers.base import JobRankingRequest, ReasoningProvider
from job_platform.providers.tasks import (
    CoverLetterDraft,
    CoverLetterRequest,
    FormFieldResolution,
    FormFieldResolutionRequest,
    NarrativeAnswerRequest,
    NarrativeAnswerResult,
    ResumeSelectionRequest,
    ResumeSelectionResult,
    ResumeTailoringRequest,
    ResumeTailoringResult,
    RevisedBullet,
)
from job_platform.ranking.models import JobMatchResult

_KNOWN_SKILLS = [
    "python", "go", "java", "c++", "rust", "typescript", "javascript", "react",
    "fastapi", "django", "flask", "kubernetes", "docker", "terraform", "aws",
    "gcp", "azure", "kafka", "redis", "postgresql", "mysql", "spark", "pytorch",
    "tensorflow", "cuda", "linux", "sql", "graphql", "grpc",
]

_YEARS = re.compile(r"(\d+)\+?\s*(?:or more\s*)?years", re.IGNORECASE)


class MockReasoningProvider(ReasoningProvider):
    name = "mock"

    async def analyze_job(self, job: Job) -> JobAnalysis:
        text = f"{job.title}\n{job.description}".lower()
        skills = [s for s in _KNOWN_SKILLS if s in text]
        years_match = _YEARS.search(job.description)
        hard: list[str] = []
        if "clearance" in text:
            hard.append("Security clearance required")
        if "us citizen" in text or "u.s. citizen" in text:
            hard.append("US citizenship required")
        return JobAnalysis(
            job_family=job.title.split(",")[0][:60],
            seniority="senior" if "senior" in text else "",
            required_skills=skills[:6],
            preferred_skills=skills[6:10],
            required_experience_years=float(years_match.group(1)) if years_match else None,
            employment_type=job.employment_type,
            remote_status=job.remote_status,
            hard_requirements=hard,
        )

    async def rank_job(self, request: JobRankingRequest) -> JobMatchResult:
        context = request.candidate_context.lower()
        required = request.analysis.required_skills
        matched = [s for s in required if s.lower() in context]
        missing = [s for s in required if s.lower() not in context]
        if required:
            score = int(30 + 65 * (len(matched) / len(required)))
        else:
            score = 50
        first_resume = ""
        for line in request.resume_inventory.splitlines():
            if "id=" in line:
                first_resume = line.split("id=")[1].split()[0]
                break
        return JobMatchResult(
            match_score=score,
            matched_required_qualifications=matched,
            missing_required_qualifications=missing,
            eligibility_concerns=list(request.analysis.hard_requirements),
            suggested_resume=first_resume,
            reasoning=(
                f"Mock ranking: matched {len(matched)}/{len(required)} required "
                "skills against the candidate context."
            ),
            confidence=0.5,
        )

    async def select_resume(self, request: ResumeSelectionRequest) -> ResumeSelectionResult:
        ids = [
            line.split("id=")[1].split()[0]
            for line in request.resume_inventory.splitlines()
            if "id=" in line
        ]
        if not ids:
            ids = ["none"]
        family = request.analysis.job_family.lower()
        selected = next((i for i in ids if i in family or family.startswith(i)), ids[0])
        return ResumeSelectionResult(
            selected_resume_id=selected,
            reasoning=f"Mock selection: chose '{selected}' from {len(ids)} available resumes.",
            alternatives=[i for i in ids if i != selected],
            confidence=0.6,
        )

    async def tailor_resume(self, request: ResumeTailoringRequest) -> ResumeTailoringResult:
        resume_lower = request.resume_text.lower()
        # Reorder only skills that actually appear in the base resume.
        supported = [s for s in request.analysis.required_skills if s.lower() in resume_lower]
        bullets = [
            line.lstrip("- ").strip()
            for line in request.resume_text.splitlines()
            if line.strip().startswith("-")
        ]
        revised = []
        if bullets:
            revised.append(
                RevisedBullet(
                    original=bullets[0],
                    revised=bullets[0],
                    supporting_sources=["base_resume"],
                    reason="Mock tailoring keeps bullets unchanged.",
                )
            )
        return ResumeTailoringResult(
            professional_summary=(
                f"Engineer applying for {request.job.title} at {request.job.company}, "
                "with directly relevant experience."
            ),
            skills_order=supported,
            revised_bullets=revised,
            warnings=["Generated by the mock provider."],
        )

    async def generate_cover_letter(self, request: CoverLetterRequest) -> CoverLetterDraft:
        body = [
            f"I am writing to apply for the {request.job.title} role at "
            f"{request.job.company}.",
            "My background aligns with the responsibilities described in the posting, "
            "and I would welcome the chance to contribute.",
            "Thank you for your consideration.",
        ]
        name = ""
        for line in request.candidate_context.splitlines():
            if '"first_name"' in line:
                name = line.split(":")[1].strip().strip('",')
                break
        return CoverLetterDraft(
            body_paragraphs=body,
            signature_name=name,
            word_count=sum(len(p.split()) for p in body),
            candidate_sources=["candidate.json"],
            warnings=["Generated by the mock provider."],
        )

    async def generate_application_answer(
        self, request: NarrativeAnswerRequest
    ) -> NarrativeAnswerResult:
        answer = (
            f"I am interested in the {request.job.title} role at {request.job.company} "
            "because it matches my experience and career goals."
        )
        if request.character_limit:
            answer = answer[: request.character_limit]
        return NarrativeAnswerResult(
            answer=answer,
            candidate_sources=["answers.md"],
            confidence=0.5,
            warnings=["Generated by the mock provider."],
        )

    async def resolve_form_field(
        self, request: FormFieldResolutionRequest
    ) -> FormFieldResolution:
        # The mock never guesses: unknown fields require user input, which is
        # the safe behavior the engine must handle (docs/09 Unknown Fields).
        return FormFieldResolution(
            field_semantic_type="unknown",
            requires_user_input=True,
            confidence=0.2,
            notes="Mock provider does not classify unknown fields.",
        )
