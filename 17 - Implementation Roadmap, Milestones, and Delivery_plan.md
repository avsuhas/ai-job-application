# 17 - Implementation Roadmap, Milestones, and Delivery Plan

## LLM-Powered Autonomous Job Search & Application Platform

Version: 1.0

---

# Purpose

This document defines the implementation roadmap, milestone structure, delivery sequence, dependency model, release gates, risk controls, and completion criteria for the LLM-Powered Autonomous Job Search and Application Platform.

The platform includes:

* Candidate Knowledge Base ingestion.
* Job discovery and normalization.
* Job ranking and selection.
* Application Package creation.
* Resume tailoring.
* Cover-letter generation.
* Application-answer preparation.
* Application Review.
* Application Readiness.
* Queue and workflow orchestration.
* Browser automation.
* ATS adapters.
* Generic form handling.
* Submission verification.
* Application history.
* Logging and audit trails.
* Security and privacy.
* Testing and quality assurance.
* Local deployment and operations.
* User interface.
* Versioned API contracts and schemas.

The platform should not be implemented as one large end-to-end automation script.

It should be delivered incrementally through independently testable milestones, with automatic submission remaining disabled until all safety-critical dependencies have passed their release gates.

---

# Core Principle

Build the platform in increasing levels of consequence.

```text
Local Read-Only Analysis
        |
        v
Local Artifact Preparation
        |
        v
Controlled Form Understanding
        |
        v
Browser Form Completion
        |
        v
Human-Reviewed Submission
        |
        v
Verified Automatic Submission
```

The system should prove correctness at each level before advancing to the next.

---

# Delivery Objectives

The roadmap should:

* Produce usable value early.
* Keep candidate data local.
* Establish canonical schemas before broad integration.
* Build deterministic services before probabilistic services.
* Build review and readiness before automatic execution.
* Build submission verification before automatic submission.
* Use synthetic data and local forms before live ATS workflows.
* Support rollback and recovery from the beginning.
* Prevent irreversible actions from appearing before their safeguards.
* Keep the MVP narrow enough to complete reliably.
* Make every phase independently testable.
* Document deferred capabilities explicitly.
* Allow partial production use in Manual and Review modes before Automatic mode.

---

# Delivery Philosophy

The project should follow these implementation principles.

---

## Safety Before Throughput

A lower application volume with reliable factual and submission integrity is preferable to broad unreliable automation.

---

## Vertical Slices with Strong Foundations

The project should establish shared foundations, then deliver end-to-end vertical slices.

Example:

```text
One Candidate
One Synthetic Job
One Application Package
One Controlled Form
One Verified Simulated Submission
One History Record
```

This is more valuable than building many disconnected components.

---

## Deterministic First

Implement deterministic functionality before reasoning-provider dependence.

Examples:

* File validation.
* Date calculations.
* Exact candidate answers.
* Duplicate checks.
* State transitions.
* Readiness rules.
* File selection.
* Submission-attempt durability.

---

## Local Fixtures Before Live Websites

Browser and ATS development should begin with controlled local fixtures.

Live ATS validation should be limited and should not be required for routine development.

---

## Manual Before Automatic

The progression should be:

```text
Preparation Only
Manual Completion
Review Mode
Limited Automatic Mode
General Automatic Mode for Stable Adapters
```

---

## Evidence-Based Completion

A milestone is complete only when:

* Its acceptance criteria pass.
* Required tests pass.
* Security and privacy checks pass.
* Documentation exists.
* Known limitations are recorded.
* Recovery behavior is tested.

---

# Roadmap Overview

Recommended implementation phases:

```text
Phase 0  - Project Foundations
Phase 1  - Candidate Data and Core Schemas
Phase 2  - Job Intake, Normalization, and Ranking
Phase 3  - Application Package Preparation
Phase 4  - Review, Readiness, and Manual Handoff
Phase 5  - Browser Automation Foundation
Phase 6  - Generic Form Engine
Phase 7  - First Dedicated ATS Adapter
Phase 8  - Queue and Execution Orchestration
Phase 9  - Submission Verification and History
Phase 10 - Review Mode End-to-End Release
Phase 11 - Security, Operations, and UX Hardening
Phase 12 - Limited Automatic Submission
Phase 13 - ATS Expansion and Advanced Capabilities
```

---

# Recommended Release Stages

```text
Internal Prototype
Developer Alpha
Local Alpha
Review-Mode Beta
Stable Review Release
Limited Automatic Beta
Stable Automatic Release
```

---

# Release Definitions

## Internal Prototype

Used only by developers with synthetic data.

No real candidate data or submissions.

---

## Developer Alpha

Core services and local browser fixtures operate.

Real candidate data may be tested only in read-only or preparation workflows.

---

## Local Alpha

A user can prepare Application Packages and manually complete applications.

Automatic browser submission remains disabled.

---

## Review-Mode Beta

The browser can complete supported forms and pause before final submission.

User approval is mandatory.

---

## Stable Review Release

Review-mode workflows are reliable for supported ATS adapters and controlled generic forms.

Submission verification and history are stable.

---

## Limited Automatic Beta

Automatic submission is enabled only for:

* Explicitly supported ATS adapters.
* Stable workflow variants.
* Packages with no warnings.
* Candidate-approved policies.
* Verified duplicate checks.
* Verified submission evidence.

---

## Stable Automatic Release

Automatic mode is available for adapters and workflows that consistently pass all quality gates.

Unsupported and degraded workflows remain in Review or Manual mode.

---

# MVP Definition

The recommended MVP should include:

* One active candidate profile.
* Local Candidate Knowledge Base.
* Direct job URL intake.
* Basic company career-page intake.
* Job normalization.
* Job scoring and recommendation.
* Application Package creation.
* One or more base resumes.
* Resume tailoring with factual validation.
* Optional cover-letter generation.
* Standard application-answer library.
* Work-authorization handling.
* Application Review.
* Application Readiness.
* Manual-completion package.
* Local CSV application history.
* Local XLSX application history.
* Structured logs.
* Local web interface.
* Controlled browser test forms.
* Generic form completion in Review mode.
* One Stable ATS adapter.
* Submission verification.
* Submission Unknown protection.
* Browser crash recovery.
* Local backups and health checks.

---

# MVP Exclusions

The MVP should not require:

* Multi-user hosting.
* Cloud database.
* Kubernetes.
* Mobile application.
* Fully autonomous application to every ATS.
* Automated CAPTCHA.
* Automated MFA.
* Automated coding assessments.
* Automated video interviews.
* Automated background checks.
* Government-ID automation.
* Bank or payment information.
* Unlimited browser concurrency.
* All ATS adapters.
* Email inbox automation.
* Calendar automation.
* Recruiter-outreach automation.
* External telemetry.
* Automatic software updates.
* Complex analytics warehouse.

---

# Critical Dependency Chain

The most important dependency chain is:

```text
Candidate Data
    |
    v
Application Package
    |
    v
Answer and Document Preparation
    |
    v
Review
    |
    v
Readiness
    |
    v
Browser Execution
    |
    v
Submission Verification
    |
    v
History
```

Automatic submission must not be implemented as an isolated browser feature.

---

# Phase 0 - Project Foundations

## Goal

Establish the repository, development environment, code-quality controls, local data conventions, and basic architecture.

---

# Phase 0 Deliverables

