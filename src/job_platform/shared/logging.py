"""Structured logging bootstrap.

Log records carry component / workflow context and are emitted both as
human-readable console lines and JSON lines under ``user_data/logs/``.
Sensitive values must be redacted by callers before logging.
"""

from __future__ import annotations

import json
import logging
from datetime import UTC, datetime
from pathlib import Path

_CONTEXT_FIELDS = ("component", "workflow_id", "application_id", "error_code", "retry_count")


class JsonLineFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        for field in _CONTEXT_FIELDS:
            value = getattr(record, field, None)
            if value is not None:
                payload[field] = value
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False)


def configure_logging(logs_dir: Path | None = None, level: int = logging.INFO) -> None:
    root = logging.getLogger("job_platform")
    root.setLevel(level)
    root.handlers.clear()

    console = logging.StreamHandler()
    console.setFormatter(logging.Formatter("%(asctime)s %(levelname)-7s %(name)s - %(message)s"))
    root.addHandler(console)

    if logs_dir is not None:
        logs_dir.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(logs_dir / "app.jsonl", encoding="utf-8")
        file_handler.setFormatter(JsonLineFormatter())
        root.addHandler(file_handler)


def get_logger(component: str) -> logging.LoggerAdapter:
    logger = logging.getLogger(f"job_platform.{component}")
    return logging.LoggerAdapter(logger, {"component": component})
