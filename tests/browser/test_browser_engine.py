"""Browser engine tests against local synthetic forms (docs/17 Phase 5
acceptance criteria). These launch real headless Chromium."""

import logging
from pathlib import Path

import pytest

from job_platform.browser.models import (
    ActionStatus,
    BrowserAction,
    ExecutionState,
    FieldType,
    InteractionPlan,
    InteractionStep,
    PageState,
)
from job_platform.browser.navigation import NavigationPolicy
from job_platform.browser.service import (
    BrowserSession,
    check_browser_health,
    snapshot_requires_pause,
)
from job_platform.shared.config import BrowserSettings
from job_platform.shared.errors import BrowserError, NavigationBlockedError
from tests.browser.conftest import TEST_SITES, page_url


def step(n: int, field: str, action: BrowserAction, value: str) -> InteractionStep:
    return InteractionStep(step_id=f"step_{n}", field_id=field, action=action, value=value)


ONE_PAGE_PLAN = InteractionPlan(
    page_id="one_page",
    steps=[
        step(1, "first_name", BrowserAction.FILL, "Alex"),
        step(2, "last_name", BrowserAction.FILL, "Sample"),
        step(3, "email", BrowserAction.FILL, "alex.sample@example.com"),
        step(4, "phone", BrowserAction.FILL, "+1-555-0100"),
        step(5, "country", BrowserAction.SELECT_OPTION, "United States"),
        step(6, "authorized", BrowserAction.SELECT_RADIO, "Yes"),
        step(7, "relocate", BrowserAction.SET_CHECKBOX, "true"),
        step(8, "why_company", BrowserAction.FILL, "I enjoy distributed systems."),
    ],
)


class TestHealthAndLaunch:
    async def test_health_check_passes(self, tmp_path, chromium_available):
        health = await check_browser_health(tmp_path / "p", tmp_path / "s")
        assert health.healthy
        assert health.chromium_installed
        assert health.problems == []

    async def test_browser_launches_and_profile_persists(self, tmp_path, chromium_available):
        policy = NavigationPolicy.for_application(
            "https://careers.example.com/jobs/1", allow_local_files=True
        )
        settings = BrowserSettings(headless=True, default_timeout_ms=10_000)
        profile = tmp_path / "profile"

        first = BrowserSession(profile, tmp_path / "s", policy, settings)
        await first.start()
        await first.open_page(page_url("one_page_form.html"))
        await first.page.evaluate("() => localStorage.setItem('probe', 'persisted')")
        await first.close()

        second = BrowserSession(profile, tmp_path / "s", policy, settings)
        await second.start()
        await second.open_page(page_url("one_page_form.html"))
        value = await second.page.evaluate("() => localStorage.getItem('probe')")
        await second.close()
        assert value == "persisted"


class TestFormExtraction:
    async def test_fields_extracted_with_labels_and_types(self, session):
        snapshot = await session.open_page(page_url("one_page_form.html"))
        assert snapshot.state == PageState.READY

        first_name = snapshot.field("first_name")
        assert first_name.label == "First Name"
        assert first_name.field_type == FieldType.TEXT
        assert first_name.required

        assert snapshot.field("email").field_type == FieldType.EMAIL
        assert snapshot.field("phone").field_type == FieldType.PHONE

        country = snapshot.field("country")
        assert country.field_type == FieldType.SELECT
        assert "United States" in country.options

        authorized = snapshot.field("authorized")
        assert authorized.field_type == FieldType.RADIO
        assert authorized.options == ["Yes", "No"]
        assert "authorized to work" in authorized.section.lower()

        assert snapshot.field("relocate").field_type == FieldType.CHECKBOX
        assert snapshot.field("why_company").field_type == FieldType.TEXTAREA

        next_actions = [a for a in snapshot.actions if a.type == "next"]
        assert next_actions and next_actions[0].label == "Save and Continue"


