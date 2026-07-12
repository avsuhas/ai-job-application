# 08 - Application Queue and Execution Orchestration

## LLM-Powered Autonomous Job Search & Application Platform

Version: 1.0

---

# Purpose

This document defines the Application Queue and Execution Orchestration system responsible for coordinating prepared Application Packages through browser execution, review, submission, recovery, and final tracking.

The orchestration layer is the central workflow controller.

It determines:

* Which applications may enter the queue.
* The order in which applications execute.
* Whether package readiness remains valid.
* Which browser profile and ATS adapter should be used.
* Which workflow stage should run next.
* When execution should pause.
* When user action is required.
* When automatic recovery is safe.
* Whether submission may proceed.
* How final outcomes are persisted.
* How failed or interrupted applications resume.

The orchestrator should not directly perform every specialized task.

It coordinates services such as:

* Application Package Service.
* Application Readiness Service.
* Application Review Service.
* Browser Automation Engine.
* Application Answer Service.
* Resume Service.
* Cover Letter Service.
* ATS Adapters.
* Submission Verifier.
* Local Application Tracker.

---

# Core Principle

The orchestrator controls workflow state, while specialized services perform domain-specific work.

```text
Selected Applications
        |
        v
Application Packages
        |
        v
Readiness Evaluation
        |
        v
Queue Admission
        |
        v
Execution Orchestrator
        |
        +--> Browser Automation
        +--> Runtime Answer Resolution
        +--> Application Review
        +--> User Intervention
        +--> Submission Verification
        |
        v
Application Tracker
```

The orchestrator should never bypass readiness, review, or submission-verification rules merely to keep the queue moving.

---

# Orchestration Objectives

The system should:

* Process selected jobs in a deterministic order.
* Execute only Ready Application Packages.
* Prevent duplicate execution.
* Prevent simultaneous use of the same persistent browser profile.
* Preserve state after every meaningful step.
* Pause safely for login, CAPTCHA, MFA, review, or missing information.
* Resume interrupted workflows.
* Isolate failures to one application.
* Avoid repeating completed work.
* Prevent duplicate submissions.
* Verify submission before marking an application Submitted.
* Continue processing other eligible applications when one package requires attention.
* Provide clear progress and outcome reporting.
* Keep all workflow data local.

---

# Scope

The orchestration system covers:

* Queue creation.
* Queue ordering.
* Queue admission.
* Package locking.
* Browser-session allocation.
* Workflow-state management.
* Stage execution.
* Runtime question resolution.
* Page progression.
* Review coordination.
* Submission coordination.
* Pause and resume.
* Retry and recovery.
* Cancellation.
* Batch execution.
* Result persistence.
* Tracker synchronization.
* Progress reporting.

The orchestration system does not itself:

* Discover jobs.
* Rank jobs.
* Tailor resumes.
* Generate cover letters.
* Generate narrative answers directly.
* Fill browser fields directly.
* Verify browser controls directly.
* Decide candidate facts.
* Bypass CAPTCHA or MFA.
* Infer submission success without evidence.

---

# System Components

```text
Application Execution Platform
    |
    +-- Queue Manager
    +-- Queue Admission Controller
    +-- Execution Orchestrator
    +-- Workflow State Manager
    +-- Package Lock Manager
    +-- Browser Resource Manager
    +-- ATS Adapter Router
    +-- Runtime Answer Coordinator
    +-- Review Coordinator
    +-- Submission Coordinator
    +-- Recovery Coordinator
    +-- User Intervention Manager
    +-- Tracker Synchronization Service
    +-- Execution Event Bus
    +-- Progress Reporter
```

---

# High-Level Workflow

```text
Receive Selected Packages
        |
        v
Evaluate Readiness
        |
        +--> Not Ready --> Exclude and Report
        |
        v
Admit Ready Packages
        |
        v
Order Queue
        |
        v
Acquire Package Lock
        |
        v
Recheck Execution Readiness
        |
        v
Start or Reuse Browser Session
        |
        v
Open Application
        |
        v
Execute Pages Sequentially
        |
        +--> Runtime Question Resolution
        +--> Login / CAPTCHA Pause
        +--> Error Recovery
        |
        v
Application Review
        |
        +--> Correct Issues
        +--> User Review When Required
        |
        v
Submission Readiness Check
        |
        v
Submit
        |
        v
Verify Submission
        |
        +--> Submitted
        +--> Failed
        +--> Submission Unknown
        |
        v
Persist Result
        |
        v
Synchronize Tracker
        |
        v
Release Lock
        |
        v
Continue Queue
```

---

# Queue Model

The Application Queue represents the ordered set of Application Packages awaiting execution.

Example:

```json
{
  "queue_id": "queue_20260712T090000",
  "created_at": "2026-07-12T09:00:00-04:00",
  "status": "running",
  "strategy": "selected_order",
  "browser_profile": "default",
  "items": [
    {
      "queue_item_id": "queue_item_001",
      "package_id": "google_123456_20260712T080000",
      "position": 1,
      "status": "pending",
      "priority": 100
    }
  ]
}
```

---

# Queue Statuses

Supported queue statuses:

```text
created
validating
ready
running
paused
completed
completed_with_errors
cancelled
failed
```

---

## Created

The queue exists but admission validation has not completed.

---

## Validating

Selected packages are undergoing readiness and duplicate checks.

---

## Ready

Queue items have been admitted and ordered.

Execution has not started.

---

## Running

At least one package is executing or the orchestrator is actively advancing the queue.

---

## Paused

Queue execution is suspended.

Possible reasons:

* User paused the queue.
* Browser authentication is required.
* Global provider outage.
* Browser profile conflict.
* System-level error.
* User intervention policy pauses all execution.

---

## Completed

All queue items reached terminal states without unresolved errors.

---

## Completed with Errors

All executable items finished, but one or more packages failed, were blocked, or require user action.

---

## Cancelled

The user cancelled the queue.

---

## Failed

A queue-level error prevented safe continuation.

Individual package failures should not normally fail the entire queue.

---

# Queue Item Model

Each queue item should contain:

```json
{
  "queue_item_id": "queue_item_001",
  "queue_id": "queue_20260712T090000",
  "package_id": "google_123456_20260712T080000",
  "position": 1,
  "priority": 100,
  "status": "pending",
  "attempt_count": 0,
  "maximum_attempts": 3,
  "admitted_at": "",
  "started_at": null,
  "completed_at": null,
  "last_error": null,
  "required_user_action": null
}
```

---

# Queue Item Statuses

Supported statuses:

```text
pending
validating
admitted
waiting
executing
waiting_for_user
waiting_for_review
retry_scheduled
submitted
completed_manual
already_applied
skipped
cancelled
blocked
failed
submission_unknown
```

---

## Pending

The item has not yet passed queue admission.

---

## Validating

Readiness and duplicate checks are running.

---

## Admitted

