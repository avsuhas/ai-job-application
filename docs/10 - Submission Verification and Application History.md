# 10 - Submission Verification and Application History

## LLM-Powered Autonomous Job Search & Application Platform

Version: 1.0

---

# Purpose

This document defines the Submission Verification and Application History system responsible for determining whether a job application was successfully submitted, preserving reliable evidence, preventing duplicate submissions, and maintaining a complete local record of application activity.

The system must never treat a final Submit-button click as proof that an application was submitted.

A final submission may result in:

* Verified submission.
* Clear rejection or failure before submission.
* Validation failure.
* Session expiration.
* Browser crash.
* Network interruption.
* Redirect to an unclear page.
* Duplicate-application message.
* Application closure.
* Unknown outcome.

The Submission Verification system must classify the outcome using explicit evidence.

The Application History system must maintain a local record of:

* Jobs considered.
* Jobs prepared.
* Jobs queued.
* Jobs opened.
* Jobs submitted.
* Jobs skipped.
* Jobs blocked.
* Jobs that failed.
* Jobs requiring user action.
* Jobs with unknown submission outcomes.
* Follow-up status changes.

For the MVP, application history should be stored locally using CSV and XLSX files rather than requiring a database.

---

# Core Principle

A submit action and a verified submission are different events.

```text id="3ykk2p"
Submit Action
      |
      v
Submission Verification
      |
      +------> Verified Submitted
      |
      +------> Verified Failed
      |
      +------> Already Applied
      |
      +------> Application Closed
      |
      +------> Submission Unknown
```

Only strong evidence may move an application to `Submitted`.

---

# Objectives

The system should:

* Record the state immediately before submission.
* Record every submission attempt.
* Avoid repeated final clicks.
* Detect strong confirmation signals.
* Distinguish weak signals from proof.
* Verify ATS dashboard status when available.
* Capture confirmation numbers and application IDs.
* Preserve screenshots and structured evidence.
* Handle browser crashes after submission.
* Mark uncertain outcomes as `Submission Unknown`.
* Prevent automatic resubmission after an uncertain outcome.
* Reconcile package status with application history.
* Detect duplicate applications before future attempts.
* Maintain CSV and XLSX tracking files.
* Keep history updates idempotent.
* Preserve historical records after candidate data changes.
* Support user corrections and annotations.
* Allow later application-status updates.
* Keep all history data local and user-controlled.

---

# Scope

This document covers:

* Pre-submission evidence.
* Submission-attempt records.
* Submit-control execution boundaries.
* Strong and weak confirmation signals.
* ATS-specific submission verification.
* Generic submission verification.
* Submission outcome classification.
* Unknown-outcome handling.
* Dashboard reconciliation.
* Duplicate-application prevention.
* Local application-history storage.
* CSV and XLSX schemas.
* Tracker synchronization.
* Idempotency.
* Status updates.
* User annotations.
* Historical immutability.
* Data retention.
* Recovery.
* Security.
* Testing.
* Metrics.

This document does not define:

* Form filling.
* Resume tailoring.
* Cover-letter generation.
* Job ranking.
* Application queue ordering.
* Low-level browser selector implementation.
* Email inbox integration.
* Interview scheduling.

---

# System Components

```text id="u34kqi"
Submission and History System
    |
    +-- Pre-Submission Snapshot Service
    +-- Submission Attempt Manager
    +-- Submission Evidence Collector
    +-- Submission Signal Classifier
    +-- ATS Submission Verifier
    +-- Generic Submission Verifier
    +-- Dashboard Reconciliation Service
    +-- Unknown Outcome Resolver
    +-- Duplicate Application Detector
    +-- Application History Service
    +-- CSV History Writer
    +-- XLSX History Writer
    +-- History Reconciliation Service
    +-- History Audit Service
    +-- Retention Manager
```

---

# Separation of Responsibilities

## Browser Automation Engine

Responsible for:

* Locating the final submission control.
* Performing one approved final click.
* Capturing browser state.
* Waiting for page changes.
* Reading confirmation-page content.
* Capturing screenshots.
* Reporting navigation and network results.

## ATS Adapter

Responsible for:

* Identifying ATS-specific final submission controls.
* Defining expected confirmation signals.
* Extracting ATS application IDs.
* Reading ATS dashboard status.
* Recognizing ATS-specific failure messages.

## Submission Verification Service

Responsible for:

* Combining evidence.
* Classifying the outcome.
* Preventing unsafe retries.
* Returning a structured verification result.

## Application History Service

Responsible for:

* Recording application lifecycle events.
* Maintaining current status.
* Updating CSV and XLSX files.
* Preventing duplicate history rows.
* Preserving audit information.

## Orchestrator

Responsible for:

* Invoking submission verification.
* Updating Application Package state.
* Triggering history synchronization.
* Deciding whether the queue may continue.
* Requesting user action when the outcome is unknown.

---

# Submission Lifecycle

```text id="41q0tr"
Ready for Submission
        |
        v
Pre-Submission Snapshot
        |
        v
Submission Lock
        |
        v
Submit Attempt Created
        |
        v
Final Click Performed
        |
        v
Verification Pending
        |
        +------> Submitted
        |
        +------> Failed
        |
        +------> Already Applied
        |
        +------> Closed
        |
        +------> Unknown
        |
        v
Package Updated
        |
        v
History Synchronized
```

---

# Submission States

Supported submission states:

```text id="si8k4c"
not_started
ready
attempt_created
click_initiated
verification_pending
submitted
failed_before_click
failed_after_click
already_applied
application_closed
cancelled_before_click
submission_unknown
verification_error
```

---

## Not Started

No final submission preparation has begun.

---

## Ready

All submission-readiness requirements have passed.

---

## Attempt Created

A durable submission-attempt record exists, but the final click has not yet occurred.

---

## Click Initiated

The browser has initiated the final interaction.

The workflow must assume that submission may have occurred.

---

## Verification Pending

The final action was executed and the verifier is collecting evidence.

---

## Submitted

Strong evidence confirms successful submission.

---

## Failed Before Click

The workflow failed before the irreversible action.

A retry may be allowed after readiness revalidation.

---

## Failed After Click

Strong evidence confirms that the submission was rejected or failed after the final action.

A retry may be allowed only when evidence clearly proves that no application was created.

---

## Already Applied

The ATS reports that an application for the same requisition already exists.

---

## Application Closed

The ATS reports that applications are no longer accepted.

---

## Cancelled Before Click

The user cancelled before the final action.

---

## Submission Unknown

The final click may have occurred, but the system cannot confirm success or failure.

Automatic retry is prohibited.

---

## Verification Error

The verification service failed to complete because of an internal system problem.

When the final click already occurred, this should normally resolve to `Submission Unknown`, not a normal retryable failure.

---

# Pre-Submission Snapshot

Before the final click, the system should create a durable snapshot.

Recommended file:

```text id="hqfjow"
submission/pre_submission_snapshot.json
```

---

# Snapshot Contents

The snapshot should include:

* Package ID.
* Workflow ID.
* Queue ID.
* Company.
* Job title.
* Job ID.
* Requisition ID.
* Application URL.
* Current browser URL.
* ATS platform.
* ATS adapter version.
* Active resume version.
* Active resume filename.
* Active resume hash.
* Active cover-letter version.
* Active cover-letter filename.
* Prepared-answer-set version.
* Final browser-form snapshot hash.
* Review approval ID.
* Submission-readiness ID.
* Submit-control label.
* Submit-control confidence.
* Screenshot path.
* Timestamp.

---

# Pre-Submission Snapshot Example

