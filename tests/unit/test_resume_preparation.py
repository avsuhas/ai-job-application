"""Tests for resume selection, tailored rendering, and factual validation."""

import pytest

from job_platform.candidate.loader import load_candidate_bundle
from job_platform.jobs.models import Job, JobAnalysis
from job_platform.preparation.resume import render_tailored_resume, select_base_resume
from job_platform.preparation.resume_validation import validate_tailored_resume
from job_platform.providers.mock import MockReasoningProvider
from job_platform.providers.tasks import (
    ResumeSelectionResult,
    ResumeTailoringResult,
    RevisedBullet,
)
from job_platform.shared.errors import CandidateDataError
from tests.conftest import StubProvider


def make_job() -> Job:
    return Job(id="j1", company="ExampleCo", title="Backend Engineer", url="https://x/1")


class SelectingProvider(StubProvider):
    def __init__(self, resume_id: str):
        self.resume_id = resume_id

    async def select_resume(self, request):
        return ResumeSelectionResult(
            selected_resume_id=self.resume_id, reasoning="scripted", confidence=0.9
        )


class TestResumeSelection:
    async def test_ranking_suggestion_wins(self, candidate_dir):
        bundle = load_candidate_bundle(candidate_dir)
        selection, resume = await select_base_resume(
            bundle, make_job(), JobAnalysis(), StubProvider(), suggested_resume_id="backend"
        )
        assert selection.method == "ranking_suggestion"
        assert resume.id == "backend"

    async def test_single_resume_selected_without_provider(self, candidate_dir):
        bundle = load_candidate_bundle(candidate_dir)
        selection, resume = await select_base_resume(
            bundle, make_job(), JobAnalysis(), StubProvider()
        )
        assert selection.method == "only_resume"
        assert selection.confidence == 1.0

    async def test_provider_used_when_multiple_resumes(self, candidate_dir):
        (candidate_dir / "resume" / "ML.txt").write_text("Alex Sample\nML resume: PyTorch")
        bundle = load_candidate_bundle(candidate_dir)
        selection, resume = await select_base_resume(
            bundle, make_job(), JobAnalysis(), SelectingProvider("ml")
        )
        assert selection.method == "provider"
        assert resume.id == "ml"

    async def test_unknown_provider_selection_falls_back(self, candidate_dir):
        (candidate_dir / "resume" / "ML.txt").write_text("Alex Sample\nML resume")
        bundle = load_candidate_bundle(candidate_dir)
        selection, resume = await select_base_resume(
            bundle, make_job(), JobAnalysis(), SelectingProvider("nonexistent")
        )
        assert resume.id == bundle.resumes[0].id

    async def test_no_resumes_raises_actionable_error(self, candidate_dir):
        for f in (candidate_dir / "resume").iterdir():
            f.unlink()
        bundle = load_candidate_bundle(candidate_dir)
        with pytest.raises(CandidateDataError) as excinfo:
            await select_base_resume(bundle, make_job(), JobAnalysis(), StubProvider())
        assert "No resumes" in str(excinfo.value)


BASE = """Alex Sample
Senior Backend Engineer

EXPERIENCE
ExampleCorp (2020-present)
- Designed order services in Python
- Reduced p99 latency 40% with Kafka

SKILLS
Python, Kafka, AWS
"""


class TestRendering:
    def test_bullet_rewrites_applied_and_sections_prepended(self):
        plan = ResumeTailoringResult(
            professional_summary="Backend engineer with 8 years of experience.",
            skills_order=["Python", "Kafka"],
            revised_bullets=[
                RevisedBullet(
                    original="Designed order services in Python",
                    revised="Designed distributed order-processing services in Python",
                    supporting_sources=["base_resume"],
                )
            ],
        )
        rendered = render_tailored_resume(BASE, plan)
        assert rendered.startswith("PROFESSIONAL SUMMARY")
        assert "KEY SKILLS\nPython, Kafka" in rendered
        assert "distributed order-processing" in rendered
        assert "Designed order services in Python" not in rendered
        # Untouched content preserved
        assert "Reduced p99 latency 40% with Kafka" in rendered

    def test_unmatched_original_is_skipped(self):
        plan = ResumeTailoringResult(
            revised_bullets=[
                RevisedBullet(original="Not in resume", revised="Invented bullet")
            ]
        )
        rendered = render_tailored_resume(BASE, plan)
        assert "Invented bullet" not in rendered


