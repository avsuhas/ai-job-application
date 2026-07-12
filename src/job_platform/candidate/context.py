"""Build trusted candidate context for reasoning tasks.

Sections follow the CKB answer-priority order (docs/02C): structured facts,
rules, reusable answers, preferences, resume, notes. Each task receives only
the sections it needs (docs/05 Context Construction) — unrelated personal
information must not be sent to the provider.
"""

from __future__ import annotations

import json

from job_platform.candidate.models import CandidateBundle, ResumeDocument

# Fields from candidate.json that are never needed for ranking/analysis and
# therefore excluded from provider-bound context by default.
_SENSITIVE_PERSONAL_FIELDS = {"address", "phone", "postal_code"}


def _structured_facts(bundle: CandidateBundle, *, include_contact: bool) -> str:
    data = bundle.profile.model_dump(mode="json")
    personal = data.get("personal", {})
    if not include_contact:
        for field in _SENSITIVE_PERSONAL_FIELDS:
            personal.pop(field, None)
    return json.dumps(data, indent=2, ensure_ascii=False)


def _section(title: str, body: str) -> str:
    return f"## {title}\n\n{body.strip()}\n"


def build_candidate_context(
    bundle: CandidateBundle,
    *,
    resume: ResumeDocument | None = None,
    include_answers: bool = False,
    include_notes: bool = True,
    include_contact: bool = False,
) -> str:
    """Render the unified candidate context in priority order."""
    sections: list[str] = [
        _section(
            "Candidate Facts (highest priority)",
            _structured_facts(bundle, include_contact=include_contact),
        )
    ]
    if bundle.rules:
        sections.append(_section("Candidate Rules (override preferences)", bundle.rules))
    if include_answers and bundle.answers:
        sections.append(_section("Approved Reusable Answers", bundle.answers))
    if bundle.preferences:
        sections.append(_section("Search Preferences", bundle.preferences))
    if resume is not None and resume.text:
        sections.append(_section(f"Resume ({resume.name})", resume.text))
    if include_notes and bundle.notes:
        sections.append(_section("Candidate Notes (lowest priority)", bundle.notes))
    return "\n".join(sections).strip()


def resume_inventory(bundle: CandidateBundle) -> str:
    """Short listing of available base resumes for resume-selection tasks."""
    if not bundle.resumes:
        return "No resumes available."
    lines = [f"- id={r.id} file={r.name} format={r.format}" for r in bundle.resumes]
    return "\n".join(lines)
