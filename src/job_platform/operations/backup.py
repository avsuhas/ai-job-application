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
    # Microsecond precision so rapid successive backups (e.g. the safety copy
    # taken during a restore) never collide with the archive being restored.
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%S_%f")
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


class RestoreResult(BaseModel):
    restored_from: str
    file_count: int
    safety_copy: str | None = None


def restore_backup(settings: Settings, backup_name: str) -> RestoreResult:
    """Restore a backup over the data root (docs/17 Phase 11 restore).

    A pre-restore safety copy of the current data is taken first so a restore
    is itself recoverable. Paths inside the archive are validated to prevent
    traversal outside the data root.
    """
    from job_platform.shared.errors import StorageError

    data_root = settings.paths.data_root.resolve()
    backup_path = data_root / "backups" / Path(backup_name).name
    if not backup_path.exists():
        raise StorageError(
            f"Backup '{backup_name}' was not found.", details={"backup": backup_name}
        )
    if not verify_backup(backup_path):
        raise StorageError(
            f"Backup '{backup_name}' is corrupt and cannot be restored.",
            details={"backup": backup_name},
        )

    safety = create_backup(settings)  # snapshot current state before overwriting

    file_count = 0
    with zipfile.ZipFile(backup_path) as archive:
        for member in archive.namelist():
            target = (data_root / member).resolve()
            if not target.is_relative_to(data_root):
                raise StorageError(
                    "Backup contains a path that escapes the data root; "
                    "refusing to restore.",
                    details={"member": member},
                )
            if member.endswith("/"):
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            with archive.open(member) as source, target.open("wb") as out:
                out.write(source.read())
            file_count += 1

    logger.info("Restored %d file(s) from %s", file_count, backup_name)
    return RestoreResult(
        restored_from=backup_name,
        file_count=file_count,
        safety_copy=Path(safety.path).name,
    )