The package may execute when it reaches the front of the queue.

---

## Waiting

The package is admitted but another package currently owns the required browser resource.

---

## Executing

Browser automation is actively processing the application.

---

## Waiting for User

The workflow requires:

* Login.
* MFA.
* CAPTCHA.
* Missing answer.
* Legal clarification.
* Sensitive field input.
* Manual browser interaction.

---

## Waiting for Review

The form is complete and awaiting configured human review.

---

## Retry Scheduled

Execution failed with a retryable error and may be retried according to policy.

This does not imply background or asynchronous execution. The retry occurs within the active orchestration workflow.

---

## Submitted

Submission was verified.

---

## Completed Manual

The package was prepared for manual completion, and the user marked it completed outside automated submission.

---

## Already Applied

A duplicate application was detected.

---

## Skipped

The package was intentionally excluded.

---

## Cancelled

The user cancelled the package.

---

## Blocked

A non-recoverable policy, eligibility, privacy, or workflow condition prevents execution.

---

## Failed

Execution ended because of a technical or preparation error.

---

## Submission Unknown

The final submission action may have occurred, but no reliable outcome was verified.

Automatic resubmission is prohibited.

---

# Queue Creation

A queue may be created from:

* User-selected jobs.
* User-selected Application Packages.
* The first N ranked jobs.
* All Ready packages within a search result.
* A manually ordered list.
* Packages filtered by company, country, role, or score.

---

# Queue Creation Request

```json
{
  "package_ids": [
    "google_123456_20260712T080000",
    "microsoft_789012_20260712T081000"
  ],
  "strategy": "selected_order",
  "automation_mode": "review",
  "browser_profile": "default",
  "continue_after_package_failure": true
}
```

---

# Queue Creation Validation

Before creating a queue:

* Confirm package IDs exist.
* Remove accidental duplicate package IDs.
* Check package status.
* Verify packages are not already executing.
* Check whether packages already belong to an active queue.
* Confirm user-selected order.
* Confirm queue-size limits.
* Confirm browser profile selection.
* Confirm application mode.

---

# Queue Ordering Strategies

Supported strategies may include:

```text
selected_order
highest_match_first
newest_job_first
oldest_job_first
company_priority
expiring_first
manual_priority
```

---

## Selected Order

Preserve the visible order selected by the user.

This should be the default.

---

## Highest Match First

Sort by candidate-to-job match score.

Tie-breakers:

1. Date posted.
2. User priority.
3. Original selection order.

---

## Newest Job First

Sort by date posted descending.

Jobs without a reliable date should be placed after dated jobs unless the user specifies otherwise.

---

## Expiring First

Prioritize jobs with known deadlines.

Unknown deadlines should not be guessed.

---

## Company Priority

Apply user-defined company preferences.

Example:

```json
{
  "company_priority": {
    "OpenAI": 100,
    "Google": 90,
    "Microsoft": 80
  }
}
```

---

# Queue Ordering Stability

Queue ordering should be stable.

If two items have the same priority, preserve original selection order.

The system should not reorder the queue unexpectedly after execution starts unless:

* The user manually reorders it.
* A package becomes blocked.
* A package requires user action and skip-ahead is enabled.
* A package becomes Already Applied.
* A job closes.

---

# Queue Admission

A package may enter the executable queue only when:

* Browser Execution Readiness is Ready or permitted Ready with Warnings.
* Package status is Ready.
* Duplicate checks pass.
* No prior Submission Unknown state exists.
* Package is not locked.
* Required active artifacts exist.
* Browser prerequisites pass.
* ATS workflow is supported or manual fallback is selected.
* Candidate rules permit execution.

---

# Queue Admission Result

```json
{
  "package_id": "",
  "status": "admitted",
  "admitted_at": "",
  "warnings": [],
  "queue_position": 2,
  "next_action": "wait"
}
```

Possible admission results:

```text
admitted
rejected_not_ready
rejected_duplicate
rejected_locked
rejected_submission_unknown
rejected_unsupported
manual_completion_only
```

---

# Revalidation Before Execution

Readiness may change while a package waits in the queue.

Immediately before execution, recheck:

* Package status.
* File hashes.
* Active resume.
* Required cover letter.
* Prepared answers.
* Candidate rules.
* Duplicate history.
* Job availability.
* Application URL.
* Browser profile.
* Browser health.
* ATS adapter status.
* Prior submission state.

A package that fails revalidation should not execute.

---

# Execution Orchestrator

## Responsibility

Advance one Application Package through its execution workflow.

Conceptual interface:

```text
ExecutionOrchestrator

    execute_queue(queue_id)
    execute_package(package_id)
    resume_package(package_id)
    pause_package(package_id)
    cancel_package(package_id)
    retry_package(package_id)

    run_stage(package_id, stage)
    determine_next_stage(package_id)
    handle_stage_result(package_id, result)
    persist_checkpoint(package_id)
```

---

# Orchestration Rule

The orchestrator should execute one durable workflow step at a time.

After every significant step:

1. Validate the result.
2. Persist state.
3. Emit an event.
4. Determine the next action.
5. Continue only when permitted.

---

# Workflow Stages

Recommended execution stages:

```text
queue_validation
package_lock
pre_execution_readiness
browser_session_start
application_navigation
application_identity_check
page_inspection
runtime_answer_resolution
form_execution
page_validation
page_progression
application_review
manual_review
submission_readiness
final_submission
submission_verification
tracker_sync
cleanup
```

---

# Stage Result Model

```json
{
  "stage": "page_validation",
  "status": "success",
  "started_at": "",
  "completed_at": "",
  "retryable": false,
  "next_stage": "page_progression",
  "warnings": [],
  "error": null,
  "checkpoint_written": true
}
```

Possible stage statuses:

```text
success
success_with_warnings
retryable_failure
non_retryable_failure
waiting_for_user
waiting_for_review
cancelled
submission_unknown
```

---

# Workflow State Model

Recommended execution state:

```json
{
  "workflow_id": "workflow_google_123456",
  "package_id": "google_123456_20260712T080000",
  "queue_id": "queue_20260712T090000",
  "status": "executing",
  "current_stage": "form_execution",
  "current_page": 3,
  "last_completed_stage": "runtime_answer_resolution",
  "next_stage": "page_validation",
  "browser_profile": "default",
  "ats_adapter": "greenhouse",
  "attempt_count": 1,
  "started_at": "",
  "updated_at": "",
  "last_checkpoint": ""
}
```

---

# Workflow Statuses

```text
initialized
running
paused
waiting_for_user
waiting_for_review
recovering
submitting
submitted
completed
blocked
failed
cancelled
submission_unknown
```

---

# Workflow State Persistence

Store workflow state in:

```text
applications/packages/{package_id}/execution/state.json
```

Persist state after:

* Queue admission.
* Package lock acquisition.
* Browser launch.
* Navigation.
* Page inspection.
* Page completion.
* File upload.
* Runtime answer generation.
* User intervention request.
* User intervention completion.
* Application review.
* Approval.
* Submission action.
* Submission verification.
* Tracker synchronization.
* Error.
* Cancellation.

---

# Checkpoints

A checkpoint should capture enough information to resume safely.

Example:

```json
{
  "checkpoint_id": "checkpoint_004",
  "package_id": "",
  "workflow_id": "",
  "stage": "page_completed",
  "page_number": 2,
  "page_url": "",
  "page_signature": "",
  "completed_fields": [],
  "uploaded_files": [],
  "browser_state_reference": "",
  "created_at": ""
}
```

---

# Checkpoint Requirements

A checkpoint should identify:

* Current application.
* Current page.
* Completed pages.
* Completed fields.
* Uploaded documents.
* Runtime answers created.
* Browser URL.
* Page signature.
* Package artifact versions.
* Review status.
* Submission status.
* Whether an irreversible action occurred.

---

# Durable vs Ephemeral State

## Durable State

Must be persisted:

* Workflow status.
* Page completion.
* Answers.
* Upload results.
* Review decisions.
* Submission state.
* Retry counts.
* Errors.
* User actions.

## Ephemeral State

May remain in memory:

* Playwright locator objects.
* Browser page objects.
* Temporary DOM references.
* Short-lived wait conditions.
* Open dropdown state.

The workflow must not rely on ephemeral objects after a restart.

---

# Package Lock Manager

## Responsibility

Prevent two processes or workflows from executing the same package simultaneously.

---

# Lock Types

```text
preparation_lock
execution_lock
review_lock
submission_lock
tracker_sync_lock
```

Only compatible locks may coexist.

---

# Execution Lock

Before browser execution:

* Acquire execution lock.
* Record queue and workflow ID.
* Reject another execution attempt.
* Renew or validate lock during long workflows.
* Release after completion, failure, or cancellation.

---

# Lock File

Recommended:

```text
applications/packages/{package_id}/.execution.lock
```

Example:

```json
{
  "lock_type": "execution",
  "package_id": "",
  "workflow_id": "",
  "queue_id": "",
  "acquired_at": "",
  "last_heartbeat": "",
  "owner_process": null
}
```

---

# Stale Lock Recovery

A lock may be stale when:

* Owning process no longer exists.
* Workflow state is terminal.
* Heartbeat is older than configured threshold.
* Browser session no longer exists.
* System restarted.

Recovery process:

1. Inspect workflow state.
2. Confirm no final submission is in progress.
3. Preserve stale lock metadata.
4. Mark workflow Recovering.
5. Remove or replace stale lock.
6. Rerun readiness.
7. Resume only from a safe checkpoint.

---

# Browser Resource Manager

## Responsibility

Allocate browser profiles, browser instances, contexts, and pages.

---

# Default Browser Concurrency

The MVP should execute one application at a time per persistent browser profile.

```text
Maximum concurrent application sessions per profile: 1
```

This avoids:

* Cookie conflicts.
* Session overwrites.
* ATS-account confusion.
* Duplicate submissions.
* Browser-profile corruption.
* Competing popup and tab handling.

---

# Multiple Profiles

Future versions may execute concurrently when each workflow has:

* A separate browser profile.
* Separate authentication state.
* Separate package lock.
* Separate browser context.
* Separate queue partition.

Concurrency should remain disabled by default.

---

# Browser Session Reuse

A browser session may remain open across sequential applications when:

* The same profile is used.
* The browser remains healthy.
* No package-specific session isolation is required.
* The prior application reached a safe terminal state.
* No unexpected popup or dialog remains.
* Cookies and storage should be preserved.

---

# Browser Session Reset

Reset the browser session when:

* Browser crashes.
* Profile becomes corrupted.
* Session state is inconsistent.
* Wrong ATS account is active.
* Security-sensitive workflow requires isolation.
* User requests a clean session.
* Adapter requires a new context.
* Repeated navigation failures occur.

---

# Browser Resource State

```json
{
  "profile_id": "default",
  "browser_status": "running",
  "active_package_id": "",
  "active_workflow_id": "",
  "active_pages": 1,
  "authenticated_domains": [],
  "started_at": "",
  "health_status": "healthy"
}
```

---

# ATS Adapter Routing

The orchestrator should route each application to the correct ATS adapter.

Selection process:

```text
Application URL
        |
        v
Domain Detection
        |
        v
Page Signature Detection
        |
        v
Dedicated Adapter Lookup
        |
        +--> Dedicated Adapter
        |
        +--> Generic Adapter
        |
        +--> Manual Completion
```

---

# Adapter Selection Result

```json
{
  "adapter_id": "greenhouse",
  "adapter_version": "1.0",
  "selection_method": "domain_match",
  "confidence": 100,
  "generic_fallback_allowed": true
}
```

---

# Adapter Revalidation

After navigation, verify that the page still matches the selected adapter.

If a company redirects from its career page to an ATS:

* Detect the new domain.
* Re-evaluate adapter selection.
* Preserve package identity.
* Confirm the redirect belongs to the intended job.

---

# Adapter Degradation

If a dedicated adapter fails because the ATS changed:

1. Capture diagnostics.
2. Reinspect the page.
3. Attempt generic adapter when permitted.
4. Mark dedicated adapter degraded.
5. Continue only when controls can be handled safely.
6. Offer manual completion when generic fallback fails.

---

# Runtime Answer Coordinator

## Responsibility

Resolve unexpected questions found during execution.

---

# Runtime Answer Workflow

```text
Unexpected Field
      |
      v
Question Extraction
      |
      v
Canonical Classification
      |
      v
Exact Answer Lookup
      |
      v
Reusable Answer Lookup
      |
      v
Deterministic Calculation
      |
      v
Claude Resolution When Required
      |
      v
Validation
      |
      v
Browser-Ready Answer
```

---

# Runtime Resolution Rules

* Prefer local exact answers.
* Do not regenerate already approved answers unnecessarily.
* Use only relevant candidate context.
* Preserve question and help text.
* Extract all available options.
* Detect negation and compound questions.
* Validate source and confidence.
* Store runtime answer in the Application Package.
* Trigger review when required by policy.

---

# Runtime Answer Result

```json
{
  "question_id": "runtime_question_004",
  "status": "resolved",
  "canonical_family": "legal.non_compete",
  "answer_type": "controlled_choice",
  "selected_option": "No",
  "source": "candidate.json:legal.non_compete",
  "confidence": 100,
  "requires_review": false
}
```

---

# Runtime Missing Information

When a required answer cannot be resolved:

* Pause the package.
* Persist browser and workflow state.
* Create a user-action request.
* Keep the browser available when practical.
* Allow queue skip-ahead if configured.
* Resume after user response.
* Rerun affected validation.

---

# User Intervention Manager

## Responsibility

Coordinate pauses requiring user participation.

---

