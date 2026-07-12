# 16 - API Contracts, Data Models, and Schema Registry

## LLM-Powered Autonomous Job Search & Application Platform

Version: 1.0

---

# Purpose

This document defines the API contracts, canonical data models, schema registry, validation rules, versioning strategy, compatibility requirements, and serialization standards for the LLM-Powered Autonomous Job Search and Application Platform.

The platform contains multiple cooperating components, including:

* Candidate Knowledge Base services.
* Job discovery and normalization.
* Job ranking.
* Application Package management.
* Resume tailoring.
* Cover-letter generation.
* Application-answer preparation.
* Application Review.
* Application Readiness.
* Queue orchestration.
* Browser automation.
* ATS adapters.
* Generic form processing.
* Submission verification.
* Application history.
* Logging and auditing.
* Security and privacy services.
* Local user interface.
* Maintenance and recovery tools.

These components should communicate through explicit, versioned, validated contracts.

No service should depend on undocumented dictionaries, arbitrary file layouts, loosely structured model responses, or implicit assumptions about another component's internal representation.

---

# Core Principle

Every service boundary should use a documented and validated contract.

```text
Producer
    |
    v
Versioned Schema
    |
    v
Validation
    |
    +--> Accepted
    |
    +--> Rejected with Structured Error
    |
    v
Consumer
```

A payload should not become trusted merely because it was produced by another internal component.

All inbound data should be validated at the receiving boundary.

---

# Objectives

The API and schema architecture should:

* Define canonical platform entities.
* Standardize field names and types.
* Separate internal identifiers from external identifiers.
* Support local API access for the user interface.
* Support service-to-service communication.
* Validate reasoning-provider outputs.
* Normalize ATS and browser data.
* Preserve source provenance.
* Support sensitive-field policies.
* Support schema evolution.
* Maintain backward compatibility where practical.
* Reject incompatible payloads clearly.
* Support migrations.
* Support idempotent operations.
* Support optimistic concurrency.
* Support auditability.
* Support partial and paginated responses.
* Support structured errors.
* Prevent arbitrary filesystem access through API payloads.
* Prevent clients from bypassing workflow-state rules.
* Keep backend state authoritative.

---

# Scope

This document covers:

* API architecture.
* Local API conventions.
* Service contracts.
* Canonical data models.
* Identifiers.
* Enumerations.
* Request and response envelopes.
* Error contracts.
* Pagination.
* Filtering.
* Sorting.
* Idempotency.
* Concurrency control.
* Schema registry.
* Schema versions.
* Compatibility.
* Validation.
* Serialization.
* Event schemas.
* File-reference contracts.
* Sensitive-data annotations.
* Provider-output schemas.
* Browser and ATS schemas.
* History schemas.
* Migration rules.
* Contract testing.
* Schema governance.

This document does not mandate:

* A specific web framework.
* A specific programming language for every future service.
* A distributed microservice deployment.
* A public external API.
* Remote multi-user hosting.
* A relational database for the MVP.

---

# API Architecture

The MVP may use a modular local application with:

* One local backend process.
* One local user interface.
* Internal service interfaces.
* A local HTTP or IPC API.
* Local file-based persistence.
* External clients for reasoning providers and ATS websites.

The API contract architecture should remain usable if the system later becomes more distributed.

---

# Logical API Layers

```text
Local User Interface API
        |
        v
Application Service Layer
        |
        +-- Candidate API
        +-- Jobs API
        +-- Packages API
        +-- Queue API
        +-- Review API
        +-- Readiness API
        +-- Submission API
        +-- History API
        +-- Settings API
        +-- Health API
        +-- Maintenance API
        |
        v
Domain Services
        |
        v
Storage, Browser, Provider, and ATS Integrations
```

---

# API Categories

The platform should distinguish:

```text
Command APIs
Query APIs
Event APIs
Maintenance APIs
External Integration APIs
```

---

# Command APIs

Commands request a state change.

Examples:

* Create package.
* Prepare application.
* Queue package.
* Pause workflow.
* Approve review.
* Submit application.
* Update candidate answer.
* Resolve Submission Unknown.
* Delete package.

Command APIs must validate:

* Current state.
* Authorization.
* Expected entity version.
* Idempotency.
* Candidate rules.
* Security policy.
* Required approvals.

---

# Query APIs

Queries retrieve state without changing it.

Examples:

* List jobs.
* Read package.
* Read queue.
* Read readiness report.
* Read history.
* Read system health.
* Read audit timeline.

Query APIs should support:

* Filtering.
* sorting.
* pagination.
* field selection where useful.
* sensitive-value masking.
* consistent timestamps.

---

# Event APIs

Events report completed or observed facts.

Examples:

* Package created.
* Queue item admitted.
* Browser page completed.
* User action required.
* Submission verified.
* History synchronized.

Events are not commands.

An event should not instruct a consumer to perform an unauthorized action.

---

# Maintenance APIs

Maintenance operations include:

* Run health check.
* Create backup.
* Restore backup.
* Run migration.
* Rebuild history.
* Validate packages.
* Repair stale locks.
* Generate diagnostic bundle.

These APIs should require explicit scope and should not run during incompatible workflow states.

---

# External Integration APIs

External integration clients include:

* Reasoning-provider APIs.
* Employer websites.
* ATS websites.
* Future email or calendar integrations.

External responses must be converted into internal canonical models before being used by other services.

---

# API Base Path

A local HTTP API may use a versioned base path.

Example:

```text
/api/v1/
```

The base version represents the public local API contract, not every individual domain schema version.

---

# Resource-Oriented Routes

Conceptual route groups:

```text
/api/v1/candidate-profiles
/api/v1/jobs
/api/v1/application-packages
/api/v1/queues
/api/v1/workflows
/api/v1/reviews
/api/v1/readiness
/api/v1/submissions
/api/v1/history
/api/v1/settings
/api/v1/health
/api/v1/maintenance
/api/v1/events
```

Exact endpoint implementation may vary.

---

# Command Naming

State-changing operations that do not map cleanly to simple resource updates may use explicit action endpoints.

Examples:

```text
POST /application-packages/{package_id}/prepare
POST /application-packages/{package_id}/refresh
POST /application-packages/{package_id}/queue
POST /workflows/{workflow_id}/pause
POST /workflows/{workflow_id}/resume
POST /reviews/{review_id}/approve
POST /submissions/{package_id}/verify
POST /submissions/{package_id}/resolve-unknown
```

---

# Request Envelope

Commands may use a standard request envelope.

```json
{
  "request_id": "req_01",
  "idempotency_key": "package_123_prepare_v1",
  "expected_version": 4,
  "actor": {
    "type": "user",
    "id": "local_user"
  },
  "data": {}
}
```

---

# Response Envelope

Successful responses may use:

```json
{
  "request_id": "req_01",
  "status": "success",
  "data": {},
  "metadata": {
    "schema_version": "1.0",
    "entity_version": 5,
    "generated_at": "2026-07-12T12:00:00-04:00"
  },
  "warnings": []
}
```

---

# Error Envelope

Failed requests should use a structured error response.

```json
{
  "request_id": "req_01",
  "status": "error",
  "error": {
    "code": "PACKAGE_VERSION_CONFLICT",
    "message": "The Application Package changed after it was loaded.",
    "category": "conflict",
    "retryable": false,
    "requires_user_action": true,
    "details": {
      "expected_version": 4,
      "current_version": 5
    }
  }
}
```

---

# Partial Success

Some batch operations may partially succeed.

Example:

```json
{
  "status": "partial_success",
  "succeeded": [
    {
      "package_id": "pkg_001"
    }
  ],
  "failed": [
    {
      "package_id": "pkg_002",
      "error": {
        "code": "PACKAGE_NOT_READY"
      }
    }
  ]
}
```

Batch APIs should not hide individual failures.

---

# API Status Values

Recommended response statuses:

```text
success
success_with_warnings
accepted
partial_success
error
```

`accepted` should be used only when the operation has actually entered a durable execution workflow.

It should not imply future completion.

---

# Synchronous and Workflow Operations

Operations should be classified as:

## Immediate

Completes within the request lifecycle.

Examples:

* Read package.
* update note.
* calculate readiness from current local data.
* list jobs.

## Workflow-Based

Creates or advances a durable workflow.

Examples:

* Prepare package.
* run queue.
* execute browser application.
* create backup.
* restore backup.
* run migration.

Workflow-based responses should return:

* Workflow ID.
* Initial workflow state.
* Event-stream reference.
* Next allowed action.

---

# Workflow Operation Response

```json
{
  "status": "accepted",
  "data": {
    "workflow_id": "workflow_pkg_001",
    "workflow_status": "initialized",
    "current_stage": "package_validation"
  }
}
```

---

# API Authentication

For a localhost-only single-user MVP, authentication may be minimal, but state-changing endpoints still require protection.

Recommended protections:

* Localhost-only binding.
* Secure local session.
* CSRF protection.
* Origin validation.
* SameSite cookies.
* Optional local authentication.
* Short-lived action tokens for sensitive operations.

---

# Authorization

The backend should authorize actions based on:

* Active candidate profile.
* Current package ownership.
* Workflow state.
* Security policy.
* Automation mode.
* User approval.
* Entity version.
* Requested operation.

The frontend cannot authorize itself by displaying or disabling a button.

---

# Canonical Identifier Rules

Every important entity should have an internal stable identifier.

Identifiers should:

* Be unique within their entity type.
* Remain stable across updates.
* Avoid embedding sensitive personal information.
* Avoid relying on mutable names.
* Be safe for local filenames when used in paths.
* Be distinguishable by prefix where helpful.

---

# Recommended Identifier Prefixes

```text
candidate_
job_
package_
queue_
queue_item_
workflow_
review_
readiness_
submission_attempt_
history_
event_
intervention_
artifact_
source_
rule_
answer_
field_
form_
page_
adapter_
profile_
backup_
migration_
```

