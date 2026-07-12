# 07D-2 - Application Readiness

## LLM-Powered Autonomous Job Search & Application Platform

Version: 1.0

---

# Purpose

This document defines the Application Readiness system responsible for determining whether an Application Package is sufficiently complete, valid, current, and safe to enter browser execution or final submission.

Application Readiness is distinct from Application Review.

Application Review evaluates the quality, consistency, correctness, and risk of application artifacts.

Application Readiness evaluates whether all mandatory conditions for the next workflow stage have been satisfied.

A package may contain high-quality materials but still be unready because:

* A required file is missing.
* A required answer is unresolved.
* The package is stale.
* The application URL is invalid.
* The job has already been applied to.
* The browser profile is unavailable.
* Manual approval is required.
* The package is locked by another process.
* A previous submission has an unknown outcome.

The readiness system should prevent incomplete or unsafe packages from entering the application queue or proceeding to final submission.

---

# Core Principle

Only validated and current Application Packages may advance.

```text
Application Package
        |
        v
Readiness Evaluation
        |
        +------> Blocking Conditions
        |
        +------> User Action Required
        |
        +------> Refresh Required
        |
        v
Ready for Next Stage
```

Readiness is stage-specific.

A package may be:

* Ready for preparation.
* Ready for browser execution.
* Ready for review.
* Ready for submission.
* Ready for history synchronization.

These are separate states with separate requirements.

---

# Application Readiness Objectives

The readiness system should ensure that:

* Required package artifacts exist.
* Package files are valid and readable.
* The selected job is still valid.
* The package has not already been submitted.
* Candidate facts required for the application are available.
* The approved resume exists.
* Required cover letters and supporting files exist.
* Required answers are resolved.
* Candidate rules are satisfied.
* The package is not stale.
* The package is not being modified elsewhere.
* Browser prerequisites are available.
* Review and approval requirements are satisfied.
* Submission risk checks have passed.
* The workflow can advance without relying on assumptions.

---

# Readiness System Components

```text
Application Readiness System
    |
    +-- Stage Readiness Evaluator
    +-- Artifact Requirement Resolver
    +-- Package Integrity Validator
    +-- Package Staleness Detector
    +-- Candidate Data Readiness Validator
    +-- Document Readiness Validator
    +-- Answer Readiness Validator
    +-- Browser Prerequisite Validator
    +-- Review Approval Validator
    +-- Duplicate Application Validator
    +-- Submission Safety Validator
    +-- Queue Admission Controller
    +-- Readiness Report Generator
```

---

# Readiness Stages

The system should support the following readiness stages.

```text
preparation
browser_execution
manual_review
submission
history_sync
archive
```

Each stage has different requirements.

---

# Preparation Readiness

A selected job is Ready for Preparation when:

* Job identity is available.
* Company name is available.
* Job title is available.
* Application URL or job-detail URL is available.
* Job has not already been submitted.
* Candidate Knowledge Base is accessible.
* At least one valid resume is available.
* Candidate rules allow consideration of the job.
* Package storage is writable.

Preparation readiness does not require a tailored resume or complete answer set.

---

# Browser Execution Readiness

An Application Package is Ready for Browser Execution when:

* Preparation is complete.
* Package integrity checks pass.
* Job snapshot exists.
* Application URL is valid.
* Duplicate application check passes.
* Candidate context snapshot exists.
* Selected active resume exists.
* Resume validation passes.
* Required cover letter exists.
* Required supporting documents exist.
* Prepared answer set exists.
* Required predicted answers are resolved.
* Application Plan exists.
* Automation mode is defined.
* Browser profile is available.
* Package is not stale.
* Package is not locked by another workflow.
* No blocking preparation-review issue remains.

---

# Manual Review Readiness

An application is Ready for Manual Review when:

* Browser form completion is complete.
* Final form values are available.
* Required fields are filled.
* Uploaded files are known.
* Browser validation has passed or known warnings are documented.
* Review-page extraction is available when supported.
* Application Review has completed.
* User-facing artifacts can be displayed.
* No active browser operation is modifying the application.

---

# Submission Readiness

An application is Ready for Submission when:

* Browser execution is complete.
* Pre-submission Application Review has passed.
* Required approval exists.
* No unresolved required field remains.
* No browser validation error remains.
* Correct resume is uploaded.
* Required cover letter is uploaded.
* Required supporting documents are uploaded.
* Candidate-rule compliance passes.
* Privacy checks pass.
* Duplicate application check passes immediately before submission.
* No previous unknown submission state exists.
* Current browser page matches the intended application.
* Final Submit control is present and enabled.
* CAPTCHA and authentication challenges are resolved.
* Package status allows submission.
* Package is not stale.
* Submission lock is acquired.

---

# History Synchronization Readiness

A submitted application is Ready for History Synchronization when:

* Submission success has been verified.
* Submission timestamp is available.
* Job ID or canonical application reference is available.
* Company and title are available.
* Final resume version is known.
* Confirmation evidence is stored.
* Application Tracker is writable.
* No matching tracker row already exists.

---

# Archive Readiness

A package may be archived when:

* It is not currently executing.
* It is not currently submitting.
* Required submission evidence has been persisted.
* Tracker synchronization has completed or an explicit warning exists.
* No active file lock remains.
* The user or retention policy permits archiving.

---

# Readiness Statuses

Supported readiness statuses:

```text
ready
ready_with_warnings
not_ready
user_action_required
refresh_required
blocked
already_applied
submission_unknown
failed
```

---

## Ready

All mandatory stage requirements pass.

The workflow may advance.

---

## Ready with Warnings

All mandatory requirements pass, but non-blocking issues remain.

Examples:

