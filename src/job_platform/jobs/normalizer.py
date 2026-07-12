"""Job normalization (docs/02D): consistent titles, countries, remote status,
plain-text descriptions, and stable internal identifiers."""

from __future__ import annotations

import html
import re

from job_platform.jobs.models import Job
from job_platform.shared.ids import stable_hash
from job_platform.shared.text import normalize_whitespace

_TAG = re.compile(r"<[^>]+>")
_BLOCK_TAG = re.compile(r"</?(?:p|div|br|li|ul|ol|h[1-6]|tr|td|th|table)[^>]*>", re.IGNORECASE)
_LOCATION_SEPARATOR = re.compile(r",|\s-\s|–|\||/")

_COUNTRIES = {
    "united states", "usa", "u.s.", "us", "canada", "united kingdom", "uk",
    "germany", "france", "netherlands", "ireland", "india", "australia",
    "singapore", "japan", "brazil", "mexico", "spain", "italy", "poland",
    "switzerland", "sweden", "israel",
}
_COUNTRY_DISPLAY = {
    "usa": "United States", "us": "United States", "u.s.": "United States",
    "uk": "United Kingdom",
}
_US_STATES = {
    "al", "ak", "az", "ar", "ca", "co", "ct", "de", "fl", "ga", "hi", "id",
    "il", "in", "ia", "ks", "ky", "la", "me", "md", "ma", "mi", "mn", "ms",
    "mo", "mt", "ne", "nv", "nh", "nj", "nm", "ny", "nc", "nd", "oh", "ok",
    "or", "pa", "ri", "sc", "sd", "tn", "tx", "ut", "vt", "va", "wa", "wv",
    "wi", "wy", "dc",
}


def html_to_text(value: str) -> str:
    """Convert ATS HTML descriptions to readable plain text."""
    text = html.unescape(value)
    text = _BLOCK_TAG.sub("\n", text)
    text = _TAG.sub("", text)
    lines = [normalize_whitespace(line) for line in text.splitlines()]
    return "\n".join(line for line in lines if line).strip()


def infer_country(location: str) -> str:
    """Best-effort country from a free-form location string."""
    if not location:
        return ""
    parts = [p.strip().lower() for p in _LOCATION_SEPARATOR.split(location) if p.strip()]
    for part in reversed(parts):
        if part in _COUNTRIES:
            return _COUNTRY_DISPLAY.get(part, part.title())
    last = parts[-1] if parts else ""
    # "Austin, TX" / "Austin, TX 78701" style locations are US
    state = last.split()[0] if last else ""
    if state in _US_STATES and len(parts) > 1:
        return "United States"
    if "remote" in parts[0] and len(parts) == 1:
        return ""
    return ""


def infer_remote_status(*fields: str) -> str:
    combined = " ".join(fields).lower()
    if "hybrid" in combined:
        return "hybrid"
    if "remote" in combined:
        return "remote"
    return "unknown"


def normalize_job(job: Job) -> Job:
    """Return a normalized copy of a raw adapter job."""
    title = normalize_whitespace(job.title)
    location = normalize_whitespace(job.location)
    country = job.country or infer_country(location)
    remote = (
        job.remote_status
        if job.remote_status not in ("", "unknown")
        else infer_remote_status(title, location)
    )
    internal_id = job.id or "job_" + stable_hash(job.company, title, location, job.job_id or job.url)
    return job.model_copy(
        update={
            "id": internal_id,
            "title": title,
            "location": location,
            "country": country,
            "remote_status": remote,
        }
    )
