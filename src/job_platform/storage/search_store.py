"""Persist search results locally (docs/04 user_data/searches/results)."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from pydantic import BaseModel, Field

from job_platform.jobs.service import DiscoveryResult, SearchFilters
from job_platform.ranking.models import RankedJob
from job_platform.shared.errors import StorageError
from job_platform.shared.files import atomic_write_text
from job_platform.shared.ids import new_id


class SearchRecord(BaseModel):
    search_id: str = Field(default_factory=lambda: new_id("search"))
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    status: str = "pending"  # pending | discovering | ranking | complete | failed
    filters: SearchFilters = Field(default_factory=SearchFilters)
    source_ids: list[str] = Field(default_factory=list)
    discovery: DiscoveryResult | None = None
    ranked_jobs: list[RankedJob] = Field(default_factory=list)
    error: str | None = None
    progress_message: str = ""


class SearchStore:
    def __init__(self, results_dir: Path) -> None:
        self._dir = results_dir

    def _path(self, search_id: str) -> Path:
        # search ids are generated internally, but never trust them as paths
        safe = "".join(c for c in search_id if c.isalnum() or c == "_")
        return self._dir / f"{safe}.json"

    def save(self, record: SearchRecord) -> None:
        atomic_write_text(self._path(record.search_id), record.model_dump_json(indent=2))

    def load(self, search_id: str) -> SearchRecord:
        path = self._path(search_id)
        if not path.exists():
            raise StorageError(
                f"Search '{search_id}' was not found.", details={"search_id": search_id}
            )
        return SearchRecord.model_validate_json(path.read_text(encoding="utf-8"))

    def list_ids(self) -> list[str]:
        if not self._dir.exists():
            return []
        return sorted(p.stem for p in self._dir.glob("search_*.json"))
