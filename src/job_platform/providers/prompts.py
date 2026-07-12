"""Prompt template loading and rendering (docs/05 Prompt Rendering).

Templates live in ``prompts/`` as Markdown with ``{{placeholder}}`` variables.
The renderer validates that every placeholder is supplied so a renamed
variable fails loudly instead of sending a broken prompt to the provider.
"""

from __future__ import annotations

import re
from functools import lru_cache
from pathlib import Path

from job_platform.shared.errors import ConfigurationError

_PLACEHOLDER = re.compile(r"\{\{(\w+)\}\}")


class PromptService:
    def __init__(self, prompts_dir: Path) -> None:
        self._prompts_dir = prompts_dir

    @lru_cache(maxsize=64)  # noqa: B019 - service is process-lived
    def load(self, name: str) -> str:
        path = self._prompts_dir / f"{name}.md"
        if not path.exists():
            raise ConfigurationError(
                f"Prompt template '{name}' not found at {path}",
                details={"path": str(path)},
            )
        return path.read_text(encoding="utf-8")

    def render(self, name: str, variables: dict[str, str]) -> str:
        template = self.load(name)
        required = set(_PLACEHOLDER.findall(template))
        missing = required - variables.keys()
        if missing:
            raise ConfigurationError(
                f"Prompt template '{name}' is missing variables: {sorted(missing)}",
                details={"template": name, "missing": sorted(missing)},
            )
        rendered = template
        for key in required:
            rendered = rendered.replace(f"{{{{{key}}}}}", variables[key])
        return rendered

    def system_instructions(self) -> str:
        return self.load("shared_system")
