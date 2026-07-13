"""Secret redaction for logs and diagnostic output (docs/12 Secret Leakage).

Redaction is a defense-in-depth layer: callers already avoid logging
candidate values, but a logging filter guarantees API keys, bearer tokens,
and obvious secret patterns never reach log files, error traces, or
diagnostic bundles.
"""

from __future__ import annotations

import logging
import re

_PATTERNS: list[tuple[re.Pattern, str]] = [
    # Anthropic-style and generic API keys.
    (re.compile(r"sk-[A-Za-z0-9_\-]{16,}"), "sk-***REDACTED***"),
    (re.compile(r"(?i)\bbearer\s+[A-Za-z0-9._\-]{12,}"), "Bearer ***REDACTED***"),
    # key=value / key: value forms for common secret field names.
    (
        re.compile(
            r"(?i)\b(api[_-]?key|token|secret|password|authorization)\b"
            r"(\s*[:=]\s*)(['\"]?)([^\s'\",}]+)"
        ),
        r"\1\2\3***REDACTED***",
    ),
]


def redact(text: str) -> str:
    if not text:
        return text
    for pattern, replacement in _PATTERNS:
        text = pattern.sub(replacement, text)
    return text


class RedactionFilter(logging.Filter):
    """Logging filter that redacts secrets from every emitted record."""

    def filter(self, record: logging.LogRecord) -> bool:
        if isinstance(record.msg, str):
            record.msg = redact(record.msg)
        if record.args:
            record.args = tuple(
                redact(arg) if isinstance(arg, str) else arg for arg in record.args
            )
        return True


def install_redaction(logger_name: str = "job_platform") -> None:
    """Attach the redaction filter to a logger and all its handlers."""
    logger = logging.getLogger(logger_name)
    redaction = RedactionFilter()
    logger.addFilter(redaction)
    for handler in logger.handlers:
        handler.addFilter(redaction)
