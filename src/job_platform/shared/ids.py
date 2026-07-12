"""Identifier generation and stable hashing utilities."""

from __future__ import annotations

import hashlib
import uuid


def new_id(prefix: str) -> str:
    """Return a unique identifier such as ``search_5f3a...``."""
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


def stable_hash(*parts: str) -> str:
    """Deterministic hash of normalized string parts (for dedup keys)."""
    normalized = "\x1f".join(p.strip().lower() for p in parts)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:16]
