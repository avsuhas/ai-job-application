"""Lever postings adapter.

Uses the public postings API (no auth):
GET https://api.lever.co/v0/postings/{org}?mode=json
"""

from __future__ import annotations

from datetime import UTC, datetime

import httpx

from job_platform.jobs.adapters.base import REQUEST_TIMEOUT, DiscoveryAdapter
from job_platform.jobs.models import Job
from job_platform.jobs.sources import CompanySource
from job_platform.shared.errors import DiscoveryError

API_URL = "https://api.lever.co/v0/postings/{org}"

_WORKPLACE_TO_REMOTE = {"remote": "remote", "hybrid": "hybrid", "onsite": "onsite", "on-site": "onsite"}


class LeverAdapter(DiscoveryAdapter):
    ats = "lever"

    async def discover(self, source: CompanySource, board_token: str) -> list[Job]:
        url = API_URL.format(org=board_token)
        async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
            try:
                response = await client.get(url, params={"mode": "json"})
                response.raise_for_status()
            except httpx.HTTPStatusError as exc:
                raise DiscoveryError(
                    f"Lever board '{board_token}' for {source.name} returned "
                    f"HTTP {exc.response.status_code}.",
                    details={"url": url, "status": exc.response.status_code},
                ) from exc
            except httpx.HTTPError as exc:
                raise DiscoveryError(
                    f"Could not reach Lever for {source.name}: {exc}",
                    details={"url": url},
                ) from exc
        payload = response.json()

        jobs: list[Job] = []
        for entry in payload:
            categories = entry.get("categories") or {}
            created_ms = entry.get("createdAt")
            date_posted = (
                datetime.fromtimestamp(created_ms / 1000, tz=UTC) if created_ms else None
            )
            workplace = (entry.get("workplaceType") or "").lower()
            jobs.append(
                Job(
                    id="",
                    company=source.name,
                    title=entry.get("text", ""),
                    job_id=str(entry.get("id", "")),
                    location=categories.get("location", "") or "",
                    country=entry.get("country", "") or "",
                    url=entry.get("hostedUrl", ""),
                    description=entry.get("descriptionPlain", "") or "",
                    department=categories.get("team", "") or "",
                    employment_type=categories.get("commitment", "") or "",
                    remote_status=_WORKPLACE_TO_REMOTE.get(workplace, ""),
                    date_posted=date_posted,
                    ats=self.ats,
                    source=source.id,
                    raw=entry,
                )
            )
        return jobs
