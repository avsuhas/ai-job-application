"""Tests for the manual completion package, answer editing, and manual
submission recording (docs/17 Phase 4)."""

import json

import pytest

from job_platform.candidate.loader import load_candidate_bundle
from job_platform.packages.models import PackageStatus
from job_platform.packages.store import PackageStore
from job_platform.preparation.answers import edit_prepared_answer
from job_platform.preparation.service import PreparationService
from job_platform.providers.mock import MockReasoningProvider
from job_platform.readiness.handoff import build_manual_completion_package
from job_platform.shared.config import Settings
from job_platform.shared.errors import DuplicateApplicationError, StorageError
from job_platform.storage.tracker import ApplicationTracker
from job_platform.submission.manual import record_manual_submission
from tests.unit.test_review import make_ranked


@pytest.fixture
def package_env(candidate_dir, tmp_path):
    bundle = load_candidate_bundle(candidate_dir)
    store = PackageStore(tmp_path / "packages")
    tracker = ApplicationTracker(tmp_path / "tracker.csv")
    prep = PreparationService(MockReasoningProvider(), store, Settings(), tracker=tracker)
    return bundle, store, tracker, prep, candidate_dir


class TestManualCompletionPackage:
    async def test_handoff_contains_everything_needed(self, package_env):
        bundle, store, tracker, prep, _ = package_env
        manifest = await prep.prepare(make_ranked(), bundle)
        package = build_manual_completion_package(manifest, store)

        assert package.application_url == "https://example.com/jobs/42"
        assert package.resume == "resume/tailored_resume.md"
        assert any("Resume" in item for item in package.upload_checklist)
        families = {a.question_family for a in package.answers}
        assert "personal.first_name" in families
        # Sensitive answers flagged
        assert "work_authorization.sponsorship_now" in package.sensitive_answers
        # Missing answers surfaced from unresolved questions
        assert any("notice_period" in m for m in package.missing_answers)
        assert any("Mark this application as submitted" in s for s in package.completion_checklist)

    async def test_handoff_markdown_rendered_and_stored(self, package_env):
        bundle, store, tracker, prep, _ = package_env
        manifest = await prep.prepare(make_ranked(), bundle)
        package = build_manual_completion_package(manifest, store)
        markdown = store.read_artifact(manifest.package_id, "manual/manual_completion.md")
        assert markdown == package.render()
        assert "# Manual application: Backend Engineer at ExampleCo" in markdown
        assert "⚠ sensitive" in markdown
        assert "- [ ]" in markdown


class TestAnswerEditing:
    async def test_edit_existing_answer_marks_user_approved(self, package_env):
        bundle, store, tracker, prep, _ = package_env
        manifest = await prep.prepare(make_ranked(), bundle)
        edited = edit_prepared_answer(
            store, manifest, "narrative_why_company", "Because I love infrastructure."
        )
        assert edited.approved is True
        assert edited.source == "user_edit"
        answers = json.loads(
            store.read_artifact(manifest.package_id, "answers/prepared_answers.json")
        )["answers"]
        stored = next(a for a in answers if a["answer_id"] == "narrative_why_company")
        assert stored["answer"] == "Because I love infrastructure."
        assert stored["approved"] is True

    async def test_edit_resolves_unresolved_question(self, package_env):
        bundle, store, tracker, prep, _ = package_env
        manifest = await prep.prepare(make_ranked(), bundle)
        edited = edit_prepared_answer(
            store, manifest, "employment.notice_period", "Two weeks"
        )
        assert edited.question_family == "employment.notice_period"
        unresolved = json.loads(
            store.read_artifact(manifest.package_id, "answers/unresolved_questions.json")
        )["questions"]
        assert not any(
            q["question_family"] == "employment.notice_period" for q in unresolved
        )

    async def test_edit_unknown_answer_raises(self, package_env):
        bundle, store, tracker, prep, _ = package_env
        manifest = await prep.prepare(make_ranked(), bundle)
        with pytest.raises(StorageError):
            edit_prepared_answer(store, manifest, "nonexistent_family", "value")

    async def test_save_for_reuse_appends_to_answers_md(self, package_env):
        bundle, store, tracker, prep, candidate_dir = package_env
        manifest = await prep.prepare(make_ranked(), bundle)
        profile_dir = candidate_dir / "profile"
        edit_prepared_answer(
            store,
            manifest,
            "employment.notice_period",
            "Two weeks",
            question="What is your notice period?",
            save_for_reuse=True,
            candidate_profile_dir=profile_dir,
        )
        content = (profile_dir / "answers.md").read_text()
        assert "## What is your notice period?" in content
        assert "Two weeks" in content

    async def test_edit_without_reuse_leaves_answers_md_untouched(self, package_env):
        bundle, store, tracker, prep, candidate_dir = package_env
        manifest = await prep.prepare(make_ranked(), bundle)
        before = (candidate_dir / "profile" / "answers.md").read_text()
        edit_prepared_answer(
            store, manifest, "employment.notice_period", "Two weeks",
            candidate_profile_dir=candidate_dir / "profile",
        )
        assert (candidate_dir / "profile" / "answers.md").read_text() == before


class TestManualSubmission:
    async def test_records_tracker_row_and_result(self, package_env):
        bundle, store, tracker, prep, _ = package_env
        manifest = await prep.prepare(make_ranked(), bundle)
        record = record_manual_submission(
            manifest, store, tracker, notes="applied via careers site"
        )
        assert record.status == "submitted"
        assert "manual submission" in record.notes
        assert "applied via careers site" in record.notes

        result = json.loads(store.read_artifact(manifest.package_id, "submission/result.json"))
        assert result["method"] == "manual"
        assert result["recorded_by"] == "user"

        reloaded = store.load_manifest(manifest.package_id)
        assert reloaded.status == PackageStatus.SUBMITTED
        # Duplicate detection now covers this job
        assert tracker.is_duplicate(make_ranked().job)

    async def test_duplicate_manual_submission_rejected(self, package_env):
        bundle, store, tracker, prep, _ = package_env
        manifest = await prep.prepare(make_ranked(), bundle)
        record_manual_submission(manifest, store, tracker)
        with pytest.raises(DuplicateApplicationError):
            record_manual_submission(manifest, store, tracker)
        # Package status unchanged by the failed second attempt
        assert store.load_manifest(manifest.package_id).status == PackageStatus.SUBMITTED