* Project repository.
* Python project configuration.
* Locked dependency management.
* Local development environment.
* Base module structure.
* Configuration loader.
* Local data-root resolver.
* Structured logger bootstrap.
* Error-code conventions.
* Basic schema registry.
* Test framework.
* CI pipeline.
* Secret-scanning configuration.
* Source-control exclusions.
* Developer documentation.
* Synthetic candidate and job fixtures.

---

# Suggested Project Structure

```text
src/
    candidate/
    jobs/
    packages/
    documents/
    answers/
    review/
    readiness/
    browser/
    ats/
    orchestration/
    submission/
    history/
    security/
    observability/
    api/
    ui/
    operations/

schemas/
tests/
fixtures/
prompts/
migrations/
docs/
```

The exact structure may vary, but domain boundaries should remain clear.

---

# Phase 0 Work Items

## Repository and Tooling

* Initialize repository.
* Configure formatting.
* Configure linting.
* Configure type checking.
* Configure unit testing.
* Configure test coverage.
* Configure secret scanning.
* Add standard `.gitignore`.
* Add contributor documentation.

## Runtime

* Select supported Python version.
* Configure virtual environment.
* Lock dependencies.
* Add environment validation.
* Add version reporting.

## Core Utilities

* ID generation.
* time service.
* hash utility.
* atomic file writes.
* JSON serialization.
* structured errors.
* temporary-directory management.
* path validation.

## Testing

* Synthetic data root.
* deterministic clock.
* test configuration.
* test secret store.
* fixture loader.
* test-result directory.

---

# Phase 0 Acceptance Criteria

* Fresh developer installation succeeds.
* Unit-test framework runs.
* CI runs automatically.
* No real candidate data is present.
* Secrets scan passes.
* Configuration schema validates.
* Atomic file writes are tested.
* Application version is available.
* Basic health command runs.
* Synthetic fixtures load successfully.

---

# Phase 0 Exit Gate

```text
Foundation Gate
```

Required:

* Development environment reproducible.
* Critical utilities tested.
* Security exclusions active.
* Schema registry can load one example schema.
* Test fixtures contain no real personal data.

---

# Phase 1 - Candidate Data and Core Schemas

## Goal

Create the trusted local representation of candidate information and the core canonical domain models.

---

# Phase 1 Deliverables

* Candidate Profile schema.
* Employment schema.
* Education schema.
* Skills schema.
* Work Authorization schema.
* Preferences schema.
* Standard Answers schema.
* Sensitive-field policy schema.
* Candidate source-reference model.
* Candidate parser interfaces.
* Candidate conflict detection.
* Candidate validation service.
* Candidate profile storage.
* Candidate profile API.
* Candidate profile UI.
* Source-file import.
* Candidate snapshot generation.

---

# Candidate Source Support

Initial support:

* JSON.
* Markdown.
* plain text.
* PDF resume.
* DOCX resume.

Structured JSON should be the highest-confidence source when available.

---

# Phase 1 Work Items

## Schemas

Implement:

* `CandidateProfile@1.0`.
* `EmploymentRecord@1.0`.
* `EducationRecord@1.0`.
* `Skill@1.0`.
* `WorkAuthorization@1.0`.
* `CandidatePreferences@1.0`.
* `StandardAnswerLibrary@1.0`.

## Candidate Storage

* Local candidate directory.
* atomic updates.
* file hashes.
* source references.
* entity versions.
* backup before mutation.

## Parsing

* Resume text extraction.
* employment extraction.
* education extraction.
* skill extraction.
* parsing confidence.
* user review.

## Validation

* Date consistency.
* current-role consistency.
* duplicate employment.
* contradictory work authorization.
* missing legal name.
* malformed contact information.
* source conflicts.

## User Interface

* Candidate overview.
* employment editor.
* education editor.
* work-authorization editor.
* preferences editor.
* source conflict resolution.

---

# Phase 1 Critical Test Cases

* Conflicting current title.
* missing future sponsorship answer.
* duplicate employment record.
* malformed date.
* unsupported file.
* candidate file hash change.
* source update invalidates snapshot.
* demographic information excluded from provider-ready context.
* government ID hidden.

---

# Phase 1 Acceptance Criteria

* Synthetic candidate can be imported.
* Extracted facts can be reviewed.
* Candidate conflicts are surfaced.
* Candidate profile can be updated with version checks.
* Candidate snapshot is reproducible.
* Work-authorization fields remain separate.
* Sensitive values are masked.
* Candidate data stays inside the approved local root.
* Candidate schema migration test passes.

---

# Phase 1 Exit Gate

```text
Candidate Data Gate
```

Required:

* Candidate profile is trustworthy enough to support downstream artifact preparation.
* No downstream service needs to read arbitrary candidate files directly.
* Candidate facts have source references.
* Sensitive data policies are active.

---

# Phase 2 - Job Intake, Normalization, and Ranking

## Goal

Accept job opportunities, normalize them, analyze requirements, and rank them against the candidate profile.

---

# Phase 2 Deliverables

* Job schema.
* Job Source schema.
* Job Analysis schema.
* Job Match schema.
* Direct URL intake.
* Manual job import.
* Company career-page source configuration.
* Job-content hashing.
* Job identity extraction.
* Date-posted extraction.
* Location and country normalization.
* Salary parsing.
* Requirement analysis.
* Match scoring.
* Hard-rule evaluation.
* Duplicate job detection.
* Jobs UI.

---

# Phase 2 Implementation Order

1. Manual structured job fixture.
2. Direct job URL.
3. Static company page.
4. ATS-hosted job page.
5. Multi-job discovery source.

---

# Phase 2 Work Items

## Job Intake

* URL validation.
* domain classification.
* page download or browser retrieval.
* job identity extraction.
* application URL extraction.
* source snapshot.

## Normalization

* Company.
* title.
* location.
* country.
* remote status.
* employment type.
* salary.
* date posted.
* job ID.
* requisition ID.

## Analysis

* Required skills.
* preferred skills.
* responsibilities.
* experience requirements.
* sponsorship language.
* application-document requirements.
* clearance requirements.

## Ranking

* Skills.
* experience.
* title.
* location.
* salary.
* work authorization.
* sponsorship.
* posting recency.
* user exclusions.

---

# Phase 2 Scoring Strategy

Start with deterministic weighted rules.

Reasoning-provider output may assist requirement extraction but should not directly produce the final score without deterministic validation.

---

# Phase 2 User Experience

The user should be able to:

* Add a direct job URL.
* see normalized job identity.
* inspect extracted requirements.
* see match score.
* see strengths and gaps.
* see rule failures.
* select or skip the job.

---

# Phase 2 Acceptance Criteria

* Synthetic job fixtures normalize correctly.
* Unknown dates remain unknown.
* Country filter works.
* Salary parsing distinguishes base and total compensation.
* Sponsorship language is detected and surfaced.
* Match score is explainable.
* Duplicate job IDs are detected.
* Job content changes produce new hashes.
* Job selection creates an auditable event.

---

# Phase 2 Exit Gate

```text
Job Analysis Gate
```

Required:

* The user can reliably determine which jobs are worth preparing.
* Job identity is strong enough to prevent wrong-role package creation.
* Ranking explanations match scoring components.

---

# Phase 3 - Application Package Preparation

## Goal

Create a self-contained, versioned Application Package containing all materials required to apply.

---

# Phase 3 Deliverables

