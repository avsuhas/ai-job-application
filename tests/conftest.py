"""Shared fixtures: synthetic candidate data and temp data roots."""

import shutil
from pathlib import Path

import pytest

from job_platform.providers.base import ReasoningProvider

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"


class StubProvider(ReasoningProvider):
    """Base for test providers: every task raises unless overridden."""

    name = "stub"

    async def analyze_job(self, job):
        raise NotImplementedError

    async def rank_job(self, request):
        raise NotImplementedError

    async def select_resume(self, request):
        raise NotImplementedError

    async def tailor_resume(self, request):
        raise NotImplementedError

    async def generate_cover_letter(self, request):
        raise NotImplementedError

    async def generate_application_answer(self, request):
        raise NotImplementedError


@pytest.fixture
def fixtures_dir() -> Path:
    return FIXTURES_DIR


@pytest.fixture
def candidate_dir(tmp_path: Path) -> Path:
    """Copy the synthetic candidate fixture into an isolated temp dir."""
    target = tmp_path / "candidate"
    shutil.copytree(FIXTURES_DIR / "candidate", target)
    return target
