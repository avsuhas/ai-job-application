"""Semantic field classification (docs/09).

Maps visible form fields to canonical question families using deterministic
signals in the spec's priority order: known label mappings first, then input
attributes (autocomplete/type), then section context. The reasoning provider
is only consulted for fields these methods cannot classify, and the mock
provider deliberately refuses to guess.

Confidence is 0–100: ≥90 may be filled automatically, 70–89 requires review,
below 70 requires user input (docs/17 Phase 6 confidence rules).
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from pydantic import BaseModel

from job_platform.browser.models import FieldType, FormField
from job_platform.providers.base import ReasoningProvider
from job_platform.providers.tasks import FormFieldResolutionRequest
from job_platform.shared.errors import ProviderError
from job_platform.shared.logging import get_logger

logger = get_logger("forms.semantic")

AUTO_CONFIDENCE = 90
REVIEW_CONFIDENCE = 70


class SemanticClassification(BaseModel):
    """docs/09 Semantic Classification Result."""

    field_id: str
    semantic_type: str = "unknown"
    confidence: int = 0
    method: str = "none"

    @property
    def requires_review(self) -> bool:
        return self.confidence < AUTO_CONFIDENCE

    @property
    def usable(self) -> bool:
        return self.semantic_type != "unknown" and self.confidence >= REVIEW_CONFIDENCE


@dataclass(frozen=True)
class _Rule:
    family: str
    pattern: re.Pattern
    field_types: tuple[FieldType, ...] = ()


def _rule(family: str, pattern: str, *field_types: FieldType) -> _Rule:
    return _Rule(family, re.compile(pattern, re.IGNORECASE), field_types)


# Ordered: more specific rules first (docs/09 canonical synonym mapping).
_LABEL_RULES: list[_Rule] = [
    _rule("documents.cover_letter", r"cover\s*letter", FieldType.FILE),
    _rule("documents.resume", r"\b(resume|c\.?v\.?|curriculum vitae)\b", FieldType.FILE),
    _rule("work_authorization.sponsorship_future", r"(future|ever).{0,40}sponsor|sponsor.{0,40}future"),
    _rule("work_authorization.sponsorship_now", r"sponsor"),
    _rule(
        "work_authorization.authorized_now",
        r"(authori[sz]ed|eligible|legally able|right)\s.{0,30}\bwork\b|work authori[sz]ation",
    ),
    _rule("work_authorization.visa_status", r"visa\s+(status|type)|immigration\s+status"),
    _rule("personal.first_name", r"\b(first|given)\s*name\b"),
    _rule("personal.last_name", r"\b(last|family)\s*name\b|surname"),
    _rule("personal.full_name", r"\b(full|legal|your)\s*name\b"),
    _rule("personal.email", r"\be-?mail\b"),
    _rule("personal.phone", r"phone|mobile|telephone"),
    _rule("personal.address", r"street address|address line|home address"),
    _rule("personal.city", r"\bcity\b|\btown\b"),
    _rule("personal.state", r"\bstate\b|\bprovince\b"),
    _rule("personal.postal_code", r"postal|zip\s*code|\bzip\b"),
    _rule("personal.country", r"\bcountry\b"),
    _rule("links.linkedin", r"linked\s*in"),
    _rule("links.github", r"git\s*hub"),
    _rule("links.portfolio", r"portfolio|personal website"),
    _rule("employment.current_company", r"current (employer|company)|most recent (employer|company)"),
    _rule("employment.current_title", r"current (title|role|position)|job title"),
    _rule("employment.years_of_experience", r"years of (professional |relevant )?experience"),
    _rule("employment.notice_period", r"notice period"),
    _rule("preferences.start_date", r"start date|available to start|earliest.{0,20}start"),
    _rule("preferences.salary_expectation", r"salary|compensation|desired pay|pay expectation"),
    _rule("preferences.relocation", r"reloca"),
    _rule("preferences.travel", r"\btravel\b"),
    _rule("education.highest_degree", r"highest (degree|level of education)|degree obtained"),
    _rule("education.institution", r"school|university|college|institution"),
    _rule("narrative.why_company", r"why (do you want|are you interested|us\b|this company|join)"),
    _rule("narrative.tell_us_about_yourself", r"about yourself|tell us about you"),
    _rule("demographic.gender", r"\bgender\b"),
    _rule("demographic.race_ethnicity", r"race|ethnicit"),
    _rule("demographic.veteran_status", r"veteran"),
    _rule("demographic.disability_status", r"disabilit"),
    _rule("legal.criminal_history", r"criminal|convicted|felony"),
]

_AUTOCOMPLETE_MAP = {
    "given-name": "personal.first_name",
    "family-name": "personal.last_name",
    "name": "personal.full_name",
    "email": "personal.email",
    "tel": "personal.phone",
    "street-address": "personal.address",
    "address-line1": "personal.address",
    "address-level2": "personal.city",
    "address-level1": "personal.state",
    "postal-code": "personal.postal_code",
    "country": "personal.country",
    "country-name": "personal.country",
    "organization": "employment.current_company",
    "organization-title": "employment.current_title",
}

_INPUT_TYPE_MAP = {
    FieldType.EMAIL: "personal.email",
    FieldType.PHONE: "personal.phone",
}


def _match_rules(text: str, field: FormField) -> _Rule | None:
    for rule in _LABEL_RULES:
        if rule.field_types and field.field_type not in rule.field_types:
            continue
        if rule.pattern.search(text):
            return rule
    return None


def classify_field(field: FormField) -> SemanticClassification:
    """Deterministic classification (docs/09 priority 1–7)."""
    label_text = " ".join(filter(None, [field.label, field.placeholder, field.help_text]))

    rule = _match_rules(label_text, field)
    if rule is not None:
        return SemanticClassification(
            field_id=field.field_id,
            semantic_type=rule.family,
            confidence=95,
            method="known_label_mapping",
        )

    if field.autocomplete in _AUTOCOMPLETE_MAP:
        return SemanticClassification(
            field_id=field.field_id,
            semantic_type=_AUTOCOMPLETE_MAP[field.autocomplete],
            confidence=90,
            method="autocomplete_attribute",
        )

    if field.field_type in _INPUT_TYPE_MAP:
        return SemanticClassification(
            field_id=field.field_id,
            semantic_type=_INPUT_TYPE_MAP[field.field_type],
            confidence=85,
            method="input_type",
        )

    if field.section:
        rule = _match_rules(field.section, field)
        if rule is not None:
            return SemanticClassification(
                field_id=field.field_id,
                semantic_type=rule.family,
                confidence=75,
                method="section_context",
            )

    return SemanticClassification(field_id=field.field_id)


async def classify_field_with_provider(
    field: FormField,
    provider: ReasoningProvider,
    candidate_context: str = "",
    page_heading: str = "",
) -> SemanticClassification:
    """Full priority chain: deterministic first, provider for unknowns.

    Provider classifications are capped below the auto-fill threshold so a
    model guess always lands in review or user-input territory (docs/09).
    """
    deterministic = classify_field(field)
    if deterministic.semantic_type != "unknown":
        return deterministic
    try:
        resolution = await provider.resolve_form_field(
            FormFieldResolutionRequest(
                label=field.label,
                placeholder=field.placeholder,
                help_text=field.help_text,
                field_type=field.field_type.value,
                options=field.options,
                section=field.section,
                page_heading=page_heading,
                candidate_context=candidate_context,
            )
        )
    except ProviderError as exc:
        logger.warning(
            "Provider classification failed for field '%s': %s", field.field_id, exc.message
        )
        return deterministic
    if resolution.field_semantic_type == "unknown" or resolution.requires_user_input:
        return deterministic
    return SemanticClassification(
        field_id=field.field_id,
        semantic_type=resolution.field_semantic_type,
        confidence=min(int(resolution.confidence * 100), AUTO_CONFIDENCE - 1),
        method="reasoning_provider",
    )
