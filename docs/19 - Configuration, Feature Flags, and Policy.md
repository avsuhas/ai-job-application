# 19 - Configuration, Feature Flags, and Policy Management

## LLM-Powered Autonomous Job Search & Application Platform

Version: 1.0

---

# Purpose

This document defines the configuration architecture, feature-flag system, policy-management framework, override hierarchy, validation rules, rollout controls, persistence model, audit requirements, migration strategy, and operational safeguards for the LLM-Powered Autonomous Job Search and Application Platform.

The platform must support configurable behavior across:

* Candidate profiles.
* Job discovery.
* Job ranking.
* Resume generation.
* Cover-letter generation.
* Application-answer handling.
* Review.
* Readiness.
* Browser automation.
* ATS adapters.
* Generic form execution.
* Queue orchestration.
* Submission.
* Application history.
* Security.
* Privacy.
* Logging.
* Retention.
* Backups.
* Experimental features.

Configuration directly affects consequential behavior.

Examples include:

* Whether automatic submission is allowed.
* Whether a particular ATS adapter may run automatically.
* Whether demographic questions are answered.
* How future sponsorship questions are handled.
* Whether optional cover letters are generated.
* Whether the queue pauses after a package failure.
* Whether raw page HTML is retained.
* Whether an unknown domain may receive candidate data.
* Whether provider fallback is permitted.
* Whether a sensitive field requires manual entry.

Configuration must therefore be:

* Typed.
* Versioned.
* Validated.
* Auditable.
* Secure.
* Explainable.
* Recoverable.
* Applied consistently.

The platform should not depend on scattered constants, hidden environment variables, ad hoc JSON keys, UI-only toggles, or undocumented command-line switches.

---

# Core Principle

Every configurable behavior should be resolved through one authoritative, versioned policy pipeline.

```text
Built-In Safe Defaults
        |
        v
Environment Profile
        |
        v
User Configuration
        |
        v
Candidate Profile Policy
        |
        v
Company or ATS Policy
        |
        v
Application Package Override
        |
        v
Runtime Safety Constraints
        |
        v
Resolved Effective Policy
```

A lower-level override must never bypass a higher-priority security or safety constraint.

---

# Objectives

The configuration and policy system should:

* Provide safe defaults.
* Use typed schemas.
* Separate secrets from normal configuration.
* Define a clear precedence hierarchy.
* Distinguish settings from policies.
* Distinguish policies from feature flags.
* Support candidate-specific configuration.
* Support company-specific and ATS-specific behavior.
* Support package-specific overrides.
* Support environment profiles.
* Support experimental capabilities safely.
* Support runtime kill switches.
* Validate incompatible combinations.
* Explain the effective value of every setting.
* Record configuration changes.
* Bind consequential actions to resolved policies.
* Support rollback.
* Support schema migration.
* Preserve unknown compatible fields.
* Avoid configuration drift.
* Prevent UI and backend disagreement.
* Keep automatic submission disabled unless explicitly eligible.
* Allow safe downgrade to Review or Manual mode.

---

# Scope

This document covers:

* Configuration categories.
* Configuration sources.
* precedence.
* typed settings.
* environment profiles.
* feature flags.
* rollout states.
* policy definitions.
* policy resolution.
* candidate rules.
* ATS and employer overrides.
* package overrides.
* runtime constraints.
* kill switches.
* configuration validation.
* secrets references.
* UI behavior.
* persistence.
* auditing.
* migrations.
* backups.
* import and export.
* testing.
* operational management.

This document does not define:

* Candidate facts.
* ATS adapter implementation.
* browser selectors.
* prompt contents.
* final submission verification logic.
* cloud-based remote configuration services.
* enterprise policy administration.

---

# Terminology

## Configuration

A typed value controlling platform behavior.

Examples:

* Browser visible mode.
* Provider timeout.
* queue retry count.
* history workbook location.

---

## Policy

A rule determining whether an action is permitted, required, blocked, or downgraded.

Examples:

* Government IDs are never provided automatically.
* Automatic submission requires a Stable ATS adapter.
* Unknown legal answers require user input.
* Submission Unknown pauses the queue.

---

## Feature Flag

A controlled switch that enables or disables a capability independently of general configuration.

Examples:

* Workday experimental adapter.
* Generic form submission.
* encrypted package archives.
* provider fallback.
* automatic account creation.

---

## Override

A scoped value that replaces or narrows a broader setting.

Examples:

* Review mode required for one company.
* Cover letter disabled for one package.
* Automatic submission disabled for one ATS.

---

## Constraint

A non-overridable rule imposed by security, integrity, compatibility, or operational health.

Examples:

* Final submission blocked when audit storage is unavailable.
* Automatic mode blocked for a degraded adapter.
* Candidate data blocked from an insecure HTTP page.

---

## Effective Policy

The final resolved result after applying defaults, settings, overrides, feature flags, and runtime constraints.

---

# Configuration Architecture

```text
Configuration System
    |
    +-- Schema Registry
    +-- Defaults Provider
    +-- Environment Profile Loader
    +-- User Configuration Repository
    +-- Candidate Policy Repository
    +-- ATS and Company Override Repository
    +-- Package Override Repository
    +-- Feature Flag Registry
    +-- Runtime Constraint Provider
    +-- Policy Resolver
    +-- Configuration Validator
    +-- Change Audit Service
    +-- Migration Service
    +-- Effective Configuration API
```

---

# Separation of Responsibilities

## Configuration Repository

Stores non-secret user settings.

## Feature Flag Registry

Defines capabilities, status, eligibility, and rollout constraints.

## Policy Repository

Stores behavioral rules and scoped overrides.

## Secret Store

Stores credentials and encryption keys separately.

## Policy Resolver

Produces the effective decision for a specific context.

## Configuration Validator

Rejects invalid or unsafe combinations.

## Runtime Constraint Provider

Applies current health, adapter status, security, and workflow constraints.

## Change Audit Service

Records configuration and policy changes.

---

# Configuration Categories

Recommended top-level categories:

```text
application
storage
candidate
jobs
ranking
documents
answers
review
readiness
browser
ats
generic_form
execution
submission
history
reasoning
security
privacy
logging
observability
retention
backup
interface
operations
experimental
```

---

# Application Configuration

Examples:

```json
{
  "application": {
    "environment": "local",
    "default_candidate_profile_id": "candidate_default",
    "default_automation_mode": "review",
    "automatic_submission_enabled": false,
    "safe_mode": false,
    "maintenance_mode": false
  }
}
```

---

# Storage Configuration

Examples:

```json
{
  "storage": {
    "data_root": "",
    "temporary_root": "",
    "cache_enabled": true,
    "maximum_cache_size_mb": 2048,
    "minimum_free_disk_mb": 5120
  }
}
```

Storage paths should be resolved and validated by the backend.

---

# Candidate Configuration

Candidate configuration may include:

* Active candidate profile.
* source precedence.
* required validation.
* profile refresh behavior.
* standard answer reuse.
* candidate-data snapshot policy.

Example:

```json
{
  "candidate": {
    "active_profile_id": "candidate_default",
    "require_profile_validation": true,
    "require_work_authorization_confirmation": true,
    "source_precedence": [
      "structured_profile",
      "user_confirmed",
      "resume",
      "imported_notes"
    ]
  }
}
```

---

# Job Discovery Configuration

Examples:

```json
{
  "jobs": {
    "target_countries": [
      "US"
    ],
    "maximum_posting_age_days": 30,
    "include_jobs_without_posting_date": true,
    "refresh_existing_jobs": true,
    "maximum_jobs_per_source": 200
  }
}
```

---

# Ranking Configuration

Examples:

```json
{
  "ranking": {
    "minimum_recommended_score": 75,
    "strong_match_score": 88,
    "hard_block_on_country_mismatch": true,
    "hard_block_on_clearance_mismatch": true,
    "hard_block_on_explicit_no_sponsorship": false,
    "weight_profile": "default_software_engineering"
  }
}
```

