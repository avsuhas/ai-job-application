"""Tests for CKB loading, validation, and context building."""

import pytest

from job_platform.candidate.context import build_candidate_context, resume_inventory
from job_platform.candidate.loader import load_candidate_bundle
from job_platform.candidate.validator import validate_bundle, validate_candidate_dir
from job_platform.shared.errors import CandidateDataError


class TestLoader:
    def test_loads_structured_profile(self, candidate_dir):
        bundle = load_candidate_bundle(candidate_dir)
        assert bundle.profile.personal.full_name == "Alex Sample"
        assert bundle.profile.work_authorization.requires_sponsorship is False
        assert bundle.profile.employment.years_of_experience == 8

    def test_loads_all_profile_documents(self, candidate_dir):
        bundle = load_candidate_bundle(candidate_dir)
        assert "Never apply to contract jobs" in bundle.rules
        assert "Preferred Countries" in bundle.preferences
        assert "Why do you want to work here?" in bundle.answers
        assert "Kubernetes certification" in bundle.notes

    def test_loads_additional_documents_without_code_changes(self, candidate_dir):
        (candidate_dir / "profile" / "publications.md").write_text("My paper on queues")
        bundle = load_candidate_bundle(candidate_dir)
        assert bundle.documents["publications"] == "My paper on queues"

    def test_loads_resumes_with_text(self, candidate_dir):
        bundle = load_candidate_bundle(candidate_dir)
        assert len(bundle.resumes) == 1
        resume = bundle.resumes[0]
        assert resume.id == "backend"
        assert "distributed order-processing" in resume.text
        assert bundle.resume_by_id("backend") is resume
        assert bundle.resume_by_id("missing") is None

    def test_invalid_candidate_json_raises_actionable_error(self, candidate_dir):
        (candidate_dir / "profile" / "candidate.json").write_text("{broken json")
        with pytest.raises(CandidateDataError) as excinfo:
            load_candidate_bundle(candidate_dir)
        assert "invalid JSON" in excinfo.value.message
        assert "line" in excinfo.value.message

    def test_missing_files_load_as_empty_bundle(self, tmp_path):
        bundle = load_candidate_bundle(tmp_path / "empty")
        assert bundle.resumes == []
        assert bundle.rules == ""


class TestValidator:
    def test_complete_bundle_passes_with_no_errors(self, candidate_dir):
        report = validate_candidate_dir(candidate_dir)
        assert report.ok
        assert report.errors == []

    def test_missing_optional_data_produces_warnings_not_errors(self, tmp_path):
        empty = tmp_path / "candidate"
        (empty / "profile").mkdir(parents=True)
        (empty / "resume").mkdir()
        report = validate_candidate_dir(empty)
        assert report.ok  # warnings only
        codes = {i.code for i in report.warnings}
        assert "no_resumes" in codes
        assert "missing_email" in codes
        assert "missing_work_authorization" in codes

    def test_contradictory_work_authorization_is_flagged(self, candidate_dir):
        profile_path = candidate_dir / "profile" / "candidate.json"
        profile_path.write_text(
            '{"work_authorization": {"authorized_to_work": false, "requires_sponsorship": false}}'
        )
        bundle = load_candidate_bundle(candidate_dir)
        report = validate_bundle(bundle)
        assert "contradictory_work_authorization" in {i.code for i in report.issues}

    def test_invalid_json_is_reported_as_error(self, candidate_dir):
        (candidate_dir / "profile" / "candidate.json").write_text("not json")
        report = validate_candidate_dir(candidate_dir)
        assert not report.ok

    def test_missing_directory_is_reported_as_error(self, tmp_path):
        report = validate_candidate_dir(tmp_path / "nowhere")
        assert not report.ok
        assert report.errors[0].code == "missing_candidate_dir"


class TestContextBuilder:
    def test_context_sections_follow_priority_order(self, candidate_dir):
        bundle = load_candidate_bundle(candidate_dir)
        context = build_candidate_context(bundle, resume=bundle.resumes[0])
        facts = context.index("Candidate Facts")
        rules = context.index("Candidate Rules")
        prefs = context.index("Search Preferences")
        resume = context.index("Resume (Backend.txt)")
        notes = context.index("Candidate Notes")
        assert facts < rules < prefs < resume < notes

    def test_contact_details_excluded_by_default(self, candidate_dir):
        bundle = load_candidate_bundle(candidate_dir)
        context = build_candidate_context(bundle)
        assert "+1-555-0100" not in context
        assert "100 Example Street" not in context
        # but non-sensitive facts remain
        assert "Alex" in context
        assert "United States" in context

    def test_contact_details_included_when_requested(self, candidate_dir):
        bundle = load_candidate_bundle(candidate_dir)
        context = build_candidate_context(bundle, include_contact=True)
        assert "+1-555-0100" in context

    def test_answers_only_included_on_request(self, candidate_dir):
        bundle = load_candidate_bundle(candidate_dir)
        assert "Why do you want to work here?" not in build_candidate_context(bundle)
        assert "Why do you want to work here?" in build_candidate_context(
            bundle, include_answers=True
        )

    def test_resume_inventory(self, candidate_dir):
        bundle = load_candidate_bundle(candidate_dir)
        listing = resume_inventory(bundle)
        assert "id=backend" in listing
        assert "file=Backend.txt" in listing