---

# Internal vs External Identifiers

The platform should distinguish:

```text
Internal Job ID
Employer Job ID
ATS Requisition ID
ATS Application ID
Confirmation Number
Package ID
History Record ID
```

These fields must not be used interchangeably.

---

# Identifier Example

```json
{
  "job_id": "job_internal_001",
  "employer_job_id": "123456",
  "requisition_id": "REQ-789",
  "ats_application_id": "APP-456",
  "confirmation_number": "CONF-123"
}
```

---

# Entity Versioning

Mutable entities should include an integer entity version.

Example:

```json
{
  "package_id": "package_001",
  "entity_version": 7
}
```

Every successful material mutation increments the version.

---

# Optimistic Concurrency

Update commands should include:

```json
{
  "expected_version": 7
}
```

If the current version is 8, the operation should fail with a conflict.

This prevents stale browser tabs or concurrent processes from overwriting newer data.

---

# Entity Timestamps

Canonical entities should use:

```text
created_at
updated_at
```

Additional timestamps may include:

* discovered_at.
* selected_at.
* prepared_at.
* queued_at.
* started_at.
* completed_at.
* submitted_at.
* verified_at.
* archived_at.

All timestamps should use ISO 8601 with an explicit offset.

---

# Time Representation

Example:

```text
2026-07-12T14:30:00-04:00
```

UTC may also be stored internally, but API responses should clearly identify the offset.

---

# Date-Only Fields

Use date-only values when time is not meaningful.

Example:

```text
2026-07-12
```

Do not serialize date-only fields as midnight timestamps.

---

# Null vs Missing

The platform should distinguish:

## Missing Field

The schema or producer omitted the field.

## Null Field

The field is known but has no value.

## Unknown Value

Use an explicit status or enum when uncertainty is meaningful.

Example:

```json
{
  "date_posted": null,
  "date_posted_status": "unknown"
}
```

---

# Canonical Enumerations

Enums should use stable machine values.

Example:

```text
ready_for_review
```

The user interface may display:

```text
Ready for Review
```

Machine values should not depend on display language.

---

# Unknown Enum Values

Consumers should not silently map unknown enum values to a different known state.

Depending on compatibility policy, consumers should:

* Preserve unknown value.
* Mark payload incompatible.
* use an explicit `unknown` fallback when supported.
* request schema migration.

---

# Common Entity Metadata

Canonical entities may include:

```json
{
  "schema_version": "1.0",
  "entity_version": 1,
  "created_at": "",
  "updated_at": "",
  "created_by": {
    "actor_type": "system",
    "actor_id": "package_service"
  },
  "source_references": []
}
```

---

# Source Reference Model

A source reference identifies where a fact or artifact originated.

```json
{
  "source_id": "source_001",
  "source_type": "candidate_json",
  "path_reference": "candidate/profile/candidate.json",
  "record_path": "work_authorization.future_sponsorship",
  "content_hash": "",
  "source_version": "3",
  "captured_at": ""
}
```

Absolute filesystem paths should generally not be exposed through UI-facing APIs.

---

# Provenance Model

```json
{
  "provenance": {
    "origin": "candidate_profile",
    "sources": [
      {
        "source_id": "source_001"
      }
    ],
    "generated": false,
    "validated": true,
    "approved_by_user": true
  }
}
```

---

# Confidence Model

When confidence is relevant:

```json
{
  "confidence": {
    "score": 96,
    "scale": "0_to_100",
    "method": "exact_label_mapping",
    "requires_review": false
  }
}
```

Confidence must not replace deterministic validation.

---

# Sensitive Data Annotation

Fields containing sensitive data should be annotated.

```json
{
  "classification": "highly_sensitive",
  "model_access": false,
  "log_policy": "none",
  "display_policy": "masked",
  "storage_policy": "local_protected"
}
```

---

# Sensitive Value Envelope

A highly sensitive value may use a protected wrapper.

```json
{
  "status": "available",
  "value_reference": "secure://candidate/government_id",
  "display_value": "[REDACTED]",
  "classification": "highly_sensitive"
}
```

The raw value should not be returned through general list APIs.

---

# File Reference Model

APIs should pass file references rather than unrestricted local paths.

```json
{
  "file_reference_id": "artifact_resume_001",
  "logical_path": "resume/tailored_resume_v2.pdf",
  "filename": "Suhas_Arudi_Google_Resume.pdf",
  "mime_type": "application/pdf",
  "size_bytes": 183420,
  "content_hash": "",
  "classification": "confidential"
}
```

---

# File Reference Rules

* Logical path must be package-relative or approved-root-relative.
* Absolute path should remain backend-only.
* Path traversal must be rejected.
* Hash should be validated before consequential use.
* File type should be validated.
* File reference must identify its owning package or candidate profile.

---

# Download Contract

A file-download API should accept a file-reference ID, not an arbitrary path.

Conceptual route:

```text
GET /api/v1/files/{file_reference_id}
```

The backend should verify:

* Reference exists.
* Actor may access it.
* File belongs to the expected entity.
* File hash or existence is valid.
* Content type is safe.

---

# Candidate Profile Model

```json
{
  "candidate_profile_id": "candidate_default",
  "schema_version": "1.0",
  "entity_version": 4,
  "display_name": "Suhas Arudi",
  "status": "active",
  "personal_information": {},
  "professional_summary": {},
  "employment_records": [],
  "education_records": [],
  "skills": [],
  "certifications": [],
  "projects": [],
  "work_authorization": {},
  "preferences": {},
  "standard_answers": {},
  "sensitive_answer_policies": {},
  "source_references": [],
  "created_at": "",
  "updated_at": ""
}
```

---

# Personal Information Model

```json
{
  "legal_first_name": "",
  "legal_middle_name": null,
  "legal_last_name": "",
  "preferred_name": null,
  "email": "",
  "phone": "",
  "location": {
    "city": "",
    "state_or_region": "",
    "postal_code": null,
    "country_code": "US"
  },
  "address": {
    "status": "available",
    "value_reference": "secure://candidate/address",
    "classification": "highly_sensitive"
  }
}
```

---

# Employment Record Model

```json
{
  "employment_record_id": "employment_001",
  "employer_name": "",
  "job_title": "",
  "employment_type": "full_time",
  "location": {},
  "start_date": "2022-01",
  "end_date": null,
  "is_current": true,
  "responsibilities": [],
  "achievements": [],
  "technologies": [],
  "source_references": [],
  "entity_version": 1
}
```

---

# Partial Dates

Employment and education records may use partial dates.

Recommended format:

```text
YYYY-MM
```

or:

```text
YYYY
```

A structured partial-date model may be used where precision must be explicit.

```json
{
  "year": 2022,
  "month": 1,
  "day": null,
  "precision": "month"
}
```

---

# Education Record Model

```json
{
  "education_record_id": "education_001",
  "institution": "",
  "degree": "",
  "field_of_study": "",
  "start_date": null,
  "graduation_date": "2020-05",
  "status": "completed",
  "gpa": null,
  "location": {},
  "source_references": []
}
```

---

# Skill Model

```json
{
  "skill_id": "skill_python",
  "name": "Python",
  "category": "programming_language",
  "status": "verified",
  "years_of_experience": null,
  "proficiency": null,
  "source_references": [],
  "allowed_in_resume": true
}
```

---

# Work Authorization Model

```json
{
  "country_code": "US",
  "authorized_to_work_now": true,
  "requires_sponsorship_now": false,
  "may_require_sponsorship_in_future": true,
  "status_type": "h1b",
  "petition_transfer_required": true,
  "expiration_date": null,
  "source_references": [],
  "last_confirmed_at": ""
}
```

The model should preserve each fact separately.

---

# Candidate Preferences Model

```json
{
  "target_roles": [],
  "target_job_families": [],
  "target_countries": [],
  "target_locations": [],
  "remote_preference": "hybrid_or_remote",
  "employment_types": [
    "full_time"
  ],
  "minimum_base_salary": {
    "amount": null,
    "currency": "USD"
  },
  "relocation": {
    "willing": true,
    "conditions": null
  },
  "travel": {
    "maximum_percentage": null
  },
  "notice_period_days": null,
  "excluded_keywords": [],
  "excluded_companies": []
}
```

---

# Job Model

```json
{
  "job_id": "job_001",
  "schema_version": "1.0",
  "entity_version": 1,
  "company": {
    "company_id": null,
    "name": ""
  },
  "job_title": "",
  "normalized_title": "",
  "job_family": "",
  "seniority": "",
  "description": "",
  "location": {},
  "country_code": "",
  "remote_status": "unknown",
  "employment_type": "unknown",
  "salary": null,
  "employer_job_id": null,
  "requisition_id": null,
  "job_url": "",
  "application_url": null,
  "source": {},
  "date_posted": null,
  "date_discovered": "",
  "status": "open",
  "content_hash": "",
  "source_references": []
}
```

---

# Job Source Model

```json
{
  "job_source_id": "source_company_001",
  "source_type": "company_career_page",
  "name": "",
  "url": "",
  "company_name": "",
  "country_scope": [],
  "last_checked_at": null,
  "status": "active"
}
```

---

# Job Salary Model

```json
{
  "minimum": 180000,
  "maximum": 220000,
  "currency": "USD",
  "period": "year",
  "compensation_type": "base_salary",
  "source_text": "",
  "confidence": 95
}
```

---

# Job Analysis Model

```json
{
  "job_analysis_id": "job_analysis_001",
  "job_id": "job_001",
  "analysis_version": 1,
  "required_skills": [],
  "preferred_skills": [],
  "responsibilities": [],
  "qualifications": [],
  "experience_requirements": [],
  "work_authorization_requirements": [],
  "salary_analysis": {},
  "security_clearance": {},
  "application_requirements": [],
  "prompt_version": "",
  "model_metadata": {},
  "validated": true
}
```

