"""Greenhouse job-board adapter.

Uses the public board API (no auth):
GET https://boards-api.greenhouse.io/v1/boards/{token}/jobs?content=true
"""

from __future__ import annotations

from datetime import datetime

import httpx

from job_platform.jobs.adapters.base import REQUEST_TIMEOUT, DiscoveryAdapter
from job_platform.jobs.models import Job
from job_platform.jobs.normalizer import html_to_text
from job_platform.jobs.sources import CompanySource
from job_platform.shared.errors import DiscoveryError

API_URL = "https://boards-api.greenhouse.io/v1/boards/{token}/jobs"


def _parse_date(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


class GreenhouseAdapter(DiscoveryAdapter):
    ats = "greenhouse"

    async def discover(self, source: CompanySource, board_token: str) -> list[Job]:
        url = API_URL.format(token=board_token)
        async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
            try:
                response = await client.get(url, params={"content": "true"})
                response.raise_for_status()
            except httpx.HTTPStatusError as exc:
                raise DiscoveryError(
                    f"Greenhouse board '{board_token}' for {source.name} returned "
                    f"HTTP {exc.response.status_code}.",
                    details={"url": url, "status": exc.response.status_code},
                ) from exc
            except httpx.HTTPError as exc:
                raise DiscoveryError(
                    f"Could not reach Greenhouse for {source.name}: {exc}",
                    details={"url": url},
                ) from exc
        payload = response.json()

        jobs: list[Job] = []
        for entry in payload.get("jobs", []):
            departments = entry.get("departments") or []
            jobs.append(
                Job(
                    id="",  # assigned during normalization
                    company=source.name,
                    title=entry.get("title", ""),
                    job_id=str(entry.get("id", "")),
                    location=(entry.get("location") or {}).get("name", ""),
                    url=entry.get("absolute_url", ""),
                    description=html_to_text(entry.get("content", "") or ""),
                    department=departments[0].get("name", "") if departments else "",
                    date_posted=_parse_date(entry.get("first_published"))
                    or _parse_date(entry.get("updated_at")),
                    ats=self.ats,
                    source=source.id,
                    raw=entry,
                )
            )
        return jobs
