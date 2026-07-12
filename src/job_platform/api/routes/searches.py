"""Search endpoints: run the discover → rank workflow and expose results.

POST /api/searches starts a search. With ``wait=true`` the request blocks
until the workflow completes (useful for scripts and tests); otherwise it
runs in the background and clients poll GET /api/searches/{id}.
"""

from __future__ import annotations

import asyncio

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field

from job_platform.api.deps import AppState, get_state
from job_platform.jobs.service import SearchFilters
from job_platform.ranking.models import RankedJob
from job_platform.shared.logging import get_logger
from job_platform.storage.search_store import SearchRecord

router = APIRouter(tags=["searches"])
logger = get_logger("api.searches")

# Keep references to background tasks so they are not garbage collected.
_background_tasks: set[asyncio.Task] = set()


class SearchRequest(BaseModel):
    source_ids: list[str] = Field(
        default_factory=list, description="Company ids to search; empty = all enabled"
    )
    filters: SearchFilters = Field(default_factory=SearchFilters)
    rank: bool = Field(default=True, description="Rank discovered jobs with the provider")


async def _run_search(state: AppState, record: SearchRecord, request: SearchRequest) -> None:
    store = state.search_store
    try:
        record.status = "discovering"
        record.progress_message = "Discovering jobs from configured sources"
        store.save(record)

        sources = state.companies
        if request.source_ids:
            wanted = set(request.source_ids)
            sources = [s for s in sources if s.id in wanted]
        record.source_ids = [s.id for s in sources]

        discovery = await state.discovery.discover(sources, request.filters)
        record.discovery = discovery
        jobs = discovery.jobs

        if state.settings.job_search.hide_already_applied:
            jobs = [job for job in jobs if not state.tracker.is_duplicate(job)]

        if request.rank and jobs:
            record.status = "ranking"
            record.progress_message = f"Ranking {len(jobs)} discovered jobs"
            store.save(record)
            bundle = state.candidate_bundle()
            record.ranked_jobs = await state.ranking_engine().rank_jobs(jobs, bundle)
        else:
            record.ranked_jobs = []

        record.status = "complete"
        record.progress_message = (
            f"Found {len(jobs)} jobs"
            + (f", ranked {len(record.ranked_jobs)}" if request.rank else "")
        )
        store.save(record)
    except Exception as exc:  # noqa: BLE001 - background task must record failures
        logger.exception("Search %s failed", record.search_id)
        record.status = "failed"
        record.error = str(exc)
        store.save(record)


@router.post("/api/searches", status_code=202)
async def create_search(
    request: SearchRequest,
    wait: bool = Query(default=False, description="Block until the search completes"),
    state: AppState = Depends(get_state),
) -> dict:
    record = SearchRecord(filters=request.filters)
    state.search_store.save(record)
    if wait:
        await _run_search(state, record, request)
        record = state.search_store.load(record.search_id)
    else:
        task = asyncio.create_task(_run_search(state, record, request))
        _background_tasks.add(task)
        task.add_done_callback(_background_tasks.discard)
    return {"search_id": record.search_id, "status": record.status}


@router.get("/api/searches/{search_id}")
def get_search(search_id: str, state: AppState = Depends(get_state)) -> dict:
    record = state.search_store.load(search_id)
    return {
        "search_id": record.search_id,
        "status": record.status,
        "progress_message": record.progress_message,
        "error": record.error,
        "created_at": record.created_at,
        "source_outcomes": (
            [o.model_dump() for o in record.discovery.outcomes] if record.discovery else []
        ),
        "job_count": len(record.discovery.jobs) if record.discovery else 0,
        "ranked_count": len(record.ranked_jobs),
    }


def _job_payload(ranked: RankedJob) -> dict:
    return {
        "job": ranked.job.model_dump(mode="json", exclude={"raw"}),
        "score": ranked.score,
        "recommendation": ranked.recommendation.value,
        "eligibility_flags": ranked.eligibility_flags,
        "match": ranked.match.model_dump() if ranked.match else None,
        "analysis": ranked.analysis.model_dump() if ranked.analysis else None,
        "error": ranked.error,
    }


@router.get("/api/searches/{search_id}/jobs")
def get_search_jobs(
    search_id: str,
    min_score: int = Query(default=0, ge=0, le=100),
    country: str | None = None,
    company: str | None = None,
    remote_only: bool = False,
    sort: str = Query(default="score", pattern="^(score|date|company|title|country)$"),
    state: AppState = Depends(get_state),
) -> dict:
    record = state.search_store.load(search_id)
    ranked = record.ranked_jobs
    if not ranked and record.discovery:
        # Un-ranked search: expose discovered jobs with neutral ranking data.
        from job_platform.ranking.models import Recommendation

        ranked = [
            RankedJob(job=job, recommendation=Recommendation.POSSIBLE_MATCH)
            for job in record.discovery.jobs
        ]

    results = [r for r in ranked if r.score >= min_score]
    if country:
        results = [r for r in results if r.job.country.lower() == country.lower()]
    if company:
        results = [r for r in results if r.job.company.lower() == company.lower()]
    if remote_only:
        results = [r for r in results if r.job.remote_status == "remote"]

    keys = {
        "score": lambda r: -r.score,
        "date": lambda r: (r.job.date_posted is None, str(r.job.date_posted or "")),
        "company": lambda r: r.job.company.lower(),
        "title": lambda r: r.job.title.lower(),
        "country": lambda r: r.job.country.lower(),
    }
    reverse = sort == "date"
    results = sorted(results, key=keys[sort], reverse=reverse)
    return {"search_id": search_id, "count": len(results), "jobs": [_job_payload(r) for r in results]}