# User Intervention Categories

```text
login_required
mfa_required
captcha_required
missing_answer
ambiguous_question
legal_question
sensitive_field
manual_review
unknown_submission
browser_interaction_required
```

---

# User Intervention Request

```json
{
  "request_id": "intervention_001",
  "package_id": "",
  "workflow_id": "",
  "category": "captcha_required",
  "message": "Complete the verification in the open browser window.",
  "required_action": "complete_captcha",
  "resume_stage": "page_inspection",
  "created_at": "",
  "status": "pending"
}
```

---

# Intervention Statuses

```text
pending
presented
completed
cancelled
expired
failed
```

---

# Pause Behavior

When pausing:

1. Stop new browser actions.
2. Save current page URL.
3. Save page signature.
4. Save completed field state.
5. Capture screenshot when appropriate.
6. Persist workflow stage.
7. Release only resources that are safe to release.
8. Mark queue item Waiting for User or Waiting for Review.

---

# Queue Skip-Ahead

The queue may continue to another package while one item waits for user action when:

* `skip_ahead_on_user_action` is enabled.
* The waiting package is at a safe checkpoint.
* The browser session can be safely repurposed or a separate session is available.
* The waiting page can be restored later.
* No submission action is pending.
* No profile-specific flow would be invalidated.

For the MVP, conservative behavior is preferred:

```text
Pause the current browser queue unless the waiting workflow can be safely restored.
```

---

# Resume After User Intervention

After user action:

1. Verify the blocking condition is resolved.
2. Reinspect the current page.
3. Compare current page with saved page signature.
4. Reconcile any changes.
5. Rerun relevant readiness checks.
6. Continue from the next safe stage.

---

# Page Execution Loop

Recommended page loop:

```text
Inspect Current Page
        |
        v
Identify Page Type
        |
        v
Extract Form
        |
        v
Resolve Answers
        |
        v
Build Interaction Plan
        |
        v
Execute Fields
        |
        v
Verify Fields
        |
        v
Validate Page
        |
        +--> Correct Errors
        |
        v
Save Checkpoint
        |
        v
Click Next
        |
        v
Verify Progression
        |
        v
Repeat
```

---

# Page Loop Termination Conditions

Stop the loop when:

* Review page reached.
* Submission page reached.
* Confirmation page reached.
* Application already submitted.
* Application closed.
* User intervention required.
* Non-recoverable error occurs.
* User cancels.
* Maximum page limit is exceeded.
* Repeated page cycle is detected.

---

# Page Cycle Detection

The orchestrator should detect loops.

Possible signals:

* Same URL repeated.
* Same page signature repeated.
* Same validation errors repeated.
* Step indicator does not advance.
* Next button returns to the same form.
* Repeated login redirect.

After bounded attempts:

* Stop.
* Capture diagnostics.
* Mark User Action Required or Failed.
* Do not loop indefinitely.

---

# Maximum Page Count

Use a configurable safety limit.

Example:

```json
{
  "maximum_application_pages": 30
}
```

Exceeding the limit should trigger review rather than automatic continuation.

---

# Page Progression Verification

After clicking Next:

* Confirm URL change, page-signature change, or step-indicator change.
* Detect validation errors.
* Detect conditional modal.
* Detect new tab.
* Detect login redirect.
* Detect application closure.
* Persist new page state.

---

# Form Execution Coordination

The orchestrator sends a structured page plan to the Browser Automation Engine.

Example:

```json
{
  "package_id": "",
  "page_id": "personal_information",
  "page_number": 1,
  "steps": [],
  "validation_policy": "strict",
  "maximum_action_retries": 3
}
```

The browser engine returns structured action results.

The orchestrator does not inspect low-level locator details unless reporting diagnostics.

---

# Form Execution Result

```json
{
  "status": "success",
  "page_id": "personal_information",
  "completed_steps": 12,
  "failed_steps": 0,
  "warnings": [],
  "requires_reinspection": false
}
```

---

# Conditional Field Coordination

After actions likely to reveal conditional fields:

* Ask the browser to reinspect.
* Compare the new form model with the prior form model.
* Resolve newly visible fields.
* Extend the page execution plan.
* Do not click Next until all required conditional fields pass validation.

---

# File Upload Coordination

Before upload:

* Confirm package active document.
* Verify file hash.
* Verify upload authorization.
* Confirm expected document type.
* Confirm browser field identity.

After upload:

* Verify filename or upload token.
* Save upload result.
* Detect ATS resume parsing.
* Reinspect parsed fields.
* Correct parsing errors.
* Record the exact file used.

---

# Review Coordination

The orchestrator should run Application Review at configured stages.

---

# Preparation Review

Run before queue admission when enabled.

---

# Pre-Submission Review

Run after browser form completion and before final submission.

This review is mandatory for automated submission.

---

# Review Coordinator Interface

```text
ReviewCoordinator

    run_preparation_review(package_id)
    run_pre_submission_review(package_id, form_snapshot)
    apply_safe_corrections(package_id, findings)
    request_manual_review(package_id)
    validate_approval(package_id)
```

---

# Review Outcome Handling

## Approved

Continue to Submission Readiness.

## Approved with Warnings

Continue when policy permits.

## Changes Required

Apply safe corrections and rerun review.

## User Input Required

Pause and create intervention request.

## Manual Review Required

Pause and present review interface.

## Blocked

End automated execution for the package.

---

# Automatic Correction Loop

```text
Review Findings
      |
      v
Identify Safe Corrections
      |
      v
Apply Corrections
      |
      v
Verify Browser Values
      |
      v
Rerun Review
```

Maximum correction rounds should be bounded.

Recommended default:

```text
3 rounds
```

---

# Manual Review Workflow

When review mode is enabled:

1. Save final form snapshot.
2. Capture review-page screenshot.
3. Show active resume and cover letter.
4. Show final answers.
5. Show warnings and corrections.
6. Pause submission.
7. Receive approval or edits.
8. Apply user changes.
9. Rerun validation and review.
10. Continue to submission only with valid approval.

---

# Approval Binding

Approval must reference:

* Package ID.
* Job identity.
* Resume version.
* Cover-letter version.
* Answer-set version.
* Browser form snapshot hash.
* Approval time.

Any material change invalidates approval.

---

# Submission Coordinator

## Responsibility

Coordinate final submission as an irreversible workflow stage.

---

# Submission Preconditions

Before submission:

* Application Review approved.
* Submission Readiness passed.
* Duplicate check passed again.
* Correct job page confirmed.
* Submit control identified.
* Package and submission locks acquired.
* Browser form snapshot stored.
* Active document versions recorded.
* No unresolved user action exists.
* No prior Submission Unknown state exists.

---

# Submission Plan

```json
{
  "package_id": "",
  "job_id": "",
  "submit_control_label": "Submit Application",
  "expected_confirmation_signals": [
    "Application submitted",
    "confirmation_number",
    "submitted_dashboard_status"
  ],
  "submission_timeout_seconds": 60,
  "retry_policy": "no_automatic_reclick"
}
```

