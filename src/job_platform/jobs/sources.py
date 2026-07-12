"""Company source configuration and ATS detection (docs/02D, docs/04)."""

from __future__ import annotations

import json
import re
from pathlib import Path

from pydantic import BaseModel, Field

from job_platform.shared.errors import ConfigurationError


class CompanySource(BaseModel):
    id: str
    name: str
    career_url: str = ""
    enabled: bool = True
    expected_ats: str = ""
    groups: list[str] = Field(default_factory=list)
    countries: list[str] = Field(default_factory=list)


def load_company_sources(path: Path) -> list[CompanySource]:
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ConfigurationError(
            f"Company configuration {path} contains invalid JSON near line {exc.lineno}.",
            details={"path": str(path)},
        ) from exc
    return [CompanySource.model_validate(entry) for entry in data]


_GREENHOUSE = re.compile(
    r"(?:boards|job-boards)\.greenhouse\.io/(?:embed/job_board\?for=)?([A-Za-z0-9_-]+)"
)
_LEVER = re.compile(r"jobs\.(?:eu\.)?lever\.co/([A-Za-z0-9_-]+)")


def detect_ats(career_url: str) -> tuple[str, str]:
    """Return (ats, board_token) for a career URL; ("", "") when unknown."""
    match = _GREENHOUSE.search(career_url)
    if match:
        return "greenhouse", match.group(1)
    match = _LEVER.search(career_url)
    if match:
        return "lever", match.group(1)
    return "", ""
