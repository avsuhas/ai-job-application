"""Tests for system health and sanitized diagnostics (docs/17 Phase 11)."""

import json

from job_platform.operations.health import diagnostic_bundle, system_health
from job_platform.shared.config import Settings
from job_platform.storage.tracker import ApplicationTracker
from job_platform.submission.history import ApplicationHistoryService


def make_settings(tmp_path, api_key=""):
    settings = Settings(
        anthropic_api_key=api_key, paths={"data_root": tmp_path / "user_data"}
    )
    settings.paths.profile_dir.mkdir(parents=True, exist_ok=True)
    (settings.paths.profile_dir / "candidate.json").write_text(
        '{"personal": {"first_name": "Alex", "email": "a@example.com"},'
        ' "work_authorization": {"authorized_to_work": true}}'
    )
    (settings.paths.resume_dir).mkdir(parents=True, exist_ok=True)
    (settings.paths.resume_dir / "Backend.txt").write_text("Engineer resume")
    settings.paths.packages_dir.mkdir(parents=True, exist_ok=True)
    return settings


class TestSystemHealth:
    def test_healthy_system(self, tmp_path):
        settings = make_settings(tmp_path)
        health = system_health(settings, "mock")
        assert health.healthy
        names = {c.name for c in health.components}
        assert {"disk", "candidate_data", "audit_trail", "reasoning_provider"} <= names

    def test_degraded_component_makes_system_unhealthy(self, tmp_path):
        settings = make_settings(tmp_path)
        # Corrupt the audit chain
        events = settings.paths.applications_dir / "history_events.jsonl"
        events.parent.mkdir(parents=True, exist_ok=True)
        events.write_text("not a valid event\n")
        health = system_health(settings, "mock")
        assert not health.healthy
        audit = next(c for c in health.components if c.name == "audit_trail")
        assert audit.state == "error"


class TestDiagnostics:
    def test_bundle_contains_no_secrets_or_candidate_values(self, tmp_path):
        settings = make_settings(tmp_path, api_key="sk-ant-supersecret1234567890")
        tracker = ApplicationTracker(settings.paths.tracker_path)
        tracker.initialize()
        history = ApplicationHistoryService(
            tracker, settings.paths.applications_dir / "history_events.jsonl"
        )
        history.record_event("submitted", package_id="p1")

        bundle = diagnostic_bundle(settings, "mock")
        text = json.dumps(bundle)

        # No secret material
        assert "supersecret" not in text
        assert "sk-ant-" not in text
        assert bundle["anthropic_api_key_configured"] is True
        # No candidate PII
        assert "Alex" not in text
        assert "a@example.com" not in text
        # Useful non-sensitive facts present
        assert bundle["version"]
        assert "counts" in bundle
        assert bundle["health"]["components"]

    def test_bundle_reports_package_and_record_counts(self, tmp_path):
        settings = make_settings(tmp_path)
        tracker = ApplicationTracker(settings.paths.tracker_path)
        tracker.initialize()
        bundle = diagnostic_bundle(settings, "mock")
        assert bundle["counts"]["packages"] == 0
        assert bundle["counts"]["tracker_records"] == 0