```json id="m27jt8"
{
  "package_id": "google_123456_20260712T080000",
  "workflow_id": "workflow_google_123456",
  "company": "Google",
  "job_title": "Senior Software Engineer",
  "job_id": "123456",
  "application_url": "",
  "browser_url": "",
  "ats_platform": "custom",
  "active_resume": {
    "version": 2,
    "filename": "Suhas_Arudi_Google_Resume.pdf",
    "hash": ""
  },
  "active_cover_letter": null,
  "answer_set_version": 3,
  "form_snapshot_hash": "",
  "review_approval_id": "",
  "submission_readiness_id": "",
  "submit_control": {
    "label": "Submit Application",
    "confidence": 99
  },
  "screenshot_path": "",
  "created_at": ""
}
```

---

# Snapshot Validation

Before creating a submission attempt, confirm:

* Snapshot was written successfully.
* File hashes match active documents.
* Review approval references active versions.
* Browser form snapshot matches the current page.
* Job identity is verified.
* Submit control is final.
* No duplicate submission is known.
* No previous unknown attempt exists.

---

# Submission Lock

A dedicated submission lock should be acquired immediately before creating the attempt.

Recommended file:

```text id="1o6xov"
submission/.submission.lock
```

---

# Submission Lock Contents

```json id="90azxi"
{
  "lock_type": "final_submission",
  "package_id": "",
  "workflow_id": "",
  "attempt_id": "",
  "acquired_at": "",
  "last_heartbeat": ""
}
```

---

# Submission Lock Rules

* Only one active submission attempt may exist per package.
* Another queue or process must not submit the same package.
* The lock must remain during verification.
* The lock should be released after a terminal outcome.
* A stale lock must be reconciled with submission-attempt records before removal.
* A lock must never be removed merely because the browser process ended.

---

# Submission Attempt

Every final submission action should have a unique attempt record.

Recommended file:

```text id="2ci0d1"
submission/attempts/submission_attempt_001.json
```

---

# Submission Attempt Model

```json id="50bz5b"
{
  "attempt_id": "submission_attempt_001",
  "package_id": "",
  "workflow_id": "",
  "attempt_number": 1,
  "status": "attempt_created",
  "created_at": "",
  "click_initiated_at": null,
  "verification_started_at": null,
  "verification_completed_at": null,
  "page_url_before": "",
  "page_url_after": null,
  "submit_control_label": "Submit Application",
  "screenshot_before": "",
  "screenshot_after": null,
  "browser_action_result": null,
  "verification_result": null
}
```

---

# Attempt Numbering

Attempt numbers should be sequential for the package.

Example:

```text id="6fqm85"
submission_attempt_001
submission_attempt_002
```

A second attempt should exist only when:

* A prior attempt clearly failed before submission.
* A prior attempt clearly failed after submission with proof that no application was created.
* The user explicitly authorizes a retry after review.
* Duplicate checks pass again.

A prior `Submission Unknown` attempt must block a new attempt.

---

# Submit Action Boundary

The system should explicitly mark the irreversible boundary.

```text id="4g65tb"
Before Click:
Safe to cancel or retry after validation.

After Click Initiated:
Do not assume retry is safe.
```

The attempt record should be persisted before the click.

---

# Browser Action Result

```json id="vtw01g"
{
  "action": "click_submit",
  "status": "performed",
  "target_label": "Submit Application",
  "target_verified": true,
  "started_at": "",
  "completed_at": "",
  "browser_exception": null
}
```

Possible statuses:

```text id="0eal2q"
not_performed
performed
failed_before_dispatch
dispatch_uncertain
```

---

# Dispatch Uncertain

`dispatch_uncertain` means the browser cannot confirm whether the click event reached the page.

Examples:

* Browser crashed during click dispatch.
* Connection to the browser process was lost.
* Page closed immediately.
* Automation framework returned an uncertain error.

This state should lead to submission verification and may become `Submission Unknown`.

---

# Submission Verification Service

## Responsibility

Collect and classify evidence after a final submission action.

Conceptual interface:

```text id="fvrf8e"
SubmissionVerificationService

    begin_verification(attempt_id)
    collect_page_evidence()
    collect_adapter_evidence()
    collect_network_evidence()
    collect_dashboard_evidence()
    classify_signals(evidence)
    verify_submission(attempt_id)
    resolve_unknown_outcome(package_id)
```

---

# Verification Evidence Sources

The verifier may use:

* Confirmation-page heading.
* Confirmation message.
* Confirmation number.
* ATS application ID.
* Submitted-status banner.
* Candidate dashboard status.
* URL pattern.
* Browser page transition.
* ATS adapter result.
* Server response.
* Application form disappearance.
* Duplicate-application message.
* Application-closed message.
* Validation errors.
* Email confirmation in a future authorized integration.
* User-provided verification.

Evidence should be categorized by strength.

---

# Evidence Model

```json id="p84py0"
{
  "evidence_id": "evidence_001",
  "attempt_id": "",
  "source": "confirmation_page",
  "signal_type": "explicit_success_message",
  "value": "Application submitted successfully",
  "strength": "strong",
  "captured_at": "",
  "screenshot_path": "",
  "metadata": {}
}
```

---

# Evidence Strength

Supported evidence strengths:

```text id="2q7o7j"
conclusive
strong
supporting
weak
contradictory
```

---

## Conclusive Evidence

Direct proof of a submission record.

Examples:

* ATS dashboard lists the requisition as Submitted.
* Confirmation number tied to the application.
* ATS application ID returned on a confirmation page.
* Explicit success response associated with the final request.

---

## Strong Evidence

Highly reliable evidence.

Examples:

* Dedicated confirmation page saying the application was submitted.
* Explicit submission-success message with correct job identity.
* Confirmation URL pattern plus correct company and requisition.

---

## Supporting Evidence

Useful but insufficient alone.

Examples:

* Submit button disappeared.
* Form became read-only.
* Current date appears beside application status.
* Browser redirected to a candidate dashboard without visible status.

---

## Weak Evidence

Cannot prove submission.

Examples:

* URL changed.
* Form disappeared.
* Browser returned to the careers page.
* Page reloaded.
* Generic success-colored banner.
* Submit button became disabled.

---

## Contradictory Evidence

Evidence that submission did not succeed or may not have occurred.

Examples:

* Validation error remains.
* Server returned an explicit failure.
* Application is still editable and marked Draft.
* ATS shows no application record.
* Job is closed.
* Session expired before form processing.
* Duplicate message references an earlier submission.

---

# Strong Success Signals

A submission may be verified as successful when one or more strong signals are present.

Examples:

```text id="g3oiti"
“Application submitted.”

“Thank you for applying.”

“Your application has been received.”

Confirmation number: ABC-12345

Application status: Submitted
```

The signal should correspond to the intended job.

---

# Job Identity Requirement

A generic success message is not enough when the browser may have moved to another application.

Verification should confirm, where possible:

* Company.
* Job title.
* Job ID.
* Requisition ID.
* Package ID through local context.
* ATS application record.

---

# Confirmation Message Extraction

Store:

* Full normalized message.
* Page heading.
* Relevant job identity.
* Confirmation number.
* Application ID.
* Timestamp.
* Source element context.
* Screenshot.

Long page content should not be stored unnecessarily.

---

# Confirmation Number Extraction

Confirmation numbers may be labeled:

* Confirmation Number.
* Application Number.
* Candidate Application ID.
* Submission ID.
* Reference Number.
* Application Reference.

The verifier should preserve the value exactly.

---

# Confirmation Number Result

```json id="h73evl"
{
  "label": "Application Reference",
  "value": "APP-483726",
  "source": "confirmation_page",
  "confidence": 99
}
```

---

# ATS Application ID

An ATS may expose an internal application ID.

Store it separately from:

* Job ID.
* Requisition ID.
* Candidate ID.
* Confirmation number.

These values should not be treated as interchangeable.

---

# URL Signals

URL changes can support verification.

