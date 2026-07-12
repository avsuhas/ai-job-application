# 11 - Logging, Observability, and Audit Trails

## LLM-Powered Autonomous Job Search & Application Platform

Version: 1.0

---

# Purpose

This document defines the Logging, Observability, and Audit Trail system responsible for recording application behavior, workflow progress, errors, decisions, artifact changes, browser activity, reasoning-provider usage, submission evidence, and application-history updates.

The system must provide enough information to:

* Understand what the platform is doing.
* Diagnose failures.
* Recover interrupted workflows.
* Explain why an application advanced or stopped.
* Identify which candidate sources produced an answer.
* Identify which resume and cover letter versions were used.
* Reconstruct browser execution.
* Verify whether submission was attempted.
* Verify whether submission succeeded.
* Detect duplicate activity.
* Investigate privacy or security incidents.
* Measure reliability and performance.
* Preserve an auditable history without storing unnecessary sensitive data.

Logging should be structured, local-first, privacy-conscious, and correlated across all platform components.

The system should not rely on ad hoc text logs scattered across modules.

---

# Core Principle

Every important workflow action should produce a structured event that can be correlated with the relevant job, package, queue, workflow, browser session, and submission attempt.

```text id="uyzpcm"
User Action
    |
    v
Workflow Operation
    |
    v
Structured Event
    |
    +--> Component Log
    +--> Package Audit Trail
    +--> Metrics
    +--> User Progress Event
    +--> Recovery State
```

Logging must support understanding and recovery without exposing unnecessary candidate information.

---

# Objectives

The system should:

* Use structured logs.
* Use consistent event schemas.
* Assign stable correlation identifiers.
* Separate user-visible progress from technical diagnostics.
* Record workflow-state transitions.
* Record package changes.
* Record reasoning-provider requests and results without exposing sensitive content.
* Record browser actions and verification outcomes.
* Record user interventions.
* Record submission attempts and outcomes.
* Record application-history synchronization.
* Record security-relevant events.
* Redact sensitive values.
* Support configurable log levels.
* Rotate and retain logs locally.
* Support local metrics and dashboards.
* Support workflow tracing.
* Preserve append-only audit events.
* Detect missing or contradictory audit records.
* Support crash recovery.
* Avoid full raw-page or prompt logging by default.
* Allow users to inspect, export, and delete local records.

---

# Scope

This document covers:

* Structured application logs.
* Component logs.
* Package-specific logs.
* Queue logs.
* Workflow traces.
* Browser-action logs.
* Reasoning-provider usage logs.
* User-intervention logs.
* Submission audit trails.
* Application-history audit trails.
* Metrics.
* Health signals.
* Error reporting.
* Log redaction.
* Data retention.
* Log rotation.
* Integrity validation.
* Local dashboards.
* Export.
* Testing.

This document does not define:

* Cloud telemetry.
* Third-party analytics.
* Public monitoring services.
* Candidate-answer generation.
* Browser implementation details.
* Application-history schemas except where required for auditing.

The MVP should not require external logging or monitoring infrastructure.

---

# System Components

```text id="adlnxp"
Logging and Observability System
    |
    +-- Structured Logger
    +-- Event Schema Registry
    +-- Correlation Context Manager
    +-- Package Audit Writer
    +-- Workflow Trace Manager
    +-- Metrics Collector
    +-- Health Monitor
    +-- Redaction and Sanitization Service
    +-- Log Rotation Manager
    +-- Retention Manager
    +-- Audit Integrity Validator
    +-- Diagnostic Bundle Generator
    +-- Local Observability Dashboard
```

---

# Separation of Responsibilities

## Structured Logger

Writes technical events using a consistent schema.

## Package Audit Writer

Maintains package-specific append-only audit events.

## Workflow Trace Manager

Links related operations across services.

## Metrics Collector

Aggregates counts, timings, and rates.

## Health Monitor

Reports the operational condition of components.

## Redaction Service

Prevents sensitive data from entering logs.

## Retention Manager

Deletes or archives logs according to user settings.

## Audit Integrity Validator

Detects missing, altered, or inconsistent audit records.

## Progress Reporter

Produces concise user-visible updates.

User progress messages and technical logs should not be treated as the same output.

---

# Logging Principles

The platform should follow these principles:

1. Structured over unstructured.
2. Local-first by default.
3. Data minimization.
4. Correlation across services.
5. Append-only audit events.
6. Explicit state transitions.
7. Deterministic event naming.
8. Safe redaction.
9. Bounded retention.
10. No silent workflow failures.
11. No secrets in logs.
12. No raw reasoning traces.
13. No full prompt or candidate-profile logging by default.
14. No claim of success without recorded evidence.

---

# Log Categories

The system should maintain several categories of logs.

```text id="qxyxip"
application
package
queue
workflow
browser
ats_adapter
reasoning_provider
review
readiness
submission
history
security
performance
health
user_intervention
```

---

# Application Logs

Application logs describe platform-wide operations.

Examples:

* Application startup.
* Configuration loading.
* Component initialization.
* Graceful shutdown.
* Unexpected shutdown.
* Schema migration.
* Health-check completion.
* Global configuration changes.

---

# Package Logs

Package logs describe one Application Package.

Examples:

* Package created.
* Job snapshot stored.
* Candidate context loaded.
* Resume selected.
* Resume generated.
* Cover letter generated.
* Answers prepared.
* Readiness evaluated.
* Package queued.
* Package execution started.
* Package submitted.
* Package archived.

---

# Queue Logs

Queue logs describe:

* Queue creation.
* Queue validation.
* Item admission.
* Queue ordering.
* Queue start.
* Queue pause.
* Queue resume.
* Item completion.
* Queue cancellation.
* Queue completion.

---

# Workflow Logs

Workflow logs describe stage execution.

Examples:

* Stage started.
* Stage completed.
* Stage failed.
* Retry initiated.
* Checkpoint written.
* User action required.
* Recovery started.
* Recovery completed.

---

# Browser Logs

Browser logs describe high-level browser activity.

Examples:

* Browser launched.
* Profile loaded.
* Application page opened.
* Page classified.
* Form inspected.
* Field interaction attempted.
* Field verification passed.
* File uploaded.
* Page progression verified.
* Browser crashed.
* Session expired.
* CAPTCHA detected.

Browser logs should not record full field values by default.

---

# ATS Adapter Logs

ATS adapter logs describe:

* ATS detection.
* Adapter selection.
* Adapter version.
* Capability resolution.
* Page-signature match.
* Generic fallback.
* Adapter degradation.
* Unsupported workflow.
* Submission-signal interpretation.

---

# Reasoning-Provider Logs

Reasoning-provider logs describe:

* Provider.
* Model.
* Prompt template.
* Prompt version.
* Request purpose.
* Request size.
* Response status.
* Structured-output validation.
* Retry count.
* Duration.
* Token usage when available.
* Cache usage.
* Fallback-provider usage.

They should not contain raw hidden reasoning or unrestricted prompts by default.

---

# Review and Readiness Logs

These should record:

* Review stage.
* Checks performed.
* Finding counts.
* Blocking issues.
* Warnings.
* Corrections.
* Approval decision.
* Readiness stage.
* Readiness result.
* Refresh requirements.
* Queue-admission decision.

---

# Submission Logs

Submission logs should record:

* Pre-submission snapshot creation.
* Submission lock acquisition.
* Submission-attempt creation.
* Final-click initiation.
* Verification start.
* Evidence collection.
* Outcome classification.
* Confirmation identifiers.
* Submission Unknown state.
* Resolution of unknown outcomes.

---

# Application-History Logs

History logs should record:

* History record creation.
* History event creation.
* CSV synchronization.
* XLSX synchronization.
* Tracker backup.
* Tracker reconciliation.
* Manual status update.
* Duplicate detection.
* Status correction.
* Import and export.

---

# Security Logs

Security-relevant events include:

* Unexpected navigation domain.
* Sensitive field encountered.
* Unauthorized local-file path request.
* Prompt-injection content detected.
* Credential logging prevented.
* Browser-profile conflict.
* Invalid file path.
* Package-integrity failure.
* Audit-integrity failure.
* Permission error.
* Suspicious external redirect.

Security logs should remain local and should not expose the sensitive value involved.

---

# Log Levels

Supported levels:

```text id="837lyy"
TRACE
DEBUG
INFO
WARNING
ERROR
CRITICAL
AUDIT
```

---

## TRACE

Highly detailed operational events.

Examples:

* Selector candidates evaluated.
* Page-stability signals.
* Field-classification candidates.
* Internal retry decisions.

TRACE should be disabled by default.

---

## DEBUG

Detailed diagnostic information useful during development or troubleshooting.

Examples:

* Adapter-selection details.
* Form-model summaries.
* Cache decisions.
* Retry context.

---

## INFO

Normal significant workflow events.

Examples:

* Package created.
* Browser opened.
* Page completed.
* Review approved.
* Submission verified.

---

## WARNING

Unexpected but recoverable conditions.

Examples:

* Generic fallback activated.
* Optional answer unavailable.
* Adapter degraded.
* Tracker synchronization delayed.

---

## ERROR

An operation failed.

Examples:

* Resume rendering failed.
* Browser navigation failed.
* Required answer unresolved.
* CSV write failed.

---

## CRITICAL

The platform cannot continue safely.

Examples:

* Package storage unavailable.
* Audit data corrupted.
* Browser profile unrecoverable.
* Submission state cannot be reconciled after a final click.

---

## AUDIT

A business-significant, security-significant, or historically significant event.

Examples:

* Candidate rule changed.
* Application submitted.
* Duplicate override approved.
* Legal answer changed.
* User approved submission.
* History record corrected.
* Sensitive-data policy changed.

AUDIT is a category with persistence requirements, not merely a severity.

---

# Structured Log Event Model

Every technical log event should follow a consistent schema.

```json id="dcgx5y"
{
  "schema_version": "1.0",
  "event_id": "evt_01",
  "event_name": "browser.page_completed",
  "level": "INFO",
  "category": "browser",
  "message": "Application page completed and verified.",
  "timestamp": "2026-07-12T12:00:00-04:00",
  "sequence": 142,
  "application_instance_id": "",
  "candidate_profile_id": "",
  "queue_id": "",
  "queue_item_id": "",
  "package_id": "",
  "workflow_id": "",
  "stage": "page_validation",
  "page_id": "personal_information",
  "submission_attempt_id": null,
  "component": "browser_service",
  "component_version": "1.0.0",
  "duration_ms": 820,
  "status": "success",
  "metadata": {},
  "error": null
}
```

---

# Required Event Fields

Every event should include:

* Schema version.
* Event ID.
* Event name.
* Timestamp.
* Sequence.
* Level.
* Category.
* Component.
* Status.
* Message.

Include correlation identifiers when available.

---

# Event Naming Convention

Use hierarchical event names.

Examples:

```text id="zxrs8i"
application.started
application.shutdown

package.created
package.updated
package.stale_detected

queue.created
queue.item_admitted
queue.completed

workflow.stage_started
workflow.stage_completed
workflow.retry_started

browser.page_opened
browser.field_filled
browser.field_verified
browser.upload_completed

review.completed
readiness.failed

submission.attempt_created
submission.click_initiated
submission.verified
submission.unknown

history.csv_synced
history.xlsx_sync_failed
```

Event names should be stable and documented.

---

# Event Statuses

Supported statuses:

```text id="vl9rv5"
started
success
success_with_warnings
failed
blocked
cancelled
waiting
unknown
```

---

# Correlation Identifiers

The logging system should support these identifiers:

```text id="m4hwmn"
application_instance_id
candidate_profile_id
job_id
package_id
queue_id
queue_item_id
workflow_id
browser_session_id
browser_page_id
ats_adapter_id
review_id
readiness_id
submission_attempt_id
history_record_id
user_intervention_id
provider_request_id
```

---

# Correlation Context

Services should receive or derive a correlation context.

Example:

```json id="j6bn2o"
{
  "application_instance_id": "",
  "candidate_profile_id": "default",
  "package_id": "",
  "queue_id": "",
  "workflow_id": "",
  "browser_session_id": "",
  "ats_adapter_id": "greenhouse"
}
```

Every service event should inherit available identifiers automatically.

---

# Application Instance ID

A new ID should be created each time the local platform starts.

This helps distinguish:

* Events before and after a restart.
* Multiple running instances.
* Crash recovery.
* Stale lock ownership.

---

# Workflow Trace

A workflow trace represents the complete execution of one Application Package.

```text id="p7ap8j"
Package Preparation
    |
    v
Readiness
    |
    v
Queue Admission
    |
    v
Browser Execution
    |
    v
Review
    |
    v
Submission
    |
    v
History Synchronization
```

---

# Trace Model

```json id="56coo3"
{
  "trace_id": "",
  "package_id": "",
  "workflow_id": "",
  "started_at": "",
  "completed_at": null,
  "current_stage": "",
  "status": "running",
  "spans": []
}
```

---

# Trace Span

Each meaningful operation may create a span.

```json id="yszykd"
{
  "span_id": "",
  "parent_span_id": null,
  "operation": "browser.complete_page",
  "component": "browser_service",
  "started_at": "",
  "completed_at": "",
  "duration_ms": 4600,
  "status": "success",
  "attributes": {}
}
```

---

# Recommended Trace Spans

* Load package.
* Evaluate readiness.
* Acquire lock.
* Launch browser.
* Navigate application.
* Inspect page.
* Resolve answers.
* Execute page.
* Validate page.
* Upload document.
* Run review.
* Await user action.
* Submit.
* Verify submission.
* Synchronize history.

---

# Trace Storage

Recommended:

```text id="ndy10m"
applications/packages/{package_id}/logs/trace.json
```

or append-only:

```text id="6qo5ys"
applications/packages/{package_id}/logs/spans.jsonl
```

---

# Package Audit Trail

Each Application Package should maintain its own append-only audit trail.

Recommended:

```text id="2h5v4v"
applications/packages/{package_id}/logs/audit.jsonl
```

---

# Audit Event Model

