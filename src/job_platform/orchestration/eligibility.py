"""Automatic-mode eligibility policy engine (docs/17 Phase 12).

A package qualifies for automatic submission only when every precondition
holds. The default posture is denial: any missing signal, any warning beyond
policy, any non-Stable adapter, or the kill switch denies automatic mode and
falls back to Review. This engine is pure/deterministic so it is fully
unit-testable without a browser.
"""

from __future__ import annotations

from datetime import date
from enum import StrEnum

from pydantic import BaseModel, Field

from job_platform.ats.base import AdapterStatus, ATSAdapter
from job_platform.candidate.models import CandidateBundle
from job_platform.orchestration.automatic import KillSwitch, check_limits
from job_platform.packages.models import PackageManifest, PackageStatus
from job_platform.packages.store import PackageStore
from job_platform.readiness.models import ReadinessStatus
from job_platform.review.models import ReviewStatus
from job_platform.shared.config import AutomaticModeSettings
from job_platform.storage.tracker import ApplicationTracker


class AutomaticDecision(StrEnum):
    AUTOMATIC = "automatic"
    DOWNGRADE_TO_REVIEW = "downgrade_to_review"


class EligibilityResult(BaseModel):
    """Whether a package may submit automatically, and why not if it may not."""

    package_id: str
    decision: AutomaticDecision
    reasons: list[str] = Field(default_factory=list)

    @property
    def automatic(self) -> bool:
        return self.decision == AutomaticDecision.AUTOMATIC


class AutomaticEligibility:
    def __init__(
        self,
        settings: AutomaticModeSettings,
        store: PackageStore,
        tracker: ApplicationTracker,
        kill_switch: KillSwitch,
    ) -> None:
        self._settings = settings
        self._store = store
        self._tracker = tracker
        self._kill_switch = kill_switch

    def quick_gate(self, manifest: PackageManifest) -> EligibilityResult:
        """Cheap pre-browser gate: enabled + kill switch. Lets an automatic
        run fail (downgrade) before launching a browser."""
        reasons: list[str] = []
        if not self._settings.enabled:
            reasons.append("Automatic mode is not enabled.")
        if self._kill_switch.engaged:
            reasons.append(
                "The automatic-mode kill switch is engaged"
                + (f": {self._kill_switch.reason()}" if self._kill_switch.reason() else ".")
            )
        return EligibilityResult(
            package_id=manifest.package_id,
            decision=AutomaticDecision.AUTOMATIC if not reasons
            else AutomaticDecision.DOWNGRADE_TO_REVIEW,
            reasons=reasons,
        )

    def evaluate(
        self,
        manifest: PackageManifest,
        bundle: CandidateBundle,
        adapter: ATSAdapter | None,
        review: ReviewStatus,
        review_warning_count: int,
        readiness: ReadinessStatus,
        final_control_confidence: int | None,
        today: date | None = None,
    ) -> EligibilityResult:
        reasons: list[str] = []

        # 1. User must have explicitly enabled automatic mode.
        if not self._settings.enabled:
            reasons.append("Automatic mode is not enabled.")
        # 2. Kill switch overrides everything.
        if self._kill_switch.engaged:
            reasons.append(
                "The automatic-mode kill switch is engaged"
                + (f": {self._kill_switch.reason()}" if self._kill_switch.reason() else ".")
            )
        # 3. A dedicated, Stable, allowlisted adapter is required.
        if adapter is None:
            reasons.append("No dedicated ATS adapter matched (generic fallback).")
        else:
            meta = adapter.metadata
            if meta.status != AdapterStatus.STABLE:
                reasons.append(
                    f"Adapter '{meta.adapter_id}' is '{meta.status.value}', not stable."
                )
            if (
                self._settings.adapter_allowlist
                and meta.adapter_id not in self._settings.adapter_allowlist
            ):
                reasons.append(f"Adapter '{meta.adapter_id}' is not allowlisted.")
        # 4. Company allowlist (when configured).
        if (
            self._settings.company_allowlist
            and manifest.job.company not in self._settings.company_allowlist
        ):
            reasons.append(f"Company '{manifest.job.company}' is not allowlisted.")
        # 5. Package must be ready and reviewed clean.
        if manifest.status != PackageStatus.READY:
            reasons.append(f"Package status is '{manifest.status.value}', not ready.")
        if manifest.blocking_attention_items:
            reasons.append("The package has blocking attention items.")
        if review not in (ReviewStatus.APPROVED, ReviewStatus.APPROVED_WITH_WARNINGS):
            reasons.append(f"Review status is '{review.value}'.")
        if review_warning_count > self._settings.max_warnings:
            reasons.append(
                f"Review has {review_warning_count} warning(s); policy permits "
                f"at most {self._settings.max_warnings}."
            )
        # 6. Readiness must be Ready (warnings only allowed if policy has slack).
        if readiness == ReadinessStatus.READY:
            pass
        elif (
            readiness == ReadinessStatus.READY_WITH_WARNINGS
            and self._settings.max_warnings > 0
        ):
            pass
        else:
            reasons.append(f"Readiness is '{readiness.value}', not ready.")
        # 7. Candidate data must be current (package not stale).
        if self._store.stale_sources(manifest, bundle):
            reasons.append("Candidate data changed since preparation (stale package).")
        # 8. Duplicate check must be current.
        from job_platform.jobs.models import Job

        probe = Job(
            id="auto_check",
            company=manifest.job.company,
            title=manifest.job.title,
            job_id=manifest.job.job_id,
            url=manifest.job.application_url,
        )
        if self._tracker.is_duplicate(probe):
            reasons.append("A duplicate application already exists.")
        # 9. Final control confidence must exceed the threshold.
        if (
            final_control_confidence is not None
            and final_control_confidence < self._settings.final_control_min_confidence
        ):
            reasons.append(
                f"Final-control confidence {final_control_confidence} is below the "
                f"threshold {self._settings.final_control_min_confidence}."
            )
        # 10. Daily and per-company limits.
        limits = check_limits(
            self._tracker,
            manifest.job.company,
            self._settings.daily_limit,
            self._settings.per_company_daily_limit,
            today=today,
        )
        if limits.daily_exceeded:
            reasons.append(
                f"Daily automatic limit reached ({limits.daily_used}/{limits.daily_limit})."
            )
        if limits.company_exceeded:
            reasons.append(
                f"Per-company daily limit reached for {manifest.job.company} "
                f"({limits.company_used}/{limits.per_company_limit})."
            )

        decision = (
            AutomaticDecision.AUTOMATIC if not reasons
            else AutomaticDecision.DOWNGRADE_TO_REVIEW
        )
        return EligibilityResult(
            package_id=manifest.package_id, decision=decision, reasons=reasons
        )
