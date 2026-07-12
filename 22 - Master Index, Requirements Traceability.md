# 22 - Master Index, Requirements Traceability, and Final Acceptance Checklist

## LLM-Powered Autonomous Job Search & Application Platform

Version: 1.0

---

# Purpose

This document is the master index, requirements traceability framework, verification matrix, release-acceptance checklist, and completion record for the LLM-Powered Autonomous Job Search and Application Platform.

It provides a single authoritative reference for:

* The complete specification suite.
* Requirement identifiers.
* Requirement ownership.
* Requirement sources.
* Implementation components.
* Verification methods.
* quality gates.
* release criteria.
* safety invariants.
* known limitations.
* deferred capabilities.
* final implementation acceptance.
* final production-use approval.

The platform combines:

* Candidate Knowledge Base management.
* Job discovery and ranking.
* Application Package creation.
* Resume and cover-letter preparation.
* Application-answer handling.
* Application Review.
* Application Readiness.
* Browser automation.
* ATS adapters.
* Generic form processing.
* Queue orchestration.
* Submission verification.
* Application history.
* Local user interfaces.
* Security and privacy.
* Testing and quality assurance.
* Deployment and maintenance.
* API contracts and schemas.
* Configuration and policies.
* Reasoning-provider integration.
* End-to-end recovery.

This document does not replace the detailed specifications.

It connects them and defines the evidence required to declare the platform ready.

---

# Core Principle

No requirement is complete merely because code exists.

```text
Requirement
    |
    v
Specification
    |
    v
Design Owner
    |
    v
Implementation
    |
    v
Automated Verification
    |
    v
Acceptance Evidence
    |
    v
Release Approval
```

Every safety-critical requirement should be traceable from written intent to repeatable evidence.

---

# Master Completion Rule

The platform is complete only when:

```text
Required behavior is implemented
and
Required tests pass
and
Required evidence exists
and
No release blocker remains
```

A demonstration of one successful application is not sufficient.

---

# Document Authority

The specification suite should be treated as a coordinated set.

Where two specifications appear to conflict, the following precedence should apply:

1. Security, privacy, and protected safety invariants.
2. Submission-integrity requirements.
3. Canonical API and schema contracts.
4. Configuration and policy constraints.
5. Domain-specific specifications.
6. End-to-end workflow definitions.
7. User-interface presentation requirements.
8. Implementation recommendations.

A lower-precedence document may clarify behavior but may not weaken a higher-precedence safety rule.

---

# Specification Suite Organization

The suite is organized into the following functional groups.

```text
Foundation and Domain Specifications
Application Review and Readiness
Execution and ATS Automation
Submission, History, and Observability
Security and Quality
Deployment and User Experience
Contracts and Implementation Structure
Configuration and Reasoning
End-to-End Acceptance
```

---

# Master Document Registry

The repository should maintain a machine-readable document registry containing:

* Document ID.
* exact filename.
* title.
* version.
* status.
* owner.
* dependencies.
* replacement document when deprecated.
* checksum.
* last reviewed date.

The repository registry is authoritative for exact filenames.

---

# Foundation Specification Set

Documents 01 through 07C define the foundational product and domain behaviors, including:

* Platform purpose and scope.
* Local-first architecture.
* Candidate Knowledge Base.
* Job discovery and ranking.
* Application Package preparation.
* Resume and cover-letter handling.
* Application-answer behavior.
* Browser preparation and form-execution foundations.

These documents should be registered individually using their exact repository filenames.

---

# Final Specification Set

## `07D-1_Application_Review.md`

Defines:

* Review stages.
* Review findings.
* factual consistency.
* artifact validation.
* browser-form review.
* safe corrections.
* user approval.
* approval invalidation.

Primary owners:

* Review module.
* Documents module.
* Answers module.

---

## `07D-2_Application_Readiness.md`

Defines:

* Stage-specific readiness.
* readiness checks.
* blockers.
* warnings.
* remediation.
* next allowed actions.
* refresh requirements.
* submission readiness.

Primary owner:

* Readiness module.

---

## `08_Application_Queue_And_Execution_Orchestration.md`

Defines:

* Queue lifecycle.
* workflow stages.
* locks.
* checkpoints.
* retries.
* pause and resume.
* cancellation.
* crash recovery.
* user interventions.

Primary owner:

* Orchestration module.

---

## `09_ATS_Adapters_And_Generic_Form_Engine.md`

Defines:

* ATS detection.
* adapter contracts.
* adapter capabilities.
* page classification.
* Generic Form Engine.
* field extraction.
* widget handling.
* fallback behavior.
* adapter stability.

Primary owners:

* ATS module.
* Browser module.

---

## `10_Submission_Verification_And_Application_History.md`

Defines:

* Final-submission boundary.
* submission attempts.
* submission locks.
* evidence.
* verification.
* Submission Unknown.
* duplicate prevention.
* application history.
* CSV and XLSX synchronization.
* history reconciliation.

Primary owners:

* Submission module.
* History module.

---

## `11_Logging_Observability_And_Audit_Trails.md`

Defines:

* Structured logs.
* audit events.
* correlation.
* traces.
* metrics.
* alerts.
* health reporting.
* diagnostic bundles.
* audit integrity.

Primary owner:

* Observability module.

---

## `12_Security_Privacy_And_Secrets_Management.md`

Defines:

* Threat model.
* data classification.
* Candidate Knowledge Base security.
* file access.
* Secret Store.
* browser-profile protection.
* provider context controls.
* prompt-injection defenses.
* sensitive-field policies.
* retention and deletion.
* incident response.

Primary owner:

* Security module.

---

## `13_Testing_Quality_Assurance_And_Validation_Strategy.md`

Defines:

* Test pyramid.
* fixtures.
* golden datasets.
* unit and integration testing.
* browser and ATS testing.
* LLM evaluation.
* security testing.
* privacy testing.
* recovery testing.
* quality gates.
* release qualification.

Primary owner:

* Quality engineering.

---

## `14_Deployment_Operations_And_Maintenance.md`

Defines:

* Installation.
* runtime dependencies.
* local directories.
* startup and shutdown.
* health checks.
* backups.
* restore.
* migrations.
* upgrades.
* rollback.
* maintenance.
* disaster recovery.
* decommissioning.

Primary owner:

* Operations module.

---

## `15_User_Interface_And_User_Experience.md`

Defines:

* Information architecture.
* onboarding.
* dashboard.
* jobs.
* packages.
* queue.
* review.
* interventions.
* submission outcomes.
* history.
* settings.
* health.
* accessibility.
* recovery experience.

Primary owners:

* Frontend.
* Local API.

---

## `16_API_Contracts_Data_Models_And_Schema_Registry.md`

Defines:

* Canonical entities.
* identifiers.
* versions.
* API contracts.
* request and response envelopes.
* errors.
* idempotency.
* concurrency.
* events.
* schema registry.
* compatibility.
* migrations.

Primary owners:

* API.
* Schema Registry.
* Domain modules.

---

## `17_Implementation_Roadmap_Milestones_And_Delivery_Plan.md`

Defines:

* Implementation phases.
* milestones.
* dependencies.
* release stages.
* rollout.
* pilot.
* risks.
* definitions of done.
* automatic-submission gates.

Primary owner:

* Project delivery.

---

## `18_Repository_Structure_Module_Boundaries_And_Code_Organization.md`

Defines:

* Modular monorepo.
* domain ownership.
* layer boundaries.
* ports and adapters.
* dependency direction.
* repository layout.
* frontend boundaries.
* schema ownership.
* architecture tests.

Primary owner:

* Software architecture.

---

## `19_Configuration_Feature_Flags_And_Policy_Management.md`

Defines:

* Typed configuration.
* precedence.
* effective policy.
* candidate rules.
* ATS and employer overrides.
* feature flags.
* kill switches.
* runtime constraints.
* policy simulation.
* configuration auditing.

Primary owner:

* Configuration and Policy module.

---

## `20_Prompt_Registry_Reasoning_Provider_Integration_And_Cost_Controls.md`

Defines:

* Prompt Registry.
* provider abstraction.
* model registry.
* context minimization.
* structured outputs.
* validation.
* retries.
* caching.
* fallback.
* evaluation.
* token accounting.
* cost controls.

Primary owners:

* Reasoning integration.
* Prompt owners.

---

## `21_End_To_End_Workflows_Sequence_Diagrams_And_Reference_Scenarios.md`

Defines:

* Integrated lifecycle.
* service interactions.
* sequence diagrams.
* failure paths.
* user interventions.
* recovery.
* Submission Unknown.
* reference scenarios.
* end-to-end acceptance behavior.

Primary owners:

* Architecture.
* Quality engineering.

---

## `22_Master_Index_Requirements_Traceability_And_Final_Acceptance_Checklist.md`

Defines:

* Master document index.
* requirements catalog.
* traceability.
* final release gates.
* acceptance evidence.
* completion record.

Primary owner:

* Project governance.

---

# Document Status Model

Each specification should have one status.

```text
draft
under_review
approved
implemented
verified
deprecated
retired
```

---

# Document Status Definitions

## Draft

The document is incomplete or actively changing.

## Under Review

The document is ready for stakeholder or architecture review.

## Approved

The document is accepted as an implementation requirement.

## Implemented

The major documented capabilities exist.

## Verified

Implementation has passed required acceptance tests.

## Deprecated

The document remains available for compatibility but has a replacement.

## Retired

The document is no longer applicable to supported releases.

---

# Document Registry Example

```json
{
  "document_id": "DOC-20",
  "filename": "20_Prompt_Registry_Reasoning_Provider_Integration_And_Cost_Controls.md",
  "title": "Prompt Registry, Reasoning Provider Integration, and Cost Controls",
  "version": "1.0",
  "status": "approved",
  "owner": "reasoning_integration",
  "depends_on": [
    "DOC-12",
    "DOC-13",
    "DOC-16",
    "DOC-19"
  ],
  "checksum": "",
  "last_reviewed_at": ""
}
```

---

# Requirement Identification System

Every implementable requirement should have a stable identifier.

Recommended format:

```text
<DOMAIN>-<NUMBER>
```

Examples:

```text
CAND-001
JOB-004
SUB-012
SEC-007
```

---

# Requirement Domains

```text
SYS  - Platform-wide architecture
CAND - Candidate Knowledge Base
JOB  - Job discovery and ranking
PKG  - Application Packages
DOC  - Resumes and cover letters
ANS  - Application questions and answers
REV  - Application Review
RDY  - Application Readiness
QUE  - Queue and orchestration
BRW  - Browser automation
ATS  - ATS adapters and Generic Form Engine
SUB  - Submission verification
HIST - Application history
OBS  - Logging, observability, and audit
SEC  - Security, privacy, and secrets
QA   - Testing and quality assurance
OPS  - Deployment, operations, and maintenance
UX   - User interface and accessibility
API  - API contracts and schemas
CFG  - Configuration, flags, and policies
LLM  - Prompt and provider integration
E2E  - Integrated workflows
REL  - Release and acceptance
```

---

# Requirement Priority

Each requirement should have one priority:

```text
P0 - Safety-critical and release-blocking
P1 - Required core capability
P2 - Required quality or usability capability
P3 - Optional or deferred enhancement
```

---

# Requirement Verification Methods

```text
UT   - Unit test
CT   - Component test
CON  - Contract test
IT   - Integration test
BT   - Controlled browser test
AT   - ATS regression test
E2E  - End-to-end test
ST   - Security test
PT   - Privacy test
RT   - Recovery test
MT   - Migration test
PERF - Performance test
A11Y - Accessibility test
MR   - Manual review
DOC  - Documentation inspection
```

A requirement may require multiple verification methods.

---

# Requirement Statuses

```text
not_started
in_progress
implemented
verified
blocked
deferred
not_applicable
```

---

# Requirement Record

