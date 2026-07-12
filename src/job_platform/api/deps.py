"""Application state and dependency wiring for the API layer."""

from __future__ import annotations

from dataclasses import dataclass, field

from fastapi import Request

from job_platform.ats.greenhouse import default_registry
from job_platform.ats.registry import ATSAdapterRegistry
from job_platform.candidate.loader import load_candidate_bundle
from job_platform.candidate.models import CandidateBundle
from job_platform.jobs.service import DiscoveryService
from job_platform.jobs.sources import CompanySource, load_company_sources
from job_platform.packages.store import PackageStore
from job_platform.preparation.service import PreparationService
from job_platform.providers.base import ReasoningProvider
from job_platform.providers.factory import create_provider
from job_platform.ranking.ranker import RankingEngine
from job_platform.readiness.service import ReadinessService
from job_platform.review.service import ReviewService
from job_platform.shared.config import Settings
from job_platform.storage.search_store import SearchStore
from job_platform.storage.tracker import ApplicationTracker


@dataclass
class AppState:
    settings: Settings
    provider: ReasoningProvider
    discovery: DiscoveryService
    tracker: ApplicationTracker
    search_store: SearchStore
    package_store: PackageStore
    ats_registry: ATSAdapterRegistry
    companies: list[CompanySource] = field(default_factory=list)
    _bundle: CandidateBundle | None = None

    @classmethod
    def build(cls, settings: Settings) -> AppState:
        return cls(
            settings=settings,
            provider=create_provider(settings),
            discovery=DiscoveryService(),
            tracker=ApplicationTracker(settings.paths.tracker_path),
            search_store=SearchStore(settings.paths.searches_dir),
            package_store=PackageStore(settings.paths.packages_dir),
            ats_registry=default_registry(),
            companies=load_company_sources(settings.companies_path),
        )

    def candidate_bundle(self, reload: bool = False) -> CandidateBundle:
        if self._bundle is None or reload:
            self._bundle = load_candidate_bundle(self.settings.paths.candidate_dir)
        return self._bundle

    def ranking_engine(self) -> RankingEngine:
        return RankingEngine(self.provider)

    def preparation_service(self) -> PreparationService:
        return PreparationService(
            self.provider, self.package_store, self.settings, tracker=self.tracker
        )

    def review_service(self) -> ReviewService:
        return ReviewService(
            self.package_store,
            known_companies=[c.name for c in self.companies],
        )

    def readiness_service(self) -> ReadinessService:
        return ReadinessService(self.package_store, tracker=self.tracker)


def get_state(request: Request) -> AppState:
    return request.app.state.container
