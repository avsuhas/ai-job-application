"""Data/config migration framework with rollback (docs/17 Phase 11).

Migrations run in order, each inside a data-root safety copy taken before the
run. If any migration raises, the run stops and the safety copy is restored,
leaving the data exactly as it was (docs/17: failed migration rolls back).
The applied schema version is tracked so migrations are idempotent.
"""

from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path

from pydantic import BaseModel, Field

from job_platform.shared.config import Settings
from job_platform.shared.files import atomic_write_json
from job_platform.shared.logging import get_logger

logger = get_logger("operations.migrations")

Migration = Callable[[Settings], None]


class MigrationStep(BaseModel):
    version: int
    name: str


class MigrationResult(BaseModel):
    from_version: int
    to_version: int
    applied: list[str] = Field(default_factory=list)
    rolled_back: bool = False
    error: str | None = None


# Registered migrations in ascending version order. Empty for now — the
# framework is what Phase 11 requires; concrete migrations are added as the
# schema evolves.
_MIGRATIONS: list[tuple[MigrationStep, Migration]] = []


def _version_path(settings: Settings) -> Path:
    return settings.paths.data_root / "schema_version.json"


def current_version(settings: Settings) -> int:
    path = _version_path(settings)
    if not path.exists():
        return 0
    try:
        return int(json.loads(path.read_text(encoding="utf-8")).get("version", 0))
    except (OSError, ValueError):
        return 0


def _set_version(settings: Settings, version: int) -> None:
    atomic_write_json(_version_path(settings), {"version": version})


def run_migrations(
    settings: Settings,
    migrations: list[tuple[MigrationStep, Migration]] | None = None,
) -> MigrationResult:
    from job_platform.operations.backup import create_backup, restore_backup

    migrations = migrations if migrations is not None else _MIGRATIONS
    start = current_version(settings)
    pending = [(step, fn) for step, fn in migrations if step.version > start]
    result = MigrationResult(from_version=start, to_version=start)
    if not pending:
        return result

    safety = create_backup(settings)  # rollback point
    try:
        for step, migrate in sorted(pending, key=lambda item: item[0].version):
            logger.info("Applying migration %d: %s", step.version, step.name)
            migrate(settings)
            _set_version(settings, step.version)
            result.applied.append(step.name)
            result.to_version = step.version
    except Exception as exc:  # noqa: BLE001 - any failure triggers rollback
        logger.exception("Migration failed; rolling back")
        restore_backup(settings, Path(safety.path).name)
        result.rolled_back = True
        result.error = str(exc)
        result.to_version = start
    return result