* Application Package schema.
* Package manifest.
* Package directory structure.
* Job snapshot.
* Candidate-context snapshot.
* Application Plan.
* Base resume selection.
* Resume-tailoring plan.
* Tailored resume generation.
* Resume validation.
* Cover-letter requirement detection.
* Cover-letter generation.
* Application-answer preparation.
* Artifact versioning.
* Package fingerprints.
* Package UI.

---

# Package Directory Structure

```text
applications/packages/{package_id}/
    manifest.json
    job/
    candidate/
    resume/
    cover_letter/
    answers/
    review/
    readiness/
    execution/
    submission/
    logs/
```

---

# Phase 3 Implementation Order

1. Package manifest.
2. Job and candidate snapshots.
3. Active base resume selection.
4. Resume-tailoring plan.
5. Resume output.
6. Resume factual validation.
7. Cover-letter preparation.
8. Standard answer set.
9. Package fingerprint.
10. Package UI.

---

# Resume Tailoring MVP

The first version should prioritize:

* Summary changes.
* Skill ordering.
* Bullet selection.
* Bullet rephrasing.
* Removal of irrelevant content.
* ATS-readable formatting.

It should not attempt complex visual redesign.

---

# Resume Validation Requirements

* Candidate name correct.
* employers unchanged.
* titles supported.
* dates unchanged.
* skills supported.
* metrics supported.
* no wrong company.
* no unsupported certification.
* PDF readable.
* DOCX valid.
* page count acceptable.

---

# Cover Letter MVP

Cover letters should be:

* Optional by policy.
* Generated only when required or useful.
* Concise.
* Job-specific.
* Factually validated.
* Free of invented referrals.
* Free of wrong-company references.

---

# Application Answer MVP

Support:

* Personal information.
* employment.
* education.
* work authorization.
* sponsorship.
* relocation.
* travel.
* notice period.
* start date.
* salary.
* standard demographic preferences.
* standard legal answers.
* simple narrative answers.

---

# Phase 3 Acceptance Criteria

* Package can be created from one job.
* Package contains immutable snapshots.
* Tailored resume is factually valid.
* Cover-letter company and role are correct.
* Required standard answers are resolved.
* Missing or ambiguous answers are explicit.
* Every artifact has a version and hash.
* Package can be reopened without regeneration.
* Package staleness can be detected.

---

# Phase 3 Exit Gate

```text
Preparation Gate
```

Required:

* A user can prepare complete materials for manual application.
* No browser automation is required.
* Package contents are reviewable and exportable.

---

# Phase 4 - Review, Readiness, and Manual Handoff

## Goal

Make prepared Application Packages safe and usable before introducing browser execution.

---

# Phase 4 Deliverables

* Application Review service.
* Review finding model.
* Cross-artifact consistency checks.
* Safe automatic corrections.
* Application Readiness service.
* Preparation readiness.
* Manual completion readiness.
* User-action requests.
* Manual-completion checklist.
* Application review UI.
* Readiness UI.
* Manual application history recording.

---

# Review Checks

* Correct company.
* correct role.
* correct job ID.
* correct resume.
* correct cover letter.
* unsupported claims.
* work-authorization consistency.
* salary-policy consistency.
* legal-answer completeness.
* demographic-policy compliance.
* document requirement compliance.
* package integrity.

---

# Readiness Checks

* Required artifacts exist.
* hashes match.
* candidate snapshot valid.
* active document versions valid.
* required answers resolved.
* review completed.
* duplicate check current.
* manual handoff files available.

---

# Manual Completion Package

The user should receive:

* Application URL.
* Tailored resume.
* cover letter.
* expected answers.
* sensitive-answer checklist.
* missing-answer list.
* upload checklist.
* completion checklist.

---

# Phase 4 Acceptance Criteria

* Blocking findings stop readiness.
* Warnings are distinct from blockers.
* Safe corrections are bounded.
* Legal unknowns are not guessed.
* Work-authorization contradictions are detected.
* User can edit an answer.
* User can save answer only for this application or for reuse.
* Manual-completion package is usable.
* User can manually mark an application submitted.
* Manual submission source is recorded accurately.

---

# Phase 4 Release

```text
Local Alpha
```

At this point, the platform provides significant value without browser automation.

---

# Phase 4 Exit Gate

```text
Manual Application Gate
```

Required:

* A user can discover, rank, prepare, review, and manually complete applications.
* CSV and XLSX history can record manual applications.
* Sensitive-data and audit rules pass.

---

# Phase 5 - Browser Automation Foundation

## Goal

Implement safe low-level browser control against synthetic local forms.

---

# Phase 5 Deliverables

* Playwright browser service.
* Dedicated browser profile manager.
* Browser session model.
* Browser health check.
* Page snapshot model.
* Form extraction primitives.
* Browser action primitives.
* Action verification.
* File upload.
* Screenshot capture.
* Navigation policy.
* CAPTCHA detection.
* Login detection.
* MFA detection.
* Browser crash recovery.
* Local synthetic application server.

---

# Browser Action Primitives

Implement:

* Navigate.
* inspect page.
* locate field.
* enter text.
* select option.
* click checkbox.
* select radio.
* upload file.
* click Next.
* verify value.
* capture screenshot.
* wait for page stability.

---

# Browser Safety Requirements

* Visible browser by default.
* Dedicated profile.
* one workflow per profile.
* no arbitrary navigation.
* no arbitrary file path.
* no automatic CAPTCHA solving.
* no automatic MFA.
* no final Submit support yet.
* all actions verified.

---

# Local Browser Fixture Suite

Create controlled pages for:

* One-page form.
* Multi-page form.
* resume upload.
* searchable dropdown.
* radio questions.
* conditional fields.
* repeated work history.
* validation errors.
* login.
* CAPTCHA.
* MFA.
* review page.
* simulated submit page.
* confirmation page.

---

# Phase 5 Acceptance Criteria

* Browser launches reliably.
* Dedicated profile works.
* Local forms can be completed.
* Every field action is verified.
* File upload verifies filename.
* conditional fields are detected.
* page progression is verified.
* browser crash before final submission recovers.
* CAPTCHA pauses.
* MFA pauses.
* untrusted navigation is blocked.
* logs do not expose values.

---

# Phase 5 Exit Gate

```text
Browser Foundation Gate
```

Required:

* Controlled local browser workflows are reliable.
* Browser actions cannot bypass package and security policies.
* Final submission remains unavailable.

---

# Phase 6 - Generic Form Engine

## Goal

Translate accessible unknown application forms into canonical form models and execute them safely in Review mode.

---

# Phase 6 Deliverables

* Form boundary detection.
* label resolution.
* field-type classification.
* semantic-field classification.
* widget-handler registry.
* Generic Form Engine.
* dynamic field detection.
* validation-message extraction.
* repeated-section support.
* review-page detection.
* ambiguous-final-action protection.
* generic-form diagnostics.

---

# Generic Engine MVP Capabilities

* Text.
* email.
* phone.
* URL.
* textarea.
* native dropdown.
* searchable dropdown.
* radio.
* checkbox.
* date.
* file upload.
* conditional fields.
* multi-page forms.

Advanced controls may remain Manual Only.

---

# Generic Engine Confidence Rules

* High-confidence fields may be completed automatically.
* Medium-confidence fields require Review mode.
* Low-confidence required fields require user input.
* Ambiguous final controls must not be clicked automatically.