* Optional question is unanswered.
* Sponsorship availability is not stated by the employer.
* Cover letter is optional and omitted.
* Preferred qualification is missing.
* One low-priority screenshot is unavailable.

The workflow may advance when user policy permits.

---

## Not Ready

One or more required items are incomplete but may be resolved automatically.

Examples:

* Resume rendering is still in progress.
* Package validation has not run.
* Prepared answers are incomplete.
* Application Plan is missing.

---

## User Action Required

A person must provide information or complete an action.

Examples:

* Required legal answer missing.
* Login required.
* CAPTCHA present.
* Manual approval required.
* Sensitive identifier is manual-only.
* Ambiguous compound question requires confirmation.

---

## Refresh Required

The package was previously valid but one or more inputs changed.

Examples:

* Candidate profile changed.
* Resume changed.
* Candidate rules changed.
* Job description changed.
* Prompt version changed.
* Active document version changed.

---

## Blocked

The package cannot safely proceed.

Examples:

* Unsupported claim remains.
* Hard candidate rule is violated.
* Job is closed.
* No truthful answer option exists.
* Wrong job is open in the browser.
* Required file is prohibited by privacy policy.
* Application destination is untrusted.

---

## Already Applied

The application tracker or package history confirms that the same job was previously submitted.

The workflow should not continue unless the user explicitly overrides.

---

## Submission Unknown

A prior final submission action occurred without reliable confirmation.

Automatic resubmission is prohibited.

---

## Failed

The readiness evaluation itself failed because of a system error.

---

# Readiness Result Model

Every evaluation should return a structured result.

```json
{
  "readiness_id": "readiness_google_123456_20260711T110000",
  "package_id": "google_123456_20260710T221500",
  "stage": "browser_execution",
  "status": "ready",
  "evaluated_at": "2026-07-11T11:00:00-04:00",
  "blocking_issues": [],
  "warnings": [],
  "required_user_actions": [],
  "refresh_reasons": [],
  "checks": {},
  "next_allowed_action": "queue_application"
}
```

---

# Readiness Check Model

Each check should return a structured record.

```json
{
  "check_id": "resume_active_version",
  "category": "documents",
  "status": "passed",
  "required": true,
  "message": "The approved active resume exists and passed validation.",
  "evidence": [
    "resume/tailored_resume_v2.pdf"
  ],
  "recommended_action": null
}
```

Possible check statuses:

```text
passed
passed_with_warning
failed
not_applicable
pending
user_action_required
stale
```

---

# Readiness Requirement Model

Requirements should be declarative where possible.

Example:

```json
{
  "requirement_id": "required_resume",
  "stage": "browser_execution",
  "artifact_type": "resume",
  "required": true,
  "conditions": [
    "application_plan.resume_required == true"
  ],
  "validator": "resume_readiness_validator"
}
```

This allows stage requirements to evolve without hardcoding all logic inside one large function.

---

# Readiness Policy

The user should be able to configure readiness behavior.

Example:

```json
{
  "readiness": {
    "allow_ready_with_warnings": true,
    "block_stale_packages": true,
    "block_duplicate_applications": true,
    "allow_duplicate_override": true,
    "require_preparation_review": true,
    "require_pre_submission_review": true,
    "require_manual_review": false,
    "maximum_warning_count": null,
    "block_on_high_severity_warning": true,
    "require_browser_health_check": true
  }
}
```

---

# Hard Requirements vs Conditional Requirements

## Hard Requirement

Always required for the stage.

Example:

```text
A valid application URL is required for browser execution.
```

## Conditional Requirement

Required only under specific conditions.

Example:

```text
A cover letter is required only when the portal requires one or a candidate rule requires it.
```

## Optional Requirement

May improve the application but does not block progression.

Example:

```text
An optional company-interest narrative may be omitted.
```

---

# Artifact Requirement Resolution

Before validating artifacts, determine which artifacts are required for the selected job.

Possible artifacts:

* Base resume.
* Tailored resume.
* Cover letter.
* Transcript.
* Portfolio.
* Writing sample.
* Certification.
* Publication list.
* Reference list.
* Prepared answers.
* Application Plan.
* Browser profile.
* Manual approval record.
* Review report.

---

# Artifact Requirement Sources

Requirements may come from:

1. Actual application form.
2. Application instructions.
3. Job description.
4. Candidate rules.
5. Company-specific rules.
6. Job-family rules.
7. Global configuration.
8. User override.

---

# Artifact Requirement Result

```json
{
  "artifacts": [
    {
      "artifact_type": "resume",
      "required": true,
      "source": "application_form",
      "expected_formats": [
        "pdf",
        "docx"
      ]
    },
    {
      "artifact_type": "cover_letter",
      "required": false,
      "source": "application_form"
    }
  ]
}
```

---

# Package Integrity Readiness

Package integrity should validate:

* Package directory exists.
* Package manifest exists.
* Manifest is valid JSON.
* Schema version is supported.
* Package ID matches directory.
* Required subdirectories exist.
* Referenced files exist.
* Referenced paths remain within approved package directories.
* File hashes match stored values.
* Package state transition is valid.
* Package is not corrupt.
* Package lock is valid.
* Package is not simultaneously executing elsewhere.

---

# File Path Safety

Every referenced file should:

* Use an approved local path.
* Remain inside approved candidate or package directories.
* Not use path traversal.
* Not point to temporary system locations unexpectedly.
* Not point to arbitrary user files.
* Not be a symbolic link to an unapproved location unless explicitly supported.

Example prohibited path:

```text
../../private_document.pdf
```

---

# File Hash Validation

Important files should be checked against stored hashes.

Examples:

* Active resume.
* Cover letter.
* Candidate-context snapshot.
* Job description.
* Prepared answers.
* Application Plan.

Hash mismatch should trigger:

* Refresh Required.
* Revalidation.
* User warning when the file was manually edited.

---

# Package Lock Readiness

Before queue admission or execution:

* Check whether a package lock exists.
* Confirm whether the lock belongs to an active process.
* Reject concurrent execution.
* Recover stale locks.
* Record lock acquisition.

Recommended lock metadata:

```json
{
  "package_id": "",
  "workflow_id": "",
  "process_id": null,
  "acquired_at": "",
  "operation": "browser_execution"
}
```

---

# Package Staleness Detection

A package is stale when its generated materials no longer correspond to current source inputs.

Potential staleness sources:

* Job description changed.
* Job title changed.
* Application URL changed.
* Candidate profile changed.
* Resume changed.
* Candidate rules changed.
* Salary preferences changed.
* Work-authorization information changed.
* Demographic preferences changed.
* Prompt templates changed.
* Reasoning model changed.
* Package schema changed.
* Active application settings changed.

---

# Staleness Fingerprint

The package should store hashes or versions for:

```json
{
  "job_description_hash": "",
  "candidate_context_hash": "",
  "candidate_rules_hash": "",
  "base_resume_hash": "",
  "active_resume_hash": "",
  "answer_library_version": "",
  "prompt_versions": {},
  "reasoning_models": {},
  "settings_hash": "",
  "schema_version": "1.0"
}
```

---

# Staleness Evaluation

```text
Stored Fingerprint
        vs
Current Inputs
```

Possible outcomes:

```text
current
partially_stale
stale
unknown
```

---

# Partial Staleness

Some changes require only partial regeneration.

Examples:

## Phone Number Changed

Refresh:

* Candidate context.
* Prepared personal answers.

Do not necessarily regenerate:

* Resume.
* Cover letter.
* Job analysis.

## Resume Changed

Refresh:

* Resume analysis.
* Resume selection.
* Tailored resume.
* Cover letter consistency.
* Narrative-answer consistency.

## Salary Rule Changed

Refresh:

* Salary answers.
* Application Review.
* Readiness report.

---

# Staleness Dependency Graph

The application should track dependencies.

Example:

```text
Candidate Work Authorization
        |
        +--> Prepared Sponsorship Answers
        +--> Application Review
        +--> Readiness

Base Resume
        |
        +--> Resume Tailoring
        +--> Cover Letter
        +--> Narrative Answers
        +--> Application Review
```

This allows selective refresh rather than full regeneration.

---

# Candidate Data Readiness

Candidate data should be considered Ready when:

* Candidate Knowledge Base is accessible.
* Required structured files are valid.
* Required identity fields exist.
* Required contact fields exist.
* Work-authorization fields required by the application exist.
* Required employment records are available.
* Required education records are available.
* Candidate rules are loaded.
* Sensitive-field policy is loaded.
* No required field has conflicting trusted sources.

---

# Candidate Data Conflict

Example:

```text
candidate.json:
Current city = Boston

preferences.md:
Currently living in New York
```

The system should:

* Identify source priority.
* Flag material conflicts.
* Avoid choosing arbitrarily when both are authoritative.
* Request user input when necessary.

---

# Candidate Identity Requirements

Common required identity fields:

* Legal first name.
* Legal last name.
* Email.
* Phone.
* Country.
* Address when required.
* Preferred name when used.

The readiness system should not require optional identity fields unless the actual application needs them.

---

# Work Authorization Readiness

Before browser execution, verify that the Candidate Knowledge Base can answer likely questions about:

* Current authorization.
* Current sponsorship need.
* Future sponsorship need.
* Visa status.
* Petition transfer requirement when applicable.
* Country-specific eligibility.

If the job or ATS regularly asks these questions and no stored data exists, mark User Action Required before execution when practical.

---

# Employment Readiness

Employment data should be Ready when:

* Employer names are present.
* Job titles are present.
* Start dates are present.
* End dates or current-role indicators are valid.
* Records do not contain impossible date sequences.
* Required responsibilities or descriptions exist when the ATS needs them.
* Contractor or employment-type distinctions are preserved.
* Reason-for-leaving answers exist only when required.

---

# Education Readiness

Education data should be Ready when:

* Institution is present.
* Degree is present.
* Field of study is present when applicable.
* Graduation date or status is available.
* No contradictory degree status exists.
* GPA disclosure policy is available when relevant.

---

# Resume Readiness

The active resume is Ready when:

* A base resume was selected.
* Active version is defined.
* File exists.
* File hash is valid.
* Resume validation passes.
* No unsupported claim exists.
* Correct candidate identity appears.
* Employer and date checks pass.
* File format is accepted.
* File size is within configured limits.
* Page count is acceptable.
* Layout validation passes.
* Approval requirements are satisfied.
* File is listed in the Application Plan.

---

# Unmodified Resume Readiness

When resume tailoring is disabled:

* Original resume must be valid.
* Original file must remain unchanged.
* File format must be accepted.
* Candidate rules must permit use.
* The Application Package should record that no tailoring occurred.
* Browser should upload the approved original file.

---

# Cover Letter Readiness

A cover letter is Ready when:

* Requirement status is known.
* It exists when required.
* Active version is defined.
* Factual validation passes.
* Resume consistency passes.
* Correct company and role are referenced.
* Word and character limits pass.
* Required format exists.
* Layout validation passes.
* Approval requirements are satisfied.
* File is listed in the Application Plan.

If optional and omitted, readiness should pass when user rules permit omission.

---

# Supporting Document Readiness

Each supporting document should be validated for:

* Requirement status.
* Approved source.
* Correct file.
* Correct document type.
* File readability.
* File format.
* File size.
* Privacy.
* Relevance.
* Application Plan inclusion.

---

# Application Answer Readiness

The prepared answer set is Ready when:

* Required predicted questions are resolved.
* Exact answers have valid sources.
* Controlled-choice mappings are valid.
* Narrative answers pass factual validation.
* Length restrictions pass.
* Candidate rules pass.
* Cross-answer consistency passes.
* Resume consistency passes.
* Cover-letter consistency passes.
* Sensitive-field policies pass.
* Required approvals exist.
* Unresolved optional questions are documented.

---

# Runtime Answer Readiness

Unexpected application questions may appear during browser execution.

The package should remain runtime-ready when:

* Unknown-question resolution is allowed.
* Relevant candidate context can be retrieved.
* Reasoning provider is available when needed.
* User intervention can be requested.
* Browser state can be paused safely.
* Runtime answers can be added to the package and reviewed.

---

# Application Plan Readiness

The Application Plan should contain:

* Package ID.
* Application URL.
* Expected ATS.
* Automation mode.
* Active resume.
* Cover-letter requirement and path.
* Supporting documents.
* Expected sections.
* Expected answer families.
* Browser profile.
* Review mode.
* Submission policy.
* Stop conditions.
* Retry limits.
* CAPTCHA policy.
* Account-creation policy.
* Generic-adapter fallback policy.

---

# Application Plan Validation

Validate that:

* Application URL matches the job.
* File references exist.
* Automation mode is allowed.
* Browser profile exists or can be created.
* Stop conditions are valid.
* Required review mode is respected.
* Submission policy matches candidate rules.
* No prohibited automatic action is enabled.
* Expected ATS is valid or marked unknown.

---

# Browser Prerequisite Readiness

Before queue admission, verify:

* Playwright is installed.
* Chromium is installed.
* Browser can launch.
* Browser profile directory is writable.
* Profile is not in conflicting use.
* Screenshot directory is writable.
* Download directory is writable.
* File-upload paths are accessible.
* Network is available when required.
* Application domain is permitted.
* Browser mode is configured.
* Browser health check is current.

---

# Browser Health Check Freshness

A browser health check may be cached for a limited duration.

Example:

```json
{
  "browser_health_check": {
    "status": "passed",
    "checked_at": "",
    "valid_for_minutes": 60
  }
}
```

A new check may be required after:

* Browser upgrade.
* Playwright upgrade.
* Profile error.
* Browser crash.
* Operating-system restart.
* Configuration change.

---

# Authentication Readiness

If the ATS requires login, readiness should determine whether:

* Existing browser session is authenticated.
* Account creation is allowed.
* Required email is available.
* Password source is secure.
* Multifactor authentication may require user action.
* Login page is expected.
* User intervention workflow is available.

A package may still be Ready with a planned login pause.

---

# CAPTCHA Readiness

CAPTCHA presence cannot always be predicted.

The package is runtime-ready when:

* CAPTCHA detection exists.
* Browser runs visibly when user action is needed.
* Workflow can pause.
* Current state can be preserved.
* User can resume the application afterward.

The readiness system should not claim that CAPTCHA handling is automated.

---

# ATS Adapter Readiness

Before execution:

* Detect expected ATS.
* Check whether a dedicated adapter exists.
* Check adapter status.
* Check adapter version.
* Determine whether generic fallback is allowed.
* Confirm required control types are supported.

Possible statuses:

```text
dedicated_adapter_ready
generic_adapter_ready
degraded_adapter
unsupported
```

---

# Unsupported ATS Workflow

If the portal requires an unsupported control or workflow:

* Mark User Action Required or Blocked.
* Preserve prepared materials.
* Offer Manual mode.
* Do not attempt arbitrary Claude-generated browser scripting.
* Store diagnostic evidence.

---

# Queue Admission Controller

## Responsibility

Make the final decision about whether a package may enter the application queue.

Conceptual interface:

```text
QueueAdmissionService

    evaluate_package(package_id)
    acquire_package_lock(package_id)
    assign_queue_position(package_id)
    admit(package_id)
    reject(package_id, findings)
    release_package_lock(package_id)
```

---

# Queue Admission Rules

A package may enter the queue when:

* Browser Execution Readiness is Ready or permitted Ready with Warnings.
* Package status is Ready.
* Package is not already queued.
* Package is not executing.
* Package lock can be acquired.
* Duplicate check passes.
* No prior unknown submission exists.
* User has not cancelled the package.
* Batch size limit is not exceeded.
* Queue policy permits the selected order.

---

# Queue Rejection Reasons

Examples:

* Not ready.
* Already applied.
* Submission unknown.
* Stale package.
* Missing active resume.
* Required answer unresolved.
* Package locked.
* Browser unavailable.
* Adapter unsupported.
* Manual approval required.
* Candidate rule violation.

---

# Queue Admission Result

```json
{
  "package_id": "",
  "status": "admitted",
  "queue_position": 4,
  "queue_strategy": "selected_order",
  "admitted_at": "",
  "warnings": []
}
```

---

# Queue Ordering Readiness

When multiple jobs are selected, validate:

* Each package independently.
* Queue order is deterministic.
* User-selected order is preserved by default.
* Failed packages do not block ready packages.
* Already-applied packages are excluded.
* Packages requiring user input remain outside the active execution queue.

---

# Batch Readiness Summary

Example:

```json
{
  "selected_jobs": 10,
  "ready": 6,
  "ready_with_warnings": 1,
  "user_action_required": 2,
  "already_applied": 1,
  "blocked": 0,
  "failed": 0
}
```

The user interface should clearly show why each package did or did not enter the queue.

---

# Parallel Preparation and Readiness

Application preparation may occur in parallel.

Readiness evaluation may also occur in parallel for independent packages.

Queue admission should remain synchronized to avoid:

* Duplicate positions.
* Duplicate locks.
* Duplicate browser execution.
* Conflicting status updates.

