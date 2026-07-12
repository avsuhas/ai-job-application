"""Application Package storage (docs/07A).

Owns the on-disk package layout under ``user_data/applications/packages/``.
Every artifact write is atomic, fingerprinted, and versioned in the manifest.
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from job_platform.candidate.models import CandidateBundle
from job_platform.packages.models import ArtifactRecord, PackageManifest
from job_platform.shared.errors import StorageError
from job_platform.shared.files import atomic_write_text
from job_platform.shared.ids import sha256_text, stable_hash
from job_platform.shared.text import slugify

MANIFEST_FILENAME = "package.json"


def make_package_id(company: str, job_id: str, title: str, now: datetime | None = None) -> str:
    """{company_slug}_{job_id|title_hash}_{created_timestamp} (docs/07A)."""
    now = now or datetime.now(UTC)
    timestamp = now.strftime("%Y%m%dT%H%M%S")
    middle = slugify(job_id) if job_id else stable_hash(title)[:8]
    return f"{slugify(company)}_{middle}_{timestamp}"


def candidate_source_fingerprints(bundle: CandidateBundle) -> dict[str, str]:
    """Hashes of the candidate sources a package was prepared from."""
    fingerprints: dict[str, str] = {}
    for name, content in sorted(bundle.documents.items()):
        fingerprints[f"profile/{name}"] = sha256_text(content)
    fingerprints["profile/candidate.json"] = sha256_text(bundle.profile.model_dump_json())
    for resume in bundle.resumes:
        fingerprints[f"resume/{resume.name}"] = sha256_text(resume.text)
    return fingerprints


class PackageStore:
    def __init__(self, packages_dir: Path) -> None:
        self._dir = packages_dir

    def package_dir(self, package_id: str) -> Path:
        safe = "".join(c for c in package_id if c.isalnum() or c in "_-")
        if not safe:
            raise StorageError("Invalid package id.", details={"package_id": package_id})
        return self._dir / safe

    def _artifact_path(self, package_id: str, relative_path: str) -> Path:
        """Resolve an artifact path, refusing escapes from the package dir."""
        base = self.package_dir(package_id).resolve()
        target = (base / relative_path).resolve()
        if not target.is_relative_to(base):
            raise StorageError(
                "Artifact path escapes the package directory.",
                details={"package_id": package_id, "artifact": relative_path},
            )
        return target

    def save_manifest(self, manifest: PackageManifest) -> None:
        manifest.touch()
        path = self.package_dir(manifest.package_id) / MANIFEST_FILENAME
        atomic_write_text(path, manifest.model_dump_json(indent=2))

    def load_manifest(self, package_id: str) -> PackageManifest:
        path = self.package_dir(package_id) / MANIFEST_FILENAME
        if not path.exists():
            raise StorageError(
                f"Application package '{package_id}' was not found.",
                details={"package_id": package_id},
            )
        return PackageManifest.model_validate_json(path.read_text(encoding="utf-8"))

    def list_package_ids(self) -> list[str]:
        if not self._dir.exists():
            return []
        return sorted(
            p.name for p in self._dir.iterdir() if (p / MANIFEST_FILENAME).exists()
        )

    def write_artifact(
        self, manifest: PackageManifest, relative_path: str, content: str
    ) -> ArtifactRecord:
        """Write one artifact atomically and record its fingerprint/version."""
        target = self._artifact_path(manifest.package_id, relative_path)
        atomic_write_text(target, content)
        digest = sha256_text(content)
        existing = manifest.artifacts.get(relative_path)
        record = ArtifactRecord(
            path=relative_path,
            sha256=digest,
            version=existing.version + 1 if existing and existing.sha256 != digest else (
                existing.version if existing else 1
            ),
        )
        manifest.artifacts[relative_path] = record
        return record

    def read_artifact(self, package_id: str, relative_path: str) -> str:
        path = self._artifact_path(package_id, relative_path)
        if not path.exists():
            raise StorageError(
                f"Artifact '{relative_path}' not found in package '{package_id}'.",
                details={"package_id": package_id, "artifact": relative_path},
            )
        return path.read_text(encoding="utf-8")

    def stale_sources(self, manifest: PackageManifest, bundle: CandidateBundle) -> list[str]:
        """Candidate sources that changed since the package was prepared."""
        current = candidate_source_fingerprints(bundle)
        changed = []
        for source, digest in manifest.source_fingerprints.items():
            if current.get(source) != digest:
                changed.append(source)
        return sorted(changed)
