"""Validate the local Candidate Knowledge Base and print a readable report."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from job_platform.candidate.validator import validate_candidate_dir  # noqa: E402
from job_platform.shared.config import load_settings  # noqa: E402


def main() -> int:
    settings = load_settings()
    candidate_dir = settings.paths.candidate_dir
    print(f"Validating candidate data in {candidate_dir}\n")
    report = validate_candidate_dir(candidate_dir)

    for issue in report.errors:
        print(f"  ERROR   [{issue.code}] {issue.message}")
    for issue in report.warnings:
        print(f"  warning [{issue.code}] {issue.message}")
    if not report.issues:
        print("  No issues found.")

    print(f"\n{'PASS' if report.ok else 'FAIL'}: {len(report.errors)} error(s), "
          f"{len(report.warnings)} warning(s)")
    return 0 if report.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