---

# Document Configuration

Examples:

```json
{
  "documents": {
    "resume_tailoring_enabled": true,
    "default_resume_artifact_id": null,
    "resume_output_formats": [
      "pdf",
      "docx"
    ],
    "maximum_resume_pages": 2,
    "cover_letter_policy": "when_required_or_high_value",
    "preserve_user_edits": true
  }
}
```

---

# Answer Configuration

Examples:

```json
{
  "answers": {
    "reuse_standard_answers": true,
    "save_user_answers_only_with_approval": true,
    "optional_question_policy": "answer_when_confident",
    "narrative_generation_enabled": true,
    "maximum_narrative_regeneration_attempts": 2
  }
}
```

---

# Review Configuration

Examples:

```json
{
  "review": {
    "preparation_review_required": true,
    "pre_submission_review_required": true,
    "block_on_high_severity_findings": true,
    "allow_approval_with_medium_warnings": true,
    "maximum_correction_rounds": 3,
    "invalidate_approval_on_material_change": true
  }
}
```

---

# Readiness Configuration

Examples:

```json
{
  "readiness": {
    "require_current_duplicate_check": true,
    "require_document_hash_validation": true,
    "require_browser_health": true,
    "require_adapter_health": true,
    "allow_ready_with_warnings": true
  }
}
```

---

# Browser Configuration

Examples:

```json
{
  "browser": {
    "visible": true,
    "profile_id": "profile_default",
    "maximum_concurrent_sessions": 1,
    "navigation_timeout_seconds": 45,
    "page_stability_timeout_seconds": 20,
    "maximum_action_retries": 3,
    "capture_error_screenshots": true
  }
}
```

---

# ATS Configuration

Examples:

```json
{
  "ats": {
    "enabled_adapters": [
      "greenhouse",
      "lever"
    ],
    "allow_generic_fallback": true,
    "require_stable_adapter_for_automatic_mode": true,
    "employer_overrides_enabled": true
  }
}
```

---

# Generic Form Configuration

Examples:

```json
{
  "generic_form": {
    "enabled": true,
    "allow_form_completion": true,
    "allow_final_submission": false,
    "minimum_field_confidence": 90,
    "minimum_final_action_confidence": 99,
    "unknown_required_field_policy": "request_user_input"
  }
}
```

---

# Execution Configuration

Examples:

```json
{
  "execution": {
    "continue_after_package_failure": true,
    "pause_on_user_action": true,
    "pause_on_security_warning": true,
    "pause_on_submission_unknown": true,
    "maximum_stage_attempts": 3,
    "maximum_queue_size": 25
  }
}
```

---

# Submission Configuration

Examples:

```json
{
  "submission": {
    "automatic_submission_enabled": false,
    "require_submission_snapshot": true,
    "require_submission_lock": true,
    "require_strong_verification": true,
    "allow_user_resolution_of_unknown": true,
    "duplicate_reapplication_window_days": 180
  }
}
```

---

# History Configuration

Examples:

```json
{
  "history": {
    "csv_enabled": true,
    "xlsx_enabled": true,
    "csv_path": "",
    "xlsx_path": "",
    "create_backup_before_write": true,
    "reconcile_on_startup": true
  }
}
```

---

# Reasoning Configuration

Examples:

```json
{
  "reasoning": {
    "provider": "claude",
    "model": "",
    "api_key_reference": "secret://reasoning/claude",
    "fallback_enabled": false,
    "fallback_model": null,
    "request_timeout_seconds": 60,
    "maximum_request_attempts": 2,
    "provider_context_minimization": true
  }
}
```

---

# Security Configuration

Examples:

```json
{
  "security": {
    "require_https": true,
    "allow_unknown_domains": false,
    "block_payment_requests": true,
    "government_id_policy": "never_provide",
    "require_upload_manifest": true,
    "block_on_audit_integrity_failure": true,
    "block_on_redaction_failure": true
  }
}
```

---

# Privacy Configuration

Examples:

```json
{
  "privacy": {
    "external_telemetry": false,
    "retain_raw_html": false,
    "retain_browser_screenshots": true,
    "demographic_policy": "use_stored_preference",
    "disability_policy": "decline_when_optional",
    "veteran_status_policy": "use_stored_preference",
    "salary_logging": "category_only"
  }
}
```

---

# Logging and Observability Configuration

Examples:

```json
{
  "logging": {
    "level": "INFO",
    "debug_enabled": false,
    "trace_enabled": false,
    "structured_output": true,
    "redaction_required": true
  },
  "observability": {
    "local_metrics_enabled": true,
    "health_checks_enabled": true,
    "diagnostic_bundle_retention_days": 14
  }
}
```

---

# Retention Configuration

Examples:

```json
{
  "retention": {
    "application_logs_days": 30,
    "debug_logs_days": 7,
    "error_screenshots_days": 30,
    "confirmation_screenshots_days": 365,
    "failed_packages_days": 180,
    "submitted_packages": "until_deleted"
  }
}
```

---

# Backup Configuration

Examples:

```json
{
  "backup": {
    "enabled": true,
    "location": "",
    "encrypt": true,
    "encryption_key_reference": "secret://backup/default",
    "daily_count": 7,
    "weekly_count": 4,
    "include_browser_profiles": false
  }
}
```

---

# Interface Configuration

Examples:

```json
{
  "interface": {
    "theme": "system",
    "density": "comfortable",
    "time_zone": "America/New_York",
    "date_format": "localized",
    "show_advanced_details": false
  }
}
```

---

# Configuration Sources

The platform may resolve configuration from the following sources:

```text
Built-In Defaults
Environment Profile
System Configuration
User Configuration
Candidate Profile Settings
ATS Override
Employer Override
Package Override
Runtime Command Override
Runtime Safety Constraints
```

---

# Precedence Order

Recommended precedence from lowest to highest:

```text
1. Built-In Defaults
2. Environment Profile
3. User Configuration
4. Candidate Profile Configuration
5. ATS-Level Override
6. Employer-Level Override
7. Package-Level Override
8. Explicit Runtime Command Override
9. Runtime Safety Constraint
10. Global Kill Switch
```

Higher-priority values may narrow behavior.

They should not be allowed to weaken immutable security constraints.

---

# Precedence Example

Suppose:

```text
Global default:
Automatic submission enabled.

ATS override:
Review mode required for Workday.

Employer override:
Manual mode required for Company X.

Package override:
Automatic requested.
```

Effective result:

```text
Manual mode
```

The package override cannot weaken the employer restriction.

---

# Configuration Merge Rules

The system should define deterministic merge behavior.

---

## Scalar Values

Higher-precedence value replaces lower-precedence value.

---

## Objects

Objects merge recursively unless marked atomic.

---

## Lists

Every list field should declare a merge strategy:

```text
replace
append
union
intersection
remove
```

Example:

```json
{
  "field": "enabled_adapters",
  "merge_strategy": "intersection"
}
```

A package should not enable an adapter globally disabled by policy.

---

## Maps

Maps merge by key unless the schema declares replacement.

---

## Null Values

Null handling should be explicit.

Possible meanings:

```text
inherit
clear
unknown
disabled
```

A field should not rely on ambiguous null semantics.

---

# Configuration Provenance

Every resolved value should include provenance.

Example:

```json
{
  "path": "submission.automatic_submission_enabled",
  "effective_value": false,
  "source": "ats_override",
  "source_id": "workday",
  "overridden_values": [
    {
      "value": true,
      "source": "user_configuration"
    }
  ],
  "constraints": [
    "adapter_not_stable"
  ]
}
```

---

# Effective Configuration Model

```json
{
  "resolution_id": "config_resolution_001",
  "context": {
    "candidate_profile_id": "candidate_default",
    "package_id": "package_001",
    "company": "Example Corp",
    "ats_adapter_id": "workday",
    "workflow_stage": "submission"
  },
  "schema_version": "1.0",
  "values": {},
  "policy_decisions": [],
  "feature_flags": [],
  "constraints": [],
  "resolved_at": ""
}
```

