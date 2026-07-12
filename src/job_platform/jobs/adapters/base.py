"""Discovery adapter interface (docs/09 discovery side, docs/02D)."""

from __future__ import annotations

from abc import ABC, abstractmethod

import httpx

from job_platform.jobs.models import Job
from job_platform.jobs.sources import CompanySource

REQUEST_TIMEOUT = httpx.Timeout(30.0)


class DiscoveryAdapter(ABC):
    """Fetches raw job postings from one ATS platform for one company."""

    ats: str = ""

    @abstractmethod
    async def discover(self, source: CompanySource, board_token: str) -> list[Job]:
        """Return raw (un-normalized) jobs for a company board."""
