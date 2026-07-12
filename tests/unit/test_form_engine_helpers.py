"""Tests for the form engine's package-integration helpers."""

import json

from job_platform.candidate.loader import load_candidate_bundle
from job_platform.forms.engine import (
    EngineStatus,
    FormExecutionReport,
    documents_for_package,
    load_prepared_answers,
    store_execution_report,
)
from job_platform.packages.store import PackageStore
from job_platform.preparation.service import PreparationOptions, PreparationService
from job_platform.providers.mock import MockReasoningProvider
from job_platform.shared.config import Settings
from tests.unit.test_review import make_ranked


class TestPackageIntegration:
    async def test_answers_and_documents_resolved_from_package(
        self, candidate_dir, tmp_path
    ):
        bundle = load_candidate_bundle(candidate_dir)
        store = PackageStore(tmp_path / "packages")
        prep = PreparationService(MockReasoningProvider(), store, Settings())
        manifest = await prep.prepare(
            make_ranked(), bundle, PreparationOptions(generate_cover_letter=True)
        )

        answers = load_prepared_answers(store, manifest)
        assert answers.answer_for("personal.first_name").answer == "Alex"

        documents = documents_for_package(manifest, store, bundle)
        assert documents["documents.resume"].endswith("resume/tailored_resume.md")
        assert documents["documents.cover_letter"].endswith("cover_letter/cover_letter.md")

    async def test_base_resume_fallback_resolves_to_candidate_file(
        self, candidate_dir, tmp_path
    ):
        bundle = load_candidate_bundle(candidate_dir)
        store = PackageStore(tmp_path / "packages")
        prep = PreparationService(MockReasoningProvider(), store, Settings())
        manifest = await prep.prepare(
            make_ranked(), bundle, PreparationOptions(tailor_resume=False)
        )
        assert manifest.selected_resume.startswith("candidate resume: ")
        documents = documents_for_package(manifest, store, bundle)
        assert documents["documents.resume"].endswith("Backend.txt")

    async def test_execution_report_persisted_into_package(self, candidate_dir, tmp_path):
        bundle = load_candidate_bundle(candidate_dir)
        store = PackageStore(tmp_path / "packages")
        prep = PreparationService(MockReasoningProvider(), store, Settings())
        manifest = await prep.prepare(make_ranked(), bundle)

        report = FormExecutionReport(status=EngineStatus.READY_FOR_REVIEW)
        store_execution_report(store, manifest, report)
        stored = json.loads(
            store.read_artifact(manifest.package_id, "execution/form_execution_report.json")
        )
        assert stored["status"] == "ready_for_review"
        assert stored["package_id"] == manifest.package_id
