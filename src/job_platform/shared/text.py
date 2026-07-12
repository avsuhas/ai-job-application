"""Text normalization helpers used across discovery and dedup."""

from __future__ import annotations

import re

_WHITESPACE = re.compile(r"\s+")
_NON_ALNUM = re.compile(r"[^a-z0-9]+")


def normalize_whitespace(value: str) -> str:
    return _WHITESPACE.sub(" ", value).strip()


def slugify(value: str) -> str:
    return _NON_ALNUM.sub("-", value.lower()).strip("-")


def truncate(value: str, limit: int) -> str:
    if len(value) <= limit:
        return value
    return value[: limit - 1].rstrip() + "…"
