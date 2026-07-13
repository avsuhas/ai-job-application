"""Local backups (docs/17 Phase 10; full restore arrives with Phase 11).

Backs up everything that cannot be regenerated: the Candidate Knowledge
Base, the application tracker, history events, queues, and package
manifests/artifacts. Browser profiles and screenshots are excluded — they
are large, machine-specific, and recreatable.
"""

from __future__ import annotations

import zipfile
from datetime import UTC, datetime
from pathlib import Path

from pydantic import BaseModel

from job_platform.shared.config import Settings
from job_platform.shared.logging import get_logger

logger = get_logger("operations.backup")

_EXCLUDED_PARTS = ("browser", "screenshots", "logs", "backups")


class BackupResult(BaseModel):
    path: str
    file_count: int
    size_bytes: int
    created_at: datetime


def create_backup(settings: Settings) -> BackupResult:
    data_root = settings.paths.data_root
    backups_dir = data_root / "backups"
    backups_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%S")
    target = backups_dir / f"backup_{stamp}.zip"

    file_count = 0
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(data_root.rglob("*")):
            if not path.is_file():
                continue
            relative = path.relative_to(data_root)
            if relative.parts and relative.parts[0] in _EXCLUDED_PARTS:
                continue
            if "screenshots" in relative.parts:
                continue
            archive.write(path, arcname=str(relative))
            file_count += 1

    result = BackupResult(
        path=str(target),
        file_count=file_count,
        size_bytes=target.stat().st_size,
        created_at=datetime.now(UTC),
    )
    logger.info("Backup created: %s (%d files)", target.name, file_count)
    return result


def list_backups(settings: Settings) -> list[dict]:
    backups_dir = settings.paths.data_root / "backups"
    if not backups_dir.exists():
        return []
    return [
        {"name": p.name, "size_bytes": p.stat().st_size}
        for p in sorted(backups_dir.glob("backup_*.zip"), reverse=True)
    ]


def verify_backup(path: Path) -> bool:
    """A backup is valid when the archive passes its CRC check."""
    try:
        with zipfile.ZipFile(path) as archive:
            return archive.testzip() is None
    except (OSError, zipfile.BadZipFile):
        return False
