"""Structured application errors.

Every error carries a stable machine-readable code so API responses,
logs, and retry policies can react without parsing messages.
"""

from __future__ import annotations

from typing import Any


class JobPlatformError(Exception):
    """Base class for all application errors."""

    code = "internal_error"

    def __init__(self, message: str, *, details: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}

    def to_dict(self) -> dict[str, Any]:
        return {"code": self.code, "message": self.message, "details": self.details}


class ConfigurationError(JobPlatformError):
    code = "configuration_error"


class CandidateDataError(JobPlatformError):
    code = "candidate_data_error"


class ProviderError(JobPlatformError):
    """The reasoning provider failed (network, auth, rate limit)."""

    code = "provider_error"


class ProviderResponseError(ProviderError):
    """The provider responded but the output failed schema validation."""

    code = "provider_response_error"


class DiscoveryError(JobPlatformError):
    code = "discovery_error"


class StorageError(JobPlatformError):
    code = "storage_error"


class BrowserError(JobPlatformError):
    code = "browser_error"


class NavigationBlockedError(BrowserError):
    """Navigation target violates the URL trust policy (docs/06)."""

    code = "navigation_blocked"


class DuplicateApplicationError(StorageError):
    code = "duplicate_application"