---

# Irreversible Action Rule

The final Submit click must never be repeated automatically merely because:

* The page is slow.
* The button remains visible temporarily.
* Navigation does not occur immediately.
* A network timeout happens.
* The browser loses connection.

After the click, the workflow enters a submission-verification state.

---

# Submission State Sequence

```text
Ready for Submission
        |
        v
Submission Lock Acquired
        |
        v
Submit Click Initiated
        |
        v
Awaiting Submission Result
        |
        +--> Submitted
        +--> Failed Before Submission
        +--> Submission Unknown
```

---

# Submission Attempt Record

```json
{
  "attempt_id": "submission_attempt_001",
  "package_id": "",
  "initiated_at": "",
  "submit_control": "",
  "page_url_before": "",
  "screenshot_before": "",
  "click_result": "performed",
  "verification_status": "pending"
}
```

---

# Submission Verification

Use strong evidence such as:

* Explicit confirmation message.
* Confirmation number.
* Confirmation page.
* ATS dashboard status.
* Application ID.
* Verified success response associated with submission.
* Confirmation email in a future authorized integration.

Weak signals alone are insufficient.

---

# Submission Verification Result

```json
{
  "status": "submitted",
  "confirmation_number": "",
  "confirmation_message": "",
  "confirmation_url": "",
  "ats_application_id": "",
  "submitted_at": "",
  "confidence": 100,
  "evidence": []
}
```

---

# Submission Failure Before Irreversible Action

If submission did not occur because:

* Submit button could not be located.
* Validation blocked the click.
* Browser crashed before clicking.
* Session expired before clicking.

The workflow may recover and retry after readiness revalidation.

---

# Submission Unknown

If the Submit action occurred but success cannot be determined:

* Set package status Submission Unknown.
* Preserve all evidence.
* Keep submission attempt record.
* Do not click Submit again.
* Do not mark Failed.
* Do not mark Submitted.
* Require dashboard, email, or user verification.

---

# Tracker Synchronization

After verified submission, update the local Application Tracker.

Initial MVP formats:

* CSV.
* XLSX.

A database is not required initially.

---

# Tracker Record

Recommended fields:

```text
application_id
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
confirmation_url
automation_mode
notes
```

---

# CSV Example

```csv
application_id,package_id,company,job_title,job_id,date_applied,application_status,resume_filename
app_001,google_123456_20260712T080000,Google,Senior Software Engineer,123456,2026-07-12,Submitted,Suhas_Arudi_Google_Resume.pdf
```

---

# Tracker Synchronization Sequence

```text
Verified Submission
        |
        v
Persist Package Submission Result
        |
        v
Write Tracker Record
        |
        v
Verify Tracker Write
        |
        v
Mark Synchronization Complete
```

The package should be marked Submitted before tracker synchronization.

A tracker failure must not cause resubmission.

---

# Tracker Sync Failure

When tracker synchronization fails:

* Preserve Submitted package status.
* Store tracker-sync error.
* Retry the tracker write when safe.
* Avoid duplicate tracker rows.
* Report the incomplete synchronization.
* Continue queue execution when policy permits.

---

# Tracker Idempotency

Tracker synchronization should be idempotent.

Use a stable unique key such as:

```text
package_id
```

or:

```text
company + job_id + submitted_at
```

A retry should update or confirm the existing row rather than append duplicates.

---

# Execution Error Categories

Recommended categories:

```text
preparation_error
readiness_error
package_lock_error
browser_startup_error
navigation_error
authentication_error
captcha_required
page_inspection_error
answer_resolution_error
interaction_error
validation_error
upload_error
page_progression_error
review_error
approval_error
submission_error
submission_unknown
tracker_sync_error
cancellation
```

---

# Retry Classification

Errors should be explicitly classified as:

```text
retryable
retryable_after_user_action
non_retryable
submission_outcome_unknown
```

---

# Retryable Errors

Examples:

* Temporary network timeout.
* Detached DOM element.
* Temporary page load failure.
* ATS server error before submission.
* Browser crash before final submission.
* Provider timeout during narrative generation.
* Temporary upload failure.
* Stale selector.

---

# Retryable After User Action

Examples:

* Login required.
* MFA required.
* CAPTCHA required.
* Missing candidate answer.
* Manual approval required.
* Browser profile locked by another visible session.

---

# Non-Retryable Errors

Examples:

* Job closed.
* Candidate rule violation.
* Duplicate application.
* No truthful answer exists.
* Required unsupported qualification.
* Sensitive field conflicts with policy.
* Application destination is untrusted.
* Required document cannot be provided.
* User cancels.

---

# Submission Outcome Unknown

This category must remain separate from normal retryable errors.

Automatic retry is prohibited.

---

# Retry Policy

Recommended default:

```json
{
  "maximum_stage_attempts": 3,
  "maximum_package_restarts": 2,
  "retry_backoff_seconds": [
    2,
    5,
    10
  ],
  "retry_submission_click": false
}
```

---

# Retry Rules

Before retrying:

1. Confirm the failed action is safe to repeat.
2. Reinspect page state.
3. Confirm application identity.
4. Check whether the action may already have succeeded.
5. Restore from the latest checkpoint.
6. Increment attempt count.
7. Record retry reason.

---

# Package Restart

A package restart may relaunch the browser and resume from a saved checkpoint.

Allowed when:

* Final submission has not been attempted.
* ATS state can be restored.
* Package is not stale.
* Required answers and documents remain valid.
* Restart count remains within limits.

---

# Recovery Coordinator

## Responsibility

Recover workflows after interruptions, browser crashes, session loss, or application restarts.

---

# Recovery Inputs

* Package state.
* Workflow state.
* Latest checkpoint.
* Lock metadata.
* Browser-profile state.
* Current tracker status.
* Submission attempt records.
* Screenshots and page signatures.

---

# Recovery Decision Tree

```text
Load Workflow
      |
      v
Was Submit Attempted?
      |
      +-- Yes --> Is Submission Verified?
      |             |
      |             +-- Yes --> Finalize Submitted
      |             |
      |             +-- No --> Submission Unknown
      |
      +-- No --> Load Last Checkpoint
                    |
                    v
              Restore Browser
                    |
                    v
              Reconcile Page
                    |
                    v
              Resume Safe Stage
```

---

# Recovery After Browser Crash

1. Record crash.
2. Close invalid resources.
3. Load package and checkpoint.
4. Check whether Submit was attempted.
5. Relaunch browser with the same profile.
6. Navigate to saved application URL or ATS dashboard.
7. Reconcile current ATS state.
8. Rerun readiness.
9. Resume from the last safe stage.

---

# Recovery After Application Restart

On application startup:

* Search for non-terminal workflows.
* Inspect locks.
* Identify packages in Executing, Submitting, or Waiting states.
* Reconcile workflow state.
* Do not automatically resubmit.
* Present recoverable workflows to the user or resume according to policy.

---

# Recovery State Reconciliation

Possible outcomes:

```text
resume_execution
waiting_for_user
submitted
submission_unknown
blocked
failed
```

---

# Session Expiration Recovery

When redirected to login:

* Pause workflow.
* Preserve checkpoint.
* Mark Waiting for User.
* Complete authentication.
* Return to application dashboard or saved URL.
* Verify package identity.
* Reconcile completed pages.
* Resume.

---

# Recovery After Page Data Loss

If unsaved form data is lost:

* Reload intended values from the package.
* Reinspect fields.
* Refill only missing values.
* Reupload documents when required.
* Rerun page validation.
* Avoid duplicating repeated sections.

---

# Cancellation

The user should be able to cancel:

* Current action.
* Current package.
* Remaining queue.
* Entire queue.

---

# Package Cancellation

Before final submission:

* Stop new browser actions.
* Save current state.
* Release package and browser resources.
* Mark package Cancelled.
* Preserve generated materials.
* Remove item from active execution.

---

# Cancellation During Submission

If the Submit action has already occurred:

* Do not assume cancellation prevented submission.
* Continue submission verification.
* Mark Submitted or Submission Unknown.
* Do not label Cancelled until the outcome is reconciled.

---

# Queue Cancellation

When cancelling the queue:

* Stop after the current safe boundary.
* Cancel pending items.
* Preserve completed results.
* Preserve waiting-for-user items.
* Release locks.
* Do not undo submitted applications.

---

# Skip Application

The user or system may skip a package.

Possible reasons:

```text
user_not_interested
job_closed
duplicate
salary_mismatch
unsupported_ats
too_many_unresolved_questions
manual_completion_preferred
application_too_long
```

Store the reason locally.

---

# Continue-After-Failure Policy

Recommended default:

```json
{
  "continue_after_package_failure": true,
  "continue_after_blocked_package": true,
  "continue_after_user_action_required": false,
  "continue_after_submission_unknown": false
}
```

For the MVP, Submission Unknown should pause the queue unless the user explicitly chooses to continue.

---

# Batch Execution Behavior

Each package should execute independently.

Example result:

```text
Selected: 10
Submitted: 6
Waiting for User: 1
Already Applied: 1
Blocked: 1
Failed: 1
```

A failure in one application should not erase or invalidate successful applications.

---

# Queue-Level Failure Conditions

The entire queue may fail when:

* Queue file is corrupt.
* Browser profile is unusable and no alternative exists.
* Package storage is unavailable.
* System-wide provider failure prevents required runtime resolution.
* Execution configuration is invalid.
* Security policy prevents all navigation.
* User cancels the queue.

---

# Progress Reporting

The orchestrator should emit user-visible progress events.

Examples:

```text
Preparing application 2 of 8.
Opening the Microsoft application.
Uploading the approved resume.
Completing work-authorization questions.
Application review passed.
Submitting application.
Submission verified.
```

Progress messages should not expose sensitive answer values.

---

# Progress Event Model

```json
{
  "event_id": "",
  "event_type": "page_completed",
  "queue_id": "",
  "package_id": "",
  "workflow_id": "",
  "stage": "page_progression",
  "message": "Completed page 2 of the application.",
  "progress": {
    "queue_position": 2,
    "queue_total": 8,
    "page_number": 2
  },
  "created_at": ""
}
```

---

# Execution Event Types

Recommended events:

```text
queue_created
queue_validated
queue_started
queue_paused
queue_resumed
queue_completed

package_admitted
package_started
package_paused
package_resumed
package_completed
package_failed
package_blocked

browser_started
navigation_completed
page_inspected
page_completed
answer_resolved
document_uploaded
review_started
review_completed
user_action_required
submission_started
submission_verified
submission_unknown
tracker_synced
```

---

# Event Persistence

Important events should be stored in:

```text
applications/packages/{package_id}/execution/events.jsonl
```

JSON Lines is suitable for append-only execution events.

---

# Event Ordering

Events should include:

* Timestamp.
* Sequence number.
* Workflow ID.
* Package ID.
* Stage.
* Event type.

Sequence numbers help reconstruct execution after clock inconsistencies.

---

# Idempotent Orchestration

Workflow operations should be safe to repeat when possible.

Examples:

* Queue admission should not create duplicate items.
* Package locking should detect existing ownership.
* Tracker synchronization should not append duplicate rows.
* Page completion should not duplicate records.
* Resume upload should verify before replacing.
* Submission verification should not click Submit.

---

# Idempotency Keys

Use stable keys such as:

```text
queue_id + package_id
workflow_id + stage + attempt
package_id + tracker_sync
package_id + submission_attempt_id
```

---

# Orchestration Configuration

Example:

```json
{
  "execution": {
    "browser_profile": "default",
    "browser_visible": true,
    "maximum_concurrent_profiles": 1,
    "continue_after_package_failure": true,
    "skip_ahead_on_user_action": false,
    "maximum_stage_attempts": 3,
    "maximum_package_restarts": 2,
    "maximum_application_pages": 30,
    "checkpoint_after_every_page": true,
    "require_pre_submission_review": true,
    "pause_on_submission_unknown": true
  }
}
```

---

# Automation Modes

Each queue item may operate in one of three modes.

```text
automatic
review
manual
```

---

## Automatic Mode

The orchestrator may:

* Open the application.
* Resolve questions.
* Fill fields.
* Upload files.
* Review the application.
* Submit when review and readiness pass.

It must still pause for:

* CAPTCHA.
* MFA.
* Missing required information.
* Ambiguous legal questions.
* Sensitive-field policy conflicts.
* Unknown submission state.

---

## Review Mode

The orchestrator:

* Completes the form.
* Runs automated review.
* Pauses before final submission.
* Applies user edits.
* Revalidates.
* Submits after approval.

---

## Manual Mode

The orchestrator may:

* Prepare documents and answers.
* Open the application.
* Present a checklist.
* Allow the user to complete or submit manually.

It should not mark the application Submitted without user confirmation or reliable evidence.

---

# Package-Specific Overrides

A package may override queue defaults.

Examples:

```json
{
  "automation_mode": "review",
  "browser_profile": "company_accounts",
  "continue_after_failure": false,
  "allow_account_creation": false,
  "generic_adapter_fallback": true,
  "require_visible_browser": true
}
```

Package overrides should be resolved before queue admission.

---

# Concurrency

## Preparation Concurrency

Application preparation may run in parallel.

## Browser Execution Concurrency

Sequential by default.

## Multiple Profile Concurrency

Optional future capability.

Every concurrent workflow must have:

* Separate browser profile.
* Separate package.
* Separate workflow ID.
* Separate locks.
* Independent event stream.
* Independent submission state.

---

