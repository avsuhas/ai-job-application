"""Claude reasoning provider (docs/05).

All Anthropic SDK usage stays inside this module. Every task sends the shared
system instructions plus a task template, requests JSON only, validates the
response against the task's Pydantic model, and retries with a repair prompt
on schema violations (docs/05 Invalid Output Handling).
"""

from __future__ import annotations

import json
from typing import TypeVar

import anthropic
from pydantic import BaseModel, ValidationError

from job_platform.jobs.models import Job, JobAnalysis
from job_platform.providers.base import JobRankingRequest, ReasoningProvider
from job_platform.providers.prompts import PromptService
from job_platform.providers.tasks import (
    CoverLetterDraft,
    CoverLetterRequest,
    NarrativeAnswerRequest,
    NarrativeAnswerResult,
    ResumeSelectionRequest,
    ResumeSelectionResult,
    ResumeTailoringRequest,
    ResumeTailoringResult,
)
from job_platform.ranking.models import JobMatchResult
from job_platform.shared.config import Settings
from job_platform.shared.errors import ProviderError, ProviderResponseError
from job_platform.shared.logging import get_logger
from job_platform.shared.text import truncate

logger = get_logger("providers.claude")

DEFAULT_MODEL = "claude-opus-4-8"
MAX_OUTPUT_TOKENS = 4096
MAX_DESCRIPTION_CHARS = 20_000

ResponseModel = TypeVar("ResponseModel", bound=BaseModel)


def extract_json_payload(text: str) -> str:
    """Strip Markdown code fences and surrounding prose from a JSON reply."""
    stripped = text.strip()
    if stripped.startswith("```"):
        first_newline = stripped.index("\n")
        stripped = stripped[first_newline + 1 :]
        if stripped.rstrip().endswith("```"):
            stripped = stripped.rstrip()[:-3]
        return stripped.strip()
    # Fall back to the outermost JSON object if the model added prose.
    if not stripped.startswith("{"):
        start = stripped.find("{")
        end = stripped.rfind("}")
        if start != -1 and end > start:
            return stripped[start : end + 1]
    return stripped


def _schema_for(model: type[BaseModel]) -> str:
    return json.dumps(model.model_json_schema(), indent=2)