---

# Effective Configuration Snapshot

Before browser execution and final submission, the platform should create a configuration snapshot.

The snapshot should include:

* Configuration schema version.
* candidate policy version.
* ATS override version.
* employer override version.
* feature-flag states.
* runtime constraints.
* final automation mode.
* security policy.
* privacy policy.
* submission policy.
* content hash.

This snapshot supports reproducibility and auditing.

---

# Settings vs Policies

Settings describe preferences or operating parameters.

Policies determine permissions or obligations.

Example:

```text
Setting:
Browser page timeout = 45 seconds.

Policy:
Unknown legal answers require user input.
```

Policies should not be stored as arbitrary booleans when their semantics require conditions and outcomes.

---

# Policy Model

```json
{
  "policy_id": "policy_submission_automatic_001",
  "policy_type": "submission_eligibility",
  "version": 1,
  "scope": {
    "level": "global"
  },
  "priority": 100,
  "conditions": [],
  "effect": "require_review",
  "reason": "Automatic submission is disabled by default.",
  "enabled": true,
  "created_at": "",
  "updated_at": ""
}
```

---

# Policy Effects

Supported policy effects:

```text
allow
deny
require
require_review
require_user_input
downgrade_to_review
downgrade_to_manual
pause
warn
redact
retain
delete
```

---

# Policy Conditions

Examples:

```json
{
  "all": [
    {
      "field": "ats.status",
      "operator": "equals",
      "value": "stable"
    },
    {
      "field": "review.status",
      "operator": "equals",
      "value": "approved"
    },
    {
      "field": "readiness.status",
      "operator": "equals",
      "value": "ready"
    }
  ]
}
```

---

# Supported Condition Operators

```text
equals
not_equals
in
not_in
greater_than
greater_than_or_equal
less_than
less_than_or_equal
exists
not_exists
contains
matches
all
any
not
```

Regular-expression use should be restricted to controlled configuration.

---

# Policy Scope

Possible policy scopes:

```text
global
environment
candidate_profile
country
job_family
company
ats
package
workflow_stage
field_category
```

---

# Policy Priority

Policies should have explicit priority.

Higher-priority policies may override lower-priority preference policies.

Security-deny policies should be non-overridable.

---

# Policy Conflict Resolution

When policies conflict:

1. Apply immutable constraints.
2. Apply explicit deny rules.
3. Apply more specific scope.
4. Apply higher priority.
5. Apply safer effect.
6. Record conflict.
7. require user or maintenance review when ambiguity remains.

---

# Safer Effect Ordering

Recommended safety ordering:

```text
deny
manual_only
require_user_input
require_review
warn
allow
```

When two equally authoritative policies conflict, choose the safer behavior.

---

# Policy Decision Model

```json
{
  "decision_id": "policy_decision_001",
  "policy_type": "sensitive_field_handling",
  "subject": "government_id",
  "decision": "deny",
  "matched_policy_ids": [
    "policy_government_id_never_provide"
  ],
  "overridden_policy_ids": [],
  "reason": "Government identifiers are configured as never provide.",
  "resolved_at": ""
}
```

---

# Candidate Rules

Candidate rules are long-lived user-specific policies.

Examples:

* Apply only to jobs in selected countries.
* Avoid positions requiring active security clearance.
* Answer future sponsorship as Yes.
* Do not disclose current salary.
* Prefer Review mode for legal questions.
* Do not generate cover letters unless required.
* Exclude specific companies.
* Minimum salary threshold.
* Maximum travel percentage.
* Relocation conditions.

---

# Candidate Rule Model

```json
{
  "rule_id": "candidate_rule_001",
  "candidate_profile_id": "candidate_default",
  "category": "salary",
  "status": "active",
  "condition": {
    "field": "job.salary.maximum",
    "operator": "less_than",
    "value": 160000
  },
  "effect": "skip_job",
  "reason": "Below candidate minimum salary.",
  "version": 2,
  "last_confirmed_at": ""
}
```

---

# Candidate Rule Categories

```text
location
country
remote
salary
employment_type
job_family
seniority
company
work_authorization
sponsorship
travel
relocation
security_clearance
document
answer
review
submission
privacy
```

---

# Candidate Rule Safety

Candidate rules should not:

* Invent candidate facts.
* automatically answer unknown legal questions.
* weaken security controls.
* bypass duplicate prevention.
* override Submission Unknown.
* authorize arbitrary file uploads.
* override unknown-domain blocking.

---

# ATS Overrides

ATS-specific overrides may define:

* Allowed automation mode.
* adapter stability.
* generic fallback.
* login behavior.
* review requirement.
* final-action confidence threshold.
* submission-verification requirements.
* known unsupported widgets.
* retry limits.

Example:

```json
{
  "ats_id": "workday",
  "version": 4,
  "overrides": {
    "automation_mode_maximum": "review",
    "require_user_review": true,
    "allow_generic_fallback": false,
    "require_dashboard_reconciliation_on_weak_confirmation": true
  }
}
```

---

# Employer Overrides

Employer-specific overrides may define:

* ATS variant.
* required document behavior.
* special legal questions.
* known account requirements.
* manual-only workflows.
* known confirmation behavior.
* company-specific answer restrictions.

Example:

```json
{
  "company_key": "example_corp",
  "version": 1,
  "overrides": {
    "automation_mode_maximum": "manual",
    "cover_letter_policy": "required",
    "account_creation_policy": "manual_only"
  }
}
```

Employer overrides must not contain candidate-specific sensitive values.

---

# Package Overrides

Package-level overrides may include:

* Selected resume.
* cover-letter decision.
* automation mode.
* question answer for this application only.
* manual review requirement.
* priority.
* skip behavior.
* supporting-document selection.

---

# Package Override Model

```json
{
  "package_id": "package_001",
  "override_version": 2,
  "values": {
    "automation_mode": "review",
    "documents.cover_letter_policy": "omit",
    "execution.priority": 120
  },
  "reason": "Candidate requested review for this employer.",
  "created_by": {
    "actor_type": "user",
    "actor_id": "local_user"
  },
  "created_at": ""
}
```

---

# Package Override Restrictions

Package overrides may not:

* Enable a globally disabled feature.
* enable automatic mode for a degraded adapter.
* bypass sensitive-field policy.
* bypass duplicate protection.
* bypass review approval.
* change candidate master facts silently.
* convert Submission Unknown to ready for retry.

---

# Runtime Constraints

Runtime constraints are temporary conditions derived from the current system state.

Examples:

* Provider unavailable.
* Browser unavailable.
* ATS adapter degraded.
* Audit storage unwritable.
* Low disk space.
* Wrong browser account.
* Unknown domain.
* Submission lock active.
* Package stale.
* Migration pending.
* Safe mode active.

---

# Runtime Constraint Model

```json
{
  "constraint_id": "constraint_adapter_degraded",
  "category": "ats_health",
  "scope": {
    "ats_adapter_id": "greenhouse"
  },
  "effect": "downgrade_to_review",
  "severity": "high",
  "reason": "Recent adapter regression tests failed.",
  "active": true,
  "created_at": ""
}
```

---

# Constraint Precedence

Runtime safety constraints override configuration and feature flags.

Example:

```text
Configured:
Automatic submission enabled.

Runtime:
Audit writer unavailable.

Effective:
Submission blocked.
```

---

# Automation Mode Resolution

Supported automation modes:

```text
automatic
review
manual
disabled
```

Safety order:

```text
disabled
manual
review
automatic
```

The effective mode should be the safest mode required by any applicable policy or constraint.

---

# Automation Mode Resolution Example

Inputs:

```text
User setting: automatic
ATS policy: review
Employer policy: manual
Runtime health: healthy
```

Effective mode:

```text
manual
```

---

# Feature Flag System

