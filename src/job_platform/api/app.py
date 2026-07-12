"""FastAPI application factory and startup sequence (docs/04)."""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from job_platform.api.deps import AppState
from job_platform.api.routes import (
    applications,
    ats,
    browser,
    candidate,
    companies,
    history,
    searches,
    system,
)
from job_platform.shared.config import Settings, load_settings
from job_platform.shared.errors import (
    CandidateDataError,
    ConfigurationError,
    DiscoveryError,
    DuplicateApplicationError,
    JobPlatformError,
    ProviderError,
    StorageError,
)
from job_platform.shared.files import ensure_dir
from job_platform.shared.logging import configure_logging, get_logger
from job_platform.version import __version__

logger = get_logger("api.app")

_STATUS_BY_ERROR: list[tuple[type[JobPlatformError], int]] = [
    (DuplicateApplicationError, 409),
    (StorageError, 404),
    (CandidateDataError, 422),
    (DiscoveryError, 502),
    (ProviderError, 502),
    (ConfigurationError, 500),
]


def _status_for(exc: JobPlatformError) -> int:
    for error_type, status in _STATUS_BY_ERROR:
        if isinstance(exc, error_type):
            return status
    return 500


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or load_settings()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        for directory in settings.paths.runtime_directories():
            ensure_dir(directory)
        configure_logging(settings.paths.logs_dir)
        state = AppState.build(settings)
        state.tracker.initialize()
        app.state.container = state
        logger.info(
            "job-platform %s started (provider=%s, companies=%d)",
            __version__,
            state.provider.name,
            len(state.companies),
        )
        yield

    app = FastAPI(
        title="Job Platform",
        version=__version__,
        description="Local-first LLM-powered job search and application platform",
        lifespan=lifespan,
    )

    @app.exception_handler(JobPlatformError)
    async def handle_platform_error(request: Request, exc: JobPlatformError) -> JSONResponse:
        return JSONResponse(status_code=_status_for(exc), content={"error": exc.to_dict()})

    app.include_router(system.router)
    app.include_router(candidate.router)
    app.include_router(companies.router)
    app.include_router(searches.router)
    app.include_router(applications.router)
    app.include_router(history.router)
    app.include_router(browser.router)
    app.include_router(ats.router)
    return app