```json id="mfnbs1"
{
  "audit_event_id": "",
  "schema_version": "1.0",
  "package_id": "",
  "event_type": "answer.user_modified",
  "actor_type": "user",
  "actor_id": "local_user",
  "artifact": "answers/prepared_answers.json",
  "artifact_version_before": 1,
  "artifact_version_after": 2,
  "change_summary": "Updated expected start date.",
  "reason": "",
  "timestamp": "",
  "previous_event_hash": "",
  "event_hash": ""
}
```

---

# Audit Actor Types

```text id="7q6yqe"
user
system
reasoning_provider
browser
ats_adapter
import
reconciliation
```

The reasoning provider should not be described as an autonomous legal actor.

It is the source of generated output within a system-controlled workflow.

---

# Required Audit Events

Audit events should be created for:

* Package creation.
* Candidate-context snapshot creation.
* Candidate rule used.
* Resume selection.
* Resume generation.
* Resume user edit.
* Cover-letter generation.
* Cover-letter user edit.
* Application-answer generation.
* Sensitive-answer change.
* Legal-answer change.
* Demographic preference change.
* Readiness decision.
* Review approval.
* User approval.
* Duplicate override.
* Submission attempt.
* Submission verification.
* Submission Unknown resolution.
* History correction.
* Package archive or deletion.

---

# Audit Trail Immutability

Audit events should be append-only.

Do not silently:

* Modify existing audit events.
* Remove user approvals.
* Replace submission evidence.
* Rewrite earlier status transitions.

Corrections should create new audit events.

---

# Tamper-Evident Audit Chain

The platform may use a hash chain.

Each event stores:

```text id="hc0hy1"
previous_event_hash
event_hash
```

The event hash should be calculated from normalized event content and the previous hash.

This does not prevent file modification, but it helps detect it.

---

# Audit Integrity Check

The integrity validator should verify:

* Event sequence.
* Event IDs are unique.
* Hash chain is valid.
* Required audit events exist.
* Package state agrees with audit state.
* Submission records agree with submission audit events.
* History corrections have corresponding audit events.

---

# Integrity Result

```json id="l8yhwx"
{
  "package_id": "",
  "status": "passed",
  "events_checked": 84,
  "hash_chain_valid": true,
  "missing_required_events": [],
  "sequence_gaps": [],
  "warnings": []
}
```

---

# Integrity Failure

When audit integrity fails:

* Do not delete evidence.
* Mark the package for review.
* Prevent automatic submission when integrity is material.
* Preserve current files.
* Record the failure in a separate system log.
* Allow reconstruction from package files when possible.
* Require user acknowledgment for unresolved inconsistencies.

---

# User-Visible Progress Events

Progress events should be concise and human-readable.

Examples:

```text id="96ikig"
Opening the application.

Uploading the approved resume.

Completing the work-history section.

Waiting for CAPTCHA completion.

Application review passed.

Submission verified.
```

Progress events should not expose:

* Salary answers.
* Visa details.
* Demographic values.
* Legal answers.
* Passwords.
* Full narrative responses.

---

# Progress Event Model

```json id="sbw29p"
{
  "event_type": "progress",
  "package_id": "",
  "workflow_id": "",
  "message": "Completed page 3 of the application.",
  "stage": "page_progression",
  "queue_position": 2,
  "queue_total": 7,
  "page_number": 3,
  "timestamp": ""
}
```

---

# Progress vs Diagnostic Logging

## Progress

Designed for the user.

* Concise.
* Safe.
* Outcome-focused.
* Minimal technical detail.

## Diagnostics

Designed for troubleshooting.

* Structured.
* Component-specific.
* May include error categories and timings.
* Still redacted.

The user interface should not display raw technical logs by default.

---

# Browser Event Logging

High-level browser actions should be logged.

Example:

```json id="cg76yk"
{
  "event_name": "browser.field_interaction",
  "field_id": "future_sponsorship",
  "semantic_type": "work_authorization.sponsorship_future",
  "action": "select_radio",
  "result": "verified",
  "value_logging": "redacted",
  "retry_count": 0
}
```

---

# Browser Value Logging Policy

Possible policies:

```text id="4mb55r"
none
redacted
hashed
category_only
full
```

Recommended defaults:

* Personal contact values: redacted.
* Legal and demographic values: category only.
* Sensitive identifiers: none.
* Non-sensitive dropdowns: category only.
* Job and company information: full.
* Debug full values: disabled by default.

---

# Field Value Hashing

When comparison is required without storing the value, a local hash may be stored.

Example:

```json id="gdmeho"
{
  "field_id": "email",
  "value_hash": "",
  "hash_scope": "package_local"
}
```

Hashes should not be used for low-entropy values such as Yes or No when they would reveal the answer easily.

---

# File Upload Logging

Record:

* Document type.
* Package-relative path.
* Filename.
* File hash.
* Upload result.
* Verification result.
* File size.
* ATS field ID.

Do not log arbitrary source-directory paths unnecessarily.

---

# File Upload Event

```json id="1b9jfe"
{
  "event_name": "browser.file_uploaded",
  "document_type": "resume",
  "filename": "Suhas_Arudi_Google_Resume.pdf",
  "file_hash": "",
  "field_id": "resume_upload",
  "verified": true
}
```

---

# Page Snapshot Logging

The system may record a sanitized page summary.

Recommended summary:

* URL domain.
* Page title.
* Page type.
* ATS.
* Field count.
* Required-field count.
* Validation-error count.
* Screenshot path.
* Page signature.

Avoid storing full raw HTML by default.

---

# Raw HTML Policy

Raw HTML should be captured only when:

* Explicitly enabled for debugging.
* Required to diagnose an adapter regression.
* Sensitive fields can be redacted.
* Retention is short.
* The user is informed through settings.

Raw HTML should never be sent automatically to a remote provider.

---

# Screenshot Logging

Screenshot events should record:

* Screenshot type.
* Page type.
* Package ID.
* Relative path.
* Reason.
* Redaction status.
* Retention category.
* Timestamp.

---

# Screenshot Types

```text id="dwyxyv"
page_opened
before_submit
after_submit
validation_error
captcha
login_required
unexpected_page
browser_error
confirmation
manual_review
```

---

# Screenshot Redaction

When feasible, redact or avoid capturing:

* Password fields.
* Government IDs.
* Demographic answers.
* Salary answers.
* Full address.
* Legal-history details.

Automatic screenshot redaction may be deferred, but storage and retention controls are mandatory.

---

# Reasoning-Provider Observability

The system should log each provider request at a metadata level.

---

# Provider Request Event

```json id="i6kx6l"
{
  "event_name": "reasoning.request_completed",
  "provider_request_id": "",
  "provider": "claude",
  "model": "",
  "purpose": "narrative_answer_generation",
  "prompt_name": "application_answer",
  "prompt_version": "1.2",
  "input_character_count": 4200,
  "output_character_count": 950,
  "token_usage": {},
  "cache_status": "miss",
  "structured_output_valid": true,
  "retry_count": 0,
  "duration_ms": 2400,
  "status": "success"
}
```

---

# Provider Request Content Policy

Do not log by default:

* Full prompt.
* Full response.
* Hidden reasoning.
* Full resume text.
* Full candidate context.
* Sensitive answers.
* Job-page raw HTML.

Permitted metadata:

* Prompt template ID.
* Prompt version.
* Content hashes.
* Input size.
* Output size.
* Structured-output status.
* Model.
* Duration.
* Token usage.

---

# Provider Content Snapshots

Optional debugging may store minimized prompt and response snapshots when:

* Explicitly enabled.
* Stored locally.
* Sensitive fields are removed.
* Retention is short.
* Production automatic execution does not depend on them.

---

# Structured Output Validation Logging

Record:

* Schema name.
* Schema version.
* Validation result.
* Missing fields.
* Invalid enum values.
* Repair attempt count.
* Final acceptance status.

---

# Provider Retry Logging

Each retry should record:

* Retry reason.
* Previous error.
* Attempt count.
* Whether the prompt changed.
* Whether a fallback model was used.
* Final result.

---

# Provider Fallback Audit

When switching models or providers:

* Record original provider.
* Record fallback provider.
* Record reason.
* Confirm candidate facts remain unchanged.
* Rerun validation.
* Record final model used for active artifact.

---

# Review Logging

Review events should include:

* Review ID.
* Review stage.
* Artifact versions.
* Check counts.
* Blocking findings.
* Warning counts.
* Correction rounds.
* Approval mode.
* Approval result.

Do not include full sensitive answer content.

---

# Review Finding Event

```json id="buaeob"
{
  "event_name": "review.finding_detected",
  "review_id": "",
  "finding_id": "",
  "category": "work_authorization_contradiction",
  "severity": "blocking",
  "artifact": "browser_form",
  "automatically_correctable": true
}
```

---

# Readiness Logging

Readiness events should record:

* Stage.
* Result.
* Required checks.
* Failed checks.
* Warnings.
* Refresh causes.
* Next allowed action.
* Queue-admission decision.

---

# User Intervention Logging

Record:

* Intervention category.
* Creation time.
* Message category.
* Whether sensitive.
* Presentation time.
* Completion time.
* Result.
* Resume stage.
* Whether answer was saved for reuse.

Do not log the sensitive answer unless required by package data rules.

---

# User Intervention Event

```json id="vhzuie"
{
  "event_name": "intervention.completed",
  "user_intervention_id": "",
  "category": "captcha_required",
  "result": "completed",
  "resume_stage": "page_inspection",
  "duration_ms": 42000
}
```

---

# Submission Audit Logging

Submission events require strict durability.

Required events:

```text id="xxm66u"
submission.snapshot_created
submission.lock_acquired
submission.attempt_created
submission.click_initiated
submission.verification_started
submission.evidence_collected
submission.verified
submission.failed
submission.unknown
submission.unknown_resolved
submission.lock_released
```

---

# Submission Event Ordering

The audit validator should reject impossible sequences.

Valid:

```text id="y34oqw"
attempt_created
    ->
click_initiated
    ->
verification_started
    ->
verified
```

Invalid:

```text id="m9q7h3"
verified
    ->
attempt_created
```

---

# Submission Evidence Logging

Record evidence metadata:

* Evidence ID.
* Source.
* Signal type.
* Strength.
* Job identity match.
* Screenshot path.
* Confirmation number when allowed.
* Timestamp.

Avoid logging entire confirmation pages.

---

# History Synchronization Logging

Record:

* History event written.
* CSV write started.
* CSV write verified.
* XLSX write started.
* XLSX write verified.
* Backup created.
* Reconciliation performed.
* Sync failure.
* Pending sync.

---

# Tracker Sync Event

```json id="uowb8z"
{
  "event_name": "history.tracker_sync_completed",
  "package_id": "",
  "history_record_id": "",
  "csv_status": "success",
  "xlsx_status": "success",
  "operation_id": "",
  "duration_ms": 740
}
```

---

# Error Model

All logged errors should use a standard structure.

```json id="1m66aa"
{
  "error_type": "BrowserNavigationError",
  "error_code": "BROWSER_NAV_TIMEOUT",
  "message": "Application page did not reach a stable state.",
  "category": "browser",
  "retryable": true,
  "requires_user_action": false,
  "submission_outcome_unknown": false,
  "attempt": 1,
  "maximum_attempts": 3,
  "stack_trace_reference": null,
  "cause": null
}
```

---

# Error Requirements

Errors should include:

* Error type.
* Stable error code.
* Human-readable message.
* Component.
* Stage.
* Retryability.
* User-action requirement.
* Submission uncertainty.
* Correlation IDs.
* Timestamp.

---

# Stack Traces

Stack traces may be stored in development or diagnostic logs.

Production defaults should:

* Store stack traces locally.
* Avoid displaying them directly to users.
* Redact file paths containing usernames.
* Redact environment variables.
* Redact request data.
* Use short retention.

---

# Stable Error Codes

Examples:

```text id="it8ru9"
PKG_MANIFEST_INVALID
PKG_FILE_HASH_MISMATCH
READINESS_REQUIRED_ARTIFACT_MISSING
BROWSER_NAV_TIMEOUT
BROWSER_FIELD_NOT_FOUND
ATS_ADAPTER_SIGNATURE_MISMATCH
ANSWER_REQUIRED_VALUE_MISSING
REVIEW_BLOCKING_CONTRADICTION
SUBMISSION_OUTCOME_UNKNOWN
HISTORY_CSV_WRITE_FAILED
HISTORY_XLSX_CORRUPT
SECURITY_UNEXPECTED_DOMAIN
```

Error codes should remain stable across minor releases.

---

# Error Deduplication

Repeated identical errors should be grouped when useful.

Example:

```json id="xhxgzj"
{
  "error_fingerprint": "",
  "first_seen_at": "",
  "last_seen_at": "",
  "occurrence_count": 5
}
```

Do not suppress the first occurrence or final failure event.

---

# Metrics

Metrics should be local and privacy-safe.

---

# Metric Types

```text id="84z2le"
counter
gauge
histogram
timer
rate
```

---

# Platform Metrics

Examples:

* Application starts.
* Application crashes.
* Active workflows.
* Active queues.
* Browser health.
* Storage usage.
* Pending user actions.
* Pending history synchronization.

---

# Package Metrics

Examples:

* Packages created.
* Packages Ready.
* Packages stale.
* Packages blocked.
* Packages submitted.
* Packages requiring review.
* Packages requiring user action.

---

# Browser Metrics

Examples:

* Pages opened.
* Pages completed.
* Fields filled.
* Field verification failures.
* Navigation failures.
* Upload failures.
* Browser crashes.
* Session expirations.
* Average page-completion time.

---

# ATS Adapter Metrics

Examples:

* Adapter detections.
* Detection confidence.
* Generic fallback count.
* Adapter failure rate.
* Page-signature mismatch rate.
* Submission-verification rate.
* Manual fallback rate.

---

# Reasoning Metrics

Examples:

* Provider requests.
* Requests by task type.
* Cache-hit rate.
* Structured-output failures.
* Retry rate.
* Average latency.
* Token usage.
* Fallback-model usage.
* Validation rejection rate.

---