Feature flags control capability availability independently of standard settings.

Examples:

```text
automatic_submission
generic_form_engine
generic_form_final_submission
workday_adapter
provider_fallback
automatic_account_creation
automatic_legal_attestation
encrypted_package_archives
multiple_candidate_profiles
browser_parallelism
email_confirmation_reconciliation
```

---

# Feature Flag Model

```json
{
  "flag_id": "generic_form_final_submission",
  "display_name": "Generic Form Final Submission",
  "description": "",
  "status": "disabled",
  "default_enabled": false,
  "risk_level": "high",
  "owner": "ats",
  "introduced_version": "1.1.0",
  "expires_at": null,
  "dependencies": [
    "generic_form_engine"
  ],
  "constraints": [],
  "metadata": {}
}
```

---

# Feature Flag Statuses

```text
disabled
internal
experimental
beta
enabled
deprecated
retired
```

---

# Feature Risk Levels

```text
low
medium
high
critical
```

Critical-risk flags include:

* Automatic submission.
* generic final submission.
* automatic legal attestation.
* automatic account creation.
* browser concurrency.

---

# Feature Flag Eligibility

A feature may be:

```text
available
unavailable
eligible
ineligible
enabled
disabled
forced_off
```

Availability and enablement are distinct.

Example:

```text
Feature exists:
Available.

ATS adapter degraded:
Ineligible.

User requested feature:
Enabled request.

Effective:
Forced off.
```

---

# Feature Flag Dependencies

A flag may depend on:

* Another flag.
* Minimum application version.
* schema version.
* adapter status.
* health status.
* environment.
* candidate policy.
* completed quality gate.

---

# Feature Dependency Example

```json
{
  "flag_id": "automatic_submission",
  "dependencies": [
    {
      "type": "feature_flag",
      "id": "submission_verification",
      "required_state": "enabled"
    },
    {
      "type": "quality_gate",
      "id": "automatic_submission_gate",
      "required_state": "passed"
    }
  ]
}
```

---

# Feature Flag Evaluation

```json
{
  "flag_id": "automatic_submission",
  "requested": true,
  "available": true,
  "eligible": false,
  "effective_enabled": false,
  "reasons": [
    "ATS adapter is not Stable.",
    "Package contains a warning requiring review."
  ]
}
```

---

# Feature Flags vs Configuration

Feature flag:

```text
Is the capability available at all?
```

Configuration:

```text
How should the available capability behave?
```

Example:

```text
Feature flag:
Generic Form Engine enabled.

Configuration:
Minimum field confidence = 90.
```

---

# Feature Flags vs Policies

Feature flag:

```text
Can this feature be used?
```

Policy:

```text
May it be used in this context?
```

Example:

```text
Feature:
Automatic submission exists and is enabled.

Policy:
Company X requires Manual mode.
```

Effective result:

```text
Automatic submission not permitted for Company X.
```

---

# Kill Switches

Kill switches are high-priority feature controls intended for immediate risk reduction.

Required kill switches:

```text
all_browser_execution
all_automatic_submission
specific_ats_adapter
generic_form_engine
generic_form_final_submission
provider_requests
automatic_account_creation
automatic_legal_attestation
history_writes
```

---

# Kill Switch Model

```json
{
  "kill_switch_id": "all_automatic_submission",
  "active": true,
  "reason": "Submission verification regression detected.",
  "activated_by": {
    "actor_type": "user",
    "actor_id": "local_user"
  },
  "activated_at": "",
  "expires_at": null
}
```

---

# Kill Switch Behavior

Activating a kill switch should:

* Prevent new affected operations.
* preserve active state.
* avoid deleting workflows.
* allow safe cleanup.
* not reinterpret previous results.
* produce an audit event.
* update the UI immediately.
* require explicit deactivation.

---

# Active Workflow Behavior

When a kill switch activates during execution:

## Before Final Submission

Pause or downgrade safely.

## During Final Submission

Continue verification of the existing attempt.

Do not cancel verification or repeat the click.

## After Verified Submission

Allow history synchronization.

---

# Rollout Controls

Feature rollouts may be scoped by:

* Environment.
* candidate profile.
* ATS.
* employer.
* job family.
* package.
* application version.
* percentage cohort in future multi-user systems.

For the single-user MVP, explicit scoped allowlists are preferred over percentage rollouts.

---

# Allowlist Model

```json
{
  "feature_flag_id": "automatic_submission",
  "allowlist": {
    "ats_adapters": [
      "greenhouse"
    ],
    "companies": [],
    "candidate_profiles": [
      "candidate_default"
    ],
    "workflow_variants": [
      "greenhouse_standard_v1"
    ]
  }
}
```

---

# Denylist Model

Denylists may block:

* Companies.
* ATS variants.
* workflow signatures.
* domains.
* field categories.
* browser versions.
* provider models.

Deny rules should override allow rules when equally scoped.

---

# Feature Expiration

Temporary flags should include:

* Owner.
* reason.
* review date.
* expiration date.
* removal plan.

Expired experimental flags should default to disabled.

---

# Feature Flag Lifecycle

```text
Proposed
    |
    v
Internal
    |
    v
Experimental
    |
    v
Beta
    |
    v
Enabled
    |
    v
Deprecated
    |
    v
Retired
```

Promotion should require evidence from the testing strategy.

---

# Promotion Requirements

Before promoting a flag:

* Functional tests pass.
* security tests pass.
* privacy tests pass.
* recovery tests pass.
* relevant quality gate passes.
* documentation is updated.
* rollback is available.
* known limitations are recorded.

---

# Policy Registry

The system should maintain a registry of supported policy types.

Recommended policy types:

```text
job_selection
document_generation
answer_resolution
sensitive_field_handling
review_requirement
readiness_requirement
browser_execution
ats_fallback
submission_eligibility
submission_verification
duplicate_application
history_retention
provider_context
logging_redaction
backup
```

---

# Policy Registry Entry

```json
{
  "policy_type": "submission_eligibility",
  "schema_version": "1.0",
  "owner": "submission",
  "supported_effects": [
    "allow",
    "deny",
    "require_review",
    "downgrade_to_manual"
  ],
  "security_critical": true
}
```

---

# Policy Ownership

Each policy type should have one owning domain module.

Examples:

```text
Sensitive field handling:
Security.

Submission eligibility:
Submission.

ATS fallback:
ATS.

Review requirement:
Review.

Job selection:
Jobs.

Retention:
Operations and Privacy.
```

---

# Policy Evaluation Interface

Conceptual interface:

```text
PolicyResolver

    resolve(policy_type, context)
    explain(decision_id)
    validate_policy(policy)
    list_applicable_policies(context)
    simulate(policy_change, context)
```

---

# Policy Context

```json
{
  "candidate_profile_id": "candidate_default",
  "job_id": "job_001",
  "package_id": "package_001",
  "company_key": "example_corp",
  "country_code": "US",
  "ats_adapter_id": "greenhouse",
  "adapter_status": "stable",
  "workflow_stage": "submission",
  "field_category": null,
  "system_health": {}
}
```

---

# Policy Explanation

The platform should explain why a decision was made.

Example:

```json
{
  "decision": "require_review",
  "summary": "Review mode is required for this application.",
  "reasons": [
    "The ATS adapter is Beta.",
    "The application includes a sensitive legal question."
  ],
  "matched_policies": [
    "policy_beta_adapter_review",
    "policy_legal_question_review"
  ]
}
```

---

# Policy Simulation

Before saving a material policy change, the platform should simulate impact.

Example:

```text
Changing future sponsorship policy affects:

6 prepared packages
2 queued packages
1 approved review

Required actions:

Refresh sponsorship answers
Invalidate affected approvals
Rerun readiness
```

---

# Policy Change Impact Model

```json
{
  "change_id": "policy_change_preview_001",
  "affected_packages": 6,
  "affected_queues": 1,
  "approvals_invalidated": 2,
  "required_refresh_categories": [
    "answers",
    "review",
    "readiness"
  ],
  "blocking_impacts": []
}
```