---

# Execution-Time Readiness Recheck

A package should be rechecked immediately before browser execution.

Reasons:

* Files may have changed.
* Candidate rules may have changed.
* Application may have been submitted manually.
* Package may have become stale.
* Job may have closed.
* Browser profile may be unavailable.
* Queue wait may have been long.

---

# Pre-Execution Recheck

Minimum checks:

* Package status.
* Package lock.
* Duplicate application.
* Active resume file.
* Required documents.
* Candidate-rule hash.
* Application URL.
* Job availability when detectable.
* Browser health.
* Adapter availability.

---

# Page-Level Runtime Readiness

Before filling each application page, verify:

* Correct application remains open.
* Page inspection succeeded.
* Required controls are supported.
* Answers can be resolved.
* Browser state is stable.
* No login or CAPTCHA blocks execution.
* Current page is compatible with saved execution state.

---

# Next-Page Readiness

Before clicking Next or Continue:

* Required fields are filled.
* Browser validation passes.
* Uploaded files are complete.
* Conditional fields are resolved.
* No visible blocking error remains.
* Current page state has been saved.

---

# Review Readiness

Before opening manual review:

* Final browser values are extracted.
* Uploaded files are known.
* Application Review report exists.
* Screenshots or review-page snapshot exist.
* User-facing data is available.
* Sensitive fields can be hidden or revealed safely.
* Browser session remains resumable.

---

# Submission Readiness Recheck

Submission readiness should be evaluated immediately before clicking Submit.

This check should be stricter than earlier readiness checks.

---

# Final Submission Requirements

The system should require:

```text
Correct job identity
Correct candidate identity
Correct active resume
Required cover letter
Required supporting documents
All required fields complete
No browser validation errors
No unresolved required answers
No unsupported claims
No cross-artifact contradictions
Candidate rules passed
Privacy checks passed
Duplicate check passed
No prior unknown submission
Current application page verified
Review approval valid
Submit control verified
Submission lock acquired
```

---

# Submission Lock

Before the final submission action, acquire a dedicated submission lock.

Example:

```json
{
  "package_id": "",
  "workflow_id": "",
  "operation": "final_submission",
  "acquired_at": ""
}
```

The lock should remain until:

* Submission succeeds.
* Submission clearly fails.
* Submission becomes unknown.
* Workflow is safely cancelled before clicking Submit.

---

# Approval Readiness

Approval should be considered valid only when it references the active artifact versions.

Example:

```json
{
  "approved_resume_version": 2,
  "approved_cover_letter_version": 1,
  "approved_answer_set_version": 3,
  "approved_form_snapshot_hash": "",
  "approved_at": ""
}
```

If any referenced artifact changes, approval becomes invalid.

---

# Review Approval Requirements

Depending on automation mode:

## Automatic Mode

Requires:

* Automated Application Review approved.
* No manual-review rule.
* No blocking issue.
* No required user input.
* Valid active artifact versions.

## Review Mode

Requires:

* User approval record.
* Active artifact versions match the approval record.
* No subsequent material browser changes.

## Manual Mode

Submission readiness may remain false because the application is intended for manual completion.

---

# Duplicate Application Readiness

Duplicate checks should occur:

1. Before package creation.
2. Before queue admission.
3. Before browser execution.
4. Immediately before final submission.
5. Before tracker synchronization.

---

# Duplicate Matching Strategy

Use:

1. Exact job ID.
2. Canonical application URL.
3. ATS requisition ID.
4. Company, title, and location.
5. Strong semantic similarity when identifiers are unavailable.
6. Existing submitted Application Packages.

---

# Duplicate Match Result

```json
{
  "status": "duplicate",
  "matched_record": {
    "company": "",
    "job_title": "",
    "job_id": "",
    "date_applied": ""
  },
  "confidence": 100,
  "override_allowed": true
}
```

---

# Duplicate Override

When the user overrides a duplicate warning:

* Record the reason.
* Record the matched prior application.
* Require confirmation.
* Preserve the override in package metadata.
* Recheck whether the prior application was for a different location or requisition.

The application should not silently override duplicates.

---

# Job Availability Readiness

When practical, check whether:

* Application URL still loads.
* Job is still open.
* Apply button exists.
* Deadline has not passed.
* Posting is not marked filled.
* Portal does not state that applications are closed.

---

# Closed Job

If the job is closed:

```text
Status:
blocked or closed
```

Actions:

* Remove from active queue.
* Preserve prepared materials.
* Update local job status.
* Do not submit.
* Allow the user to retain the package for reference.

---

# Changed Job

If the job description or title materially changes:

* Mark Refresh Required.
* Update the job snapshot only after preserving the original.
* Rerun job analysis.
* Rerun ranking.
* Revalidate resume and answers.
* Require renewed approval when applicable.

---

# Submission Safety Validator

## Responsibility

Confirm that the system can attempt submission without a high risk of misrepresentation, duplication, or data leakage.

Checks include:

* Job identity.
* Candidate identity.
* Artifact versions.
* Review status.
* Browser state.
* Duplicate status.
* Privacy policy.
* Sensitive-field handling.
* Attestation authorization.
* Prior submission state.
* Destination trust.
* Submit-button semantics.

---

# Destination Trust

Before uploading files or submitting data, verify that:

* Current domain is expected.
* Redirect path is associated with the application.
* TLS is present for external destinations.
* Domain is recognized company or ATS infrastructure.
* No suspicious unrelated domain appears.
* Application is not embedded in an untrusted third-party page unexpectedly.

---

# Suspicious Destination

If the application redirects to an unknown domain requesting sensitive information:

* Pause execution.
* Capture evidence.
* Mark User Action Required or Blocked.
* Do not upload files.
* Do not submit personal data.
* Require explicit user confirmation after inspection.

