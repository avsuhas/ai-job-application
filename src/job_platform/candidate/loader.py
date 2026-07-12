"""Candidate Knowledge Base loader.

Loads structured facts (candidate.json), free-form profile documents
(rules.md, preferences.md, answers.md, notes.md, and any additional supported
files), and base resumes with extracted text. Files are user-owned: the loader
only reads, never mutates (docs/02C).
"""

from __future__ import annotations

import json
from pathlib import Path

from pypdf import PdfReader

from job_platform.candidate.models import CandidateBundle, CandidateProfile, ResumeDocument
from job_platform.shared.errors import CandidateDataError
from job_platform.shared.logging import get_logger
from job_platform.shared.text import slugify

logger = get_logger("candidate.loader")

PROFILE_TEXT_SUFFIXES = {".md", ".txt", ".yaml", ".yml"}
RESUME_SUFFIXES = {".pdf", ".txt", ".md", ".docx"}


def _extract_pdf_text(path: Path) -> str:
    reader = PdfReader(str(path))
    return "\n".join(page.extract_text() or "" for page in reader.pages).strip()


def _extract_resume_text(path: Path) -> tuple[str, str | None]:
    """Return (text, error). Extraction failure is a warning, not a crash."""
    try:
        if path.suffix.lower() == ".pdf":
            return _extract_pdf_text(path), None
        if path.suffix.lower() in {".txt", ".md"}:
            return path.read_text(encoding="utf-8").strip(), None
        return "", f"Text extraction not supported for {path.suffix} yet"
    except Exception as exc:  # noqa: BLE001 - report any parser failure as data issue
        return "", f"Failed to extract text from {path.name}: {exc}"


def load_candidate_profile(profile_dir: Path) -> CandidateProfile:
    candidate_json = profile_dir / "candidate.json"
    if not candidate_json.exists():
        return CandidateProfile()
    try:
        data = json.loads(candidate_json.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise CandidateDataError(
            f"The candidate profile could not be loaded because candidate.json "
            f"contains invalid JSON near line {exc.lineno}.",
            details={"path": str(candidate_json), "error": str(exc)},
        ) from exc
    return CandidateProfile.model_validate(data)


def load_profile_documents(profile_dir: Path) -> dict[str, str]:
    documents: dict[str, str] = {}
    if not profile_dir.exists():
        return documents
    for path in sorted(profile_dir.iterdir()):
        if path.suffix.lower() in PROFILE_TEXT_SUFFIXES and path.is_file():
            documents[path.stem] = path.read_text(encoding="utf-8").strip()
    return documents


def load_resumes(resume_dir: Path) -> list[ResumeDocument]:
    resumes: list[ResumeDocument] = []
    if not resume_dir.exists():
        return resumes
    for path in sorted(resume_dir.iterdir()):
        if not path.is_file() or path.suffix.lower() not in RESUME_SUFFIXES:
            continue
        text, error = _extract_resume_text(path)
        if error:
            logger.warning("Resume text extraction issue: %s", error)
        resumes.append(
            ResumeDocument(
                id=slugify(path.stem),
                name=path.name,
                path=path,
                format=path.suffix.lower().lstrip("."),
                text=text,
                text_extraction_error=error,
            )
        )
    return resumes


def load_candidate_bundle(candidate_dir: Path) -> CandidateBundle:
    """Load the full CKB from ``user_data/candidate/``."""
    profile_dir = candidate_dir / "profile"
    return CandidateBundle(
        profile=load_candidate_profile(profile_dir),
        documents=load_profile_documents(profile_dir),
        resumes=load_resumes(candidate_dir / "resume"),
        source_dir=candidate_dir,
    )