---

# Material Configuration Changes

Material changes include:

* Candidate work-authorization rules.
* salary minimum.
* legal-answer policy.
* demographic policy.
* active resume.
* automatic submission.
* review requirement.
* sensitive-field policy.
* ATS adapter enablement.
* provider model.
* duplicate window.
* unknown-submission behavior.

Material changes should trigger:

* Impact analysis.
* audit event.
* dependent package invalidation.
* readiness refresh.
* approval invalidation when applicable.

---

# Non-Material Changes

Examples:

* UI theme.
* table density.
* default sort order.
* non-sensitive notification preference.

These should not invalidate packages.

---

# Configuration Classification

Each setting should declare its impact class.

```text
presentation
operational
workflow
artifact
candidate_fact
security
privacy
submission_critical
```

---

# Setting Metadata

```json
{
  "path": "submission.automatic_submission_enabled",
  "type": "boolean",
  "default": false,
  "impact_class": "submission_critical",
  "sensitive": false,
  "requires_confirmation": true,
  "requires_audit": true,
  "invalidates": [
    "submission_readiness"
  ]
}
```

---

# Configuration Schema

Configuration should use a versioned schema.

Example:

```json
{
  "schema_version": "1.0",
  "application": {},
  "storage": {},
  "candidate": {},
  "jobs": {},
  "ranking": {},
  "documents": {},
  "answers": {},
  "review": {},
  "readiness": {},
  "browser": {},
  "ats": {},
  "generic_form": {},
  "execution": {},
  "submission": {},
  "history": {},
  "reasoning": {},
  "security": {},
  "privacy": {},
  "logging": {},
  "observability": {},
  "retention": {},
  "backup": {},
  "interface": {},
  "operations": {},
  "experimental": {}
}
```

---

# Configuration Validation Levels

```text
syntactic
structural
semantic
cross_setting
environment
policy
runtime
```

---

# Syntactic Validation

Checks:

* Valid JSON or YAML.
* valid encoding.
* valid date and duration format.
* valid numbers.

---

# Structural Validation

Checks:

* Required sections.
* field types.
* enums.
* array shapes.
* object structure.

---

# Semantic Validation

Checks:

* Retry counts are non-negative.
* percentages are within range.
* retention periods are valid.
* paths are resolvable.
* score thresholds are ordered correctly.

---

# Cross-Setting Validation

Examples:

* Automatic submission cannot be enabled while review is globally disabled and no automatic gate has passed.
* Generic final submission requires Generic Form Engine.
* Encrypted backups require an encryption key reference.
* Parallel browser count cannot exceed available profile count.
* Raw HTML retention cannot be unlimited under strict privacy mode.

---

# Environment Validation

Checks:

* Data root writable.
* browser profile exists.
* Secret Store available.
* configured provider supported.
* ATS adapters installed.
* backup path writable.
* local UI binding secure.

---

# Policy Validation

Checks:

* Effect supported for policy type.
* scope is valid.
* priority is allowed.
* conditions reference known fields.
* non-overridable constraints are not weakened.
* policy does not create an impossible state.

---

# Runtime Validation

Checks:

* Feature eligibility.
* current health.
* adapter status.
* active locks.
* package state.
* submission state.
* migration state.

---

# Configuration Error Model

```json
{
  "code": "CONFIGURATION_CONFLICT",
  "path": "submission.automatic_submission_enabled",
  "message": "Automatic submission cannot be enabled because the required quality gate has not passed.",
  "severity": "error",
  "blocking": true,
  "recommended_action": "Use Review mode."
}
```

---

# Configuration Warnings

Warnings may include:

* High debug retention.
* optional provider unavailable.
* Beta adapter enabled.
* low disk threshold.
* cover-letter generation disabled.
* external telemetry enabled.
* browser profile stored in a synchronized folder.

Warnings should not hide blocking errors.

---

# Safe Defaults

The platform should default to:

```text
Review mode
Automatic submission disabled
Visible browser
One browser session
CAPTCHA manual
MFA manual
Unknown legal answer requires user input
Government IDs never provided
External telemetry disabled
Raw HTML retention disabled
Generic final submission disabled
Duplicate blocking enabled
Submission Unknown pauses queue
Strong verification required
Audit persistence required
Provider context minimization enabled
```

---

# Default Deny Areas

The following should default to denied or manual-only:

* Government identifiers.
* bank information.
* payment information.
* passport scans.
* immigration-document numbers.
* automatic legal attestations.
* background-check questionnaires.
* third-party assessments.
* arbitrary local file uploads.
* insecure HTTP submission.
* unknown domains.

---

# Secrets Separation

Configuration should store secret references only.

Example:

```json
{
  "reasoning": {
    "api_key_reference": "secret://reasoning/claude"
  }
}
```

Prohibited:

```json
{
  "reasoning": {
    "api_key": "sk-..."
  }
}
```

---

# Secret Reference Validation

The configuration validator may check:

* Reference syntax.
* Secret Store availability.
* secret existence.
* provider compatibility.
* expiration metadata.

It should not return the secret value.

---

# Environment Variables

Environment variables may override limited development settings.

Recommended allowed categories:

* Environment profile.
* test data root.
* local port.
* explicit secret references.
* debug mode.

Environment variables should not silently enable automatic submission.

---

# Command-Line Overrides

Command-line overrides may support:

* Safe mode.
* maintenance mode.
* data root.
* local port.
* test profile.
* log level.
* synthetic mode.

High-risk settings should require explicit confirmation or should be disallowed through command-line overrides.

---

# Raw Configuration Editor

An advanced raw editor may be available.

Requirements:

* Validate before saving.
* show schema errors.
* create backup.
* show impact preview.
* block plaintext secrets.
* prevent unsafe combinations.
* support rollback.

---

# Configuration User Interface

Recommended Settings sections:

```text
General
Candidate
Jobs and Ranking
Documents
Answers
Review
Browser
ATS Adapters
Queue
Submission
History
Reasoning Provider
Privacy
Security
Logging
Retention
Backups
Feature Flags
Advanced
```

---

# Setting Presentation

Each setting should show:

* Display name.
* description.
* current effective value.
* configured value.
* source.
* default.
* impact.
* restart requirement.
* related policy.
* validation status.

---

# Effective vs Configured Value

Example:

```text
Configured automation mode:
Automatic

Effective automation mode:
Review

Reason:
The Greenhouse adapter is currently Beta.
```

The UI should never hide the difference.

---

# Inherited Values

Inherited settings should display:

```text
Inherited from global configuration
```

or:

```text
Inherited from ATS policy
```

The user should be able to inspect the inheritance chain.

---

# Override UI

The UI should support scoped override creation for:

* Candidate profile.
* ATS.
* employer.
* package.

It should clearly display scope.

Example:

```text
This change applies only to applications at Example Corp.
```

---

# Dangerous Setting Confirmation

High-risk changes should require explicit confirmation.

Examples:

* Enable automatic submission.
* enable external telemetry.
* allow unknown domains.
* enable generic final submission.
* enable automatic legal attestation.
* disable duplicate blocking.
* reduce screenshot retention protections.

---

# Confirmation Content

The dialog should state:

* Exact setting.
* current value.
* new value.
* affected scope.
* consequences.
* invalidated packages.
* rollback option.

---

# Policy Management UI

The policy interface should allow the user to:

* View policy categories.
* inspect active policies.
* inspect effective decisions.
* add permitted candidate rules.
* disable editable policies.
* see protected policies.
* preview impact.
* review audit history.

---

# Protected Policies

Some policies should be built-in and non-editable.

Examples:

* No automatic retry after an unknown submission.
* No provider access to passwords.
* No arbitrary file upload.
* No payment-information entry.
* No final submission without an attempt record.
* No Submitted status without verification or explicit user resolution.

---

# Feature Flags UI