---

# Phase 6 Acceptance Criteria

* Application form is distinguished from search or newsletter forms.
* Labels are resolved through accessibility metadata.
* known standard questions map correctly.
* ambiguous questions are surfaced.
* validation errors map to fields.
* dynamic fields are re-inspected.
* review page is captured.
* final Submit remains user-approved and simulated.
* unsupported widgets fall back to Manual mode.

---

# Phase 6 Exit Gate

```text
Generic Form Gate
```

Required:

* Standard accessible forms can be filled safely.
* Review-mode completion works on local fixtures.
* Generic engine never guesses final submission.

---

# Phase 7 - First Dedicated ATS Adapter

## Goal

Implement one deeply supported ATS adapter with reliable end-to-end form completion.

---

# ATS Selection Criteria

Choose an ATS that:

* Appears frequently in target jobs.
* Has accessible forms.
* supports stable test fixtures.
* has manageable authentication requirements.
* provides identifiable submission confirmation.
* can deliver useful MVP coverage.

Potential first targets:

```text
Greenhouse
Lever
Ashby
```

A complex Workday adapter may follow after the framework is proven.

---

# Phase 7 Deliverables

* ATS detection rules.
* adapter metadata.
* capability declarations.
* page signatures.
* page classification.
* form extraction.
* ATS-specific widget handlers.
* resume upload.
* custom questions.
* review extraction.
* submission-control detection.
* simulated confirmation.
* limited live non-submission validation.
* regression fixtures.
* adapter-health metrics.

---

# Adapter Stability Progression

```text
Experimental
    |
    v
Beta
    |
    v
Stable
```

Automatic mode remains disabled during Experimental and Beta.

---

# Phase 7 Acceptance Criteria

* ATS detected reliably.
* correct job identity maintained.
* supported employer variants pass.
* resume upload works.
* custom questions work.
* review page is extracted.
* session and redirect handling work.
* generic localized fallback works.
* adapter regression suite passes.
* simulated submission verification passes.
* live inspection does not require real submission.

---

# Phase 7 Exit Gate

```text
First ATS Gate
```

Required:

* One ATS adapter reaches Beta or Stable Review mode.
* Generic fallback is available.
* Unsupported variants fail safely.

---

# Phase 8 - Queue and Execution Orchestration

## Goal

Coordinate multiple packages through durable sequential browser workflows.

---

# Phase 8 Deliverables

* Queue Manager.
* queue admission.
* stable ordering.
* workflow state machine.
* stage executor.
* package locks.
* profile locks.
* checkpoints.
* retries.
* user interventions.
* pause and resume.
* queue cancellation.
* package cancellation.
* recovery after restart.
* event stream.
* queue UI.

---

# Implementation Order

1. One package workflow.
2. Durable stage state.
3. checkpoint after page.
4. pause and resume.
5. browser crash recovery.
6. queue with two packages.
7. package failure isolation.
8. user intervention.
9. queue completion summary.
10. restart recovery.

---

# Queue MVP Policy

```text
One active browser profile
One executing application
Sequential queue
Pause on user action
Pause on Submission Unknown
Continue after ordinary package failure
```

---

# Phase 8 Acceptance Criteria

* Ready packages are admitted.
* unready packages are rejected.
* duplicate package execution is blocked.
* package locks work.
* browser profile lock works.
* queue order is stable.
* state persists after every stage.
* browser crash resumes safely.
* current package can be cancelled.
* remaining queue can continue after safe failures.
* active final action cannot be cancelled ambiguously.
* events update the UI.

---

# Phase 8 Exit Gate

```text
Orchestration Gate
```

Required:

* Multiple synthetic applications can execute sequentially.
* Recovery does not duplicate completed actions.
* No final submission support is enabled without Phase 9.

---

# Phase 9 - Submission Verification and Application History

## Goal

Implement the irreversible-action boundary, strong submission verification, duplicate protection, and durable application history.

---

# Phase 9 Deliverables

* Pre-submission snapshot.
* submission lock.
* submission-attempt model.
* one-click-only enforcement.
* verification state.
* evidence model.
* confirmation extraction.
* confirmation-number extraction.
* dashboard reconciliation interface.
* Submission Unknown.
* unknown-outcome resolution.
* CSV history.
* XLSX history.
* append-only history events.
* idempotent synchronization.
* duplicate application detector.
* history UI.

---

# Implementation Order

1. Simulated final-click event.
2. durable attempt creation.
3. confirmation-page verification.
4. weak-confirmation handling.
5. Submission Unknown.
6. browser crash after click.
7. CSV synchronization.
8. XLSX synchronization.
9. duplicate detection.
10. history reconciliation.

---

# Submission Safety Requirements

* Attempt record written before click.
* final click no more than once.
* no automatic click retry.
* strong evidence required for Submitted.
* weak evidence becomes Unknown.
* tracker failure cannot trigger resubmission.
* duplicate check runs immediately before submission.

---

# Phase 9 Acceptance Criteria

* Explicit confirmation verifies submission.
* confirmation number is captured.
* weak redirect becomes Submission Unknown.
* browser crash after click never retries.
* unknown state survives restart.
* user can resolve unknown state.
* CSV and XLSX update idempotently.
* corrupt XLSX can be rebuilt.
* existing application blocks duplicate submission.
* submission and recruitment statuses remain separate.

---

# Phase 9 Exit Gate

```text
Submission Safety Gate
```

Required:

* Submission truth is durable.
* Unknown outcomes are protected.
* History remains accurate during partial failures.
* Final-click idempotency tests pass with zero failures.

---

# Phase 10 - Review Mode End-to-End Release

## Goal

Deliver the first complete real-user workflow with mandatory user review before final submission.

---

# Phase 10 Deliverables

* Full onboarding.
* job intake.
* package preparation.
* review.
* readiness.
* browser execution.
* ATS adapter.
* generic form fallback.
* manual intervention.
* user approval.
* final submission.
* submission verification.
* history.
* recovery.
* backups.
* stable local UI.

---

# Review-Mode Workflow

```text
Add Job
    |
    v
Prepare Package
    |
    v
Review Readiness
    |
    v
Queue Application
    |
    v
Complete Browser Form
    |
    v
Automated Review
    |
    v
User Approval
    |
    v
Submit
    |
    v
Verify
    |
    v
Update History
```

---

# Phase 10 Supported Workflow Policy

Review mode may be enabled for:

* Stable ATS adapter workflows.
* Beta adapters with additional warnings.
* accessible generic forms with strong final-action identification.

Manual mode should remain available for every workflow.

---

# Phase 10 Acceptance Criteria

* End-to-end synthetic workflow passes repeatedly.
* Limited real application workflow can pause before submission.
* User sees exact artifact versions.
* user approval is bound to form snapshot.
* submission verification works.
* application appears in history.
* restart recovery works.
* audit trail passes integrity checks.
* data remains local.
* backup succeeds.

---

# Phase 10 Release

```text
Review-Mode Beta
```

---

# Phase 10 Exit Gate

```text
Review Release Gate
```

Required:

* No unresolved Critical defects.
* no unresolved High submission-safety defects.
* no sensitive-data leaks.
* no duplicate final clicks.
* no wrong-company artifact leakage.
* accessibility of critical workflow validated.

---

# Phase 11 - Security, Operations, and UX Hardening

## Goal

Harden the platform for sustained local use.

---

