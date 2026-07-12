# 07A - Application Packages

## LLM-Powered Autonomous Job Search & Application Platform

Version: 1.0

---

# Purpose

This document defines the Application Package system.

An Application Package is the complete local, job-specific bundle used to prepare, execute, review, submit, recover, and audit a single job application.

Every selected job should have its own Application Package before browser automation begins.

The Application Package acts as the contract between:

* Job analysis
* Candidate context
* Resume selection
* Resume tailoring
* Answer generation
* Browser automation
* Human review
* Submission verification
* Application tracking

The browser should not begin an application using scattered files or unstructured context.

It should receive one validated package containing all information required for that job.

---

# Core Principle

One selected job equals one Application Package.

```text
Selected Job
    |
    v
Application Preparation
    |
    v
Application Package
    |
    v
Readiness Validation
    |
    v
Application Queue
    |
    v
Browser Execution
    |
    v
Submission Result
```

An Application Package should exist before the browser begins interacting with the application form.

---

# Why Application Packages Are Required

Without Application Packages, the system may need to:

* Reanalyze the job repeatedly.
* Reload candidate files during browser execution.
* Regenerate answers while the application is open.
* Search for the correct resume during submission.
* Repeat Claude calls after temporary browser failures.
* Lose work when a browser session closes.
* Mix files between different jobs.
* Submit the wrong resume.
* Lose track of which answers were used.

Application Packages prevent these problems.

They make the application workflow:

* Deterministic
* Resumable
* Auditable
* Testable
* Recoverable
* Easier to debug
* Easier to review
* Safer for batch execution

---

# Application Package Responsibilities

An Application Package should contain or reference:

* The selected job
* Job metadata
* Raw job description
* Structured job analysis
* Match score and recommendation
* Candidate context used for the application
* Candidate rules
* Selected base resume
* Tailored resume
* Resume-change report
* Cover letter when required
* Reusable application answers
* Job-specific narrative answers
* Application plan
* Expected ATS platform
* Browser execution state
* Review status
* Submission result
* Screenshots
* Logs
* Confirmation evidence
* Package metadata

---

# Application Package Lifecycle

The package lifecycle should use explicit states.

```text
Created
    |
    v
Collecting Context
    |
    v
Selecting Resume
    |
    v
Generating Materials
    |
    v
Validating
    |
    +------> Needs Attention
    |
    v
Ready
    |
    v
Queued
    |
    v
Executing
    |
    +------> Waiting for User
    |
    +------> Failed
    |
    v
Ready for Review
    |
    v
Submitting
    |
    +------> Submission Unknown
    |
    v
Submitted
```

---

# Package States

The following package states should be supported.

## Created

The package directory and metadata have been created.

No preparation work is complete.

---

## Collecting Context

The system is gathering:

* Candidate facts
* Resume information
* Job details
* Candidate rules
* Application history
* Relevant reusable answers

---

## Selecting Resume

The system is evaluating available resumes and selecting the strongest base resume.

---

## Generating Materials

The system is generating or preparing:

* Tailored resume
* Cover letter
* Application answers
* Application plan
* Supporting documents

---

## Validating

The package is being checked for:

* Missing data
* Unsupported claims
* Missing files
* Invalid paths
* Candidate-rule conflicts
* Duplicate application risk
* Readiness for browser execution

---

## Needs Attention

The package cannot proceed automatically.

Examples:

* No suitable resume exists.
* Required candidate information is missing.
* Resume tailoring introduced unsupported claims.
* Salary expectations are unavailable.
* Required document is missing.
* Work-authorization answer is unresolved.
* The job may already have been applied to.
* Application URL is invalid.

---

## Ready

The package has passed readiness validation and may enter the application queue.

---

## Queued

The package is waiting for browser execution.

---

## Executing

The browser is actively processing the application.

---

## Waiting for User

The workflow requires user action.

Examples:

* CAPTCHA
* Login
* Multifactor authentication
* Unresolved question
* Manual document request
* Optional review
* Unknown submission state

---

## Ready for Review

The form has been completed and is waiting for optional user review before submission.

---

## Submitting

The browser has initiated final submission and is waiting for a result.

---

## Submitted

The application has been verified as successfully submitted.

---

## Submission Unknown

The final submission action occurred, but the system cannot confirm success or failure.

The application must not be resubmitted automatically.

---

## Failed

The package could not be prepared or executed successfully.

The package should retain all generated files and state for diagnosis or retry.

---

## Skipped

The user or system intentionally skipped the job.

---