Each flag should show:

* Name.
* status.
* risk level.
* availability.
* eligibility.
* effective state.
* dependencies.
* limitations.
* owner.
* expiry.
* rollback behavior.

---

# Experimental Feature Warning

Example:

```text
Experimental feature

This capability has limited test coverage and may require Manual mode.
It cannot enable automatic submission unless its release gate passes.
```

---

# Automatic Submission Enablement Flow

Enabling automatic submission should require:

1. User selects Enable.
2. Platform runs eligibility check.
3. Platform shows supported ATS adapters.
4. Platform shows disallowed workflows.
5. Platform shows safety requirements.
6. User confirms.
7. Change is audited.
8. Automatic mode remains package- and policy-dependent.

---

# Automatic Submission Eligibility Result

```json
{
  "eligible": false,
  "blocking_reasons": [
    "No ATS adapter has Stable automatic eligibility.",
    "Automatic Submission quality gate is not passed."
  ],
  "warnings": [],
  "recommended_mode": "review"
}
```

---

# Configuration Persistence

Recommended file:

```text
configuration/config.json
```

Additional scoped files may include:

```text
configuration/profiles/{profile_id}.json
configuration/ats/{ats_id}.json
configuration/companies/{company_key}.json
```

Package overrides should remain inside the relevant Application Package.

---

# Persistence Requirements

Configuration writes should:

* Use atomic replacement.
* validate before commit.
* create backup.
* increment entity version.
* update content hash.
* add audit event.
* preserve previous valid configuration.
* avoid partial writes.

---

# Configuration Repository Model

```json
{
  "configuration_id": "user_default",
  "schema_version": "1.0",
  "entity_version": 8,
  "content_hash": "",
  "updated_at": "",
  "updated_by": {
    "actor_type": "user",
    "actor_id": "local_user"
  }
}
```

---

# Optimistic Concurrency

Configuration updates should include:

```json
{
  "expected_version": 8
}
```

A stale update should fail instead of overwriting a newer configuration.

---

# Configuration Change Model

```json
{
  "change_id": "config_change_001",
  "scope": {
    "type": "global",
    "id": "user_default"
  },
  "changes": [
    {
      "path": "review.pre_submission_review_required",
      "old_value": true,
      "new_value": false
    }
  ],
  "reason": "",
  "impact_preview_id": "",
  "created_at": ""
}
```

---

# Audit Requirements

Audit events are required for changes to:

* Candidate rules.
* work-authorization policy.
* sensitive-field policy.
* demographic policy.
* legal-answer handling.
* automatic submission.
* ATS enablement.
* generic final submission.
* provider fallback.
* browser profile.
* duplicate rules.
* retention.
* external telemetry.
* kill switches.
* protected policy overrides.
* feature-flag promotion.

---

# Configuration Audit Event

```json
{
  "event_type": "configuration.updated",
  "scope": "global",
  "path": "submission.automatic_submission_enabled",
  "old_value": false,
  "new_value": true,
  "actor": {
    "actor_type": "user",
    "actor_id": "local_user"
  },
  "reason": "",
  "affected_packages": [],
  "timestamp": ""
}
```

Sensitive values should not appear in audit events.

---

# Effective Policy Audit

Consequential actions should reference the policy resolution used.

Examples:

* Resume generated under document policy X.
* Browser executed under automation policy Y.
* Submission authorized under submission policy Z.
* Sensitive field blocked by policy A.

---

# Policy Snapshot Binding

Final submission should bind to:

* Package version.
* review approval.
* readiness result.
* effective configuration snapshot.
* policy resolution ID.
* feature-flag evaluation.
* runtime constraint snapshot.

---

# Configuration Drift

Configuration drift occurs when:

* UI displays a stale value.
* package uses an old policy.
* runtime environment differs from stored settings.
* adapter metadata changes.
* feature status changes.
* a configuration file is edited externally.

---

# Drift Detection

The platform should compare:

* Stored content hash.
* loaded configuration hash.
* package policy snapshot.
* current effective policy.
* schema version.
* adapter version.
* feature registry version.

---

# Drift Result

```json
{
  "status": "drift_detected",
  "changes": [
    {
      "path": "ats.greenhouse.status",
      "previous": "stable",
      "current": "degraded"
    }
  ],
  "required_actions": [
    "Rerun submission readiness."
  ]
}
```

---

# External File Changes

If a configuration file changes outside the application:

* Detect hash mismatch.
* validate the new file.
* do not apply invalid content.
* record external modification.
* show impact.
* invalidate dependent state when necessary.

---

# Hot Reload

Low-risk settings may support hot reload.

Examples:

* UI theme.
* table density.
* log level.
* optional notifications.

High-risk settings should require controlled reload or workflow boundary.

Examples:

* Browser profile.
* provider.
* ATS adapter enablement.
* submission policy.
* security policy.
* storage root.

---

# Restart Requirements

Each setting should declare:

```text
none
ui_reload
service_reload
browser_restart
application_restart
maintenance_mode
```

---

# Active Workflow Changes

When configuration changes during an active workflow:

* Completed stages remain historically bound to prior snapshots.
* Future safe stages may use updated settings only after revalidation.
* Approval may be invalidated.
* browser execution may pause.
* final submission should require a fresh policy resolution.

---

# Configuration Change During Submission

After final-click initiation:

* Do not change the active attempt's policy snapshot.
* continue verification.
* apply new settings only to future attempts.
* record the timing of the configuration change.

---

# Configuration Backup

Configuration should be included in:

* Full backups.
* pre-upgrade backups.
* pre-migration backups.
* pre-restore backups.

Secret values remain excluded.

---

# Configuration Export

The user may export:

* Non-secret settings.
* feature states.
* candidate rules.
* employer overrides.
* ATS overrides.
* policy definitions.
* audit summary.

---

# Export Manifest

```json
{
  "export_type": "configuration",
  "schema_version": "1.0",
  "includes": [
    "user_configuration",
    "candidate_rules",
    "feature_flags",
    "ats_overrides"
  ],
  "excludes": [
    "secret_values",
    "browser_cookies"
  ],
  "created_at": ""
}
```

---

# Configuration Import

Import should:

1. Validate archive or file.
2. inspect schema version.
3. detect secrets.
4. compare current settings.
5. show changes.
6. show safety impact.
7. back up current configuration.
8. import into staging.
9. validate effective policy.
10. apply after confirmation.

---

# Import Conflict Handling

Conflicts may be resolved by:

```text
keep_current
use_imported
merge
skip
manual_review
```

Security-critical settings should not merge ambiguously.

---

# Configuration Migration

Configuration schema changes require versioned migrations.

---

# Migration Requirements

Each migration should define:

* Source version.
* target version.
* transformed fields.
* defaults added.
* deprecated fields.
* compatibility.
* rollback.
* validation.
* test fixtures.

---

# Migration Example

```json
{
  "migration_id": "configuration_1_0_to_1_1",
  "source_version": "1.0",
  "target_version": "1.1",
  "changes": [
    "Split automatic_mode into default_automation_mode and automatic_submission_enabled."
  ]
}
```

---

# Unsafe Migration Defaults

A migration must not default to:

* Automatic submission enabled.
* unknown-domain access allowed.
* government ID automatic.
* external telemetry enabled.
* duplicate blocking disabled.
* review disabled.

New high-risk features should default to disabled.

---

# Deprecated Settings

Deprecated settings should include:

* Replacement.
* deprecation version.
* planned removal version.
* migration behavior.

Example:

```json
{
  "path": "application.auto_apply",
  "status": "deprecated",
  "replacement": "submission.automatic_submission_enabled",
  "removal_version": "2.0"
}
```

---

# Unknown Configuration Fields

For compatible minor versions:

* Preserve unknown optional fields.
* do not execute unknown behavior.
* show a compatibility warning.
* avoid dropping fields during round trips.

Unknown security-critical fields should require version compatibility review.

---

# Configuration API