```json
{
  "requirement_id": "SUB-006",
  "title": "Final click occurs no more than once",
  "priority": "P0",
  "source_documents": [
    "DOC-10",
    "DOC-13",
    "DOC-21"
  ],
  "owner": "submission",
  "implementation_components": [
    "SubmissionService",
    "SubmissionAttemptRepository",
    "SubmissionLock"
  ],
  "verification_methods": [
    "UT",
    "IT",
    "E2E",
    "RT"
  ],
  "acceptance_evidence": [],
  "status": "not_started"
}
```

---

# Platform-Wide Requirements

## SYS-001 - Local-First Operation

The platform should store candidate data, Application Packages, browser profiles, history, logs, and submission evidence locally by default.

Priority:

```text
P0
```

Verification:

```text
IT, ST, PT, DOC
```

Acceptance:

* No required cloud backend.
* Candidate data root remains local.
* External transmissions are purpose-limited.

---

## SYS-002 - Single-User MVP

The initial supported deployment should use one local user, one primary candidate profile, and controlled local browser sessions.

Priority:

```text
P1
```

Verification:

```text
IT, E2E, DOC
```

---

## SYS-003 - Modular Architecture

The platform should use explicit domain modules and public contracts rather than one monolithic workflow script.

Priority:

```text
P1
```

Verification:

```text
CON, architecture tests, DOC
```

---

## SYS-004 - Backend Authority

The backend should remain authoritative for entity state, allowed actions, approvals, and submission outcomes.

Priority:

```text
P0
```

Verification:

```text
CON, IT, ST
```

---

## SYS-005 - Safe Failure

When required truth, authorization, or evidence is missing, the platform should stop, downgrade, or request user input.

Priority:

```text
P0
```

Verification:

```text
UT, IT, E2E, ST
```

---

## SYS-006 - Manual Mode Availability

Every unsupported application workflow should offer a safe Manual-mode path when practical.

Priority:

```text
P1
```

Verification:

```text
IT, E2E, UX
```

---

# Candidate Knowledge Base Requirements

## CAND-001 - Canonical Candidate Profile

Candidate facts should be represented through a structured, versioned Candidate Profile.

Priority:

```text
P0
```

Verification:

```text
UT, CON, IT
```

---

## CAND-002 - Source Provenance

Every material candidate fact should retain source references.

Priority:

```text
P0
```

Verification:

```text
UT, CT, IT
```

---

## CAND-003 - Conflict Detection

Conflicting material candidate facts should be surfaced rather than silently resolved arbitrarily.

Priority:

```text
P0
```

Verification:

```text
UT, IT, E2E
```

---

## CAND-004 - Work Authorization Separation

The profile should represent separately:

* Authorized to work now.
* requires sponsorship now.
* may require sponsorship in the future.

Priority:

```text
P0
```

Verification:

```text
UT, CT, E2E
```

---

## CAND-005 - Candidate Snapshot

Every Application Package should use an immutable candidate-context snapshot.

Priority:

```text
P0
```

Verification:

```text
IT, CON, RT
```

---

## CAND-006 - Sensitive-Field Protection

Highly sensitive candidate values should be masked and accessed through protected interfaces.

Priority:

```text
P0
```

Verification:

```text
ST, PT, IT
```

---

## CAND-007 - Purpose-Specific Views

Downstream modules should receive only the candidate information required for their purpose.

Priority:

```text
P0
```

Verification:

```text
CON, PT, architecture tests
```

---

## CAND-008 - Versioned Updates

Candidate updates should use optimistic concurrency and atomic persistence.

Priority:

```text
P1
```

Verification:

```text
UT, IT, RT
```

---

## CAND-009 - Impact Analysis

Material candidate changes should identify affected prepared and queued packages.

Priority:

```text
P1
```

Verification:

```text
IT, E2E
```

---

## CAND-010 - No Silent Generated Facts

Generated documents or answers may not silently update candidate master data.

Priority:

```text
P0
```

Verification:

```text
architecture tests, ST, E2E
```

---

# Job Requirements

## JOB-001 - Canonical Job Identity

Every job should have a stable internal ID and preserve available employer job IDs and requisition IDs separately.

Priority:

```text
P0
```

Verification:

```text
UT, CON, IT
```

---

## JOB-002 - Source Preservation

The original job URL, source, content hash, and discovery time should be retained.

Priority:

```text
P1
```

Verification:

```text
IT
```

---

## JOB-003 - Unknown Values Remain Unknown

Missing salary, date, sponsorship, or location information should not be fabricated.

Priority:

```text
P0
```

Verification:

```text
UT, CT, LLM evaluation
```

---

## JOB-004 - Requirement Classification

Job analysis should distinguish required and preferred qualifications.

Priority:

```text
P1
```

Verification:

```text
UT, CT, LLM evaluation
```

---

## JOB-005 - Explainable Ranking

The match recommendation should expose score components, strengths, gaps, and hard-rule results.

Priority:

```text
P1
```

Verification:

```text
UT, IT, UX
```

---

## JOB-006 - Deterministic Hard Rules

Country, clearance, exclusion, salary, and other hard rules should be enforced deterministically.

Priority:

```text
P0
```

Verification:

```text
UT, CT
```

---

## JOB-007 - Duplicate Job Detection

Repeated discovery of the same job should not create uncontrolled duplicate records.

Priority:

```text
P1
```

Verification:

```text
UT, IT
```

---

## JOB-008 - Untrusted Content Treatment

Job descriptions should be treated as untrusted external content.

Priority:

```text
P0
```

Verification:

```text
ST, PT, E2E
```

---

# Application Package Requirements

## PKG-001 - Self-Contained Package

Each selected job should create a self-contained Application Package.

Priority:

```text
P0
```

Verification:

```text
IT, E2E
```

---

## PKG-002 - Immutable Snapshots

Packages should retain immutable job and candidate snapshots.

Priority:

```text
P0
```

Verification:

```text
IT, RT
```

---

## PKG-003 - Versioned Artifacts

Every resume, cover letter, answer set, review, and readiness report should have a version.

Priority:

```text
P0
```

Verification:

```text
CON, IT
```

---

## PKG-004 - Artifact Hashes

Consequential artifacts should have content hashes.

Priority:

```text
P0
```

Verification:

```text
UT, IT, ST
```

---

## PKG-005 - Package Manifest

Every package should have a schema-validated manifest.

Priority:

```text
P1
```

Verification:

```text
CON, IT
```

---

## PKG-006 - Staleness Detection

The platform should detect when source facts, policies, jobs, or active artifacts make a package stale.

Priority:

```text
P0
```

Verification:

```text
UT, IT, E2E
```

---

## PKG-007 - Atomic Writes

Package persistence should use atomic or staged writes.

Priority:

```text
P0
```

Verification:

```text
IT, RT
```

---

## PKG-008 - Package Lock

An executing package should be protected by a durable ownership lock.

Priority:

```text
P0
```

Verification:

```text
UT, IT, RT
```

---

## PKG-009 - Submitted Package Preservation

Submitted artifacts and snapshots should not be silently overwritten by later source changes.

Priority:

```text
P0
```

Verification:

```text
IT, RT
```

---

# Document Requirements

## DOC-001 - Supported Base Resume

Resume tailoring should begin from an approved existing resume or candidate source.

Priority:

```text
P0
```

Verification:

```text
CT, IT
```

---

## DOC-002 - Factual Resume Validation

Tailored resumes should preserve supported employers, titles, dates, skills, achievements, and metrics.

Priority:

```text
P0
```

Verification:

```text
UT, CT, LLM evaluation, E2E
```

---

## DOC-003 - No Unsupported Qualifications

Documents should not introduce unsupported skills, certifications, education, metrics, referrals, or clearance.

Priority:

```text
P0
```

Verification:

```text
CT, LLM evaluation, ST
```

---

## DOC-004 - Correct Company and Role

Cover letters and job-specific materials should reference the correct employer and role.

Priority:

```text
P0
```

Verification:

```text
CT, LLM evaluation, E2E
```

---

## DOC-005 - ATS-Readable Output

Generated resumes should remain readable and uploadable in configured formats.

Priority:

```text
P1
```

Verification:

```text
CT, document-rendering tests, BT
```

---

## DOC-006 - User-Edit Preservation

Regeneration should not silently overwrite approved user edits.

Priority:

```text
P1
```

Verification:

```text
IT, UX
```

---

## DOC-007 - Version Comparison

Users should be able to inspect changes and prior artifact versions.

Priority:

```text
P2
```

Verification:

```text
UX, IT
```

---

## DOC-008 - Optional Cover-Letter Policy

Cover letters should be generated or omitted according to resolved package policy.

Priority:

```text
P1
```

Verification:

```text
UT, IT
```

---

# Application Answer Requirements

## ANS-001 - Canonical Question Families

Application questions should map to versioned canonical question families.

Priority:

```text
P1
```

Verification:

```text
UT, CT, LLM evaluation
```

---

## ANS-002 - Deterministic Standard Answers

Exact candidate facts and saved answers should be resolved deterministically.

Priority:

```text
P0
```

Verification:

```text
UT, CT
```

---

## ANS-003 - Missing Is Not No

An absent answer must not be interpreted as No.

Priority:

```text
P0
```

Verification:

```text
UT, E2E
```

---

## ANS-004 - Legal Answers Not Inferred

The provider should not determine unknown legal answers.

Priority:

```text
P0
```

Verification:

```text
ST, PT, E2E
```

---

## ANS-005 - Demographics Not Inferred

Demographic, disability, and veteran-status answers should never be inferred.

Priority:

```text
P0
```

Verification:

```text
PT, ST, E2E
```

---

## ANS-006 - Compound Question Handling

Ambiguous compound questions should require explicit resolution.

Priority:

```text
P0
```

Verification:

```text
UT, CT, E2E
```

---

## ANS-007 - Narrative Source Support

Narrative answers should use approved candidate facts and stories.

Priority:

```text
P0
```

Verification:

```text
CT, LLM evaluation
```

---

## ANS-008 - Length Compliance

Narrative outputs should satisfy browser or application character limits.

Priority:

```text
P1
```

Verification:

```text
UT, CT
```

---

## ANS-009 - Scoped Reuse

User answers should support application-only, company, question-family, or global reuse with explicit approval.

Priority:

```text
P1
```

Verification:

```text
IT, UX
```

---

## ANS-010 - Answer Provenance

Every resolved answer should identify its source and confidence or resolution method.

Priority:

```text
P0
```

Verification:

```text
CON, IT
```

---

# Review Requirements

## REV-001 - Preparation Review

Prepared documents and answers should undergo consistency review before readiness.

Priority:

```text
P0
```

Verification:

```text
CT, IT
```

---

## REV-002 - Browser-Form Review

The final browser form should be reviewable against package expectations.

Priority:

```text
P0
```

Verification:

```text
BT, AT, E2E
```

---

## REV-003 - Severity Classification

Review findings should use stable severities and categories.

Priority:

```text
P1
```

Verification:

```text
UT, CON
```

---

## REV-004 - Blocking Findings

Blocking or disallowed high-severity findings should prevent progression.

Priority:

```text
P0
```

Verification:

```text
UT, IT, E2E
```

---

## REV-005 - Bounded Safe Corrections

Only predefined safe corrections should be applied automatically.

Priority:

```text
P0
```

Verification:

```text
UT, CT
```

---

## REV-006 - Version-Bound Approval

Approval should reference exact artifact, answer-set, package, and form versions.

Priority:

```text
P0
```

Verification:

```text
CON, IT, E2E
```

---

## REV-007 - Approval Invalidation

Material changes should invalidate prior approval.

Priority:

```text
P0
```

Verification:

```text
UT, IT, E2E
```

---

## REV-008 - Provider Cannot Approve Submission

Reasoning-provider review output may inform findings but cannot authorize final submission.

Priority:

```text
P0
```

Verification:

```text
architecture tests, ST
```

---

# Readiness Requirements

## RDY-001 - Stage-Specific Readiness

Readiness should be evaluated separately for preparation, execution, review, submission, and history synchronization.

Priority:

```text
P0
```

Verification:

```text
UT, CT, IT
```

---

## RDY-002 - Current Inputs

Readiness should bind to current entity, artifact, policy, and health versions.

Priority:

```text
P0
```

Verification:

```text
UT, IT
```

---

## RDY-003 - Explicit Blockers and Warnings

Readiness should distinguish blockers from warnings.

Priority:

```text
P1
```

Verification:

```text
UT, UX
```

---

## RDY-004 - Next Allowed Actions

The backend should return next allowed actions.

Priority:

```text
P0
```

Verification:

```text
CON, IT, ST
```

---

## RDY-005 - Duplicate Check Currency

Submission readiness should require a current duplicate check.

Priority:

```text
P0
```

Verification:

```text
IT, E2E
```

---

## RDY-006 - Operational Health

Final submission should require sufficient storage, audit, browser, and integrity health.

Priority:

```text
P0
```

Verification:

```text
IT, RT, E2E
```

---

## RDY-007 - Runtime Policy Recalculation

Readiness should be recalculated when a relevant runtime constraint changes.

Priority:

```text
P0
```

Verification:

```text
IT, E2E
```

---

# Queue and Orchestration Requirements

## QUE-001 - Sequential MVP Execution

The initial queue should execute one application at a time per browser profile.

Priority:

```text
P1
```

Verification:

```text
IT, E2E
```

---

## QUE-002 - Queue Admission Validation

Only eligible packages should be admitted.

Priority:

```text
P0
```

Verification:

```text
UT, IT
```

---

## QUE-003 - Durable Workflow State

Workflow state should persist after every consequential stage.

Priority:

```text
P0
```

Verification:

```text
IT, RT
```

---

## QUE-004 - Checkpoint Recovery

Recoverable workflows should resume from validated checkpoints.

Priority:

```text
P0
```

Verification:

```text
RT, E2E
```

---

## QUE-005 - Pause and Resume

The queue should pause and resume without losing authoritative state.

Priority:

```text
P1
```

Verification:

```text
IT, RT
```

---

## QUE-006 - User Intervention

CAPTCHA, MFA, missing answers, reviews, and assessments should create explicit user-action requests.

Priority:

```text
P0
```

Verification:

```text
BT, E2E, UX
```

---

## QUE-007 - Failure Isolation

An ordinary package failure should not necessarily invalidate the rest of the queue.

Priority:

```text
P1
```

Verification:

```text
IT, E2E
```

---

## QUE-008 - Conservative Submission Recovery

An interrupted final-submission workflow should enter verification rather than normal execution.

Priority:

```text
P0
```

Verification:

```text
RT, E2E
```

---

## QUE-009 - Queue Event Stream

Queue and workflow changes should be visible through structured events.

Priority:

```text
P1
```

Verification:

```text
CON, IT, UX
```

---

# Browser Requirements

## BRW-001 - Dedicated Browser Profile

Automation should use a dedicated browser profile rather than the user's ordinary browser profile.

Priority:

```text
P0
```

Verification:

```text
BT, ST
```

---

## BRW-002 - Visible Browser Default

Browser automation should be visible by default.

Priority:

```text
P1
```

Verification:

```text
BT, UX
```

---

## BRW-003 - Approved Interaction Plan

The Browser Service should execute a validated interaction plan rather than resolve candidate truth.

Priority:

```text
P0
```

Verification:

```text
architecture tests, CON, ST
```

---

## BRW-004 - Action Verification

Each field and navigation action should be verified.

Priority:

```text
P0
```

Verification:

```text
BT, AT, E2E
```

---

## BRW-005 - Upload Verification

Uploaded files should be approved, hashed, type-validated, and verified in the browser.

Priority:

```text
P0
```

Verification:

```text
BT, ST, E2E
```

---

## BRW-006 - No CAPTCHA Bypass

The platform should pause for manual CAPTCHA completion.

Priority:

```text
P0
```

Verification:

```text
BT, ST, E2E
```

---

## BRW-007 - No MFA Bypass

The platform should pause for manual MFA completion.

Priority:

```text
P0
```

Verification:

```text
BT, ST
```

---

## BRW-008 - Account Identity Check

The platform should detect and stop on a mismatched ATS candidate identity.

Priority:

```text
P0
```

Verification:

```text
BT, E2E, ST
```

---

## BRW-009 - Controlled Navigation

Unexpected redirects and untrusted domains should pause before candidate data entry.

Priority:

```text
P0
```

Verification:

```text
ST, BT, E2E
```

---

## BRW-010 - Crash Recovery

Browser crashes should preserve package and workflow safety.

Priority:

```text
P0
```

Verification:

```text
RT, E2E
```

---

# ATS Requirements

## ATS-001 - Adapter Contract

Every dedicated ATS adapter should implement the canonical adapter contract.

Priority:

```text
P1
```

Verification:

```text
CON, AT
```

---

## ATS-002 - ATS Detection

ATS detection should use domain, page signatures, and other controlled signals.

Priority:

```text
P1
```

Verification:

```text
UT, AT
```

---

## ATS-003 - Capability Declaration

Adapters should declare capabilities and unsupported behavior.

Priority:

```text
P1
```

Verification:

```text
CON, AT
```

---

## ATS-004 - Stability Classification

Each adapter should be Experimental, Beta, Stable, Degraded, or Disabled.

Priority:

```text
P0
```

Verification:

```text
IT, QA review
```

---

## ATS-005 - Automatic-Mode Restriction

Only Stable and explicitly approved workflows may use Automatic mode.

Priority:

```text
P0
```

Verification:

```text
UT, IT, E2E
```

---

## ATS-006 - Generic Form Safety

The Generic Form Engine should require sufficient field and action confidence.

Priority:

```text
P0
```

Verification:

```text
BT, ST, E2E
```

---

## ATS-007 - Unsupported Widget Handling

Unsupported required controls should cause user intervention or Manual mode.

Priority:

```text
P0
```

Verification:

```text
BT, E2E
```

---

## ATS-008 - Final Control Identification

Final submission controls should be identified separately from normal navigation controls.

Priority:

```text
P0
```

Verification:

```text
AT, BT, E2E
```

---

## ATS-009 - Adapter Regression Suite

Every supported adapter should have sanitized regression fixtures.

Priority:

```text
P0
```

Verification:

```text
AT, release qualification
```

---

## ATS-010 - Safe Degradation

An adapter regression should downgrade affected workflows before final submission.

Priority:

```text
P0
```

Verification:

```text
IT, E2E
```

---

# Submission Requirements

## SUB-001 - Centralized Submission Authority

Only the Submission module may authorize and record the final action.

Priority:

```text
P0
```

Verification:

```text
architecture tests, ST
```

---

## SUB-002 - Pre-Submission Snapshot

The platform should persist a final package, policy, form, and readiness snapshot before the click.

Priority:

```text
P0
```

Verification:

```text
IT, RT
```

---

## SUB-003 - Submission Lock

The platform should acquire a durable submission lock.

Priority:

```text
P0
```

Verification:

```text
UT, IT, RT
```

---

## SUB-004 - Attempt Record Before Click

The submission-attempt record should be durable before browser execution of the final control.

Priority:

```text
P0
```

Verification:

```text
IT, RT, E2E
```

---

## SUB-005 - Exact Attempt Identity

Each final action should use a unique attempt ID and idempotency key.

Priority:

```text
P0
```

Verification:

```text
UT, CON, IT
```

---

## SUB-006 - Single Final Click

The final control should be activated no more than once for an attempt.

Priority:

```text
P0
```

Verification:

```text
UT, IT, RT, E2E
```

Acceptance target:

```text
Zero duplicate final clicks.
```

---

## SUB-007 - Strong Evidence Required

Submitted status should require conclusive or strong evidence.

Priority:

```text
P0
```

Verification:

```text
UT, AT, E2E
```

---

## SUB-008 - Submission Unknown

Insufficient evidence after a click should create Submission Unknown.

Priority:

```text
P0
```

Verification:

```text
UT, IT, E2E, RT
```

---

## SUB-009 - No Automatic Unknown Retry

Submission Unknown should never trigger an automatic repeat click.

Priority:

```text
P0
```

Verification:

```text
UT, ST, RT, E2E
```

---

## SUB-010 - Unknown Resolution History

Resolving an unknown outcome should preserve the original unknown event and record the resolution source.

Priority:

```text
P0
```

Verification:

```text
IT, E2E
```

---

## SUB-011 - Duplicate Prevention

The platform should check historical and available ATS evidence before submission.

Priority:

```text
P0
```

Verification:

```text
UT, IT, E2E
```

---

## SUB-012 - Tracker Independence

History write failures should not alter verified submission truth.

Priority:

```text
P0
```

Verification:

```text
IT, RT, E2E
```

---

## SUB-013 - Failure Timing Clarity

The system should distinguish failure before click from uncertainty after click.

Priority:

```text
P0
```

Verification:

```text
UT, UX, E2E
```

---

# History Requirements

## HIST-001 - Canonical History Record

Every application should have a structured history record.

Priority:

```text
P1
```

Verification:

```text
CON, IT
```

---

## HIST-002 - Separate Status Domains

Submission status and recruitment status should remain separate.

Priority:

```text
P0
```

Verification:

```text
UT, IT
```

---

## HIST-003 - Append-Only Events

Material history changes should create append-only events.

Priority:

```text
P1
```

Verification:

```text
IT, RT
```

---

## HIST-004 - CSV Synchronization

The system should maintain a local CSV tracker when enabled.

Priority:

```text
P1
```

Verification:

```text
IT, RT
```

---

## HIST-005 - XLSX Synchronization

The system should maintain a local XLSX tracker when enabled.

Priority:

```text
P1
```

Verification:

```text
IT, RT
```

---

## HIST-006 - Idempotent Writes

History synchronization should not create duplicate records.

Priority:

```text
P0
```

Verification:

```text
UT, IT, RT
```

---

## HIST-007 - Rebuild

CSV and XLSX outputs should be rebuildable from canonical package and event state.

Priority:

```text
P1
```

Verification:

```text
RT, E2E
```

---

## HIST-008 - Manual Applications

User-reported manual applications should identify their verification source.

Priority:

```text
P1
```

Verification:

```text
IT, UX
```

---

## HIST-009 - Corrections Audited

History corrections should record old value, new value, reason, actor, and time.

Priority:

```text
P1
```

Verification:

```text
IT, OBS checks
```

---

# Observability Requirements

## OBS-001 - Structured Logs

Runtime logs should use structured events and stable categories.

Priority:

```text
P1
```

Verification:

```text
CT, IT
```

---

## OBS-002 - Correlation Identifiers

Events should include available package, workflow, queue, request, and attempt IDs.

Priority:

```text
P1
```

Verification:

```text
CT, IT
```

---

## OBS-003 - Audit Trail

Business-significant changes should create audit events.

Priority:

```text
P0
```

Verification:

```text
IT, E2E
```

---

## OBS-004 - Audit Integrity

Audit chains or equivalent integrity checks should detect modification or missing events.

Priority:

```text
P0
```

Verification:

```text
ST, RT
```

---

## OBS-005 - Sensitive Redaction

Logs and diagnostics should redact protected values.

Priority:

```text
P0
```

Verification:

```text
ST, PT
```

---

## OBS-006 - Health Checks

The system should expose health for storage, browser, provider, adapters, history, schemas, audit, and disk.

Priority:

```text
P1
```

Verification:

```text
IT, OPS tests
```

---

## OBS-007 - Diagnostic Bundles

Diagnostic bundles should be sanitized and explicitly generated.

Priority:

```text
P1
```