---

# Job Match Model

```json
{
  "job_match_id": "match_001",
  "job_id": "job_001",
  "candidate_profile_id": "candidate_default",
  "score": 91,
  "recommendation": "strong_match",
  "components": {
    "skills": 35,
    "experience": 25,
    "title": 15,
    "location": 8,
    "salary": 8
  },
  "strengths": [],
  "gaps": [],
  "hard_rule_results": [],
  "explanation": "",
  "evaluated_at": ""
}
```

---

# Application Package Model

```json
{
  "package_id": "package_001",
  "schema_version": "1.0",
  "entity_version": 5,
  "candidate_profile_id": "candidate_default",
  "job_id": "job_001",
  "status": "ready",
  "automation_mode": "review",
  "job_snapshot": {},
  "candidate_context_snapshot": {},
  "active_artifacts": {},
  "answer_set": {},
  "application_plan": {},
  "review_summary": {},
  "readiness_summary": {},
  "execution_summary": {},
  "submission_summary": {},
  "fingerprints": {},
  "created_at": "",
  "updated_at": ""
}
```

---

# Package Status Enum

```text
draft
preparing
needs_attention
refresh_required
ready
queued
executing
ready_for_review
submitting
submitted
submission_unknown
already_applied
blocked
failed
cancelled
closed
archived
```

---

# Artifact Model

```json
{
  "artifact_id": "artifact_resume_001",
  "artifact_type": "resume",
  "package_id": "package_001",
  "version": 2,
  "status": "active",
  "file_reference": {},
  "source_artifact_id": "artifact_base_resume_001",
  "generation_metadata": {},
  "validation_report_id": "",
  "approved": true,
  "created_at": ""
}
```

---

# Artifact Types

```text
base_resume
resume
cover_letter
transcript
portfolio
writing_sample
certification
reference_list
prepared_answers
application_plan
form_snapshot
review_report
readiness_report
submission_evidence
```

---

# Artifact Statuses

```text
draft
active
inactive
superseded
approved
rejected
submitted
archived
invalid
```

---

# Resume Change Model

```json
{
  "change_id": "change_001",
  "section": "experience",
  "change_type": "rewrite",
  "source_text_reference": "",
  "new_text_reference": "",
  "reason": "Emphasize distributed systems experience.",
  "factual_validation": "passed"
}
```

---

# Application Answer Model

```json
{
  "answer_id": "answer_001",
  "question": {
    "question_id": "question_001",
    "original_text": "",
    "normalized_text": "",
    "canonical_family": "work_authorization.sponsorship_future",
    "field_type": "radio",
    "required": true,
    "options": []
  },
  "resolution": {
    "status": "resolved",
    "answer_type": "controlled_choice",
    "value": "yes",
    "display_value": "Yes",
    "source_references": [],
    "confidence": 100,
    "requires_review": false
  },
  "sensitivity": {
    "classification": "highly_sensitive",
    "log_policy": "category_only"
  },
  "version": 1
}
```

---

# Answer Resolution Statuses

```text
resolved
resolved_with_review
missing
ambiguous
manual_only
declined
optional_blank
blocked_by_policy
invalid
```

---

# Question Model

```json
{
  "question_id": "question_001",
  "original_text": "",
  "normalized_text": "",
  "help_text": "",
  "canonical_family": "",
  "question_type": "controlled_choice",
  "field_type": "radio",
  "required": true,
  "options": [],
  "constraints": {},
  "source_context": {},
  "sensitive": false
}
```

---

# Question Option Model

```json
{
  "option_id": "option_yes",
  "label": "Yes",
  "value": "yes",
  "enabled": true,
  "selected": false,
  "metadata": {}
}
```

---

# Application Plan Model

```json
{
  "application_plan_id": "plan_001",
  "package_id": "package_001",
  "application_url": "",
  "expected_ats": "greenhouse",
  "automation_mode": "review",
  "browser_profile_id": "profile_default",
  "active_resume_artifact_id": "",
  "cover_letter_requirement": "optional",
  "supporting_artifacts": [],
  "expected_sections": [],
  "expected_question_families": [],
  "review_policy": {},
  "submission_policy": {},
  "stop_conditions": [],
  "retry_policy": {},
  "created_at": ""
}
```

---

# Review Model

```json
{
  "review_id": "review_001",
  "package_id": "package_001",
  "review_stage": "pre_submission",
  "status": "approved_with_warnings",
  "findings": [],
  "corrections": [],
  "reviewed_artifacts": [],
  "reviewed_form_snapshot_hash": "",
  "approval": null,
  "created_at": "",
  "completed_at": ""
}
```

---

# Review Finding Model

```json
{
  "finding_id": "finding_001",
  "category": "work_authorization_contradiction",
  "severity": "blocking",
  "artifact_reference": "",
  "field_reference": "",
  "message": "",
  "evidence": [],
  "recommended_action": "",
  "automatically_correctable": true,
  "status": "open"
}
```

---

# Finding Severities

```text
blocking
high
medium
low
informational
```

---

# Review Statuses

```text
approved
approved_with_warnings
changes_required
user_input_required
manual_review_required
blocked
failed
```

---

# Approval Model

```json
{
  "approval_id": "approval_001",
  "review_id": "review_001",
  "package_id": "package_001",
  "decision": "approved",
  "approval_mode": "user",
  "approved_artifact_versions": {
    "resume": 2,
    "cover_letter": 1,
    "answer_set": 3
  },
  "form_snapshot_hash": "",
  "approved_by": {
    "actor_type": "user",
    "actor_id": "local_user"
  },
  "approved_at": "",
  "expires_at": null
}
```

---

# Readiness Model

```json
{
  "readiness_id": "readiness_001",
  "package_id": "package_001",
  "stage": "submission",
  "status": "ready",
  "checks": [],
  "blocking_issues": [],
  "warnings": [],
  "required_user_actions": [],
  "refresh_reasons": [],
  "next_allowed_actions": [
    "submit"
  ],
  "evaluated_at": ""
}
```

---

# Readiness Statuses

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

# Readiness Check Model

```json
{
  "check_id": "check_resume_verified",
  "category": "documents",
  "status": "passed",
  "required": true,
  "message": "",
  "evidence": [],
  "recommended_action": null
}
```

---

# Queue Model

```json
{
  "queue_id": "queue_001",
  "schema_version": "1.0",
  "entity_version": 2,
  "status": "running",
  "strategy": "selected_order",
  "browser_profile_id": "profile_default",
  "automation_mode": "review",
  "items": [],
  "created_at": "",
  "started_at": "",
  "completed_at": null
}
```

---

# Queue Item Model

```json
{
  "queue_item_id": "queue_item_001",
  "queue_id": "queue_001",
  "package_id": "package_001",
  "position": 1,
  "priority": 100,
  "status": "executing",
  "attempt_count": 1,
  "maximum_attempts": 3,
  "required_user_action_id": null,
  "started_at": "",
  "completed_at": null
}
```

---

# Queue Statuses

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

# Queue Item Statuses

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

# Workflow Model

```json
{
  "workflow_id": "workflow_001",
  "package_id": "package_001",
  "queue_id": "queue_001",
  "status": "running",
  "current_stage": "form_execution",
  "last_completed_stage": "runtime_answer_resolution",
  "next_stage": "page_validation",
  "current_page_number": 3,
  "browser_session_id": "",
  "ats_adapter_id": "greenhouse",
  "attempt_count": 1,
  "checkpoint_reference": "",
  "started_at": "",
  "updated_at": ""
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

# Workflow Stage Enum

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

# Checkpoint Model

```json
{
  "checkpoint_id": "checkpoint_001",
  "workflow_id": "workflow_001",
  "package_id": "package_001",
  "stage": "page_completed",
  "page_number": 2,
  "page_url": "",
  "page_signature": "",
  "completed_fields": [],
  "uploaded_files": [],
  "artifact_versions": {},
  "submission_attempted": false,
  "created_at": ""
}
```

---

# Browser Session Model

```json
{
  "browser_session_id": "browser_session_001",
  "profile_id": "profile_default",
  "status": "running",
  "active_package_id": "package_001",
  "active_workflow_id": "workflow_001",
  "browser_engine": "chromium",
  "browser_version": "",
  "started_at": "",
  "health_status": "healthy"
}
```

---

# Browser Page Model

```json
{
  "page_id": "page_001",
  "browser_session_id": "browser_session_001",
  "url": "",
  "domain": "",
  "title": "",
  "page_type": "work_history",
  "page_number": 3,
  "page_signature": "",
  "ats_adapter_id": "workday",
  "form_model": {},
  "captured_at": ""
}
```

---

# Form Model

```json
{
  "form_id": "form_001",
  "page_id": "page_001",
  "page_type": "work_authorization",
  "title": "",
  "sections": [],
  "fields": [],
  "actions": [],
  "validation_messages": [],
  "adapter_metadata": {}
}
```

---

# Field Model

```json
{
  "field_id": "field_001",
  "adapter_field_id": null,
  "label": "",
  "help_text": "",
  "field_type": "dropdown",
  "semantic_type": "personal.country",
  "required": true,
  "visible": true,
  "enabled": true,
  "read_only": false,
  "current_value": null,
  "options": [],
  "constraints": {},
  "sensitivity": {},
  "confidence": 98
}
```

---

# Field Types

```text
text
email
phone
url
number
textarea
rich_text
dropdown
searchable_dropdown
multi_select
radio
checkbox
checkbox_group
date
date_picker
file_upload
signature
address_autocomplete
hidden
unknown
```

---

# Form Action Model

```json
{
  "action_id": "action_continue",
  "action_type": "next",
  "label": "Save and Continue",
  "enabled": true,
  "final_submission": false,
  "confidence": 99
}
```

---

# Browser Interaction Plan

```json
{
  "interaction_plan_id": "interaction_plan_001",
  "package_id": "package_001",
  "page_id": "page_001",
  "steps": [
    {
      "step_id": "step_001",
      "field_id": "field_001",
      "action_type": "select_option",
      "expected_value": "United States",
      "sensitive": false
    }
  ],
  "validation_policy": "strict",
  "maximum_action_retries": 3
}
```

---

# Browser Action Result

```json
{
  "step_id": "step_001",
  "status": "verified",
  "action_type": "select_option",
  "field_id": "field_001",
  "expected_value_policy": "category_only",
  "verification_method": "read_back",
  "retry_count": 0,
  "error": null
}
```

---

# User Intervention Model

```json
{
  "intervention_id": "intervention_001",
  "package_id": "package_001",
  "workflow_id": "workflow_001",
  "category": "captcha_required",
  "status": "pending",
  "title": "Verification required",
  "message": "",
  "sensitive": false,
  "available_actions": [
    "mark_completed",
    "cancel_application"
  ],
  "resume_stage": "page_inspection",
  "created_at": "",
  "completed_at": null
}
```

---

# Intervention Categories

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
external_assessment
security_confirmation
```

