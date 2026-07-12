"""Tests for the Phase 3 provider task contracts (selection, tailoring,
cover letters, narrative answers) on both Claude (stubbed SDK) and mock."""

import json

from job_platform.jobs.models import JobAnalysis
from job_platform.providers.mock import MockReasoningProvider
from job_platform.providers.tasks import (
    CoverLetterDraft,
    CoverLetterRequest,
    NarrativeAnswerRequest,
    ResumeSelectionRequest,
    ResumeTailoringRequest,
)
from tests.unit.test_providers import make_claude_provider, make_job

RESUME_INVENTORY = "- id=backend file=Backend.pdf format=pdf\n- id=ml file=ML.pdf format=pdf"

RESUME_TEXT = """Alex Sample
Senior Backend Engineer

EXPERIENCE
ExampleCorp — Senior Backend Engineer (2020–present)
- Designed distributed order-processing services in Python
- Reduced p99 latency 40% with Kafka

SKILLS
Python, Kafka, AWS
"""


def analysis() -> JobAnalysis:
    return JobAnalysis(job_family="Backend Engineering", required_skills=["python", "kafka"])


class TestClaudeProviderTasks:
    async def test_select_resume(self):
        payload = json.dumps(
            {"selected_resume_id": "backend", "reasoning": "Best match", "confidence": 0.9}
        )
        provider = make_claude_provider([payload])
        result = await provider.select_resume(
            ResumeSelectionRequest(
                job=make_job(), analysis=analysis(), resume_inventory=RESUME_INVENTORY
            )
        )
        assert result.selected_resume_id == "backend"
        prompt = provider._client.messages.create.await_args_list[0].kwargs["messages"][0][
            "content"
        ]
        assert "id=backend" in prompt

    async def test_tailor_resume(self):
        payload = json.dumps(
            {
                "professional_summary": "Backend engineer...",
                "skills_order": ["Python", "Kafka"],
                "revised_bullets": [
                    {
                        "original": "Designed distributed order-processing services in Python",
                        "revised": "Designed Python distributed systems for order processing",
                        "supporting_sources": ["base_resume"],
                        "reason": "emphasis",
                    }
                ],
            }
        )
        provider = make_claude_provider([payload])
        result = await provider.tailor_resume(
            ResumeTailoringRequest(
                job=make_job(),
                analysis=analysis(),
                resume_text=RESUME_TEXT,
                candidate_context="ctx",
            )
        )
        assert result.skills_order == ["Python", "Kafka"]
        assert result.revised_bullets[0].supporting_sources == ["base_resume"]

    async def test_generate_cover_letter(self):
        payload = json.dumps(
            {
                "body_paragraphs": ["I am applying for X.", "My experience fits."],
                "signature_name": "Alex Sample",
                "word_count": 12,
                "candidate_sources": ["resume"],
            }
        )
        provider = make_claude_provider([payload])
        draft = await provider.generate_cover_letter(
            CoverLetterRequest(job=make_job(), analysis=analysis(), candidate_context="ctx")
        )
        rendered = draft.render()
        assert rendered.startswith("Dear Hiring Team,")
        assert "Alex Sample" in rendered

    async def test_generate_application_answer(self):
        payload = json.dumps({"answer": "Because I like it.", "confidence": 0.8})
        provider = make_claude_provider([payload])
        result = await provider.generate_application_answer(
            NarrativeAnswerRequest(
                job=make_job(),
                canonical_question="Why do you want to work here?",
                question_family="narrative.why_company",
                candidate_context="ctx",
            )
        )
        assert result.answer == "Because I like it."


class TestMockProviderTasks:
    async def test_select_resume_prefers_matching_family(self):
        provider = MockReasoningProvider()
        result = await provider.select_resume(
            ResumeSelectionRequest(
                job=make_job(),
                analysis=JobAnalysis(job_family="ml engineering"),
                resume_inventory=RESUME_INVENTORY,
            )
        )
        assert result.selected_resume_id == "ml"
        assert "backend" in result.alternatives

    async def test_tailor_resume_only_reorders_supported_skills(self):
        provider = MockReasoningProvider()
        result = await provider.tailor_resume(
            ResumeTailoringRequest(
                job=make_job(),
                analysis=JobAnalysis(required_skills=["python", "rust"]),
                resume_text=RESUME_TEXT,
                candidate_context="ctx",
            )
        )
        assert "python" in result.skills_order
        assert "rust" not in result.skills_order  # not in the base resume

    async def test_cover_letter_mentions_company_and_role(self):
        provider = MockReasoningProvider()
        draft = await provider.generate_cover_letter(
            CoverLetterRequest(
                job=make_job(),
                analysis=analysis(),
                candidate_context='"first_name": "Alex",',
            )
        )
        assert isinstance(draft, CoverLetterDraft)
        text = draft.render()
        assert "ExampleCo" in text
        assert "Senior Backend Engineer" in text

    async def test_narrative_answer_respects_character_limit(self):
        provider = MockReasoningProvider()
        result = await provider.generate_application_answer(
            NarrativeAnswerRequest(
                job=make_job(),
                canonical_question="Why here?",
                question_family="narrative.why_company",
                candidate_context="ctx",
                character_limit=40,
            )
        )
        assert len(result.answer) <= 40
