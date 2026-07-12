"""Form boundary detection (docs/09).

A page may contain several unrelated forms (search, newsletter, login,
application). The detector scores each form's fields and actions and selects
the application form — or none, when no candidate looks application-related.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from job_platform.browser.models import FieldType, FormAction, FormField

_APPLICATION_LABEL_MARKERS = (
    "first name", "last name", "full name", "email", "phone", "resume", "cv",
    "cover letter", "linkedin", "work authorization", "sponsor", "salary",
    "experience", "education", "why do you want",
)
_NEGATIVE_LABEL_MARKERS = ("search", "keyword", "newsletter", "subscribe")
_APPLICATION_ACTION_MARKERS = ("apply", "submit application", "continue", "next", "save")


class FormCandidate(BaseModel):
    form_id: str
    field_count: int = 0
    score: int = 0
    application_related: bool = False


class FormBoundaryResult(BaseModel):
    candidates: list[FormCandidate] = Field(default_factory=list)
    selected_form_id: str | None = None

    def selected_fields(self, fields: list[FormField]) -> list[FormField]:
        if self.selected_form_id is None:
            return []
        return [f for f in fields if f.form_id == self.selected_form_id]

    def selected_actions(self, actions: list[FormAction]) -> list[FormAction]:
        if self.selected_form_id is None:
            return []
        return [a for a in actions if a.form_id == self.selected_form_id]


def detect_form_boundary(
    fields: list[FormField], actions: list[FormAction]
) -> FormBoundaryResult:
    by_form: dict[str, list[FormField]] = {}
    for field in fields:
        if field.visible:
            by_form.setdefault(field.form_id or "(none)", []).append(field)

    candidates: list[FormCandidate] = []
    for form_id, form_fields in by_form.items():
        score = 0
        labels = [
            " ".join([f.label, f.placeholder, f.section]).lower() for f in form_fields
        ]
        for label in labels:
            if any(marker in label for marker in _APPLICATION_LABEL_MARKERS):
                score += 10
            if any(marker in label for marker in _NEGATIVE_LABEL_MARKERS):
                score -= 15
        # Login forms are not application forms.
        if any(f.field_type == FieldType.PASSWORD for f in form_fields):
            score -= 30
        if any(f.field_type == FieldType.FILE for f in form_fields):
            score += 15
        score += min(len(form_fields), 10)  # richer forms score higher

        form_actions = [a for a in actions if a.form_id == form_id]
        for action in form_actions:
            if any(m in action.label.lower() for m in _APPLICATION_ACTION_MARKERS):
                score += 5

        candidates.append(
            FormCandidate(
                form_id=form_id,
                field_count=len(form_fields),
                score=score,
                application_related=score >= 25,
            )
        )

    candidates.sort(key=lambda c: c.score, reverse=True)
    selected = next((c.form_id for c in candidates if c.application_related), None)
    return FormBoundaryResult(candidates=candidates, selected_form_id=selected)