# Application Metrics

Examples:

* Jobs selected.
* Applications prepared.
* Applications queued.
* Applications submitted.
* Submission Unknown count.
* Duplicate applications prevented.
* Applications blocked by policy.
* Manual-completion fallbacks.

---

# Review Metrics

Examples:

* Reviews completed.
* Blocking issues detected.
* Automatic corrections.
* User edits.
* Manual approvals.
* Cross-company contamination detections.
* Sponsorship contradictions.
* Wrong-resume detections.

---

# Submission Metrics

Examples:

* Submission attempts.
* Verified submissions.
* Verified failures.
* Unknown outcomes.
* Unknown outcomes resolved.
* Average verification time.
* Confirmation-number extraction rate.
* Dashboard reconciliation rate.

---

# History Metrics

Examples:

* CSV sync successes.
* XLSX sync successes.
* Sync failures.
* Reconciliation events.
* Duplicate rows prevented.
* Tracker rebuilds.
* Manual history records.

---

# Metric Labels

Metrics may be labeled by:

* ATS.
* Workflow stage.
* Error category.
* Automation mode.
* Package status.
* Adapter version.

Avoid high-cardinality or sensitive labels such as:

* Candidate name.
* Email.
* Full job URL.
* Answer text.
* Confirmation number.

---

# Metrics Storage

Recommended local structure:

```text id="a3g6wh"
user_data/
    observability/
        metrics/
            daily_metrics.json
            cumulative_metrics.json
```

For the MVP, JSON summaries are sufficient.

A local embedded metrics database may be introduced later.

---

# Metrics Aggregation

Metrics may be aggregated:

* Per workflow.
* Per queue.
* Per day.
* Per week.
* Per month.
* Per ATS.
* Per application stage.

---

# Health Monitoring

The Health Monitor should evaluate components such as:

```text id="7w6qx3"
package_storage
candidate_knowledge_base
reasoning_provider
browser_engine
browser_profile
ats_adapter_registry
history_csv
history_xlsx
disk_space
log_writer
```

---

# Health Statuses

```text id="31i471"
healthy
degraded
unavailable
unknown
```

---

# Health Check Result

```json id="bzm32s"
{
  "component": "browser_engine",
  "status": "healthy",
  "checked_at": "",
  "latency_ms": 420,
  "details": {},
  "recommended_action": null
}
```

---

# Platform Health Summary

```json id="4zef2j"
{
  "overall_status": "degraded",
  "components": {
    "browser_engine": "healthy",
    "reasoning_provider": "healthy",
    "history_xlsx": "degraded",
    "package_storage": "healthy"
  }
}
```

---

# Degraded Operation

The platform may continue in a degraded state when safe.

Examples:

* XLSX unavailable but CSV works.
* Dedicated ATS adapter degraded but generic fallback works.
* Metrics writer unavailable but package logging works.

The platform should stop when:

* Package storage is unavailable.
* Audit writer cannot persist submission events.
* Submission attempt cannot be stored.
* Sensitive-data redaction cannot be guaranteed.
* Browser profile is corrupted during submission.

---

# Local Alerting

The system may produce local alerts for:

* Submission Unknown.
* Browser crash.
* History sync failure.
* Audit-integrity failure.
* Disk-space shortage.
* Package-storage failure.
* Repeated ATS adapter failures.
* Stale execution locks.
* Corrupt tracker files.

The MVP does not require external email or push alerts.

---

# Alert Model

```json id="n4k3tk"
{
  "alert_id": "",
  "severity": "high",
  "category": "submission_unknown",
  "package_id": "",
  "message": "Submission could not be verified.",
  "created_at": "",
  "acknowledged": false,
  "recommended_action": ""
}
```

---

# Local Observability Dashboard

The platform should provide a local interface showing:

* Platform health.
* Active queues.
* Active workflows.
* Waiting user actions.
* Recent errors.
* Submission Unknown items.
* Tracker synchronization failures.
* Adapter health.
* Storage usage.
* Recent audit events.
* Metrics summary.

---

# Dashboard Privacy

The dashboard should hide by default:

* Demographic answers.
* Legal answers.
* Government IDs.
* Salary values.
* Full contact details.
* Full application answers.

---

# Workflow Detail View

A workflow detail screen may show:

* Package.
* Job.
* Queue.
* Current stage.
* Current page.
* Adapter.
* Browser status.
* Checkpoints.
* Retries.
* Errors.
* User interventions.
* Review result.
* Submission state.
* History sync state.

---

# Event Timeline

The UI should present important events chronologically.

Example:

```text id="srwgny"
09:00 Package admitted to queue
09:01 Browser session started
09:02 Personal information completed
09:04 Resume uploaded
09:06 User action required: CAPTCHA
09:08 CAPTCHA completed
09:10 Application review passed
09:11 Submission verified
09:11 History synchronized
```

---

# Diagnostic Bundle

The system should be able to create a local diagnostic bundle for one package or workflow.

Recommended contents:

* Sanitized package manifest.
* Workflow state.
* Relevant log events.
* Error records.
* Adapter metadata.
* Page summaries.
* Sanitized screenshots when selected.
* Readiness report.
* Review report.
* Submission state.
* Version information.

---

# Diagnostic Bundle Exclusions

Exclude by default:

* Passwords.
* Cookies.
* Authentication tokens.
* Government IDs.
* Full candidate profile.
* Full demographic responses.
* Full legal responses.
* Unredacted screenshots.
* Browser profile files.

---

# Diagnostic Bundle Manifest

```json id="5xhagx"
{
  "bundle_id": "",
  "package_id": "",
  "workflow_id": "",
  "created_at": "",
  "sanitization_status": "completed",
  "included_files": [],
  "excluded_categories": []
}
```

---

# Diagnostic Bundle Export

Bundles should remain local unless the user explicitly exports them.

Before export:

* Show included categories.
* Warn about screenshots.
* Apply redaction.
* Validate no credential files are included.

---

# Redaction Service

## Responsibility

Remove or mask sensitive data before logging.

---

# Sensitive Data Categories

```text id="w4z3na"
passwords
authentication_tokens
cookies
session_ids
government_ids
passport_numbers
immigration_document_numbers
bank_information
full_home_address
phone_numbers
email_addresses
demographic_answers
disability_answers
veteran_answers
criminal_history
salary_information
legal_answers
```

---

# Redaction Strategies

Supported strategies:

```text id="djbiez"
remove
mask
hash
tokenize
category_only
length_only
last_four
```

---

# Redaction Examples

Email:

```text id="c015jx"
su***@gmail.com
```

Phone:

```text id="qr2l9m"
***-***-1234
```

Government ID:

```text id="xyva45"
[REDACTED]
```

Salary:

```text id="5txonl"
numeric_value_present
```

---

# Secret Detection

Before writing logs, scan for:

* API keys.
* OAuth tokens.
* JWT-like strings.
* Cookies.
* Password-field values.
* Authorization headers.
* Private-key blocks.
* Environment-variable secrets.

Detected secrets should be removed and a security event recorded.

---

# Redaction Failure

If required redaction fails:

