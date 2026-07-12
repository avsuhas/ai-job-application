"""Manual completion package (docs/17 Phase 4).

Everything the user needs to complete an application by hand: the URL, the
documents, prepared answers with a sensitive-answer checklist, missing
answers, and upload/completion checklists. Rendered as reviewable Markdown
and stored inside the package.
"""

from __future__ import annotations

import json

from pydantic import BaseModel, Field

from job_platform.packages.models import PackageManifest
from job_platform.packages.store import PackageStore

HANDOFF_PATH = "manual/manual_completion.md"

_SENSITIVE_FAMILY_PREFIXES = ("work_authorization.", "demographic.", "legal.")


class HandoffAnswer(BaseModel):
    question_family: str
    question: str
    answer: str
    source: str
    sensitive: bool = False
    approved: bool = True


class ManualCompletionPackage(BaseModel):
    package_id: str
    company: str
    title: str
    application_url: str
    resume: str | None
    cover_letter: str | None
    answers: list[HandoffAnswer] = Field(default_factory=list)
    sensitive_answers: list[str] = Field(default_factory=list)
    missing_answers: list[str] = Field(default_factory=list)
    upload_checklist: list[str] = Field(default_factory=list)
    completion_checklist: list[str] = Field(default_factory=list)

    def render(self) -> str:
        lines = [
            f"# Manual application: {self.title} at {self.company}",
            "",
            f"Apply at: {self.application_url or 'NO APPLICATION URL RECORDED'}",
            "",
            "## Documents to upload",
        ]
        lines += [f"- [ ] {item}" for item in self.upload_checklist] or ["- (none)"]
        lines += ["", "## Prepared answers", ""]
        for answer in self.answers:
            flag = " ⚠ sensitive — verify before entering" if answer.sensitive else ""
            note = "" if answer.approved else " (generated draft — review wording)"
            lines.append(f"### {answer.question}{flag}")
            lines.append(f"{answer.answer}{note}")
            lines.append(f"_source: {answer.source}_")
            lines.append("")
        if self.missing_answers:
            lines += ["## Answers you must provide yourself", ""]
            lines += [f"- [ ] {item}" for item in self.missing_answers]
            lines.append("")
        lines += ["## Completion checklist", ""]
        lines += [f"- [ ] {item}" for item in self.completion_checklist]
        return "\n".join(lines) + "\n"


def build_manual_completion_package(
    manifest: PackageManifest, store: PackageStore
) -> ManualCompletionPackage:
    answers_raw = json.loads(
        store.read_artifact(manifest.package_id, "answers/prepared_answers.json")
    ).get("answers", [])
    try:
        unresolved = json.loads(
            store.read_artifact(manifest.package_id, "answers/unresolved_questions.json")
        ).get("questions", [])
    except Exception:  # noqa: BLE001 - optional artifact
        unresolved = []

    answers = [
        HandoffAnswer(
            question_family=a["question_family"],
            question=a["canonical_question"],
            answer=a["answer"],
            source=a["source"],
            sensitive=a["question_family"].startswith(_SENSITIVE_FAMILY_PREFIXES),
            approved=a.get("approved", True),
        )
        for a in answers_raw
    ]

    upload_checklist = []
    if manifest.selected_resume:
        upload_checklist.append(f"Resume: {manifest.selected_resume}")
    if manifest.cover_letter:
        upload_checklist.append(f"Cover letter: {manifest.cover_letter}")

    package = ManualCompletionPackage(
        package_id=manifest.package_id,
        company=manifest.job.company,
        title=manifest.job.title,
        application_url=manifest.job.application_url,
        resume=manifest.selected_resume,
        cover_letter=manifest.cover_letter,
        answers=answers,
        sensitive_answers=[a.question_family for a in answers if a.sensitive],
        missing_answers=[
            f"{q.get('question_family')}: {q.get('reason')}" for q in unresolved
        ],
        upload_checklist=upload_checklist,
        completion_checklist=[
            "Open the application URL in your browser",
            "Fill personal information from the prepared answers",
            "Upload the documents listed above",
            "Enter the prepared answers, double-checking sensitive ones",
            "Provide any answers listed as missing",
            "Review everything on the final page before submitting",
            "Submit the application",
            "Mark this application as submitted so it is recorded in the tracker",
        ],
    )
    store.write_artifact(manifest, HANDOFF_PATH, package.render())
    store.save_manifest(manifest)
    return package
