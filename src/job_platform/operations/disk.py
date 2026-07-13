"""Disk-space monitoring (docs/17 Phase 11 low-disk behavior).

Submission and other write-heavy operations must not proceed when the local
disk is critically low — a failed write mid-submission could corrupt state.
"""

from __future__ import annotations

import shutil
from pathlib import Path

from pydantic import BaseModel

# Below this free space, block operations that must write durably.
MIN_FREE_BYTES = 200 * 1024 * 1024  # 200 MB


class DiskStatus(BaseModel):
    total_bytes: int
    free_bytes: int
    healthy: bool
    safe_to_write: bool
    message: str = ""


def check_disk(path: Path, min_free_bytes: int = MIN_FREE_BYTES) -> DiskStatus:
    usage = shutil.disk_usage(path if path.exists() else path.anchor or "/")
    safe = usage.free >= min_free_bytes
    return DiskStatus(
        total_bytes=usage.total,
        free_bytes=usage.free,
        healthy=safe,
        safe_to_write=safe,
        message=""
        if safe
        else (
            f"Only {usage.free // (1024 * 1024)} MB free; durable writes are "
            "blocked until space is freed."
        ),
    )