Verification:

```text
ST, PT, OPS tests
```

---

## OBS-008 - Critical Alerts

Security, unknown-submission, audit-integrity, and durability failures should create prominent alerts.

Priority:

```text
P0
```

Verification:

```text
IT, UX, E2E
```

---

# Security and Privacy Requirements

## SEC-001 - Data Classification

Stored and transmitted information should have a data classification.

Priority:

```text
P0
```

Verification:

```text
CON, ST, PT
```

---

## SEC-002 - Secret Store

API keys, passwords, session material, and encryption keys should not be stored as ordinary configuration values.

Priority:

```text
P0
```

Verification:

```text
ST, IT
```

---

## SEC-003 - Safe File References

APIs should use approved file references rather than arbitrary absolute paths.

Priority:

```text
P0
```

Verification:

```text
CON, ST
```

---

## SEC-004 - Path Traversal Prevention

All file operations should reject path traversal and unsafe symbolic-link behavior.

Priority:

```text
P0
```

Verification:

```text
ST
```

---

## SEC-005 - Upload Authorization

Browser uploads should require an approved manifest and destination.

Priority:

```text
P0
```

Verification:

```text
ST, BT
```

---

## SEC-006 - Domain Trust

Navigation should enforce HTTPS and trusted-domain policy.

Priority:

```text
P0
```

Verification:

```text
ST, BT, E2E
```

---

## SEC-007 - Provider Context Minimization

Only task-required candidate information should be sent to reasoning providers.

Priority:

```text
P0
```

Verification:

```text
PT, ST, CT
```

---

## SEC-008 - Prompt-Injection Defense

External content should not override platform instructions, policies, or access controls.

Priority:

```text
P0
```

Verification:

```text
ST, LLM evaluation, E2E
```

---

## SEC-009 - Government-ID Policy

Government identifiers should default to Never Provide or Manual Only according to protected policy.

Priority:

```text
P0
```

Verification:

```text
ST, PT, E2E
```

---

## SEC-010 - Payment-Request Blocking

Bank or payment requests in ordinary job applications should trigger a critical stop.

Priority:

```text
P0
```

Verification:

```text
ST, E2E
```

---

## SEC-011 - Browser-Profile Isolation

Browser profiles should be dedicated, protected, and excluded from normal exports and backups.

Priority:

```text
P0
```

Verification:

```text
ST, OPS tests
```

---

## SEC-012 - Local API Protection

The local UI API should use localhost binding, origin validation, CSRF protection, and secure session behavior.

Priority:

```text
P0
```

Verification:

```text
ST
```

---

## SEC-013 - No Arbitrary Provider Tools

Reasoning providers should not receive unrestricted shell, file, browser, secret, or network tools.

Priority:

```text
P0
```

Verification:

```text
architecture tests, ST
```

---

## SEC-014 - Retention and Deletion

Users should be able to inspect retention and deliberately delete local data by category.

Priority:

```text
P1
```

Verification:

```text
IT, PT, UX
```

---

## SEC-015 - Security Incident Response

Secret exposure, untrusted domains, audit failures, and sensitive-data leakage should have defined incident workflows.

Priority:

```text
P0
```

Verification:

```text
RT, E2E, MR
```

---

# Testing and Quality Requirements

## QA-001 - Synthetic Test Data

Automated testing should use synthetic candidates, jobs, and browser forms.

Priority:

```text
P0
```

Verification:

```text
DOC, repository scan
```

---

## QA-002 - Test Pyramid

The project should maintain unit, component, contract, integration, browser, end-to-end, security, and recovery tests.

Priority:

```text
P1
```

Verification:

```text
test inventory
```

---

## QA-003 - Deterministic Provider Mocks

Routine tests should use deterministic reasoning-provider mocks.

Priority:

```text
P1
```

Verification:

```text
CT, CI inspection
```

---

## QA-004 - Real-Model Evaluation

Prompt or model changes should trigger synthetic real-model evaluation before release.

Priority:

```text
P0
```

Verification:

```text
evaluation report
```

---

## QA-005 - Zero-Tolerance Critical Failures

Critical evaluation sets should allow zero:

* Unsupported factual claims.
* wrong-company references.
* sensitive-data leaks.
* duplicate final clicks.
* false verified submissions.

Priority:

```text
P0
```

Verification:

```text
release quality report
```

---

## QA-006 - ATS Regression

Every supported adapter should have a passing regression suite.

Priority:

```text
P0
```

Verification:

```text
AT
```

---

## QA-007 - Recovery Testing

Crashes and interruptions should be tested before, during, and after final submission.

Priority:

```text
P0
```

Verification:

```text
RT, E2E
```

---

## QA-008 - Migration Testing

Schema and configuration migrations should have forward, failure, and rollback tests.

Priority:

```text
P0
```

Verification:

```text
MT
```

---

## QA-009 - Requirement Traceability

Every P0 and P1 requirement should map to one or more tests.

Priority:

```text
P0
```

Verification:

```text
traceability report
```

---

## QA-010 - Defect Regression Fixtures

Every consequential fixed defect should produce a regression test when practical.

Priority:

```text
P1
```

Verification:

```text
code review and fixture inventory
```

---

# Deployment and Operations Requirements

## OPS-001 - Reproducible Installation

Installation should use supported, pinned runtime and dependencies.

Priority:

```text
P1
```

Verification:

```text
installation tests
```

---

## OPS-002 - Local Data Initialization

The platform should create and validate required local directories safely.

Priority:

```text
P1
```

Verification:

```text
IT, installation tests
```

---

## OPS-003 - Startup Validation

Startup should validate configuration, storage, schemas, logs, audit persistence, and pending migrations.

Priority:

```text
P0
```

Verification:

```text
IT, RT
```

---

## OPS-004 - Graceful Shutdown

Shutdown should preserve workflow state, checkpoints, logs, and unresolved submission locks.

Priority:

```text
P0
```

Verification:

```text
RT
```

---

## OPS-005 - Safe Mode

Safe mode should permit diagnosis while disabling consequential actions.

Priority:

```text
P1
```

Verification:

```text
IT, OPS tests
```

---

## OPS-006 - Maintenance Mode

Migrations, restores, and destructive repairs should run in Maintenance mode.

Priority:

```text
P1
```

Verification:

```text
MT, RT
```

---

## OPS-007 - Verified Backup

Backups should have manifests, checksums, exclusions, and verification.

Priority:

```text
P0
```

Verification:

```text
RT, OPS tests
```

---

## OPS-008 - Staged Restore

Restore should validate and stage data before replacing current state.

Priority:

```text
P0
```

Verification:

```text
RT, ST
```

---

## OPS-009 - Upgrade Rollback

Upgrades should create pre-upgrade backups and support rollback.

Priority:

```text
P0
```

Verification:

```text
MT, installation tests
```

---

## OPS-010 - Disk-Space Protection

Final submission should be blocked when durable evidence cannot be guaranteed.

Priority:

```text
P0
```

Verification:

```text
RT, E2E
```

---

## OPS-011 - Cache and Log Retention

Caches, logs, screenshots, and diagnostics should have bounded retention.

Priority:

```text
P1
```

Verification:

```text
OPS tests, PT
```

---

## OPS-012 - Decommissioning

The user should be able to remove the application, data, profiles, history, backups, and secrets through explicit scopes.

Priority:

```text
P1
```

Verification:

```text
OPS tests, PT, UX
```

---

# User Interface Requirements

## UX-001 - Clear Workflow State

The interface should show what is happening, what happened, and what happens next.

Priority:

```text
P1
```

Verification:

```text
UX, A11Y, E2E
```

---

## UX-002 - Submission-State Distinction

The UI should distinguish:

* Ready.
* Ready for Review.
* Submitting.
* Submitted.
* Failed.
* Submission Unknown.

Priority:

```text
P0
```

Verification:

```text
UX, E2E
```

---

## UX-003 - Irreversible Action Labeling

User-approved final submission should use an explicit action label.

Priority:

```text
P0
```

Verification:

```text
UX, A11Y
```

---

## UX-004 - Sensitive Masking

Sensitive values should be hidden by default and revealed explicitly.

Priority:

```text
P0
```

Verification:

```text
PT, UX, A11Y
```

---

## UX-005 - Actionable Errors

Errors should explain impact, data safety, submission possibility, and next action.

Priority:

```text
P1
```

Verification:

```text
UX, E2E
```

---

## UX-006 - Intervention Context

CAPTCHA, MFA, missing answers, and assessments should retain the active job and workflow context.

Priority:

```text
P1
```

Verification:

```text
UX, E2E
```

---

## UX-007 - Configured vs Effective Settings

Settings should show requested and effective values with explanations.

Priority:

```text
P1
```

Verification:

```text
UX, IT
```

---

## UX-008 - Keyboard Accessibility

Critical workflows should be operable without a mouse.

Priority:

```text
P1
```

Verification:

```text
A11Y
```

---

## UX-009 - Screen-Reader Status

Critical status changes should be announced accessibly.

Priority:

```text
P1
```

Verification:

```text
A11Y
```

---

## UX-010 - Color Independence

Status should not be communicated by color alone.

Priority:

```text
P1
```

Verification:

```text
A11Y, visual review
```

---

## UX-011 - Recovery UI

Interrupted workflows should display recovery category, previous checkpoint, and submission-attempt state.

Priority:

```text
P0
```

Verification:

```text
UX, RT, E2E
```

---

# API and Schema Requirements

## API-001 - Versioned Schemas

Every canonical domain payload should use a registered schema version.

Priority:

```text
P0
```

Verification:

```text
CON, schema health
```

---

## API-002 - Stable Identifiers

Entities should have stable type-specific identifiers.

Priority:

```text
P1
```

Verification:

```text
UT, CON
```

---

## API-003 - Structured Errors

APIs should return stable error codes, categories, retryability, and user-action requirements.

Priority:

```text
P1
```

Verification:

```text
CON, IT
```

---

## API-004 - Optimistic Concurrency

Mutable entities should use expected entity versions.

Priority:

```text
P0
```

Verification:

```text
UT, IT
```

---

## API-005 - Idempotent Commands

Retryable state-changing commands should support idempotency keys.

Priority:

```text
P0
```

Verification:

```text
UT, IT
```

---

## API-006 - Strict Submission Idempotency

Final submission should use stricter attempt-based idempotency than normal commands.

Priority:

```text
P0
```

Verification:

```text
UT, IT, E2E
```

---

## API-007 - File Reference Contract

APIs should not accept unrestricted filesystem paths.

Priority:

```text
P0
```

Verification:

```text
CON, ST
```

---

## API-008 - Sensitive Response Policy

General APIs should return masked values and secret metadata rather than secret values.

Priority:

```text
P0
```

Verification:

```text
ST, PT
```

---

## API-009 - Event Replay and Deduplication

UI event delivery should support event IDs, sequence, reconnect, and deduplication.

Priority:

```text
P1
```

Verification:

```text
CON, IT
```

---

## API-010 - Compatibility Enforcement

Incompatible major schema versions should be rejected or migrated.

Priority:

```text
P0
```

Verification:

```text
CON, MT
```

---

# Configuration and Policy Requirements

## CFG-001 - Typed Configuration

Every supported setting should be schema-defined.

Priority:

```text
P1
```

Verification:

```text
CON, IT
```

---

## CFG-002 - Safe Defaults

High-risk capabilities should default to disabled, Manual, or Review mode.

Priority:

```text
P0
```

Verification:

```text
UT, IT
```

---

## CFG-003 - Deterministic Precedence

Configuration source precedence and merge strategies should be deterministic.

Priority:

```text
P1
```

Verification:

```text
UT, CT
```

---

## CFG-004 - Effective Policy Explanation

The platform should show why an effective decision differs from a configured preference.

Priority:

```text
P1
```

Verification:

```text
IT, UX
```

---

