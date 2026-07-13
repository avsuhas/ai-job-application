"""Sensitive-field policy (docs/12 Malicious Website; docs/17 MVP exclusions).

Some fields must never be auto-filled or sent to the provider by the MVP:
government identification, bank/payment details, and passwords. These are
hard-blocked at the form-mapping layer so no policy toggle can enable them,
and their presence on a page is a signal review surfaces.
"""

from __future__ import annotations

import re

from pydantic import BaseModel

# Field label / semantic patterns that must be left to the user (never
# auto-filled, never sent to the reasoning provider).
_BLOCKED_PATTERNS = [
    (re.compile(r"social security|ssn\b|national insurance|sin\b", re.IGNORECASE),
     "government_id"),
    (re.compile(r"passport|driver'?s? licen[cs]e|national id\b", re.IGNORECASE),
     "government_id"),
    (re.compile(r"bank account|routing number|iban|swift|sort code", re.IGNORECASE),
     "bank_details"),
    (re.compile(r"credit card|card number|cvv|cvc|payment", re.IGNORECASE),
     "payment"),
    (re.compile(r"\bpassword\b", re.IGNORECASE), "password"),
    (re.compile(r"date of birth|birth ?date|\bdob\b", re.IGNORECASE), "date_of_birth"),
]


class SensitiveFieldCheck(BaseModel):
    blocked: bool = False
    category: str = ""
    reason: str = ""


def check_sensitive_field(label: str, section: str = "", field_type: str = "") -> SensitiveFieldCheck:
    haystack = f"{label} {section}".strip()
    if field_type == "password":
        return SensitiveFieldCheck(
            blocked=True, category="password",
            reason="Password fields are never auto-filled.",
        )
    for pattern, category in _BLOCKED_PATTERNS:
        if pattern.search(haystack):
            return SensitiveFieldCheck(
                blocked=True,
                category=category,
                reason=f"'{category}' fields must be completed by the user (policy).",
            )
    return SensitiveFieldCheck()
