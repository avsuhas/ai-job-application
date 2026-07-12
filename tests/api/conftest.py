"""Shared API test fixtures: app wired to temp dirs with the mock provider."""

import json
import shutil

import pytest
from fastapi.testclient import TestClient

from job_platform.api.app import create_app
from job_platform.shared.config import Settings

GREENHOUSE_URL = "https://boards-api.greenhouse.io/v1/boards/exampleco/jobs"


@pytest.fixture
def client(tmp_path, candidate_dir, monkeypatch):
    """App wired to temp dirs, fixture candidate data, and the mock provider."""
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    data_root = tmp_path / "user_data"
    data_root.mkdir(parents=True, exist_ok=True)
    shutil.copytree(candidate_dir, data_root / "candidate")

    config_dir = tmp_path / "config"
    config_dir.mkdir()
    (config_dir / "companies.json").write_text(
        json.dumps(
            [
                {
                    "id": "exampleco",
                    "name": "ExampleCo",
                    "career_url": "https://boards.greenhouse.io/exampleco",
                    "enabled": True,
                },
                {
                    "id": "unsupported",
                    "name": "CustomSite",
                    "career_url": "https://careers.custom.com",
                    "enabled": True,
                },
            ]
        )
    )

    settings = Settings(
        reasoning={"provider": "mock"},
        paths={"data_root": data_root},
        config_dir=config_dir,
    )
    app = create_app(settings)
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def greenhouse_payload(fixtures_dir):
    return json.loads((fixtures_dir / "jobs" / "greenhouse_board.json").read_text())