## CFG-005 - Protected Policies

Package or user overrides should not weaken protected safety rules.

Priority:

```text
P0
```

Verification:

```text
UT, ST
```

---

## CFG-006 - Runtime Constraints

Current health and safety conditions should override unsafe configuration.

Priority:

```text
P0
```

Verification:

```text
IT, E2E
```

---

## CFG-007 - Feature Flag Lifecycle

Feature flags should have status, owner, dependencies, risk level, and review or expiration information.

Priority:

```text
P1
```

Verification:

```text
CON, IT
```

---

## CFG-008 - Kill Switches

The platform should support disabling automatic submission, browser execution, providers, adapters, and other high-risk capabilities.

Priority:

```text
P0
```

Verification:

```text
IT, E2E
```

---

## CFG-009 - Change Impact Analysis

Material changes should identify invalidated packages, reviews, and readiness results before application.

Priority:

```text
P1
```

Verification:

```text
IT, UX
```

---

## CFG-010 - Policy Snapshot

Consequential workflows should retain the resolved configuration and policy snapshot used.

Priority:

```text
P0
```

Verification:

```text
IT, audit inspection
```

---

# Reasoning Provider Requirements

## LLM-001 - Registered Tasks

Every provider call should correspond to a registered task and prompt.

Priority:

```text
P0
```

Verification:

```text
CON, ST
```

---

## LLM-002 - Immutable Prompt Versions

Released prompt versions should be immutable and checksummed.

Priority:

```text
P1
```

Verification:

```text
registry health, CI
```

---

## LLM-003 - Task-Specific Context Builder

The platform should not send entire unrestricted packages to providers.

Priority:

```text
P0
```

Verification:

```text
PT, CT
```

---

## LLM-004 - Context Manifest

Each provider request should identify included and excluded data categories.

Priority:

```text
P0
```

Verification:

```text
CON, PT
```

---

## LLM-005 - Structured Outputs

Provider outputs should use registered structured schemas where practical.

Priority:

```text
P0
```

Verification:

```text
CON, LLM evaluation
```

---

## LLM-006 - Multi-Layer Validation

Outputs should pass schema, semantic, factual, job-identity, security, and privacy validation.

Priority:

```text
P0
```

Verification:

```text
CT, ST, PT, LLM evaluation
```

---

## LLM-007 - Bounded Repair and Retry

Repairs, retries, and fallback should be bounded and auditable.

Priority:

```text
P0
```

Verification:

```text
UT, IT
```

---

## LLM-008 - Request Idempotency

An accepted output for the same prompt, context, model, and schema should be reused safely.

Priority:

```text
P1
```

Verification:

```text
UT, IT
```

---

## LLM-009 - Budget Enforcement

Requests should be checked against task, package, queue, and aggregate budgets.

Priority:

```text
P1
```

Verification:

```text
UT, IT
```

---

## LLM-010 - No Fabricated Cost

When pricing is unavailable or stale, the platform should report tokens without claiming exact cost.

Priority:

```text
P1
```

Verification:

```text
UT, UX
```

---

## LLM-011 - Evaluated Fallback

Fallback providers or models should be used only when configured and evaluated.

Priority:

```text
P0
```

Verification:

```text
CT, LLM evaluation
```

---

## LLM-012 - No Direct Consequential Control

Provider output should not directly control browser actions, package truth, approval, or submission.

Priority:

```text
P0
```

Verification:

```text
architecture tests, ST
```

---

# End-to-End Requirements

## E2E-001 - Onboarding

The user should be able to create a validated profile, configure a provider, create a browser profile, and run a synthetic test.

Priority:

```text
P1
```

Verification:

```text
E2E
```

---

## E2E-002 - Manual Application Lifecycle

The user should be able to discover, rank, prepare, review, export, and record a manual application.

Priority:

```text
P1
```

Verification:

```text
E2E
```

---

## E2E-003 - Review-Mode Lifecycle

The platform should complete a supported form, obtain user approval, submit once, verify, and update history.

Priority:

```text
P0
```

Verification:

```text
E2E
```

---

## E2E-004 - Automatic-Mode Lifecycle

Allowlisted workflows should complete automatically only when all eligibility conditions pass.

Priority:

```text
P0
```

Verification:

```text
E2E
```

---

## E2E-005 - CAPTCHA Recovery

The platform should pause, retain context, and resume after manual CAPTCHA completion.

Priority:

```text
P0
```

Verification:

```text
E2E
```

---

## E2E-006 - Missing Legal Answer

The platform should request user input and rerun review and readiness.

Priority:

```text
P0
```

Verification:

```text
E2E
```

---

## E2E-007 - Wrong Resume Detection

The platform should detect, replace, reverify, and rereview an incorrect upload.

Priority:

```text
P0
```

Verification:

```text
E2E
```

---

## E2E-008 - Duplicate Application

A confirmed duplicate should block automatic execution and submission.

Priority:

```text
P0
```

Verification:

```text
E2E
```

---

## E2E-009 - Crash Before Submit

A browser crash before the final action should allow safe checkpoint recovery.

Priority:

```text
P0
```

Verification:

```text
E2E, RT
```

---

## E2E-010 - Crash After Submit

A browser crash after the click should start verification without another click.

Priority:

```text
P0
```

Verification:

```text
E2E, RT
```

---

## E2E-011 - Submission Unknown

Weak evidence should produce a durable Submission Unknown state.

Priority:

```text
P0
```

Verification:

```text
E2E
```

---

## E2E-012 - History Failure

A history write failure should preserve Submitted status and permit idempotent repair.

Priority:

```text
P0
```

Verification:

```text
E2E, RT
```

---

## E2E-013 - Provider Outage

Provider failure should preserve existing data and offer deterministic or Manual continuation.

Priority:

```text
P1
```

Verification:

```text
E2E
```

---

## E2E-014 - Adapter Degradation

Adapter degradation should disable new automatic submissions.

Priority:

```text
P0
```

Verification:

```text
E2E
```

---

## E2E-015 - Security Incident

Prompt injection, unknown domains, or secret exposure should stop affected workflows.

Priority:

```text
P0
```

Verification:

```text
E2E, ST
```

---

# Traceability Matrix Requirements

The project should generate a traceability report with one row per requirement.

Required fields:

```text
Requirement ID
Title
Priority
Source Documents
Owning Module
Implementation Component
Schema or API Contract
Test IDs
Acceptance Evidence
Defect References
Status
Release Gate
```

---

# Traceability Matrix Example

| Requirement | Owner            | Implementation                        | Verification               | Release Gate        |
| ----------- | ---------------- | ------------------------------------- | -------------------------- | ------------------- |
| CAND-004    | Candidate        | WorkAuthorization model and validator | UT-CAND-WA-*, E2E-014      | Real Candidate Data |
| BRW-005     | Browser/Security | Upload Policy and Playwright upload   | BT-UPLOAD-*, ST-PATH-*     | Browser Gate        |
| SUB-006     | Submission       | Attempt state machine and lock        | UT-SUB-CLICK-*, E2E-024    | Submission Safety   |
| SEC-008     | Security         | Context Filter and prompt separation  | ST-INJECTION-*, E2E-041    | Security Gate       |
| HIST-006    | History          | Idempotent sync service               | UT-HIST-IDEMP-*, RT-HIST-* | Review Release      |
| UX-002      | Frontend         | Submission-status components          | UX-STATE-*, A11Y-STATUS-*  | Review Release      |

---

# Test Identifier Convention

Recommended test ID format:

```text
<TEST-TYPE>-<DOMAIN>-<NUMBER>
```

Examples:

```text
UT-CAND-001
CON-API-004
BT-BRW-012
AT-GREENHOUSE-021
ST-SEC-007
PT-LLM-003
RT-SUB-005
E2E-SUB-011
A11Y-UX-006
```

---

# Evidence Identifier Convention

Recommended evidence ID format:

```text
EV-<RELEASE>-<NUMBER>
```

Examples:

```text
EV-LOCAL-ALPHA-001
EV-REVIEW-BETA-014
EV-AUTO-BETA-008
```

---

# Acceptance Evidence Types

Evidence may include:

* Automated test report.
* browser trace.
* sanitized screenshot.
* audit-event sequence.
* schema-validation report.
* migration report.
* backup manifest.
* restore report.
* prompt evaluation report.
* security scan.
* accessibility report.
* release-quality report.
* user-acceptance record.

Evidence should not contain real secrets or unnecessary candidate-sensitive data.

---

# Traceability Completeness Rules

Before a release:

* Every P0 requirement should have an owner.
* Every P0 requirement should have implementation evidence.
* Every P0 requirement should have an automated verification method.
* Every P0 requirement should have a passing test result.
* Every P1 requirement required by the release should be verified.
* Deferred requirements should have an explicit deferred status and reason.
* No requirement should be marked Verified based only on a code review.
* Manual evidence should not replace automation for repeatable P0 behavior.

---

# Final Safety Invariants

The following invariants are non-negotiable.

---

## INV-001 - Candidate Truth Has One Owner

Candidate facts originate from the Candidate Knowledge Base or explicit user input.

---

## INV-002 - Unknown Is Not False

Missing information cannot be silently converted into No, false, zero, or decline.

---

## INV-003 - External Content Is Untrusted

Job descriptions, application questions, pages, redirects, and provider outputs cannot override local policy.

---

## INV-004 - Provider Output Is a Proposal

No provider output is trusted before deterministic validation.

---

## INV-005 - Browser Does Not Decide Truth

The browser executes approved values but does not determine candidate answers.

---

## INV-006 - Submission Is Centralized

No component outside the Submission boundary may authorize or record the final submission.

---

## INV-007 - One Click per Attempt

The final submission control is never automatically clicked twice for one attempt.

---

## INV-008 - Evidence Defines Submission

Submitted requires verification or explicit evidence-based resolution.

---

## INV-009 - Unknown Prevents Retry

Submission Unknown prevents automatic resubmission.

---

## INV-010 - Tracking Does Not Define Submission

CSV, XLSX, or UI tracker state cannot override package submission evidence.

---

## INV-011 - Security Overrides Convenience

A preference or package override cannot weaken protected safety policy.

---

## INV-012 - Failure Preserves Evidence

Crashes and partial failures preserve attempt, package, audit, and recovery state.

---

# Global Release Blockers

A release must be rejected when any of the following exists:

* Unresolved Critical defect.
* Unresolved P0 requirement required by the release.
* Unsupported candidate claim in the critical evaluation set.
* Wrong-company reference in a critical artifact.
* Sensitive-data leakage.
* Secret in logs, prompts, exports, or diagnostics.
* Duplicate final click.
* Unverified result marked Submitted.
* Submission Unknown automatically retried.
* Wrong candidate account not blocked.
* Wrong resume not detected.
* Government ID entered automatically contrary to protected policy.
* Payment information entered into an ordinary application.
* Audit persistence unavailable during final submission.
* Submission evidence lost after crash.
* History failure triggers resubmission.
* Migration corrupts submitted records.
* Automatic mode enabled for an ineligible adapter.
* Critical accessibility barrier in the final-review or submission workflow.

---

# Development Gate Checklist

Before merging a change:

* [ ] Formatting passes.
* [ ] Linting passes.
* [ ] Type checks pass.
* [ ] Unit tests pass.
* [ ] Relevant component tests pass.
* [ ] Schemas validate.
* [ ] Generated code is current.
* [ ] No import-boundary violation exists.
* [ ] Secret scanning passes.
* [ ] No real candidate data is committed.
* [ ] New behavior has tests.
* [ ] New errors use stable codes.
* [ ] Logs follow redaction policy.
* [ ] Documentation is updated.
* [ ] Migration is included when required.
* [ ] Security implications are reviewed.
* [ ] Requirement and test IDs are linked.

---

# Component Completion Checklist

For each module:

* [ ] Responsibility is documented.
* [ ] Public interface exists.
* [ ] Owned entities are identified.
* [ ] Allowed dependencies are documented.
* [ ] Prohibited dependencies are tested.
* [ ] Inputs are schema validated.
* [ ] Outputs are schema validated.
* [ ] Error behavior is defined.
* [ ] Idempotency is tested where applicable.
* [ ] Concurrency behavior is tested.
* [ ] Sensitive-data behavior is tested.
* [ ] Audit events are tested.
* [ ] Recovery behavior is tested.
* [ ] Synthetic fixtures exist.
* [ ] Completion criteria from the source specification pass.

---

# Candidate Data Gate

Required before using real candidate data:

* [ ] Candidate schema active.
* [ ] Candidate source imports validated.
* [ ] Conflict resolution works.
* [ ] Work-authorization fields are separate.
* [ ] Candidate snapshots work.
* [ ] Sensitive values are masked.
* [ ] File-access restrictions pass.
* [ ] Path-traversal tests pass.
* [ ] Candidate data is excluded from source control.
* [ ] Candidate data is excluded from unauthorized provider contexts.
* [ ] Candidate update audit events work.
* [ ] Backup includes candidate data safely.
* [ ] Deletion behavior is documented.

---

# Preparation Gate

Required before releasing package preparation:

* [ ] Job identity is validated.
* [ ] Candidate snapshot is captured.
* [ ] Job snapshot is captured.
* [ ] Package manifest validates.
* [ ] Base resume selection works.
* [ ] Tailored resume passes factual validation.
* [ ] Cover-letter company and role validation passes.
* [ ] Standard answers resolve correctly.
* [ ] Missing and ambiguous answers are explicit.
* [ ] Narrative answers have source support.
* [ ] Artifact hashes are stored.
* [ ] Artifact versions are stored.
* [ ] User edits are preserved.
* [ ] Preparation Review passes.
* [ ] Preparation Readiness passes.
* [ ] Package can reopen without regeneration.
* [ ] Package staleness is detected.

---

# Manual Application Release Checklist

Required for Local Alpha:

* [ ] Candidate onboarding works.
* [ ] Direct job import works.
* [ ] Job ranking is explainable.
* [ ] Package preparation works.
* [ ] Resume and cover-letter preview works.
* [ ] Answer checklist works.
* [ ] Manual application URL is available.
* [ ] Manual submission can be recorded.
* [ ] Manual record is identified as user-reported.
* [ ] CSV history works.
* [ ] XLSX history works.
* [ ] Package export works.
* [ ] Sensitive information remains masked.
* [ ] Backup works.
* [ ] Restore of manual-stage data works.
* [ ] No browser submission capability is accidentally enabled.

---

# Browser Gate Checklist

Required before real browser form completion:

* [ ] Playwright runtime is pinned and validated.
* [ ] Dedicated browser profile works.
* [ ] Browser profile lock works.
* [ ] Visible browser launches.
* [ ] Local one-page fixture passes.
* [ ] Local multi-page fixture passes.
* [ ] Text entry verifies.
* [ ] Dropdown selection verifies.
* [ ] Radio selection verifies.
* [ ] Checkbox selection verifies.
* [ ] Date entry verifies.
* [ ] Resume upload verifies.
* [ ] Conditional fields are reinspected.
* [ ] Repeating sections work.
* [ ] Validation messages map to fields.
* [ ] CAPTCHA pauses.
* [ ] MFA pauses.
* [ ] Login pauses.
* [ ] Wrong-account detection works.
* [ ] Unexpected-domain protection works.
* [ ] Browser crash recovery works.
* [ ] Final submission remains disabled or simulated.

---

# ATS Adapter Gate Checklist

For each adapter:

* [ ] Adapter ID and version registered.
* [ ] Supported domains declared.
* [ ] Capabilities declared.
* [ ] Unsupported controls declared.
* [ ] ATS detection passes.
* [ ] Page signatures pass.
* [ ] Job identity remains correct.
* [ ] Resume upload passes.
* [ ] Employment entry passes.
* [ ] Education entry passes.
* [ ] Custom questions pass.
* [ ] Review-page extraction passes.
* [ ] Final-control classification passes.
* [ ] Confirmation signals pass.
* [ ] Browser-version compatibility is documented.
* [ ] Regression fixture suite passes.
* [ ] Crash recovery passes.
* [ ] Security tests pass.
* [ ] Privacy tests pass.
* [ ] Automatic eligibility status is explicit.
* [ ] Known limitations are documented.

---

# Queue and Orchestration Gate Checklist

* [ ] Ready packages are admitted.
* [ ] Unready packages are rejected.
* [ ] Duplicate queue entries are blocked.
* [ ] Queue ordering is stable.
* [ ] Package locks work.
* [ ] Browser-profile lock works.
* [ ] Workflow stages persist.
* [ ] Page checkpoints persist.
* [ ] Pause works.
* [ ] Resume works.
* [ ] Safe cancellation works.
* [ ] Current-package failure isolation works.
* [ ] User intervention works.
* [ ] Application restart recovery works.
* [ ] Stale locks are handled safely.
* [ ] Final-action stage cannot be cancelled ambiguously.
* [ ] Queue event replay works.
* [ ] Queue UI reflects backend state.

---

# Submission Safety Gate Checklist

Required before any platform-controlled real submission:

* [ ] Final-review snapshot exists.
* [ ] Review approval is current when required.
* [ ] Submission readiness passes.
* [ ] Correct job identity verified.
* [ ] Correct candidate account verified.
* [ ] Correct resume verified.
* [ ] Required answers verified.
* [ ] Duplicate check current.
* [ ] Audit storage writable.
* [ ] Package storage writable.
* [ ] Sufficient disk space available.
* [ ] Submission lock acquired.
* [ ] Attempt record durable before click.
* [ ] Attempt ID unique.
* [ ] Idempotency key unique.
* [ ] Final control unambiguous.
* [ ] Final click count test passes.
* [ ] Strong evidence verification works.
* [ ] Submission Unknown works.
* [ ] Unknown state survives restart.
* [ ] Unknown state blocks retry.
* [ ] Dashboard reconciliation works where supported.
* [ ] Tracker failure does not alter submission truth.
* [ ] Confirmation evidence is retained.
* [ ] Locks release only at safe boundaries.

---

# Stable Review Release Checklist

Required before Stable Review mode:

* [ ] Manual Application Release gate passes.
* [ ] Browser Gate passes.
* [ ] At least one adapter reaches Stable Review status.
* [ ] Queue Gate passes.
* [ ] Submission Safety Gate passes.
* [ ] Review UI passes usability testing.
* [ ] Approval is bound to exact versions.
* [ ] CAPTCHA intervention passes.
* [ ] MFA intervention passes.
* [ ] Missing legal-answer flow passes.
* [ ] Wrong resume flow passes.
* [ ] Duplicate application flow passes.
* [ ] Crash before submit passes.
* [ ] Crash after submit passes.
* [ ] Submission Unknown passes.
* [ ] History failure recovery passes.
* [ ] Audit integrity passes.
* [ ] Backup and restore pass.
* [ ] Upgrade and rollback pass.
* [ ] Security Gate passes.
* [ ] Privacy Gate passes.
* [ ] Accessibility Gate passes.
* [ ] No Critical or High submission-safety defect remains.

---

# Security Gate Checklist

* [ ] Threat model reviewed.
* [ ] Data classification implemented.
* [ ] Secret Store implemented.
* [ ] Plaintext-secret validation passes.
* [ ] Provider context filter passes.
* [ ] Prompt-injection suite passes.
* [ ] Output security scan passes.
* [ ] File-reference policy passes.
* [ ] Path-traversal suite passes.
* [ ] Symbolic-link restrictions pass.
* [ ] Upload manifest enforcement passes.
* [ ] MIME and signature validation pass.
* [ ] Unknown-domain tests pass.
* [ ] HTTPS enforcement passes.
* [ ] Browser-profile isolation passes.
* [ ] Wrong-account protection passes.
* [ ] Government-ID policy passes.
* [ ] Payment-request blocking passes.
* [ ] Local API CSRF tests pass.
* [ ] Origin and host validation pass.
* [ ] Log redaction passes.
* [ ] Diagnostic sanitization passes.
* [ ] Audit integrity tests pass.
* [ ] Incident-response runbooks are tested.

---

# Privacy Gate Checklist

* [ ] Minimum necessary data policy implemented.
* [ ] Candidate purpose-specific views implemented.
* [ ] Demographic values excluded from unrelated prompts.
* [ ] Disability values excluded from unrelated prompts.
* [ ] Veteran values excluded from unrelated prompts.
* [ ] Government identifiers excluded from providers.
* [ ] Credentials excluded from providers.
* [ ] Contact information minimized.
* [ ] Full prompts are not logged by default.
* [ ] Full responses are not logged by default.
* [ ] Sensitive UI values are masked.
* [ ] Screenshot retention is configurable.
* [ ] Raw HTML retention is disabled by default.
* [ ] Export manifests show included categories.
* [ ] Secret and browser-profile exports are excluded.
* [ ] Data-deletion scopes work.
* [ ] Retention rules are enforced.
* [ ] Backup exclusions are correct.
* [ ] Decommissioning limitations are documented.

---

# Prompt and Provider Gate Checklist

For each active prompt:

* [ ] Prompt ID registered.
* [ ] Owner identified.
* [ ] Version immutable.
* [ ] Checksum recorded.
* [ ] Input schema registered.
* [ ] Output schema registered.
* [ ] Allowed context categories defined.
* [ ] Prohibited context categories defined.
* [ ] Context builder tested.
* [ ] Token budget defined.
* [ ] Retry policy defined.
* [ ] Repair limit defined.
* [ ] Cache policy defined.
* [ ] Fallback policy defined.
* [ ] Evaluation suite passes.
* [ ] Prompt-injection tests pass.
* [ ] Critical factual-error count is zero.
* [ ] Wrong-company count is zero.
* [ ] Sensitive-data leakage count is zero.
* [ ] Source-reference validation passes.
* [ ] Model compatibility recorded.
* [ ] Usage accounting works.

For each provider:

* [ ] Secret reference works.
* [ ] Health check works.
* [ ] Selected models are accessible.
* [ ] Structured output works.
* [ ] Token usage parses.
* [ ] Error classification works.
* [ ] Timeout works.
* [ ] Retry works.
* [ ] Cancellation works where supported.
* [ ] Fallback behavior passes.
* [ ] No provider-specific objects leak into domain code.

---

# Operations Gate Checklist

* [ ] Fresh installation passes.
* [ ] Repeated installation passes.
* [ ] Unsupported runtime fails clearly.
* [ ] Data root initializes.
* [ ] Directory permissions validate.
* [ ] Configuration validates.
* [ ] Secret references validate.
* [ ] Browser installation validates.
* [ ] Startup recovery runs.
* [ ] Graceful shutdown passes.
* [ ] Safe mode passes.
* [ ] Maintenance mode passes.
* [ ] Full health check passes.
* [ ] Backup creation passes.
* [ ] Backup encryption passes.
* [ ] Backup verification passes.
* [ ] Restore to empty data root passes.
* [ ] Partial restore passes.
* [ ] Restore conflicts are handled.
* [ ] Configuration migration passes.
* [ ] Package migration passes.
* [ ] Failed migration rollback passes.
* [ ] Upgrade passes.
* [ ] Rollback passes.
* [ ] Low disk handling passes.
* [ ] History rebuild passes.
* [ ] Package validation passes.
* [ ] Stale-lock repair passes.
* [ ] Diagnostic bundle sanitization passes.
* [ ] Complete removal behavior is tested.

---

# Accessibility Gate Checklist

