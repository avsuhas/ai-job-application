"""Unit tests for automatic-mode limits, kill switch, and the eligibility
policy engine (docs/17 Phase 12)."""

from datetime import date, timedelta

import pytest

from job_platform.ats.base import AdapterStatus
from job_platform.ats.greenhouse import GreenhouseAdapter
from job_platform.candidate.loader import load_candidate_bundle
from job_platform.orchestration.automatic import (
    KillSwitch,
    check_limits,
    compute_metrics,
)
from job_platform.orchestration.eligibility import (
    AutomaticDecision,
    AutomaticEligibility,
)
from job_platform.packages.store import PackageStore
from job_platform.preparation.service import PreparationService
from job_platform.providers.mock import MockReasoningProvider
from job_platform.readiness.models import ReadinessStatus
from job_platform.review.models import ReviewStatus
from job_platform.shared.config import AutomaticModeSettings, Settings
from job_platform.storage.tracker import ApplicationRecord, ApplicationTracker
from job_platform.submission.history import HistoryEvent
from tests.unit.test_review import make_ranked

TODAY = date(2026, 7, 13)


class StableGreenhouse(GreenhouseAdapter):
    """A Stable variant for exercising the automatic path (the real adapter
    stays Beta until it earns Stable)."""

    _metadata = GreenhouseAdapter._metadata.model_copy(
        update={"status": AdapterStatus.STABLE}
    )


class TestKillSwitch:
    def test_engage_and_release(self, tmp_path):
        ks = KillSwitch(tmp_path)
        assert not ks.engaged
        ks.engage("safety incident")
        assert ks.engaged
        assert ks.reason() == "safety incident"
        ks.release()
        assert not ks.engaged


class TestLimits:
    def _tracker(self, tmp_path, submitted):
        tracker = ApplicationTracker(tmp_path / "tracker.csv")
        for i, (company, when) in enumerate(submitted):
            tracker.add(ApplicationRecord(
                company=company, job_title=f"Role {i}", job_id=str(i),
                application_url=f"https://x/{i}", status="submitted",
                date_applied=when.isoformat(),
            ))
        return tracker

    def test_daily_limit_counts_today_only(self, tmp_path):
        yesterday = TODAY - timedelta(days=1)
        tracker = self._tracker(tmp_path, [
            ("A", TODAY), ("B", TODAY), ("C", yesterday),
        ])
        limits = check_limits(tracker, "D", daily_limit=3, per_company_limit=2, today=TODAY)
        assert limits.daily_used == 2
        assert not limits.daily_exceeded

    def test_per_company_limit(self, tmp_path):
        tracker = self._tracker(tmp_path, [("A", TODAY), ("A", TODAY)])
        limits = check_limits(tracker, "A", daily_limit=10, per_company_limit=2, today=TODAY)
        assert limits.company_used == 2
        assert limits.company_exceeded


class TestMetrics:
    def test_rolls_up_event_types(self):
        events = [
            HistoryEvent(event_type="auto_submitted"),
            HistoryEvent(event_type="auto_submitted"),
            HistoryEvent(event_type="auto_downgraded"),
            HistoryEvent(event_type="auto_blocked"),
            HistoryEvent(event_type="submitted"),  # ignored
        ]
        metrics = compute_metrics(events)
        assert metrics.auto_submitted == 2
        assert metrics.downgraded_to_review == 1
        assert metrics.blocked == 1


@pytest.fixture
async def eligibility_env(candidate_dir, tmp_path):
    bundle = load_candidate_bundle(candidate_dir)
    store = PackageStore(tmp_path / "packages")
    tracker = ApplicationTracker(tmp_path / "tracker.csv")
    prep = PreparationService(MockReasoningProvider(), store, Settings(), tracker=tracker)
    manifest = await prep.prepare(make_ranked(company="ExampleCo"), bundle)
    kill = KillSwitch(tmp_path)
    return bundle, store, tracker, manifest, kill


def enabled_settings(**overrides) -> AutomaticModeSettings:
    base = dict(enabled=True, adapter_allowlist=["greenhouse"],
                company_allowlist=["ExampleCo"], daily_limit=10,
                per_company_daily_limit=3, max_warnings=0,
                final_control_min_confidence=90)
    base.update(overrides)
    return AutomaticModeSettings(**base)


def evaluate(env, settings, adapter=None, review=ReviewStatus.APPROVED,
             warnings=0, readiness=ReadinessStatus.READY, confidence=98):
    bundle, store, tracker, manifest, kill = env
    engine = AutomaticEligibility(settings, store, tracker, kill)
    return engine.evaluate(
        manifest, bundle, adapter if adapter is not None else StableGreenhouse(),
        review, warnings, readiness, confidence, today=TODAY,
    )


