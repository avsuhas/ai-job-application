"""Provider factory (docs/05): the rest of the app never instantiates SDKs."""

from __future__ import annotations

from job_platform.providers.base import ReasoningProvider
from job_platform.providers.claude import ClaudeProvider
from job_platform.providers.mock import MockReasoningProvider
from job_platform.providers.prompts import PromptService
from job_platform.shared.config import Settings
from job_platform.shared.errors import ConfigurationError


def create_provider(settings: Settings, prompts: PromptService | None = None) -> ReasoningProvider:
    provider_name = settings.reasoning.provider.lower()
    if provider_name == "claude":
        return ClaudeProvider(settings, prompts or PromptService(settings.prompts_dir))
    if provider_name == "mock":
        return MockReasoningProvider()
    raise ConfigurationError(
        f"Unknown reasoning provider '{settings.reasoning.provider}'. "
        "Supported providers: claude, mock.",
        details={"provider": settings.reasoning.provider},
    )
