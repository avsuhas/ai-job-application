"""Aggregated system health and sanitized diagnostics (docs/17 Phase 11).

System health rolls up component checks so degraded parts are identifiable.
The diagnostic bundle is a support artifact that must contain no secrets and
no candidate values — only counts, versions, and component states.
"""

from __future__ import annotations

from datetime import UTC, datetime

from pydantic import BaseModel, Field

from job_platform.candidate.validator import validate_candidate_dir
from job_platform.operations.audit import verify_event_log
from job_platform.operations.disk import check_disk
from job_platform.packages.store import PackageStore
from job_platform.security.redaction import redact
from job_platform.shared.config import Settings
from job_platform.storage.tracker import ApplicationTracker
from job_platform.version import __version__


class ComponentHealth(BaseModel):
    name: str
    state: str  # ok | degraded | error | not_applicable
    detail: str = ""


class SystemHealth(BaseModel):
    healthy: bool
    version: str = __version__
    components: list[ComponentHealth] = Field(default_factory=list)
    checked_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


def system_health(settings: Settings, provider_name: str) -> SystemHealth:
    components: list[ComponentHealth] = []

    disk = check_disk(settings.paths.data_root)
    components.append(
        ComponentHealth(
            name="disk",
            state="ok" if disk.safe_to_write else "degraded",
            detail=f"{disk.free_bytes // (1024 * 1024)} MB free",
        )
    )

    report = validate_candidate_dir(settings.paths.candidate_dir)
    components.append(
        ComponentHealth(
            name="candidate_data",
            state="ok" if report.ok else "error",
            detail=f"{len(report.errors)} error(s), {len(report.warnings)} warning(s)",
        )
    )

    audit = verify_event_log(
        settings.paths.applications_dir / "history_events.jsonl",
        store=PackageStore(settings.paths.packages_dir),
    )
    components.append(
        ComponentHealth(
            name="audit_trail",
            state="ok" if audit.ok else "error",
            detail=f"{audit.events_checked} event(s), chain_valid={audit.chain_valid}",
        )
    )

    components.append(
        ComponentHealth(name="reasoning_provider", state="ok", detail=provider_name)
    )

    healthy = all(c.state in ("ok", "not_applicable") for c in components)
    return SystemHealth(healthy=healthy, components=components)


def diagnostic_bundle(settings: Settings, provider_name: str) -> dict:
    """A sanitized snapshot for support. Contains only counts, versions, and
    component states — never candidate values or secrets."""
    tracker = ApplicationTracker(settings.paths.tracker_path)
    health = system_health(settings, provider_name)
    package_store = PackageStore(settings.paths.packages_dir)
    bundle = {
        "version": __version__,
        "app_env": settings.app_env,
        "provider": provider_name,
        "automation_mode": settings.applications.automation_mode,
        "counts": {
            "packages": len(package_store.list_package_ids()),
            "tracker_records": len(tracker.records()),
        },
        "health": health.model_dump(mode="json"),
        # Presence of an API key, never the key itself.
        "anthropic_api_key_configured": bool(settings.anthropic_api_key),
    }

    # Defense in depth: run the whole bundle through redaction so no secret
    # can slip through even if a future field is added carelessly.
    import json

    return json.loads(redact(json.dumps(bundle)))