* [ ] Main navigation is keyboard accessible.
* [ ] Onboarding is keyboard accessible.
* [ ] Job selection is keyboard accessible.
* [ ] Package review is keyboard accessible.
* [ ] Queue controls are keyboard accessible.
* [ ] CAPTCHA instructions are accessible.
* [ ] Missing-answer forms are accessible.
* [ ] Final-review dialog is accessible.
* [ ] Final-submit action is accessible.
* [ ] Submission Unknown is announced.
* [ ] Status is not conveyed by color alone.
* [ ] Focus is visible.
* [ ] Focus order is logical.
* [ ] Dialog focus is managed.
* [ ] Form errors associate with fields.
* [ ] Tables expose headers.
* [ ] Sensitive reveal controls have descriptive names.
* [ ] Text remains usable at 200% zoom.
* [ ] Reduced-motion preference is respected.
* [ ] Screen-reader testing covers critical workflows.

---

# Limited Automatic Beta Checklist

Required in addition to Stable Review:

* [ ] User explicitly enables automatic submission.
* [ ] Automatic Submission feature flag eligible.
* [ ] Automatic Submission quality gate passed.
* [ ] Global kill switch works.
* [ ] Adapter-specific kill switch works.
* [ ] At least one Stable adapter is allowlisted.
* [ ] Workflow variant is allowlisted.
* [ ] Candidate profile is validated.
* [ ] Browser account identity is verified.
* [ ] Strong confirmation is supported.
* [ ] Generic fallback automatically downgrades.
* [ ] Unknown required field automatically downgrades.
* [ ] Legal or sensitive ambiguity automatically downgrades.
* [ ] Adapter degradation automatically downgrades.
* [ ] Provider fallback follows review policy.
* [ ] Package warnings obey automatic eligibility policy.
* [ ] Daily application limits work.
* [ ] Company limits work.
* [ ] Automatic attempt audit is complete.
* [ ] Automatic-mode metrics are available.
* [ ] Incident runbook passes.
* [ ] Zero duplicate click failures.
* [ ] Zero unsupported critical claims.
* [ ] Zero sensitive-data leaks.
* [ ] Zero false verified submissions.

---

# Stable Automatic Release Checklist

Required in addition to Limited Automatic Beta:

* [ ] Pilot success criteria pass.
* [ ] Automatic workflow success rate meets approved target.
* [ ] Verification rate meets approved target.
* [ ] Unknown-submission rate is understood and safely handled.
* [ ] Automatic downgrade behavior is reliable.
* [ ] No unresolved Critical defects.
* [ ] No unresolved High safety defects.
* [ ] Adapter maintenance process is operational.
* [ ] Prompt and model change process is operational.
* [ ] Release rollback is tested.
* [ ] Security incident response is tested.
* [ ] User can disable all automatic submissions immediately.
* [ ] Historical audit evidence is complete.
* [ ] Known limitations are enforced, not merely documented.
* [ ] Final production approval is recorded.

---

# End-to-End Reference Scenario Checklist

Before Stable Review:

* [ ] E2E-001 First-Time Onboarding.
* [ ] E2E-002 Candidate Conflict Resolution.
* [ ] E2E-003 Direct Job URL Intake.
* [ ] E2E-004 Batch Job Discovery.
* [ ] E2E-005 Package Preparation.
* [ ] E2E-006 Preparation Review and Readiness.
* [ ] E2E-007 Manual Handoff.
* [ ] E2E-008 Queue Admission.
* [ ] E2E-009 Review-Mode Browser Application.
* [ ] E2E-011 CAPTCHA Intervention.
* [ ] E2E-012 Login and MFA.
* [ ] E2E-013 Wrong Account.
* [ ] E2E-014 Missing Legal Answer.
* [ ] E2E-015 Ambiguous Sponsorship Question.
* [ ] E2E-016 External Assessment.
* [ ] E2E-017 Duplicate Application.
* [ ] E2E-018 Wrong Resume.
* [ ] E2E-019 ATS Parsing Error.
* [ ] E2E-020 Unsupported Widget.
* [ ] E2E-022 Generic Form Fallback.
* [ ] E2E-023 Crash Before Submission.
* [ ] E2E-024 Crash After Submission.
* [ ] E2E-025 Strong Submission Confirmation.
* [ ] E2E-026 Submission Unknown.
* [ ] E2E-027 Unknown Resolved as Submitted.
* [ ] E2E-028 Failure Before Click.
* [ ] E2E-029 Application Closed.
* [ ] E2E-030 Provider Outage.
* [ ] E2E-031 Unsupported Provider Claim.
* [ ] E2E-032 Reasoning Budget Exhausted.
* [ ] E2E-033 Configuration Invalidation.
* [ ] E2E-034 Active Workflow Configuration Change.
* [ ] E2E-036 Low Disk Before Submission.
* [ ] E2E-037 CSV Failure After Submission.
* [ ] E2E-038 XLSX Rebuild.
* [ ] E2E-039 Mixed-Outcome Queue.
* [ ] E2E-040 Queue Restart Recovery.
* [ ] E2E-041 Prompt Injection.
* [ ] E2E-042 Unknown Domain Redirect.
* [ ] E2E-043 Secure Backup Before Upgrade.
* [ ] E2E-044 Restore.
* [ ] E2E-045 Migration Failure.
* [ ] E2E-046 Audit Integrity Failure.
* [ ] E2E-047 Secret Exposure.
* [ ] E2E-048 Recruitment Status Update.
* [ ] E2E-049 Package Archive.
* [ ] E2E-050 Complete Local Data Deletion.

Before Automatic Beta:

* [ ] E2E-010 Automatic Supported Application.
* [ ] E2E-021 ATS Adapter Degradation.
* [ ] E2E-035 Automatic Submission Kill Switch.

---

# Performance Acceptance Checklist

The platform should be tested with representative local workloads.

* [ ] Jobs list remains usable with at least 1,000 jobs.
* [ ] Application list remains usable with at least 100 active packages.
* [ ] History remains usable with at least 1,000 records.
* [ ] Large audit timelines load incrementally.
* [ ] Queue events do not freeze the interface.
* [ ] Package validation completes within acceptable local limits.
* [ ] History rebuild completes without excessive memory use.
* [ ] Cache size remains bounded.
* [ ] Logs and screenshots remain within retention limits.
* [ ] Browser concurrency remains within configured safe limits.
* [ ] Provider requests respect timeouts and budgets.
* [ ] Startup health checks do not mutate workflow truth.

Exact performance targets should be recorded in the release-quality report for each supported platform.

---

# Supported Environment Acceptance

For every supported operating system:

* [ ] Supported runtime installs.
* [ ] Dependency lock resolves.
* [ ] Secret Store works.
* [ ] Browser installs.
* [ ] Browser launches.
* [ ] PDF generation works.
* [ ] DOCX generation works.
* [ ] CSV history works.
* [ ] XLSX history works.
* [ ] Local UI starts securely.
* [ ] File permissions behave as expected.
* [ ] Backup works.
* [ ] Restore works.
* [ ] Upgrade works.
* [ ] Uninstall or decommission works.

A platform should not be listed as supported until this checklist passes.

---

# Documentation Acceptance Checklist

* [ ] Master document registry exists.
* [ ] Every specification has an owner.
* [ ] Every specification has a version.
* [ ] Every specification has a status.
* [ ] Architecture overview is current.
* [ ] Module catalog is current.
* [ ] API reference is generated.
* [ ] Schema reference is generated.
* [ ] Prompt registry documentation is current.
* [ ] Installation guide is current.
* [ ] Candidate setup guide is current.
* [ ] Job intake guide is current.
* [ ] Package preparation guide is current.
* [ ] Browser operation guide is current.
* [ ] Review-mode guide is current.
* [ ] Automatic-mode guide is current.
* [ ] Submission Unknown guide is current.
* [ ] Security and privacy guide is current.
* [ ] Backup and restore guide is current.
* [ ] Troubleshooting guide is current.
* [ ] Known limitations are current.
* [ ] Release notes are complete.
* [ ] Deferred capabilities are recorded.
* [ ] Requirement-to-test report is generated.

---

# Known-Limitations Register

Every release should include a known-limitations register.

Required fields:

```text
Limitation ID
Description
Affected Capability
Affected ATS or Environment
Risk Level
Enforced Mitigation
User-Visible Behavior
Planned Resolution
Status
```

---

# Limitation Rules

A limitation is acceptable only when:

* It does not violate a protected invariant.
* It is visible to the user.
* It is enforced in code or policy.
* It has a safe fallback.
* It is documented in release notes.

Example:

```text
Limitation:
Workday adapter supports Review mode only.

Enforcement:
Automatic mode eligibility is disabled for Workday.

Fallback:
User review or Manual mode.
```

A limitation is not acceptable when it merely documents unsafe behavior without preventing it.

---

# Deferred Capabilities

The following may remain deferred beyond the MVP:

* Mobile-native interface.
* Public cloud hosting.
* multi-user accounts.
* enterprise identity management.
* large-scale browser concurrency.
* automatic CAPTCHA solving.
* automatic MFA.
* automated coding assessments.
* automated personality assessments.
* automated video interviews.
* automated background checks.
* government-ID automation.
* payment-information automation.
* unrestricted third-party plugins.
* automatic email sending.
* automatic recruiter outreach.
* cloud synchronization.
* advanced analytics warehouse.
* public third-party API.

Deferred capabilities should be represented as:

```text
deferred
```

not silently omitted from planning.

---

# Risk Acceptance Record

Any accepted residual risk should contain:

* Risk ID.
* description.
* affected requirement.
* severity.
* probability.
* mitigation.
* detection.
* owner.
* expiry or review date.
* approving authority.

No risk acceptance may override a protected invariant.

---

# Defect Severity

## Critical

May cause:

* False candidate information.
* sensitive-data disclosure.
* duplicate application submission.
* false Submitted status.
* wrong job submission.
* wrong candidate account usage.
* unrecoverable submission ambiguity.
* secret compromise.

Critical defects block all affected releases.

---

## High

May cause:

* Major workflow corruption.
* inability to recover.
* significant privacy exposure.
* incorrect required answer.
* audit-integrity loss.
* broad adapter instability.

High defects block affected production modes.

---

## Medium

May cause:

* Recoverable workflow failure.
* incomplete optional feature.
* misleading non-critical UI.
* degraded performance.

May be accepted only with documented limitation and safe behavior.

---

## Low

Minor usability, presentation, or non-consequential issue.

May be accepted with normal backlog tracking.

---

# Release Quality Report

Every release candidate should produce a report containing:

* Release version.
* build ID.
* source revision.
* release channel.
* supported platforms.
* supported ATS adapters.
* adapter stability.
* feature-flag status.
* schema versions.
* prompt versions.
* provider models.
* migrations.
* total requirements.
* verified requirements.
* deferred requirements.
* failed requirements.
* unit-test results.
* component-test results.
* integration-test results.
* browser-test results.
* ATS regression results.
* end-to-end results.
* security scan.
* privacy test result.
* accessibility result.
* prompt evaluation.
* migration result.
* backup and restore result.
* known limitations.
* unresolved defects.
* release decision.

---

# Release Decision Values

```text
approved
approved_with_enforced_limitations
rejected
```

---

# Approved with Enforced Limitations

Examples:

* Automatic mode disabled for a Beta adapter.
* Generic Form Engine restricted to Review mode.
* Provider fallback disabled for sensitive tasks.
* One operating system not yet supported.
* Dashboard reconciliation unavailable for one ATS.

Every limitation must be enforced through configuration, policy, feature eligibility, or code.

---

# Release Approval Record

```json
{
  "release_version": "1.0.0",
  "decision": "approved_with_enforced_limitations",
  "approved_modes": [
    "manual",
    "review"
  ],
  "automatic_mode_approved": false,
  "supported_adapters": [
    {
      "adapter_id": "greenhouse",
      "status": "stable_review"
    }
  ],
  "known_limitation_ids": [],
  "quality_report_id": "",
  "approved_by": [],
  "approved_at": ""
}
```