Conceptual operations:

```text
GET   /api/v1/settings
PATCH /api/v1/settings
POST  /api/v1/settings/validate
POST  /api/v1/settings/preview-impact
GET   /api/v1/settings/effective
GET   /api/v1/settings/provenance
POST  /api/v1/settings/export
POST  /api/v1/settings/import
```

---

# Feature Flag API

Conceptual operations:

```text
GET   /api/v1/feature-flags
GET   /api/v1/feature-flags/{flag_id}
POST  /api/v1/feature-flags/{flag_id}/evaluate
POST  /api/v1/feature-flags/{flag_id}/enable
POST  /api/v1/feature-flags/{flag_id}/disable
POST  /api/v1/kill-switches/{kill_switch_id}/activate
POST  /api/v1/kill-switches/{kill_switch_id}/deactivate
```

---

# Policy API

Conceptual operations:

```text
GET    /api/v1/policies
POST   /api/v1/policies
GET    /api/v1/policies/{policy_id}
PATCH  /api/v1/policies/{policy_id}
POST   /api/v1/policies/resolve
POST   /api/v1/policies/simulate
GET    /api/v1/policies/decisions/{decision_id}
```

Protected policies should be read-only.

---

# Configuration Update Request

```json
{
  "expected_version": 8,
  "changes": [
    {
      "operation": "replace",
      "path": "review.pre_submission_review_required",
      "value": true
    }
  ],
  "reason": "Require review for all applications."
}
```

---

# Feature Enablement Request

```json
{
  "expected_registry_version": 5,
  "scope": {
    "type": "candidate_profile",
    "id": "candidate_default"
  },
  "acknowledged_risks": [
    "review_required",
    "adapter_limitations"
  ],
  "reason": ""
}
```

---

# Effective Policy Query

```json
{
  "policy_type": "submission_eligibility",
  "context": {
    "package_id": "package_001",
    "ats_adapter_id": "greenhouse"
  }
}
```

---

# Effective Policy Response

```json
{
  "decision": "require_review",
  "effective_automation_mode": "review",
  "matched_policies": [],
  "constraints": [],
  "explanation": "",
  "resolution_id": "policy_resolution_001"
}
```

---

# Configuration Service Interface

Conceptual interface:

```text
ConfigurationService

    load_configuration()
    validate_configuration(configuration)
    get_effective_configuration(context)
    update_configuration(change_request)
    preview_change_impact(change_request)
    export_configuration(selection)
    import_configuration(source)
    migrate_configuration(target_version)
```

---

# Feature Flag Service Interface

```text
FeatureFlagService

    list_flags()
    evaluate_flag(flag_id, context)
    enable_flag(flag_id, scope)
    disable_flag(flag_id, scope)
    activate_kill_switch(kill_switch_id, reason)
    deactivate_kill_switch(kill_switch_id)
    validate_dependencies(flag_id)
```

---

# Policy Service Interface

```text
PolicyService

    register_policy(policy)
    validate_policy(policy)
    resolve_policy(policy_type, context)
    explain_decision(decision_id)
    simulate_change(change, context)
    list_applicable_policies(context)
```

---

# Configuration Testing Strategy

Testing should cover:

* Defaults.
* precedence.
* merge behavior.
* feature eligibility.
* policy conflicts.
* validation.
* persistence.
* auditing.
* migrations.
* UI behavior.
* active workflow changes.
* runtime constraints.

---

# Unit Tests

Unit-test:

* Scalar precedence.
* list merge strategies.
* null semantics.
* policy condition operators.
* policy priority.
* safer-effect selection.
* feature dependencies.
* kill-switch precedence.
* effective mode resolution.
* provenance.
* impact classification.
* configuration hashing.
* version conflicts.
* migration transforms.

---

# Integration Tests

Integration-test:

* Configuration file loading.
* OS-specific paths.
* Secret Store references.
* candidate rule resolution.
* ATS override resolution.
* employer override resolution.
* package override resolution.
* runtime health constraints.
* API update and audit.
* UI effective-value display.
* package invalidation.
* approval invalidation.

---

# Required Test Scenarios

## Default Startup

No user configuration exists.

Expected:

* Safe defaults load.
* Review mode active.
* automatic submission disabled.
* external telemetry disabled.
* configuration file may be initialized.
* health check passes.

---

## Invalid Configuration

Retry count is negative.

Expected:

* Validation fails.
* previous valid configuration remains active.
* normal operation does not use invalid settings.
* error is actionable.

---

## Plaintext Secret

Configuration includes an API key.

Expected:

* Validation fails.
* value is redacted.
* migration to Secret Store is offered.
* key does not enter logs.

---

## Automatic Submission Without Gate

User enables automatic submission before its quality gate passes.

Expected:

* Requested value may be stored as desired preference only if supported.
* effective value remains disabled.
* blocking reason shown.
* no package becomes automatically eligible.

---

## ATS Downgrade

ATS adapter changes from Stable to Degraded.

Expected:

* Effective automatic mode becomes Review or Manual.
* queued packages are revalidated.
* approvals may remain valid only if unaffected.
* automatic submission is blocked.

---

## Employer Manual Override

Global mode is Automatic, but employer override is Manual.

Expected:

* Effective package mode is Manual.
* provenance shows employer override.
* package override cannot weaken it.

---

## Package Review Override

Global mode is Review.

User sets one package to Manual.

Expected:

* Effective mode is Manual.
* change is audited.
* other packages remain unchanged.

---

## Runtime Low Disk Constraint

Configuration permits submission.

Disk falls below critical threshold.

Expected:

* runtime constraint blocks final submission.
* effective policy explanation shows low disk.
* configuration itself is not rewritten.

---

## Kill Switch During Queue

Global automatic-submission kill switch activates.

Expected:

* No new automatic submissions begin.
* current pre-submit workflow pauses or downgrades.
* in-progress verification continues.
* queue state remains durable.

---

## Candidate Work-Authorization Change

Future sponsorship changes from No to Yes.

Expected:

* affected packages identified.
* sponsorship answers invalidated.
* review approval invalidated where relevant.
* readiness reruns.
* unrelated document content remains intact when valid.

---

## External File Modification

Configuration file is manually edited.

Expected:

* hash change detected.
* new content validated.
* invalid content not activated.
* external modification event recorded.

---

## Feature Dependency Failure

Generic final submission is enabled while Generic Form Engine is disabled.

Expected:

* validation fails.
* dependent flag remains ineffective.
* dependency explanation shown.

---

## Feature Expiration

Experimental flag reaches expiration.

Expected:

* effective state becomes disabled.
* user receives notice.
* existing historical packages retain snapshots.
* future workflows do not use the feature.

---

## Policy Conflict

One policy allows automatic submission and another equally scoped policy requires review.

Expected:

* safer effect selected.
* conflict recorded.
* explanation includes both policies.

---

## Non-Overridable Policy

Package override attempts to allow government-ID entry.

Expected:

* override rejected.
* protected policy remains active.
* security event recorded.

---

## Configuration Migration

Old configuration uses deprecated `auto_apply`.

Expected:

* backup created.
* field migrated.
* automatic submission remains disabled unless explicitly and safely enabled.
* migration report generated.

---

## Concurrent Settings Update

Two UI tabs update version 8.

First succeeds and creates version 9.

Second submits expected version 8.

Expected:

* conflict.
* no overwrite.
* second tab reloads current configuration.

---

## Active Submission Configuration Change

User disables automatic submission after final click.

Expected:

* current verification continues.
* no retry or cancellation.
* future submissions disabled.
* change audit includes active-attempt context.

---

## Configuration Export

User exports configuration.

Expected:

* non-secret settings included.
* secret values excluded.
* manifest generated.
* export audit event created.

---

## Configuration Import

Imported configuration enables external telemetry and unknown domains.

Expected:

* changes highlighted.
* explicit confirmation required.
* safety validation applied.
* import may be rejected based on protected policy.