## Cancelled

The user cancelled preparation or execution.

---

## Already Applied

The application tracker indicates that the same job has already been submitted.

---

# Package Identity

Every Application Package should have a stable unique identifier.

Recommended format:

```text
{company_slug}_{job_id}_{created_timestamp}
```

Example:

```text
google_123456_20260710T221500
```

If no job ID exists:

```text
{company_slug}_{title_hash}_{created_timestamp}
```

Example:

```text
microsoft_8f3a91c2_20260710T221500
```

The package ID should remain unchanged throughout the workflow.

---

# Package Directory Structure

Recommended structure:

```text
user_data/
    applications/
        packages/
            google_123456_20260710T221500/
                package.json
                status.json
                job/
                    job.json
                    raw_description.txt
                    analysis.json
                    ranking.json
                candidate/
                    context.json
                    rules_snapshot.md
                    answer_sources.json
                resume/
                    base_resume_reference.json
                    tailored_resume.docx
                    tailored_resume.pdf
                    tailoring_plan.json
                    change_report.json
                    validation_report.json
                cover_letter/
                    cover_letter.md
                    cover_letter.docx
                    cover_letter.pdf
                    metadata.json
                answers/
                    prepared_answers.json
                    unresolved_questions.json
                    answer_sources.json
                plan/
                    application_plan.json
                    expected_fields.json
                    execution_preferences.json
                execution/
                    state.json
                    completed_pages.json
                    field_actions.json
                    uploaded_files.json
                    errors.json
                review/
                    review_report.json
                    user_changes.json
                    approval.json
                submission/
                    result.json
                    confirmation.txt
                    confirmation_page.html
                    confirmation_metadata.json
                screenshots/
                logs/
```

Not every directory must contain files for every application.

For example, the cover-letter directory may remain empty when no cover letter is required.

---

# Minimal MVP Package Structure

The MVP may begin with a simpler structure.

```text
applications/
    packages/
        {package_id}/
            package.json
            job.json
            analysis.json
            candidate_context.json
            application_plan.json
            answers.json
            resume.pdf
            state.json
            submission_result.json
            screenshots/
            logs/
```

The more detailed structure may be introduced as features are implemented.

---

# package.json

`package.json` is the main package manifest.

It should contain high-level package metadata and references to package files.

Example:

```json
{
  "package_id": "google_123456_20260710T221500",
  "schema_version": "1.0",
  "created_at": "2026-07-10T22:15:00-04:00",
  "updated_at": "2026-07-10T22:22:00-04:00",
  "status": "ready",
  "candidate_profile_id": "default",
  "job": {
    "company": "Google",
    "title": "Senior Software Engineer",
    "job_id": "123456",
    "application_url": "https://example.com/job/123456"
  },
  "match_score": 91,
  "selected_resume": "resume/tailored_resume.pdf",
  "cover_letter": null,
  "answers_file": "answers/prepared_answers.json",
  "application_plan": "plan/application_plan.json",
  "execution_state": "execution/state.json",
  "submission_result": "submission/result.json",
  "automation_mode": "review",
  "expected_ats": "custom"
}
```

---

# Package Schema Versioning

Every package should include a schema version.

Example:

```json
{
  "schema_version": "1.0"
}
```

Schema versioning allows future versions of the application to:

* Load older packages
* Migrate package structures
* Detect incompatible files
* Preserve auditability
* Update only required data

The application should not silently rewrite older packages without creating a backup or migration record.

---

# Job Snapshot

Every package should contain a snapshot of the selected job.

This snapshot should remain unchanged even if the original job listing later changes or disappears.

Required fields:

* Company
* Job title
* Job ID
* Application URL
* Source URL
* ATS platform
* Country
* Location
* Remote status
* Employment type
* Date posted
* Date discovered
* Salary range when available
* Raw description
* Structured analysis
* Match score
* Recommendation

---

# Why Store a Job Snapshot?

The job listing may later:

* Be removed
* Change title
* Change qualifications
* Change location
* Expire
* Redirect elsewhere
* Become unavailable

The package must preserve the exact version of the job used to create the application materials.

---

# Raw Job Description

Store the original extracted description in:

```text
job/raw_description.txt
```

The raw description should be treated as untrusted external content.

It should not contain browser navigation text, cookie banners, or unrelated page content when those can be removed safely.

---

# Structured Job Analysis

Store the Claude-generated or deterministic job analysis in:

```text
job/analysis.json
```

Example:

```json
{
  "job_family": "Backend Engineering",
  "seniority": "Senior",
  "required_skills": [
    "Python",
    "Distributed Systems"
  ],
  "preferred_skills": [
    "Kubernetes"
  ],
  "required_experience_years": 6,
  "hard_requirements": [],
  "work_authorization_requirements": [],
  "ambiguities": []
}
```

---

# Ranking Snapshot

Store the candidate-to-job ranking in:

```text
job/ranking.json
```

Example:

```json
{
  "match_score": 91,
  "recommendation": "Strong Match",
  "matched_required_qualifications": [
    "Python",
    "Distributed Systems"
  ],
  "missing_required_qualifications": [],
  "missing_preferred_qualifications": [
    "Kubernetes"
  ],
  "suggested_resume": "Backend.pdf",
  "reasoning": "The candidate strongly matches the required backend qualifications."
}
```

---

# Candidate Context Snapshot

The package should contain the candidate context used during preparation.

Recommended file:

```text
candidate/context.json
```

This should be a task-specific snapshot rather than a copy of the entire Candidate Knowledge Base.

It may include:

* Identity
* Contact details
* Work authorization
* Employment records
* Education
* Relevant skills
* Relevant projects
* Candidate rules
* Search preferences
* Reusable answers
* Selected demographic responses
* Salary rules
* Relocation preferences

---

# Why Store the Candidate Context Snapshot?

Candidate files may change after the application is prepared.

The package should preserve which facts were used at preparation time.

This enables:

* Reproducibility
* Auditing
* Debugging
* Comparing later candidate updates
* Explaining why an answer was selected

---

# Candidate Context Minimization

The context snapshot should contain only information relevant to that application.

Do not copy unrelated sensitive files into every package.

Examples of information usually unnecessary for ranking or resume tailoring:

* Government identification numbers
* Passport information
* Unrelated demographic details
* Passwords
* Authentication credentials
* Browser cookies
* Unrelated supporting documents

---

# Candidate Rules Snapshot

Store the candidate rules applied to the package.

Recommended file:

```text
candidate/rules_snapshot.md
```

Examples:

* Never apply to contract positions.
* Do not claim relocation availability.
* Always answer future sponsorship as Yes.
* Use the Backend resume for backend roles.
* Do not generate cover letters unless required.

The package should preserve the exact rule set used during preparation.

---

# Answer Source Inventory

Store reusable candidate sources in:

```text
candidate/answer_sources.json
```

Example:

```json
{
  "first_name": {
    "value": "Suhas",
    "source": "candidate.json:personal.first_name"
  },
  "future_sponsorship": {
    "value": "Yes",
    "source": "candidate.json:work_authorization.may_require_sponsorship_in_future"
  },
  "salary_expectation": {
    "value": "Use stored salary rule",
    "source": "answers.md:salary_expectations"
  }
}
```

This helps the Answer Resolution Engine avoid repeatedly searching the Candidate Knowledge Base.

---

# Resume References

The package should preserve both:

* Base resume reference
* Final application resume

---

# Base Resume Reference

Recommended file:

```text
resume/base_resume_reference.json
```

Example:

```json
{
  "resume_id": "backend_resume",
  "original_path": "candidate/resume/Backend.pdf",
  "file_hash": "",
  "selected_at": "",
  "selection_reason": "",
  "selection_confidence": 94
}
```

The original resume should remain in the Candidate Knowledge Base.

The package should not modify it.

---

# Tailored Resume Files

Generated resume files may include:

```text
resume/tailored_resume.docx
resume/tailored_resume.pdf
```

The PDF is typically used for upload.

The DOCX may be retained for editing and review.

---

# Resume Tailoring Plan

Store the approved tailoring plan in:

```text
resume/tailoring_plan.json
```

The plan should describe:

* Summary changes
* Skill ordering
* Section ordering
* Bullet rewrites
* Content reduction
* Keywords to emphasize
* Content that must remain unchanged
* Supporting candidate sources

Detailed tailoring requirements are defined in `07B_Resume_Tailoring.md`.

---

# Resume Change Report

Store a human-readable or structured change report.

Recommended file:

```text
resume/change_report.json
```

Example:

```json
{
  "summary_changes": [],
  "reordered_sections": [],
  "revised_bullets": [
    {
      "original": "",
      "revised": "",
      "reason": "",
      "supporting_sources": []
    }
  ],
  "removed_content": [],
  "added_supported_keywords": [],
  "unsupported_claims_removed": []
}
```

---

# Resume Validation Report

Store resume validation results in:

```text
resume/validation_report.json
```

Example:

```json
{
  "status": "passed",
  "blocking_issues": [],
  "warnings": [],
  "unsupported_claims": [],
  "date_consistency": "passed",
  "employer_consistency": "passed",
  "education_consistency": "passed"
}
```

A resume with blocking validation failures must not be used in browser execution.

---

# Cover Letter Files

When a cover letter is required or enabled, store:

```text
cover_letter/cover_letter.md
cover_letter/cover_letter.docx
cover_letter/cover_letter.pdf
cover_letter/metadata.json
```

The metadata should include:

* Generation time
* Prompt version
* Model
* Word count
* Candidate facts used
* Validation status
* Whether the cover letter was required
* Whether the user approved it

Detailed cover-letter requirements are defined in `07C_Cover_Letters_And_Application_Answers.md`.

---

# Prepared Answers

Store prepared answers in:

```text
answers/prepared_answers.json
```

The file should contain both factual and narrative answers.

Example:

```json
{
  "answers": [
    {
      "answer_id": "work_authorization_us",
      "question_family": "work_authorization",
      "canonical_question": "Are you legally authorized to work in the United States?",
      "answer": "Yes",
      "selected_option": "Yes",
      "source": "candidate.json:work_authorization.authorized_to_work",
      "confidence": 100,
      "factual": true,
      "approved": true
    },
    {
      "answer_id": "why_company",
      "question_family": "why_company",
      "canonical_question": "Why do you want to work here?",
      "answer": "",
      "selected_option": null,
      "source": "reasoned_narrative_based_on_resume_and_job",
      "confidence": 91,
      "factual": false,
      "approved": true
    }
  ]
}
```

---

# Unresolved Questions

Store unresolved information in:

```text
answers/unresolved_questions.json
```

Example:

```json
{
  "questions": [
    {
      "question_family": "expected_start_date",
      "reason": "No notice period or start-date rule is stored.",
      "required_for_readiness": true,
      "requires_user_input": true
    }
  ]
}
```

Packages with unresolved required questions should usually enter `Needs Attention`.

---

# Application Plan

The Application Plan is the browser-facing preparation artifact.

Recommended file:

```text
plan/application_plan.json
```

It should describe:

* Target application URL
* Expected ATS
* Automation mode
* Resume file
* Cover-letter file
* Supporting documents
* Expected question families
* Expected application sections
* Known account requirements
* Submission preferences
* Review rules
* Stop conditions

---

# Example Application Plan

```json
{
  "package_id": "google_123456_20260710T221500",
  "application_url": "https://example.com/job/123456/apply",
  "expected_ats": "custom",
  "automation_mode": "review",
  "resume_file": "resume/tailored_resume.pdf",
  "cover_letter_file": null,
  "supporting_documents": [],
  "expected_sections": [
    "personal_information",
    "work_history",
    "education",
    "questionnaire",
    "review"
  ],
  "review_before_submit": true,
  "allow_unknown_question_resolution": true,
  "allow_account_creation": false,
  "stop_on_captcha": true,
  "stop_on_unknown_submission_state": true
}
```

---

# Expected Fields

The preparation engine may predict common application fields and store them in:

```text
plan/expected_fields.json
```

Examples:

* First name
* Last name
* Email
* Phone
* Address
* LinkedIn
* Resume upload
* Work authorization
* Sponsorship
* Relocation
* Salary expectations
* Demographic responses
* E-signature

This prediction is not authoritative.

The browser must still inspect the real form.

---

# Execution Preferences

Store job-specific execution preferences in:

```text
plan/execution_preferences.json
```

Example:

```json
{
  "browser_profile": "default",
  "visible_browser": true,
  "maximum_action_retries": 3,
  "capture_page_screenshots": true,
  "review_mode": "before_submit",
  "cookie_preference": "reject_optional",
  "allow_generic_adapter_fallback": true
}
```

---

# Package Creation Workflow

The package creation process should follow a defined sequence.

```text
Receive Selected Job
        |
        v
Check Duplicate Application
        |
        v
Create Package ID
        |
        v
Create Package Directory
        |
        v
Save Job Snapshot
        |
        v
Build Candidate Context
        |
        v
Select Base Resume
        |
        v
Generate Application Materials
        |
        v
Generate Application Plan
        |
        v
Validate Package
        |
        v
Assign Final Preparation Status
```

---

# Duplicate Check Before Package Creation

Before creating a package, check the local application tracker.

Use:

1. Job ID
2. Canonical application URL
3. Company + title + location
4. Semantic similarity when identifiers are unavailable