* Do not write the unsafe event.
* Write a minimal security event.
* Mark logging component degraded.
* Stop sensitive workflows when safe logging is mandatory.
* Never fall back to unredacted logging.

---

# Logging Policy by Field

The platform may maintain a field policy registry.

Example:

```json id="7kwufd"
{
  "personal.email": "masked",
  "personal.phone": "masked",
  "personal.government_id": "none",
  "work_authorization.visa_status": "category_only",
  "demographic.gender": "none",
  "preferences.salary_expectation": "category_only"
}
```

---

# Prompt and Response Redaction

Before storing prompt-related diagnostics:

* Remove candidate contact details.
* Remove sensitive answers.
* Remove local file paths.
* Remove credentials.
* Remove unrelated Candidate Knowledge Base content.
* Replace values with semantic placeholders where possible.

---

# Configuration Logging

Log configuration state without secrets.

Safe examples:

* Automation mode.
* Maximum retries.
* Enabled adapters.
* Review policy.
* Retention policy.
* Browser visible mode.
* Provider model name.

Unsafe examples:

* API key.
* Password.
* Browser cookie.
* Secure local-secret value.

---

# Configuration Change Audit

Audit changes to:

* Candidate rules.
* Automation mode.
* Review requirements.
* Submission policy.
* Sensitive-field policy.
* Retention policy.
* Enabled ATS adapters.
* Provider configuration.
* Browser profile selection.
* Duplicate-application rules.

---

# Log Storage Structure

Recommended:

```text id="c9vf42"
user_data/
    logs/
        application/
            application.jsonl
        security/
            security.jsonl
        health/
            health.jsonl
        errors/
            errors.jsonl

    observability/
        metrics/
        alerts/
        diagnostic_bundles/

    execution/
        queues/
            {queue_id}/
                events.jsonl
                summary.json

    applications/
        packages/
            {package_id}/
                logs/
                    events.jsonl
                    audit.jsonl
                    errors.json
                    trace.json
```

---

# JSON Lines

JSON Lines is recommended for append-only events because it supports:

* Incremental writing.
* Stream processing.
* Crash resilience.
* Easy filtering.
* Simple local inspection.

---

# Log File Naming

Recommended:

```text id="stcdl3"
application_2026-07-12.jsonl
security_2026-07-12.jsonl
errors_2026-07-12.jsonl
```

Package-specific files may remain unpartitioned until rotation is required.

---

# Atomic Logging

Append operations should:

* Flush important audit events.
* Handle partial writes.
* Detect invalid trailing records.
* Preserve prior records after a crash.

Critical submission events should be synchronously persisted before continuing.

---

# Critical Persistence Events

These events should be durably written before the workflow advances:

* Submission-attempt creation.
* Submit-click initiation.
* Submission outcome.
* User approval.
* Duplicate override.
* Legal-answer update.
* Package deletion.
* History correction.

---

# Log Rotation

Rotation may occur by:

* Date.
* File size.
* Event count.

Example policy:

```json id="cfrhyc"
{
  "rotation": {
    "maximum_file_size_mb": 25,
    "rotate_daily": true,
    "compress_rotated_logs": true
  }
}
```

---

# Compression

Rotated logs may be compressed locally.

Compressed logs must still respect:

* Retention.
* Access permissions.
* Encryption settings.
* Deletion requests.

---

# Retention Policy

Example:

```json id="jz4316"
{
  "retention": {
    "application_logs_days": 30,
    "debug_logs_days": 7,
    "security_logs_days": 180,
    "audit_logs": "keep_with_package",
    "submission_logs": "keep_with_package",
    "health_logs_days": 30,
    "metrics_days": 365,
    "diagnostic_bundles_days": 14
  }
}
```

---

# Retention Categories

## Short-Term

* TRACE logs.
* DEBUG logs.
* Raw HTML.
* Detailed browser diagnostics.

## Medium-Term

* Application logs.
* Health logs.
* Error logs.
* Performance logs.

## Long-Term

* Package audit trail.
* Submission evidence.
* User approvals.
* History events.
* Duplicate overrides.

---

# Retention Execution

The Retention Manager should:

1. Identify expired files.
2. Exclude active workflows.
3. Preserve required audit records.
4. Delete eligible files.
5. Record deletion.
6. Update storage metrics.
7. Avoid deleting files referenced by unresolved submission states.

---

# Retention Protection

Do not automatically delete:

* Submission Unknown evidence.
* Active workflow logs.
* Current queue logs.
* Submitted artifact fingerprints.
* User approval records.
* Audit-integrity records.
* Files under legal or user hold.

---

# User-Controlled Deletion

The user may delete:

* Debug logs.
* Screenshots.
* Diagnostic bundles.
* Archived package logs.
* Metrics.

Deleting submitted-package audit records should require explicit confirmation and should record the deletion before removal when possible.

---

# Disk-Space Monitoring

The Health Monitor should track:

* Total disk space.
* Free disk space.
* Log directory size.
* Package directory size.
* Screenshot size.
* Browser profile size.
* History backup size.

---

# Disk-Space Thresholds

Example:

```text id="5sqfna"
Healthy:
More than 5 GB free.

Warning:
1–5 GB free.

Critical:
Less than 1 GB free.
```

Thresholds should be configurable.

---

# Low-Disk Behavior

When disk space is low:

* Pause new package generation when necessary.
* Prevent final submission when critical audit records cannot be persisted.
* Rotate or delete expired debug logs.
* Preserve submission and audit evidence.
* Notify the user.
* Avoid deleting active package data automatically.

---

# Access Permissions

Where supported, log directories should be readable and writable only by the local user account.

Sensitive package logs should not be placed in public or shared folders by default.

---

# Encryption

Encryption at rest may be optional for the MVP.

Future support may include:

* Operating-system encrypted storage.
* Encrypted diagnostic bundles.
* Encrypted sensitive package logs.
* User-managed keys.

The logging architecture should not assume that logs are public or unencrypted.

---

# Clock and Timestamp Rules

All events should store:

* ISO 8601 timestamp.
* Time-zone offset.
* Sequence number.

Example:

```text id="4ory4w"
2026-07-12T14:30:00-04:00
```

---

# Monotonic Timing

Operation duration should use a monotonic clock when available.

Wall-clock timestamps are still required for audit records.

---

# Clock Drift

Sequence numbers help preserve event order if:

* System time changes.
* Daylight saving changes.
* Clock synchronization occurs.

---

# Sequence Numbers

Each event stream should have increasing sequence numbers.

Possible sequence scopes:

* Application instance.
* Package.
* Queue.
* Audit trail.

Sequence scope should be identified in metadata.

---

# Crash Recovery Using Logs

On startup, the system may use logs and state files to identify:

* Interrupted queues.
* Active workflow stage.
* Last checkpoint.
* Submission attempt in progress.
* History synchronization pending.
* Stale locks.
* Incomplete audit writes.

State files remain authoritative for workflow control.

Logs provide supporting recovery evidence.

---

# Recovery Event

```json id="gcnszw"
{
  "event_name": "workflow.recovery_started",
  "package_id": "",
  "workflow_id": "",
  "previous_application_instance_id": "",
  "recovery_source": "checkpoint_and_audit",
  "last_known_stage": "",
  "submission_click_recorded": false
}
```

