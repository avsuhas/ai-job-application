"""Generic Form Engine browser tests against local fixtures (docs/17 Phase 6
acceptance criteria)."""

from job_platform.forms.engine import EngineStatus, GenericFormEngine, is_review_page
from job_platform.forms.mapper import PlanEntryStatus
from job_platform.preparation.answers import PreparedAnswer, PreparedAnswerSet
from job_platform.providers.mock import MockReasoningProvider
from tests.browser.conftest import TEST_SITES, page_url


def answer(family: str, value: str) -> PreparedAnswer:
    return PreparedAnswer(
        answer_id=family.replace(".", "_"), question_family=family,
        canonical_question=family, answer=value,
        source=f"candidate.json:{family}", confidence=100,
    )


ANSWERS = PreparedAnswerSet(
    answers=[
        answer("personal.first_name", "Alex"),
        answer("personal.last_name", "Sample"),
        answer("personal.email", "alex@example.com"),
        answer("work_authorization.authorized_now", "Yes"),
        answer("work_authorization.sponsorship_now", "Yes"),
        answer("work_authorization.visa_status", "H1B"),
        answer("employment.years_of_experience", "8"),
    ]
)

RESUME_PATH = str(TEST_SITES.parent / "fixtures" / "candidate" / "resume" / "Backend.txt")


def make_engine(session, answers=ANSWERS, **kw) -> GenericFormEngine:
    return GenericFormEngine(
        session,
        MockReasoningProvider(),
        answers,
        documents={"documents.resume": RESUME_PATH},
        **kw,
    )


class TestApplicationFormSelection:
    async def test_engine_fills_application_form_and_ignores_others(self, session):
        snapshot = await session.open_page(page_url("job_page_multi_form.html"))
        engine = make_engine(session)
        report = await engine.run_review_mode(snapshot)

        # Progressed from the application page to the review page fixture
        assert report.status == EngineStatus.READY_FOR_REVIEW
        assert report.screenshot is not None
        page = report.pages[0]
        planned = {e.field_id: e for e in page.entries}

        # Application fields planned; search/newsletter fields never touched
        assert planned["first_name"].status == PlanEntryStatus.PLANNED
        assert planned["email"].status == PlanEntryStatus.PLANNED
        assert planned["resume"].status == PlanEntryStatus.PLANNED
        assert planned["authorized"].status == PlanEntryStatus.PLANNED
        assert "q" not in planned
        assert "nl_email" not in planned

        # Ambiguous custom question surfaced instead of guessed
        assert planned["favorite_color"].status == PlanEntryStatus.UNKNOWN_FIELD
        assert any(
            e.field_id == "favorite_color" for e in report.fields_needing_user
        )

        # Every executed action verified
        assert all(r.verified for r in page.action_results)

    async def test_search_only_page_reports_no_application_form(self, session, tmp_path):
        (tmp_path / "search_only.html").write_text(
            '<html><body><h1>Job Search</h1><form id="s">'
            '<label for="q">Search jobs</label><input id="q" name="q">'
            "</form>"
            '<form id="n"><label for="e">Email</label>'
            '<input id="e" placeholder="Subscribe to our newsletter"></form>'
            "</body></html>"
        )
        snapshot = await session.open_page((tmp_path / "search_only.html").as_uri())
        report = await make_engine(session).run_review_mode(snapshot)
        assert report.status == EngineStatus.NO_APPLICATION_FORM


class TestFinalActionProtection:
    async def test_submit_only_page_stops_before_submit(self, session):
        snapshot = await session.open_page(page_url("submit_only.html"))
        report = await make_engine(session).run_review_mode(snapshot)
        assert report.status == EngineStatus.STOPPED_BEFORE_SUBMIT
        # The email was filled, but the submit control was never clicked
        assert report.pages[0].action_results
        refreshed = await session.inspect_page()
        assert refreshed.heading == "Final Step"  # page unchanged

    async def test_review_fixture_detected_without_submitting(self, session):
        snapshot = await session.open_page(page_url("multi_page_review.html"))
        assert is_review_page(snapshot)
        report = await make_engine(session).run_review_mode(snapshot)
        assert report.status == EngineStatus.READY_FOR_REVIEW
        assert report.pages == []  # nothing was filled or clicked


class TestDynamicFields:
    async def test_conditional_field_filled_in_dynamic_round(self, session):
        snapshot = await session.open_page(page_url("conditional_fields.html"))
        report = await make_engine(session).run_review_mode(snapshot)

        page = report.pages[0]
        assert page.dynamic_rounds >= 1
        by_field = {e.field_id: e for e in page.entries}
        # Radio filled first; visa_type appeared afterwards and was filled too
        assert by_field["sponsorship"].status in (
            PlanEntryStatus.PLANNED, PlanEntryStatus.NEEDS_REVIEW
        )
        assert "visa_type" in by_field
        refreshed = await session.inspect_page()
        assert refreshed.field("visa_type").current_value == "H1B"


class TestMultiPageFlow:
    async def test_multi_page_run_ends_at_review_page(self, session):
        snapshot = await session.open_page(page_url("multi_page_1.html"))
        report = await make_engine(session).run_review_mode(snapshot)

        assert report.status == EngineStatus.READY_FOR_REVIEW
        assert len(report.pages) == 2
        assert report.pages[0].heading.startswith("Step 1")
        assert report.pages[1].heading.startswith("Step 2")
        # Full name computed from first + last on page 1
        page1 = {e.field_id: e for e in report.pages[0].entries}
        assert page1["full_name"].answer_source.startswith("computed:")

    async def test_validation_errors_recorded_when_page_refuses_to_progress(
        self, session
    ):
        snapshot = await session.open_page(page_url("validation_errors.html"))
        empty_answers = PreparedAnswerSet(answers=[])
        report = await make_engine(session, answers=empty_answers).run_review_mode(snapshot)
        assert report.status == EngineStatus.STOPPED_NO_PROGRESSION
        assert any(
            "Email address is required" in e for e in report.pages[0].validation_errors
        )


class TestSafetyPauses:
    async def test_engine_pauses_on_captcha(self, session):
        snapshot = await session.open_page(page_url("captcha.html"))
        report = await make_engine(session).run_review_mode(snapshot)
        assert report.status == EngineStatus.PAUSED_CAPTCHA
        assert report.screenshot is not None
        assert report.pages == []