# Phase 11 Deliverables

* OS credential-store integration.
* provider context filter.
* prompt-injection detection.
* upload manifest enforcement.
* unexpected-domain protection.
* local API CSRF protection.
* Content Security Policy.
* sensitive-value reveal controls.
* log redaction.
* audit hash chains.
* backup and restore.
* Safe mode.
* Maintenance mode.
* migrations.
* health dashboard.
* disk monitoring.
* diagnostic bundles.
* accessibility improvements.
* performance improvements.

---

# Security Hardening Work Items

* Threat-model review.
* path traversal testing.
* file-signature validation.
* malicious-document fixtures.
* provider secret scanning.
* browser profile isolation.
* wrong-account detection.
* payment-request blocking.
* government-ID policy enforcement.
* diagnostic-bundle sanitization.

---

# Operations Hardening Work Items

* Fresh install test.
* upgrade test.
* rollback test.
* migration test.
* backup verification.
* restore staging.
* corrupt-history recovery.
* stale-lock repair.
* low-disk behavior.
* browser-profile replacement.

---

# UX Hardening Work Items

* Onboarding usability.
* queue clarity.
* Submission Unknown prominence.
* keyboard navigation.
* screen-reader announcements.
* status terminology.
* error-message quality.
* responsive layouts.
* large-history performance.

---

# Phase 11 Acceptance Criteria

* Security test suite passes.
* privacy test suite passes.
* backup restores successfully.
* failed migration rolls back.
* low disk blocks unsafe submission.
* audit tampering is detected.
* local UI remains localhost-only.
* diagnostic bundle contains no secrets.
* critical workflows are keyboard accessible.
* system health identifies degraded components.

---

# Phase 11 Exit Gate

```text
Operational Hardening Gate
```

Required:

* Stable Review release can be maintained, upgraded, backed up, and recovered safely.
* Security and privacy controls are active by default.

---

# Phase 12 - Limited Automatic Submission

## Goal

Enable automatic submission only for narrowly approved workflows.

---

# Automatic Mode Preconditions

Automatic submission should remain disabled unless:

* ATS adapter status is Stable.
* workflow variant is supported.
* package has no blocking findings.
* warning policy permits execution.
* candidate data is current.
* all required answers have exact sources.
* sensitive-field policy permits execution.
* duplicate check is current.
* browser identity is verified.
* job identity is verified.
* submission readiness is Ready.
* final control confidence exceeds threshold.
* strong verification signals are supported.
* user explicitly enables automatic mode.

---

# Phase 12 Deliverables

* Automatic-mode policy engine.
* ATS and employer allowlist.
* package-specific automatic overrides.
* user enablement flow.
* automatic submission audit.
* automatic-mode quality dashboard.
* automatic-mode kill switch.
* automatic downgrade to Review mode.
* daily application limits.
* company limits.
* automatic-mode incident runbook.

---

# Limited Automatic Scope

Initial automatic mode should support:

```text
One candidate profile
One browser profile
One Stable ATS adapter
Known application workflow
No unresolved warning
No manual-only sensitive field
No CAPTCHA at final stage
Strong submission confirmation
```

---

# Automatic Downgrade Conditions

Automatically switch to Review or Manual mode when:

* ATS signature changes.
* unknown field appears.
* sensitive field appears.
* final button is ambiguous.
* generic fallback becomes necessary.
* review produces warning above threshold.
* provider fallback model was used unexpectedly.
* job identity confidence drops.
* browser account identity is uncertain.
* adapter health becomes degraded.

---

# Phase 12 Acceptance Criteria

* Automatic mode cannot be enabled accidentally.
* only allowlisted workflows qualify.
* final submission occurs once.
* strong verification is required.
* uncertain outcome pauses queue.
* automatic-mode metrics are recorded.
* kill switch stops future automatic submissions.
* adapter degradation disables automatic mode.
* candidate can review the full audit trail.

---

# Phase 12 Release

```text
Limited Automatic Beta
```

---

# Phase 12 Exit Gate

```text
Automatic Submission Gate
```

Required:

* Zero Critical failures in automatic-mode regression suite.
* zero duplicate final clicks.
* zero unsupported factual claims in critical dataset.
* zero sensitive-data leakage.
* unknown-submission protection proven.
* incident response tested.

---

# Phase 13 - ATS Expansion and Advanced Capabilities

## Goal

Expand supported workflows without weakening quality gates.

---

# Potential Phase 13 Capabilities

* Additional ATS adapters.
* Workday support.
* SmartRecruiters support.
* iCIMS support.
* Taleo support.
* employer-specific overrides.
* multiple browser profiles.
* limited concurrency.
* advanced dashboard reconciliation.
* optional email confirmation integration.
* application follow-up reminders.
* richer job discovery.
* saved search sources.
* improved analytics.
* encrypted package archives.
* additional candidate profiles.
* optional local database.

---

# Expansion Rule

Every new ATS adapter must independently pass:

* Detection tests.
* form tests.
* review tests.
* submission tests.
* recovery tests.
* security tests.
* privacy tests.
* live non-submission validation.
* controlled release gate.

Broad coverage should not inherit trust from another adapter.

---

# Workstream Structure

The project may be organized into parallel workstreams.

```text
Workstream A - Candidate Data and Schemas
Workstream B - Job Intelligence
Workstream C - Documents and Answers
Workstream D - Review and Readiness
Workstream E - Browser and ATS
Workstream F - Orchestration and Submission
Workstream G - History and Observability
Workstream H - Security and Operations
Workstream I - User Interface
Workstream J - Testing and Quality
```

---

# Workstream Dependencies

## Candidate Data

Feeds:

* Job ranking.
* resume tailoring.
* cover letters.
* answers.
* review.
* browser execution.

## Schemas

Feed every component.

## Review and Readiness

Depend on:

* Candidate data.
* packages.
* documents.
* answers.

Browser execution depends on Readiness.

## Submission Verification

Depends on:

* Browser.
* ATS adapters.
* orchestration.
* audit persistence.

## Automatic Mode

Depends on every safety-critical workstream.

---

# Recommended Development Sequencing

The following sequence minimizes rework:

```text
Schemas
    |
    v
Candidate Data
    |
    v
Job and Package Models
    |
    v
Documents and Answers
    |
    v
Review and Readiness
    |
    v
Browser Form Model
    |
    v
Generic Form Engine
    |
    v
ATS Adapter
    |
    v
Orchestration
    |
    v
Submission Verification
    |
    v
History and Operations
    |
    v
Automatic Mode
```

---

# Milestone Catalog

Recommended milestones:

```text
M0  Repository and Tooling
M1  Candidate Profile
M2  Job Intake
M3  Job Ranking
M4  Package Manifest
M5  Resume Tailoring
M6  Cover Letters and Answers
M7  Review
M8  Readiness
M9  Manual Application Release
M10 Browser Foundation
M11 Generic Form Engine
M12 First ATS Adapter
M13 Workflow Orchestration
M14 Submission Verification
M15 History and Reconciliation
M16 Review-Mode Beta
M17 Security and Operations Hardening
M18 Limited Automatic Beta
M19 Stable Automatic Release
```

---

# Milestone M0 - Repository and Tooling

Completion:

* Project installs.
* tests run.
* CI passes.
* schemas load.
* synthetic fixtures available.

---

# Milestone M1 - Candidate Profile

Completion:

* Candidate can be imported.
* structured profile is editable.
* work authorization is explicit.
* source conflicts are visible.

---

# Milestone M2 - Job Intake

Completion:

* Direct URL creates canonical Job.
* job identity and application URL captured.
* page snapshot retained.

---

# Milestone M3 - Job Ranking

Completion:

* Candidate-to-job score produced.
* hard-rule failures visible.
* recommendation explained.

---

# Milestone M4 - Package Manifest

Completion:

* Package created.
* snapshots stored.
* package versioning and fingerprints work.

---

# Milestone M5 - Resume Tailoring

Completion:

* Tailored resume produced.
* factual validation passes.
* PDF and DOCX are usable.

---

# Milestone M6 - Cover Letters and Answers

Completion:

* Cover letter generated when required.
* standard questions resolved.
* unknowns surfaced.

---

# Milestone M7 - Review

Completion:

* Cross-artifact contradictions detected.
* blocking findings stop progression.
* safe corrections work.

---

# Milestone M8 - Readiness

Completion:

* Preparation and manual-completion readiness exist.
* next allowed action is explicit.

---

# Milestone M9 - Manual Application Release

Completion:

* User can use package to apply manually.
* manual submission can be recorded.
* CSV and XLSX history update.

---

# Milestone M10 - Browser Foundation

Completion:

* Local synthetic forms complete.
* file upload and field verification pass.
* login and CAPTCHA pauses work.

---

# Milestone M11 - Generic Form Engine

Completion:

* Accessible unknown forms normalize and execute.
* ambiguous final controls require review.

---

# Milestone M12 - First ATS Adapter

Completion:

* One ATS completes supported workflow in Review mode.
* regression fixtures pass.

---

# Milestone M13 - Workflow Orchestration

Completion:

* Multiple packages run sequentially.
* pause, resume, cancellation, and crash recovery work.

---

# Milestone M14 - Submission Verification

Completion:

* Final click is durable.
* successful submission is verified.
* unknown outcome is protected.

---

# Milestone M15 - History and Reconciliation

Completion:

* Package, CSV, XLSX, and event log remain consistent.
* tracker failure cannot alter submission truth.

---

# Milestone M16 - Review-Mode Beta

Completion:

* Real-user Review-mode workflow available for supported ATS.
* mandatory approval before submission.

---

# Milestone M17 - Security and Operations Hardening

Completion:

* Secret Store.
* backups.
* migrations.
* health checks.
* Safe mode.
* security suite.

---

# Milestone M18 - Limited Automatic Beta

Completion:

* Automatic mode enabled only for allowlisted stable workflows.
* kill switch and downgrade rules work.

---

# Milestone M19 - Stable Automatic Release

Completion:

* Automatic mode repeatedly meets all safety and quality targets.
* operations and incident response are proven.

---

# Prioritization Framework

Work items should be prioritized by:

```text
Safety Impact
Dependency Value
User Value
Risk Reduction
Testability
Implementation Cost
Maintenance Cost
```

---

# Priority Levels

## P0 - Safety-Critical

Examples:

* Candidate factual integrity.
* work-authorization correctness.
* file upload restrictions.
* submission-attempt durability.
* Submission Unknown.
* duplicate prevention.
* secret redaction.
* job identity verification.

P0 work blocks release.

---

## P1 - Core Workflow

Examples:

* Candidate profile.
* job intake.
* package creation.
* resume preparation.
* review.
* readiness.
* browser form completion.
* history.

---

## P2 - Quality and Usability

Examples:

* Improved ranking.
* better document preview.
* richer search.
* analytics.
* expanded export.
* UI customization.

---

## P3 - Expansion

Examples:

* Additional ATS adapters.
* concurrency.
* email integration.
* multiple candidate profiles.
* cloud synchronization.

---

# Definition of Done for a Work Item

A work item is complete when:

* Code is implemented.
* schemas are updated.
* API contracts are updated.
* unit tests pass.
* integration tests pass where applicable.
* security and privacy checks pass.
* logs are structured.
* error messages are actionable.
* user interface is updated when needed.
* documentation is updated.
* migration exists when needed.
* known limitations are documented.

---

# Definition of Done for a Milestone

A milestone is complete when:

* All required work items are done.
* acceptance criteria pass.
* milestone tests pass.
* no blocking defects remain.
* health checks pass.
* operational recovery is tested.
* release notes exist.
* completion evidence is stored.

---

# Delivery Artifacts

Each milestone should produce:

* Source code.
* schemas.
* API documentation.
* tests.
* fixtures.
* migration files.
* user documentation.
* technical documentation.
* release notes.
* test report.
* known-limitations report.

---

# Backlog Structure

Recommended backlog hierarchy:

```text
Epic
    |
    +-- Capability
            |
            +-- Feature
                    |
                    +-- Work Item
                            |
                            +-- Test Cases
```

---

# Example Epic

```text
Epic:
Application Submission Safety

Capabilities:
Submission Attempt
Verification
Submission Unknown
Dashboard Reconciliation
History Synchronization
```

---

# Risk Register

The project should maintain a living risk register.

Recommended fields:

```text
Risk ID
Description
Probability
Impact
Mitigation
Detection Signal
Owner
Status
```

---

# Major Risk: Scope Expansion

## Description

Attempting to support too many ATS platforms before stabilizing the core architecture.

## Impact

* Delayed delivery.
* brittle automation.
* incomplete testing.
* maintenance burden.

## Mitigation

* One dedicated adapter first.
* Generic Form Engine.
* explicit adapter stability levels.
* automatic mode restricted by adapter.

---

# Major Risk: Candidate Fact Hallucination

## Description

Reasoning-provider output introduces unsupported experience or qualifications.

## Mitigation

* Source references.
* claim validation.
* deterministic cross-checks.
* critical zero-tolerance test set.
* human review before automatic mode.

---

# Major Risk: Work Authorization Error

## Description

Current authorization and future sponsorship are combined incorrectly.

## Mitigation

* Separate canonical fields.
* dedicated test matrix.
* question-family mappings.
* user confirmation.
* blocking consistency review.

---

# Major Risk: ATS Interface Changes

## Description

A supported ATS changes markup or workflow.

## Mitigation

* Semantic selectors.
* page signatures.
* adapter health monitoring.
* fixture regression.
* automatic downgrade to Review or Manual mode.

---

# Major Risk: Duplicate Submission

## Description

Crash, retry, stale state, or concurrency causes repeated submission.

## Mitigation

* Package lock.
* submission lock.
* durable attempt record.
* idempotency key.
* no final-click retry.
* Submission Unknown.

---

# Major Risk: Sensitive Data Leakage

## Description

Secrets or candidate-sensitive values enter logs, prompts, exports, or diagnostics.

## Mitigation

* Data classification.
* provider context filter.
* redaction.
* secret scanning.
* diagnostic sanitization.
* privacy tests.

---

# Major Risk: Browser Profile Corruption

## Description

Persistent profile becomes unusable or contains wrong account state.

## Mitigation

* Dedicated profiles.
* profile health checks.
* identity checks.
* profile replacement workflow.
* no profile backup by default.

---

# Major Risk: Tracker Corruption

## Description

CSV or XLSX becomes inconsistent with package submission state.

## Mitigation

* Packages remain source of truth.
* append-only event log.
* idempotent sync.
* atomic writes.
* backups.
* rebuild workflow.

---

