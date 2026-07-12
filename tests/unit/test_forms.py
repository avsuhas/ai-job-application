"""Unit tests for semantic classification, answer mapping, and boundary
detection (docs/09) — no browser required."""

import pytest

from job_platform.browser.models import BrowserAction, FieldType, FormAction, FormField
from job_platform.forms.boundary import detect_form_boundary
from job_platform.forms.mapper import PlanEntryStatus, build_form_plan, match_option
from job_platform.forms.semantic import (
    classify_field,
    classify_field_with_provider,
)
from job_platform.preparation.answers import PreparedAnswer, PreparedAnswerSet
from job_platform.providers.mock import MockReasoningProvider
from job_platform.providers.tasks import FormFieldResolution
from tests.conftest import StubProvider


def field(field_id="f1", label="", field_type=FieldType.TEXT, **kw) -> FormField:
    return FormField(
        field_id=field_id, label=label, field_type=field_type,
        selector=f"#{field_id}", **kw,
    )


def answer(family: str, value: str) -> PreparedAnswer:
    return PreparedAnswer(
        answer_id=family.replace(".", "_"), question_family=family,
        canonical_question=family, answer=value, source=f"candidate.json:{family}",
        confidence=100,
    )


ANSWERS = PreparedAnswerSet(
    answers=[
        answer("personal.first_name", "Alex"),
        answer("personal.last_name", "Sample"),
        answer("personal.email", "alex@example.com"),
        answer("personal.country", "United States"),
        answer("work_authorization.authorized_now", "Yes"),
        answer("work_authorization.sponsorship_now", "No"),
        answer("preferences.relocation", "Yes"),
    ]
)


class TestSemanticClassification:
    @pytest.mark.parametrize(
        ("label", "expected"),
        [
            ("First Name", "personal.first_name"),
            ("Given name", "personal.first_name"),
            ("Surname", "personal.last_name"),
            ("Email Address", "personal.email"),
            ("Mobile phone", "personal.phone"),
            ("LinkedIn Profile", "links.linkedin"),
            ("Current employer", "employment.current_company"),
            ("Are you legally authorized to work in the US?", "work_authorization.authorized_now"),
            ("Will you now or in the future require sponsorship?", "work_authorization.sponsorship_future"),
            ("Desired salary", "preferences.salary_expectation"),
            ("Are you willing to relocate?", "preferences.relocation"),
            ("Why do you want to work here?", "narrative.why_company"),
            ("Gender", "demographic.gender"),
            ("Have you ever been convicted of a felony?", "legal.criminal_history"),
        ],
    )
    def test_known_labels_map_correctly(self, label, expected):
        result = classify_field(field(label=label))
        assert result.semantic_type == expected
        assert result.confidence >= 90
        assert result.method == "known_label_mapping"

    def test_resume_upload_requires_file_type(self):
        as_file = classify_field(field(label="Resume/CV", field_type=FieldType.FILE))
        assert as_file.semantic_type == "documents.resume"
        as_text = classify_field(field(label="Resume/CV", field_type=FieldType.TEXT))
        assert as_text.semantic_type != "documents.resume"

    def test_sponsorship_future_beats_now_when_future_mentioned(self):
        result = classify_field(
            field(label="Will sponsorship ever be required in the future?")
        )
        assert result.semantic_type == "work_authorization.sponsorship_future"

    def test_autocomplete_attribute_fallback(self):
        result = classify_field(field(label="Vorname", autocomplete="given-name"))
        assert result.semantic_type == "personal.first_name"
        assert result.method == "autocomplete_attribute"

    def test_input_type_fallback(self):
        result = classify_field(field(label="Contact", field_type=FieldType.EMAIL))
        assert result.semantic_type == "personal.email"
        assert result.method == "input_type"
        assert result.requires_review  # 85 < 90

    def test_section_context_fallback(self):
        result = classify_field(
            field(label="Details", section="Work Authorization Status: authorized to work")
        )
        assert result.semantic_type == "work_authorization.authorized_now"
        assert result.method == "section_context"

    def test_unclassifiable_field_is_unknown(self):
        result = classify_field(field(label="Favorite color"))
        assert result.semantic_type == "unknown"
        assert not result.usable


class ResolvingProvider(StubProvider):
    async def resolve_form_field(self, request):
        return FormFieldResolution(
            field_semantic_type="preferences.travel",
            confidence=0.95,
            source="preferences.md",
        )


class TestProviderFallback:
    async def test_deterministic_wins_without_provider_call(self):
        result = await classify_field_with_provider(
            field(label="First Name"), StubProvider()  # would raise if called
        )
        assert result.semantic_type == "personal.first_name"

    async def test_provider_used_for_unknown_and_capped_below_auto(self):
        result = await classify_field_with_provider(
            field(label="Mobility expectations for this role?"),  # no deterministic rule
            ResolvingProvider(),
        )
        assert result.semantic_type == "preferences.travel"
        assert result.method == "reasoning_provider"
        assert result.confidence < 90  # provider output never auto-fills

    async def test_mock_provider_refuses_to_guess(self):
        result = await classify_field_with_provider(
            field(label="Favorite color"), MockReasoningProvider()
        )
        assert result.semantic_type == "unknown"


class TestOptionMatching:
    def test_exact_and_case_insensitive(self):
        assert match_option(["Yes", "No"], "yes") == "Yes"

    def test_boolean_normalization(self):
        assert match_option(["Yes", "No"], "true") == "Yes"
        assert match_option(["Yes", "No"], "false") == "No"

    def test_contains_matching(self):
        assert match_option(["United States of America", "Canada"], "United States") \
            == "United States of America"

    def test_no_match_returns_none(self):
        assert match_option(["Red", "Blue"], "Green") is None