class TestVerifiedActions:
    async def test_full_form_completed_with_every_action_verified(self, session):
        snapshot = await session.open_page(page_url("one_page_form.html"))
        results = await session.execute_plan(ONE_PAGE_PLAN, snapshot)
        assert len(results) == len(ONE_PAGE_PLAN.steps)
        assert all(r.status == ActionStatus.SUCCESS for r in results)
        assert all(r.verified for r in results)

        # Values actually landed in the page
        refreshed = await session.inspect_page()
        assert refreshed.field("first_name").current_value == "Alex"
        assert refreshed.field("country").current_value == "United States"
        assert refreshed.field("authorized").current_value == "Yes"
        assert refreshed.field("relocate").current_value == "true"

    async def test_invalid_radio_value_fails_and_stops_plan(self, session):
        snapshot = await session.open_page(page_url("one_page_form.html"))
        plan = InteractionPlan(
            steps=[
                step(1, "authorized", BrowserAction.SELECT_RADIO, "Maybe"),
                step(2, "first_name", BrowserAction.FILL, "Alex"),
            ]
        )
        results = await session.execute_plan(plan, snapshot)
        assert results[0].status == ActionStatus.FAILED
        assert len(results) == 1  # plan stopped at the failure

    async def test_unknown_field_fails_cleanly(self, session):
        snapshot = await session.open_page(page_url("one_page_form.html"))
        plan = InteractionPlan(steps=[step(1, "no_such_field", BrowserAction.FILL, "x")])
        results = await session.execute_plan(plan, snapshot)
        assert results[0].status == ActionStatus.FAILED
        assert "not found" in results[0].message


class TestFileUpload:
    async def test_upload_verifies_filename(self, session):
        snapshot = await session.open_page(page_url("upload_form.html"))
        resume = TEST_SITES.parent / "fixtures" / "candidate" / "resume" / "Backend.txt"
        result = await session.upload_file(snapshot.field("resume"), str(resume))
        assert result.status == ActionStatus.SUCCESS
        assert result.verified

    async def test_missing_file_fails(self, session):
        snapshot = await session.open_page(page_url("upload_form.html"))
        result = await session.upload_file(
            snapshot.field("resume"), str(TEST_SITES.parent / "fixtures" / "nope.pdf")
        )
        assert result.status == ActionStatus.FAILED

    async def test_upload_outside_allowed_roots_refused(self, session, tmp_path):
        outside = Path("/etc/hosts")
        snapshot = await session.open_page(page_url("upload_form.html"))
        result = await session.upload_file(snapshot.field("resume"), str(outside))
        assert result.status == ActionStatus.FAILED
        assert "allowed directories" in result.message


class TestConditionalFields:
    async def test_conditional_field_appears_after_trigger(self, session):
        snapshot = await session.open_page(page_url("conditional_fields.html"))
        visa = snapshot.field("visa_type")
        assert visa is not None and not visa.visible

        await session.select_radio(snapshot.field("sponsorship"), "Yes")
        refreshed = await session.inspect_page()
        assert refreshed.field("visa_type").visible


class TestPageProgression:
    async def test_multi_page_progression_verified(self, session):
        snapshot = await session.open_page(page_url("multi_page_1.html"))
        await session.fill_field(snapshot.field("full_name"), "Alex Sample")
        await session.fill_field(snapshot.field("email"), "alex@example.com")

        next_action = next(a for a in snapshot.actions if a.type == "next")
        progressed, page2 = await session.click_action(next_action)
        assert progressed
        assert page2.heading.startswith("Step 2")

        await session.fill_field(page2.field("years"), "8")
        progressed, review = await session.click_action(
            next(a for a in page2.actions if a.type == "next")
        )
        assert progressed
        assert "review" in review.heading.lower()

    async def test_submit_actions_are_refused(self, session):
        review = await session.open_page(page_url("multi_page_review.html"))
        submit = next(a for a in review.actions if a.type == "submit")
        with pytest.raises(BrowserError) as excinfo:
            await session.click_action(submit)
        assert "not supported in this phase" in excinfo.value.message


