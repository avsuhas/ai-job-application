# Job Platform

Local-first, LLM-powered job search and application platform. Claude performs
all reasoning (job analysis, ranking, tailoring, answers); this application
performs execution (discovery, orchestration, storage, browser automation).

Full specifications live in [docs/](docs/).

## Status

Implemented so far (Phases 0–3 of the [roadmap](docs/17%20-%20Implementation%20Roadmap,%20Milestones,%20and%20Delivery_plan.md)):

- Project foundation: configuration, structured logging, atomic file storage
- Candidate Knowledge Base loading, validation, and provider context building
- Reasoning provider abstraction with Claude implementation and mock provider
- Job discovery via Greenhouse and Lever adapters, normalization, deduplication
- Deterministic eligibility filtering plus Claude-based job ranking
- CSV application tracker with duplicate detection
- Application Packages (docs/07A): versioned manifests, immutable job and
  candidate snapshots, artifact fingerprints, staleness detection
- Resume preparation (docs/07B): base resume selection, provider tailoring,
  deterministic factual validation with fallback to the base resume
- Cover letters (docs/07C-1): policy-driven requirement detection, generation,
  company/role validation
- Standard application answers (docs/07C-2): deterministic resolution from the
  CKB with source attribution, provider narratives, explicit unresolved list
- Local FastAPI service exposing the full discover → rank → prepare workflow

Not yet implemented: review/readiness services (Phase 4), browser automation
(Playwright, Phase 5+), form engine, ATS submission adapters, frontend.

## Quick start

```bash
# 1. Install dependencies (Python 3.11+)
uv sync --group dev

# 2. Configure secrets
cp .env.example .env   # add ANTHROPIC_API_KEY and REASONING__MODEL

# 3. Create local data folders + candidate templates
uv run python scripts/initialize_user_data.py

# 4. Edit user_data/candidate/profile/* and drop resumes into
#    user_data/candidate/resume/, then validate:
uv run python scripts/validate_candidate_data.py

# 5. Run the API
uv run uvicorn job_platform.api.app:create_app --factory --reload
# open http://localhost:8000/docs

# 6. Run tests
uv run pytest
```

## Layout

```
src/job_platform/   backend package (shared, candidate, jobs, ranking,
                    providers, storage, api)
prompts/            versioned prompt templates
config/             non-secret app configuration (settings.json, companies.json)
user_data/          local candidate data — never committed
fixtures/           synthetic test data
tests/              unit and API tests
docs/               full product and architecture specifications
```

## Security notes

- `user_data/` (candidate data, browser profiles, logs, tracker) is git-ignored.
- Secrets live only in `.env` (git-ignored).
- Job descriptions and web content are treated as untrusted input and clearly
  delimited before being sent to the reasoning provider.