If already applied:

* Mark the selection `Already Applied`.
* Do not create a full package by default.
* Allow user override.
* Record the override in package metadata.

---

# Existing Package Check

The system should also check whether an Application Package already exists for the same job.

Possible situations:

* Package exists and is Ready
* Package exists and is Executing
* Package exists and Failed
* Package exists and Submitted
* Package exists but job data changed

The user should not receive duplicate packages accidentally.

---

# Reusing Existing Packages

The application may reuse an existing package when:

* The job is unchanged.
* Candidate source files are unchanged.
* The package schema is compatible.
* Generated materials remain valid.
* The package has not already been submitted.

The package should be regenerated when relevant inputs change.

---

# Package Input Fingerprint

Each package should store an input fingerprint.

The fingerprint may include hashes of:

* Job description
* Candidate context
* Selected base resume
* Candidate rules
* Prompt versions
* Model identifiers
* Package schema version
* Application settings

Example:

```json
{
  "input_fingerprint": {
    "job_hash": "",
    "candidate_context_hash": "",
    "base_resume_hash": "",
    "rules_hash": "",
    "prompt_versions_hash": "",
    "settings_hash": ""
  }
}
```

This helps determine whether generated materials are stale.

---

# Package Staleness

A package may become stale when:

* The job description changes.
* Candidate information changes.
* The base resume changes.
* Candidate rules change.
* Resume tailoring prompts change.
* Salary or sponsorship rules change.
* Package schema changes.

Stale packages should not execute automatically until revalidated.

---

# Package Refresh

A refresh operation may selectively regenerate:

* Candidate context
* Resume selection
* Tailored resume
* Cover letter
* Answers
* Application plan
* Readiness report

It should preserve:

* Existing screenshots
* Logs
* Previous versions
* User-approved edits
* Submission evidence

---

# Package Immutability After Submission

After a package reaches `Submitted`, core submission artifacts should become read-only.

Protected artifacts should include:

* Final resume used
* Final cover letter used
* Final answers
* Submission result
* Confirmation page
* Confirmation number
* Submission screenshots
* Submitted timestamp

Corrections should be stored as later annotations rather than silently changing historical files.

---

# Package Version History

Generated artifacts may use versioned filenames.

Example:

```text
resume/tailored_resume_v1.pdf
resume/tailored_resume_v2.pdf
answers/prepared_answers_v1.json
answers/prepared_answers_v2.json
```

The package manifest should identify the active version.

---

# Application Package Builder

The Application Package Builder is responsible for:

* Creating package directories
* Generating the package ID
* Writing the manifest
* Saving input snapshots
* Creating subdirectories
* Updating package status
* Linking generated artifacts
* Validating file references
* Preserving schema version
* Managing package refreshes

---

# Package Builder Interface

Conceptual interface:

```text
ApplicationPackageService

    create_package(selected_job)
    load_package(package_id)
    update_package(package_id, changes)
    refresh_package(package_id)
    validate_package(package_id)
    archive_package(package_id)
    mark_submitted(package_id, submission_result)
```

---

# Package Builder Restrictions

The builder should not:

* Analyze jobs
* Tailor resumes
* Generate answers
* Control the browser
* Decide whether submission succeeded
* Modify original candidate files
* Create candidate facts

It coordinates and stores outputs produced by specialized services.

---

# Package Metadata

Recommended metadata fields:

```json
{
  "package_id": "",
  "schema_version": "1.0",
  "created_at": "",
  "updated_at": "",
  "created_by_application_version": "",
  "candidate_profile_id": "",
  "job_id": "",
  "company": "",
  "title": "",
  "status": "",
  "automation_mode": "",
  "expected_ats": "",
  "prompt_versions": {},
  "reasoning_models": {},
  "input_fingerprint": {},
  "warnings": [],
  "blocking_issues": []
}
```

---

# Application Readiness

A package may enter the queue only after readiness validation.

The package is Ready when:

* Job data is complete.
* Application URL is valid.
* Duplicate checks pass.
* Candidate context is available.
* Required candidate facts are resolved.
* A base resume is selected.
* The final resume exists.
* Resume validation passes.
* Required cover letter exists.
* Required supporting documents exist.
* Required standard answers are resolved.
* Candidate rules are satisfied.
* Application plan exists.
* File references are valid.
* No blocking issues remain.

---

# Package Readiness Report

Recommended file:

```text
readiness_report.json
```

Example:

```json
{
  "status": "ready",
  "checked_at": "",
  "blocking_issues": [],
  "warnings": [
    "The job description does not specify sponsorship availability."
  ],
  "checks": {
    "job_snapshot": "passed",
    "duplicate_check": "passed",
    "candidate_context": "passed",
    "resume_selected": "passed",
    "resume_generated": "passed",
    "resume_validation": "passed",
    "cover_letter": "not_required",
    "answers": "passed",
    "application_plan": "passed",
    "file_references": "passed"
  }
}
```

Detailed readiness rules are defined in `07D_Application_Review_And_Readiness.md`.

---

# Queue Admission

Only packages with status `Ready` may enter the application queue.

Queue admission should verify the package again at the time of admission.

This protects against:

* Deleted resume files
* Modified candidate rules
* Changed package status
* Duplicate submission after preparation
* Missing generated documents
* Stale packages

---

# Queue Admission Record

The package should store:

```json
{
  "queued_at": "",
  "queue_position": 1,
  "queue_strategy": "selected_order",
  "admission_check": "passed"
}
```

---

# Queue Ordering

Default ordering should preserve the order selected by the user.

Example:

```text
Apply to the first ten jobs.
```

The queue should preserve the visible ranking order of those ten jobs.

Alternative queue strategies may include:

* Highest match first
* Newest first
* Company priority
* Manual order
* Expiring job first

---

# Batch Package Creation

When the user selects multiple jobs:

```text
Selected Jobs
    |
    v
Create One Package Per Job
    |
    v
Prepare Independently
    |
    v
Validate Independently
    |
    v
Queue Only Ready Packages
```

A preparation failure for one job should not block all other jobs.

---

# Parallel Preparation

Independent Application Packages may be prepared concurrently.

Safe parallel tasks include:

* Job analysis
* Resume selection
* Resume-tailoring planning
* Answer generation
* Cover-letter generation
* Package validation

Concurrency should remain configurable to control:

* Claude API usage
* Local CPU use
* Memory
* File-generation load
* Provider rate limits

Browser execution should remain sequential by default.

---

# Partial Batch Results

After batch preparation, the system should summarize:

```text
Selected: 10
Ready: 7
Needs Attention: 2
Already Applied: 1
Failed: 0
```

The user should be able to inspect and resolve packages that are not Ready.

---

# Package Error Handling

Preparation errors should be stored inside the package.

Recommended file:

```text
execution/errors.json
```

For preparation-stage errors, the same file or a package-level error log may be used.

Example:

```json
{
  "errors": [
    {
      "stage": "resume_validation",
      "error_type": "unsupported_claim",
      "message": "The tailored resume introduced an unsupported Kafka claim.",
      "retryable": true,
      "requires_user_input": false,
      "created_at": ""
    }
  ]
}
```

---

# Preparation Error Categories

Possible categories:

* Job data missing
* Invalid application URL
* Duplicate application
* Candidate context unavailable
* Resume unavailable
* Resume selection failed
* Resume generation failed
* Resume validation failed
* Cover letter required but unavailable
* Answer unresolved
* Supporting document missing
* Provider error
* File-system error
* Package schema error
* Candidate-rule conflict

---

# Retry Behavior

Retry only the failed preparation stage when possible.

Example:

```text
Resume generation failed
    |
    v
Retry resume generation
```

Do not repeat:

* Job discovery
* Job analysis
* Candidate context loading

unless those inputs changed or were responsible for the failure.

---

# User Edits

The user may edit:

* Tailored resume
* Cover letter
* Narrative answers
* Application plan
* Queue priority
* Automation mode

The system should record user edits.

Recommended file:

```text
review/user_changes.json
```

Example:

```json
{
  "changes": [
    {
      "artifact": "answers/prepared_answers.json",
      "field": "why_company",
      "previous_value": "",
      "new_value": "",
      "changed_at": "",
      "changed_by": "user"
    }
  ]
}
```

---

# Preserving User Edits

Package refresh operations must not silently overwrite user-approved edits.

Before regeneration:

* Detect edited artifacts.
* Warn the user.
* Preserve the existing version.
* Generate a new candidate version.
* Allow the user to compare and select.

---

# Approval State

The package may store approval information.

Recommended file:

```text
review/approval.json
```

Example:

```json
{
  "resume_approved": true,
  "cover_letter_approved": true,
  "answers_approved": true,
  "final_application_approved": false,
  "approved_at": "",
  "approval_mode": "manual"
}
```

Automatic mode may set approval values according to configured rules after validation.

---