Examples:

```text id="v8ksmb"
/application/confirmation
/apply/success
/candidate/home
/application/submitted
```

URL evidence should be combined with page content or ATS-specific knowledge.

---

# Page Content Signals

The verifier should inspect:

* Headings.
* Alerts.
* Status badges.
* Application summaries.
* Confirmation sections.
* Error summaries.
* Buttons.
* Edit controls.
* Dashboard rows.

---

# Application Form Disappearance

Form disappearance is supporting evidence only.

It may also occur because:

* Session expired.
* Browser navigated away.
* Page crashed.
* Job closed.
* User returned to job listing.

---

# Network Evidence

Network evidence may be used carefully.

Possible strong signals:

* Final request returned a documented success status.
* Response includes an application ID.
* ATS adapter recognizes the submission endpoint and response schema.

Network evidence must not store:

* Authentication headers.
* Cookies.
* Full request body containing candidate information.
* Session tokens.
* Sensitive identifiers unnecessarily.

---

# Network Failure

A network timeout after clicking Submit does not prove failure.

The server may have processed the request.

The result should remain pending until other evidence is collected.

If no reliable evidence is available, classify as `Submission Unknown`.

---

# Browser Crash After Click

When the browser crashes after the click:

1. Preserve the submission-attempt record.
2. Mark verification pending.
3. Restart the browser with the same profile.
4. Open the ATS dashboard or application URL.
5. Search for a submitted application record.
6. Check local history.
7. Avoid clicking Submit again.
8. Resolve as Submitted, Failed, or Unknown.

---

# Browser Crash Before Click

When evidence proves the click was not initiated:

* Mark `Failed Before Click`.
* Release submission lock.
* Rerun readiness.
* Permit a controlled retry.

---

# Session Expiration

Session expiration may happen:

* Before the click.
* During submission.
* After submission.

## Before Click

Retry may be allowed after login and readiness revalidation.

## During or After Click

Verify ATS status before any retry.

If the outcome cannot be determined, mark Submission Unknown.

---

# ATS-Specific Submission Verifier

Each dedicated ATS adapter should define:

* Strong success patterns.
* Confirmation URL patterns.
* Confirmation-number selectors.
* Dashboard status mapping.
* Duplicate-message patterns.
* Failure-message patterns.
* Closed-application patterns.
* Draft-status patterns.
* Verification timeout.

---

# ATS Verification Result

```json id="a406qv"
{
  "adapter_id": "greenhouse",
  "adapter_version": "1.0.0",
  "status": "submitted",
  "signals": [],
  "application_id": "",
  "confirmation_number": "",
  "confidence": 100
}
```

---

# Generic Submission Verifier

The Generic Submission Verifier should use conservative rules.

It may mark Submitted when:

* Explicit success message is present.
* Correct job identity is visible.
* No contradictory error is present.
* Page is clearly a confirmation page.

It should mark Submission Unknown when:

* Only weak signals are present.
* Page is blank.
* Browser redirected without confirmation.
* Domain changed unexpectedly.
* Page closed.
* Browser crashed.
* Generic “success” wording is unrelated.
* Confirmation cannot be tied to the job.

---

# Submission Classification

Supported final classifications:

```text id="1bxy4k"
submitted
failed
already_applied
application_closed
cancelled
submission_unknown
```

---

# Classification Rules

## Submitted

Requires conclusive or strong evidence.

## Failed

Requires clear evidence that submission did not create an application.

## Already Applied

Requires ATS or history evidence of an existing application.

## Application Closed

Requires employer or ATS evidence that submission is no longer accepted.

## Cancelled

Only valid when final click was not initiated.

## Submission Unknown

Used whenever success and failure cannot be determined reliably.

---

# Verification Result Model

```json id="9nkj8j"
{
  "attempt_id": "submission_attempt_001",
  "package_id": "",
  "status": "submitted",
  "confidence": 100,
  "confirmation_number": "",
  "ats_application_id": "",
  "confirmation_message": "",
  "confirmation_url": "",
  "dashboard_status": "",
  "submitted_at": "",
  "verified_at": "",
  "evidence": [],
  "warnings": [],
  "requires_user_action": false
}
```

---

# Confidence Guidance

```text id="q5d4b1"
100:
Conclusive ATS record or confirmation identifier.

95–99:
Explicit confirmation page with correct job identity.

80–94:
Strong ATS-specific success signal with supporting evidence.

Below 80:
Normally insufficient for automatic Submitted classification.
```

Confidence thresholds should remain configurable by ATS adapter.

---

# Verification Timeout

Verification should use a bounded timeout.

Example:

```json id="mnncrt"
{
  "initial_page_verification_seconds": 60,
  "dashboard_reconciliation_seconds": 60,
  "maximum_total_verification_seconds": 180
}
```

A timeout should not cause automatic resubmission.

---

# Verification Retry

The verifier may retry evidence collection.

Safe retry actions:

* Re-read page text.
* Wait for confirmation content.
* Refresh the dashboard.
* Reopen application history.
* Reauthenticate.
* Reinspect current URL.
* Reconnect to the browser.

Unsafe retry action:

```text id="4drh7m"
Click Submit again
```

---

# Already Applied Detection

An ATS may display messages such as:

* You have already applied.
* An application already exists.
* You cannot apply to this job again.
* This requisition is already in your profile.
* Application previously submitted.

---

# Already Applied Result

```json id="kx5vwm"
{
  "status": "already_applied",
  "source": "ats_message",
  "matched_job_id": "",
  "existing_application_date": null,
  "confidence": 98
}
```

---

# Already Applied Handling

When detected:

* Do not submit.
* Save the ATS message.
* Search local history.
* Reconcile the existing application.
* Mark package Already Applied.
* Add or update a history record when appropriate.
* Preserve prepared documents.
* Require explicit override only when evidence may refer to a different requisition.

---

# Application Closed Detection

Signals may include:

* Applications are no longer accepted.
* Job is no longer available.
* Requisition has been filled.
* Posting has expired.
* Apply button unavailable with explicit closure message.

---

# Application Closed Handling

* Mark package `Application Closed`.
* Save evidence.
* Update job status.
* Do not create a submission attempt when closure is detected before the click.
* If closure appears after a click, verify whether an application record was created.
* Preserve preparation artifacts.
* Update application history as Closed or Not Submitted.

---

# Submission Failure

A failure may be verified when:

* ATS explicitly rejects the submission request.
* Required validation remains and the final click did not create an application.
* Server response clearly indicates failure.
* Dashboard shows Draft only.
* Session expired before processing and no application record exists.
* Upload failure blocked submission.

---

# Failure Result

```json id="fyyh4v"
{
  "status": "failed",
  "failure_stage": "submission",
  "error_code": "",
  "message": "",
  "application_created": false,
  "retry_allowed": true,
  "evidence": []
}
```

---

# Retry After Verified Failure

A retry may be allowed when:

* Evidence confirms no application was created.
* The error is correctable.
* Duplicate check passes.
* Package remains valid.
* Submission readiness reruns.
* A new submission attempt is created.
* Retry count remains within policy.

---

# Submission Unknown

Submission Unknown is a protected state.

It means:

* Final submission may have occurred.
* Evidence is insufficient.
* Automatic retry could create a duplicate.

---

# Unknown Outcome Causes

Examples:

* Browser crash after click.
* Network connection loss.
* Blank page.
* Unexpected redirect.
* Confirmation page failed to load.
* ATS returned an undocumented response.
* Browser closed.
* Submit control remained visible.
* Dashboard unavailable.
* Session expired during processing.

---

# Unknown Outcome Record

Recommended file:

```text id="7mk39a"
submission/unknown_outcome.json
```

Example:

```json id="9wyyd2"
{
  "package_id": "",
  "attempt_id": "",
  "status": "submission_unknown",
  "reason": "Browser crashed after the final click and dashboard status could not be loaded.",
  "known_evidence": [],
  "missing_evidence": [
    "confirmation_page",
    "dashboard_status"
  ],
  "automatic_retry_allowed": false,
  "required_actions": [
    "Open the ATS dashboard and verify application status."
  ],
  "created_at": ""
}
```

---

# Unknown Outcome Rules

When status is Submission Unknown:

* Do not create another submission attempt.
* Do not mark the package Failed.
* Do not mark the package Submitted.
* Pause the queue by default.
* Preserve the browser profile.
* Preserve the attempt record.
* Preserve screenshots and URLs.
* Attempt dashboard reconciliation.
* Request user verification when needed.
* Allow explicit resolution later.

---

# Unknown Outcome Resolution

Possible resolutions:

```text id="wuxfg6"
submission_unknown -> submitted
submission_unknown -> failed
submission_unknown -> already_applied
submission_unknown -> application_closed
```

Resolution should include evidence and an audit record.

---

# Unknown Outcome Resolution Model

```json id="3haj34"
{
  "package_id": "",
  "previous_status": "submission_unknown",
  "resolved_status": "submitted",
  "resolution_source": "ats_dashboard",
  "evidence": [],
  "resolved_by": "system",
  "resolved_at": ""
}
```

---

# User-Provided Resolution

The user may confirm:

* Application appears as Submitted.
* Application does not exist.
* Application was manually submitted.
* Application should remain unresolved.

User-provided resolution should be recorded distinctly from ATS evidence.

---

# Dashboard Reconciliation

## Responsibility

Use the candidate ATS dashboard to determine submission status.

Conceptual interface:

```text id="c74ym7"
DashboardReconciliationService

    open_dashboard(adapter_id)
    list_applications()
    match_application(package)
    read_application_status(application_reference)
    resolve_submission_attempt(attempt_id)
```

---

# Dashboard Application Record

```json id="9y1t7g"
{
  "ats_application_id": "",
  "job_id": "",
  "requisition_id": "",
  "job_title": "",
  "company": "",
  "location": "",
  "application_date": "",
  "status": "submitted",
  "dashboard_url": ""
}
```

---

# Dashboard Matching Priority

1. Exact ATS application ID.
2. Exact requisition ID.
3. Exact job ID.
4. Exact job title and location.
5. Job title, company, and application date.
6. Strong multi-field similarity.

A title-only match is insufficient.

---

# Dashboard Status Normalization

ATS platforms may use labels such as:

```text id="z3b6da"
Submitted
Application Received
Under Review
In Process
Active
Interview
Not Selected
Withdrawn
Draft
Incomplete
```

Normalize these into internal statuses.

---

# Internal Application Statuses

Recommended current-status values:

```text id="p1ai8a"
discovered
selected
preparing
ready
queued
in_progress
waiting_for_user
ready_for_review
submission_unknown
submitted
under_review
assessment
interview
offer
rejected
withdrawn
closed
skipped
failed
already_applied
archived
```

---

# Submission Status vs Recruitment Status

These should be separate.

## Submission Status

Describes whether the application was submitted.

```text id="26wjod"
not_submitted
submitted
submission_unknown
```

## Recruitment Status

Describes the employer's later process.

```text id="5jy6v1"
under_review
assessment
interview
offer
rejected
withdrawn
closed
```

A rejected application remains successfully submitted.

---

# Application History System

## Responsibility

Maintain a durable local history of all relevant application activity.

Conceptual interface:

```text id="rufg7h"
ApplicationHistoryService

    create_record(package)
    update_record(package_id, changes)
    record_submission(result)
    record_status_change(package_id, status)
    find_by_job_id(job_id)
    find_duplicates(job)
    list_records(filters)
    reconcile_packages()
    reconcile_tracker_files()
    export_csv()
    export_xlsx()
```

---

# History Storage Strategy

The MVP should use:

```text id="hk2dqq"
user_data/
    application_history/
        applications.csv
        applications.xlsx
        events.jsonl
        sync_state.json
        backups/
```

The Application Package remains the detailed source of truth.

CSV and XLSX provide a convenient summarized history.

---

# Source of Truth

Recommended source hierarchy:

1. Application Package submission artifacts.
2. Application Package workflow and review state.
3. Append-only history event log.
4. CSV and XLSX summary trackers.

CSV and XLSX should not be the only record of submission evidence.

---

# Application History Record

Each job should have one primary history record per application package.

Recommended fields:

```text id="xc98lc"
history_record_id
package_id
candidate_profile_id
company
job_title
job_id
requisition_id
department
location
country
remote_status
employment_type
job_source
job_url
application_url
ats_platform
date_posted
date_discovered
date_selected
date_prepared
date_queued
date_applied
last_status_date
match_score
recommendation
application_status
submission_status
recruitment_status
automation_mode
resume_filename
resume_version
cover_letter_filename
cover_letter_version
confirmation_number
ats_application_id
confirmation_url
submission_attempt_count
duplicate_override
requires_follow_up
next_follow_up_date
notes
created_at
updated_at
```

---

# Minimal MVP CSV Schema

A smaller MVP may begin with:

```text id="ib58gy"
package_id
company
job_title
job_id
location
country
job_url
application_url
date_posted
date_discovered
date_applied
match_score
application_status
resume_filename
cover_letter_filename
ats_platform
confirmation_number
notes
```

The schema should remain extensible.

---

# CSV Requirements

The CSV writer should:

* Use UTF-8 encoding.
* Include a stable header.
* Quote values safely.
* Preserve commas and line breaks.
* Use ISO date formats.
* Avoid duplicate rows.
* Write atomically.
* Create a backup before destructive rewrites.
* Preserve unknown columns during compatible updates when possible.

---

# CSV Date Format

Recommended:

```text id="5f84ep"
YYYY-MM-DD
```

For timestamps:

```text id="xjczuf"
YYYY-MM-DDTHH:MM:SS-04:00
```

---

# CSV Atomic Write

Recommended sequence:

```text id="o19bj9"
Read Current CSV
        |
        v
Apply In-Memory Update
        |
        v
Write Temporary File
        |
        v
Validate Temporary File
        |
        v
Replace Original File Atomically
```

---

# CSV Backup

Before replacing the file, store:

```text id="5rsldu"
backups/applications_20260712T120000.csv
```

Retention may limit the number of backups.

---

# XLSX Requirements

The XLSX tracker should be designed for human review.

Recommended workbook sheets:

```text id="nhay94"
Applications
Status Summary
Companies
Monthly Activity
Settings
```

The MVP may start with only `Applications`.

---

# Applications Sheet

Recommended columns:

* Package ID.
* Company.
* Job Title.
* Job ID.
* Location.
* Country.
* Date Posted.
* Date Applied.
* Match Score.
* Application Status.
* Recruitment Status.
* ATS Platform.
* Resume.
* Cover Letter.
* Confirmation Number.
* Follow-Up Date.
* Notes.

---

# XLSX Formatting

The workbook should use:

* Frozen header row.
* Filters.
* Consistent date formats.
* Text wrapping for Notes.
* Appropriate column widths.
* Status data validation where useful.
* Hyperlinks for job and confirmation URLs.
* No formulas that require online services.
* No macros.

---

# Status Summary Sheet

A future summary sheet may display:

* Total applications.
* Submitted applications.
* Applications under review.
* Interviews.
* Offers.
* Rejections.
* Unknown submissions.
* Applications by month.
* Applications by company.
* Applications by ATS.
* Average match score.

The package history remains the authoritative data source.

---

# Workbook Safety

The XLSX writer should:

* Preserve workbook readability.
* Avoid macros.
* Validate the file after saving.
* Create backups.
* Recover from a corrupt workbook using CSV or package records.
* Avoid storing sensitive demographic or legal answers.

---

# History Record Identity

Use `package_id` as the primary local key.

Additional deduplication keys may include:

* ATS application ID.
* Job ID.
* Requisition ID.
* Canonical application URL.
* Company, title, and location.

---

# History Record Creation

A history record may be created when:

* A package is created.
* A package becomes Ready.
* A package enters the queue.
* Browser execution begins.

Creating records before submission supports complete activity tracking.

The `submission_status` should remain `not_submitted` until verified.

---

# History Event Log

Use an append-only JSON Lines file:

```text id="b4iiyy"
application_history/events.jsonl
```

---

# History Event Model

```json id="uaecoa"
{
  "event_id": "",
  "sequence": 1,
  "package_id": "",
  "event_type": "submission_verified",
  "previous_status": "in_progress",
  "new_status": "submitted",
  "source": "submission_verifier",
  "metadata": {},
  "created_at": ""
}
```

---

# History Event Types

```text id="8ocfxw"
job_discovered
job_selected
package_created
preparation_started
preparation_completed
readiness_passed
queued
execution_started
waiting_for_user
review_ready
review_approved
submission_attempt_created
submission_click_initiated
submission_verified
submission_failed
submission_unknown
submission_resolved
already_applied_detected
application_closed
status_updated
interview_recorded
offer_recorded
rejection_recorded
withdrawal_recorded
history_corrected
tracker_synced
tracker_sync_failed
```

---

# Append-Only Audit Principle

History events should not be silently deleted or rewritten.

Corrections should create new events.

Example:

```text id="xfxfyj"
Incorrect:
Delete the old Submitted event.

Correct:
Add a status-correction event explaining the change.
```

---

# Current Status Derivation

Current history status may be derived from the latest valid status event.

The CSV and XLSX files should store the current summarized status.

The event log preserves how that status changed.

---

# History Synchronization Workflow

```text id="z7jb6e"
Package State Change
        |
        v
Write History Event
        |
        v
Update Current History Record
        |
        v
Write CSV
        |
        v
Write XLSX
        |
        v
Verify Both Files
        |
        v
Write Sync State
```

---

# Sync State

Recommended file:

```text id="y44jvb"
application_history/sync_state.json
```

Example:

```json id="8ixuw4"
{
  "last_event_sequence": 142,
  "last_csv_sync_at": "",
  "last_xlsx_sync_at": "",
  "csv_status": "success",
  "xlsx_status": "success",
  "pending_package_ids": []
}
```

---

# Idempotent Synchronization

History synchronization must be safe to repeat.

A retry should:

* Find the existing package row.
* Update it rather than append another row.
* Avoid duplicate history events for the same operation.
* Use stable event or operation IDs.
* Verify the resulting record.

---

# Sync Idempotency Key

Examples:

```text id="5nqtl3"
package_id + event_type + workflow_stage
package_id + submission_attempt_id + submission_verified
package_id + status_update_id
```

---

# Partial Sync Failure

Possible outcomes:

```text id="fepfmp"
Package updated
Event log updated
CSV updated
XLSX failed
```

Handling:

* Preserve package and event-log success.
* Mark XLSX sync pending.
* Retry XLSX only.
* Do not create duplicate CSV rows.
* Do not resubmit the application.

---

# Tracker Reconciliation

## Responsibility

Repair disagreement between packages, event log, CSV, and XLSX.

Conceptual interface:

```text id="sgomra"
HistoryReconciliationService

    scan_packages()
    scan_event_log()
    scan_csv()
    scan_xlsx()
    identify_conflicts()
    rebuild_summary_records()
    repair_trackers()
```

---

# Reconciliation Priority

When records conflict:

1. Verified package submission evidence.
2. Package status and workflow state.
3. Append-only event log.
4. CSV.
5. XLSX.
6. User annotation.

User corrections should be stored as explicit history events.

---

# Reconciliation Example

```text id="vhf10o"
Package:
Submitted

CSV:
In Progress

XLSX:
Submitted

Resolution:
Update CSV to Submitted.
```

---

# Missing Tracker Record

If a submitted package has no CSV or XLSX row:

* Recreate the row from package metadata.
* Preserve original submitted timestamp.
* Add a reconciliation event.
* Verify no duplicate exists.

---

# Orphan Tracker Record

An orphan record has no corresponding package.

Possible causes:

* Imported historical application.
* Package deleted.
* Manual record.
* Corrupt package directory.

The system should not delete it automatically.

Mark its source:

```text id="1x6drx"
manual
imported
package_missing
```

---

# Manual History Records

The user should be able to add applications completed outside the platform.

Required fields may include:

* Company.
* Job title.
* Date applied.
* Job URL.
* Status.
* Resume used.
* Notes.

Manual records should have:

```text id="5fkbtj"
source = manual
```

and may not have an Application Package.

---

# Imported History

Future versions may import:

* Existing CSV.
* Existing XLSX.
* ATS exports.
* User-maintained trackers.

Imported records should receive stable local history IDs.

---

# Duplicate Application Detector

## Responsibility

Prevent repeat applications to the same requisition.

Conceptual interface:

```text id="sn27ab"
DuplicateApplicationService

    check_job(job)
    check_package(package_id)
    check_before_queue(package_id)
    check_before_execution(package_id)
    check_before_submission(package_id)
    compare_with_history(job)
    compare_with_packages(job)
```

---

# Duplicate Check Timing

Run duplicate checks:

1. During job discovery.
2. Before package creation.
3. Before queue admission.
4. Before browser execution.
5. Immediately before submission.
6. During history synchronization.

---

# Duplicate Match Levels

```text id="6tqjio"
exact
strong
possible
none
```

---

## Exact Duplicate

Examples:

* Same job ID.
* Same requisition ID.
* Same ATS application ID.
* Same canonical application URL.

---

## Strong Duplicate

Examples:

* Same company.
* Same title.
* Same location.
* Same posting date.
* Same ATS.
* Application date already recorded.

---

## Possible Duplicate

Examples:

* Same company and title but different job ID.
* Same role in another location.
* Reposted job.
* Similar requisition.

Possible duplicates should not be blocked automatically without sufficient evidence.

---

# Duplicate Result

```json id="tlf2qr"
{
  "status": "exact",
  "confidence": 100,
  "matched_records": [
    {
      "package_id": "",
      "job_id": "",
      "date_applied": "",
      "application_status": "submitted"
    }
  ],
  "automatic_block": true
}
```

---

# Reposted Jobs

A reposted job may have:

* Same title.
* Same company.
* New job ID.
* New posting date.
* Different location.
* Changed description.

The system should not automatically classify it as an exact duplicate.

Candidate rules may define whether to reapply.

---

# Reapplication Rules

Example:

```json id="xm5np1"
{
  "duplicate_rules": {
    "allow_different_requisition": true,
    "allow_reapply_after_days": 180,
    "block_same_job_id": true,
    "review_same_company_title": true
  }
}
```

---

# Duplicate Override

The user may override a duplicate block.

Required override record:

```json id="db9g2i"
{
  "override_id": "",
  "package_id": "",
  "matched_package_id": "",
  "reason": "Different requisition and location.",
  "approved_by": "user",
  "approved_at": ""
}
```

The override should be rechecked immediately before submission.

---

# Application Status Updates

The user should be able to update later recruitment outcomes.

Examples:

* Under Review.
* Assessment.
* Recruiter Contact.
* Interview.
* Final Interview.
* Offer.
* Rejected.
* Withdrawn.
* Position Closed.

---

# Status Update Model

```json id="4xklre"
{
  "status_update_id": "",
  "package_id": "",
  "previous_status": "submitted",
  "new_status": "interview",
  "effective_date": "",
  "source": "user",
  "notes": "",
  "created_at": ""
}
```

