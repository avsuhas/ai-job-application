"""Package and browser-profile locks (docs/08 Package Lock Manager).

File-based locks so a second process (or a crashed prior run) can never
execute the same package or share a browser profile concurrently. A lock file
records owner pid and timestamp; stale locks (dead pid or expired age) are
reclaimed with a log entry (docs/08 Stale Lock Recovery).
"""

from __future__ import annotations

import json
import os
from datetime import UTC, datetime, timedelta
from pathlib import Path

from job_platform.shared.errors import JobPlatformError
from job_platform.shared.files import atomic_write_text, ensure_dir
from job_platform.shared.logging import get_logger

logger = get_logger("orchestration.locks")

STALE_AFTER = timedelta(hours=2)


class LockUnavailableError(JobPlatformError):
    code = "lock_unavailable"


def _pid_alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


class FileLock:
    def __init__(self, path: Path, owner: str = "") -> None:
        self._path = path
        self._owner = owner or f"pid_{os.getpid()}"
        self._held = False

    @property
    def held(self) -> bool:
        return self._held

    def _read(self) -> dict | None:
        try:
            return json.loads(self._path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return None

    def _is_stale(self, data: dict) -> bool:
        pid = data.get("pid")
        if isinstance(pid, int) and not _pid_alive(pid):
            return True
        try:
            acquired = datetime.fromisoformat(data["acquired_at"])
        except (KeyError, ValueError):
            return True
        return datetime.now(UTC) - acquired > STALE_AFTER

    def acquire(self) -> None:
        ensure_dir(self._path.parent)
        if self._path.exists():
            existing = self._read()
            if existing is not None and existing.get("pid") == os.getpid():
                # Re-entrant within the same process (e.g. resume).
                self._held = True
                return
            if existing is not None and not self._is_stale(existing):
                raise LockUnavailableError(
                    f"Lock {self._path.name} is held by another process "
                    f"(pid {existing.get('pid')}).",
                    details={"lock": str(self._path)},
                )
            logger.warning("Reclaiming stale lock %s", self._path.name)
        atomic_write_text(
            self._path,
            json.dumps(
                {
                    "owner": self._owner,
                    "pid": os.getpid(),
                    "acquired_at": datetime.now(UTC).isoformat(),
                }
            ),
        )
        self._held = True

    def release(self) -> None:
        if not self._held:
            return
        try:
            data = self._read()
            if data is not None and data.get("pid") == os.getpid():
                self._path.unlink(missing_ok=True)
        finally:
            self._held = False

    def __enter__(self) -> FileLock:
        self.acquire()
        return self

    def __exit__(self, *exc_info) -> None:
        self.release()


class LockManager:
    """Creates package-execution and browser-profile locks (docs/08)."""

    def __init__(self, packages_dir: Path, profiles_dir: Path) -> None:
        self._packages_dir = packages_dir
        self._profiles_dir = profiles_dir

    def package_lock(self, package_id: str) -> FileLock:
        return FileLock(self._packages_dir / package_id / "execution" / "package.lock")

    def profile_lock(self, profile_name: str = "default") -> FileLock:
        safe = "".join(c for c in profile_name if c.isalnum() or c in "_-") or "default"
        return FileLock(self._profiles_dir / f"{safe}.lock")

    def is_package_locked(self, package_id: str) -> bool:
        lock_path = self._packages_dir / package_id / "execution" / "package.lock"
        if not lock_path.exists():
            return False
        probe = FileLock(lock_path)
        data = probe._read()
        if data is None or probe._is_stale(data):
            return False
        return data.get("pid") != os.getpid()
