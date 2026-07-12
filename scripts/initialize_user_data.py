"""First-run initialization (docs/04 User Data Initialization).

Creates the local user_data layout, template candidate files, and an empty
application tracker. Safe to re-run: existing files are never overwritten.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from job_platform.shared.config import load_settings  # noqa: E402
from job_platform.shared.files import ensure_dir  # noqa: E402
from job_platform.storage.tracker import ApplicationTracker  # noqa: E402

CANDIDATE_TEMPLATE = {
    "personal": {
        "first_name": "",
        "last_name": "",
        "email": "",
        "phone": "",
        "address": "",
        "city": "",
        "state": "",
        "country": "",
        "postal_code": "",
    },
    "employment": {"current_company": "", "current_title": "", "years_of_experience": 0},
    "work_authorization": {
        "authorized_to_work": None,
        "requires_sponsorship": None,
        "visa_status": "",
    },
    "education": {"highest_degree": "", "university": ""},
}

TEMPLATES = {
    "preferences.md": (
        "Preferred Countries: \n\nPreferred Roles: \n\nRemote: \n\nPreferred Salary: \n"
    ),
    "rules.md": (
        "# Permanent rules Claude must follow when applying\n\n"
        "Example: Never apply to contract jobs.\n"
        "Example: Always answer sponsorship truthfully.\n"
    ),
    "answers.md": (
        "## Why do you want to work here?\n\n(your reusable answer)\n\n"
        "## Tell us about yourself\n\n(your reusable answer)\n"
    ),
    "notes.md": "Free-form notes Claude may use when relevant.\n",
}


def main() -> None:
    settings = load_settings()
    created: list[str] = []

    for directory in settings.paths.runtime_directories():
        if not directory.exists():
            created.append(str(directory))
        ensure_dir(directory)

    profile_dir = settings.paths.profile_dir
    candidate_json = profile_dir / "candidate.json"
    if not candidate_json.exists():
        candidate_json.write_text(json.dumps(CANDIDATE_TEMPLATE, indent=2))
        created.append(str(candidate_json))
    for name, content in TEMPLATES.items():
        path = profile_dir / name
        if not path.exists():
            path.write_text(content)
            created.append(str(path))

    tracker = ApplicationTracker(settings.paths.tracker_path)
    if not settings.paths.tracker_path.exists():
        created.append(str(settings.paths.tracker_path))
    tracker.initialize()

    if created:
        print("Created:")
        for path in created:
            print(f"  {path}")
    else:
        print("User data already initialized; nothing to do.")
    print(f"\nNext steps:\n  1. Edit {profile_dir}/candidate.json and the profile .md files")
    print(f"  2. Copy resumes into {settings.paths.resume_dir}")
    print("  3. Run: uv run python scripts/validate_candidate_data.py")


if __name__ == "__main__":
    main()