---

# Status Source

Supported sources:

```text id="20xf1y"
system
ats_dashboard
user
email_integration
calendar_integration
import
reconciliation
```

The MVP may primarily use system and user sources.

---

# Status History

The system should preserve every status change.

Example:

```text id="h7x3ba"
Submitted
    |
    v
Under Review
    |
    v
Interview
    |
    v
Rejected
```

The current tracker row shows Rejected.

The event log preserves the full sequence.

---

# Application Notes

Users may attach notes such as:

* Recruiter name.
* Interview preparation notes.
* Referral.
* Salary range.
* Follow-up date.
* Reasons for skipping.
* Outcome details.

Notes should remain separate from system evidence.

---

# Follow-Up Tracking

Optional history fields:

* Requires follow-up.
* Follow-up date.
* Follow-up type.
* Contact.
* Follow-up notes.

Example:

```json id="j3v7bb"
{
  "requires_follow_up": true,
  "next_follow_up_date": "2026-07-20",
  "follow_up_type": "recruiter_email"
}
```

---

# Withdrawal Tracking

When the user withdraws:

* Set recruitment status Withdrawn.
* Preserve original submission evidence.
* Record withdrawal date.
* Record reason optionally.
* Do not change submission status from Submitted.

---

# Rejection Tracking

A rejection is a later recruitment status.

It should not change:

```text id="zd1h22"
submission_status = submitted
```

It should update:

```text id="aykd4q"
recruitment_status = rejected
```

---

# Offer Tracking

Offer records may include:

* Offer date.
* Role.
* Location.
* Compensation.
* Deadline.
* Accepted or declined.

Detailed compensation should remain optional and locally protected.

---

# Application History Search

The system should support filtering by:

* Company.
* Job title.
* Date applied.
* Status.
* Country.
* Location.
* ATS.
* Match score.
* Resume version.
* Queue.
* Submission outcome.
* Follow-up date.

---

# History Summary

Useful summaries:

* Applications submitted this week.
* Applications submitted this month.
* Applications by company.
* Applications by role type.
* Applications awaiting follow-up.
* Unknown submissions.
* Interview conversion.
* Offer conversion.
* Rejection count.

These are descriptive local statistics, not predictive guarantees.

---

# History Export

The user should be able to export:

* Full CSV.
* Full XLSX.
* Filtered CSV.
* Submitted applications only.
* Applications by date range.
* Applications requiring action.

Export should not include hidden sensitive package details unless explicitly selected.

---

# Package Submission Directory

Recommended structure:

```text id="e8kjrz"
submission/
    pre_submission_snapshot.json
    attempts/
        submission_attempt_001.json
    evidence/
        evidence.json
        confirmation.txt
        confirmation_metadata.json
        dashboard_record.json
    result.json
    unknown_outcome.json
    resolution.json
    tracker_sync.json
```

---

# Submission Result File

Recommended:

```text id="0b7w4d"
submission/result.json
```

Example:

```json id="myi06w"
{
  "package_id": "",
  "attempt_id": "submission_attempt_001",
  "status": "submitted",
  "submitted_at": "",
  "verified_at": "",
  "company": "",
  "job_title": "",
  "job_id": "",
  "confirmation_number": "",
  "ats_application_id": "",
  "confirmation_url": "",
  "evidence_count": 3,
  "verification_confidence": 100
}
```

---

# Confirmation Text File

Store concise confirmation text in:

```text id="ujul34"
submission/evidence/confirmation.txt
```

Do not store the entire webpage unless needed.

---

# Confirmation Metadata

```json id="rcymx1"
{
  "page_title": "",
  "confirmation_heading": "",
  "confirmation_message": "",
  "confirmation_number": "",
  "ats_application_id": "",
  "confirmation_url": "",
  "captured_at": "",
  "screenshot_path": ""
}
```

---

# Submission Evidence Retention

Submission evidence should normally be retained while the application history is retained.

Evidence may include sensitive information.

Retention should be configurable.

---

# Retention Configuration

```json id="w5l3jr"
{
  "submission_retention": {
    "submitted_packages": "keep",
    "confirmation_screenshots_days": 365,
    "failed_attempt_screenshots_days": 90,
    "browser_logs_days": 30,
    "history_events": "keep",
    "tracker_backups_count": 20
  }
}
```

---

# Historical Immutability

After verified submission, the following should not be silently modified:

* Job snapshot.
* Submitted resume.
* Submitted cover letter.
* Submitted answer set.
* Submission timestamp.
* Confirmation number.
* ATS application ID.
* Confirmation evidence.
* Submission attempt.

Corrections should create annotations or amended metadata.

---

# History Correction

A user may correct an inaccurate tracker value.

Example:

```json id="sn6foz"
{
  "correction_id": "",
  "package_id": "",
  "field": "location",
  "previous_value": "Boston, MA",
  "corrected_value": "Cambridge, MA",
  "reason": "Tracker import used the wrong city.",
  "corrected_by": "user",
  "created_at": ""
}
```

The original package job snapshot should remain preserved unless it was itself incorrect and explicitly versioned.

---

# Submitted Artifact Fingerprints

Store hashes for:

* Resume.
* Cover letter.
* Answer set.
* Form snapshot.
* Confirmation evidence when useful.

This proves which versions were used.

---

# Artifact Fingerprint Example

```json id="79frq3"
{
  "resume_hash": "",
  "cover_letter_hash": null,
  "answer_set_hash": "",
  "form_snapshot_hash": "",
  "confirmation_screenshot_hash": ""
}
```

---

# Manual Submission

The user may complete an application manually.

The system may record it as Submitted when:

* The user confirms submission.
* Submission date is supplied.
* Job identity is known.
* Manual-source status is recorded.

This should be distinguished from system-verified submission.

---

# Manual Submission Result

```json id="owbs95"
{
  "status": "submitted",
  "verification_source": "user",
  "verification_confidence": null,
  "submitted_at": "",
  "confirmation_number": null,
  "notes": "Submitted manually in the browser."
}
```

---

# Verification Source

Supported verification sources:

```text id="0a4vju"
ats_confirmation_page
ats_dashboard
network_response
email_confirmation
user
import
reconciliation
```

---

# User Confirmation Policy

User confirmation may resolve a manual application.

For an automated submission with an uncertain final click, user confirmation should include a specific observation such as:

```text id="ark7bu"
The ATS dashboard lists the application as Submitted.
```

This is stronger than:

```text id="8xaf7k"
I think it probably went through.
```

---

# Email Confirmation Integration

A future authorized email integration may search for:

* Application received.
* Thank you for applying.
* Confirmation number.
* Job title.
* Company.
* Requisition ID.

Email evidence should be matched carefully and should not be assumed to represent the latest attempt without job identity.

The MVP does not require email integration.

---

# Email Evidence Strength

An email confirmation may be conclusive or strong when it contains:

* Correct company.
* Correct job title or job ID.
* Confirmation text.
* Timestamp after the submission attempt.

---

# Security and Privacy

The submission and history system should:

* Store all records locally.
* Restrict package and history directory permissions where supported.
* Exclude credentials.
* Exclude cookies.
* Exclude authentication tokens.
* Redact sensitive IDs from routine logs.
* Avoid storing full demographic or legal answers in trackers.
* Avoid placing government identifiers in CSV or XLSX.
* Prevent public serving of history files.
* Support user-controlled deletion and retention.

---

# Tracker Data Minimization

CSV and XLSX should contain operational summary data.

They should not normally contain:

* Social Security number.
* Passport number.
* Immigration document number.
* Full demographic answers.
* Criminal-history details.
* Passwords.
* Session information.
* Complete application-answer text.
* Full home address.