# Major Risk: False Submission Success

## Description

Weak redirect or button disappearance is treated as verified submission.

## Mitigation

* Evidence-strength model.
* strong confirmation requirement.
* ATS-specific verification.
* Submission Unknown.

---

# Major Risk: Excessive Provider Dependence

## Description

Provider outage blocks the entire platform.

## Mitigation

* Deterministic local services first.
* cached approved outputs.
* manual mode.
* tested fallback model.
* provider health status.

---

# Major Risk: Maintenance Burden

## Description

Prompt versions, schemas, browser versions, and ATS variants create excessive upkeep.

## Mitigation

* Version registry.
* adapter contracts.
* automated regression.
* stable release channels.
* limited supported matrix.

---

# Decision Gates

Important decisions should occur at explicit gates.

---

# Gate A - Candidate Data Ready

Question:

```text
Can the platform represent candidate facts accurately and securely?
```

---

# Gate B - Preparation Ready

Question:

```text
Can the platform create truthful, reviewable application materials?
```

---

# Gate C - Manual Workflow Ready

Question:

```text
Can a user safely apply manually using the prepared package?
```

---

# Gate D - Browser Ready

Question:

```text
Can the browser fill controlled forms accurately and recoverably?
```

---

# Gate E - ATS Ready

Question:

```text
Can one ATS workflow be completed reliably in Review mode?
```

---

# Gate F - Submission Ready

Question:

```text
Can the platform perform and verify one irreversible submission without unsafe retry?
```

---

# Gate G - Review Release Ready

Question:

```text
Can a user complete supported applications with mandatory approval?
```

---

# Gate H - Automatic Ready

Question:

```text
Can an allowlisted workflow submit automatically with verified safety?
```

---

# Quality Metrics by Release Stage

## Manual Application Release

Track:

* Package preparation success.
* unsupported-claim findings.
* missing-answer frequency.
* user correction rate.
* history synchronization.

## Review-Mode Beta

Track:

* Browser completion rate.
* intervention frequency.
* review finding rate.
* ATS fallback rate.
* submission verification rate.
* Submission Unknown rate.

## Automatic Beta

Track:

* Automatic qualification rate.
* automatic downgrade rate.
* verified submission rate.
* unknown-submission rate.
* duplicate-prevention events.
* incidents.

---

# Suggested Quality Targets

Targets should be refined through testing.

```text
Critical candidate-fact errors:
0 in release test set.

Duplicate final clicks:
0.

Sensitive-data leakage:
0.

Wrong-company references:
0 in critical artifact set.

Structured provider output:
At least 99%.

Submission verification:
At least 99% for allowlisted automatic workflows.

Unknown submission:
Handled safely in 100% of tests.

History duplicate rows:
0.
```

---

# Technical Debt Policy

Technical debt should be recorded when:

* A temporary adapter selector is introduced.
* a migration lacks rollback.
* a service bypasses canonical schemas.
* raw dictionaries cross service boundaries.
* sensitive values are temporarily overexposed.
* a manual workaround replaces required automation.
* tests depend on unstable live sites.

Safety-related debt should not be deferred past the next release gate.

---

# Change-Control Policy

Changes affecting any of the following require expanded review:

* Work authorization.
* legal answers.
* demographic handling.
* upload paths.
* browser profiles.
* final submission.
* Submission Unknown.
* duplicate detection.
* secret storage.
* audit trail.
* history status.

---

# Feature Flag Strategy

Feature flags may control:

* Automatic submission.
* experimental ATS adapters.
* generic fallback.
* account creation.
* automatic attestation.
* raw HTML debugging.
* provider fallback.
* multi-profile concurrency.
* email integration.

---

# Feature Flag Requirements

* Safe default.
* documented owner.
* environment scope.
* expiration or review date.
* audit changes.
* no secret value.
* backend enforcement.

---

# Kill Switches

The platform should support immediate disabling of:

```text
All Automatic Submission
Specific ATS Adapter
Generic Form Submission
Provider Requests
Browser Execution
Account Creation
Automatic Attestation
```

Kill switches should not delete state.

---

# Rollout Strategy

## Stage 1 - Synthetic Only

* Synthetic candidate.
* synthetic jobs.
* local forms.
* simulated submissions.

## Stage 2 - Real Preparation

* Real candidate data.
* real jobs.
* local document generation.
* no browser submission.

## Stage 3 - Manual Handoff

* Real prepared packages.
* user submits manually.
* history recorded.

## Stage 4 - Browser Review

* Real browser form completion.
* stop before Submit.
* user reviews manually.

## Stage 5 - Review Submission

* User approves.
* platform submits.
* platform verifies.

## Stage 6 - Limited Automatic

* Allowlisted ATS.
* allowlisted workflow.
* no warnings.
* automatic submission enabled.

---

# Pilot Plan

A controlled pilot should use:

* One candidate profile.
* one target country.
* one browser profile.
* one Stable ATS adapter.
* a small number of jobs.
* Review mode.
* detailed diagnostics.
* daily history validation.
* immediate downgrade on regression.

---

# Pilot Success Criteria

* No wrong-job execution.
* no wrong-document upload.
* no factual contradiction submitted.
* no duplicate application.
* every submission verified or safely marked Unknown.
* history matches package evidence.
* user can recover every interrupted workflow.
* no sensitive-value leaks.

---

# Documentation Roadmap

Documentation should be delivered alongside implementation.

Required documentation categories:

* Installation.
* Candidate setup.
* Job intake.
* Package preparation.
* Review.
* browser operation.
* ATS limitations.
* submission states.
* history.
* privacy.
* security.
* backups.
* recovery.
* troubleshooting.
* developer architecture.
* schema reference.
* API reference.

---

# User Documentation Milestones

## Before Local Alpha

* Candidate setup.
* job import.
* package preparation.
* manual application.

## Before Review Beta

* Browser profile.
* queue.
* CAPTCHA and MFA.
* review.
* submission evidence.
* Submission Unknown.

## Before Automatic Beta

* Automatic-mode eligibility.
* automatic-mode risks.
* kill switch.
* incident handling.

---

# Testing Roadmap

Testing should grow with each phase.

```text
Phase 0:
Unit and schema tests.

Phase 1:
Candidate parsing and privacy tests.

Phase 2:
Job normalization and ranking tests.

Phase 3:
Artifact and answer validation.

Phase 4:
Review and readiness integration.

Phase 5:
Local browser fixtures.

Phase 6:
Generic form regression.

Phase 7:
ATS adapter regression.

Phase 8:
Recovery and concurrency.

Phase 9:
Submission and history durability.

Phase 10+:
End-to-end, security, upgrade, and release qualification.
```

---

# Migration Roadmap

Schema migrations should begin before substantial real data exists.

Initial migrations should support:

* Candidate Profile.
* Job.
* Application Package.
* History.
* Audit events.
* Configuration.

Every major schema should have at least one tested no-op or example migration path before Stable release.

---

# Operational Readiness Roadmap

## Before Real Candidate Data

* Local data root.
* restrictive permissions.
* secret store.
* redaction.
* backups.

## Before Browser Execution

* browser health.
* profile isolation.
* navigation policy.
* upload policy.
* crash recovery.

## Before Submission

* durable audit.
* submission lock.
* verification.
* history.
* disk-space check.

## Before Automatic Mode

* kill switch.
* health dashboard.
* adapter downgrade.
* incident runbook.
* tested rollback.