---

# Feature Flag Test Matrix

Each high-risk feature should test:

```text
Unavailable
Available but Ineligible
Eligible but Disabled
Enabled
Forced Off
Expired
Deprecated
Dependency Missing
Kill Switch Active
```

---

# Policy Test Matrix

Each policy type should test:

```text
No Matching Policy
One Matching Policy
Multiple Compatible Policies
Conflicting Policies
More Specific Override
Protected Deny
Runtime Constraint
Unknown Condition Field
Invalid Effect
```

---

# Configuration Security Tests

Test:

* Path traversal in storage paths.
* plaintext secrets.
* malicious regex.
* oversized configuration.
* unknown high-risk field.
* insecure local UI binding.
* TLS verification disabled.
* upload root set to filesystem root.
* external telemetry enabled without consent.
* protected policy mutation.
* malformed import archive.

---

# Configuration Performance

Configuration resolution should be efficient enough for:

* Page-level field decisions.
* package readiness.
* queue admission.
* submission checks.

Recommended approach:

* Cache immutable validated configuration.
* cache policy indexes.
* invalidate cache on version change.
* include resolution IDs.
* avoid reading files for every field interaction.

---

# Resolution Cache

Cache key may include:

```text
Configuration version
Candidate profile version
ATS override version
Employer override version
Package override version
Feature registry version
Runtime constraint version
Context hash
```

---

# Cache Safety

Do not use cached effective policy when:

* Package version changed.
* adapter status changed.
* kill switch changed.
* security health changed.
* submission state changed.
* candidate rule changed.

---

# Operational Monitoring

Useful metrics:

* Configuration validation failures.
* policy conflict count.
* feature forced-off count.
* package invalidations.
* approval invalidations.
* kill-switch activations.
* external file modifications.
* migration failures.
* automatic-mode downgrade rate.
* protected-policy override attempts.

---

# Health Checks

Configuration health should verify:

* Schema loads.
* current configuration validates.
* active feature flags have valid dependencies.
* policy registry loads.
* protected policies exist.
* secret references are resolvable.
* no expired active flags.
* no conflicting critical policies.
* effective automatic mode is safe.
* configuration backup exists.

---

# Configuration Health Result

```json
{
  "component": "configuration",
  "status": "healthy",
  "schema_version": "1.0",
  "entity_version": 8,
  "warnings": [],
  "blocking_issues": []
}
```

---

# Failure Behavior

When configuration cannot be loaded safely:

* Start in Safe mode.
* use only immutable safe defaults where possible.
* disable browser execution.
* disable provider requests when credentials are uncertain.
* disable submission.
* allow configuration inspection and restore.
* preserve the invalid file for diagnosis.

---

# Policy Registry Failure

When the policy registry is unavailable:

* Block actions requiring policy authorization.
* allow read-only inspection.
* do not assume allow.
* use protected deny defaults.
* enter degraded or Safe mode.

---

# Feature Registry Failure

When feature status cannot be resolved:

* Treat high-risk features as disabled.
* preserve existing workflow state.
* allow safe verification of active submission attempts.
* show a health warning.

---

# Configuration Documentation

Every setting should document:

* Path.
* type.
* default.
* allowed values.
* description.
* impact class.
* restart requirement.
* security classification.
* related policies.
* invalidation behavior.
* deprecation status.

---

# Generated Settings Reference

The schema may generate:

* Backend typed settings.
* frontend setting forms.
* API documentation.
* default configuration.
* validation messages.
* settings reference documentation.

---

# Configuration Ownership

Recommended ownership:

| Category                  | Owning Module |
| ------------------------- | ------------- |
| Candidate                 | Candidate     |
| Jobs and Ranking          | Jobs          |
| Documents                 | Documents     |
| Answers                   | Answers       |
| Review                    | Review        |
| Readiness                 | Readiness     |
| Browser                   | Browser       |
| ATS and Generic Form      | ATS           |
| Execution                 | Orchestration |
| Submission                | Submission    |
| History                   | History       |
| Security and Privacy      | Security      |
| Logging and Observability | Observability |
| Backup and Maintenance    | Operations    |
| UI Presentation           | Frontend      |

The Configuration module manages storage and resolution but does not redefine domain semantics.

---

# Change Review Requirements

Expanded review is required for changes to:

* Safe defaults.
* precedence.
* automation-mode resolution.
* protected policies.
* submission eligibility.
* sensitive-field handling.
* feature dependencies.
* kill-switch behavior.
* unknown-submission policy.
* secret handling.
* configuration migration.

---

# Completion Criteria

The Configuration, Feature Flags, and Policy Management system is complete when:

* All settings are typed.
* Configuration schema is versioned.
* Safe defaults exist.
* Secrets are referenced, not stored.
* Precedence is deterministic.
* Merge strategies are documented.
* Effective values include provenance.
* Candidate rules are modeled.
* ATS overrides are supported.
* employer overrides are supported.
* package overrides are supported.
* runtime constraints override unsafe configuration.
* feature flags have lifecycle states.
* high-risk flags have dependencies and eligibility checks.
* kill switches exist.
* protected policies cannot be weakened.
* policy conflicts resolve safely.
* policy decisions are explainable.
* material changes produce impact previews.
* dependent packages are invalidated correctly.
* approvals are invalidated when necessary.
* configuration writes are atomic and versioned.
* changes are audited.
* migrations and rollback work.
* import and export are safe.
* active-workflow configuration changes are handled safely.
* UI shows configured and effective values.
* tests cover precedence, conflicts, flags, constraints, and migrations.

---

# Definition of Configuration Completion

The configuration system is complete when the platform can reliably answer:

```text
What value is configured?

What value is effective?

Where did the value come from?

Which settings were overridden?

Which policies applied?

Which feature flags are enabled?

Why is a requested feature unavailable?

Which runtime constraint changed the outcome?

Will this change invalidate existing packages?

Does the change require restart or review?

Can the prior configuration be restored?
```

---

# Definition of Policy Safety

Policy management is safe when:

* A lower-level override cannot weaken a protected rule.
* Unknown policy states default to safer behavior.
* automatic submission requires explicit eligibility.
* feature availability does not imply permission.
* runtime health can block unsafe operations.
* Submission Unknown cannot be configured into an automatic retry.
* sensitive-field policies cannot be bypassed by package overrides.
* candidate facts are not created through configuration defaults.
* policy changes are auditable and reversible.

---

# Required Reference Policies

The platform should ship with protected reference policies for:

```text
No final submission without a durable attempt record
No automatic retry after Submission Unknown
No Submitted status without verification or explicit resolution
No provider access to credentials
No arbitrary local file upload
No payment or bank-information entry
No automatic CAPTCHA bypass
No automatic MFA bypass
No demographic inference
No legal-answer guessing
No automatic government-ID entry
No insecure HTTP transmission of sensitive data
No automatic mode for degraded ATS adapters
No submission when audit persistence is unavailable
```

---

# Summary

The configuration and policy layer controls how the platform behaves across candidates, jobs, packages, ATS platforms, workflows, and operational environments.

It should provide:

* Typed settings.
* safe defaults.
* explicit precedence.
* candidate rules.
* ATS and employer overrides.
* package-specific behavior.
* feature flags.
* kill switches.
* runtime constraints.
* policy explanations.
* impact previews.
* auditing.
* migrations.
* rollback.

The most important distinction is:

```text
Configuration expresses a preference.

Policy determines permission.

Runtime constraints enforce safety.
```

The most important resolution rule is:

```text
The effective behavior is always the safest applicable result.
```

The most important feature-flag rule is:

```text
Enabling a feature does not bypass policy, readiness, security, or quality gates.
```

The platform should make every consequential behavior explainable by showing:

* The requested setting.
* the effective setting.
* the source.
* applicable policies.
* active constraints.
* resulting allowed actions.

Configuration should increase flexibility without reducing candidate accuracy, privacy, workflow integrity, or submission safety.
