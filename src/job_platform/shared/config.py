"""Application configuration.

Settings are layered per docs/04: defaults < config/settings.json < environment
variables (``SECTION__FIELD`` style, e.g. ``REASONING__MODEL``). Secrets such as
``ANTHROPIC_API_KEY`` come only from the environment / .env file.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from job_platform.shared.errors import ConfigurationError

AutomationMode = Literal["review", "automatic", "manual"]


class ReasoningSettings(BaseModel):
    provider: str = "claude"
    model: str = ""
    temperature: float = 0.0
    max_retries: int = 3
    timeout_seconds: float = 120.0
    base_url: str | None = None


class BrowserSettings(BaseModel):
    headless: bool = False
    reuse_profile: bool = True
    slow_motion_ms: int = 0
    default_timeout_ms: int = 30_000


class ApplicationSettings(BaseModel):
    automation_mode: AutomationMode = "review"
    maximum_batch_size: int = 10
    capture_screenshots: bool = True
    tailor_resume: bool = True
    generate_cover_letter: bool = False


class JobSearchSettings(BaseModel):
    max_results_per_source: int = 100
    minimum_match_score: int = 60
    hide_already_applied: bool = True


class StorageSettings(BaseModel):
    tracker_format: Literal["csv"] = "csv"


class PathSettings(BaseModel):
    data_root: Path = Path("user_data")

    @property
    def candidate_dir(self) -> Path:
        return self.data_root / "candidate"

    @property
    def resume_dir(self) -> Path:
        return self.candidate_dir / "resume"

    @property
    def profile_dir(self) -> Path:
        return self.candidate_dir / "profile"

    @property
    def generated_dir(self) -> Path:
        return self.candidate_dir / "generated"

    @property
    def applications_dir(self) -> Path:
        return self.data_root / "applications"

    @property
    def tracker_path(self) -> Path:
        return self.applications_dir / "tracker.csv"

    @property
    def packages_dir(self) -> Path:
        return self.applications_dir / "packages"

    @property
    def searches_dir(self) -> Path:
        return self.data_root / "searches" / "results"

    @property
    def browser_profile_dir(self) -> Path:
        return self.data_root / "browser" / "profiles"

    @property
    def screenshots_dir(self) -> Path:
        return self.data_root / "screenshots"

    @property
    def logs_dir(self) -> Path:
        return self.data_root / "logs"

    def runtime_directories(self) -> list[Path]:
        return [
            self.resume_dir,
            self.profile_dir,
            self.candidate_dir / "documents",
            self.generated_dir / "resumes",
            self.generated_dir / "cover_letters",
            self.generated_dir / "answers",
            self.packages_dir,
            self.searches_dir,
            self.data_root / "searches" / "saved",
            self.browser_profile_dir,
            self.screenshots_dir,
            self.logs_dir,
        ]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_nested_delimiter="__",
        extra="ignore",
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls,
        init_settings,
        env_settings,
        dotenv_settings,
        file_secret_settings,
    ):
        # Environment variables override values loaded from settings.json,
        # which are passed in as init kwargs by load_settings().
        return (env_settings, dotenv_settings, init_settings, file_secret_settings)

    app_env: str = "development"
    anthropic_api_key: str = ""

    reasoning: ReasoningSettings = Field(default_factory=ReasoningSettings)
    browser: BrowserSettings = Field(default_factory=BrowserSettings)
    applications: ApplicationSettings = Field(default_factory=ApplicationSettings)
    job_search: JobSearchSettings = Field(default_factory=JobSearchSettings)
    storage: StorageSettings = Field(default_factory=StorageSettings)
    paths: PathSettings = Field(default_factory=PathSettings)

    config_dir: Path = Path("config")
    prompts_dir: Path = Path("prompts")

    @property
    def companies_path(self) -> Path:
        return self.config_dir / "companies.json"


def load_settings(settings_file: Path | None = None) -> Settings:
    """Build settings from config/settings.json (if present) plus environment."""
    file_values: dict = {}
    path = settings_file or Path("config/settings.json")
    if path.exists():
        try:
            file_values = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise ConfigurationError(
                f"Settings file {path} contains invalid JSON: {exc}",
                details={"path": str(path)},
            ) from exc
    return Settings(**file_values)
