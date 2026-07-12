"""Tests for cover letter decision/validation and standard answer preparation."""

import json

from job_platform.candidate.loader import load_candidate_bundle
from job_platform.jobs.models import Job, JobAnalysis
from job_platform.preparation.answers import prepare_answers, resolve_standard_answers
from job_platform.preparation.cover_letter import (
    decide_cover_letter,
    prepare_cover_letter,
    validate_cover_letter,
)
from job_platform.providers.mock import MockReasoningProvider
from job_platform.providers.tasks import CoverLetterDraft
from job_platform.shared.config import Settings


def make_job() -> Job:
    return Job(id="j1", company="ExampleCo", title="Backend Engineer", url="https://x/1")


class TestCoverLetterDecision:
    def test_default_is_no_cover_letter(self, candidate_dir):
        bundle = load_candidate_bundle(candidate_dir)
        decision = decide_cover_letter(Settings(), bundle)
        assert decision.generate is False
        assert decision.source == "default"

    def test_explicit_request_wins(self, candidate_dir):
        bundle = load_candidate_bundle(candidate_dir)
        decision = decide_cover_letter(Settings(), bundle, explicit_request=True)
        assert decision.generate is True
        assert decision.source == "user_instruction"

    def test_explicit_disable_wins_over_setting(self, candidate_dir):
        bundle = load_candidate_bundle(candidate_dir)
        settings = Settings(applications={"generate_cover_letter": True})
        decision = decide_cover_letter(settings, bundle, explicit_request=False)
        assert decision.generate is False

    def test_candidate_rule_never_beats_global_setting(self, candidate_dir):
        (candidate_dir / "profile" / "rules.md").write_text(
            "Never generate a cover letter.\n"
        )
        bundle = load_candidate_bundle(candidate_dir)
        settings = Settings(applications={"generate_cover_letter": True})
        decision = decide_cover_letter(settings, bundle)
        assert decision.generate is False
        assert decision.source == "candidate_rule"

    def test_candidate_rule_always(self, candidate_dir):
        (candidate_dir / "profile" / "rules.md").write_text(
            "Always generate a cover letter for senior roles.\n"
        )
        bundle = load_candidate_bundle(candidate_dir)
        decision = decide_cover_letter(Settings(), bundle)
        assert decision.generate is True

    def test_global_setting_enables(self, candidate_dir):
        bundle = load_candidate_bundle(candidate_dir)
        settings = Settings(applications={"generate_cover_letter": True})
        decision = decide_cover_letter(settings, bundle)
        assert decision.generate is True
        assert decision.source == "global_setting"


class TestCoverLetterValidation:
    def test_missing_company_blocks(self):
        draft = CoverLetterDraft(body_paragraphs=["I want to work at SomeOtherCorp."])
        validation = validate_cover_letter(draft, make_job())
        assert not validation.passed
        assert any("ExampleCo" in issue for issue in validation.blocking_issues)

    def test_unsupported_claims_block(self):
        draft = CoverLetterDraft(
            body_paragraphs=["Applying to ExampleCo as Backend Engineer."],
            unsupported_claims=["invented Kubernetes cert"],
        )
        validation = validate_cover_letter(draft, make_job())
        assert not validation.passed

    def test_flattery_and_length_warn(self):
        draft = CoverLetterDraft(
            body_paragraphs=["ExampleCo is a world-renowned Backend Engineer employer. " + "word " * 500]
        )
        validation = validate_cover_letter(draft, make_job(), max_words=400)
        assert validation.passed  # warnings only
        assert any("flattery" in w for w in validation.warnings)
        assert any("words" in w for w in validation.warnings)

    async def test_mock_generation_passes_validation(self, candidate_dir):
        bundle = load_candidate_bundle(candidate_dir)
        draft, validation = await prepare_cover_letter(
            MockReasoningProvider(), make_job(), JobAnalysis(), bundle
        )
        assert validation.passed
        assert "ExampleCo" in draft.render()


class TestStandardAnswers:
    def test_resolves_personal_and_authorization_facts(self, candidate_dir):
        bundle = load_candidate_bundle(candidate_dir)
        result = resolve_standard_answers(bundle)
        first_name = result.answer_for("personal.first_name")
        assert first_name.answer == "Alex"
        assert first_name.source == "candidate.json:personal.first_name"
        assert first_name.factual and first_name.approved

        sponsorship = result.answer_for("work_authorization.sponsorship_now")
        assert sponsorship.answer == "No"

        auth = result.answer_for("work_authorization.authorized_now")
        assert auth.answer == "Yes"

    def test_resolves_preferences_from_documents(self, candidate_dir):
        bundle = load_candidate_bundle(candidate_dir)
        result = resolve_standard_answers(bundle)
        salary = result.answer_for("preferences.salary_expectation")
        assert salary is not None
        assert "200000" in salary.answer
        assert salary.source == "preferences.md"

    def test_missing_required_fields_are_unresolved(self, candidate_dir):
        (candidate_dir / "profile" / "candidate.json").write_text(json.dumps({}))
        bundle = load_candidate_bundle(candidate_dir)
        result = resolve_standard_answers(bundle)
        families = {u.question_family for u in result.unresolved}
        assert "personal.first_name" in families
        assert "work_authorization.authorized_now" in families
        required = [u for u in result.unresolved if u.required_for_readiness]
        assert required  # missing name/email/auth are readiness-blocking

    def test_unstored_preferences_are_unresolved_not_guessed(self, candidate_dir):
        (candidate_dir / "profile" / "preferences.md").write_text("Preferred Roles: Backend")
        (candidate_dir / "profile" / "notes.md").write_text("nothing relevant")
        bundle = load_candidate_bundle(candidate_dir)
        result = resolve_standard_answers(bundle)
        assert result.answer_for("preferences.salary_expectation") is None
        families = {u.question_family for u in result.unresolved}
        assert "preferences.salary_expectation" in families

    async def test_narratives_generated_and_marked_unapproved(self, candidate_dir):
        bundle = load_candidate_bundle(candidate_dir)
        result = await prepare_answers(MockReasoningProvider(), make_job(), bundle)
        why = result.answer_for("narrative.why_company")
        assert why is not None
        assert why.factual is False
        assert why.approved is False
        assert "ExampleCo" in why.answer
