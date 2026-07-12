"""Navigation trust policy (docs/06 URL Trust Rules).

The browser may navigate only to explicitly allowed destinations: the
application URL for the selected job, its host, known ATS domains, and
user-approved URLs. Everything else is refused before navigation.
"""

from __future__ import annotations

from urllib.parse import urlparse

from pydantic import BaseModel, Field

# ATS platforms whose domains an application may legitimately redirect through.
KNOWN_ATS_DOMAINS = [
    "greenhouse.io",
    "lever.co",
    "myworkdayjobs.com",
    "smartrecruiters.com",
    "ashbyhq.com",
    "icims.com",
    "taleo.net",
    "successfactors.com",
]


def _host(url: str) -> str:
    return (urlparse(url).hostname or "").lower()


def _registrable_suffix_match(host: str, domain: str) -> bool:
    return host == domain or host.endswith("." + domain)


class NavigationPolicy(BaseModel):
    """Allow-list policy built per workflow (docs/06)."""

    allowed_urls: list[str] = Field(default_factory=list)
    allowed_domains: list[str] = Field(default_factory=list)
    allow_local_files: bool = False

    @classmethod
    def for_application(
        cls,
        application_url: str,
        extra_urls: list[str] | None = None,
        allow_local_files: bool = False,
    ) -> NavigationPolicy:
        urls = [application_url] + list(extra_urls or [])
        domains = [_host(u) for u in urls if _host(u)]
        return cls(
            allowed_urls=urls,
            allowed_domains=domains + KNOWN_ATS_DOMAINS,
            allow_local_files=allow_local_files,
        )

    def is_allowed(self, url: str) -> bool:
        parsed = urlparse(url)
        if parsed.scheme == "file":
            return self.allow_local_files
        if parsed.scheme not in ("http", "https"):
            return False
        host = (parsed.hostname or "").lower()
        if not host:
            return False
        return any(
            _registrable_suffix_match(host, domain)
            for domain in self.allowed_domains
            if domain
        )