---

# Final Product Acceptance Checklist

## Architecture

* [ ] Local-first deployment confirmed.
* [ ] Modular monorepo implemented.
* [ ] Domain ownership enforced.
* [ ] No circular dependency remains.
* [ ] Submission boundary centralized.
* [ ] Security boundary centralized.
* [ ] Canonical schemas active.
* [ ] Runtime data separated from source.

## Candidate Truth

* [ ] Candidate profile validated.
* [ ] Sources and conflicts handled.
* [ ] Work authorization modeled correctly.
* [ ] Sensitive values protected.
* [ ] Candidate snapshots reproducible.
* [ ] Candidate changes invalidate dependents correctly.

## Job Truth

* [ ] Job identity reliable.
* [ ] Source and hashes preserved.
* [ ] Unknown fields remain unknown.
* [ ] Ranking is explainable.
* [ ] Hard rules are deterministic.
* [ ] Malicious job text is contained.

## Package Integrity

* [ ] Package manifest validates.
* [ ] Snapshots immutable.
* [ ] Artifacts versioned.
* [ ] Artifacts hashed.
* [ ] Staleness detected.
* [ ] Package locks work.
* [ ] Submitted state preserved.

## Generated Content

* [ ] Resume facts validated.
* [ ] Unsupported claims blocked.
* [ ] Cover-letter identity validated.
* [ ] Narrative answers source-supported.
* [ ] User edits preserved.
* [ ] Wrong-company contamination blocked.
* [ ] Prompt evaluations pass.

## Application Answers

* [ ] Standard answers deterministic.
* [ ] Missing is not treated as No.
* [ ] Legal answers are not inferred.
* [ ] Demographics are not inferred.
* [ ] Compound questions are handled.
* [ ] Sensitive answers are protected.
* [ ] Answer provenance is complete.

## Review and Readiness

* [ ] Preparation Review passes.
* [ ] Browser Review passes.
* [ ] Blocking findings stop progression.
* [ ] Safe corrections are bounded.
* [ ] Approval is version-bound.
* [ ] Material changes invalidate approval.
* [ ] Readiness uses current state.
* [ ] Next allowed actions are authoritative.

## Browser and ATS

* [ ] Dedicated profile used.
* [ ] Account identity verified.
* [ ] Browser actions verified.
* [ ] Uploads authorized and verified.
* [ ] CAPTCHA and MFA remain manual.
* [ ] Unknown domains pause.
* [ ] Generic fallback is safe.
* [ ] Supported adapter regressions pass.
* [ ] Unsupported controls downgrade safely.

## Queue and Recovery

* [ ] Queue admission works.
* [ ] Workflow state is durable.
* [ ] Checkpoints work.
* [ ] Pause and resume work.
* [ ] User interventions work.
* [ ] Browser crash recovery works.
* [ ] Application restart recovery works.
* [ ] Mixed outcomes remain distinct.

## Submission

* [ ] Duplicate check current.
* [ ] Submission readiness passes.
* [ ] Submission lock works.
* [ ] Attempt record precedes click.
* [ ] Final click is executed once.
* [ ] Strong evidence verifies success.
* [ ] Weak evidence becomes Unknown.
* [ ] Unknown prevents retry.
* [ ] Unknown resolution is audited.
* [ ] Failure-before-click is distinct.
* [ ] History failure cannot resubmit.

## History and Audit

* [ ] Canonical record exists.
* [ ] Submission and recruitment statuses are separate.
* [ ] CSV synchronization works.
* [ ] XLSX synchronization works.
* [ ] Writes are idempotent.
* [ ] Rebuild works.
* [ ] Audit events are complete.
* [ ] Audit integrity validates.
* [ ] Diagnostics are sanitized.

## Security and Privacy

* [ ] Secret Store active.
* [ ] Plaintext secrets rejected.
* [ ] File references protected.
* [ ] Path traversal blocked.
* [ ] Prompt injection blocked.
* [ ] Provider context minimized.
* [ ] Sensitive data not leaked.
* [ ] Government-ID policy enforced.
* [ ] Payment requests blocked.
* [ ] Local API protected.
* [ ] Browser profiles protected.
* [ ] Retention enforced.
* [ ] Deletion scopes work.

## Configuration

* [ ] Safe defaults loaded.
* [ ] Configuration schema validates.
* [ ] Precedence works.
* [ ] Effective values explainable.
* [ ] Protected policies immutable.
* [ ] Feature dependencies enforced.
* [ ] Kill switches work.
* [ ] Runtime constraints work.
* [ ] Material-change impact analysis works.
* [ ] Policy snapshots retained.

## Provider and Cost Controls

* [ ] Prompts registered.
* [ ] Models registered.
* [ ] Context builders purpose-specific.
* [ ] Output schemas validate.
* [ ] Fact validation works.
* [ ] Repairs are bounded.
* [ ] Retries are bounded.
* [ ] Fallback is evaluated.
* [ ] Caching is isolated.
* [ ] Usage is tracked.
* [ ] Budgets are enforced.
* [ ] Pricing uncertainty is honest.
* [ ] Provider outages degrade safely.

## Operations

* [ ] Installation passes.
* [ ] Startup health passes.
* [ ] Safe mode works.
* [ ] Maintenance mode works.
* [ ] Backup verifies.
* [ ] Restore passes.
* [ ] Migration passes.
* [ ] Migration rollback passes.
* [ ] Upgrade passes.
* [ ] Upgrade rollback passes.
* [ ] Low disk blocks unsafe action.
* [ ] Decommissioning works.

## User Experience

* [ ] Onboarding is understandable.
* [ ] Dashboard shows priorities.
* [ ] Jobs and packages are searchable.
* [ ] Required actions are prominent.
* [ ] Final submission is explicit.
* [ ] Submission Unknown is distinct.
* [ ] Sensitive values are masked.
* [ ] Error messages are actionable.
* [ ] Recovery paths are clear.
* [ ] Critical workflows are accessible.

---

# Final MVP Acceptance

The MVP should be accepted when the user can:

1. Install the application locally.
2. Create and validate a candidate profile.
3. Import and rank jobs.
4. Select jobs.
5. Create Application Packages.
6. Prepare truthful resumes and cover letters.
7. Prepare application answers.
8. review package consistency.
9. confirm readiness.
10. use a manual application handoff.
11. complete supported applications in Review mode.
12. resolve CAPTCHA, MFA, and missing-answer interventions.
13. approve an exact final application.
14. submit once.
15. verify success or preserve Submission Unknown.
16. track the application in CSV and XLSX.
17. recover interrupted workflows.
18. inspect audit and health information.
19. back up and restore local data.
20. manage privacy and security settings.

---

# Final Stable Review Acceptance

Stable Review mode should be accepted when:

* The MVP acceptance checklist passes.
* At least one ATS adapter is Stable for Review mode.
* Mandatory user approval is reliable.
* Submission verification is reliable.
* Submission Unknown protection is proven.
* Duplicate prevention is proven.
* Browser crashes are recoverable.
* Tracker failures are recoverable.
* Security and privacy gates pass.
* Accessibility gate passes.
* Upgrade and rollback pass.
* No Critical or High submission-safety defect remains.

---

# Final Automatic-Mode Acceptance

Automatic mode should be accepted only when:

* Stable Review mode is already approved.
* The user explicitly enables Automatic mode.
* A Stable adapter and workflow variant are allowlisted.
* All required package facts have sources.
* No disqualifying review finding exists.
* No prohibited sensitive field exists.
* Candidate and job identity are verified.
* Browser account identity is verified.
* Strong confirmation is supported.
* Final action confidence is sufficient.
* Attempt durability is proven.
* Single-click behavior is proven.
* Submission Unknown behavior is proven.
* Kill switches are proven.
* Automatic downgrade is proven.
* Incident response is proven.
* Quality targets are met across the controlled pilot.
* No unresolved safety blocker remains.

---

# Final Approval Questions

Before approving any production-use mode, reviewers should answer:

```text
Does the platform use only truthful candidate facts?

Can every consequential answer be traced to a source?

Can malicious external content influence protected behavior?

Can the wrong resume be uploaded without detection?

Can the wrong job be submitted?

Can the wrong candidate account be used?

Can final Submit be clicked twice?

Can an uncertain outcome be retried automatically?

Can a tracker failure alter submission truth?

Can a provider response authorize an irreversible action?

Can secrets appear in prompts or logs?

Can the system recover safely after a crash?

Can the user understand whether an application was submitted?

Can the user disable automatic behavior immediately?

Can the release be backed up, upgraded, rolled back, and restored?
```

Any unsafe or unknown answer should block the affected release mode.

---

# Final Sign-Off Template

```text
Release Version:
Build Identifier:
Release Channel:

Approved Modes:
[ ] Manual
[ ] Review
[ ] Limited Automatic
[ ] Stable Automatic

Supported Operating Systems:

Supported ATS Adapters:

Approved Prompt Registry Version:

Approved Schema Registry Version:

Quality Report ID:

Security Review ID:

Privacy Review ID:

Accessibility Review ID:

Migration Report ID:

Backup and Restore Evidence ID:

Known Limitations:

Deferred Capabilities:

Open Medium or Low Defects:

Release Decision:
[ ] Approved
[ ] Approved with Enforced Limitations
[ ] Rejected

Approvers:

Approval Date:
```

---

# Definition of Specification-Suite Completion

The specification suite is complete when:

* All documents are registered.
* Titles and filenames are authoritative.
* Versions and statuses are recorded.
* Owners are identified.
* Dependencies are recorded.
* Requirements have stable IDs.
* P0 and P1 requirements have verification methods.
* release gates are defined.
* acceptance checklists are complete.
* safety invariants are explicit.
* known limitations have enforcement.
* deferred capabilities are visible.
* final sign-off is defined.

---

# Definition of Implementation Completion

Implementation is complete when:

* Required code exists.
* architecture boundaries are enforced.
* schemas and APIs are generated and validated.
* migrations exist.
* tests pass.
* security and privacy controls pass.
* operational recovery passes.
* accessibility passes.
* documentation is current.
* traceability report is complete.
* release evidence exists.

---

# Definition of Verification Completion

Verification is complete when:

* Every required P0 requirement has passing evidence.
* Every release-required P1 requirement has passing evidence.
* critical end-to-end scenarios pass.
* no global release blocker remains.
* all accepted limitations are enforced.
* quality reports are reproducible.
* evidence uses synthetic or sanitized data.
* evidence is retained according to policy.

---

# Definition of Final Platform Acceptance

The platform is finally accepted when it can demonstrate, repeatedly and safely, that it:

* Understands the candidate accurately.
* understands the job accurately.
* creates truthful application materials.
* resolves answers consistently.
* identifies uncertainty.
* protects sensitive information.
* fills supported application forms accurately.
* stops on unsupported or ambiguous behavior.
* obtains user input when required.
* submits only through a controlled boundary.
* clicks the final control no more than once.
* verifies the outcome honestly.
* preserves uncertainty rather than guessing.
* prevents duplicate applications.
* maintains reliable application history.
* recovers from failures.
* explains its behavior.
* remains maintainable over time.

---

# Final Summary

The complete specification suite defines a local-first application platform that progresses through:

```text
Candidate Truth
    |
    v
Job Truth
    |
    v
Application Package
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
Final Submission
    |
    v
Verification
    |
    v
Application History
```

The master traceability system connects:

```text
Requirement
    |
    v
Owning Specification
    |
    v
Owning Module
    |
    v
Implementation
    |
    v
Test
    |
    v
Evidence
    |
    v
Release Decision
```

The final acceptance rule is:

```text
The platform is not ready because it can submit an application.

It is ready only when it can submit the correct application,
with truthful information,
through a controlled action,
verify the result,
recover from uncertainty,
and prove what happened.
```
