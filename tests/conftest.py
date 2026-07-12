"""Shared fixtures: synthetic candidate data and temp data roots."""

import shutil
from pathlib import Path

import pytest

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"


@pytest.fixture
def fixtures_dir() -> Path:
    return FIXTURES_DIR


@pytest.fixture
def candidate_dir(tmp_path: Path) -> Path:
    """Copy the synthetic candidate fixture into an isolated temp dir."""
    target = tmp_path / "candidate"
    shutil.copytree(FIXTURES_DIR / "candidate", target)
    return target
