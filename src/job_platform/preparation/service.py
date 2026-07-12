"""Application preparation service (docs/07A lifecycle, docs/17 Phase 3).

Orchestrates package creation in the spec's implementation order:
manifest → snapshots → resume selection → tailoring → validation →
cover letter → answers → application plan → fingerprint → final status.

Failures degrade gracefully: a failed tailoring falls back to the base
resume, a failed cover letter or unresolved required answer marks the
package ``needs_attention`` instead of aborting it.
"""

from __future__ import annotations

import json

from pydantic import BaseModel

from job_platform.candidate.context import build_candidate_context
from job_platform.candidate.models import CandidateBundle
from job_platform.packages.models import (
    AttentionItem,
    PackageJobSummary,
    PackageManifest,
    PackageStatus,
)
from job_platform.packages.store import (
    PackageStore,
    candidate_source_fingerprints,
    make_package_id,
)
from job_platform.preparation.answers import prepare_answers
from job_platform.preparation.cover_letter import (
    decide_cover_letter,
    prepare_cover_letter,
)
from job_platform.preparation.resume import render_tailored_resume, select_base_resume
from job_platform.preparation.resume_validation import validate_tailored_resume
from job_platform.providers.base import ReasoningProvider
from job_platform.providers.tasks import ResumeTailoringRequest
from job_platform.ranking.models import RankedJob
from job_platform.shared.config import Settings
from job_platform.shared.errors import ProviderError
from job_platform.shared.logging import get_logger
from job_platform.storage.tracker import ApplicationTracker

logger = get_logger("preparation.service")


class PreparationOptions(BaseModel):
    tailor_resume: bool | None = None  # None = use global setting
    generate_cover_letter: bool | None = None  # None = decision order
    include_narrative_answers: bool = True


