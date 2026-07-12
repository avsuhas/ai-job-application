"""Fixtures for real-Chromium browser tests against local synthetic forms."""

from pathlib import Path

import pytest

from job_platform.browser.navigation import NavigationPolicy
from job_platform.browser.service import BrowserSession, check_browser_health
from job_platform.shared.config import BrowserSettings

TEST_SITES = Path(__file__).parent.parent.parent / "local_test_sites"


def page_url(name: str) -> str:
    return (TEST_SITES / name).as_uri()


@pytest.fixture(scope="session")
def chromium_available(tmp_path_factory):
    """Skip the whole suite when Chromium is not installed."""
    import asyncio

    root = tmp_path_factory.mktemp("health")
    health = asyncio.run(check_browser_health(root / "profile", root / "shots"))
    if not health.healthy:
        pytest.skip(f"Chromium unavailable: {health.problems}")
    return True


@pytest.fixture
async def session(tmp_path, chromium_available):
    """A headless session with a fresh profile allowed to open local files."""
    browser = BrowserSession(
        profile_dir=tmp_path / "profile",
        screenshots_dir=tmp_path / "screenshots",
        policy=NavigationPolicy.for_application(
            "https://careers.example.com/jobs/1", allow_local_files=True
        ),
        settings=BrowserSettings(headless=True, default_timeout_ms=10_000),
        allowed_upload_roots=[tmp_path, TEST_SITES.parent / "fixtures"],
    )
    await browser.start()
    yield browser
    await browser.close()