class TestSafetyPauses:
    async def test_captcha_pauses(self, session):
        snapshot = await session.open_page(page_url("captcha.html"))
        assert snapshot.state == PageState.CAPTCHA_DETECTED
        assert snapshot_requires_pause(snapshot)

    async def test_login_pauses(self, session):
        snapshot = await session.open_page(page_url("login.html"))
        assert snapshot.state == PageState.LOGIN_REQUIRED
        assert snapshot_requires_pause(snapshot)

    async def test_mfa_pauses(self, session):
        snapshot = await session.open_page(page_url("mfa.html"))
        assert snapshot.state == PageState.MFA_REQUIRED
        assert snapshot_requires_pause(snapshot)

    async def test_normal_form_does_not_pause(self, session):
        snapshot = await session.open_page(page_url("one_page_form.html"))
        assert not snapshot_requires_pause(snapshot)


class TestNavigationSafety:
    async def test_untrusted_navigation_blocked(self, session):
        with pytest.raises(NavigationBlockedError):
            await session.open_page("https://evil.example.net/steal")

    async def test_javascript_urls_blocked(self, session):
        with pytest.raises(NavigationBlockedError):
            await session.open_page("javascript:alert(1)")


class TestValidationExtraction:
    async def test_validation_errors_extracted(self, session):
        snapshot = await session.open_page(page_url("validation_errors.html"))
        assert snapshot.validation_errors == []
        next_action = next(a for a in snapshot.actions if a.type == "next")
        # Click with the required email empty -> same page, error shown
        _, after = await session.click_action(next_action)
        assert any("Email address is required" in e for e in after.validation_errors)


class TestCrashRecovery:
    async def test_recovery_skips_completed_steps(self, session, tmp_path):
        state_file = tmp_path / "execution_state.json"
        snapshot = await session.open_page(page_url("one_page_form.html"))
        partial = InteractionPlan(steps=ONE_PAGE_PLAN.steps[:3])
        state = ExecutionState(package_id="pkg_test")
        results = await session.execute_plan(partial, snapshot, state, state_file)
        assert all(r.status == ActionStatus.SUCCESS for r in results)
        assert state_file.exists()

        # Simulate a crash: session torn down, new session restores state.
        await session.close()
        recovered = BrowserSession(
            profile_dir=tmp_path / "recovered_profile",
            screenshots_dir=tmp_path / "screenshots",
            policy=NavigationPolicy.for_application(
                "https://careers.example.com/jobs/1", allow_local_files=True
            ),
            settings=BrowserSettings(headless=True, default_timeout_ms=10_000),
        )
        await recovered.start()
        try:
            restored = recovered.load_execution_state(state_file)
            assert restored.completed_step_ids == ["step_1", "step_2", "step_3"]
            snapshot = await recovered.open_page(page_url("one_page_form.html"))
            results = await recovered.execute_plan(ONE_PAGE_PLAN, snapshot, restored)
            by_id = {r.step_id: r for r in results}
            assert by_id["step_1"].status == ActionStatus.SKIPPED
            assert by_id["step_3"].status == ActionStatus.SKIPPED
            assert by_id["step_5"].status == ActionStatus.SUCCESS
        finally:
            await recovered.close()


class TestEvidenceAndPrivacy:
    async def test_screenshot_captured(self, session, tmp_path):
        await session.open_page(page_url("one_page_form.html"))
        path = await session.capture_screenshot("one_page")
        assert path.exists()
        assert path.stat().st_size > 1000

    async def test_logs_do_not_expose_field_values(self, session, caplog):
        secret = "SECRET-VALUE-742"
        snapshot = await session.open_page(page_url("one_page_form.html"))
        with caplog.at_level(logging.DEBUG):
            await session.fill_field(snapshot.field("first_name"), secret)
            plan = InteractionPlan(steps=[step(1, "email", BrowserAction.FILL, secret + "@x.com")])
            await session.execute_plan(plan, snapshot)
        joined = " ".join(record.getMessage() for record in caplog.records)
        assert secret not in joined