---

# ATS Adapter Metadata Model

```json
{
  "adapter_id": "greenhouse",
  "display_name": "Greenhouse",
  "adapter_version": "1.0.0",
  "status": "stable",
  "enabled": true,
  "supported_domains": [],
  "capabilities": {},
  "minimum_browser_engine_version": "",
  "last_regression_result": "passed"
}
```

---

# ATS Detection Result

```json
{
  "detected_ats": "greenhouse",
  "confidence": 99,
  "detection_methods": [
    "domain_pattern",
    "page_signature"
  ],
  "matched_adapter_id": "greenhouse",
  "generic_fallback_allowed": true,
  "warnings": []
}
```

---

# Adapter Capability Model

```json
{
  "resume_upload": "supported",
  "resume_parsing": "supported",
  "repeating_employment": "supported",
  "repeating_education": "supported",
  "review_page": "supported",
  "submission_verification": "supported",
  "application_dashboard": "partially_supported"
}
```

---

# Capability Values

```text
supported
partially_supported
manual_only
unsupported
unknown
```

---

# Submission Attempt Model

```json
{
  "attempt_id": "submission_attempt_001",
  "package_id": "package_001",
  "workflow_id": "workflow_001",
  "attempt_number": 1,
  "status": "verification_pending",
  "page_url_before": "",
  "page_url_after": null,
  "submit_control_label": "Submit Application",
  "click_initiated_at": "",
  "verification_started_at": "",
  "verification_completed_at": null,
  "evidence": [],
  "result": null
}
```

---

# Submission Attempt Statuses

```text
attempt_created
click_initiated
verification_pending
submitted
failed_before_click
failed_after_click
already_applied
application_closed
submission_unknown
verification_error
```

---

# Submission Evidence Model

```json
{
  "evidence_id": "evidence_001",
  "attempt_id": "submission_attempt_001",
  "source": "confirmation_page",
  "signal_type": "explicit_success_message",
  "strength": "strong",
  "value_policy": "summary",
  "captured_at": "",
  "screenshot_reference": null,
  "metadata": {}
}
```

---

# Evidence Strengths

```text
conclusive
strong
supporting
weak
contradictory
```

---

# Submission Result Model

```json
{
  "package_id": "package_001",
  "attempt_id": "submission_attempt_001",
  "status": "submitted",
  "confidence": 100,
  "confirmation_number": null,
  "ats_application_id": null,
  "confirmation_message": "",
  "confirmation_url": "",
  "submitted_at": "",
  "verified_at": "",
  "verification_source": "ats_confirmation_page",
  "evidence_ids": []
}
```

---

# Submission Statuses

```text
not_submitted
submitted
submission_unknown
failed
already_applied
application_closed
cancelled
```

---

# Unknown Submission Resolution Model

```json
{
  "resolution_id": "resolution_001",
  "package_id": "package_001",
  "attempt_id": "submission_attempt_001",
  "previous_status": "submission_unknown",
  "resolved_status": "submitted",
  "resolution_source": "ats_dashboard",
  "evidence_ids": [],
  "resolved_by": {
    "actor_type": "system",
    "actor_id": "dashboard_reconciliation"
  },
  "resolved_at": ""
}
```

---

# History Record Model

```json
{
  "history_record_id": "history_001",
  "package_id": "package_001",
  "candidate_profile_id": "candidate_default",
  "company": "",
  "job_title": "",
  "job_id": "job_001",
  "employer_job_id": null,
  "requisition_id": null,
  "location": {},
  "job_url": "",
  "application_url": "",
  "ats_platform": "",
  "date_discovered": "",
  "date_applied": null,
  "match_score": 91,
  "application_status": "submitted",
  "submission_status": "submitted",
  "recruitment_status": "under_review",
  "automation_mode": "review",
  "resume_artifact_id": "",
  "cover_letter_artifact_id": null,
  "confirmation_number": null,
  "ats_application_id": null,
  "follow_up": {},
  "notes": "",
  "created_at": "",
  "updated_at": ""
}
```

---

# History Event Model

```json
{
  "event_id": "history_event_001",
  "sequence": 1,
  "history_record_id": "history_001",
  "package_id": "package_001",
  "event_type": "submission_verified",
  "previous_status": "in_progress",
  "new_status": "submitted",
  "source": "submission_verifier",
  "metadata": {},
  "created_at": ""
}
```

---

# Application Status vs Recruitment Status

These remain separate.

```json
{
  "submission_status": "submitted",
  "recruitment_status": "rejected"
}
```

A rejection does not undo a successful submission.

---

# Audit Event Model

```json
{
  "audit_event_id": "audit_001",
  "schema_version": "1.0",
  "package_id": "package_001",
  "event_type": "review.user_approved",
  "actor": {
    "actor_type": "user",
    "actor_id": "local_user"
  },
  "artifact_versions": {},
  "change_summary": "",
  "reason": null,
  "timestamp": "",
  "previous_event_hash": "",
  "event_hash": ""
}
```

---

# Actor Model

```json
{
  "actor_type": "user",
  "actor_id": "local_user",
  "display_name": null
}
```

Actor types:

```text
user
system
browser
ats_adapter
reasoning_provider
import
reconciliation
maintenance
```

---

# System Event Model

```json
{
  "event_id": "event_001",
  "event_name": "workflow.stage_completed",
  "level": "INFO",
  "category": "workflow",
  "timestamp": "",
  "sequence": 120,
  "correlation": {
    "package_id": "package_001",
    "workflow_id": "workflow_001",
    "queue_id": "queue_001"
  },
  "component": "orchestrator",
  "status": "success",
  "message": "",
  "metadata": {}
}
```

---

# Health Result Model

```json
{
  "health_check_id": "health_001",
  "checked_at": "",
  "overall_status": "degraded",
  "components": {
    "storage": {
      "status": "healthy"
    },
    "reasoning_provider": {
      "status": "unavailable"
    }
  },
  "warnings": [],
  "blocking_issues": []
}
```

---

# Health Statuses

```text
healthy
degraded
unavailable
blocked
unknown
```

---

# Configuration Model

Configuration should be schema-validated.

```json
{
  "schema_version": "1.0",
  "application": {},
  "storage": {},
  "candidate": {},
  "reasoning": {},
  "browser": {},
  "ats": {},
  "execution": {},
  "review": {},
  "readiness": {},
  "submission": {},
  "history": {},
  "logging": {},
  "security": {},
  "privacy": {},
  "retention": {},
  "backup": {}
}
```

---

# Secret Reference Model

```json
{
  "secret_reference": "secret://reasoning/claude_api_key",
  "provider": "os_credential_store",
  "status": "available",
  "last_validated_at": ""
}
```

The API must never return the secret value.

---

# Backup Model

```json
{
  "backup_id": "backup_001",
  "application_version": "1.0.0",
  "schema_versions": {},
  "encrypted": true,
  "included_categories": [],
  "excluded_categories": [],
  "file_count": 0,
  "total_size_bytes": 0,
  "checksums": {},
  "created_at": "",
  "verification_status": "passed"
}
```

---

# Migration Model

```json
{
  "migration_id": "package_schema_1_0_to_1_1",
  "source_version": "1.0",
  "target_version": "1.1",
  "status": "success",
  "backup_id": "backup_001",
  "records_processed": 25,
  "warnings": [],
  "started_at": "",
  "completed_at": ""
}
```

---

# Provider Request Model

```json
{
  "provider_request_id": "provider_req_001",
  "purpose": "narrative_answer_generation",
  "provider": "claude",
  "model": "",
  "prompt_id": "application_answer",
  "prompt_version": "1.2",
  "input_schema": "NarrativeAnswerRequest@1.0",
  "output_schema": "NarrativeAnswerResponse@1.0",
  "context_manifest": {},
  "timeout_seconds": 60
}
```

---

# Provider Context Manifest

```json
{
  "included_categories": [
    "relevant_employment",
    "relevant_skills",
    "job_description"
  ],
  "excluded_categories": [
    "government_ids",
    "demographics",
    "credentials"
  ],
  "sensitive_data_present": false,
  "content_hash": ""
}
```

---

# Provider Output Envelope

```json
{
  "schema_version": "1.0",
  "status": "success",
  "result": {},
  "source_references": [],
  "warnings": [],
  "model_metadata": {
    "provider": "claude",
    "model": "",
    "prompt_version": "1.2"
  }
}
```

---

# Narrative Answer Output Schema

