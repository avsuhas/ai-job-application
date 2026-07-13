"""Application Review service (docs/07D-1, preparation stage).

Deterministic cross-artifact checks that run in code, independent of the
provider, so contaminated or inconsistent materials cannot reach submission.
Browser-stage review (form values, review-page extraction) arrives with the
browser engine in a later phase.
"""

from __future__ import annotations

import json
import re

from job_platform.candidate.models import CandidateBundle
from job_platform.packages.models import PackageManifest
from job_platform.packages.store import PackageStore
from job_platform.review.models import ReviewFinding, ReviewReport, ReviewStatus, Severity
from job_platform.security.injection import scan_for_injection
from job_platform.shared.errors import StorageError
from job_platform.shared.ids import sha256_text
from job_platform.shared.logging import get_logger

logger = get_logger("review.service")

REVIEW_REPORT_PATH = "review/review_report.json"

# Artifacts whose content is generated per-application and therefore must not
# reference a different employer than the target company.
_GENERATED_TEXT_ARTIFACTS = [
    ("cover_letter/cover_letter.md", "cover_letter"),
    ("resume/tailored_resume.md", "resume"),
]


class ReviewService:
    def __init__(
        self,
        store: PackageStore,
        known_companies: list[str] | None = None,
        block_on_high_severity: bool = True,
    ) -> None:
        self._store = store
        self._known_companies = known_companies or []
        self._block_on_high_severity = block_on_high_severity

    def review(self, manifest: PackageManifest, bundle: CandidateBundle) -> ReviewReport:
        report = ReviewReport(package_id=manifest.package_id)
        try:
            self._check_package_integrity(manifest, report)
            self._check_staleness(manifest, bundle, report)
            self._check_job_identity(manifest, report)
            self._check_cross_company_contamination(manifest, bundle, report)
            self._check_candidate_facts(manifest, bundle, report)
            self._check_work_authorization(manifest, report)
            self._check_resume(manifest, report)
            self._check_cover_letter(manifest, report)
            self._check_answers(manifest, report)
            self._check_injection(manifest, report)
            report.status = report.derive_status(self._block_on_high_severity)
        except Exception as exc:  # noqa: BLE001 - a broken package must fail review, not crash
            logger.exception("Review failed for package %s", manifest.package_id)
            report.findings.append(
                ReviewFinding(
                    category="review_failure",
                    severity=Severity.BLOCKING,
                    message=f"The review itself could not complete: {exc}",
                )
            )
            report.status = ReviewStatus.FAILED

        self._store.write_artifact(manifest, REVIEW_REPORT_PATH, report.model_dump_json(indent=2))
        self._store.save_manifest(manifest)
        return report

    # ------------------------------------------------------------------ #

    def _read_text(self, manifest: PackageManifest, path: str) -> str | None:
        """Read an artifact; a missing file returns None because the
        integrity check has already produced a blocking finding for it."""
        if path not in manifest.artifacts:
            return None
        try:
            return self._store.read_artifact(manifest.package_id, path)
        except StorageError:
            return None

    def _read_json(self, manifest: PackageManifest, path: str) -> dict | None:
        text = self._read_text(manifest, path)
        return json.loads(text) if text is not None else None

    def _check_package_integrity(self, manifest: PackageManifest, report: ReviewReport) -> None:
        package_dir = self._store.package_dir(manifest.package_id)
        for path, record in sorted(manifest.artifacts.items()):
            if path == REVIEW_REPORT_PATH:
                continue
            file_path = package_dir / path
            if not file_path.exists():
                report.findings.append(
                    ReviewFinding(
                        category="package_integrity",
                        severity=Severity.BLOCKING,
                        artifact=path,
                        message=f"Artifact '{path}' is recorded in the manifest but missing.",
                        recommended_action="Re-run preparation for this package.",
                    )
                )
                continue
            current = sha256_text(file_path.read_text(encoding="utf-8"))
            if current != record.sha256:
                report.findings.append(
                    ReviewFinding(
                        category="package_integrity",
                        severity=Severity.BLOCKING,
                        artifact=path,
                        message=(
                            f"Artifact '{path}' was modified outside the application "
                            "(hash mismatch with the manifest)."
                        ),
                        evidence=[f"expected {record.sha256[:12]}…, found {current[:12]}…"],
                        recommended_action="Re-run preparation or restore the artifact.",
                    )
                )
            report.reviewed_artifacts.append(path)

    def _check_staleness(
        self, manifest: PackageManifest, bundle: CandidateBundle, report: ReviewReport
    ) -> None:
        stale = self._store.stale_sources(manifest, bundle)
        if stale:
            report.findings.append(
                ReviewFinding(
                    category="stale_package",
                    severity=Severity.HIGH,
                    message=(
                        "Candidate files changed after this package was prepared: "
                        + ", ".join(stale)
                    ),
                    evidence=stale,
                    recommended_action="Re-prepare the package from current candidate data.",
                    automatically_correctable=True,
                )
            )

    def _check_job_identity(self, manifest: PackageManifest, report: ReviewReport) -> None:
        job = self._read_json(manifest, "job/job.json")
        if job is None:
            report.findings.append(
                ReviewFinding(
                    category="job_identity",
                    severity=Severity.BLOCKING,
                    artifact="job/job.json",
                    message="The package has no job snapshot.",
                )
            )
            return
        for field in ("company", "title", "job_id"):
            snapshot_value = job.get(field, "")
            manifest_value = getattr(manifest.job, field if field != "job_id" else "job_id")
            if snapshot_value != manifest_value:
                report.findings.append(
                    ReviewFinding(
                        category="job_identity",
                        severity=Severity.BLOCKING,
                        artifact="job/job.json",
                        message=(
                            f"Job snapshot {field} ({snapshot_value!r}) does not match "
                            f"the manifest ({manifest_value!r})."
                        ),
                    )
                )
        if not manifest.job.application_url:
            report.findings.append(
                ReviewFinding(
                    category="job_identity",
                    severity=Severity.HIGH,
                    message="The package has no application URL for submission or handoff.",
                )
            )

    def _check_cross_company_contamination(
        self, manifest: PackageManifest, bundle: CandidateBundle, report: ReviewReport
    ) -> None:
        target = manifest.job.company.lower()
        # Employers appearing in the candidate's own materials are legitimate.
        candidate_text = " ".join(
            [r.text.lower() for r in bundle.resumes]
            + [bundle.profile.employment.current_company.lower()]
        )
        suspects = [
            name
            for name in self._known_companies
            if name.lower() != target and name.lower() not in candidate_text
        ]
        if not suspects:
            return
        for path, artifact in _GENERATED_TEXT_ARTIFACTS:
            text = self._read_text(manifest, path)
            if not text:
                continue
            lowered = text.lower()
            for name in suspects:
                if re.search(rf"\b{re.escape(name.lower())}\b", lowered):
                    report.findings.append(
                        ReviewFinding(
                            category="cross_company_contamination",
                            severity=Severity.BLOCKING,
                            artifact=artifact,
                            message=(
                                f"The {artifact.replace('_', ' ')} references "
                                f"'{name}' in an application to {manifest.job.company}."
                            ),
                            recommended_action=(
                                "Regenerate the artifact for the correct company."
                            ),
                        )
                    )

    def _check_candidate_facts(
        self, manifest: PackageManifest, bundle: CandidateBundle, report: ReviewReport
    ) -> None:
        answers = self._read_json(manifest, "answers/prepared_answers.json")
        if answers is None:
            return
        profile = bundle.profile.model_dump(mode="json")
        for answer in answers.get("answers", []):
            source = answer.get("source", "")
            if not source.startswith("candidate.json:"):
                continue
            dotted = source.split(":", 1)[1]
            node = profile
            for part in dotted.split("."):
                node = node.get(part, {}) if isinstance(node, dict) else {}
            expected = node if not isinstance(node, dict) else None
            if expected is None:
                continue
            if isinstance(expected, bool):
                expected = "Yes" if expected else "No"
            if str(expected) != str(answer.get("answer", "")):
                report.findings.append(
                    ReviewFinding(
                        category="candidate_fact_mismatch",
                        severity=Severity.BLOCKING,
                        artifact="answers/prepared_answers.json",
                        message=(
                            f"Prepared answer '{answer.get('question_family')}' "
                            f"({answer.get('answer')!r}) no longer matches the "
                            f"candidate fact {dotted!r} ({expected!r})."
                        ),
                        recommended_action="Re-prepare answers from current candidate data.",
                        automatically_correctable=True,
                    )
                )

    def _check_work_authorization(self, manifest: PackageManifest, report: ReviewReport) -> None:
        ranking = self._read_json(manifest, "job/ranking.json")
        if ranking:
            for flag in ranking.get("eligibility_flags", []):
                report.findings.append(
                    ReviewFinding(
                        category="work_authorization",
                        severity=Severity.HIGH,
                        message=f"Eligibility conflict recorded at ranking time: {flag}",
                        recommended_action=(
                            "Confirm eligibility before submitting this application."
                        ),
                    )
                )
        answers = self._read_json(manifest, "answers/prepared_answers.json") or {}
        by_family = {a["question_family"]: a for a in answers.get("answers", [])}
        authorized = by_family.get("work_authorization.authorized_now", {}).get("answer")
        sponsorship = by_family.get("work_authorization.sponsorship_now", {}).get("answer")
        if authorized == "No" and sponsorship == "No":
            report.findings.append(
                ReviewFinding(
                    category="work_authorization",
                    severity=Severity.HIGH,
                    artifact="answers/prepared_answers.json",
                    message=(
                        "Contradiction: not authorized to work but also not requiring "
                        "sponsorship. One of these answers is likely wrong."
                    ),
                    requires_user_input=True,
                )
            )

    def _check_resume(self, manifest: PackageManifest, report: ReviewReport) -> None:
        if manifest.selected_resume == "resume/tailored_resume.md":
            validation = self._read_json(manifest, "resume/validation_report.json")
            if validation is None or validation.get("status") != "passed":
                report.findings.append(
                    ReviewFinding(
                        category="resume",
                        severity=Severity.BLOCKING,
                        artifact="resume/tailored_resume.md",
                        message=(
                            "The tailored resume is selected but has no passing "
                            "validation report."
                        ),
                    )
                )
        elif not manifest.selected_resume:
            report.findings.append(
                ReviewFinding(
                    category="resume",
                    severity=Severity.BLOCKING,
                    message="No resume is selected for this application.",
                )
            )

    def _check_cover_letter(self, manifest: PackageManifest, report: ReviewReport) -> None:
        metadata = self._read_json(manifest, "cover_letter/metadata.json")
        if manifest.cover_letter:
            validation = (metadata or {}).get("validation", {})
            if validation.get("status") != "passed":
                report.findings.append(
                    ReviewFinding(
                        category="cover_letter",
                        severity=Severity.BLOCKING,
                        artifact=manifest.cover_letter,
                        message="The attached cover letter did not pass validation.",
                    )
                )
        elif metadata and not metadata.get("decision", {}).get("generate", False):
            report.findings.append(
                ReviewFinding(
                    category="cover_letter",
                    severity=Severity.INFORMATIONAL,
                    message=(
                        "No cover letter was generated: "
                        + metadata.get("decision", {}).get("reason", "")
                    ),
                )
            )

    def _check_answers(self, manifest: PackageManifest, report: ReviewReport) -> None:
        unresolved = self._read_json(manifest, "answers/unresolved_questions.json") or {}
        for question in unresolved.get("questions", []):
            required = bool(question.get("required_for_readiness"))
            report.findings.append(
                ReviewFinding(
                    category="unresolved_answer",
                    severity=Severity.HIGH if required else Severity.LOW,
                    artifact="answers/unresolved_questions.json",
                    message=(
                        f"Unresolved question '{question.get('question_family')}': "
                        f"{question.get('reason')}"
                    ),
                    # Optional blanks are warnings (docs/07D-1 approved-with-
                    # warnings); only required answers force user input.
                    requires_user_input=required,
                    recommended_action="Provide this answer before applying.",
                )
            )
            if required:
                report.required_user_actions.append(
                    f"Provide an answer for {question.get('question_family')}"
                )
        answers_doc = self._read_json(manifest, "answers/prepared_answers.json") or {}
        unapproved = [
            a["question_family"]
            for a in answers_doc.get("answers", [])
            if not a.get("approved", False)
        ]
        if unapproved:
            report.findings.append(
                ReviewFinding(
                    category="unapproved_narrative",
                    severity=Severity.LOW,
                    artifact="answers/prepared_answers.json",
                    message=(
                        "Generated narrative answers await user review: "
                        + ", ".join(unapproved)
                    ),
                )
            )
            report.required_user_actions.append("Review and approve narrative answers")

    def _check_injection(self, manifest: PackageManifest, report: ReviewReport) -> None:
        """Flag prompt-injection phrasing in the (untrusted) job description
        snapshot so the user is aware before submission (docs/12)."""
        description = self._read_text(manifest, "job/raw_description.txt")
        if not description:
            return
        scan = scan_for_injection(description)
        if scan.detected:
            report.findings.append(
                ReviewFinding(
                    category="prompt_injection",
                    severity=Severity.MEDIUM,
                    artifact="job/raw_description.txt",
                    message=(
                        "The job description contains instruction-like content "
                        "that may be a prompt-injection attempt. It was treated "
                        "as untrusted data; review before submitting."
                    ),
                    evidence=scan.matches,
                )
            )