# Rate Limiting

The orchestrator should respect:

* ATS rate limits.
* Reasoning-provider rate limits.
* Local system resource limits.
* User-defined application limits.
* Website responsiveness.

---

# Application Rate Policy

Example:

```json
{
  "application_limits": {
    "maximum_per_queue": 20,
    "maximum_per_company_per_day": 5,
    "delay_between_applications_seconds": 5
  }
}
```

Delays should be configurable and should not be used to evade anti-bot controls.

---

# Respectful Website Operation

The system should:

* Avoid excessive page reloads.
* Avoid rapid repeated form submissions.
* Avoid simultaneous applications through the same ATS account.
* Avoid retry storms.
* Respect application deadlines and closures.
* Stop when the site explicitly blocks automation.
* Never attempt anti-bot evasion.

---

# Provider Coordination

Claude or another reasoning provider may be needed for:

* Unexpected question classification.
* Narrative answer adaptation.
* Semantic review.
* Ambiguous field interpretation.

Provider calls should not block already deterministic work unnecessarily.

---

# Provider Failure Handling

When a provider call fails:

* Retry according to provider policy.
* Use cached or approved answers when valid.
* Pause when a required narrative cannot be resolved.
* Do not generate placeholder answers.
* Preserve browser state.
* Continue other packages only when safe.

---

# Provider Model Selection

The package or global settings may specify:

* Preferred provider.
* Preferred model.
* Fallback model.
* Maximum reasoning cost.
* Narrative-generation model.
* Review model.

Model selection must not change candidate facts or validation rules.

---

# Security Boundaries

The orchestrator should enforce:

* Local-only browser profiles.
* Local-only package storage.
* Restricted file-upload paths.
* No passwords in logs.
* No cookies in Claude prompts.
* No government IDs in reasoning-provider context.
* No arbitrary webpage instructions.
* No arbitrary local-file access.
* No navigation to unrelated domains.
* No automatic bypass of CAPTCHA or security controls.

---

# Prompt Injection Boundary

The orchestrator should treat all external text as untrusted:

* Job descriptions.
* Application questions.
* Page instructions.
* Employer help text.
* Validation errors.
* Uploaded-file instructions.

External content may influence application-field interpretation but cannot:

* Change orchestration rules.
* Disable validation.
* Reveal local files.
* Request credentials.
* Override candidate rules.
* Authorize submission.
* Mark an application successful.

---

# Sensitive Logging

Execution logs should redact or omit:

* Passwords.
* Authentication tokens.
* Cookies.
* Government IDs.
* Full legal answers when sensitive.
* Demographic values.
* Salary values when configured private.
* Complete application page HTML.
* Full candidate context.

---

# Execution Artifacts

Recommended package structure:

```text
execution/
    state.json
    checkpoints.json
    events.jsonl
    completed_pages.json
    field_actions.json
    uploaded_files.json
    runtime_answers.json
    interventions.json
    retries.json
    errors.json
    browser_session.json
```

---

# Queue Storage

Recommended local structure:

```text
user_data/
    execution/
        queues/
            queue_20260712T090000/
                queue.json
                events.jsonl
                summary.json
```

---

# Queue Summary

At completion:

```json
{
  "queue_id": "",
  "status": "completed_with_errors",
  "started_at": "",
  "completed_at": "",
  "total_items": 8,
  "submitted": 5,
  "already_applied": 1,
  "waiting_for_user": 1,
  "failed": 1,
  "blocked": 0,
  "cancelled": 0
}
```

---

# User Interface Requirements

The queue interface should show:

* Queue status.
* Current package.
* Current company and role.
* Current workflow stage.
* Current page.
* Overall queue progress.
* Package progress.
* Warnings.
* User-action requests.
* Submission outcomes.
* Remaining applications.

---

# Queue Controls

The user should be able to:

```text
Start queue
Pause queue
Resume queue
Cancel queue
Cancel current package
Skip current package
Reorder pending items
Retry failed package
Open package details
Complete user action
Approve application
Switch package to Manual mode
Continue after submission unknown
```

Continuing after Submission Unknown should require explicit acknowledgment.

---

# Package Detail View During Execution

Display:

* Company.
* Job title.
* Application URL.
* Package status.
* Execution stage.
* Browser status.
* Completed pages.
* Current page.
* Active resume.
* Cover letter status.
* Runtime questions.
* Review status.
* Errors.
* Screenshots.
* Submission status.

---

# Startup Recovery Interface

On application restart, show incomplete workflows.

Example:

```text
Google — Senior Software Engineer
Status: Waiting for CAPTCHA
Last checkpoint: Application page 3

Microsoft — Backend Engineer
Status: Submission Unknown
Action required: Verify ATS dashboard before retrying
```

---

# Notifications

The system may notify the user when:

* Login is required.
* CAPTCHA is required.
* MFA is required.
* A required answer is missing.
* Manual review is ready.
* Submission succeeds.
* Submission is unknown.
* Queue completes.
* Browser session crashes.

Notifications should not contain sensitive answer values.

---

# Testing Strategy

Testing should use controlled local applications before live ATS testing.

---

# Unit Tests

Unit-test:

* Queue ordering.
* Queue admission.
* State transitions.
* Lock acquisition.
* Lock recovery.
* Retry classification.
* Retry counters.
* Idempotency keys.
* Next-stage selection.
* Cancellation.
* Duplicate prevention.
* Approval invalidation.
* Event ordering.
* Queue summary generation.

---

# Integration Tests

Integration-test:

* Ready package to queue admission.
* Sequential execution of multiple packages.
* Browser-session reuse.
* Runtime question resolution.
* File upload.
* Page checkpointing.
* CAPTCHA pause and resume.
* Manual review pause and approval.
* Submission verification.
* Tracker synchronization.
* Package failure isolation.
* Queue continuation.
* Browser crash recovery.
* Application restart recovery.
* Submission Unknown handling.

---

# Controlled Local Test Workflows

The local test application should support:

* One-page application.
* Multi-page application.
* Required resume upload.
* Optional cover letter.
* Conditional sponsorship question.
* Runtime unexpected question.
* Validation error.
* Login simulation.
* CAPTCHA simulation.
* Review page.
* Successful submission page.
* Failed submission.
* Unknown submission outcome.
* Session expiration.
* Browser crash simulation.

---

# Required Test Scenarios

## Two Ready Packages

Both packages pass readiness.

Expected:

1. Package 1 executes.
2. Submission is verified.
3. Tracker updates.
4. Locks release.
5. Package 2 executes.
6. Queue completes.

---

## First Package Fails Before Submission

Package 1 fails because a required field cannot be located.

Expected:

* Package 1 marked Failed or User Action Required.
* Diagnostics saved.
* No submission recorded.
* Package 2 proceeds when queue policy permits.

---

## Runtime Question Resolved Locally

Unexpected sponsorship question appears.

Expected:

* Canonical mapping succeeds.
* Exact local answer used.
* No Claude call.
* Answer saved to runtime answers.
* Execution continues.

---

## Runtime Narrative Question

Unexpected “Why are you interested in this role?” field appears.

Expected:

* Relevant candidate and job context sent to the reasoning provider.
* Answer generated and validated.
* Character limit enforced.
* Answer saved.
* Browser fills and verifies the field.

---

## CAPTCHA

CAPTCHA appears during application.

Expected:

* Browser actions stop.
* Checkpoint saved.
* User notified.
* Package enters Waiting for User.
* Automation resumes after CAPTCHA completion.

---

## Manual Review Mode

Application form is complete.

Expected:

* Automated review runs.
* Package enters Waiting for Review.
* Submit button is not clicked.
* User approves.
* Readiness reruns.
* Submission proceeds.

---

## Browser Crash Before Submission

Browser crashes on page 3.

Expected:

* Crash recorded.
* Package state preserved.
* Browser restarted.
* Application restored.
* Completed fields reconciled.
* Execution resumes.

---

## Browser Crash After Submit Click

Browser crashes after Submit was clicked but before confirmation.

Expected:

* Package marked Submission Unknown.
* No automatic retry.
* User or ATS-dashboard verification required.

---

## Duplicate Package in Two Queues

The same package is added to two active queues.

Expected:

* Second queue admission rejected.
* Existing queue ownership reported.
* No parallel execution.

---

## Profile Conflict

Two workflows attempt to use the same persistent profile.

Expected:

* One workflow owns the profile.
* Other workflow waits or fails admission.
* No simultaneous profile access.

---

## Wrong ATS Redirect

Application redirects to an unrelated domain.

Expected:

* Navigation blocked.
* Evidence captured.
* Package marked User Action Required or Blocked.
* No candidate files uploaded.

---

## Wrong Job Redirect

Application package is for one job, but browser opens another requisition.

Expected:

* Identity check fails.
* No form completion or submission.
* Recovery or user action required.

---

## Review Correction

Browser contains the wrong sponsorship answer.

Expected:

* Review detects mismatch.
* Browser value corrected.
* Review reruns.
* Submission proceeds only after approval.

---

## Required User Answer

A required legal question has no stored answer.

Expected:

* Package pauses.
* User receives precise question.
* User response is stored in the package.
* Optional reusable storage requires approval.
* Review reruns.

---

## User Cancels Current Package

Expected:

* Browser actions stop at a safe boundary.
* State saved.
* Package marked Cancelled.
* Locks released.
* Queue continues according to policy.

---

## Queue Cancellation

Expected:

* Pending items marked Cancelled.
* Current item stops safely.
* Submitted items remain Submitted.
* Locks release.
* Queue summary persists.

---

## Tracker Write Failure

Submission succeeds, but XLSX or CSV write fails.

Expected:

* Package remains Submitted.
* Tracker-sync error saved.
* No resubmission.
* Synchronization may be retried safely.

---

## Job Closes While Waiting

A queued job is closed before execution.

Expected:

* Pre-execution readiness detects closure.
* Package removed from executable queue.
* Status updated.
* Other items continue.

---

## Stale Package

Candidate resume changes after queue admission.

Expected:

* Pre-execution fingerprint check fails.
* Package marked Refresh Required.
* Execution does not start.
* Other ready packages may continue.

---

## Submission Unknown Queue Policy

One item reaches Submission Unknown.

Expected default:

* Current package stops.
* Queue pauses.
* User is notified.
* No automatic resubmission or continuation without policy approval.

---

# Orchestration Error Types

Recommended internal errors:

```text
QueueCreationError
QueueValidationError
QueueAdmissionError
QueueStateError
QueueItemStateError
PackageLockError
BrowserResourceError
WorkflowStateError
WorkflowStageError
RuntimeAnswerResolutionError
UserInterventionError
ReviewCoordinationError
SubmissionCoordinationError
SubmissionUnknownError
TrackerSynchronizationError
RecoveryError
CancellationError
```

---

# State Transition Validation

All transitions should be explicit.

Examples:

```text
Pending -> Validating
Validating -> Admitted
Admitted -> Waiting
Waiting -> Executing
Executing -> Waiting for User
Executing -> Waiting for Review
Executing -> Submitted
Executing -> Failed
Submitting -> Submitted
Submitting -> Submission Unknown
```

Invalid:

```text
Pending -> Submitted
Failed -> Submitted
Submission Unknown -> Executing
Cancelled -> Submitting
```

Invalid transitions should raise a state error and preserve the previous state.

---

# Terminal Queue Item States

Terminal states:

```text
submitted
completed_manual
already_applied
skipped
cancelled
blocked
failed
submission_unknown
```

Submission Unknown is terminal for automatic execution but may later be resolved to Submitted or Failed through explicit verification.

---

# Definition of Queue and Orchestration Completion

The Application Queue and Execution Orchestration system is complete when:

* Ready packages can be admitted to a queue.
* Queue ordering is deterministic.
* Duplicate package entries are prevented.
* Package locks prevent concurrent execution.
* One persistent browser profile executes applications sequentially.
* Workflow stages are explicit.
* State persists after every meaningful step.
* Application pages execute sequentially.
* Runtime unexpected questions can be resolved.
* Missing information pauses safely.
* CAPTCHA, login, and MFA pauses work.
* Manual review mode works.
* Automatic review mode works.
* Application corrections can be applied and revalidated.
* Final submission requires submission readiness.
* Submit is never automatically clicked twice.
* Submission success requires strong evidence.
* Submission Unknown blocks automatic resubmission.
* Browser crashes can recover before submission.
* Application restarts can recover incomplete workflows.
* Individual package failures do not erase successful results.
* Queue cancellation and package cancellation work.
* Tracker synchronization is idempotent.
* Tracker failure does not trigger resubmission.
* Execution events and progress are persisted.
* Sensitive information is excluded from logs.
* Prompt-injection protections remain enforced.
* Controlled local integration tests pass.
* At least one supported ATS can complete an end-to-end queue workflow.

---

# Summary

The Application Queue and Execution Orchestration system is the control layer that turns prepared Application Packages into completed application workflows.

It is responsible for:

* Queue admission.
* Queue ordering.
* Workflow-state management.
* Package locking.
* Browser-resource allocation.
* ATS-adapter routing.
* Page-by-page execution.
* Runtime answer resolution.
* User intervention.
* Application review.
* Submission coordination.
* Submission verification.
* Recovery.
* Tracker synchronization.

The orchestrator should favor:

* Explicit states.
* Durable checkpoints.
* Sequential browser execution.
* Deterministic transitions.
* Bounded retries.
* Safe pauses.
* Idempotent operations.
* Strong submission evidence.
* Isolation of package failures.

The system must never prioritize queue throughput over factual accuracy, privacy, application integrity, or duplicate-submission prevention.