```json
{
  "answer_text": "",
  "character_count": 0,
  "word_count": 0,
  "claims": [
    {
      "claim_text": "",
      "source_references": []
    }
  ],
  "company_references": [],
  "role_references": [],
  "validation_hints": [],
  "confidence": 95
}
```

---

# Job Analysis Provider Schema

```json
{
  "normalized_job_title": "",
  "job_family": "",
  "seniority": "",
  "required_skills": [],
  "preferred_skills": [],
  "responsibilities": [],
  "qualifications": [],
  "application_requirements": [],
  "work_authorization_text": [],
  "salary_text": [],
  "warnings": []
}
```

---

# Resume Tailoring Provider Schema

```json
{
  "tailoring_plan": {
    "summary_changes": [],
    "skill_order": [],
    "bullet_changes": [],
    "sections_to_preserve": []
  },
  "unsupported_claims": [],
  "source_references": [],
  "warnings": []
}
```

The provider should not directly modify source facts without validation.

---

# Application Review Provider Schema

```json
{
  "status": "approved",
  "blocking_issues": [],
  "warnings": [],
  "inconsistencies": [],
  "unsupported_claims": [],
  "wrong_company_references": [],
  "recommended_changes": [],
  "summary": ""
}
```

---

# Structured Output Validation

Provider output should pass:

* JSON parsing.
* Schema validation.
* Required-field validation.
* Enum validation.
* String-length validation.
* Source-reference validation.
* Candidate-fact validation.
* Sensitive-content validation.
* Job-identity validation.

Malformed or unsafe output should not enter domain models.

---

# Schema Registry

## Responsibility

The Schema Registry should maintain all canonical platform schemas and their versions.

Conceptual interface:

```text
SchemaRegistry

    register_schema(schema_name, version, definition)
    get_schema(schema_name, version)
    get_latest_compatible(schema_name, consumer_version)
    validate(schema_name, version, payload)
    list_versions(schema_name)
    deprecate_schema(schema_name, version)
    get_migration_path(schema_name, from_version, to_version)
```

---

# Schema Naming

Recommended schema naming:

```text
CandidateProfile
Job
JobAnalysis
JobMatch
ApplicationPackage
ApplicationAnswerSet
ApplicationPlan
ReviewReport
ReadinessReport
Queue
Workflow
FormModel
SubmissionResult
HistoryRecord
AuditEvent
HealthResult
```

A fully qualified identifier may be:

```text
ApplicationPackage@1.0
```

---

# Schema Registry Entry

```json
{
  "schema_name": "ApplicationPackage",
  "version": "1.0",
  "status": "active",
  "compatibility_policy": "backward",
  "definition_path": "schemas/application_package/1.0.json",
  "checksum": "",
  "registered_at": "",
  "deprecated_at": null,
  "replacement_version": null
}
```

---

# Registry Storage

Conceptual structure:

```text
schemas/
    candidate_profile/
        1.0.json
    job/
        1.0.json
    application_package/
        1.0.json
        1.1.json
    review_report/
        1.0.json
    events/
        workflow_event/
            1.0.json
```

---

# Schema Statuses

```text
draft
experimental
active
deprecated
retired
```

---

# Schema Version Format

Domain schemas should use:

```text
major.minor
```

Example:

```text
1.0
1.1
2.0
```

Patch-level implementation fixes that do not change the schema structure need not change the schema version.

---

# Major Schema Change

A major version is required when:

* Required field is removed.
* Field meaning changes incompatibly.
* Field type changes incompatibly.
* Enum meaning changes.
* Entity identity changes.
* Existing consumers cannot safely interpret the payload.
* Security classification changes incompatibly.

---

# Minor Schema Change

A minor version may be used when:

* Optional field is added.
* New enum value is added under a compatible enum policy.
* New metadata is added.
* Validation is clarified without invalidating existing valid data.
* A field becomes deprecated but remains supported.

---

# Compatibility Policies

Supported policies:

```text
backward
forward
full
none
```

---

# Backward Compatibility

A newer consumer can read older producer data.

---

# Forward Compatibility

An older consumer can tolerate newer producer data.

This usually requires:

* Ignoring unknown optional fields.
* Preserving unknown fields during round trips.
* Avoiding closed enums where new values are likely.

---

# Full Compatibility

Both backward and forward compatible.

---

# No Compatibility

Explicit migration is required.

---

# Compatibility Rules

Consumers should:

* Reject incompatible major versions.
* Accept compatible minor versions according to policy.
* Ignore unknown optional fields when safe.
* Preserve unknown fields during compatible edits when practical.
* Never ignore unknown security-critical states.
* Never map unknown submission statuses to Failed or Submitted.

---

# Security-Critical Enum Policy

Enums related to consequential states should use strict handling.

Examples:

* Submission status.
* sensitive-field policy.
* review status.
* readiness status.
* security alert severity.

Unknown values should cause:

* Incompatible payload error.
* Safe blocked state.
* User or maintenance review.

---

# Open Enum Policy

Less critical categorization fields may allow unknown values.

Examples:

* Skill category.
* job source type.
* optional metric label.

---

# Schema Validation Levels

Recommended levels:

```text
syntactic
structural
semantic
cross_entity
policy
```

---

# Syntactic Validation

Checks:

* Valid JSON.
* valid encoding.
* supported date formats.
* valid numbers.
* valid strings.

---

# Structural Validation

Checks:

* Required fields.
* field types.
* enum membership.
* array shapes.
* object structure.
* maximum sizes.

---

# Semantic Validation

Checks:

* Start date before end date.
* current role has no false end date.
* salary minimum not above maximum.
* package job ID exists.
* answer option exists.
* artifact belongs to package.

---

# Cross-Entity Validation

Checks:

* Approval references active artifact versions.
* Queue item references Ready package.
* Submission attempt references active workflow.
* History record matches package identity.
* Browser form snapshot matches job identity.

---

# Policy Validation

Checks:

* Candidate rules.
* sensitive-field policy.
* automatic submission policy.
* domain trust.
* duplicate policy.
* privacy policy.

---

# Validation Result Model

```json
{
  "status": "failed",
  "schema_name": "ApplicationPackage",
  "schema_version": "1.0",
  "errors": [
    {
      "code": "REQUIRED_FIELD_MISSING",
      "path": "active_artifacts.resume",
      "message": "An active resume is required."
    }
  ],
  "warnings": []
}
```

---

# Validation Error Path

Use a stable path notation.

Examples:

```text
candidate.work_authorization.may_require_sponsorship_in_future
artifacts[0].file_reference.content_hash
fields[3].options[1].label
```

---

# Validation Error Severity

```text
error
warning
informational
```

A structural or policy error should not be downgraded merely to permit workflow progression.

---

# Schema Size Limits

Schemas should define limits for externally supplied or potentially large fields.

Examples:

* Maximum job-description length.
* maximum narrative-answer length.
* maximum number of form fields.
* maximum number of queue items.
* maximum event metadata size.
* maximum file-reference filename length.
* maximum note length.

This protects local services from malformed payloads.

---

# Serialization Standards

Canonical API serialization should use JSON.

Files such as CSV, XLSX, PDF, and DOCX remain domain artifacts, not API payload formats.

---

# JSON Encoding

Use:

* UTF-8.
* standard JSON types.
* no comments.
* no trailing commas.
* explicit nulls where meaningful.
* ISO dates.
* stable machine enums.

---

# Decimal and Currency Values

Currency should not use binary floating-point values.

Use integer minor units or decimal strings.

Example:

```json
{
  "amount": "180000.00",
  "currency": "USD"
}
```

For whole annual salaries, integer major units may be acceptable if documented consistently.

---

# Percentage Values

Example:

```json
{
  "travel_percentage": 25
}
```

Validation should enforce:

```text
0 <= value <= 100
```

---

# Boolean Values

Use true and false for factual booleans.

Do not overload false to mean unknown.

Use:

```json
{
  "value": null,
  "status": "unknown"
}
```

when needed.

---

# Text Normalization

Canonical text normalization may include:

* Unicode normalization.
* line-ending normalization.
* trimming accidental surrounding whitespace.
* preserving meaningful internal whitespace.
* preserving original external text separately when needed.

---

# Original vs Normalized Text

For questions and job titles, preserve both:

```json
{
  "original_text": "",
  "normalized_text": ""
}
```

Normalization should not overwrite source evidence.

---

# Pagination

List APIs should support pagination.

Request:

```text
?page_size=50&page_token=...
```

Response:

```json
{
  "items": [],
  "next_page_token": null,
  "total_count": 120
}
```

---

# Pagination Requirements

* Stable ordering.
* bounded page size.
* opaque continuation token.
* clear total count when practical.
* consistent filters across pages.
* token invalidation when query changes.

---

# Offset Pagination

Offset pagination may be acceptable for small local datasets.

Cursor pagination is preferable for event streams and mutable datasets.

---

# Sorting

Conceptual sort parameters:

```text
sort=date_posted:desc
sort=match_score:desc,company:asc
```

Only allowlisted fields should be sortable.

---

# Filtering

Filters should use explicit fields.

Examples:

```text
status=submitted
company=Google
country_code=US
match_score_min=80
date_applied_from=2026-07-01
```

The backend should not interpret arbitrary filter expressions.

---

# Search

Free-text search may be supported across allowlisted fields such as:

* Company.
* job title.
* job ID.
* notes.
* confirmation number.

Sensitive answer values should not be included by default.

---

# Field Selection

Some APIs may support limited field selection.

Example:

```text
fields=package_id,company,job_title,status
```

Sensitive fields should remain protected regardless of client request.

---

# Batch Operations

Batch requests should define:

* Maximum item count.
* Per-item result.
* Idempotency behavior.
* Failure isolation.
* Order preservation where relevant.

---

# Batch Prepare Request

```json
{
  "package_ids": [
    "package_001",
    "package_002"
  ],
  "automation_mode": "review"
}
```

---

# Batch Result