Detailed data remains inside protected Application Packages.

---

# Screenshot Privacy

Confirmation screenshots may contain:

* Name.
* Email.
* Phone.
* Application ID.
* Demographic sections.
* Salary answers.

The system should:

* Store screenshots locally.
* Avoid external upload by default.
* Allow redaction.
* Apply retention rules.
* Avoid using screenshots as tracker attachments unless necessary.

---

# Logs

Submission logs may include:

* Package ID.
* Attempt ID.
* Submission state.
* Submit-control label.
* Evidence types.
* Verification status.
* Confirmation number when configured.
* Error category.
* Retry count.
* Duration.

Logs should not include:

* Full application answers.
* Government IDs.
* Cookies.
* Authentication headers.
* Passwords.

---

# Submission Metrics

Useful local metrics include:

* Submission attempts.
* Verified submissions.
* Verified failures.
* Already-applied detections.
* Closed-job detections.
* Unknown outcomes.
* Unknown outcomes later resolved.
* Average verification duration.
* Dashboard reconciliation success.
* Duplicate submissions prevented.
* Tracker-sync failures.
* Manual submissions.
* Applications by ATS.

---

# History Metrics

Useful local metrics include:

* Jobs discovered.
* Jobs selected.
* Packages prepared.
* Applications submitted.
* Applications under review.
* Assessments.
* Interviews.
* Offers.
* Rejections.
* Withdrawals.
* Submission-to-interview rate.
* Interview-to-offer rate.
* Applications by month.
* Applications by company.
* Applications by job family.

These metrics should be interpreted as personal tracking data, not hiring predictions.

---

# Failure Handling

Recommended error types:

```text id="v2f2vh"
PreSubmissionSnapshotError
SubmissionLockError
SubmissionAttemptError
SubmissionActionError
SubmissionVerificationError
SubmissionEvidenceError
SubmissionUnknownError
DashboardReconciliationError
DuplicateApplicationError
HistoryRecordError
HistoryEventError
CSVWriteError
XLSXWriteError
TrackerSyncError
HistoryReconciliationError
HistoryImportError
HistoryExportError
```

---

# Error Classification

Errors should be classified as:

```text id="h0n4mv"
retryable_before_click
retryable_verification
requires_user_action
non_retryable
submission_outcome_unknown
```

---

# Retryable Before Click

Examples:

* Snapshot write failed.
* Lock could not be acquired.
* Submit control disappeared before interaction.
* Browser validation failed.
* Readiness became stale.

No final action occurred.

---

# Retryable Verification

Examples:

* Confirmation content loads slowly.
* Dashboard temporarily unavailable.
* Browser reconnect required.
* Adapter verification timed out.

Retry only evidence collection, not the final click.

---

# Requires User Action

Examples:

* ATS dashboard login required.
* Manual application status verification required.
* Unknown outcome cannot be resolved.
* User must confirm manual submission.

---

# Non-Retryable

Examples:

* Application closed.
* Exact duplicate.
* Candidate cancelled.
* Untrusted destination.
* History file is read-only until repaired.

---

# Recovery After Application Restart

On startup:

1. Find packages with submission attempts in non-terminal states.
2. Load submission locks.
3. Determine whether a final click was initiated.
4. If no click occurred, permit controlled recovery.
5. If click occurred, begin verification.
6. Reconcile with ATS dashboard.
7. Mark Submitted, Failed, or Submission Unknown.
8. Repair tracker synchronization.
9. Never automatically create a second attempt.

---

# Interrupted Attempt Reconciliation

Possible attempt states after restart:

```text id="cp8nlv"
attempt_created
click_initiated
verification_pending
```

---

## Attempt Created

If no click timestamp exists and browser evidence confirms no action:

* Mark failed or cancelled before click.
* Release the lock.
* Rerun readiness.

## Click Initiated

* Assume submission may have occurred.
* Verify before any retry.

## Verification Pending

* Resume evidence collection.
* Do not click Submit.

---

# History Backup and Recovery

History backups should be stored locally.

Recommended backup triggers:

* Before CSV rewrite.
* Before XLSX rewrite.
* Before schema migration.
* Before bulk import.
* Before reconciliation repair.

---

# Backup Structure

```text id="lppwus"
application_history/
    backups/
        applications_20260712T120000.csv
        applications_20260712T120000.xlsx
        events_20260712T120000.jsonl
```

---

# Tracker Recovery

If CSV is corrupted:

* Rebuild from packages and event log.
* Validate row count.
* Preserve the corrupt file for inspection.
* Create a recovery event.

If XLSX is corrupted:

* Rebuild from CSV or current records.
* Preserve the corrupt workbook.
* Validate the new workbook.

---

# Schema Versioning

CSV, XLSX, and event records should include or reference a schema version.

Example:

```json id="ywa447"
{
  "history_schema_version": "1.0"
}
```

For CSV, schema version may be stored in `sync_state.json`.

For XLSX, it may be stored in the Settings sheet.

---

# Schema Migration

A migration should:

1. Back up current files.
2. Read existing records.
3. Map old fields to new fields.
4. Preserve unknown data.
5. Write new files.
6. Validate record counts.
7. Record migration result.

---

# Application History User Interface

The history interface should display:

* Company.
* Job title.
* Location.
* Date applied.
* Match score.
* Application status.
* Recruitment status.
* ATS platform.
* Resume used.
* Follow-up date.
* Notes.

---

# History Detail View

A detailed record may show:

* Job snapshot.
* Package ID.
* Submission attempt.
* Confirmation evidence.
* Resume version.
* Cover-letter version.
* Status timeline.
* Queue and workflow IDs.
* Review report.
* Follow-up notes.
* User corrections.

Sensitive fields should remain hidden by default.

---

# Submission Verification User Interface

For a verified submission:

```text id="7wh0qj"
Application Submitted

Company: Google
Role: Senior Software Engineer
Submitted: July 12, 2026
Confirmation Number: APP-483726
Resume: Suhas_Arudi_Google_Resume.pdf
History Status: Synchronized
```

---

# Submission Unknown Interface

```text id="zwghv7"
Submission Status Unknown

The final submission action was initiated, but no confirmation was detected.

Do not submit again yet.

Recommended action:
Open the ATS dashboard and check whether the application appears as Submitted.
```

---

# History Controls

The user should be able to:

```text id="04o23t"
Open application record
Open job URL
Open confirmation URL
View submission evidence
Update recruitment status
Add note
Set follow-up date
Resolve unknown submission
Mark manual submission
Correct tracker field
Archive record
Export records
```

---

# Reconciliation Interface

When conflicts exist, show:

* Package status.
* CSV status.
* XLSX status.
* Event-log status.
* Recommended resolution.
* Evidence source.

Example:

```text id="olez89"
Package: Submitted
CSV: In Progress
XLSX: Submitted

Recommended action:
Update CSV from verified package evidence.
```

---

# Testing Strategy

Testing should use controlled forms and synthetic application packages.

---

# Unit Tests

Unit-test:

* Evidence-strength classification.
* Confirmation-message extraction.
* Confirmation-number extraction.
* Submission-state transitions.
* Unknown-outcome rules.
* Duplicate matching.
* History-row identity.
* CSV quoting.
* CSV atomic writes.
* XLSX updates.
* Event ordering.
* Idempotency keys.
* Status normalization.
* Tracker reconciliation.
* Schema migration.

---

# Submission Integration Tests

Integration-test:

* Strong confirmation page.
* Confirmation number extraction.
* ATS dashboard verification.
* Verified failure before click.
* Verified failure after click.
* Browser crash before click.
* Browser crash after click.
* Network timeout after click.
* Session expiration.
* Already-applied message.
* Closed-job message.
* Weak confirmation only.
* Unknown-outcome resolution.
* Duplicate prevention.
* Tracker synchronization.
* Tracker-sync retry.

