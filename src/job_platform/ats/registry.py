"""ATS adapter registry (docs/09).

Resolves which adapter owns a page using the spec's priority order; when no
adapter matches confidently, the Generic Form Engine is the fallback and
manual mode the floor. Unsupported variants therefore fail safely.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from job_platform.ats.base import AdapterStatus, ATSAdapter, ATSDetectionResult
from job_platform.browser.models import PageSnapshot
from job_platform.shared.logging import get_logger

logger = get_logger("ats.registry")

# Below this confidence the registry refuses to hand the page to an adapter.
ADAPTER_MATCH_THRESHOLD = 60


class AdapterResolution(BaseModel):
    """Outcome of adapter resolution for one page."""

    adapter_id: str | None = None
    detection: ATSDetectionResult = Field(default_factory=ATSDetectionResult)
    use_generic_fallback: bool = True


class ATSAdapterRegistry:
    def __init__(self) -> None:
        self._adapters: dict[str, ATSAdapter] = {}

    def register(self, adapter: ATSAdapter) -> None:
        self._adapters[adapter.metadata.adapter_id] = adapter

    def unregister(self, adapter_id: str) -> None:
        self._adapters.pop(adapter_id, None)

    def get_adapter(self, adapter_id: str) -> ATSAdapter | None:
        adapter = self._adapters.get(adapter_id)
        if adapter is None or not adapter.metadata.enabled:
            return None
        return adapter

    def list_adapters(self) -> list[ATSAdapter]:
        return list(self._adapters.values())

    def resolve(
        self,
        url: str,
        snapshot: PageSnapshot | None = None,
        override_adapter_id: str | None = None,
    ) -> AdapterResolution:
        """docs/09 Adapter Priority: explicit override → best detection →
        generic fallback."""
        if override_adapter_id:
            adapter = self.get_adapter(override_adapter_id)
            if adapter is not None:
                return AdapterResolution(
                    adapter_id=override_adapter_id,
                    detection=ATSDetectionResult(
                        detected_ats=override_adapter_id,
                        confidence=100,
                        detection_methods=["package_override"],
                        matched_adapter=override_adapter_id,
                    ),
                    use_generic_fallback=adapter.metadata.generic_fallback_allowed,
                )

        best: ATSDetectionResult | None = None
        for adapter in self._adapters.values():
            meta = adapter.metadata
            if not meta.enabled or meta.status in (
                AdapterStatus.DISABLED,
                AdapterStatus.UNSUPPORTED,
            ):
                continue
            detection = adapter.detect(url, snapshot)
            if best is None or detection.confidence > best.confidence:
                best = detection

        if best is None or best.confidence < ADAPTER_MATCH_THRESHOLD:
            logger.info(
                "No adapter matched %s confidently; using the generic engine.", url
            )
            return AdapterResolution(
                adapter_id=None,
                detection=best or ATSDetectionResult(),
                use_generic_fallback=True,
            )
        logger.info(
            "Adapter '%s' matched %s (confidence=%d, methods=%s)",
            best.matched_adapter,
            url,
            best.confidence,
            best.detection_methods,
        )
        return AdapterResolution(
            adapter_id=best.matched_adapter,
            detection=best,
            use_generic_fallback=best.generic_fallback_allowed,
        )
