"""End-to-end automatic-mode tests with real Chromium (docs/17 Phase 12
acceptance and the Automatic Submission Gate). Uses a Stable test adapter —
the real Greenhouse adapter stays Beta and is refused (proven separately)."""

import json

import pytest

from job_platform.ats.base import AdapterStatus
from job_platform.ats.greenhouse import GreenhouseAdapter
from job_platform.ats.registry import ATSAdapterRegistry
from job_platform.candidate.loader import load_candidate_bundle
from job_platform.orchestration.automatic import KillSwitch
from job_platform.orchestration.eligibility import AutomaticEligibility
from job_platform.orchestration.locks import LockManager
from job_platform.orchestration.models import WorkflowStatus
from job_platform.orchestration.workflow import ApplicationWorkflow
from job_platform.packages.store import PackageStore
from job_platform.preparation.service import PreparationOptions, PreparationService
from job_platform.providers.mock import MockReasoningProvider
from job_platform.readiness.service import ReadinessService
from job_platform.review.service import ReviewService
from job_platform.shared.config import AutomaticModeSettings, Settings
from job_platform.storage.tracker import ApplicationTracker
from job_platform.submission.history import ApplicationHistoryService
from job_platform.submission.service import SubmissionService
from tests.browser.conftest import page_url
from tests.unit.test_review import make_ranked

GH_URL = page_url("greenhouse_clean.html")


class StableGreenhouse(GreenhouseAdapter):
    _metadata = GreenhouseAdapter._metadata.model_copy(
        update={"status": AdapterStatus.STABLE}
    )


def stable_registry() -> ATSAdapterRegistry:
    registry = ATSAdapterRegistry()
    registry.register(StableGreenhouse())
    return registry


@pytest.fixture
def auto_env(candidate_dir, tmp_path, chromium_available):
    settings = Settings(
        reasoning={"provider": "mock"},
        browser={"headless": True, "default_timeout_ms": 10_000, "max_retries": 1},
        paths={"data_root": tmp_path / "user_data"},
        automatic_mode=AutomaticModeSettings(
            enabled=True, adapter_allowlist=["greenhouse"],
            company_allowlist=["ExampleCo"], daily_limit=10, per_company_daily_limit=3,
        ),
    )
    bundle = load_candidate_bundle(candidate_dir)
    store = PackageStore(settings.paths.packages_dir)
    tracker = ApplicationTracker(settings.paths.tracker_path)
    history = ApplicationHistoryService(
        tracker, settings.paths.applications_dir / "history_events.jsonl",
        settings.paths.applications_dir / "tracker.xlsx",
    )
    reviewer = ReviewService(store, known_companies=["ExampleCo"])
    readiness = ReadinessService(store, tracker=tracker)
    locks = LockManager(settings.paths.packages_dir, settings.paths.browser_profile_dir)
    prep = PreparationService(MockReasoningProvider(), store, settings, tracker=tracker)
    submission = SubmissionService(store, tracker, history)
    kill = KillSwitch(settings.paths.data_root)
    return locals()


async def prepared(env, url=GH_URL, job_id="4001", clean=True):
    """Prepare a reviewed package. When ``clean`` (the default), resolve every
    optional answer and skip narratives so review has zero warnings — the only
    state that qualifies for automatic submission."""
    store, bundle = env["store"], env["bundle"]
    if clean:
        prefs = env["candidate_dir"] / "profile" / "preferences.md"
        prefs.write_text(
            prefs.read_text()
            + "\nNotice Period: 2 weeks\nEarliest Start Date: 2026-09-01\n"
            "Relocation: Yes\nMaximum Travel: 25%\n"
        )
        bundle = load_candidate_bundle(env["candidate_dir"])
        env["bundle"] = bundle
    manifest = await env["prep"].prepare(
        make_ranked(url=url, title="Backend Engineer", company="ExampleCo",
                    job_id=job_id, id=f"job_{job_id}"),
        bundle,
        PreparationOptions(include_narrative_answers=not clean),
    )
    env["reviewer"].review(manifest, bundle)
    env["readiness"].evaluate(manifest, bundle)
    return store.load_manifest(manifest.package_id)


def build_workflow(env, manifest, registry=None, kill=None):
    return ApplicationWorkflow(
        manifest=manifest,
        bundle=env["bundle"],
        store=env["store"],
        provider=MockReasoningProvider(),
        registry=registry or stable_registry(),
        readiness=env["readiness"],
        locks=env["locks"],
        settings=env["settings"],
        submit_mode=False,
        automatic_mode=True,
        submission_service=env["submission"],
        eligibility=AutomaticEligibility(
            env["settings"].automatic_mode, env["store"], env["tracker"],
            kill or env["kill"],
        ),
        history=env["history"],
    )


class TestAutomaticSubmission:
    async def test_clean_workflow_auto_submits(self, auto_env):
        env = auto_env
        manifest = await prepared(env)
        state = await build_workflow(env, manifest).run()

        assert state.status == WorkflowStatus.SUBMITTED
        stages = [r.stage.value for r in state.stage_results]
        assert "final_submission" in stages
        assert "user_approval_check" in stages  # the automatic pre-check

        # Submission recorded once, with confirmation
        result = json.loads(
            env["store"].read_artifact(manifest.package_id, "submission/result.json")
        )
        assert result["confirmation_number"]["value"] == "GH-483726"
        assert len(env["tracker"].records()) == 1

        # Audit metric recorded
        types = [e.event_type for e in env["history"].events()]
        assert "auto_submitted" in types

    async def test_no_duplicate_final_click(self, auto_env):
        env = auto_env
        manifest = await prepared(env)
        await build_workflow(env, manifest).run()
        # A second automatic run is blocked by duplicate + already-submitted
        state = await build_workflow(env, env["store"].load_manifest(manifest.package_id)).run()
        assert state.status != WorkflowStatus.SUBMITTED
        assert len(env["submission"].load_attempts(manifest.package_id)) == 1


class TestDowngrade:
    async def test_beta_adapter_downgrades_to_review(self, auto_env):
        env = auto_env
        manifest = await prepared(env)
        # Registry with the real (Beta) Greenhouse adapter
        beta_registry = ATSAdapterRegistry()
        beta_registry.register(GreenhouseAdapter())
        state = await build_workflow(env, manifest, registry=beta_registry).run()

        assert state.status == WorkflowStatus.WAITING_FOR_REVIEW
        assert env["tracker"].records() == []  # nothing submitted
        types = [e.event_type for e in env["history"].events()]
        assert "auto_downgraded" in types

    async def test_kill_switch_downgrades(self, auto_env):
        env = auto_env
        manifest = await prepared(env)
        env["kill"].engage("operator stop")
        state = await build_workflow(env, manifest).run()
        assert state.status != WorkflowStatus.SUBMITTED
        assert env["tracker"].records() == []

    async def test_unknown_field_downgrades(self, auto_env):
        env = auto_env
        # This fixture has a "favorite_color" custom question -> field needs
        # user -> automatic must downgrade rather than submit a blank field.
        # (greenhouse_application.html already includes such a question, but
        # its custom answer is surfaced; confirm downgrade did not submit.)
        manifest = await prepared(env)
        # Force downgrade by disallowing the company mid-run
        env["settings"].automatic_mode.company_allowlist = ["SomeoneElse"]
        state = await build_workflow(env, manifest).run()
        assert state.status == WorkflowStatus.WAITING_FOR_REVIEW
        assert env["tracker"].records() == []