class TestPlanBuilder:
    def make_fields(self):
        return [
            field("first_name", "First Name"),
            field("email", "Email", FieldType.EMAIL),
            field("country", "Country", FieldType.SELECT,
                  options=["Select...", "United States", "Canada"]),
            field("authorized", "Are you authorized to work in the US?",
                  FieldType.RADIO, options=["Yes", "No"], required=True),
            field("gender", "Gender", FieldType.SELECT, options=["Male", "Female"]),
            field("mystery", "Favorite color", required=True),
            field("resume", "Resume/CV", FieldType.FILE, required=True),
        ]

    def classifications(self, fields):
        return {f.field_id: classify_field(f) for f in fields}

    def test_plan_contains_only_confident_answerable_fields(self):
        fields = self.make_fields()
        result = build_form_plan(
            fields, self.classifications(fields), ANSWERS,
            documents={"documents.resume": "/pkg/resume/tailored_resume.md"},
        )
        by_field = {e.field_id: e for e in result.entries}
        assert by_field["first_name"].status == PlanEntryStatus.PLANNED
        assert by_field["country"].status == PlanEntryStatus.PLANNED
        assert by_field["authorized"].status == PlanEntryStatus.PLANNED
        assert by_field["resume"].status == PlanEntryStatus.PLANNED
        # Sensitive question skipped by policy, unknown surfaced
        assert by_field["gender"].status == PlanEntryStatus.SENSITIVE_SKIPPED
        assert by_field["mystery"].status == PlanEntryStatus.UNKNOWN_FIELD

        planned_fields = {s.field_id for s in result.plan.steps}
        assert "gender" not in planned_fields
        assert "mystery" not in planned_fields

        upload = next(s for s in result.plan.steps if s.field_id == "resume")
        assert upload.action == BrowserAction.UPLOAD_FILE
        assert upload.value == "/pkg/resume/tailored_resume.md"

    def test_option_values_mapped_to_widget_options(self):
        fields = self.make_fields()
        result = build_form_plan(fields, self.classifications(fields), ANSWERS,
                                 documents={"documents.resume": "/x"})
        radio = next(s for s in result.plan.steps if s.field_id == "authorized")
        assert radio.value == "Yes"

    def test_option_mismatch_surfaced_not_guessed(self):
        fields = [field("country", "Country", FieldType.SELECT,
                        options=["Germany", "France"], required=True)]
        result = build_form_plan(fields, self.classifications(fields), ANSWERS)
        assert result.entries[0].status == PlanEntryStatus.OPTION_MISMATCH
        assert result.plan.steps == []
        assert result.unresolved_required

    def test_missing_answer_surfaced(self):
        fields = [field("notice", "Notice period", required=True)]
        result = build_form_plan(fields, self.classifications(fields), ANSWERS)
        assert result.entries[0].status == PlanEntryStatus.NO_STORED_ANSWER
        assert result.unresolved_required

    def test_medium_confidence_flagged_for_review(self):
        fields = [field("contact", "Contact", FieldType.EMAIL)]  # input_type → 85
        result = build_form_plan(fields, self.classifications(fields), ANSWERS)
        assert result.entries[0].status == PlanEntryStatus.NEEDS_REVIEW
        assert len(result.plan.steps) == 1  # still planned, review mode covers it

    def test_sponsorship_future_falls_back_to_now_answer(self):
        fields = [field("sponsor", "Will you ever require sponsorship in the future?",
                        FieldType.RADIO, options=["Yes", "No"])]
        result = build_form_plan(fields, self.classifications(fields), ANSWERS)
        step = result.plan.steps[0]
        assert step.value == "No"

    def test_full_name_computed_from_parts(self):
        fields = [field("name", "Full Name")]
        result = build_form_plan(fields, self.classifications(fields), ANSWERS)
        assert result.plan.steps[0].value == "Alex Sample"
        assert result.entries[0].answer_source.startswith("computed:")

    def test_invisible_and_password_fields_ignored(self):
        fields = [
            field("hidden_token", "Token", visible=False),
            field("pw", "Password", FieldType.PASSWORD),
        ]
        result = build_form_plan(fields, self.classifications(fields), ANSWERS)
        assert result.entries == []
        assert result.plan.steps == []


class TestBoundaryDetection:
    def test_application_form_selected_among_others(self):
        fields = [
            field("q", "Search jobs", form_id="search_form"),
            field("nl_email", "Email", FieldType.EMAIL, form_id="newsletter",
                  placeholder="Subscribe to our newsletter"),
            field("first_name", "First Name", form_id="apply_form"),
            field("email", "Email", FieldType.EMAIL, form_id="apply_form"),
            field("resume", "Resume/CV", FieldType.FILE, form_id="apply_form"),
        ]
        actions = [
            FormAction(action_id="s", type="unknown", label="Search", selector="#s",
                       form_id="search_form"),
            FormAction(action_id="a", type="submit", label="Apply Now", selector="#a",
                       form_id="apply_form"),
        ]
        result = detect_form_boundary(fields, actions)
        assert result.selected_form_id == "apply_form"
        selected = result.selected_fields(fields)
        assert {f.field_id for f in selected} == {"first_name", "email", "resume"}

    def test_login_form_not_selected(self):
        fields = [
            field("user", "Email", FieldType.EMAIL, form_id="login"),
            field("pass", "Password", FieldType.PASSWORD, form_id="login"),
        ]
        result = detect_form_boundary(fields, [])
        assert result.selected_form_id is None

    def test_search_only_page_selects_nothing(self):
        fields = [field("q", "Search keyword", form_id="search")]
        result = detect_form_boundary(fields, [])
        assert result.selected_form_id is None