class PreparationService:
    def __init__(
        self,
        provider: ReasoningProvider,
        store: PackageStore,
        settings: Settings,
        tracker: ApplicationTracker | None = None,
    ) -> None:
        self._provider = provider
        self._store = store
        self._settings = settings
        self._tracker = tracker

    async def prepare(
        self,
        ranked: RankedJob,
        bundle: CandidateBundle,
        options: PreparationOptions | None = None,
    ) -> PackageManifest:
        options = options or PreparationOptions()
        job = ranked.job
        manifest = PackageManifest(
            package_id=make_package_id(job.company, job.job_id, job.title),
            job=PackageJobSummary(
                company=job.company,
                title=job.title,
                job_id=job.job_id,
                application_url=job.url,
            ),
            match_score=ranked.match.match_score if ranked.match else None,
            recommendation=ranked.recommendation.value,
            expected_ats=job.ats,
            automation_mode=self._settings.applications.automation_mode,
        )

        if self._tracker is not None and self._tracker.is_duplicate(job):
            manifest.status = PackageStatus.ALREADY_APPLIED
            manifest.attention_items.append(
                AttentionItem(
                    code="already_applied",
                    message="This job is already recorded in the application tracker.",
                )
            )
            self._store.save_manifest(manifest)
            return manifest

        try:
            await self._prepare_materials(manifest, ranked, bundle, options)
        except Exception as exc:  # noqa: BLE001 - preparation must record failures
            logger.exception("Preparation failed for package %s", manifest.package_id)
            manifest.status = PackageStatus.FAILED
            manifest.attention_items.append(
                AttentionItem(code="preparation_failed", message=str(exc))
            )
        self._store.save_manifest(manifest)
        return manifest

    async def _prepare_materials(
        self,
        manifest: PackageManifest,
        ranked: RankedJob,
        bundle: CandidateBundle,
        options: PreparationOptions,
    ) -> None:
        job = ranked.job
        analysis = ranked.analysis
        store = self._store

        # --- Immutable snapshots (docs/07A) -------------------------------
        manifest.status = PackageStatus.COLLECTING_CONTEXT
        store.write_artifact(
            manifest, "job/job.json", job.model_dump_json(indent=2, exclude={"raw"})
        )
        store.write_artifact(manifest, "job/raw_description.txt", job.description)
        if analysis is not None:
            store.write_artifact(manifest, "job/analysis.json", analysis.model_dump_json(indent=2))
        if ranked.match is not None:
            ranking_snapshot = ranked.match.model_dump()
            ranking_snapshot["recommendation"] = ranked.recommendation.value
            ranking_snapshot["eligibility_flags"] = ranked.eligibility_flags
            store.write_artifact(
                manifest, "job/ranking.json", json.dumps(ranking_snapshot, indent=2)
            )

        candidate_context = build_candidate_context(
            bundle, resume=bundle.resumes[0] if bundle.resumes else None
        )
        store.write_artifact(
            manifest,
            "candidate/context.json",
            json.dumps(
                {
                    "profile": bundle.profile.model_dump(mode="json"),
                    "context_markdown": candidate_context,
                },
                indent=2,
            ),
        )
        store.write_artifact(
            manifest, "candidate/rules_snapshot.md", bundle.rules or "No rules defined.\n"
        )
        manifest.source_fingerprints = candidate_source_fingerprints(bundle)

        if analysis is None:
            manifest.attention_items.append(
                AttentionItem(
                    code="missing_analysis",
                    message="The ranked job has no structured analysis; re-run ranking.",
                )
            )
            manifest.status = PackageStatus.NEEDS_ATTENTION
            return

        # --- Resume selection and tailoring (docs/07B) --------------------
        manifest.status = PackageStatus.SELECTING_RESUME
        suggested = ranked.match.suggested_resume if ranked.match else ""
        selection, base_resume = await select_base_resume(
            bundle, job, analysis, self._provider, suggested_resume_id=suggested
        )
        store.write_artifact(
            manifest,
            "resume/base_resume_reference.json",
            json.dumps(
                {
                    "resume_id": base_resume.id,
                    "original_path": str(base_resume.path),
                    "selection_reason": selection.reason,
                    "selection_method": selection.method,
                    "selection_confidence": selection.confidence,
                },
                indent=2,
            ),
        )
        manifest.selected_resume = f"candidate resume: {base_resume.name}"

        manifest.status = PackageStatus.GENERATING_MATERIALS
        tailor = (
            options.tailor_resume
            if options.tailor_resume is not None
            else self._settings.applications.tailor_resume
        )
        if tailor and base_resume.text:
            await self._tailor_resume(manifest, ranked, bundle, base_resume, candidate_context)
        elif tailor and not base_resume.text:
            manifest.attention_items.append(
                AttentionItem(
                    code="resume_text_unavailable",
                    message=(
                        f"No text could be extracted from {base_resume.name}; "
                        "the base resume will be used without tailoring."
                    ),
                    blocking=False,
                )
            )

        # --- Cover letter (docs/07C-1) -------------------------------------
        decision = decide_cover_letter(
            self._settings, bundle, explicit_request=options.generate_cover_letter
        )
        cover_metadata: dict = {"decision": decision.model_dump()}
        if decision.generate:
            try:
                draft, validation = await prepare_cover_letter(
                    self._provider, job, analysis, bundle
                )
                store.write_artifact(manifest, "cover_letter/cover_letter.md", draft.render())
                cover_metadata["validation"] = validation.model_dump()
                cover_metadata["word_count"] = draft.word_count
                if validation.passed:
                    manifest.cover_letter = "cover_letter/cover_letter.md"
                else:
                    manifest.attention_items.append(
                        AttentionItem(
                            code="cover_letter_invalid",
                            message="; ".join(validation.blocking_issues),
                        )
                    )
            except ProviderError as exc:
                manifest.attention_items.append(
                    AttentionItem(
                        code="cover_letter_failed",
                        message=f"Cover letter generation failed: {exc.message}",
                        blocking=False,
                    )
                )
        store.write_artifact(
            manifest, "cover_letter/metadata.json", json.dumps(cover_metadata, indent=2)
        )

        # --- Standard answers (docs/07C-2) ---------------------------------
        manifest.status = PackageStatus.VALIDATING
        answers = await prepare_answers(
            self._provider,
            job,
            bundle,
            include_narratives=options.include_narrative_answers,
        )
        store.write_artifact(
            manifest,
            "answers/prepared_answers.json",
            json.dumps({"answers": [a.model_dump() for a in answers.answers]}, indent=2),
        )
        store.write_artifact(
            manifest,
            "answers/unresolved_questions.json",
            json.dumps({"questions": [u.model_dump() for u in answers.unresolved]}, indent=2),
        )
        manifest.answers_file = "answers/prepared_answers.json"
        for unresolved in answers.unresolved:
            if unresolved.required_for_readiness:
                manifest.attention_items.append(
                    AttentionItem(
                        code=f"unresolved:{unresolved.question_family}",
                        message=unresolved.reason,
                    )
                )

        # --- Application plan (docs/07A) ------------------------------------
        plan = {
            "package_id": manifest.package_id,
            "application_url": job.url,
            "expected_ats": job.ats or "unknown",
            "automation_mode": manifest.automation_mode,
            "resume_file": manifest.selected_resume,
            "cover_letter_file": manifest.cover_letter,
            "review_before_submit": manifest.automation_mode != "automatic",
            "allow_account_creation": False,
            "stop_on_captcha": True,
            "stop_on_unknown_submission_state": True,
        }
        store.write_artifact(manifest, "plan/application_plan.json", json.dumps(plan, indent=2))

        manifest.status = (
            PackageStatus.NEEDS_ATTENTION
            if manifest.blocking_attention_items
            else PackageStatus.READY
        )

    async def _tailor_resume(
        self,
        manifest: PackageManifest,
        ranked: RankedJob,
        bundle: CandidateBundle,
        base_resume,
        candidate_context: str,
    ) -> None:
        store = self._store
        try:
            plan = await self._provider.tailor_resume(
                ResumeTailoringRequest(
                    job=ranked.job,
                    analysis=ranked.analysis,
                    resume_text=base_resume.text,
                    candidate_context=candidate_context,
                    candidate_rules=bundle.rules,
                )
            )
        except ProviderError as exc:
            manifest.attention_items.append(
                AttentionItem(
                    code="tailoring_failed",
                    message=(
                        f"Resume tailoring failed ({exc.message}); "
                        "the base resume will be used."
                    ),
                    blocking=False,
                )
            )
            return

        store.write_artifact(manifest, "resume/tailoring_plan.json", plan.model_dump_json(indent=2))
        tailored = render_tailored_resume(base_resume.text, plan)
        report = validate_tailored_resume(tailored, base_resume.text, plan, bundle)
        store.write_artifact(
            manifest, "resume/validation_report.json", report.model_dump_json(indent=2)
        )
        if report.passed:
            store.write_artifact(manifest, "resume/tailored_resume.md", tailored)
            manifest.selected_resume = "resume/tailored_resume.md"
        else:
            # A resume with blocking validation failures must not be used
            # (docs/07A); fall back to the untouched base resume.
            manifest.attention_items.append(
                AttentionItem(
                    code="tailored_resume_invalid",
                    message=(
                        "Tailored resume failed factual validation and was discarded: "
                        + "; ".join(report.blocking_issues)
                    ),
                    blocking=False,
                )
            )
