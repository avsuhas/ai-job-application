"""Lever adapter browser regression suite against local fixtures (docs/17
Phase 13 Expansion Rule: form + submission + live-non-submission tests run
independently for the new adapter). Real headless Chromium."""

from job_platform.ats.greenhouse import default_registry
from job_platform.ats.lever import LeverAdapter
from job_platform.forms.engine import EngineStatus, GenericFormEngine
from job_platform.forms.mapper import PlanEntryStatus
from job_platform.preparation.answers import PreparedAnswer, PreparedAnswerSet
from job_platform.providers.mock import MockReasoningProvider
from tests.browser.conftest import page_url
from tests.browser.test_form_engine import RESUME_PATH


def answer(family: str, value: str) -> PreparedAnswer:
    return PreparedAnswer(
        answer_id=family.replace(".", "_"), question_family=family,
        canonical_question=family, answer=value,
        source=f"candidate.json:{family}", confidence=100,
    )


ANSWERS = PreparedAnswerSet(answers=[
    answer("personal.first_name", "Alex"),
    answer("personal.last_name", "Sample"),
    answer("personal.email", "alex@example.com"),
    answer("personal.phone", "+1-555-0100"),
    answer("employment.current_company", "ExampleCorp"),
])


def make_engine(session) -> GenericFormEngine:
    return GenericFormEngine(
        session, MockReasoningProvider(), ANSWERS,
        documents={"documents.resume": RESUME_PATH},
        adapter=LeverAdapter(),
    )


class TestDetectionOnFixture:
    async def test_registry_resolves_lever_from_signature(self, session):
        snapshot = await session.open_page(page_url("lever_application.html"))
        resolution = default_registry().resolve(snapshot.url, snapshot)
        assert resolution.adapter_id == "lever"
        assert "page_signature" in resolution.detection.detection_methods

    async def test_job_identity(self, session):
        # file:// URL can't carry the lever.co posting pattern, so identity
        # comes from the "Company - Title" page title.
        snapshot = await session.open_page(page_url("lever_application.html"))
        identity = LeverAdapter().extract_job_identity(snapshot)
        assert identity.company == "OtherCorp"
        assert identity.title == "Backend Engineer"


class TestReviewModeRun:
    async def test_fills_lever_form_and_stops_before_submit(self, session):
        snapshot = await session.open_page(page_url("lever_application.html"))
        report = await make_engine(session).run_review_mode(snapshot)

        assert report.adapter_id == "lever"
        assert report.status == EngineStatus.STOPPED_BEFORE_SUBMIT
        page = report.pages[0]
        assert page.page_type == "application_form"
        assert page.submission_control == "btn-submit"

        by_field = {e.field_id: e for e in page.entries}
        # Lever's single full-name field computed from first + last
        assert by_field["name"].status == PlanEntryStatus.PLANNED
        assert by_field["email"].status == PlanEntryStatus.PLANNED
        assert by_field["org"].status == PlanEntryStatus.PLANNED
        for e in page.entries:
            if e.field_id in ("name", "email", "org", "resume", "urls[LinkedIn]"):
                assert e.classification_method == "ats_known_field_id"
        # Custom card has no stored answer -> surfaced, not guessed
        assert by_field["cards[abc][0]"].status in (
            PlanEntryStatus.UNKNOWN_FIELD, PlanEntryStatus.NO_STORED_ANSWER,
        )

        refreshed = await session.inspect_page()
        assert refreshed.field("name").current_value == "Alex Sample"
        assert refreshed.field("resume").current_value == "Backend.txt"
        # Never submitted
        assert refreshed.heading == "Backend Engineer"

    async def test_confirmation_page_detected(self, session):
        snapshot = await session.open_page(page_url("lever_confirmation.html"))
        report = await make_engine(session).run_review_mode(snapshot)
        assert report.status == EngineStatus.CONFIRMATION_DETECTED
        assert report.confirmation["confirmed"] is True
        assert report.pages == []
