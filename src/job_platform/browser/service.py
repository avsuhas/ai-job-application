"""Playwright browser service (docs/06).

All Playwright usage stays inside this module. Every action follows the
locate → validate → interact → verify lifecycle, navigation is gated by the
trust policy, and page snapshots carry safety signals so callers pause on
CAPTCHA, login walls, and MFA. Final submission is deliberately not
implemented in this phase (docs/17 Phase 5 safety requirements).

Log lines never contain candidate values — only field ids and outcomes.
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from playwright.async_api import Error as PlaywrightError
from playwright.async_api import Locator, async_playwright

from job_platform.browser.detection import PageContent, detect_signals, state_for_signals
from job_platform.browser.extraction import EXTRACTION_SCRIPT
from job_platform.browser.models import (
    ActionResult,
    ActionStatus,
    BrowserAction,
    BrowserHealth,
    ExecutionState,
    FormAction,
    FormField,
    InteractionPlan,
    PageSnapshot,
    PageState,
)
from job_platform.browser.navigation import NavigationPolicy
from job_platform.shared.config import BrowserSettings
from job_platform.shared.errors import BrowserError, NavigationBlockedError
from job_platform.shared.files import atomic_write_text, ensure_dir
from job_platform.shared.logging import get_logger

logger = get_logger("browser.service")


async def check_browser_health(
    profile_dir: Path, screenshots_dir: Path
) -> BrowserHealth:
    """Startup validation (docs/06): playwright, chromium, writable dirs."""
    health = BrowserHealth(healthy=False, playwright_installed=True)
    try:
        async with async_playwright() as pw:
            executable = Path(pw.chromium.executable_path)
            health.chromium_installed = executable.exists()
            if not health.chromium_installed:
                health.problems.append(
                    "Chromium is not installed. Run: uv run playwright install chromium"
                )
    except Exception as exc:  # noqa: BLE001
        health.problems.append(f"Playwright could not start: {exc}")
    for name, directory, attr in (
        ("profile", profile_dir, "profile_dir_writable"),
        ("screenshots", screenshots_dir, "screenshots_dir_writable"),
    ):
        try:
            ensure_dir(directory)
            probe = directory / ".write_probe"
            probe.write_text("ok")
            probe.unlink()
            setattr(health, attr, True)
        except OSError as exc:
            health.problems.append(f"The {name} directory is not writable: {exc}")
    health.healthy = (
        health.chromium_installed
        and health.profile_dir_writable
        and health.screenshots_dir_writable
    )
    return health


class BrowserSession:
    """One persistent-profile Chromium session processing one workflow."""

    def __init__(
        self,
        profile_dir: Path,
        screenshots_dir: Path,
        policy: NavigationPolicy,
        settings: BrowserSettings | None = None,
        allowed_upload_roots: list[Path] | None = None,
    ) -> None:
        self._profile_dir = profile_dir
        self._screenshots_dir = screenshots_dir
        self._policy = policy
        self._settings = settings or BrowserSettings()
        self._allowed_upload_roots = [p.resolve() for p in (allowed_upload_roots or [])]
        self._pw = None
        self._context = None
        self._page = None

    # -- lifecycle ----------------------------------------------------- #

    async def start(self) -> None:
        ensure_dir(self._profile_dir)
        ensure_dir(self._screenshots_dir)
        self._pw = await async_playwright().start()
        try:
            self._context = await self._pw.chromium.launch_persistent_context(
                str(self._profile_dir),
                headless=self._settings.headless,
                slow_mo=self._settings.slow_motion_ms or 0,
            )
        except PlaywrightError as exc:
            await self._pw.stop()
            self._pw = None
            raise BrowserError(
                f"Chromium failed to launch: {exc}. If it is not installed, run "
                "'uv run playwright install chromium'.",
            ) from exc
        self._context.set_default_timeout(self._settings.default_timeout_ms)
        self._page = (
            self._context.pages[0] if self._context.pages else await self._context.new_page()
        )
        logger.info("Browser session started (profile=%s)", self._profile_dir.name)

    async def close(self) -> None:
        if self._context is not None:
            try:
                await self._context.close()
            except PlaywrightError:  # already crashed/closed
                pass
            self._context = None
            self._page = None
        if self._pw is not None:
            await self._pw.stop()
            self._pw = None
        logger.info("Browser session closed")

    @property
    def page(self):
        if self._page is None:
            raise BrowserError("The browser session is not started.")
        return self._page

    # -- navigation and inspection -------------------------------------- #

    async def open_page(self, url: str) -> PageSnapshot:
        if not self._policy.is_allowed(url):
            raise NavigationBlockedError(
                f"Navigation to {url!r} is not allowed by the URL trust policy.",
                details={"url": url},
            )
        try:
            await self.page.goto(url)
        except PlaywrightError as exc:
            raise BrowserError(
                f"Navigation failed: {exc}", details={"url": url}
            ) from exc
        await self._wait_for_stability()
        return await self.inspect_page()

    async def _wait_for_stability(self) -> None:
        """docs/06: wait for load, then a bounded network-idle settle —
        never rely on network idle alone."""
        await self.page.wait_for_load_state("load")
        try:
            await self.page.wait_for_load_state("networkidle", timeout=2_000)
        except PlaywrightError:
            pass  # dynamic pages may never go idle; load already fired

    async def inspect_page(self) -> PageSnapshot:
        raw = await self.page.evaluate(EXTRACTION_SCRIPT)
        content = PageContent.model_validate(raw["content"])
        signals = detect_signals(content)
        snapshot = PageSnapshot(
            url=self.page.url,
            title=raw.get("title", ""),
            heading=(raw.get("heading") or "").strip(),
            state=state_for_signals(signals),
            fields=[FormField.model_validate(f) for f in raw.get("fields", [])],
            actions=[FormAction.model_validate(a) for a in raw.get("actions", [])],
            signals=signals,
            validation_errors=raw.get("validation_errors", []),
            frames=content.iframe_titles,
        )
        logger.info(
            "Inspected page (state=%s, fields=%d, actions=%d)",
            snapshot.state.value,
            len(snapshot.fields),
            len(snapshot.actions),
        )
        return snapshot

    # -- verified action primitives -------------------------------------- #

    def _locator(self, field: FormField) -> Locator:
        if not field.selector:
            raise BrowserError(
                f"Field '{field.field_id}' has no usable selector.",
                details={"field_id": field.field_id},
            )
        return self.page.locator(field.selector).first

    async def _validated_locator(self, field: FormField) -> Locator:
        locator = self._locator(field)
        await locator.scroll_into_view_if_needed()
        if not await locator.is_visible():
            raise BrowserError(f"Field '{field.field_id}' is not visible.")
        if not await locator.is_enabled():
            raise BrowserError(f"Field '{field.field_id}' is disabled.")
        return locator

    def _result(
        self,
        step_id: str,
        field: FormField,
        action: BrowserAction,
        verified: bool,
        message: str = "",
    ) -> ActionResult:
        result = ActionResult(
            step_id=step_id,
            field_id=field.field_id,
            action=action,
            status=ActionStatus.SUCCESS if verified else ActionStatus.FAILED,
            verified=verified,
            message=message,
        )
        logger.info(
            "Action %s on field '%s': %s (verified=%s)",
            action.value,
            field.field_id,
            result.status.value,
            verified,
        )
        return result

    async def fill_field(
        self, field: FormField, value: str, step_id: str = ""
    ) -> ActionResult:
        locator = await self._validated_locator(field)
        await locator.fill(value)
        await locator.blur()
        read_back = await locator.input_value()
        verified = read_back == value
        return self._result(
            step_id, field, BrowserAction.FILL, verified,
            "" if verified else "Value read back from the field did not match.",
        )

    async def select_option(
        self, field: FormField, value: str, step_id: str = ""
    ) -> ActionResult:
        locator = await self._validated_locator(field)
        try:
            await locator.select_option(label=value)
        except PlaywrightError:
            await locator.select_option(value=value)
        selected = await locator.evaluate(
            "el => el.options[el.selectedIndex] ? "
            "(el.options[el.selectedIndex].label || el.options[el.selectedIndex].value) : ''"
        )
        verified = selected.strip().lower() == value.strip().lower() or (
            await locator.input_value()
        ).strip().lower() == value.strip().lower()
        return self._result(
            step_id, field, BrowserAction.SELECT_OPTION, verified,
            "" if verified else "The selected option did not match the requested value.",
        )

    async def select_radio(
        self, field: FormField, value: str, step_id: str = ""
    ) -> ActionResult:
        selector = f"{field.selector}[value=\"{value}\"]"
        locator = self.page.locator(selector).first
        try:
            await locator.scroll_into_view_if_needed()
            await locator.check()
        except PlaywrightError as exc:
            return self._result(
                step_id, field, BrowserAction.SELECT_RADIO, False,
                f"Radio option could not be selected: {exc.__class__.__name__}",
            )
        verified = await locator.is_checked()
        return self._result(step_id, field, BrowserAction.SELECT_RADIO, verified)

    async def set_checkbox(
        self, field: FormField, value: str, step_id: str = ""
    ) -> ActionResult:
        desired = value.strip().lower() in ("true", "yes", "1", "checked")
        locator = await self._validated_locator(field)
        if desired:
            await locator.check()
        else:
            await locator.uncheck()
        verified = await locator.is_checked() == desired
        return self._result(step_id, field, BrowserAction.SET_CHECKBOX, verified)

    async def upload_file(
        self, field: FormField, path: str, step_id: str = ""
    ) -> ActionResult:
        file_path = Path(path).resolve()
        if self._allowed_upload_roots and not any(
            file_path.is_relative_to(root) for root in self._allowed_upload_roots
        ):
            return self._result(
                step_id, field, BrowserAction.UPLOAD_FILE, False,
                "Upload path is outside the allowed directories.",
            )
        if not file_path.exists():
            return self._result(
                step_id, field, BrowserAction.UPLOAD_FILE, False,
                "Upload file does not exist.",
            )
        locator = self._locator(field)
        await locator.set_input_files(str(file_path))
        uploaded_name = await locator.evaluate(
            "el => el.files && el.files.length ? el.files[0].name : ''"
        )
        verified = uploaded_name == file_path.name
        return self._result(
            step_id, field, BrowserAction.UPLOAD_FILE, verified,
            "" if verified else "Uploaded filename did not match.",
        )

    # -- plan execution --------------------------------------------------- #

    async def execute_plan(
        self,
        plan: InteractionPlan,
        snapshot: PageSnapshot,
        state: ExecutionState | None = None,
        state_file: Path | None = None,
    ) -> list[ActionResult]:
        """Execute steps with verification; stop on the first failure.

        Completed step ids from a previous run are skipped, which is what
        makes crash recovery resumable.
        """
        state = state or ExecutionState()
        results: list[ActionResult] = []
        dispatch = {
            BrowserAction.FILL: self.fill_field,
            BrowserAction.SELECT_OPTION: self.select_option,
            BrowserAction.SELECT_RADIO: self.select_radio,
            BrowserAction.SET_CHECKBOX: self.set_checkbox,
            BrowserAction.UPLOAD_FILE: self.upload_file,
        }
        for step in plan.steps:
            if step.step_id in state.completed_step_ids:
                results.append(
                    ActionResult(
                        step_id=step.step_id,
                        field_id=step.field_id,
                        action=step.action,
                        status=ActionStatus.SKIPPED,
                        verified=True,
                        message="Already completed in a previous session.",
                    )
                )
                continue
            field = snapshot.field(step.field_id)
            if field is None:
                results.append(
                    ActionResult(
                        step_id=step.step_id,
                        field_id=step.field_id,
                        action=step.action,
                        status=ActionStatus.FAILED,
                        message="Field not found in the current page snapshot.",
                    )
                )
                break
            try:
                result = await dispatch[step.action](field, step.value, step.step_id)
            except BrowserError as exc:
                result = ActionResult(
                    step_id=step.step_id,
                    field_id=step.field_id,
                    action=step.action,
                    status=ActionStatus.FAILED,
                    message=exc.message,
                )
            results.append(result)
            if result.status != ActionStatus.SUCCESS:
                break
            state.completed_step_ids.append(step.step_id)
            state.current_url = self.page.url
            if state_file is not None:
                self.save_execution_state(state, state_file)
        return results

    # -- page progression -------------------------------------------------- #

    async def click_action(self, action: FormAction) -> tuple[bool, PageSnapshot]:
        """Click a next/back control and verify the page actually progressed.

        Refuses submit-type actions: final submission is not part of Phase 5.
        """
        if action.type == "submit":
            raise BrowserError(
                "Submit actions are not supported in this phase; submission "
                "requires the review workflow.",
                details={"action_id": action.action_id},
            )
        before_url = self.page.url
        before = await self.page.evaluate(
            "() => (document.querySelector('h1') || {}).innerText || document.title"
        )
        locator = self.page.locator(action.selector).first
        await locator.click()
        await self._wait_for_stability()
        after_url = self.page.url
        after = await self.page.evaluate(
            "() => (document.querySelector('h1') || {}).innerText || document.title"
        )
        progressed = after_url != before_url or after != before
        logger.info(
            "Clicked action '%s' (progressed=%s)", action.action_id, progressed
        )
        return progressed, await self.inspect_page()

    # -- evidence and recovery --------------------------------------------- #

    async def capture_screenshot(self, name: str) -> Path:
        ensure_dir(self._screenshots_dir)
        safe = "".join(c for c in name if c.isalnum() or c in "_-") or "page"
        stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%S")
        path = self._screenshots_dir / f"{safe}_{stamp}.png"
        await self.page.screenshot(path=str(path), full_page=True)
        return path

    def save_execution_state(self, state: ExecutionState, path: Path) -> None:
        state.last_saved = datetime.now(UTC)
        atomic_write_text(path, state.model_dump_json(indent=2))

    @staticmethod
    def load_execution_state(path: Path) -> ExecutionState:
        return ExecutionState.model_validate_json(path.read_text(encoding="utf-8"))


def snapshot_requires_pause(snapshot: PageSnapshot) -> bool:
    """True when a human must take over (docs/06: no automatic CAPTCHA/MFA/login)."""
    return snapshot.state in (
        PageState.CAPTCHA_DETECTED,
        PageState.LOGIN_REQUIRED,
        PageState.MFA_REQUIRED,
    )