---

# Sensitive Field Readiness

For every sensitive field, verify:

* Field is required or intentionally answered.
* Local policy permits handling.
* Exact value source is secure.
* Value is not being sent to Claude.
* Destination is trusted.
* Logging is redacted.
* Browser value can be verified safely.

---

# Government ID Readiness

Possible policies:

```text
manual_only
secure_local_autofill
never_provide
ask_each_time
```

A package should not be Submission Ready when a required government-ID field conflicts with the user's policy.

---

# Attestation Readiness

Before automating a legal attestation:

* Full statement extracted.
* Candidate rule authorizes automated attestation.
* Application Review has passed.
* Required answers are complete.
* Exact legal name is available.
* No unresolved inconsistency exists.
* Attestation record can be stored.

---

# CAPTCHA and Authentication Readiness

A package may remain execution-ready even when a manual challenge is expected, but it is not submission-ready until:

* CAPTCHA is completed.
* Login is authenticated.
* Multifactor challenge is complete.
* Session is valid.
* Current application state is restored.

---

# Submission Unknown Handling

A package with Submission Unknown status must not become Submission Ready automatically.

Resolution methods:

* Inspect confirmation page.
* Inspect ATS dashboard.
* Check application history.
* Check confirmation email in future integrations.
* Ask the user.
* Confirm no tracker record exists only as supporting evidence, not proof of failure.

---

# Unknown State Resolution Result

```json
{
  "previous_status": "submission_unknown",
  "resolved_status": "submitted",
  "evidence": [
    "ATS dashboard shows Submitted"
  ],
  "resolved_at": ""
}
```

---

# Readiness Warning Policy

Warnings should not prevent progression unless:

* Candidate policy treats the category as blocking.
* Warning severity is High.
* Warning count exceeds a configured threshold.
* The warning involves legal, privacy, or duplication risk.

---

# Common Non-Blocking Warnings

Examples:

* Optional cover letter omitted.
* Optional demographic question skipped.
* Employer sponsorship policy is not stated.
* Preferred skill missing.
* One optional narrative answer was not prepared in advance.
* Application may require runtime login.

---

# Common Blocking Issues

Examples:

* No valid resume.
* Required cover letter missing.
* Required answer unresolved.
* Candidate rule violated.
* Unsupported claim remains.
* Job already applied to.
* Job closed.
* Package stale.
* Wrong job open.
* Sensitive-data policy conflict.
* Browser validation failed.
* Review approval missing.
* Previous submission unknown.
* Required file upload failed.

---

# Automatic Remediation

The readiness system may trigger safe remediation.

Examples:

* Regenerate a missing readiness report.
* Revalidate a file.
* Recompute a stale fingerprint.
* Reload candidate context.
* Rerender a PDF.
* Regenerate a shortened answer.
* Correct a missing exact field.
* Re-run duplicate checks.
* Release a stale lock.
* Refresh browser health status.

---

# Automatic Remediation Rules

Automatic remediation is allowed when:

* The correct action is deterministic.
* No user-approved edit is overwritten.
* Candidate facts are not changed.
* No final submission occurs.
* The action is logged.
* Readiness is reevaluated afterward.
* Retry count is bounded.

---

# Remediation Result

```json
{
  "remediation_id": "",
  "check_id": "active_resume_exists",
  "action": "rerender_resume_pdf",
  "status": "success",
  "attempt": 1,
  "verified": true
}
```

---

# Maximum Remediation Attempts

Recommended default:

```text
3 attempts per readiness issue
```

After the limit:

* Mark Not Ready or User Action Required.
* Preserve all diagnostics.
* Do not enter an infinite loop.

---

# User Action Requests

When readiness requires user action, provide a precise request.

Bad:

```text
Application is not ready.
```

Preferred:

```text
The application requires an answer to whether you are subject to a non-compete agreement. No reusable answer exists. Select Yes or No to continue.
```

---

# User Action Request Model

```json
{
  "request_id": "",
  "package_id": "",
  "category": "missing_candidate_answer",
  "message": "",
  "required_for_stage": "browser_execution",
  "available_actions": [],
  "can_save_for_reuse": true,
  "sensitive": true
}
```

---

# Readiness Report Storage

Recommended package files:

```text
readiness/
    preparation_readiness.json
    execution_readiness.json
    review_readiness.json
    submission_readiness.json
    history_sync_readiness.json
    checks.json
    remediations.json
```

A simpler MVP may store:

```text
readiness_report.json
```

---

# Readiness Report Metadata

```json
{
  "readiness_id": "",
  "package_id": "",
  "stage": "",
  "schema_version": "1.0",
  "evaluated_at": "",
  "application_version": "",
  "evaluator_version": "",
  "duration_ms": 0,
  "input_fingerprint": {}
}
```

---

# Readiness Summary for the User Interface

Example:

```text
Application Status: Ready for Browser Execution

Company: Google
Role: Senior Software Engineer
Package Integrity: Passed
Candidate Data: Passed
Resume: Passed
Cover Letter: Not Required
Prepared Answers: Passed
Duplicate Check: Passed
Browser Health: Passed
Application Review: Passed

Warnings:
The portal may require account login.
```

---

# Not-Ready Summary Example

```text
Application Status: User Action Required

Blocking Item:
A required conflict-of-interest question has no stored answer.

Action:
Provide the answer and optionally save it to your reusable applicant profile.
```

---

# Readiness Dashboard

The user interface should show for each package:

* Package status.
* Current readiness stage.
* Readiness status.
* Blocking issues.
* Warnings.
* Required user actions.
* Staleness.
* Queue eligibility.
* Review status.
* Duplicate status.
* Next allowed action.

---

# Next Allowed Actions

Possible actions:

```text
prepare
refresh
resolve_missing_information
review
queue
execute
resume_execution
approve
submit
verify_submission
sync_history
archive
skip
cancel
```

The readiness system should explicitly return the allowed next action rather than leaving the UI to infer it.

---

# State Transitions

Readiness should control workflow-state transitions.

Example:

```text
Preparing
    |
    +-- Readiness passed --> Ready
    |
    +-- Missing information --> Needs Attention
    |
    +-- Stale inputs --> Refresh Required
    |
    +-- Duplicate --> Already Applied
```

---

# Browser Execution Transition

Allowed:

```text
Ready -> Queued -> Executing
```

Not allowed:

```text
Needs Attention -> Executing
```

unless readiness is reevaluated and passes.

---

# Submission Transition

Allowed:

```text
Ready for Review
    |
    +-- Review approved --> Submitting
```

or:

```text
Executing
    |
    +-- Automatic review approved --> Submitting
```

Not allowed:

```text
Submission Unknown -> Submitting
```

without explicit resolution.

---

# Readiness and Cancellation

The user may cancel a package at any point before submission.

On cancellation:

* Stop new readiness evaluations.
* Release queue and package locks.
* Preserve generated artifacts.
* Mark Cancelled.
* Remove from active queue.
* Do not delete the package automatically.

---

# Readiness and Skip

The user may skip a package because:

* Job is no longer desirable.
* Too many unresolved questions exist.
* Application is too long.
* Salary is unsuitable.
* ATS is unsupported.
* Manual intervention is not worthwhile.

The skip reason should be stored.

---

# Readiness and Manual Mode

A package may be considered Ready for Manual Completion even when it is not Ready for Automatic Browser Execution.

Example:

```text
Prepared resume: Ready
Cover letter: Ready
Answers: Partially ready
ATS adapter: Unsupported
```

The system may provide:

* Application URL.
* Final documents.
* Prepared answers.
* Manual-completion checklist.

---

# Manual Completion Package

Possible status:

```text
ready_for_manual_completion
```

This allows the user to benefit from preparation even when browser automation cannot complete the portal.

---

# Readiness Service Interface

Conceptual interface:

```text
ApplicationReadinessService

    evaluate_preparation_readiness(package_id)
    evaluate_execution_readiness(package_id)
    evaluate_review_readiness(package_id)
    evaluate_submission_readiness(package_id)
    evaluate_history_sync_readiness(package_id)

    validate_package_integrity(package_id)
    detect_staleness(package_id)
    validate_candidate_data(package_id)
    validate_documents(package_id)
    validate_answers(package_id)
    validate_application_plan(package_id)
    validate_browser_prerequisites(package_id)
    validate_review_approval(package_id)
    validate_duplicate_status(package_id)
    validate_submission_safety(package_id)

    remediate_safe_issues(package_id)
    request_user_action(package_id)
    admit_to_queue(package_id)
    get_next_allowed_action(package_id)
```

---

# Separation of Responsibilities

## Readiness Evaluator

Determines whether a stage may proceed.

## Application Review System

Evaluates correctness, quality, and consistency.

## Package Service

Stores and updates package artifacts.

## Queue Service

Controls execution order.

## Browser Engine

Executes form interactions.

## Submission Engine

Performs and verifies final submission.

The readiness system should coordinate outputs from these components but should not duplicate their internal responsibilities.

---

# Readiness Error Types

Recommended internal errors:

```text
ApplicationReadinessError
ReadinessConfigurationError
ReadinessEvaluationError
PackageIntegrityReadinessError
PackageStaleError
CandidateDataNotReadyError
DocumentNotReadyError
AnswerSetNotReadyError
BrowserNotReadyError
ReviewNotApprovedError
DuplicateApplicationReadinessError
SubmissionSafetyError
QueueAdmissionError
PackageLockError
ReadinessRemediationError
```

---

# Readiness Logging

Logs may include:

* Package ID.
* Readiness stage.
* Readiness status.
* Check ID.
* Check result.
* Warning count.
* Blocking count.
* Required user action count.
* Staleness result.
* Duplicate result.
* Queue-admission result.
* Duration.
* Retry count.

Logs should not include sensitive answer values by default.

---

# Readiness Metrics

Useful local metrics include:

* Packages evaluated.
* Packages ready on first evaluation.
* Packages requiring refresh.
* Packages requiring user action.
* Duplicate applications prevented.
* Stale packages detected.
* Missing documents detected.
* Browser prerequisite failures.
* Queue admissions.
* Queue rejections.
* Submission-readiness failures.
* Average remediation attempts.
* Average time from Selected to Ready.
* Manual-mode fallbacks.

These metrics should not imply hiring success.

---

# Readiness Testing

Testing should include:

* Stage-specific requirements.
* Package integrity.
* Missing file detection.
* Invalid file hash.
* Staleness detection.
* Selective refresh.
* Candidate-data conflicts.
* Resume readiness.
* Optional cover-letter handling.
* Required cover-letter handling.
* Supporting-document requirements.
* Answer readiness.
* Browser health.
* Profile lock.
* Adapter readiness.
* Queue admission.
* Duplicate checks.
* Job closure.
* Review approval invalidation.
* Submission unknown.
* Sensitive-field policy.
* Manual-mode fallback.
* Automatic remediation.
* Bounded retry behavior.
* State transitions.

---

# Required Test Scenarios

## Fully Ready Package

Package contains:

* Valid job.
* Valid resume.
* No required cover letter.
* Complete answers.
* Valid plan.
* Browser available.
* Review passed.
* No duplicate.

Expected:

```text
Ready
```

Next action:

```text
Queue Application
```

---

## Missing Resume

Active resume path does not exist.

Expected:

* Not Ready.
* Blocking document issue.
* Attempt safe rerender when source exists.
* Queue admission denied.