class ClaudeProvider(ReasoningProvider):
    name = "claude"

    def __init__(self, settings: Settings, prompts: PromptService) -> None:
        self._settings = settings
        self._prompts = prompts
        self._model = settings.reasoning.model or DEFAULT_MODEL
        client_kwargs: dict = {
            "timeout": settings.reasoning.timeout_seconds,
            # SDK retries transport-level failures; schema repair is ours.
            "max_retries": 2,
        }
        if settings.anthropic_api_key:
            client_kwargs["api_key"] = settings.anthropic_api_key
        if settings.reasoning.base_url:
            client_kwargs["base_url"] = settings.reasoning.base_url
        self._client = anthropic.AsyncAnthropic(**client_kwargs)

    async def _request_text(self, messages: list[dict]) -> str:
        try:
            response = await self._client.messages.create(
                model=self._model,
                max_tokens=MAX_OUTPUT_TOKENS,
                system=self._prompts.system_instructions(),
                messages=messages,
            )
        except anthropic.AuthenticationError as exc:
            raise ProviderError(
                "Claude authentication failed. Check ANTHROPIC_API_KEY in .env.",
                details={"provider_error": str(exc)},
            ) from exc
        except anthropic.RateLimitError as exc:
            raise ProviderError(
                "Claude rate limit exceeded; retry later.",
                details={"provider_error": str(exc)},
            ) from exc
        except anthropic.APIStatusError as exc:
            raise ProviderError(
                f"Claude API error (status {exc.status_code}).",
                details={"provider_error": exc.message, "status": exc.status_code},
            ) from exc
        except anthropic.APIConnectionError as exc:
            raise ProviderError(
                "Could not reach the Claude API. Check the network connection "
                "and any configured base_url.",
                details={"provider_error": str(exc)},
            ) from exc

        if response.stop_reason == "refusal":
            raise ProviderError(
                "The reasoning provider declined this request.",
                details={"stop_reason": "refusal"},
            )
        text = "".join(block.text for block in response.content if block.type == "text")
        if not text:
            raise ProviderResponseError(
                "Claude returned no text content.",
                details={"stop_reason": response.stop_reason},
            )
        usage = response.usage
        logger.info(
            "Claude task complete (model=%s, input_tokens=%s, output_tokens=%s)",
            self._model,
            usage.input_tokens,
            usage.output_tokens,
        )
        return text

    async def _structured_task(
        self,
        template: str,
        variables: dict[str, str],
        response_model: type[ResponseModel],
    ) -> ResponseModel:
        variables = {**variables, "output_schema": _schema_for(response_model)}
        prompt = self._prompts.render(template, variables)
        messages: list[dict] = [{"role": "user", "content": prompt}]

        last_error: Exception | None = None
        for attempt in range(1 + self._settings.reasoning.max_retries):
            text = await self._request_text(messages)
            payload = extract_json_payload(text)
            try:
                return response_model.model_validate_json(payload)
            except ValidationError as exc:
                last_error = exc
                errors = "\n".join(
                    f"- {'.'.join(str(p) for p in e['loc'])}: {e['msg']}" for e in exc.errors()
                )
                logger.warning(
                    "Claude response failed validation for %s (attempt %d): %s",
                    template,
                    attempt + 1,
                    errors,
                )
                messages = messages + [
                    {"role": "assistant", "content": text},
                    {
                        "role": "user",
                        "content": (
                            "Your previous response did not match the required schema.\n\n"
                            f"Validation errors:\n{errors}\n\n"
                            "Return the corrected JSON only. Do not include Markdown "
                            "or explanation outside the JSON."
                        ),
                    },
                ]
        raise ProviderResponseError(
            f"Claude output failed schema validation for task '{template}' after "
            f"{self._settings.reasoning.max_retries + 1} attempts.",
            details={"task": template, "last_error": str(last_error)},
        )

    async def analyze_job(self, job: Job) -> JobAnalysis:
        return await self._structured_task(
            "job_analysis",
            {
                "company": job.company,
                "title": job.title,
                "location": job.location or "Unknown",
                "description": truncate(job.description, MAX_DESCRIPTION_CHARS),
            },
            JobAnalysis,
        )

    async def rank_job(self, request: JobRankingRequest) -> JobMatchResult:
        return await self._structured_task(
            "job_ranking",
            {
                "candidate_context": request.candidate_context,
                "resume_inventory": request.resume_inventory,
                "company": request.job.company,
                "title": request.job.title,
                "location": request.job.location or "Unknown",
                "job_analysis": request.analysis.model_dump_json(indent=2),
            },
            JobMatchResult,
        )

    async def select_resume(self, request: ResumeSelectionRequest) -> ResumeSelectionResult:
        return await self._structured_task(
            "resume_selection",
            {
                "candidate_rules": request.candidate_rules or "None provided.",
                "resume_inventory": request.resume_inventory,
                "company": request.job.company,
                "title": request.job.title,
                "job_analysis": request.analysis.model_dump_json(indent=2),
            },
            ResumeSelectionResult,
        )

    async def tailor_resume(self, request: ResumeTailoringRequest) -> ResumeTailoringResult:
        return await self._structured_task(
            "resume_tailoring",
            {
                "candidate_context": request.candidate_context,
                "candidate_rules": request.candidate_rules or "None provided.",
                "resume_text": request.resume_text,
                "company": request.job.company,
                "title": request.job.title,
                "job_analysis": request.analysis.model_dump_json(indent=2),
            },
            ResumeTailoringResult,
        )

    async def generate_cover_letter(self, request: CoverLetterRequest) -> CoverLetterDraft:
        return await self._structured_task(
            "cover_letter",
            {
                "max_words": str(request.max_words),
                "excluded_topics": ", ".join(request.excluded_topics) or "nothing specific",
                "candidate_context": request.candidate_context,
                "template": request.template or "None provided.",
                "company": request.job.company,
                "title": request.job.title,
                "job_analysis": request.analysis.model_dump_json(indent=2),
            },
            CoverLetterDraft,
        )

    async def generate_application_answer(
        self, request: NarrativeAnswerRequest
    ) -> NarrativeAnswerResult:
        return await self._structured_task(
            "answer_generation",
            {
                "character_limit": (
                    str(request.character_limit) if request.character_limit else "none"
                ),
                "candidate_context": request.candidate_context,
                "question_family": request.question_family,
                "question": request.canonical_question,
                "company": request.job.company,
                "title": request.job.title,
            },
            NarrativeAnswerResult,
        )