```json
{
  "status": "partial_success",
  "results": [
    {
      "package_id": "package_001",
      "status": "accepted",
      "workflow_id": "workflow_001"
    },
    {
      "package_id": "package_002",
      "status": "error",
      "error": {
        "code": "PACKAGE_ALREADY_SUBMITTED"
      }
    }
  ]
}
```

---

# Idempotency

State-changing commands that may be retried should accept an idempotency key.

Examples:

* Create package.
* queue package.
* create submission attempt.
* synchronize history.
* create backup.
* apply status update.

---

# Idempotency Record

```json
{
  "idempotency_key": "package_001_queue_20260712",
  "operation": "queue_package",
  "request_hash": "",
  "result_reference": "",
  "created_at": "",
  "expires_at": null
}
```

---

# Idempotency Rules

If the same key and same request are received:

* Return the prior result.

If the same key and different request are received:

* Reject with an idempotency conflict.

---

# Final Submission Idempotency

The final submission command must be stricter.

The API should require:

* Valid submission-readiness ID.
* valid review approval ID.
* current package version.
* unique submission-attempt ID.
* submission lock.
* no prior unknown attempt.
* no prior verified submission.

The system must not use normal command retries to repeat the final click.

---

# State Transition Contracts

Every state-changing API should validate allowed transitions.

Example:

```text
ready -> queued
queued -> executing
executing -> waiting_for_user
executing -> ready_for_review
ready_for_review -> submitting
submitting -> submitted
```

Invalid:

```text
draft -> submitted
cancelled -> submitting
submission_unknown -> executing
```

---

# State Transition Error

```json
{
  "code": "INVALID_STATE_TRANSITION",
  "message": "A package in Submission Unknown state cannot return to execution.",
  "details": {
    "current_state": "submission_unknown",
    "requested_state": "executing"
  }
}
```

---

# Next Allowed Actions Contract

Entities such as packages and workflows should expose backend-calculated actions.

```json
{
  "next_allowed_actions": [
    "review",
    "queue",
    "refresh",
    "skip"
  ]
}
```

The UI should not infer allowed transitions independently.

---

# Action Preconditions

A command response may return unmet preconditions.

```json
{
  "status": "error",
  "error": {
    "code": "ACTION_PRECONDITIONS_FAILED",
    "details": {
      "failed_preconditions": [
        "review_approval_missing",
        "duplicate_check_stale"
      ]
    }
  }
}
```

---

# Error Categories

Recommended categories:

```text
validation
authentication
authorization
not_found
conflict
precondition
rate_limit
external_dependency
browser
provider
security
privacy
storage
migration
internal
submission_unknown
```

---

# Error Code Conventions

Use stable uppercase machine codes.

Examples:

```text
CANDIDATE_PROFILE_NOT_FOUND
JOB_SOURCE_INVALID
PACKAGE_NOT_READY
PACKAGE_VERSION_CONFLICT
QUEUE_ALREADY_RUNNING
WORKFLOW_USER_ACTION_REQUIRED
ATS_ADAPTER_UNSUPPORTED
BROWSER_PROFILE_LOCKED
REVIEW_APPROVAL_INVALID
SUBMISSION_ALREADY_ATTEMPTED
SUBMISSION_OUTCOME_UNKNOWN
HISTORY_SYNC_FAILED
SECURITY_UNTRUSTED_DOMAIN
PRIVACY_SENSITIVE_FIELD_BLOCKED
```

---

# Error Retryability

Every error should identify:

```json
{
  "retryable": false,
  "retry_after_seconds": null
}
```

For final submission uncertainty:

```json
{
  "retryable": false,
  "submission_outcome_unknown": true
}
```

---

# Human-Readable Errors

Machine codes should be accompanied by concise user-facing messages.

Internal stack traces should not be returned through normal APIs.

---

# Warning Model

```json
{
  "code": "OPTIONAL_COVER_LETTER_OMITTED",
  "message": "The cover letter was optional and was not included.",
  "category": "documents",
  "severity": "low"
}
```

---

# API Deprecation

Deprecated fields or endpoints should be marked.

Example response metadata:

```json
{
  "deprecations": [
    {
      "field": "application_status",
      "replacement": "submission_status and recruitment_status",
      "removal_version": "2.0"
    }
  ]
}
```

---

# Endpoint Versioning

Breaking local API changes should increment the API major version.

Example:

```text
/api/v1/
/api/v2/
```

Compatible endpoint additions should remain within the current major version.

---

# Domain Schema Versioning

Domain schemas version independently from API versions.

Example:

```text
API: v1
ApplicationPackage schema: 1.2
ReviewReport schema: 1.0
```

---

# Content-Type Versioning

A future implementation may use:

```text
application/vnd.autonomous-job-platform.application-package+json;version=1.0
```

This is optional for the local MVP.

---

# Event Schema Registry

Events should also be versioned.

Example:

```json
{
  "event_name": "submission.verified",
  "event_schema_version": "1.0",
  "data": {}
}
```

---

# Event Delivery

Local UI event delivery may use:

* Server-sent events.
* WebSocket.
* polling.
* append-only event replay.

The delivery mechanism should not change the event schema.

---

# Event Stream Requirements

* Event IDs.
* sequence numbers.
* timestamps.
* correlation identifiers.
* replay support.
* duplicate detection.
* reconnect behavior.
* retention policy.

---

# Event Replay

A client reconnecting after event 120 may request:

```text
events after sequence 120
```

The backend should either:

* Replay available events.
* return current authoritative state when older events expired.
* indicate a replay gap.

---

# Event Deduplication

Consumers should deduplicate by:

```text
event_id
```

Sequence numbers support ordering but should not be the sole identity.

---

# Command and Event Distinction

Example:

```text
Command:
submit_application

Event:
submission.click_initiated
```

An event should never be treated as permission to repeat the command.

---

# Sensitive API Responses

List and summary APIs should return masked values.

Example:

```json
{
  "email": "su***@gmail.com",
  "email_status": "available"
}
```

A separate protected detail operation may reveal the value when authorized.

---

# Sensitive Reveal Contract

```json
{
  "request_id": "",
  "field_reference": "candidate.personal.email",
  "purpose": "review_application",
  "confirmation": true
}
```

The backend should log a sensitive-reveal audit event where appropriate.

---

# No Secret Retrieval API

General APIs should not provide:

* API keys.
* passwords.
* cookies.
* refresh tokens.
* encryption keys.

They may provide only secret metadata and availability status.

---

# API File Uploads

User uploads to the local platform should use controlled multipart or file-reference creation.

The backend should validate:

* File size.
* file type.
* file signature.
* destination category.
* candidate profile.
* path.
* malware or active-content policy where supported.

---

# File Upload Response

```json
{
  "file_reference_id": "source_resume_001",
  "filename": "resume.pdf",
  "mime_type": "application/pdf",
  "size_bytes": 180000,
  "content_hash": "",
  "validation_status": "passed"
}
```

---

# API Download Headers

File responses should use:

* Correct content type.
* safe filename.
* attachment or inline disposition as appropriate.
* no arbitrary path disclosure.
* no permissive caching for sensitive files.

---

# Local Cache APIs

Cache invalidation should be explicit.

Examples:

```text
POST /maintenance/cache/clear
POST /application-packages/{package_id}/invalidate-cache
```

Cache APIs should not delete source-of-truth artifacts.

---

# Candidate Profile API

Conceptual operations:

```text
GET    /candidate-profiles
POST   /candidate-profiles
GET    /candidate-profiles/{candidate_profile_id}
PATCH  /candidate-profiles/{candidate_profile_id}
POST   /candidate-profiles/{candidate_profile_id}/validate
POST   /candidate-profiles/{candidate_profile_id}/import
GET    /candidate-profiles/{candidate_profile_id}/conflicts
POST   /candidate-profiles/{candidate_profile_id}/resolve-conflict
```

---

# Candidate Update Contract

```json
{
  "expected_version": 4,
  "changes": [
    {
      "operation": "replace",
      "path": "work_authorization.may_require_sponsorship_in_future",
      "value": true
    }
  ],
  "reason": "Updated candidate status."
}
```

A JSON Patch-like structure may be used, but only allowlisted paths should be writable.

---

# Job API

Conceptual operations:

```text
GET    /jobs
POST   /jobs/discover
POST   /jobs/import
GET    /jobs/{job_id}
POST   /jobs/{job_id}/refresh
POST   /jobs/{job_id}/analyze
POST   /jobs/{job_id}/rank
POST   /jobs/{job_id}/select
POST   /jobs/{job_id}/skip
```

---

# Job Discovery Request

```json
{
  "sources": [
    {
      "source_type": "company_career_page",
      "url": ""
    }
  ],
  "filters": {
    "countries": [
      "US"
    ],
    "maximum_posting_age_days": 30
  }
}
```

---

# Package API

Conceptual operations:

```text
GET    /application-packages
POST   /application-packages
GET    /application-packages/{package_id}
POST   /application-packages/{package_id}/prepare
POST   /application-packages/{package_id}/refresh
POST   /application-packages/{package_id}/validate
POST   /application-packages/{package_id}/cancel
POST   /application-packages/{package_id}/archive
DELETE /application-packages/{package_id}
```

---

# Create Package Request

```json
{
  "candidate_profile_id": "candidate_default",
  "job_id": "job_001",
  "automation_mode": "review",
  "selected_resume_artifact_id": null
}
```

---

# Queue API

Conceptual operations:

```text
GET    /queues
POST   /queues
GET    /queues/{queue_id}
POST   /queues/{queue_id}/start
POST   /queues/{queue_id}/pause
POST   /queues/{queue_id}/resume
POST   /queues/{queue_id}/cancel
PATCH  /queues/{queue_id}/items/order
POST   /queues/{queue_id}/items/{queue_item_id}/skip
```

---