---

# History Integration Tests

Integration-test:

* Package creation to history record.
* Queue and execution status updates.
* Verified submission to CSV.
* Verified submission to XLSX.
* Manual submission record.
* Recruitment-status update.
* Follow-up update.
* CSV rebuild.
* XLSX rebuild.
* Package-history reconciliation.
* Duplicate record prevention.
* Imported record handling.
* Orphan record preservation.

---

# Required Test Scenarios

## Explicit Confirmation Page

After Submit, the page says:

```text id="no861r"
Your application has been submitted.
```

The correct job ID is visible.

Expected:

* Status Submitted.
* Confirmation evidence stored.
* History synchronized.

---

## Confirmation Number

A confirmation page contains:

```text id="7zrk0t"
Application Reference: APP-12345
```

Expected:

* Reference extracted exactly.
* Stored in package and trackers.
* Submission confidence high.

---

## Dashboard Submitted Status

Confirmation page is unavailable, but ATS dashboard shows the correct requisition as Submitted.

Expected:

* Status Submitted.
* Dashboard record stored as evidence.
* No retry.

---

## Weak Redirect

After Submit, browser returns to the career homepage.

No success text or dashboard record is available.

Expected:

* Submission Unknown.
* No automatic retry.
* User action required.

---

## Browser Crash Before Click

The browser crashes before the final action.

Expected:

* Failed Before Click.
* Retry may be allowed after readiness checks.

---

## Browser Crash After Click

The browser crashes immediately after the final action.

Expected:

* Verification through dashboard.
* Submitted when record exists.
* Submission Unknown when not verifiable.
* No second click.

---

## Network Timeout

The final request times out.

The ATS dashboard later shows Submitted.

Expected:

* Submitted.
* Network timeout treated as non-conclusive.
* No retry.

---

## Validation Error

The final page shows a required-field error and remains editable.

No application record exists.

Expected:

* Failed or Changes Required.
* Correct the field.
* New attempt allowed after review.

---

## Already Applied Message

ATS says:

```text id="fv0mj2"
You have already applied to this position.
```

Expected:

* Already Applied.
* History searched.
* Existing record linked when possible.
* No submission attempt repeated.

---

## Application Closed

ATS says applications are no longer accepted.

Expected:

* Application Closed.
* No submission.
* History updated.
* Package preserved.

---

## Submission Unknown Resolved as Submitted

The user opens the ATS dashboard and confirms the application appears.

Expected:

* Unknown status resolved to Submitted.
* Resolution event written.
* CSV and XLSX updated.

---

## Submission Unknown Resolved as Failed

ATS dashboard contains no application, and ATS support confirms no submission was created.

Expected:

* Unknown status resolved to Failed.
* Retry may be permitted after explicit review.

---

## Duplicate Job ID

History contains a Submitted record with the same job ID.

Expected:

* Exact duplicate.
* Queue and submission blocked.
* Override required.

---

## Similar Requisition

Same title and company, but different job ID and location.

Expected:

* Possible duplicate warning.
* Not automatically blocked.
* Candidate rule applied.

---

## CSV Failure After Submission

Package is verified Submitted, but CSV write fails.

Expected:

* Package remains Submitted.
* Sync marked pending.
* No resubmission.
* CSV retry remains idempotent.

---

## XLSX Corruption

The workbook cannot be opened.

Expected:

* Preserve corrupt file.
* Rebuild XLSX from current history records.
* CSV and package records remain unchanged.

---

## Duplicate Tracker Sync

Tracker synchronization runs twice.

Expected:

* One row per package.
* Existing row updated.
* No duplicate event for the same synchronization operation.

---

## Manual Application

User reports that they manually submitted an application.

Expected:

* Manual history record created.
* Verification source marked User.
* No automated confirmation claim.

---

## Rejection Update

A submitted application is later rejected.

Expected:

* Submission status remains Submitted.
* Recruitment status changes to Rejected.
* Status event added.

---

## History Conflict

Package says Submitted, CSV says Failed, XLSX says Submitted.

Expected:

* Verified package evidence wins.
* CSV corrected.
* Reconciliation event stored.

---

## Sensitive Data Protection

Confirmation screenshot contains demographic answers.

Expected:

* Screenshot stored locally.
* Tracker excludes demographic values.
* Routine logs remain redacted.

---

# Submission Verification Completion Criteria

The Submission Verification system is complete when:

* Pre-submission snapshots are stored.
* Submission locks prevent concurrent attempts.
* Every final click has an attempt record.
* The irreversible action boundary is explicit.
* Strong and weak evidence are distinguished.
* ATS-specific verification is supported.
* Generic verification is conservative.
* Confirmation numbers and application IDs are extracted.
* Dashboard reconciliation works for supported ATS platforms.
* Browser crashes before and after the final click are handled differently.
* Network timeouts do not trigger blind retries.
* Already-applied and closed-job outcomes are detected.
* Submission Unknown blocks automatic resubmission.
* Unknown outcomes can be resolved later.
* Submission evidence is retained locally.
* Verified outcomes update the Application Package.
* Tracker failure does not alter submission truth.
* Controlled end-to-end tests pass.

---

# Application History Completion Criteria

The Application History system is complete when:

* One stable history record exists per package.
* CSV history can be created and updated.
* XLSX history can be created and updated.
* Writes are atomic and backed up.
* History events are append-only.
* Current statuses can be derived.
* Submission and recruitment statuses remain separate.
* Duplicate records are prevented.
* Duplicate application checks use history and packages.
* Manual applications can be recorded.
* Later status changes can be recorded.
* Follow-up fields are supported.
* Reconciliation can repair CSV and XLSX.
* Corrupt trackers can be rebuilt.
* Schema migration is supported.
* Sensitive application details are excluded from trackers.
* History remains local and user-controlled.
* Filtering and export work.
* Integration tests cover submission-to-history synchronization.

---

# Definition of Submission and History Completion

The complete Submission Verification and Application History phase is finished when:

* A final button click is never treated as proof by itself.
* Every submission has a durable attempt record.
* Verified submission requires strong evidence.
* Confirmation evidence is stored with the correct job identity.
* Unknown outcomes are protected against automatic retry.
* ATS dashboards can resolve uncertain outcomes where supported.
* Duplicate applications are blocked at multiple workflow stages.
* Application Packages remain the detailed source of truth.
* CSV and XLSX provide reliable summarized history.
* Tracker updates are idempotent.
* Tracker failures cannot cause resubmission.
* Recruitment outcomes can be updated over time.
* Historical records preserve submitted artifact versions.
* Corrections and status changes create audit events.
* Privacy rules protect sensitive candidate information.
* Recovery after browser or application restart is safe.
* Submission and history workflows pass controlled regression tests.

---

# Summary

The Submission Verification system determines whether an application was actually submitted.

It must distinguish between:

```text id="t6r1q8"
Submit was clicked
```

and:

```text id="lrj8ch"
Submission was verified
```

It uses:

* Confirmation messages.
* Confirmation numbers.
* ATS application IDs.
* Dashboard status.
* ATS-specific signals.
* Structured browser evidence.
* Conservative generic verification.

When evidence is insufficient, the correct result is:

```text id="nl0lmb"
Submission Unknown
```

not an automatic retry.

The Application History system preserves the complete lifecycle of each application locally.

It maintains:

* Application Package evidence.
* Append-only status events.
* CSV tracking.
* XLSX tracking.
* Duplicate detection.
* Status updates.
* Follow-up information.
* Audit and reconciliation records.

Together, these systems ensure that the platform can prove what was submitted, avoid duplicate applications, recover from uncertain outcomes, and maintain a trustworthy local history of the candidate's job search.