---

## Required Cover Letter Missing

Application form requires a cover letter.

Expected:

* Not Ready.
* Cover-letter generation required.
* Browser execution blocked until resolved.

---

## Optional Cover Letter Missing

Cover letter is optional and user rules permit omission.

Expected:

* Ready.
* Optional warning or informational record only.

---

## Missing Required Legal Answer

Required non-compete question has no stored response.

Expected:

* User Action Required.
* No automatic inference.
* Package excluded from execution queue.

---

## Stale Candidate Context

Candidate work-authorization data changed after package preparation.

Expected:

* Refresh Required.
* Refresh sponsorship answers and review.
* Existing approval invalidated.

---

## Changed Resume

Base resume file hash changed.

Expected:

* Refresh Required.
* Rerun resume analysis, tailoring, cover-letter consistency, and review.

---

## Duplicate Application

Tracker contains matching job ID.

Expected:

* Already Applied.
* Queue admission denied.
* Explicit user override required.

---

## Similar Job but Different Requisition

Same company and title, different job ID and location.

Expected:

* Not automatically treated as exact duplicate.
* Similarity warning may appear.
* Application may proceed after deterministic comparison.

---

## Browser Profile In Use

Persistent profile is locked by another process.

Expected:

* Not Ready.
* Retry or ask user to close the other session.
* Do not launch conflicting execution.

---

## Unsupported ATS

No adapter supports the application, and generic fallback is disabled.

Expected:

* Blocked for automatic execution.
* Offer Manual completion mode.

---

## CAPTCHA Expected

The site displays a CAPTCHA after opening.

Expected:

* Browser execution pauses.
* User Action Required.
* Package state preserved.
* Readiness resumes after completion.

---

## Review Approval Missing

Automation mode is Review, but no approval record exists.

Expected:

* Not Ready for Submission.
* Ready for Manual Review.
* Submit action unavailable.

---

## Approval Invalidated

User edits a narrative answer after approval.

Expected:

* Approval invalidated.
* Review and submission readiness rerun.

---

## Wrong Job Open

Package is for Job ID 123, but browser shows Job ID 456.

Expected:

* Blocked.
* No submission.
* Navigation recovery required.

---

## Submission Unknown

Prior attempt clicked Submit without confirmation.

Expected:

* Submission Unknown.
* No automatic retry.
* Require dashboard or user verification.

---

## Job Closed

Apply control is absent, and portal states applications are closed.

Expected:

* Blocked or Closed.
* Removed from active queue.
* Prepared package preserved.

---

## Sensitive ID Policy Conflict

Portal requires Social Security number before submission.

User policy is `never_provide`.

Expected:

* Blocked.
* No value entered.
* Explain the policy conflict.

---

## Ready with Warning

All mandatory requirements pass, but sponsorship availability is unknown.

Expected:

* Ready with Warnings.
* Workflow may proceed based on user policy.

---

## Stale Lock

Package lock exists, but owning process no longer exists.

Expected:

* Recover stale lock.
* Log recovery.
* Rerun readiness.

---

## Automatic Remediation Failure

PDF is missing and rerender fails three times.

Expected:

* Not Ready.
* Remediation stops.
* User Action Required or Failed.
* No infinite retry.

---

# Readiness Regression Fixtures

Recommended fixtures:

```text
tests/sample_data/readiness/
    ready_package/
    ready_with_warnings/
    missing_resume/
    required_cover_letter_missing/
    unresolved_legal_answer/
    stale_candidate_context/
    duplicate_application/
    browser_profile_locked/
    unsupported_ats/
    review_approval_missing/
    submission_unknown/
    closed_job/
    sensitive_policy_conflict/
```

Fixtures must use synthetic candidate data.

---

# Definition of Application Readiness Completion

The Application Readiness system is complete when:

* Stage-specific readiness can be evaluated.
* Preparation readiness works.
* Browser-execution readiness works.
* Review readiness works.
* Submission readiness works.
* History-synchronization readiness works.
* Mandatory and conditional artifacts are resolved.
* Package integrity is validated.
* File references and hashes are checked.
* Stale packages are detected.
* Selective refresh requirements are produced.
* Candidate data readiness is validated.
* Resume, cover letter, and supporting documents are validated.
* Answer-set readiness is validated.
* Application Plan readiness is validated.
* Browser prerequisites are validated.
* ATS-adapter readiness is validated.
* Duplicate applications are blocked.
* Job closure is detected when possible.
* Approval validity is checked against active versions.
* Sensitive-field policies are enforced.
* Prior unknown submission states block resubmission.
* Safe remediation is supported.
* Remediation attempts are bounded.
* Required user actions are explicit.
* Queue admission uses readiness results.
* Execution-time readiness is rechecked.
* Final submission readiness is rechecked immediately before Submit.
* Manual-completion fallback is supported.
* Structured readiness reports are stored.
* State transitions reject invalid progression.
* Automated applications cannot proceed from an unready state.

---

# Summary

The Application Readiness system is the workflow gatekeeper.

It determines whether an Application Package has everything required to advance safely to the next stage.

It validates:

* Package integrity.
* Job identity.
* Candidate data.
* Resume.
* Cover letter.
* Supporting documents.
* Application answers.
* Application Plan.
* Browser prerequisites.
* Review approval.
* Duplicate status.
* Submission safety.
* Package freshness.

Application Review asks:

```text
Is this application correct, consistent, and safe?
```

Application Readiness asks:

```text
Has every mandatory condition for the next step been satisfied?
```

Only packages that pass both review and readiness should proceed to automated execution or final submission.

The readiness system should favor explicit states, deterministic checks, bounded remediation, clear user actions, and prevention of duplicate or uncertain submissions.
