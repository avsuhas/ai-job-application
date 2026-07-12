"""Map classified fields to prepared answers and build the interaction plan
(docs/09 Form Plan Builder, docs/17 Phase 6 confidence rules).

- High-confidence classification + stored answer → planned automatically.
- Medium confidence → planned but flagged for review.
- Low confidence, missing answers, or unmatched options → surfaced, never
  guessed and never filled with placeholders (docs/09 Unknown Fields).
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field

from job_platform.browser.models import (
    BrowserAction,
    FieldType,
    FormField,
    InteractionPlan,
    InteractionStep,
)
from job_platform.forms.semantic import AUTO_CONFIDENCE, SemanticClassification
from job_platform.preparation.answers import PreparedAnswerSet

# Semantic families whose stored answer can satisfy a related question.
_FAMILY_FALLBACKS = {
    "work_authorization.sponsorship_future": "work_authorization.sponsorship_now",
    "personal.state": "personal.state",
}

_SENSITIVE_PREFIXES = ("demographic.", "legal.")


class PlanEntryStatus(StrEnum):
    PLANNED = "planned"
    NEEDS_REVIEW = "needs_review"  # planned, but flagged for review mode
    NO_STORED_ANSWER = "no_stored_answer"
    OPTION_MISMATCH = "option_mismatch"
    UNSUPPORTED_WIDGET = "unsupported_widget"
    UNKNOWN_FIELD = "unknown_field"
    SENSITIVE_SKIPPED = "sensitive_skipped"


class PlanEntry(BaseModel):
    field_id: str
    label: str = ""
    semantic_type: str = "unknown"
    classification_method: str = "none"
    confidence: int = 0
    status: PlanEntryStatus
    answer_source: str = ""
    required: bool = False
    note: str = ""


class FormPlan(BaseModel):
    plan: InteractionPlan
    entries: list[PlanEntry] = Field(default_factory=list)

    @property
    def unresolved_required(self) -> list[PlanEntry]:
        return [
            e
            for e in self.entries
            if e.required
            and e.status
            not in (PlanEntryStatus.PLANNED, PlanEntryStatus.NEEDS_REVIEW)
        ]


def match_option(options: list[str], answer: str) -> str | None:
    """Map a stored answer onto one of the widget's options (docs/06)."""
    normalized = answer.strip().lower()
    for option in options:
        if option.strip().lower() == normalized:
            return option
    truthy = {"yes", "true"}
    falsy = {"no", "false"}
    if normalized in truthy or normalized in falsy:
        wanted = "yes" if normalized in truthy else "no"
        for option in options:
            if option.strip().lower() == wanted:
                return option
    for option in options:
        lowered = option.strip().lower()
        if normalized and (normalized in lowered or lowered in normalized):
            return option
    return None


def _action_for(field: FormField) -> BrowserAction | None:
    if field.field_type in (
        FieldType.TEXT,
        FieldType.TEXTAREA,
        FieldType.EMAIL,
        FieldType.PHONE,
        FieldType.NUMBER,
        FieldType.URL,
        FieldType.DATE,
    ):
        return BrowserAction.FILL
    if field.field_type == FieldType.SELECT:
        return BrowserAction.SELECT_OPTION
    if field.field_type == FieldType.RADIO:
        return BrowserAction.SELECT_RADIO
    if field.field_type == FieldType.CHECKBOX:
        return BrowserAction.SET_CHECKBOX
    if field.field_type == FieldType.FILE:
        return BrowserAction.UPLOAD_FILE
    return None


def _lookup_answer(
    semantic_type: str, answers: PreparedAnswerSet
) -> tuple[str, str] | None:
    """Return (value, source) for a semantic family, with fallbacks."""
    direct = answers.answer_for(semantic_type)
    if direct is not None:
        return direct.answer, direct.source
    fallback_family = _FAMILY_FALLBACKS.get(semantic_type)
    if fallback_family:
        fallback = answers.answer_for(fallback_family)
        if fallback is not None:
            return fallback.answer, fallback.source
    if semantic_type == "personal.full_name":
        first = answers.answer_for("personal.first_name")
        last = answers.answer_for("personal.last_name")
        if first and last:
            return f"{first.answer} {last.answer}", "computed:first_name+last_name"
    return None


def build_form_plan(
    fields: list[FormField],
    classifications: dict[str, SemanticClassification],
    answers: PreparedAnswerSet,
    documents: dict[str, str] | None = None,
    fill_sensitive: bool = False,
) -> FormPlan:
    """Build the interaction plan for one page.

    ``documents`` maps document families (documents.resume,
    documents.cover_letter) to absolute file paths for upload fields.
    """
    documents = documents or {}
    steps: list[InteractionStep] = []
    entries: list[PlanEntry] = []
    step_counter = 0

    for field in fields:
        if not field.visible or not field.enabled or field.read_only:
            continue
        if field.field_type in (FieldType.HIDDEN, FieldType.PASSWORD):
            continue
        classification = classifications.get(
            field.field_id, SemanticClassification(field_id=field.field_id)
        )

        def entry(
            status: PlanEntryStatus,
            note: str = "",
            source: str = "",
            _field: FormField = field,
            _classification: SemanticClassification = classification,
        ) -> None:
            entries.append(
                PlanEntry(
                    field_id=_field.field_id,
                    label=_field.label or _field.section,
                    semantic_type=_classification.semantic_type,
                    classification_method=_classification.method,
                    confidence=_classification.confidence,
                    status=status,
                    answer_source=source,
                    required=_field.required,
                    note=note,
                )
            )

        if not classification.usable:
            entry(
                PlanEntryStatus.UNKNOWN_FIELD,
                "The field could not be classified confidently; provide this "
                "answer manually.",
            )
            continue

        semantic = classification.semantic_type
        if semantic.startswith(_SENSITIVE_PREFIXES) and not fill_sensitive:
            entry(
                PlanEntryStatus.SENSITIVE_SKIPPED,
                "Sensitive question left for the user by policy.",
            )
            continue

        action = _action_for(field)
        if action is None:
            entry(
                PlanEntryStatus.UNSUPPORTED_WIDGET,
                f"Widget type '{field.field_type.value}' is not supported by the "
                "generic engine; complete manually.",
            )
            continue

        if action == BrowserAction.UPLOAD_FILE:
            path = documents.get(semantic)
            if not path:
                entry(PlanEntryStatus.NO_STORED_ANSWER, "No document available to upload.")
                continue
            value, source = path, f"package:{semantic}"
        else:
            looked_up = _lookup_answer(semantic, answers)
            if looked_up is None:
                entry(
                    PlanEntryStatus.NO_STORED_ANSWER,
                    "No stored answer for this question; provide it manually.",
                )
                continue
            value, source = looked_up

        if action in (BrowserAction.SELECT_OPTION, BrowserAction.SELECT_RADIO):
            matched = match_option(field.options, value)
            if matched is None:
                entry(
                    PlanEntryStatus.OPTION_MISMATCH,
                    f"Stored answer does not match any of the {len(field.options)} "
                    "available options.",
                    source,
                )
                continue
            value = matched

        step_counter += 1
        steps.append(
            InteractionStep(
                step_id=f"step_{step_counter}",
                field_id=field.field_id,
                action=action,
                value=value,
            )
        )
        entry(
            PlanEntryStatus.PLANNED
            if classification.confidence >= AUTO_CONFIDENCE
            else PlanEntryStatus.NEEDS_REVIEW,
            source=source,
        )

    return FormPlan(plan=InteractionPlan(steps=steps), entries=entries)
