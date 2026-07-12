"""Job discovery service (docs/02D Discovery Pipeline).

Career sources → adapter fetch → normalization → deduplication → filtering.
Ranking runs separately on the discovered jobs (ranking module).
"""

from __future__ import annotations

import asyncio

from pydantic import BaseModel, Field

from job_platform.jobs.adapters.base import DiscoveryAdapter
from job_platform.jobs.adapters.greenhouse import GreenhouseAdapter
from job_platform.jobs.adapters.lever import LeverAdapter
from job_platform.jobs.deduplicator import deduplicate
from job_platform.jobs.models import Job
from job_platform.jobs.normalizer import normalize_job
from job_platform.jobs.sources import CompanySource, detect_ats
from job_platform.shared.errors import DiscoveryError
from job_platform.shared.logging import get_logger

logger = get_logger("jobs.service")


class SearchFilters(BaseModel):
    keywords: list[str] = Field(default_factory=list)
    excluded_keywords: list[str] = Field(default_factory=list)
    countries: list[str] = Field(default_factory=list)
    locations: list[str] = Field(default_factory=list)
    remote_only: bool = False
    max_results_per_source: int = 100


class SourceOutcome(BaseModel):
    source_id: str
    ats: str = ""
    job_count: int = 0
    error: str | None = None


class DiscoveryResult(BaseModel):
    jobs: list[Job] = Field(default_factory=list)
    outcomes: list[SourceOutcome] = Field(default_factory=list)


def matches_filters(job: Job, filters: SearchFilters) -> bool:
    haystack = f"{job.title}\n{job.description}\n{job.department}".lower()
    if filters.keywords and not any(k.lower() in haystack for k in filters.keywords):
        return False
    if any(k.lower() in haystack for k in filters.excluded_keywords):
        return False
    if filters.countries:
        wanted = {c.lower() for c in filters.countries}
        country = job.country.lower()
        location = job.location.lower()
        if country not in wanted and not any(c in location for c in wanted):
            return False
    if filters.locations and not any(
        loc.lower() in job.location.lower() for loc in filters.locations
    ):
        return False
    if filters.remote_only and job.remote_status != "remote":
        return False
    return True


class DiscoveryService:
    def __init__(self, adapters: dict[str, DiscoveryAdapter] | None = None) -> None:
        self._adapters = adapters or {
            "greenhouse": GreenhouseAdapter(),
            "lever": LeverAdapter(),
        }

    async def _discover_source(
        self, source: CompanySource, filters: SearchFilters
    ) -> tuple[list[Job], SourceOutcome]:
        ats, token = detect_ats(source.career_url)
        if not ats:
            ats = source.expected_ats
        adapter = self._adapters.get(ats)
        if adapter is None or not token:
            return [], SourceOutcome(
                source_id=source.id,
                ats=ats,
                error=(
                    f"No supported ATS adapter for {source.name} "
                    f"(url={source.career_url!r}). Supported: "
                    f"{', '.join(sorted(self._adapters))}."
                ),
            )
        try:
            raw_jobs = await adapter.discover(source, token)
        except DiscoveryError as exc:
            logger.warning("Discovery failed for %s: %s", source.id, exc.message)
            return [], SourceOutcome(source_id=source.id, ats=ats, error=exc.message)

        normalized = [normalize_job(job) for job in raw_jobs]
        filtered = [job for job in normalized if matches_filters(job, filters)]
        capped = filtered[: filters.max_results_per_source]
        return capped, SourceOutcome(source_id=source.id, ats=ats, job_count=len(capped))

    async def discover(
        self, sources: list[CompanySource], filters: SearchFilters | None = None
    ) -> DiscoveryResult:
        filters = filters or SearchFilters()
        enabled = [s for s in sources if s.enabled]
        results = await asyncio.gather(
            *(self._discover_source(source, filters) for source in enabled)
        )
        all_jobs: list[Job] = []
        outcomes: list[SourceOutcome] = []
        for jobs, outcome in results:
            all_jobs.extend(jobs)
            outcomes.append(outcome)
        unique = deduplicate(all_jobs)
        logger.info(
            "Discovery complete: %d jobs from %d sources (%d before dedup)",
            len(unique),
            len(enabled),
            len(all_jobs),
        )
        return DiscoveryResult(jobs=unique, outcomes=outcomes)
