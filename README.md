# Job Platform

Local-first, LLM-powered job search and application platform. Claude performs
all reasoning (job analysis, ranking, tailoring, answers); this application
performs execution (discovery, orchestration, storage, browser automation).

Full specifications live in [docs/](docs/).

## Status

Implemented so far (Phases 0–11 of the [roadmap](docs/17%20-%20Implementation%20Roadmap,%20Milestones,%20and%20Delivery_plan.md)) — **hardened Review-Mode Beta**:

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
- Application review (docs/07D-1): deterministic cross-artifact checks —
  package integrity, staleness, job identity, cross-company contamination,
  candidate-fact drift, work-authorization contradictions
- Application readiness (docs/07D-2): staged gating with structured checks,
  duplicate detection, refresh detection, next-allowed-action guidance
- Manual handoff (Local Alpha): manual-completion checklist with sensitive-
  answer flags, per-answer editing with optional save-for-reuse, manual
  submission recording with accurate source attribution
- Browser automation foundation (docs/06): Playwright/Chromium with
  persistent profiles, URL trust policy, structured form extraction,
  verified action primitives (fill/select/radio/checkbox/upload), page
  progression verification, CAPTCHA/login/MFA pause detection, crash
  recovery via execution state, screenshot evidence — no submit capability
  yet, tested against local synthetic forms in local_test_sites/
- Generic Form Engine (docs/09): form boundary detection (application vs
  search/newsletter/login forms), deterministic semantic field classification
  with provider fallback for unknowns, prepared-answer mapping with
  confidence gating (high=auto, medium=review, low=user), dynamic
  conditional-field rounds, review-page detection, and ambiguous-final-action
  protection — the engine never clicks submit
- Greenhouse ATS adapter (docs/09, beta): multi-signal detection (domain,
  embedded iframe, page signature), page classification, job-identity
  extraction, exact field-id semantics, submission-control identification
  (never clicked), simulated confirmation verification, registry with
  priority resolution and safe generic fallback
- Queue and execution orchestration (docs/08): admission control with
  rejection reasons, sequential queue over one browser profile, durable
  workflow state machine (validation → lock → readiness → browser →
  navigation → identity check → form execution) persisted after every stage,
  package and profile file locks with stale-lock recovery, bounded retries,
  crash recovery that never repeats completed actions, failure isolation,
  pause/resume/cancel/skip, event stream, restart recovery
- Submission verification and history (docs/10): the irreversible-action
  boundary — pre-submission snapshot, submission lock reconciled against
  attempt records, durable attempt before the click, one-click-only
  enforcement with no click retry, evidence-graded verification (weak
  evidence becomes the protected Submission Unknown state), confirmation
  number extraction, user resolution of unknown outcomes, append-only
  history events, and idempotent CSV/XLSX synchronization where the CSV is
  the source of truth and the workbook is always rebuildable
- Review-mode release (docs/17 Phase 10): user approval bound to exact
  artifact fingerprints and the reviewed form snapshot, verified again
  immediately before submission; approved-submission workflow (approval
  check → fresh refill → final click → verification → history); local
  backups; audit-trail integrity checks; and a local dashboard at
  http://localhost:8000/ covering the full workflow
- Security, operations, and UX hardening (docs/12, docs/17 Phase 11):
  secret redaction in logs, prompt-injection detection wired into review and
  form filling, hard-blocking of government-ID/payment/password fields,
  localhost-only API with CSRF origin checks and a strict CSP, backup/restore
  with pre-restore safety copy, migration framework with automatic rollback,
  low-disk submission guard, hash-chained tamper-evident audit trail,
  aggregated system health, and a sanitized (secret-free) diagnostic bundle
- Local FastAPI service exposing the complete loop: discover → rank →
  prepare → review → readiness → queue → review-mode execution →
  approve → submit → verify → history

Not yet implemented: limited automatic mode (Phase 12), additional ATS
adapters (Phase 13).

## Quick start

```bash
# 1. Install dependencies (Python 3.11+) and the browser runtime
uv sync --group dev
uv run playwright install chromium

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
