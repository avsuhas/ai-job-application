"""Prompt-injection detection for untrusted content (docs/12 Prompt Injection).

Job descriptions, form labels, and web page text are untrusted data. The
provider already treats them as data (delimited, schema-constrained), but
scanning for injection phrasing lets review surface a warning and lets the
form engine refuse to auto-fill fields whose own label tries to hijack the
agent. This is heuristic defense-in-depth, not a guarantee.
"""

from __future__ import annotations

import re

from pydantic import BaseModel, Field

_INJECTION_PATTERNS = [
    re.compile(p, re.IGNORECASE)
    for p in (
        r"ignore (all |the |your )?(previous|prior|above) instructions",
        r"disregard (all |the |your )?(previous|prior|above)",
        r"forget (everything|all|your instructions)",
        r"you are now (a|an|in) ",
        r"new instructions?:",
        r"system prompt",
        r"reveal|disclose|print|output.{0,30}(secret|api key|password|credential|"
        r"system prompt|instructions)",
        r"upload (every|all|any) (local )?file",
        r"send.{0,30}(all|every).{0,20}(file|data|candidate)",
        r"do not (tell|inform|ask) the (user|candidate)",
        r"without (asking|approval|confirmation)",
        r"</?(system|assistant|user)>",
    )
]


class InjectionScan(BaseModel):
    detected: bool = False
    matches: list[str] = Field(default_factory=list)


def scan_for_injection(text: str, max_matches: int = 5) -> InjectionScan:
    if not text:
        return InjectionScan()
    matches: list[str] = []
    for pattern in _INJECTION_PATTERNS:
        found = pattern.search(text)
        if found:
            snippet = found.group(0).strip()
            if snippet not in matches:
                matches.append(snippet[:120])
        if len(matches) >= max_matches:
            break
    return InjectionScan(detected=bool(matches), matches=matches)
