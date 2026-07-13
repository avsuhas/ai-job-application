# Automatic Mode — Incident Runbook

Operational guide for the limited automatic-submission feature (roadmap
Phase 12). Automatic mode is **disabled by default** and gated behind an
explicit opt-in, adapter/company allowlists, and per-day limits.

## Emergency stop (kill switch)

If automatic mode is misbehaving, stop all future automatic submissions
immediately:

```
POST /api/automatic-mode/kill   { "reason": "<why>" }
```

The kill switch is a persistent file (`user_data/automatic_mode.killed`).
While engaged, every eligibility check returns "downgrade to review" — no
automatic submission can occur regardless of settings. It survives restarts.
Release only after the cause is understood:

```
POST /api/automatic-mode/release
```

A workflow already mid-submission is not interrupted by the kill switch (the
final click is atomic and never retried); the switch prevents the **next**
automatic submission.

## Disabling automatic mode entirely

```
PUT /api/automatic-mode   { "enabled": false }
```

New automatic queues are rejected while disabled. Existing review-mode
workflows are unaffected.

## What automatic mode guarantees

- **Never enabled accidentally** — off by default, requires explicit enable
  plus a Stable, allowlisted adapter (Greenhouse is currently Beta, so it is
  refused until promoted).
- **One final click** — the submission service persists the attempt before the
  click and refuses a second attempt on the same package; there is no click
  retry.
- **Strong verification required** — only conclusive/strong evidence with
  verified job identity marks a submission Submitted; weak evidence becomes
  Submission Unknown, which pauses the queue and blocks re-submission.
- **Automatic downgrade to Review** whenever any precondition fails: non-Stable
  or unmatched adapter, review warnings beyond policy, stale candidate data,
  duplicate, low final-control confidence, an unknown/sensitive/injection
  field, or the kill switch.

## Diagnosing an incident

1. **Metrics** — `GET /api/automatic-mode/metrics` shows counts of
   `auto_submitted`, `downgraded_to_review`, `blocked`, and `unknown_outcomes`.
2. **Audit trail** — `GET /api/system/audit` verifies the hash-chained history
   log is intact. `GET /api/history/events` lists every `auto_*` event with the
   reason.
3. **Submission Unknown** — `GET /api/applications/{id}/submission` shows the
   unresolved outcome; resolve it via
   `POST /api/applications/{id}/submission/resolve` after checking the ATS.
4. **System health** — `GET /api/system/health` flags degraded components.

## Recovery

- **Duplicate suspicion**: the tracker duplicate check runs immediately before
  every submission; a matched job downgrades, so duplicates cannot be
  auto-submitted. Verify with `GET /api/history`.
- **Corrupt history/workbook**: `GET /api/history/export` rebuilds the XLSX
  from the CSV source of truth.
- **Bad data state**: restore the latest backup with
  `POST /api/system/restore` (a pre-restore safety copy is taken automatically).

## Limits

Daily and per-company caps are counted from the durable tracker, so they hold
across restarts. Tune via `PUT /api/automatic-mode`
(`daily_limit`, `per_company_daily_limit`). Reaching a limit downgrades further
packages to review rather than blocking the queue.