---

# Missing Event Detection

The integrity validator should detect expected-event gaps.

Example:

```text id="hqyo86"
submission.click_initiated exists
but
submission.verification_started is missing
```

The recovery system should begin verification.

---

# Conflicting Event Detection

Example:

```text id="id8d7b"
submission.verified
and
submission.failed
for the same attempt
```

This should trigger reconciliation.

---

# Audit Reconciliation

Reconciliation should compare:

* Package state.
* Workflow state.
* Submission result.
* Audit events.
* History events.
* CSV and XLSX status.

The system should generate a correction event rather than silently rewriting history.

---

# Observability During Automatic Mode

Automatic mode should provide enough visibility that the user can understand:

* Which package is running.
* Which stage is active.
* Whether browser automation is progressing.
* Whether review passed.
* Whether submission succeeded.
* Whether intervention is required.

Automatic mode should not hide failures or uncertain outcomes.

---

# Observability During Review Mode

Review mode should additionally display:

* Review findings.
* Pending approval.
* Changes since preparation.
* Active artifact versions.
* Final form snapshot status.

---

# Observability During Manual Mode

Manual mode should log:

* Application opened.
* Documents prepared.
* Manual handoff.
* User-confirmed completion.
* User-confirmed submission.
* Manual status updates.

It should not claim browser verification unless it occurred.

---

# Performance Observability

The platform should measure duration for:

* Job analysis.
* Candidate-context loading.
* Resume tailoring.
* Cover-letter generation.
* Answer preparation.
* Readiness.
* Queue waiting.
* Browser startup.
* Page completion.
* Runtime answer resolution.
* Review.
* Submission verification.
* History synchronization.

---

# Performance Event

```json id="6la0ev"
{
  "event_name": "performance.operation_completed",
  "operation": "resume_tailoring",
  "duration_ms": 12400,
  "status": "success",
  "package_id": ""
}
```

---

# Slow Operation Detection

The system may warn when an operation exceeds configured thresholds.

Examples:

* Browser page load over 30 seconds.
* Provider request over 60 seconds.
* Resume parsing over 60 seconds.
* History synchronization over 10 seconds.

Slow does not necessarily mean failed.

---

# Retry Observability

Every retry should record:

* Original operation.
* Error.
* Retry classification.
* Attempt number.
* Maximum attempts.
* Delay.
* Result.
* Whether state was revalidated.

---

# Retry Event

```json id="0cm6f4"
{
  "event_name": "workflow.retry_started",
  "operation": "browser.navigate",
  "attempt": 2,
  "maximum_attempts": 3,
  "reason": "temporary_navigation_timeout",
  "safe_to_repeat": true
}
```

---

# Cancellation Logging

Record:

* Cancellation target.
* User or system actor.
* Current stage.
* Whether final click had occurred.
* State persisted.
* Locks released.
* Resulting status.

---

# Package Deletion Audit

Before deleting a package, record:

* Package ID.
* Status.
* Submission status.
* Confirmation that user requested deletion.
* Artifacts scheduled for deletion.
* Deletion timestamp.

For submitted packages, deletion should require stronger confirmation.

---

# Data Export Logging

Record exports of:

* History.
* Diagnostic bundles.
* Audit records.
* Package reports.

Do not log exported file content.

Record:

* Export type.
* Filters.
* Output path category.
* Timestamp.
* Record count.
* Sanitization status.

---

# External Telemetry Policy

The MVP should not send logs, metrics, prompts, screenshots, or candidate information to external telemetry services by default.

Any future external telemetry should require:

* Explicit user opt-in.
* Clear data categories.
* Redaction.
* Configurable retention.
* Disable control.
* No secrets.
* No candidate-answer content by default.

---

# Telemetry Setting

Example:

```json id="xe37h2"
{
  "telemetry": {
    "external_enabled": false,
    "local_metrics_enabled": true,
    "anonymous_crash_reports": false
  }
}
```

---

# Audit Reports

The system should generate audit summaries.

Possible reports:

* Package lifecycle report.
* Submission audit report.
* User-approval report.
* Candidate-rule usage report.
* Sensitive-field handling report.
* History reconciliation report.
* Security-event report.

---

# Submission Audit Report

Example contents:

```text id="wr8et5"
Package ID
Job identity
Active resume version
Active cover-letter version
Answer-set version
Review approval
Submission-attempt ID
Final-click time
Verification evidence
Outcome
History synchronization
```

---

# Candidate Rule Audit

The system should be able to identify:

* Which rules applied.
* Which rule blocked an action.
* Which rule selected an answer.
* Which rule required review.
* Which rule was overridden.
* Who approved the override.

---

# Rule Audit Event

```json id="d8mjzy"
{
  "event_name": "rule.evaluated",
  "rule_id": "",
  "rule_result": "passed",
  "workflow_stage": "submission_readiness",
  "effect": "allow",
  "override_id": null
}
```

---

# Explainability

The audit system should answer operational questions such as:

* Why was this package not queued?
* Why was this answer selected?
* Why did the workflow pause?
* Why was manual review required?
* Which resume was uploaded?
* Was Submit clicked?
* What evidence confirmed submission?
* Why was a duplicate blocked?
* Why did the tracker status change?

Answers should use structured events and source references, not hidden reasoning.

---

# Explainability Result

```json id="nfo1om"
{
  "question": "Why was the application blocked?",
  "summary": "A required non-compete answer was missing.",
  "supporting_events": [],
  "supporting_rules": [],
  "next_action": "Provide the missing answer."
}
```

---

# Testing Strategy

Testing should cover:

* Event schema validation.
* Correlation propagation.
* Redaction.
* Audit chains.
* Metrics.
* Rotation.
* Retention.
* Recovery.
* Tracker synchronization.
* Submission durability.
* Diagnostic bundle generation.
* Security failures.

---

# Unit Tests

Unit-test:

* Event ID generation.
* Event-name validation.
* Timestamp formatting.
* Sequence generation.
* Correlation-context inheritance.
* Log-level filtering.
* Redaction.
* Secret detection.
* Error serialization.
* Hash-chain generation.
* Hash-chain validation.
* Metric aggregation.
* Retention eligibility.
* Rotation thresholds.
* Event deduplication.
* Stable error codes.

---

# Integration Tests

Integration-test:

* Package lifecycle logging.
* Queue-to-package correlation.
* Browser workflow logging.
* Provider metadata logging.
* User-intervention logging.
* Submission-attempt durability.
* History synchronization logs.
* Crash recovery from logs.
* Audit reconciliation.
* Low-disk behavior.
* Diagnostic bundle sanitization.

---

# Required Test Scenarios

## Package Lifecycle

Create, prepare, queue, execute, submit, and archive a synthetic package.

Expected:

* Events exist for every major transition.
* All events share the package ID.
* Workflow trace is complete.
* Audit trail passes integrity check.

---

## Sensitive Answer

A legal or demographic answer is processed.

Expected:

* Answer value does not appear in routine logs.
* Event records the semantic category.
* Package data retains the authorized value.
* Security scan finds no leak.