# Automation Mode

Each package should store its automation mode.

Supported values:

```text
automatic
review
manual
```

---

## Automatic

The package may proceed through form completion and submission without pausing when all validations pass.

---

## Review

The package may be filled automatically but must pause before final submission.

---

## Manual

The application prepares materials and may open the job page, but the user completes or submits the application manually.

---

# Package-Specific Overrides

The user should be able to override global settings for one package.

Examples:

* Use review mode for Google.
* Skip resume tailoring for one job.
* Use a specific resume.
* Generate a cover letter.
* Do not create an ATS account.
* Stop before voluntary demographic questions.
* Use a different Claude model for resume preparation.

Overrides should be stored in the package metadata.

---

# Supporting Documents

Some applications may request:

* Transcript
* Certifications
* Portfolio
* Writing sample
* Work sample
* Reference list
* Publication list
* Security-clearance proof

The package should explicitly list approved supporting documents.

Example:

```json
{
  "supporting_documents": [
    {
      "document_type": "transcript",
      "path": "candidate/documents/transcript.pdf",
      "approved_for_upload": true,
      "required": false
    }
  ]
}
```

The browser must upload only documents listed in the Application Plan.

---

# Document Copying vs Referencing

The system may either:

* Copy approved documents into the package
* Store a secure reference to the original file

For reliability and reproducibility, generated application files should usually be copied into the package.

Sensitive source documents may remain referenced if copying would create unnecessary duplication.

---

# File Hashing

Important package files should have hashes.

Examples:

* Job description
* Base resume
* Tailored resume
* Cover letter
* Candidate context
* Prepared answers

Hashes help detect:

* Accidental modification
* Stale packages
* Wrong file upload
* Corrupted files

---

# File Reference Validation

Before queue admission, verify:

* File exists
* File is readable
* File type is allowed
* File hash matches package metadata
* File path is within approved directories
* File is not empty
* Uploaded filename is appropriate

---

# Filename Sanitization

Generated filenames should:

* Avoid unsupported characters
* Avoid excessively long names
* Avoid exposing unnecessary personal information
* Include company or job identifier when useful
* Use stable extensions

Example:

```text
Suhas_Arudi_Google_Senior_Software_Engineer_Resume.pdf
```

A privacy-focused configuration may use:

```text
Resume_Google_123456.pdf
```

---

# Package Logging

Every package should have isolated logs.

Recommended directory:

```text
logs/
```

Logs may include:

* Preparation events
* Resume selection
* Claude requests metadata
* Validation results
* Queue admission
* Browser execution
* Submission verification

Logs should not include full sensitive values by default.

---

# Package Screenshots

All screenshots related to one application should remain inside its package.

Examples:

* Application opened
* Login required
* Validation error
* Before submission
* After submission
* Submission unknown
* Confirmation page

---

# Confirmation Evidence

After successful submission, store:

```text
submission/result.json
submission/confirmation.txt
submission/confirmation_page.html
submission/confirmation_metadata.json
screenshots/{confirmation_screenshot}.png
```

The confirmation metadata may include:

* Confirmation number
* Submitted timestamp
* Confirmation URL
* ATS application ID
* Success indicators
* Verification confidence

---

# Tracker Synchronization

After verified submission:

1. Mark the package Submitted.
2. Save submission evidence.
3. Append the application to the local tracker.
4. Store the tracker row identifier if available.
5. Confirm the tracker write succeeded.

The package and tracker should not disagree silently.

---

# Tracker Failure After Submission

If submission succeeds but tracker recording fails:

* Keep the package status Submitted.
* Store the tracker error.
* Retry tracker synchronization.
* Warn the user.
* Do not resubmit the application.

---

# Package Archiving

The user should be able to archive packages.

Possible archive categories:

* Submitted
* Rejected
* Withdrawn
* Skipped
* Expired
* Failed
* Test

Archiving should not delete evidence by default.

---

# Package Deletion

Deleting a package should require confirmation when the package contains:

* Submitted application evidence
* User-approved documents
* Confirmation numbers
* Review history

The user should be able to configure retention policies.

---

# Data Retention

Possible retention settings:

```json
{
  "retention": {
    "failed_packages_days": 30,
    "screenshots_days": 90,
    "submitted_packages": "keep",
    "logs_days": 30
  }
}
```

Retention should be local and user-controlled.

---

# Privacy Rules

Application Packages may contain sensitive information.

Therefore:

* Store packages locally.
* Exclude package directories from source control.
* Restrict permissions where supported.
* Do not upload entire packages to Claude.
* Send only task-relevant context.
* Do not include browser cookies or credentials.
* Do not store plaintext passwords.
* Allow users to delete packages.
* Do not expose packages through a public web server.

---

# Package Encryption

Encryption at rest may be optional for the MVP.

Future versions may support:

* Operating-system encrypted storage
* Encrypted package archives
* User-managed encryption keys
* Secure secret storage

The architecture should not prevent later encryption support.

---

# Package Test Fixtures

The repository should include sanitized test packages.

Examples:

```text
tests/sample_data/application_packages/
    ready_package/
    needs_attention_package/
    submitted_package/
    stale_package/
    invalid_resume_package/
    unresolved_answer_package/
```

Fixtures must not contain real candidate data.

---

# Unit Tests

Unit-test:

* Package ID generation
* Directory creation
* Manifest writing
* Schema validation
* File reference validation
* Input fingerprint generation
* Staleness detection
* Status transitions
* Queue admission
* Duplicate package detection
* User-edit preservation
* Submission immutability

---

# Integration Tests

Integration-test:

* Selected job to Ready package
* Batch package creation
* Resume-selection integration
* Resume-generation integration
* Answer-generation integration
* Readiness validation
* Package refresh
* Failed package retry
* Package-to-browser handoff
* Submission-result persistence
* Tracker synchronization

---

# Package State-Transition Rules

Allowed transitions should be explicit.

Example:

```text
Created -> Collecting Context
Collecting Context -> Selecting Resume
Selecting Resume -> Generating Materials
Generating Materials -> Validating
Validating -> Ready
Validating -> Needs Attention
Ready -> Queued
Queued -> Executing
Executing -> Waiting for User
Executing -> Ready for Review
Executing -> Submitting
Submitting -> Submitted
Submitting -> Submission Unknown
Executing -> Failed
Needs Attention -> Validating
Failed -> Validating
```

Invalid transitions should be rejected.

Example:

```text
Created -> Submitted
```

This should not be permitted.

---

# Package Locking

While a package is Executing or Submitting:

* Prevent conflicting preparation updates.
* Prevent simultaneous browser execution.
* Prevent deletion.
* Prevent queue duplication.

A lightweight local lock file may be used.

Example:

```text
.package.lock
```

Stale locks should be detected and recoverable.

---

# Crash Recovery

If the application crashes:

1. Reload package manifests.
2. Detect packages in transient states.
3. Inspect lock files.
4. Reconcile browser execution state.
5. Mark uncertain packages for recovery.
6. Avoid automatic resubmission.
7. Preserve all existing artifacts.

Packages left in `Submitting` should usually become `Submission Unknown` until verified.

---

# Package Summary for the User Interface

The frontend should display a concise package summary.

Example:

```text
Company: Google
Role: Senior Software Engineer
Match Score: 91
Resume: Backend_Google.pdf
Cover Letter: Not Required
Answers Prepared: 18
Unresolved Questions: 0
Status: Ready
Automation Mode: Review
```

---

# Package Detail View

The user should be able to inspect:

* Job details
* Match analysis
* Resume used
* Resume changes
* Cover letter
* Prepared answers
* Unresolved questions
* Application plan
* Readiness report
* Browser progress
* Screenshots
* Submission evidence
* Errors

---

# Definition of Application Package Completion

The Application Package system is complete when:

* Every selected job receives a unique package.
* Package directories are created consistently.
* Job and candidate snapshots are preserved.
* Resume references are stored.
* Generated documents are linked correctly.
* Prepared answers are stored with sources and confidence.
* Application plans are created.
* Package states are explicit and validated.
* Packages can be refreshed without losing user edits.
* Stale packages are detected.
* Only Ready packages enter the queue.
* Batch preparation isolates failures.
* Browser execution can resume from package state.
* Submission evidence is stored.
* Submitted packages become historically stable.
* Tracker synchronization works.
* Sensitive package content remains local.
* Sanitized test fixtures cover major package states.

---

# Summary

An Application Package is the central job-specific unit of work for the application.

It preserves:

* What job was selected
* What candidate facts were used
* Which resume was chosen
* How the resume was tailored
* Which answers were prepared
* What the browser should execute
* What happened during execution
* Whether submission succeeded

By preparing and validating one complete package per job before browser execution, the system avoids repeated reasoning, wrong-file uploads, lost state, inconsistent answers, and unrecoverable browser failures.

Application Packages make the platform reliable, resumable, auditable, and suitable for controlled batch job applications.