---

# Team Allocation Guidance

For a small team or solo developer, recommended focus order:

1. Domain schemas and package state.
2. Candidate data.
3. job analysis.
4. document and answer preparation.
5. review and readiness.
6. browser foundation.
7. one ATS adapter.
8. orchestration.
9. submission verification.
10. UI and operations hardening.

Parallelism should be limited when shared contracts are still changing rapidly.

---

# Parallelizable Work

After schemas stabilize, the following may proceed in parallel:

* UI for jobs and packages.
* resume-generation service.
* answer-service fixtures.
* browser local fixtures.
* history writer.
* security redaction.
* documentation.

---

# Work That Should Not Be Parallelized Prematurely

Avoid simultaneous independent implementation of:

* Multiple ATS adapters before the adapter contract stabilizes.
* Automatic submission before submission verification.
* Multiple package schemas.
* Frontend state transitions separate from backend rules.
* Multiple history sources of truth.
* multiple browser profile strategies.

---

# Solo-Developer Delivery Strategy

For a solo developer:

* Complete one milestone at a time.
* keep one active end-to-end synthetic workflow.
* avoid broad ATS coverage.
* prefer Review mode.
* automate tests early.
* maintain a small supported configuration matrix.
* use explicit deferred-feature lists.
* release Local Alpha before browser automation is complete.

---

# Example Iteration Structure

Each implementation iteration may follow:

```text
Select One Capability
        |
        v
Confirm Schema
        |
        v
Implement Domain Logic
        |
        v
Implement Persistence
        |
        v
Implement API
        |
        v
Implement UI
        |
        v
Add Tests
        |
        v
Run Security Review
        |
        v
Update Documentation
```

---

# Milestone Review Template

Each milestone review should answer:

```text
What was delivered?
Which acceptance criteria passed?
Which tests failed?
Which risks changed?
Which limitations remain?
Which release modes are enabled?
Which migrations are required?
What is the next dependency?
```

---

# Release Checklist

Before every user-facing release:

* Version updated.
* dependencies locked.
* schemas registered.
* migrations tested.
* test suite passed.
* security scan passed.
* synthetic end-to-end passed.
* browser version validated.
* adapter status reviewed.
* provider prompts evaluated.
* backup tested.
* upgrade tested.
* rollback tested.
* release notes written.
* limitations documented.
* automatic submission default confirmed.

---

# Review-Mode Release Checklist

Additional requirements:

* Browser form verification passes.
* review approval binding works.
* final click occurs once.
* confirmation verification passes.
* Submission Unknown survives restart.
* CSV and XLSX sync.
* queue pause behavior tested.
* wrong-account detection tested.

---

# Automatic-Mode Release Checklist

Additional requirements:

* Stable ATS adapter.
* allowlist active.
* automatic downgrade tested.
* zero Critical defects.
* zero duplicate final clicks.
* zero critical factual errors.
* zero secret leakage.
* kill switch tested.
* incident runbook tested.
* user explicitly enables automatic mode.

---

# Delivery Success Metrics

The roadmap should measure delivery success through outcomes rather than code volume.

Examples:

* Percentage of selected jobs successfully packaged.
* percentage of packages Ready.
* average number of blocking review findings.
* percentage of browser workflows completed.
* percentage of submissions verified.
* percentage of tracker syncs successful.
* percentage of interruptions recovered.
* number of Critical defects.
* number of automatic-mode downgrades.
* number of unsupported workflows handled safely.

---

# Deferred Capability Register

Maintain a visible deferred list.

Possible deferred capabilities:

* Mobile interface.
* cloud synchronization.
* team accounts.
* recruiter messaging.
* email inbox parsing.
* calendar scheduling.
* automatic assessments.
* advanced analytics.
* multi-candidate hosting.
* large-scale browser concurrency.
* external API for third parties.
* cloud-based secret management.
* automatic browser-profile backups.

Deferred does not mean rejected.

It means the capability is outside the current release boundary.

---

# Roadmap Completion Criteria

The implementation roadmap is complete when:

* Phases are defined.
* dependencies are explicit.
* milestones are testable.
* release stages are defined.
* MVP scope is constrained.
* MVP exclusions are documented.
* automatic submission has separate gates.
* acceptance criteria exist for each phase.
* security and privacy are integrated throughout.
* operations and recovery are included.
* risk register categories are defined.
* testing grows with implementation.
* rollback and migration are planned.
* pilot and rollout strategies exist.
* deferred capabilities are documented.
* definitions of done are explicit.

---

# Definition of MVP Completion

The MVP is complete when a user can:

1. Install the platform locally.
2. Create and validate a candidate profile.
3. Add and analyze job URLs.
4. Rank and select jobs.
5. Create Application Packages.
6. Generate truthful tailored resumes.
7. Generate optional cover letters.
8. Prepare standard application answers.
9. Review package consistency.
10. confirm readiness.
11. complete applications manually or through Review-mode browser automation.
12. approve final submission.
13. verify submission.
14. track applications in CSV and XLSX.
15. recover interrupted workflows.
16. back up and restore local data.
17. inspect audit and health information.

---

# Definition of Review-Mode Completion

Review mode is complete when:

* Supported application forms can be completed.
* all required fields are verified.
* uploaded documents are verified.
* final browser values are reviewed.
* user approval is bound to exact versions.
* final submission occurs once.
* success is verified.
* uncertain outcomes are protected.
* history is updated.
* recovery works.

---

# Definition of Automatic-Mode Completion

Automatic mode is complete when:

* Only allowlisted Stable workflows qualify.
* package has no unresolved warning above policy threshold.
* candidate facts are fully sourced.
* sensitive fields comply with policy.
* job and account identity are verified.
* final control is unambiguous.
* final action occurs once.
* strong submission evidence is available.
* unknown outcomes stop automatic progression.
* adapter degradation disables automatic mode.
* user can disable automatic submission globally.
* audit evidence is complete.
* quality targets are consistently met.

---

# Recommended First Production Boundary

The first production-quality boundary should be:

```text
Stable Review Mode
```

not broad automatic submission.

This release should support:

* Reliable preparation.
* reliable browser completion.
* mandatory final review.
* verified submission.
* durable history.
* safe recovery.

Automatic submission should be a later capability layered on top of this stable foundation.

---

# Summary

The implementation roadmap should move from low-risk local processing to high-consequence browser submission in deliberate stages.

The recommended sequence is:

```text
Foundations
    |
    v
Candidate Data
    |
    v
Job Intelligence
    |
    v
Application Packages
    |
    v
Review and Readiness
    |
    v
Manual Application
    |
    v
Browser Foundation
    |
    v
Generic Form Engine
    |
    v
First ATS Adapter
    |
    v
Queue Orchestration
    |
    v
Submission Verification
    |
    v
Review-Mode Release
    |
    v
Security and Operations Hardening
    |
    v
Limited Automatic Submission
```

The most important delivery rule is:

```text
Do not build automatic submission before building the systems that can stop it, verify it, recover it, and explain it.
```

A successful platform is not one that applies to the largest number of jobs.

It is one that:

* Uses truthful candidate information.
* selects appropriate jobs.
* creates high-quality materials.
* fills applications accurately.
* protects private data.
* avoids duplicate submissions.
* verifies submission outcomes.
* preserves reliable history.
* fails safely when uncertainty remains.
