"""Greenhouse adapter regression suite against local fixtures (docs/17
Phase 7 acceptance criteria). Runs real headless Chromium."""

from job_platform.ats.greenhouse import GreenhouseAdapter, default_registry
from job_platform.forms.engine import EngineStatus, GenericFormEngine
from job_platform.forms.mapper import PlanEntryStatus
from job_platform.providers.mock import MockReasoningProvider
from tests.browser.conftest import page_url
from tests.browser.test_form_engine import ANSWERS, RESUME_PATH


def make_engine(session, adapter=None) -> GenericFormEngine:
    return GenericFormEngine(
        session,
        MockReasoningProvider(),
        ANSWERS,
        documents={"documents.resume": RESUME_PATH},
        adapter=adapter or GreenhouseAdapter(),
    )


class TestDetectionOnFixture:
    async def test_registry_resolves_greenhouse_from_page_signature(self, session):
        # file:// URL means no domain signal — signature must carry detection
        snapshot = await session.open_page(page_url("greenhouse_application.html"))
        resolution = default_registry().resolve(snapshot.url, snapshot)
        assert resolution.adapter_id == "greenhouse"
        assert "page_signature" in resolution.detection.detection_methods

    async def test_job_identity_extracted(self, session):
        snapshot = await session.open_page(page_url("greenhouse_application.html"))
        identity = GreenhouseAdapter().extract_job_identity(snapshot)
        assert identity.company == "ExampleCo"
        assert identity.title == "Backend Engineer"


class TestReviewModeRun:
    async def test_full_review_mode_run_stops_before_submit(self, session):
        snapshot = await session.open_page(page_url("greenhouse_application.html"))
        report = await make_engine(session).run_review_mode(snapshot)

        assert report.adapter_id == "greenhouse"
        assert report.status == EngineStatus.STOPPED_BEFORE_SUBMIT
        page = report.pages[0]
        assert page.page_type == "application_form"
        assert page.submission_control == "submit_app"

        by_field = {e.field_id: e for e in page.entries}
        # Standard Greenhouse ids filled through the adapter mapping
        for field_id in ("first_name", "last_name", "email", "phone"):
            assert by_field[field_id].status == PlanEntryStatus.PLANNED
            assert by_field[field_id].classification_method == "ats_known_field_id"
        # Resume uploaded; custom question surfaced; demographic skipped
        assert by_field["resume"].status == PlanEntryStatus.PLANNED
        assert (
            by_field["job_application_answers_attributes_0_text_value"].status
            == PlanEntryStatus.UNKNOWN_FIELD
        )
        assert by_field["gender"].status == PlanEntryStatus.SENSITIVE_SKIPPED
        assert by_field["authorized"].status == PlanEntryStatus.PLANNED

        # Values actually landed
        refreshed = await session.inspect_page()
        assert refreshed.field("first_name").current_value == "Alex"
        assert refreshed.field("resume").current_value == "Backend.txt"
        assert refreshed.field("gender").current_value == "Please select"  # untouched
        # Page not submitted
        assert refreshed.heading == "Backend Engineer"

    async def test_simulated_submission_verification(self, session):
        snapshot = await session.open_page(page_url("greenhouse_confirmation.html"))
        report = await make_engine(session).run_review_mode(snapshot)
        assert report.status == EngineStatus.CONFIRMATION_DETECTED
        assert report.confirmation["confirmed"] is True
        assert report.screenshot is not None
        assert report.pages == []  # nothing filled on a confirmation page

    async def test_confirmation_verifier_rejects_application_page(self, session):
        snapshot = await session.open_page(page_url("greenhouse_application.html"))
        result = GreenhouseAdapter().verify_confirmation(snapshot)
        assert not result.confirmed


class TestGenericFallback:
    async def test_non_greenhouse_page_still_works_via_generic_engine(self, session):
        # Unsupported variant: registry finds nothing, engine runs without adapter
        snapshot = await session.open_page(page_url("job_page_multi_form.html"))
        resolution = default_registry().resolve(snapshot.url, snapshot)
        assert resolution.adapter_id is None
        engine = GenericFormEngine(
            session, MockReasoningProvider(), ANSWERS,
            documents={"documents.resume": RESUME_PATH},
        )
        report = await engine.run_review_mode(snapshot)
        assert report.adapter_id is None
        assert report.status == EngineStatus.READY_FOR_REVIEW