class TestValidation:
    def make_bundle(self, candidate_dir):
        return load_candidate_bundle(candidate_dir)

    def test_clean_tailoring_passes(self, candidate_dir):
        bundle = self.make_bundle(candidate_dir)
        plan = ResumeTailoringResult(skills_order=["Python", "Kafka"])
        rendered = render_tailored_resume(BASE, plan)
        report = validate_tailored_resume(rendered, BASE, plan, bundle)
        assert report.passed
        assert report.status == "passed"

    def test_missing_name_blocks(self, candidate_dir):
        bundle = self.make_bundle(candidate_dir)
        plan = ResumeTailoringResult()
        tailored = BASE.replace("Alex Sample", "Someone Else")
        report = validate_tailored_resume(tailored, BASE, plan, bundle)
        assert any("name" in issue for issue in report.blocking_issues)

    def test_invented_year_blocks(self, candidate_dir):
        bundle = self.make_bundle(candidate_dir)
        tailored = BASE + "\nAcmeCorp (2010-2015)"
        report = validate_tailored_resume(tailored, BASE, ResumeTailoringResult(), bundle)
        assert any("introduces years" in issue for issue in report.blocking_issues)

    def test_dropped_year_blocks(self, candidate_dir):
        bundle = self.make_bundle(candidate_dir)
        tailored = BASE.replace("(2020-present)", "(recently)")
        report = validate_tailored_resume(tailored, BASE, ResumeTailoringResult(), bundle)
        assert any("dropped employment years" in issue for issue in report.blocking_issues)

    def test_unsupported_skill_blocks(self, candidate_dir):
        bundle = self.make_bundle(candidate_dir)
        plan = ResumeTailoringResult(skills_order=["COBOL"])
        rendered = render_tailored_resume(BASE, plan)
        report = validate_tailored_resume(rendered, BASE, plan, bundle)
        assert any("COBOL" in issue for issue in report.blocking_issues)

    def test_invented_metric_in_bullet_blocks(self, candidate_dir):
        bundle = self.make_bundle(candidate_dir)
        plan = ResumeTailoringResult(
            revised_bullets=[
                RevisedBullet(
                    original="Designed order services in Python",
                    revised="Designed order services in Python, improving throughput 300%",
                    supporting_sources=["base_resume"],
                )
            ]
        )
        rendered = render_tailored_resume(BASE, plan)
        report = validate_tailored_resume(rendered, BASE, plan, bundle)
        assert any("unsupported metrics" in issue for issue in report.blocking_issues)

    def test_preserved_metric_passes(self, candidate_dir):
        bundle = self.make_bundle(candidate_dir)
        plan = ResumeTailoringResult(
            revised_bullets=[
                RevisedBullet(
                    original="Reduced p99 latency 40% with Kafka",
                    revised="Cut p99 latency 40% using Kafka streaming",
                    supporting_sources=["base_resume"],
                )
            ]
        )
        rendered = render_tailored_resume(BASE, plan)
        report = validate_tailored_resume(rendered, BASE, plan, bundle)
        assert report.passed

    async def test_mock_provider_tailoring_validates_end_to_end(self, candidate_dir):
        bundle = self.make_bundle(candidate_dir)
        provider = MockReasoningProvider()
        from job_platform.providers.tasks import ResumeTailoringRequest

        base = bundle.resumes[0].text
        plan = await provider.tailor_resume(
            ResumeTailoringRequest(
                job=make_job(),
                analysis=JobAnalysis(required_skills=["python", "kafka"]),
                resume_text=base,
                candidate_context="ctx",
            )
        )
        rendered = render_tailored_resume(base, plan)
        report = validate_tailored_resume(rendered, base, plan, bundle)
        assert report.passed