class TestEligibilityPolicy:
    async def test_all_preconditions_met_is_automatic(self, eligibility_env):
        result = evaluate(eligibility_env, enabled_settings())
        assert result.decision == AutomaticDecision.AUTOMATIC
        assert result.automatic
        assert result.reasons == []

    async def test_disabled_by_default_downgrades(self, eligibility_env):
        result = evaluate(eligibility_env, AutomaticModeSettings())  # enabled=False
        assert not result.automatic
        assert any("not enabled" in r for r in result.reasons)

    async def test_kill_switch_blocks(self, eligibility_env):
        eligibility_env[4].engage("incident")
        result = evaluate(eligibility_env, enabled_settings())
        assert not result.automatic
        assert any("kill switch" in r for r in result.reasons)

    async def test_beta_adapter_refused(self, eligibility_env):
        result = evaluate(eligibility_env, enabled_settings(), adapter=GreenhouseAdapter())
        assert not result.automatic
        assert any("not stable" in r for r in result.reasons)

    async def test_generic_fallback_refused(self, eligibility_env):
        # adapter=None means no dedicated adapter matched
        bundle, store, tracker, manifest, kill = eligibility_env
        engine = AutomaticEligibility(enabled_settings(), store, tracker, kill)
        result = engine.evaluate(
            manifest, bundle, None, ReviewStatus.APPROVED, 0,
            ReadinessStatus.READY, 98, today=TODAY,
        )
        assert not result.automatic
        assert any("generic fallback" in r for r in result.reasons)

    async def test_non_allowlisted_adapter_refused(self, eligibility_env):
        result = evaluate(eligibility_env, enabled_settings(adapter_allowlist=["workday"]))
        assert not result.automatic
        assert any("not allowlisted" in r for r in result.reasons)

    async def test_non_allowlisted_company_refused(self, eligibility_env):
        result = evaluate(eligibility_env, enabled_settings(company_allowlist=["OtherCo"]))
        assert not result.automatic
        assert any("Company" in r for r in result.reasons)

    async def test_review_warnings_over_policy_downgrade(self, eligibility_env):
        result = evaluate(
            eligibility_env, enabled_settings(max_warnings=0),
            review=ReviewStatus.APPROVED_WITH_WARNINGS, warnings=2,
        )
        assert not result.automatic
        assert any("warning" in r for r in result.reasons)

    async def test_blocked_review_downgrades(self, eligibility_env):
        result = evaluate(eligibility_env, enabled_settings(), review=ReviewStatus.BLOCKED)
        assert not result.automatic

    async def test_not_ready_downgrades(self, eligibility_env):
        result = evaluate(
            eligibility_env, enabled_settings(), readiness=ReadinessStatus.NOT_READY
        )
        assert not result.automatic
        assert any("Readiness" in r for r in result.reasons)

    async def test_low_final_control_confidence_downgrades(self, eligibility_env):
        result = evaluate(eligibility_env, enabled_settings(), confidence=70)
        assert not result.automatic
        assert any("confidence" in r for r in result.reasons)

    async def test_stale_package_downgrades(self, eligibility_env, candidate_dir):
        bundle, store, tracker, manifest, kill = eligibility_env
        (candidate_dir / "profile" / "rules.md").write_text("changed after prep")
        updated = load_candidate_bundle(candidate_dir)
        engine = AutomaticEligibility(enabled_settings(), store, tracker, kill)
        result = engine.evaluate(
            manifest, updated, StableGreenhouse(), ReviewStatus.APPROVED, 0,
            ReadinessStatus.READY, 98, today=TODAY,
        )
        assert not result.automatic
        assert any("stale" in r for r in result.reasons)

    async def test_duplicate_downgrades(self, eligibility_env):
        bundle, store, tracker, manifest, kill = eligibility_env
        tracker.add(ApplicationRecord.from_job(make_ranked(company="ExampleCo").job))
        result = evaluate(eligibility_env, enabled_settings())
        assert not result.automatic
        assert any("duplicate" in r.lower() for r in result.reasons)

    async def test_daily_limit_downgrades(self, eligibility_env):
        bundle, store, tracker, manifest, kill = eligibility_env
        for i in range(10):
            tracker.add(ApplicationRecord(
                company=f"Co{i}", job_title=f"R{i}", job_id=str(i),
                application_url=f"https://x/{i}", status="submitted",
                date_applied=TODAY.isoformat(),
            ))
        result = evaluate(eligibility_env, enabled_settings(daily_limit=10))
        assert not result.automatic
        assert any("Daily automatic limit" in r for r in result.reasons)