# Queue Create Request

```json
{
  "package_ids": [
    "package_001",
    "package_002"
  ],
  "strategy": "selected_order",
  "automation_mode": "review",
  "browser_profile_id": "profile_default",
  "continue_after_package_failure": true
}
```

---

# Review API

Conceptual operations:

```text
POST /application-packages/{package_id}/reviews
GET  /reviews/{review_id}
POST /reviews/{review_id}/apply-safe-corrections
POST /reviews/{review_id}/approve
POST /reviews/{review_id}/reject
POST /reviews/{review_id}/rerun
```

---

# Review Approval Request

```json
{
  "expected_package_version": 8,
  "review_id": "review_001",
  "decision": "approved",
  "acknowledged_warning_ids": [],
  "approved_artifact_versions": {
    "resume": 2,
    "cover_letter": 1,
    "answer_set": 3
  },
  "form_snapshot_hash": ""
}
```

---

# Readiness API

Conceptual operations:

```text
POST /application-packages/{package_id}/readiness/evaluate
GET  /application-packages/{package_id}/readiness
POST /application-packages/{package_id}/readiness/remediate
```

---

# Workflow API

Conceptual operations:

```text
GET  /workflows/{workflow_id}
POST /workflows/{workflow_id}/pause
POST /workflows/{workflow_id}/resume
POST /workflows/{workflow_id}/cancel
POST /workflows/{workflow_id}/recover
GET  /workflows/{workflow_id}/events
```

---

# User Intervention API

Conceptual operations:

```text
GET  /interventions
GET  /interventions/{intervention_id}
POST /interventions/{intervention_id}/complete
POST /interventions/{intervention_id}/cancel
```

---

# Missing Answer Completion Request

```json
{
  "answer": {
    "answer_type": "controlled_choice",
    "value": "no"
  },
  "reuse_policy": "this_application_only",
  "expected_package_version": 9
}
```

---

# Submission API

Conceptual operations:

```text
GET  /application-packages/{package_id}/submission
POST /application-packages/{package_id}/submission/prepare
POST /application-packages/{package_id}/submission/execute
POST /application-packages/{package_id}/submission/verify
POST /application-packages/{package_id}/submission/resolve-unknown
GET  /submission-attempts/{attempt_id}
```

---

# Submission Execute Request

```json
{
  "expected_package_version": 10,
  "review_approval_id": "approval_001",
  "submission_readiness_id": "readiness_001",
  "submission_attempt_id": "submission_attempt_001",
  "idempotency_key": "package_001_submission_attempt_001"
}
```

---

# Unknown Submission Resolution Request

```json
{
  "resolved_status": "submitted",
  "resolution_source": "user_dashboard_observation",
  "evidence_note": "The ATS dashboard lists the application as Submitted.",
  "confirmation_number": null
}
```

---

# History API

Conceptual operations:

```text
GET    /history
POST   /history/manual-records
GET    /history/{history_record_id}
PATCH  /history/{history_record_id}
POST   /history/{history_record_id}/status-updates
POST   /history/{history_record_id}/follow-up
POST   /history/export
POST   /history/reconcile
```

---

# History Status Update Request

```json
{
  "new_recruitment_status": "interview",
  "effective_date": "2026-07-20",
  "source": "user",
  "notes": ""
}
```

---

# Settings API

Conceptual operations:

```text
GET   /settings
PATCH /settings
POST  /settings/validate
GET   /settings/schemas
POST  /settings/test-provider
POST  /settings/test-browser
```

Sensitive secret values should use separate Secret Store operations.

---

# Health API

Conceptual operations:

```text
GET  /health
POST /health/check
GET  /health/components/{component}
```

---

# Maintenance API

Conceptual operations:

```text
POST /maintenance/backups
POST /maintenance/backups/{backup_id}/verify
POST /maintenance/backups/{backup_id}/restore
POST /maintenance/history/rebuild
POST /maintenance/packages/validate
POST /maintenance/locks/repair
POST /maintenance/diagnostics
POST /maintenance/migrations
```

---

# Schema Registry API

Conceptual operations:

```text
GET  /schemas
GET  /schemas/{schema_name}
GET  /schemas/{schema_name}/{version}
POST /schemas/validate
GET  /schemas/{schema_name}/compatibility
GET  /schemas/{schema_name}/migrations
```

The registry itself should be read-only during ordinary operation.

---

# Schema Validation Request

```json
{
  "schema_name": "ApplicationPackage",
  "schema_version": "1.0",
  "payload": {}
}
```

---

# Schema Validation Response

```json
{
  "status": "failed",
  "errors": [
    {
      "code": "INVALID_ENUM_VALUE",
      "path": "status",
      "value": "done",
      "allowed_values": [
        "ready",
        "submitted",
        "failed"
      ]
    }
  ]
}
```

---

# Schema Migration Contracts

A migration should implement:

```text
validate_source(payload)
migrate(payload)
validate_target(payload)
create_migration_record()
```

---

# Migration Result

```json
{
  "migration_id": "ApplicationPackage_1_0_to_1_1",
  "status": "success",
  "source_version": "1.0",
  "target_version": "1.1",
  "warnings": [],
  "preserved_unknown_fields": []
}
```

---

# Unknown Field Preservation

During compatible migrations and round trips:

* Preserve unknown optional fields when practical.
* Do not expose them as editable without a known schema.
* Do not preserve unknown security-critical instructions blindly.
* Record fields dropped by an incompatible migration.

---

# Default Values

Schemas should avoid defaults that alter candidate facts.

Safe defaults may include:

* Empty warning list.
* review required.
* automatic submission disabled.
* external telemetry disabled.
* no generic fallback override.
* no demographic inference.

Unsafe defaults include:

* Sponsorship No.
* legal answer No.
* relocation Yes.
* salary zero.
* demographic identity.
* submission succeeded.

---

# Required vs Optional Fields

A field should be required only when the entity cannot be interpreted safely without it.

Example:

* `package_id` required.
* `job_id` required.
* `confirmation_number` optional.
* `date_posted` optional.
* `legal_answer` not defaulted when missing.

---

# Derived Fields

Derived fields should be clearly marked.

Examples:

* Match score.
* current application status.
* display name.
* age of posting.
* next allowed action.

Consumers should not persist derived values as source facts unless required for snapshots.

---

# Snapshot Models

Application Packages should contain immutable snapshots of:

* Job.
* candidate context.
* candidate rules.
* artifact versions.
* provider configuration.
* schema versions.

Snapshots preserve historical reproducibility.

---

# Snapshot Header

```json
{
  "snapshot_id": "snapshot_001",
  "source_entity_id": "candidate_default",
  "source_entity_version": 4,
  "schema_version": "1.0",
  "content_hash": "",
  "captured_at": ""
}
```

---

# Mutable Reference vs Snapshot

Use a mutable reference when current state is desired.

Use a snapshot when historical reproducibility is required.

Example:

```text
Candidate profile page:
Current mutable candidate profile.

Submitted Application Package:
Immutable candidate-context snapshot.
```

---

# Data Redaction Contract

Services returning redacted data should identify the policy.

```json
{
  "value": "su***@gmail.com",
  "redaction": {
    "applied": true,
    "strategy": "mask",
    "original_available": true
  }
}
```

---

# Auditability Requirements

State-changing API responses should include or reference:

* Actor.
* operation ID.
* entity version.
* audit-event ID.
* timestamp.

---

# Command Result Metadata

```json
{
  "operation_id": "operation_001",
  "audit_event_id": "audit_001",
  "entity_version": 6
}
```

---

# API Logging Requirements

Log:

* Request ID.
* route or operation.
* actor type.
* entity IDs.
* status.
* duration.
* error code.
* response size category.

Do not log:

* Secret values.
* passwords.
* cookies.
* government IDs.
* full sensitive payloads.
* unrestricted prompts.

---

# Request Size Limits

The API should define maximum sizes for:

* JSON request body.
* file upload.
* batch request count.
* event metadata.
* free-text note.
* job description.
* provider output.

Oversized requests should return a structured error.

---

# Rate Limits

Local rate limits may protect:

* Final submission command.
* account creation.
* login attempts.
* provider test requests.
* file uploads.
* maintenance operations.
* sensitive reveal operations.

Rate limiting should not interfere with normal local use.

---

# API Timeouts

Immediate operations should have bounded timeouts.

Workflow operations should return a workflow ID rather than hold a request open indefinitely.

---

# Cancellation Contract

Cancellable workflows should support:

```json
{
  "cancellation_scope": "current_package",
  "reason": "user_requested"
}
```

The response should state whether cancellation is:

* Completed.
* pending safe boundary.
* impossible because final submission is in progress.
* converted to submission verification.

---

# Delete Contract

Deletion requests should include scope.

```json
{
  "delete_package": true,
  "delete_artifacts": true,
  "delete_screenshots": true,
  "delete_history_record": false,
  "confirmation": "delete_submitted_package"
}
```

The backend should reject ambiguous deletion requests.

---

# Export Contract

```json
{
  "export_type": "application_history",
  "format": "xlsx",
  "filters": {},
  "include_sensitive_data": false,
  "encrypt": false
}
```

---

# Contract Test Requirements

Every public service contract should have tests for:

* Valid payload.
* missing required field.
* invalid type.
* invalid enum.
* unknown optional field.
* incompatible version.
* oversized payload.
* stale entity version.
* unauthorized action.
* invalid state transition.
* sensitive-field masking.
* idempotent retry.

---

# Schema Test Fixtures

Recommended fixture categories:

```text
valid_minimal
valid_complete
valid_previous_minor
invalid_missing_required
invalid_enum
invalid_date
invalid_reference
invalid_sensitive_policy
unknown_optional_field
incompatible_major_version
```

---

# Provider Schema Tests

Test:

* Valid JSON.
* malformed JSON.
* extra commentary outside JSON.
* missing source references.
* unsupported claims.
* secret leakage.
* wrong company.
* invalid enum.
* truncated output.
* incorrect schema version.

---

# Browser Contract Tests

Test:

* Form model extraction.
* field model completeness.
* option normalization.
* action classification.
* browser action plan.
* action verification result.
* conditional-field update.
* unsupported control.
* final action ambiguity.

---

# Submission Contract Tests

Test:

* Attempt creation.
* final-click initiation.
* verification pending.
* strong evidence.
* weak evidence.
* Submission Unknown.
* duplicate attempt.
* idempotency conflict.
* resolution.
* invalid retry.

---

# History Contract Tests

Test:

* New record.
* update.
* manual record.
* submission status.
* recruitment status.
* CSV mapping.
* XLSX mapping.
* unknown optional fields.
* schema migration.
* duplicate package ID.

---

# Compatibility Test Matrix

Example:

| Producer    | Consumer     | Expected                            |
| ----------- | ------------ | ----------------------------------- |
| Package 1.0 | Consumer 1.0 | Pass                                |
| Package 1.0 | Consumer 1.1 | Pass                                |
| Package 1.1 | Consumer 1.0 | Pass when added fields are optional |
| Package 2.0 | Consumer 1.x | Reject and require migration        |

---

# Schema Governance

Every schema change should include:

* Change proposal.
* affected services.
* compatibility analysis.
* security and privacy review.
* migration requirement.
* updated fixtures.
* contract tests.
* documentation.
* release note.

---

# Schema Owner

Each major schema should have an owner.

Examples:

```text
CandidateProfile:
Candidate Data Service

ApplicationPackage:
Package Service

FormModel:
Browser and ATS Integration

SubmissionResult:
Submission Verification Service

HistoryRecord:
Application History Service
```

---

# Schema Change Review

A change should be rejected when it:

* Makes a sensitive field less protected without justification.
* changes submission meaning ambiguously.
* merges distinct work-authorization facts.
* removes provenance.
* removes entity versioning.
* makes state transitions implicit.
* allows arbitrary file paths.
* breaks auditability.
* introduces a default that may create false information.

---

# Deprecation Period

A compatible deprecation may remain supported for:

* One major release.
* or a documented migration window.

Security-critical deprecated fields may be removed sooner with a mandatory migration.

---

# Schema Documentation

Each schema should document:

* Purpose.
* owner.
* version.
* fields.
* required fields.
* enum meanings.
* sensitive fields.
* validation rules.
* compatibility.
* examples.
* migrations.
* known limitations.

---

# Generated Types

Where practical, schema definitions should generate:

* Backend data classes.
* frontend TypeScript types.
* validation code.
* API documentation.
* test fixtures.

Generated types reduce drift between frontend and backend.

---

# Generated Type Restrictions

Generated code should not replace:

* Semantic validation.
* policy validation.
* state-transition rules.
* security checks.
* provenance checks.

---

# API Documentation

The local API should provide developer documentation.

Possible formats:

* OpenAPI.
* generated JSON Schema documentation.
* Markdown service contracts.

The documentation should not expose:

* Secrets.
* real candidate data.
* browser cookies.
* internal filesystem paths.

---

# OpenAPI Usage

An OpenAPI document may define:

* Routes.
* request schemas.
* response schemas.
* error responses.
* authentication.
* examples.

Domain schemas may be referenced from the Schema Registry.

---

# Schema Registry Health

The Health Service should verify:

* Registry loads.
* schema files exist.
* checksums match.
* active schemas validate.
* migrations are available for stored older versions.
* no duplicate schema identifiers exist.

---

# Schema Registry Failure

If a critical schema is unavailable:

* Block affected operations.
* enter degraded or Safe mode.
* preserve existing data.
* do not write unvalidated payloads.
* provide diagnostic information.

---

# Data Model Completion Criteria

The canonical data model phase is complete when models exist for:

* Candidate profile.
* employment.
* education.
* skills.
* work authorization.
* preferences.
* job.
* job analysis.
* job match.
* Application Package.
* artifact.
* application answer.
* question.
* Application Plan.
* review.
* readiness.
* queue.
* workflow.
* checkpoint.
* browser session.
* page.
* form.
* field.
* user intervention.
* ATS adapter.
* submission attempt.
* submission evidence.
* submission result.
* history record.
* history event.
* audit event.
* configuration.
* health.
* backup.
* migration.
* provider request and output.

---

# API Completion Criteria

The API layer is complete when:

* Command and query boundaries are defined.
* Request and response envelopes are consistent.
* Errors are structured.
* identifiers are stable.
* entity versions support concurrency.
* state transitions are backend validated.
* next allowed actions are returned.
* list APIs support filtering and pagination.
* batch operations report per-item results.
* idempotency is supported.
* final submission uses strict idempotency.
* sensitive responses are masked.
* arbitrary filesystem paths are rejected.
* local UI operations have documented contracts.
* workflow operations return durable workflow IDs.
* event streaming supports reconnect and deduplication.
* contract tests pass.

---

# Schema Registry Completion Criteria

The Schema Registry is complete when:

* Every canonical schema has a name and version.
* Schema files are stored in a predictable structure.
* checksums are validated.
* schemas have owners.
* active, deprecated, and retired states exist.
* compatibility policies are documented.
* incompatible major versions are rejected.
* compatible minor versions are accepted correctly.
* migration paths are registered.
* provider outputs are schema validated.
* browser and ATS models are schema validated.
* event schemas are versioned.
* schema health checks exist.
* schema fixtures and compatibility tests pass.

---

# Definition of Contract Safety

Contracts are safe when:

* Missing values are not interpreted as false.
* unknown submission states are not interpreted as failure.
* unknown security states do not silently pass.
* sensitive values cannot be retrieved through general APIs.
* final submission cannot be repeated through normal retries.
* stale clients cannot overwrite newer package versions.
* arbitrary file paths cannot enter file operations.
* provider outputs cannot directly authorize browser or submission actions.
* approval references exact artifact versions.
* history distinguishes submission status from recruitment outcome.

---

# Required API Scenarios

## Create Application Package

Expected:

* Candidate and job references validated.
* package ID created.
* entity version starts at 1.
* audit event created.
* duplicate package policy applied.
* package returned in Draft or Preparing state.

---

## Stale Package Update

A client submits expected version 4 while package is version 5.

Expected:

* Conflict response.
* no overwrite.
* current version returned.
* UI asked to reload.

---

## Queue Unready Package

Expected:

* Precondition error.
* failed readiness checks returned.
* no queue item created.

---

## Approve Outdated Review

Resume changed after review.

Expected:

* Approval rejected.
* active artifact mismatch returned.
* review rerun required.

---

## Duplicate Submission Command

Same submission-attempt key is sent twice.

Expected:

* Existing attempt returned.
* no second final click.
* verification state preserved.

---

## Unknown Submission Retry

Package is in Submission Unknown state.

Expected:

* New submission command rejected.
* verification or resolution actions returned.

---

## Sensitive Field Request

General package query requests government ID.

Expected:

* Raw value not returned.
* secure reference or blocked status returned.
* access policy enforced.

---

## Invalid File Reference

API payload includes `../../private.pdf`.

Expected:

* Validation failure.
* no file read.
* security event recorded.

---

## Provider Malformed Output

Reasoning provider returns invalid JSON.

Expected:

* Schema validation fails.
* bounded repair or retry.
* no domain entity created from invalid output.
* error logged without sensitive content.

---

## New Optional Schema Field

Producer sends Package schema 1.1 with an optional metadata field.

Consumer supports 1.0 under forward-compatible policy.

Expected:

* Payload accepted.
* unknown field preserved or ignored safely.
* no behavior change.

---

## Incompatible Major Schema

Producer sends Package schema 2.0.

Consumer supports only 1.x.

Expected:

* Incompatible-version error.
* migration required.
* no partial mutation.

---

## History Recruitment Update

A submitted application becomes Rejected.

Expected:

* Submission status remains Submitted.
* recruitment status becomes Rejected.
* event written.
* entity version incremented.

---

## Event Stream Reconnect

Client reconnects after sequence 120.

Expected:

* Events after 120 replayed when available.
* duplicates ignored by event ID.
* authoritative state reloaded when replay gap exists.

---

# Definition of Phase Completion

The API Contracts, Data Models, and Schema Registry phase is complete when the platform can answer:

```text
What entity is being exchanged?

Which schema version defines it?

Which fields are required?

Which values are sensitive?

Where did each important value come from?

Which state transitions are allowed?

How are concurrent updates prevented?

How is a repeated command handled?

How are incompatible versions detected?

How can stored data be migrated?

How can a consumer validate the payload?

How can an action be audited?
```

The answers should come from versioned schemas, service contracts, validation rules, and registry metadata.

---

# Summary

The API and schema layer provides the shared language of the platform.

It defines how components represent and exchange:

* Candidate facts.
* jobs.
* rankings.
* documents.
* application answers.
* packages.
* reviews.
* readiness.
* queues.
* browser forms.
* ATS capabilities.
* submission evidence.
* application history.
* security metadata.
* audit events.
* operational state.

The platform should not depend on undocumented payloads or implicit assumptions.

Every important boundary should use:

* Stable identifiers.
* versioned schemas.
* structured validation.
* explicit state models.
* source provenance.
* sensitive-data annotations.
* optimistic concurrency.
* idempotency.
* structured errors.
* compatibility rules.
* migrations.

The most consequential contracts—review approval, browser execution, final submission, and submission verification—must bind to exact package, artifact, and workflow versions.

The backend remains authoritative.

The user interface, reasoning provider, ATS adapter, and browser automation engine may request or propose actions, but none may bypass the domain contracts that protect factual accuracy, privacy, workflow integrity, and submission safety.
