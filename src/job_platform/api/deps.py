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
from job_platform.orchestration.admission import QueueAdmissionController
from job_platform.orchestration.automatic import KillSwitch
from job_platform.orchestration.eligibility import AutomaticEligibility
from job_platform.orchestration.locks import LockManager
from job_platform.orchestration.models import WorkflowState
from job_platform.orchestration.queue import QueueManager
from job_platform.orchestration.workflow import ApplicationWorkflow
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
from job_platform.submission.history import ApplicationHistoryService
from job_platform.submission.service import SubmissionService


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

    def lock_manager(self) -> LockManager:
        return LockManager(
            self.settings.paths.packages_dir,
            self.settings.paths.browser_profile_dir,
        )

    def history_service(self) -> ApplicationHistoryService:
        return ApplicationHistoryService(
            self.tracker,
            self.settings.paths.applications_dir / "history_events.jsonl",
            self.settings.paths.applications_dir / "tracker.xlsx",
        )

    def submission_service(self) -> SubmissionService:
        return SubmissionService(self.package_store, self.tracker, self.history_service())

    def kill_switch(self) -> KillSwitch:
        return KillSwitch(self.settings.paths.data_root)

    def eligibility_engine(self) -> AutomaticEligibility:
        return AutomaticEligibility(
            self.settings.automatic_mode,
            self.package_store,
            self.tracker,
            self.kill_switch(),
        )

    async def _run_workflow(
        self,
        package_id: str,
        queue_id: str,
        submit: bool = False,
        automatic: bool = False,
    ) -> WorkflowState:
        manifest = self.package_store.load_manifest(package_id)
        needs_submission = submit or automatic
        workflow = ApplicationWorkflow(
            manifest=manifest,
            bundle=self.candidate_bundle(),
            store=self.package_store,
            provider=self.provider,
            registry=self.ats_registry,
            readiness=self.readiness_service(),
            locks=self.lock_manager(),
            settings=self.settings,
            queue_id=queue_id,
            submit_mode=submit,
            automatic_mode=automatic,
            submission_service=self.submission_service() if needs_submission else None,
            eligibility=self.eligibility_engine() if automatic else None,
            history=self.history_service() if automatic else None,
        )
        return await workflow.run()

    async def _run_automatic_workflow(
        self, package_id: str, queue_id: str
    ) -> WorkflowState:
        return await self._run_workflow(package_id, queue_id, automatic=True)

    async def run_submission_workflow(self, package_id: str) -> WorkflowState:
        """Run the approved-submission workflow for one package, holding the
        browser profile lock like a queue run would."""
        profile_lock = self.lock_manager().profile_lock("default")
        profile_lock.acquire()
        try:
            return await self._run_workflow(package_id, queue_id="", submit=True)
        finally:
            profile_lock.release()

    def queue_manager(self, automatic: bool = False) -> QueueManager:
        attr = "_auto_queue_manager" if automatic else "_queue_manager"
        if not hasattr(self, attr):
            locks = self.lock_manager()
            runner = self._run_automatic_workflow if automatic else self._run_workflow
            setattr(
                self,
                attr,
                QueueManager(
                    queues_dir=self.settings.paths.queues_dir,
                    package_store=self.package_store,
                    admission=QueueAdmissionController(
                        self.package_store, self.readiness_service(), locks
                    ),
                    locks=locks,
                    workflow_runner=runner,
                ),
            )
        return getattr(self, attr)


def get_state(request: Request) -> AppState:
    return request.app.state.container