---

## Provider Request

A narrative answer is generated.

Expected:

* Provider, model, prompt version, duration, and validation result logged.
* Full prompt and response not logged by default.
* No hidden reasoning recorded.

---

## Browser Field Interaction

Email and phone fields are filled.

Expected:

* Field IDs and verification status logged.
* Values are masked or omitted.
* No raw contact value appears.

---

## File Upload

Resume is uploaded.

Expected:

* Document type, filename, hash, and verification result logged.
* Arbitrary source path is not exposed.

---

## CAPTCHA

CAPTCHA is detected.

Expected:

* User-intervention event created.
* Screenshot path recorded.
* No CAPTCHA bypass event exists.
* Resume event appears after user completion.

---

## Review Blocking Issue

Work-authorization answers contradict each other.

Expected:

* Blocking finding logged.
* Sensitive values remain redacted.
* Correction and rereview events recorded.

---

## Submission Success

Submission is verified.

Expected event sequence:

```text id="ij9ucv"
snapshot_created
lock_acquired
attempt_created
click_initiated
verification_started
evidence_collected
verified
history_synced
lock_released
```

Audit integrity passes.

---

## Submission Unknown

Browser crashes after the final click.

Expected:

* Click event already durable.
* Submission Unknown event recorded.
* No retry event for the final click.
* User-action alert created.
* History marks submission status unknown.

---

## CSV Sync Failure

Application submission succeeds, but CSV update fails.

Expected:

* Submission remains verified.
* CSV error logged.
* XLSX result logged independently.
* Pending synchronization recorded.
* No resubmission triggered.

---

## Audit Modification

An audit event is altered manually.

Expected:

* Hash-chain validation fails.
* Package marked for review.
* Original evidence is not deleted.
* Integrity alert created.

---

## Low Disk Space

Free disk falls below the critical threshold.

Expected:

* Critical alert.
* Expired debug logs eligible for cleanup.
* New submission blocked if audit persistence cannot be guaranteed.
* Submission evidence preserved.

---

## Redaction Failure

Logger receives a payload containing an API key.

Expected:

* Key removed.
* Security event recorded.
* Unsafe payload not written.
* Workflow continues only if safe.

---

## Crash Recovery

Platform stops during page execution.

Expected:

* On restart, application instance changes.
* Previous workflow and checkpoint are located.
* Recovery event references previous instance.
* Trace continues without duplicating completed stages.

---

## Diagnostic Bundle

User creates a diagnostic bundle.

Expected:

* Relevant state and logs included.
* Credentials and sensitive values excluded.
* Sanitization report generated.
* Bundle export audited.

---

## Log Rotation

Application log exceeds configured size.

Expected:

* File rotates.
* New events continue in a new file.
* Rotated log remains readable.
* Retention metadata remains correct.

---

## Retention Cleanup

Debug logs exceed retention period.

Expected:

* Expired files deleted.
* Active workflow files retained.
* Deletion event recorded.
* Audit and submission evidence preserved.

---

# Error Types

Recommended internal errors:

```text id="pblpj4"
LoggingConfigurationError
LogWriteError
LogRotationError
LogRetentionError
LogSchemaValidationError
CorrelationContextError
RedactionError
SecretDetectionError
AuditWriteError
AuditIntegrityError
TraceWriteError
MetricWriteError
HealthCheckError
DiagnosticBundleError
ObservabilityStorageError
```

---

# Logging Service Interface

Conceptual interface:

```text id="yd594n"
LoggingService

    log_event(event)
    log_error(error, context)
    log_audit_event(event)
    create_progress_event(message, context)
    create_trace(workflow_id)
    start_span(operation, context)
    end_span(span_id, result)
    record_metric(metric)
    record_health_check(result)
    rotate_logs()
    apply_retention()
    validate_audit_integrity(package_id)
    create_diagnostic_bundle(package_id)
```

---

# Redaction Service Interface

```text id="0e91h0"
RedactionService

    classify_value(field_type, value)
    redact_value(field_type, value)
    sanitize_event(event)
    detect_secrets(payload)
    sanitize_diagnostic_bundle(files)
```

---

# Audit Service Interface

```text id="xp5gpo"
AuditService

    append_package_event(package_id, event)
    append_system_event(event)
    validate_package_chain(package_id)
    explain_package_decision(package_id, question)
    reconcile_audit_state(package_id)
    export_audit_report(package_id)
```

---

# Metrics Service Interface

```text id="74lh2p"
MetricsService

    increment(metric_name, labels)
    set_gauge(metric_name, value, labels)
    record_duration(metric_name, duration, labels)
    calculate_rate(metric_name, period)
    build_daily_summary()
    build_package_summary(package_id)
```

---

# Completion Criteria

The Logging, Observability, and Audit Trails system is complete when:

* All major services emit structured events.
* Event names and schemas are documented.
* Correlation identifiers propagate across workflows.
* Package-specific event logs exist.
* Queue-specific event logs exist.
* Workflow traces exist.
* User-visible progress events are separate from diagnostics.
* Browser interactions are logged without exposing values.
* Provider requests are logged at metadata level.
* Review and readiness results are observable.
* User interventions are logged.
* Submission events are durably persisted.
* Application-history synchronization is logged.
* Stable error codes exist.
* Sensitive values are redacted.
* Secret detection prevents credential leakage.
* Audit trails are append-only.
* Audit hash-chain validation works.
* Metrics are collected locally.
* Component health can be displayed.
* Log rotation works.
* Retention policies work.
* Low-disk conditions are detected.
* Crash recovery can use logs and checkpoints.
* Diagnostic bundles can be generated safely.
* External telemetry is disabled by default.
* Unit and integration tests pass.
* Submission cannot proceed when mandatory audit persistence is unavailable.

---

# Definition of Logging and Audit Completion

The full phase is complete when the system can reliably answer:

```text id="t9str2"
What happened?

When did it happen?

Which package and workflow were involved?

Which component performed the action?

Which artifact version was used?

Why did the workflow continue, pause, or stop?

Was the browser action verified?

Was final submission attempted?

Was submission verified?

Was application history synchronized?

Were sensitive values protected?
```

The answer should be derived from structured events, package state, audit records, and submission evidence.

It should not depend on hidden reasoning, developer memory, or unstructured console output.

---

# Summary

The Logging, Observability, and Audit Trails system makes the platform understandable, recoverable, and trustworthy.

It provides:

* Structured technical logs.
* Package audit trails.
* Queue event streams.
* Workflow traces.
* Browser diagnostics.
* Provider metadata.
* Review and readiness records.
* Submission evidence.
* History synchronization records.
* Local metrics.
* Health monitoring.
* Security alerts.
* Diagnostic bundles.

The system should record enough information to reconstruct important workflows while minimizing sensitive data.

Routine logs should not contain:

* Passwords.
* Cookies.
* Authentication tokens.
* Government identifiers.
* Full demographic answers.
* Full legal answers.
* Complete candidate profiles.
* Hidden reasoning.

Critical application events, especially approvals and submission actions, must be durably and append-only recorded.

The platform should be observable without sacrificing candidate privacy.
