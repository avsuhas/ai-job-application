# 18 - Repository Structure, Module Boundaries, and Code Organization

## LLM-Powered Autonomous Job Search & Application Platform

Version: 1.0

---

# Purpose

This document defines the repository structure, source-code organization, module boundaries, dependency rules, package conventions, shared-library policy, adapter layout, testing layout, and code-ownership model for the LLM-Powered Autonomous Job Search and Application Platform.

The platform includes many interconnected capabilities:

* Candidate Knowledge Base processing.
* Job discovery and normalization.
* Job analysis and ranking.
* Application Package creation.
* Resume and cover-letter generation.
* Application-answer preparation.
* Review and readiness.
* Browser automation.
* ATS adapters.
* Generic form handling.
* Queue orchestration.
* Submission verification.
* Application history.
* Security and privacy.
* Logging and audit trails.
* Local APIs.
* User interface.
* Deployment and maintenance.

Without explicit module boundaries, the codebase could gradually become:

* One large orchestration script.
* A set of circularly dependent services.
* ATS-specific logic mixed into browser primitives.
* Candidate facts embedded in prompt code.
* File paths passed freely across modules.
* UI components controlling domain transitions directly.
* Submission behavior duplicated across adapters.
* Security policies implemented inconsistently.
* Schemas drifting between frontend and backend.
* Tests that require the full platform to run.

The repository should make architectural boundaries visible in the filesystem and enforce them through imports, interfaces, tests, and dependency rules.

---

# Core Principle

Organize code around stable domain responsibilities rather than implementation technologies.

```text
Domain Capability
      |
      v
Public Contract
      |
      v
Application Service
      |
      v
Ports
      |
      +--> Local Storage Adapter
      +--> Browser Adapter
      +--> Reasoning Provider Adapter
      +--> ATS Adapter
```

High-level domain policy should not depend directly on low-level frameworks, browser selectors, file formats, or provider SDKs.

---

# Objectives

The repository structure should:

* Make domain ownership obvious.
* Keep modules independently testable.
* Prevent circular dependencies.
* Separate domain policy from infrastructure.
* Separate browser primitives from ATS knowledge.
* Separate ATS knowledge from candidate facts.
* Separate reasoning-provider prompts from business authorization.
* Keep submission logic centralized.
* Keep security policy centralized.
* Keep canonical schemas versioned.
* Allow generated frontend and backend types.
* Keep runtime data outside the source repository.
* Support one local application process without requiring microservices.
* Allow future extraction of services if needed.
* Make unsafe dependency directions difficult.
* Minimize the size of shared libraries.
* Support controlled plugin-style ATS adapters.
* Preserve clear test ownership.
* Support incremental implementation milestones.

---

# Scope

This document covers:

* Repository topology.
* Top-level directory structure.
* Backend package structure.
* Frontend structure.
* Domain-module boundaries.
* Layering.
* Public interfaces.
* Ports and adapters.
* Shared utilities.
* Schema organization.
* Prompt organization.
* ATS adapter organization.
* Browser-engine organization.
* Persistence adapters.
* Configuration.
* Migrations.
* Testing.
* Fixtures.
* Generated code.
* Scripts and developer tools.
* Naming conventions.
* Import rules.
* Dependency enforcement.
* Code ownership.
* Build outputs.
* Runtime-data separation.
* Module completion criteria.

This document does not prescribe every class, function, or source file.

It defines the structural rules that implementations should follow.

---

# Repository Strategy

The recommended initial structure is a single repository containing:

* Backend application code.
* Local frontend code.
* Canonical schemas.
* prompts.
* ATS adapters.
* tests.
* local fixture applications.
* migrations.
* operational scripts.
* documentation.

This may be described as a modular monorepo.

```text
One Repository
    |
    +-- One Backend Application
    +-- One Local Frontend
    +-- Multiple Strong Domain Modules
    +-- Shared Versioned Schemas
    +-- Adapter Plugins
    +-- Unified Test Suite
```

A modular monorepo provides:

* Simple local installation.
* Atomic changes across contracts and consumers.
* Easier schema synchronization.
* One dependency lock.
* One release version.
* Easier end-to-end testing.
* Less operational complexity than microservices.

---

# Why Not Microservices for the MVP

The MVP should not use separate network services for every capability.

Microservices would introduce:

* Additional authentication.
* service discovery.
* network failure modes.
* distributed transactions.
* deployment complexity.
* schema synchronization complexity.
* more places for candidate data to leak.
* more difficult local debugging.

Strong internal module boundaries provide most of the architectural benefits without distributed-system overhead.

---

# Top-Level Repository Structure

Recommended structure:

```text
autonomous-job-platform/
    pyproject.toml
    uv.lock
    README.md
    LICENSE
    CHANGELOG.md
    SECURITY.md
    CONTRIBUTING.md
    .gitignore
    .env.example

    src/
        job_platform/

    frontend/
        package.json
        lockfile
        src/
        tests/

    schemas/
    prompts/
    migrations/
    tests/
    fixtures/
    local_test_sites/
    scripts/
    docs/
    tools/
    generated/
```

---

# Top-Level Directory Responsibilities

## `src/`

Contains production backend source code.

It must not contain:

* Real candidate data.
* browser profiles.
* generated application packages.
* production secrets.
* runtime logs.
* test output.

---

## `frontend/`

Contains the local user interface.

It should communicate with the backend through documented local API contracts.

The frontend must not directly read Application Package files or candidate directories.

---

## `schemas/`

Contains canonical versioned schemas.

Examples:

* Candidate Profile.
* Job.
* Application Package.
* Review Report.
* Readiness Report.
* Workflow.
* Submission Result.
* History Record.
* Audit Event.

---

## `prompts/`

Contains versioned reasoning-provider prompt templates and their metadata.

Prompts should not be embedded throughout business logic.

---

## `migrations/`

Contains versioned data and configuration migrations.

---

## `tests/`

Contains backend, frontend-integration, contract, security, and end-to-end tests.

---

## `fixtures/`

Contains synthetic and sanitized test inputs.

It must not contain real candidate or employer-confidential information.

---

## `local_test_sites/`

Contains local synthetic job and ATS-like web applications used for browser tests.

---

## `scripts/`

Contains supported operational and developer scripts.

Scripts should call application services rather than duplicate domain logic.

---

## `docs/`

Contains architecture, user, operations, API, and development documentation.

---

## `tools/`

Contains repository-development tools that are not part of the runtime application.

Examples:

* Fixture sanitizers.
* schema generators.
* import-boundary checkers.
* release-manifest builders.

---

## `generated/`

Contains generated code or documentation that is safe to regenerate.

Generated files should clearly state that they should not be edited manually.

---

# Backend Package Structure

Recommended backend structure:

```text
src/job_platform/
    __init__.py
    version.py

    bootstrap/
    shared/
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
    configuration/
    operations/
    api/
```

---

# Domain-Oriented Modules

Each major directory should correspond to one stable domain capability.

A module should normally contain:

```text
module/
    domain/
    application/
    ports/
    infrastructure/
    api/
    errors.py
    models.py
```

Not every small module requires every subdirectory.

The structure should be proportional to complexity.

---

# Standard Module Layers

## Domain Layer

Contains:

* Domain entities.
* value objects.
* state-transition rules.
* domain validation.
* domain-specific errors.
* pure policies.

The domain layer should not depend on:

* Playwright.
* HTTP frameworks.
* provider SDKs.
* spreadsheet libraries.
* operating-system keychains.
* concrete file paths.
* UI code.

---

## Application Layer

Contains:

* Use cases.
* application services.
* workflow coordination inside the module.
* authorization of domain actions.
* transaction boundaries.
* port usage.
* command and query handlers.

The application layer depends on:

* Its own domain layer.
* approved public contracts from upstream modules.
* abstract ports.

---

## Ports Layer

Defines abstract interfaces required by the module.

Examples:

* Candidate repository.
* package repository.
* provider client.
* browser session.
* history writer.
* secret store.

Ports describe what the module needs, not how it is implemented.

---

## Infrastructure Layer

Contains concrete implementations of ports.

Examples:

* JSON file repository.
* Playwright browser implementation.
* Claude provider client.
* XLSX writer.
* OS credential-store adapter.

Infrastructure may depend on external libraries.

---

## API Layer

Maps local API requests and responses to application services.

The API layer should not implement domain policy.

---

# Dependency Direction

The required dependency direction is:

```text
Infrastructure
      |
      v
Application
      |
      v
Domain
```

More precisely:

```text
API --> Application --> Domain
Infrastructure --> Ports
Application --> Ports
```

The domain layer must remain independent.

---

# Dependency Rule

Source code dependencies should point inward toward stable policy.

```text
User Interface
    |
    v
Local API
    |
    v
Application Services
    |
    v
Domain Rules
```

External frameworks should remain at the edges.

---

# High-Level Module Dependency Graph

Recommended dependency direction:

```text
candidate
   |
   +-------------------+
   |                   |
   v                   v
jobs              answers
   |                   |
   v                   |
packages <-------------+
   |
   +------> documents
   +------> review
   +------> readiness
                  |
                  v
             orchestration
                  |
         +--------+--------+
         |                 |
         v                 v
      browser             ats
         |                 |
         +--------+--------+
                  |
                  v
             submission
                  |
                  v
               history
```

Cross-cutting modules:

```text
security
observability
configuration
shared
```

Cross-cutting modules should provide narrow services and should not become universal dependency containers.

---

# Public Module Interfaces

Every major module should expose a small public surface.

Implementation details should remain private.

Recommended pattern:

```text
candidate/
    __init__.py
    public.py
    domain/
    application/
    infrastructure/
```

Other modules should import from:

```text
job_platform.candidate.public
```

rather than arbitrary internal files.

---

# Internal Import Policy

Prohibited:

```python
from job_platform.candidate.infrastructure.json_repository import JsonCandidateRepository
```

from an unrelated domain module.

Preferred:

```python
from job_platform.candidate.public import CandidateProfileReader
```

The composition root may import concrete infrastructure classes.

---

# Composition Root

Concrete dependencies should be assembled in one clear composition area.

Recommended:

```text
src/job_platform/bootstrap/
    application.py
    dependencies.py
    lifecycle.py
    routes.py
```

The composition root may:

* Read validated configuration.
* instantiate repositories.
* instantiate provider clients.
* instantiate browser services.
* register ATS adapters.
* connect application services.
* create API routers.
* initialize lifecycle hooks.

Domain modules should not instantiate their own global dependencies.

---

# Dependency Injection

Dependencies should be passed explicitly.

Preferred:

```python
class PrepareApplicationService:
    def __init__(
        self,
        package_repository: PackageRepository,
        resume_service: ResumePreparationPort,
        answer_service: AnswerPreparationPort,
    ) -> None:
        ...
```

Avoid:

* Hidden global service locators.
* importing singleton repositories.
* reading global configuration inside domain entities.
* constructing provider clients inside use cases.

---

# Shared Module Policy

Recommended shared structure:

```text
shared/
    ids/
    time/
    result/
    errors/
    hashing/
    serialization/
    paths/
    pagination/
    money/
    country_codes/
```

The shared module should contain only stable, domain-neutral primitives.

---

# What Belongs in `shared`

Examples:

* Entity ID types.
* Clock interface.
* ISO timestamp utilities.
* generic result envelopes.
* content hashes.
* safe path primitives.
* pagination models.
* money value object.
* country-code validation.

---

# What Does Not Belong in `shared`

Do not place the following in shared:

* Resume selection.
* sponsorship logic.
* job ranking.
* submission states.
* ATS page classification.
* browser selectors.
* candidate profile repositories.
* review severity rules.

If code is meaningful only in one domain, it belongs in that domain.

---

# Shared-Kernel Size Rule

The shared kernel should remain intentionally small.

A new shared abstraction should be added only when:

* At least two modules use it.
* Its semantics are identical across those modules.
* It is stable.
* It does not create hidden domain coupling.

---

# Candidate Module

Recommended structure:

```text
candidate/
    public.py
    domain/
        profile.py
        employment.py
        education.py
        work_authorization.py
        preferences.py
        source_reference.py
        validation.py
    application/
        import_candidate.py
        update_profile.py
        validate_profile.py
        resolve_conflict.py
        create_snapshot.py
        queries.py
    ports/
        candidate_repository.py
        source_parser.py
        secure_value_store.py
    infrastructure/
        file_repository.py
        json_parser.py
        markdown_parser.py
        pdf_resume_parser.py
        docx_resume_parser.py
    api/
        routes.py
        schemas.py
    errors.py
```

---

# Candidate Module Responsibilities

Owns:

* Candidate Profile.
* employment records.
* education records.
* skills.
* work authorization.
* preferences.
* standard answers.
* candidate source provenance.
* candidate-source conflicts.
* candidate snapshots.

---

# Candidate Module Must Not Own

* Job ranking.
* resume tailoring.
* browser form filling.
* ATS question mapping.
* submission.
* application history.

---

# Candidate Module Public Operations

Examples:

* Read current candidate profile.
* import candidate source.
* validate candidate profile.
* update candidate fact.
* resolve source conflict.
* create immutable candidate snapshot.
* retrieve permitted candidate context.

---

# Candidate Access Policy

Other modules should not receive unrestricted Candidate Profile objects by default.

They should request purpose-specific views.

Examples:

```text
Resume Context
Cover Letter Context
Application Answer Context
Browser Field Context
Review Context
```

---

# Jobs Module

Recommended structure:

```text
jobs/
    public.py
    domain/
        job.py
        job_source.py
        job_analysis.py
        job_match.py
        normalization.py
        ranking_policy.py
        duplicate_policy.py
    application/
        discover_jobs.py
        import_job.py
        refresh_job.py
        analyze_job.py
        rank_job.py
        select_job.py
    ports/
        job_repository.py
        job_source_reader.py
        job_analyzer.py
    infrastructure/
        direct_url_reader.py
        career_page_reader.py
        provider_job_analyzer.py
        file_repository.py
    api/
        routes.py
        schemas.py
```

---

# Jobs Module Responsibilities

Owns:

* Job records.
* Job Sources.
* job identity.
* normalized job metadata.
* job analysis.
* match scoring.
* job selection and skipping.
* duplicate job detection before package creation.

---

# Jobs Module Must Not Own

* Candidate profile mutation.
* resume generation.
* browser form execution.
* final duplicate-application decisions.
* application submission.

---

# Job Ranking Boundary

The ranking service may consume a candidate ranking view.

It should not modify candidate records.

It should return:

* Score.
* recommendation.
* matched requirements.
* gaps.
* hard-rule decisions.

---

# Packages Module

Recommended structure:

```text
packages/
    public.py
    domain/
        application_package.py
        manifest.py
        artifact_reference.py
        package_status.py
        fingerprint.py
        staleness.py
    application/
        create_package.py
        update_package.py
        refresh_package.py
        archive_package.py
        validate_package.py
        queries.py
    ports/
        package_repository.py
        artifact_store.py
        package_lock.py
    infrastructure/
        file_package_repository.py
        filesystem_artifact_store.py
        file_lock.py
    api/
        routes.py
        schemas.py
```

---

# Packages Module Responsibilities

Owns:

* Application Package identity.
* package manifest.
* job snapshot.
* candidate snapshot reference.
* active artifact references.
* artifact versions.
* package status.
* package fingerprints.
* staleness.
* package locks.
* package archive state.

---

# Packages Module Must Not Own

* Resume-writing logic.
* answer-generation logic.
* browser automation.
* submission verification.
* history spreadsheet formatting.

---

# Package as Integration Boundary

The Application Package is the central integration boundary.

Other modules should exchange package-linked references rather than directly manipulating each other's files.

Examples:

* Documents module creates an Artifact result.
* Packages module registers the artifact.
* Review module reads the package through a package read model.
* Browser module receives an approved Application Plan.
* Submission module records result references back into the package.

---

# Documents Module

Recommended structure:

```text
documents/
    public.py
    domain/
        artifact.py
        resume.py
        cover_letter.py
        validation_report.py
        document_policy.py
    application/
        select_base_resume.py
        tailor_resume.py
        generate_cover_letter.py
        validate_document.py
        render_document.py
        compare_versions.py
    ports/
        reasoning_writer.py
        document_renderer.py
        document_parser.py
        artifact_writer.py
    infrastructure/
        claude_writer.py
        docx_renderer.py
        pdf_renderer.py
        text_extractor.py
    api/
        routes.py
        schemas.py
```

---

# Documents Module Responsibilities

Owns:

* Resume preparation.
* Cover-letter preparation.
* document rendering.
* document validation.
* document-version comparison.
* document-specific factual checks.
* document artifact metadata.

---

# Documents Module Must Not Own

* Candidate master facts.
* package status transitions.
* application form questions.
* final browser uploads.
* submission decisions.

---

# Document Generation Rule

The Documents module receives immutable candidate and job contexts.

It returns proposed artifacts and validation results.

The Packages module determines whether an artifact becomes active.

---

# Answers Module

Recommended structure:

```text
answers/
    public.py
    domain/
        question.py
        canonical_family.py
        application_answer.py
        answer_policy.py
        reuse_policy.py
    application/
        classify_question.py
        resolve_answer.py
        generate_narrative.py
        validate_answer.py
        save_reusable_answer.py
        build_answer_set.py
    ports/
        answer_repository.py
        narrative_generator.py
        candidate_answer_reader.py
    infrastructure/
        file_answer_repository.py
        claude_narrative_generator.py
        canonical_mapping_registry.py
    api/
        routes.py
        schemas.py
```

---

# Answers Module Responsibilities

Owns:

* Canonical application-question families.
* question classification.
* answer resolution.
* answer provenance.
* narrative-answer generation.
* answer validation.
* answer reuse policy.
* prepared answer sets.

---

# Answers Module Must Not Own

* Browser field selectors.
* ATS option selection mechanics.
* candidate source-file mutation without Candidate module approval.
* legal truth determination through reasoning.
* final submission.

---

# Review Module

Recommended structure:

```text
review/
    public.py
    domain/
        review.py
        finding.py
        severity.py
        approval.py
        correction.py
    application/
        review_preparation.py
        review_browser_form.py
        apply_safe_corrections.py
        approve_review.py
        invalidate_approval.py
        explain_finding.py
    ports/
        semantic_reviewer.py
        package_review_reader.py
        correction_executor.py
    infrastructure/
        deterministic_checks.py
        provider_semantic_reviewer.py
    api/
        routes.py
        schemas.py
```

---

# Review Module Responsibilities

Owns:

* Review lifecycle.
* findings.
* severity.
* cross-artifact consistency.
* approval.
* approval invalidation.
* safe-correction classification.
* review explanations.

---

# Review Module Must Not Own

* Package file storage.
* browser action execution.
* readiness admission.
* submission.
* history status.

---

# Readiness Module

Recommended structure:

```text
readiness/
    public.py
    domain/
        readiness.py
        readiness_stage.py
        readiness_check.py
        requirement.py
        remediation.py
    application/
        evaluate_preparation.py
        evaluate_execution.py
        evaluate_review.py
        evaluate_submission.py
        evaluate_history_sync.py
        remediate.py
    ports/
        package_readiness_reader.py
        browser_health_reader.py
        adapter_capability_reader.py
        duplicate_check_reader.py
    infrastructure/
        policy_registry.py
    api/
        routes.py
        schemas.py
```

---

# Readiness Module Responsibilities

Owns:

* Stage-specific readiness.
* readiness checks.
* blocking requirements.
* warnings.
* next allowed actions.
* refresh requirements.
* bounded remediation plans.

---

# Readiness Module Must Not Own

* Actual browser actions.
* package mutation beyond approved readiness metadata.
* review approval.
* duplicate history storage.
* final submission.

---

# Browser Module

Recommended structure:

```text
browser/
    public.py
    domain/
        browser_session.py
        page_snapshot.py
        form_model.py
        field_model.py
        action_model.py
        interaction_plan.py
        action_result.py
    application/
        start_session.py
        open_page.py
        inspect_page.py
        execute_interaction.py
        verify_action.py
        capture_snapshot.py
        recover_session.py
    ports/
        browser_driver.py
        navigation_policy.py
        upload_policy.py
        screenshot_store.py
    infrastructure/
        playwright_driver.py
        playwright_profile_manager.py
        accessibility_snapshot.py
        screenshot_store.py
    widgets/
        text.py
        select.py
        combobox.py
        radio.py
        checkbox.py
        date.py
        upload.py
        repeated_section.py
    api/
        internal.py
```

---

# Browser Module Responsibilities

Owns:

* Browser sessions.
* browser profiles during execution.
* page navigation.
* page inspection.
* canonical Form Model extraction primitives.
* low-level field interaction.
* action verification.
* screenshots.
* browser recovery.

---

# Browser Module Must Not Own

* Candidate answer resolution.
* ATS-specific workflow semantics.
* application queue ordering.
* final submission authorization.
* duplicate detection.
* application-history updates.

---

# Browser Primitive Rule

The Browser module should know:

```text
Select option “Yes” in field X.
```

It should not decide:

```text
The candidate's future sponsorship answer should be Yes.
```

---

# ATS Module

Recommended structure:

```text
ats/
    public.py
    registry/
        adapter_registry.py
        metadata.py
        health.py
    base/
        adapter.py
        capabilities.py
        detection.py
        page_classifier.py
    generic/
        form_engine.py
        form_boundary.py
        semantic_classifier.py
        action_classifier.py
    adapters/
        greenhouse/
            adapter.py
            metadata.py
            detection.py
            pages.py
            widgets.py
            navigation.py
            submission.py
            fixtures/
        lever/
        workday/
    application/
        detect_ats.py
        select_adapter.py
        inspect_application.py
        build_page_plan.py
        verify_submission_signal.py
    api/
        routes.py
        schemas.py
```

---

# ATS Module Responsibilities

Owns:

* ATS detection.
* adapter registry.
* adapter capabilities.
* ATS page classification.
* ATS-specific form normalization.
* ATS-specific widget behavior.
* ATS navigation semantics.
* ATS submission-signal interpretation.
* Generic Form Engine.

---

# ATS Module Must Not Own

* Candidate facts.
* answer truth.
* package approval.
* queue scheduling.
* final submission authorization.
* application-history storage.

---

# Adapter Contract Boundary

ATS adapters should consume:

* Browser Page Snapshot.
* Form Model.
* Application Plan.
* resolved Answer Set.
* approved artifact references.

They should return:

* normalized form.
* interaction plan.
* navigation decision.
* review snapshot.
* submission-control metadata.
* confirmation evidence.

---

# ATS Adapter Isolation

One adapter should not import another adapter's internal implementation.

Shared ATS logic belongs in:

```text
ats/base/
```

or:

```text
ats/generic/
```

Employer-specific overrides should remain inside the owning adapter package.

---

# Generic Form Engine Boundary

The Generic Form Engine belongs under the ATS integration layer because it provides application-form interpretation.

It should use Browser module primitives but should not become part of the Browser driver.

---

# Orchestration Module

Recommended structure:

```text
orchestration/
    public.py
    domain/
        queue.py
        queue_item.py
        workflow.py
        stage.py
        checkpoint.py
        retry_policy.py
        cancellation.py
    application/
        create_queue.py
        admit_package.py
        start_queue.py
        execute_workflow.py
        pause_workflow.py
        resume_workflow.py
        cancel_workflow.py
        recover_workflow.py
        advance_stage.py
    ports/
        workflow_repository.py
        checkpoint_store.py
        package_lock_service.py
        browser_execution_port.py
        readiness_port.py
        review_port.py
        submission_port.py
    infrastructure/
        file_workflow_repository.py
        file_checkpoint_store.py
        scheduler.py
    api/
        routes.py
        schemas.py
```

---

# Orchestration Module Responsibilities

Owns:

* Queue state.
* queue ordering.
* queue-item state.
* workflow state.
* stage transitions.
* checkpoints.
* retries.
* pause and resume.
* cancellation.
* recovery.
* coordination of module calls.

---

# Orchestration Module Must Not Own

* Candidate facts.
* resume generation.
* question resolution.
* browser selector logic.
* ATS parsing.
* submission evidence classification.
* CSV/XLSX formatting.

---

# Orchestrator Rule

The orchestrator decides:

```text
Which stage runs next.
```

It should not implement:

```text
How a searchable ATS dropdown works.
```

---

# Submission Module

Recommended structure:

```text
submission/
    public.py
    domain/
        attempt.py
        submission_state.py
        evidence.py
        verification_result.py
        submission_lock.py
        unknown_resolution.py
    application/
        prepare_submission.py
        create_attempt.py
        initiate_click.py
        verify_submission.py
        reconcile_dashboard.py
        resolve_unknown.py
    ports/
        submission_attempt_repository.py
        evidence_store.py
        submission_browser_port.py
        dashboard_verifier.py
        duplicate_checker.py
        history_sync_port.py
    infrastructure/
        file_attempt_repository.py
        file_evidence_store.py
        file_submission_lock.py
    api/
        routes.py
        schemas.py
```

---

# Submission Module Responsibilities

Owns:

* Submission attempt.
* irreversible-action boundary.
* submission lock.
* click initiation state.
* submission evidence.
* evidence strength.
* verification outcome.
* Submission Unknown.
* unknown-outcome resolution.

---

# Submission Module Must Not Own

* Browser field completion.
* ATS form extraction.
* queue ordering.
* candidate answers.
* CSV and XLSX implementation.
* user-interface presentation.

---

# Final Submission Centralization

Only the Submission module should authorize and record a final submission attempt.

ATS adapters may identify the control.

Browser services may execute the click.

The Orchestrator may call the Submission service.

No other module may directly perform a final submission action.

---

# History Module

Recommended structure:

```text
history/
    public.py
    domain/
        history_record.py
        history_event.py
        recruitment_status.py
        follow_up.py
        duplicate_match.py
    application/
        create_record.py
        sync_submission.py
        update_status.py
        add_manual_record.py
        reconcile_history.py
        export_history.py
    ports/
        history_repository.py
        csv_writer.py
        xlsx_writer.py
        package_history_reader.py
    infrastructure/
        jsonl_event_repository.py
        csv_history_writer.py
        xlsx_history_writer.py
        file_history_repository.py
    api/
        routes.py
        schemas.py
```

---

# History Module Responsibilities

Owns:

* Current application-history records.
* Append-only history events.
* submission-status history.
* recruitment-status history.
* manual applications.
* follow-up information.
* duplicate-application history queries.
* CSV synchronization.
* XLSX synchronization.
* reconciliation and export.

---

# History Module Must Not Own

* Submission truth.
* package artifacts.
* browser automation.
* candidate profile.
* job discovery.

The Submission Package remains the detailed source of submission truth.

---

# Security Module

Recommended structure:

```text
security/
    public.py
    domain/
        data_classification.py
        access_policy.py
        sensitive_field_policy.py
        domain_trust.py
        upload_policy.py
        security_event.py
    application/
        authorize_data_access.py
        validate_domain.py
        validate_upload.py
        evaluate_sensitive_field.py
        scan_secret.py
        run_privacy_review.py
    ports/
        secret_store.py
        encryption_service.py
        security_event_writer.py
    infrastructure/
        os_secret_store.py
        encrypted_file_store.py
        secret_scanner.py
        path_policy.py
    api/
        routes.py
        schemas.py
```

---

# Security Module Responsibilities

Owns:

* Data classification.
* component-access policy.
* sensitive-field policy.
* secret-store abstraction.
* domain trust.
* path safety.
* upload authorization.
* secret scanning.
* security events.
* privacy-review policy.

---

# Security Module Must Not Own

* Candidate business facts.
* application ranking.
* browser navigation implementation.
* submission evidence.
* user-interface state.

---

# Security Dependency Rule

Security policy may be consulted by every module.

However, domain modules should depend on narrow security interfaces rather than the entire Security module.

Example:

```text
Provider Context Authorization Port
Upload Authorization Port
Sensitive Field Policy Port
```

---

# Observability Module

Recommended structure:

```text
observability/
    public.py
    domain/
        log_event.py
        audit_event.py
        metric.py
        health_result.py
        alert.py
        trace.py
    application/
        log_event.py
        append_audit.py
        record_metric.py
        run_health_check.py
        generate_diagnostics.py
        validate_audit_chain.py
    ports/
        event_writer.py
        metric_store.py
        health_probe.py
        diagnostic_store.py
    infrastructure/
        jsonl_logger.py
        audit_chain_writer.py
        local_metric_store.py
        diagnostic_bundle_writer.py
    api/
        routes.py
        schemas.py
```

---

# Observability Module Responsibilities

Owns:

* Structured events.
* audit events.
* trace spans.
* metrics.
* component health aggregation.
* alerts.
* diagnostic bundles.
* audit integrity.

---

# Observability Module Must Not Own

* Domain state transitions.
* package business status.
* submission truth.
* security authorization.

It records facts produced by other modules.

---

# Configuration Module

Recommended structure:

```text
configuration/
    public.py
    domain/
        settings.py
        feature_flags.py
        policy_references.py
    application/
        load_configuration.py
        validate_configuration.py
        update_configuration.py
        migrate_configuration.py
    ports/
        configuration_repository.py
    infrastructure/
        json_configuration_repository.py
        environment_reader.py
    api/
        routes.py
        schemas.py
```

---

# Configuration Module Responsibilities

Owns:

* Non-secret settings.
* schema validation.
* feature flags.
* policy references.
* environment-profile selection.
* configuration migration.

Secrets remain in the Security module's Secret Store.

---

# Operations Module

Recommended structure:

```text
operations/
    public.py
    domain/
        backup.py
        migration.py
        maintenance_mode.py
        operation_result.py
    application/
        initialize_data_root.py
        create_backup.py
        restore_backup.py
        run_migrations.py
        rebuild_history.py
        validate_packages.py
        repair_locks.py
        shutdown.py
    ports/
        backup_store.py
        migration_registry.py
        system_probe.py
    infrastructure/
        local_backup_store.py
        archive_service.py
        migration_runner.py
    api/
        routes.py
        schemas.py
```

---

# API Module

Recommended structure:

```text
api/
    app.py
    dependencies.py
    middleware/
        request_id.py
        errors.py
        csrf.py
        origin_validation.py
        logging.py
    routers/
        candidate.py
        jobs.py
        packages.py
        queue.py
        review.py
        readiness.py
        submission.py
        history.py
        settings.py
        health.py
        maintenance.py
    contracts/
        requests.py
        responses.py
        errors.py
```

---

# API Module Responsibilities

Owns:

* Local HTTP or IPC transport.
* request parsing.
* response serialization.
* middleware.
* authentication/session handling.
* CSRF validation.
* mapping API contracts to application commands and queries.

---

# API Module Must Not Own

* Domain policy.
* state-transition rules.
* file-path resolution beyond transport validation.
* browser execution.
* provider prompts.

---

# Frontend Repository Structure

Recommended:

```text
frontend/src/
    app/
        router/
        providers/
        layout/
        state/

    features/
        onboarding/
        dashboard/
        jobs/
        applications/
        queue/
        review/
        submission/
        history/
        candidate/
        settings/
        health/
        maintenance/

    components/
        status/
        forms/
        tables/
        dialogs/
        documents/
        timeline/
        notifications/

    api/
        client/
        generated/
        events/

    security/
        sanitization/
        sensitive_display/

    accessibility/
    utilities/
    styles/
```

---

# Frontend Feature Boundaries

Frontend features should align with backend domain capabilities.

A feature may include:

* Page components.
* feature-specific state.
* API queries.
* actions.
* accessibility behavior.
* tests.

Shared visual components belong in `components/`.

Domain logic should remain on the backend.

---

# Frontend State Rule

The frontend should store:

* UI filters.
* local form drafts.
* navigation state.
* selected table rows.
* temporary display state.

The frontend should not become the source of truth for:

* Package status.
* queue status.
* submission status.
* review approval.
* allowed actions.
* artifact versions.

---

# Frontend Generated Types

Generated API types should reside in:

```text
frontend/src/api/generated/
```

They should be generated from canonical API or schema definitions.

Manual domain-type duplication should be avoided.

---

# Frontend Security Boundary

The frontend must not:

* Read arbitrary local files.
* resolve backend file paths.
* access the Secret Store directly.
* authorize final submission.
* infer permitted state transitions.
* render unsanitized external HTML.

---

# Schemas Directory

Recommended:

```text
schemas/
    registry.json

    common/
        actor/
        source_reference/
        file_reference/
        error/

    candidate/
        candidate_profile/
            1.0.json
        employment_record/
            1.0.json

    jobs/
        job/
            1.0.json
        job_analysis/
            1.0.json

    packages/
        application_package/
            1.0.json

    review/
    readiness/
    orchestration/
    browser/
    ats/
    submission/
    history/
    observability/
    configuration/
    operations/
```

---

# Schema Source of Truth

Canonical schema definitions should have one source of truth.

Generated representations may include:

* Python models.
* TypeScript types.
* API documentation.
* test validators.

Generated representations should not diverge from registry definitions.

---

# Schema Ownership

Each schema should be owned by its domain module.

Examples:

```text
CandidateProfile -> candidate
ApplicationPackage -> packages
FormModel -> browser
SubmissionResult -> submission
HistoryRecord -> history
```

---

# Schema Import Rules

A domain module may reference schemas from upstream dependencies.

It should not copy those schemas into its own directory.

---

# Prompts Directory

Recommended:

```text
prompts/
    registry.json

    job_analysis/
        1.0/
            system.md
            user_template.md
            output_schema.json
            metadata.json
            evaluation_cases.json

    resume_tailoring/
    cover_letter/
    narrative_answer/
    semantic_review/
    question_classification/
```

---

# Prompt Ownership

Prompts should be owned by the domain module that consumes their outputs.

Examples:

* Job-analysis prompts owned by Jobs.
* Resume prompts owned by Documents.
* Narrative-answer prompts owned by Answers.
* Semantic-review prompts owned by Review.

---

# Prompt Execution Boundary

Prompt templates should not call provider SDKs directly.

Domain application services should call a provider port with:

* Prompt ID.
* prompt version.
* structured context.
* expected output schema.
* privacy manifest.

---

# Prompt Metadata

Prompt metadata should include:

* Prompt ID.
* version.
* owner.
* purpose.
* input schema.
* output schema.
* sensitive-data policy.
* evaluation suite.
* status.

---

# Migrations Directory

Recommended:

```text
migrations/
    registry.json

    configuration/
        001_config_1_0_to_1_1.py

    candidate/
        001_candidate_1_0_to_1_1.py

    packages/
        001_package_1_0_to_1_1.py

    history/
    audit/
```

---

# Migration Ownership

The module that owns the schema owns its migrations.

Cross-module migrations should be coordinated through Operations.

---

# Migration Rules

A migration should:

* Import domain migration interfaces.
* avoid calling UI code.
* avoid provider calls.
* avoid browser calls.
* use staging.
* preserve submitted evidence.
* produce validation results.
* support rollback when feasible.

---

# Runtime Data Separation

Runtime user data must remain outside the source repository.

Prohibited repository locations:

```text
candidate_data/
application_packages/
browser_profiles/
application_history/
logs/
screenshots/
secrets/
```

unless those directories contain only synthetic test fixtures under `fixtures/`.

---

# Runtime Data Root

Backend code should access runtime data through configured storage abstractions.

It should not assume:

```text
./user_data
```

relative to the repository.

---

# File Path Rule

Domain models should use:

* Entity IDs.
* File Reference IDs.
* logical paths.

Concrete absolute paths should remain inside infrastructure adapters.

---

# Forbidden Absolute Path Flow

Prohibited:

```text
UI -> API -> Domain -> Browser
with an arbitrary absolute local path
```

Required:

```text
UI selects Artifact ID
        |
        v
Backend resolves approved File Reference
        |
        v
Security validates path
        |
        v
Browser receives approved resolved file
```

---

# Persistence Adapter Layout

File-based repositories should remain in owning modules' infrastructure directories.

Examples:

```text
candidate/infrastructure/file_repository.py
packages/infrastructure/file_package_repository.py
history/infrastructure/file_history_repository.py
```

Avoid one universal filesystem repository containing all domain logic.

---

# Repository Contracts

Each repository port should define:

* Read methods.
* write methods.
* entity-version handling.
* atomicity requirements.
* missing-entity behavior.
* conflict behavior.
* audit behavior.

---

# Transaction Boundaries

The MVP may not use a relational transaction manager.

Operations involving multiple files should use:

* Staging.
* atomic replacement.
* durable operation records.
* idempotency keys.
* reconciliation.

The application service should define the logical transaction boundary.

---

# Cross-Module Coordination

A module should not directly edit another module's persistence files.

Example:

The Submission module must not edit `applications.csv` directly.

It should call the History module's public interface.

---

# Event-Based Coordination

Domain events may be used for secondary effects.

Example:

```text
submission.verified
    |
    +--> Package status update
    +--> History synchronization
    +--> Audit event
    +--> User notification
```

Critical actions should still use explicit application coordination rather than relying only on best-effort events.

---

# Domain Event Location

Domain event definitions should live with the domain that owns the fact.

Example:

```text
submission/domain/events.py
```

Transport-level event envelopes may live in Observability or API contracts.

---

# Synchronous vs Asynchronous Boundaries

The MVP may process events synchronously within the local process.

The event model should still be durable where required.

Critical submission events must be persisted before dependent actions proceed.

---

# Error Organization

Each module should define domain-specific errors in:

```text
module/errors.py
```

or:

```text
module/domain/errors.py
```

---

# Error Naming

Examples:

```text
CandidateProfileConflictError
JobIdentityMismatchError
PackageVersionConflictError
ReviewApprovalInvalidError
ReadinessFailedError
BrowserActionVerificationError
ATSAdapterUnsupportedError
SubmissionOutcomeUnknownError
HistorySyncError
```

---

# Error Translation

Errors should be translated at boundaries:

```text
Infrastructure Exception
        |
        v
Module Error
        |
        v
API Error Contract
        |
        v
User-Friendly Message
```

Raw third-party exceptions should not cross domain or API boundaries.

---

# Logging Organization

Modules should emit structured events through the Observability public interface.

They should not configure their own logger destinations.

---

# Module Log Context

Every module should include available correlation identifiers:

* Package ID.
* Workflow ID.
* Queue ID.
* Submission Attempt ID.
* Request ID.
* Candidate Profile ID.

---

# Audit Event Ownership

The module performing a business-significant action should request the corresponding audit event.

Examples:

* Candidate module audits candidate-fact changes.
* Review module audits approval.
* Submission module audits final attempt.
* History module audits correction.

---

# Security Policy Integration

Modules should use narrow policy interfaces.

Examples:

```text
CandidateContextAuthorization
ProviderContextAuthorization
FileReadAuthorization
UploadAuthorization
DomainNavigationAuthorization
SensitiveFieldDecision
```

Avoid one generic method such as:

```python
security.check_everything(...)
```

that hides policy semantics.

---

# Plugin Architecture

ATS adapters may use a controlled plugin registry.

Recommended adapter registration:

```python
adapter_registry.register(
    adapter_id="greenhouse",
    factory=create_greenhouse_adapter,
    metadata=greenhouse_metadata,
)
```

---

# Plugin Restrictions

Plugins should:

* Be shipped with trusted application releases in the MVP.
* conform to the adapter contract.
* declare capabilities.
* declare version.
* declare supported browser version.
* pass regression tests.
* use approved browser ports.
* not access candidate storage directly.
* not access secrets directly.
* not perform final submission outside the Submission module.

---

# Dynamic Plugin Loading

Arbitrary third-party dynamic plugin loading should be deferred.

If added later, it would require:

* Signing.
* trust policy.
* sandboxing.
* permission manifests.
* compatibility checks.
* user approval.

---

# Adapter Fixture Location

Adapter-specific fixtures may be stored under:

```text
fixtures/ats/greenhouse/
```

or inside:

```text
src/job_platform/ats/adapters/greenhouse/fixtures/
```

Preferred shared test-fixture location:

```text
fixtures/ats/greenhouse/
```

to keep production packages free of large fixture files.

---

# Local Test Sites Structure

Recommended:

```text
local_test_sites/
    standard_form/
    multi_page_form/
    greenhouse_like/
    workday_like/
    malicious_form/
    confirmation_variants/
    external_assessment/
```

Each site should include:

* Scenario metadata.
* expected form model.
* expected actions.
* expected outcome.
* test-only submission endpoint.

---

# Tests Directory Structure

Recommended:

```text
tests/
    unit/
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

    contract/
    component/
    integration/
    browser/
    end_to_end/
    security/
    privacy/
    recovery/
    performance/
    migrations/
    installation/
```

---

# Test Mirroring Rule

Unit-test directories should mirror production-module structure where practical.

Example:

```text
src/job_platform/submission/domain/attempt.py
tests/unit/submission/domain/test_attempt.py
```

---

# Contract Test Ownership

The consumer and producer should share responsibility for contract tests.

Example:

```text
ATS Adapter -> Browser Form Model
```

Tests should confirm:

* Adapter produces valid Form Model.
* Browser consumer handles supported versions.

---

# Synthetic Fixture Policy

All repository fixtures must be:

* Synthetic.
* sanitized.
* clearly labeled.
* free of valid credentials.
* free of real candidate data.
* safe for source control.

---

# Golden Test Data

Golden datasets should reside under:

```text
fixtures/golden/
```

with ownership metadata.

Example:

```text
fixtures/golden/answers/future_sponsorship_001.json
```

---

# Snapshot Test Policy

Snapshot tests are appropriate for:

* Stable schemas.
* generated API documentation.
* normalized form models.
* user-interface component rendering.
* sanitized audit event structure.

They should not replace semantic assertions.

---

# Integration Test Composition

Integration tests should instantiate real application services with test infrastructure adapters.

Example:

```text
Real Package Service
Real Review Service
Temporary File Repositories
Mock Reasoning Provider
Local Test Browser
```

---

# End-to-End Test Boundary

End-to-end tests should enter through the same API or application entry point used by the frontend.

They should not bypass orchestration by directly invoking internal domain functions.

---

# Generated Code

Generated code may include:

* Python schema models.
* TypeScript API types.
* OpenAPI specification.
* frontend API client.
* schema documentation.
* enum mappings.

---

# Generated Code Location

Recommended:

```text
generated/python/
generated/typescript/
generated/openapi/
generated/docs/
```

Production imports may point to a packaged generated module when necessary.

---

# Generated File Header

Every generated file should include:

```text
This file is generated. Do not edit manually.
Source: schemas/...
Generator version: ...
```

---

# Generation Reproducibility

Code generation should be deterministic.

CI should verify that:

* Generated outputs match source schemas.
* No uncommitted generation drift exists.
* Generator version is recorded.

---

# Manual Code Around Generated Types

Generated DTOs should remain separate from domain entities.

Example:

```text
Generated API Model
        |
        v
Mapper
        |
        v
Domain Entity
```

Do not make domain behavior depend on code-generation framework details.

---

# Mapping Layer

Each API-owning module should define mapping functions between:

* API DTOs.
* domain models.
* persistence records.
* schema-registry payloads.

Mapping should be explicit for security-critical entities.

---

# Scripts Directory

Recommended scripts:

```text
scripts/
    dev_start.py
    run_health_check.py
    initialize_data_root.py
    generate_types.py
    validate_schemas.py
    run_migrations.py
    create_backup.py
    rebuild_history.py
    sanitize_fixture.py
    release_check.py
```

---

# Script Rule

Scripts should call public application services.

They should not directly manipulate package manifests, history CSV files, or browser-profile locks unless the script is the owned infrastructure tool for that operation.

---

# Developer Tooling

Recommended tools:

* Formatter.
* linter.
* type checker.
* unit test runner.
* import-boundary checker.
* dependency-cycle detector.
* secret scanner.
* vulnerability scanner.
* schema validator.
* OpenAPI validator.
* frontend accessibility checker.

---

# Import Boundary Enforcement

The project should use automated checks to prevent forbidden imports.

Examples of rules:

```text
candidate.domain must not import jobs
browser must not import candidate
ats.adapters must not import history
frontend must not import backend filesystem code
domain modules must not import infrastructure
```

---

# Dependency Rule File

A machine-readable dependency policy may be stored in:

```text
tools/dependency_rules.toml
```

Conceptual example:

```toml
[modules.browser]
allowed = ["shared", "security.public", "observability.public"]

[modules.ats]
allowed = ["shared", "browser.public", "security.public"]

[modules.submission]
allowed = [
  "shared",
  "packages.public",
  "review.public",
  "readiness.public",
  "browser.public",
  "ats.public",
  "history.public",
  "security.public",
  "observability.public"
]
```

---

# Circular Dependency Policy

Circular imports between domain modules are prohibited.

When two modules need each other:

1. Identify which module owns the concept.
2. introduce a narrow port.
3. move common primitives to the owning module or shared kernel.
4. use an application coordinator.
5. avoid mutual direct imports.

---

# Example Circular Dependency Resolution

Problem:

```text
Packages imports Review
Review imports Packages
```

Resolution:

* Packages owns package state.
* Review consumes a `PackageReviewView` contract.
* Review returns `ReviewResult`.
* An application coordinator registers the result with Packages.

---

# Naming Conventions

## Python Modules

Use:

```text
snake_case.py
```

## Classes

Use:

```text
PascalCase
```

## Functions and Variables

Use:

```text
snake_case
```

## Constants

Use:

```text
UPPER_SNAKE_CASE
```

## IDs

Use explicit names:

```text
package_id
workflow_id
submission_attempt_id
```

Avoid generic:

```text
id
```

when multiple entities are present.

---

# Service Naming

Application services should use action-oriented names.

Examples:

```text
CreateApplicationPackage
EvaluateSubmissionReadiness
VerifySubmission
ReconcileApplicationHistory
```

Avoid vague names such as:

```text
PackageManager
UtilityService
CommonHandler
```

unless the responsibility is precise.

---

# Port Naming

Ports should describe the capability.

Examples:

```text
PackageRepository
ReasoningProviderClient
BrowserExecutionPort
SubmissionEvidenceStore
HistoryWriter
```

---

# Infrastructure Naming

Concrete adapters should identify technology or format.

Examples:

```text
FilePackageRepository
PlaywrightBrowserDriver
ClaudeReasoningProvider
XlsxHistoryWriter
MacOSKeychainSecretStore
```

---

# DTO Naming

API data-transfer objects may use suffixes such as:

```text
CreatePackageRequest
PackageResponse
ReviewApprovalRequest
ErrorResponse
```

Domain entities should not use transport-oriented suffixes.

---

# File Size and Complexity

Large files should be split by responsibility.

Signals that a file should be split:

* Multiple unrelated classes.
* domain and infrastructure code mixed.
* more than one public service.
* ATS variants mixed together.
* business rules embedded in route handlers.
* excessive conditional branching by provider or ATS.

---

# Avoid Generic Utility Modules

Avoid files named:

```text
utils.py
helpers.py
common.py
misc.py
```

unless their content is genuinely narrow and stable.

Prefer:

```text
hashing.py
date_parsing.py
path_validation.py
```

---

# Configuration Access Rule

Only bootstrap and Configuration application services should read raw configuration files.

Other modules should receive typed settings objects.

---

# Secret Access Rule

Only approved infrastructure adapters should resolve secret references.

Domain and application code should use a provider client already configured with secret access.

---

# Environment Variable Rule

Raw environment-variable access should remain inside:

```text
configuration/infrastructure/environment_reader.py
```

or Secret Store adapters.

---

# Provider SDK Boundary

Provider SDK imports should remain inside provider infrastructure adapters.

Prohibited in domain code:

```python
from anthropic import Anthropic
```

Preferred boundary:

```text
documents/application
    |
    v
DocumentWritingPort
    |
    v
documents/infrastructure/claude_writer
```

---

# Playwright Boundary

Playwright imports should remain inside Browser infrastructure.

ATS adapters should use browser abstractions and adapter context.

An ATS adapter may define selector hints but should not control the raw browser process outside the approved adapter interface.

---

# Spreadsheet Library Boundary

Spreadsheet libraries should remain inside History infrastructure.

Application code should work with canonical History Records rather than workbook cells.

---

# PDF and DOCX Library Boundary

Document-format libraries should remain inside Documents infrastructure or approved candidate parsers.

Domain code should not manipulate low-level PDF objects.

---

# Persistence Model Separation

Persistence records may differ from domain models.

Use explicit mappers when necessary.

Example:

```text
Domain ApplicationPackage
        |
        v
PackagePersistenceRecord
        |
        v
manifest.json
```

---

# Serialization Boundary

Domain entities should not be responsible for writing themselves to disk.

Persistence adapters should serialize and deserialize them.

---

# Immutable Domain Objects

Important historical objects should be immutable after creation.

Examples:

* Candidate snapshot.
* Job snapshot.
* submitted artifact fingerprint.
* submission attempt.
* submission evidence.
* audit event.

Mutations should create new versions or events.

---

# Mutable Aggregate Roots

Examples:

* Candidate Profile.
* Job.
* Application Package.
* Queue.
* Workflow.
* History Record.

Mutations should occur through application services with version checks.

---

# Aggregate Ownership

Each aggregate root should have one owning module.

Other modules should not mutate nested state directly.

---

# Application Package Mutation

Only the Packages module should persist package-state changes.

Other modules return results that the Package service registers.

---

# Queue Mutation

Only the Orchestration module should mutate Queue and Workflow state.

---

# Submission Attempt Mutation

Only the Submission module should mutate Submission Attempt state.

---

# History Mutation

Only the History module should mutate current history records and history events.

---

# API Route Organization

Route files should remain thin.

A route should normally:

1. Parse request.
2. validate transport schema.
3. resolve actor and correlation context.
4. call application service.
5. map result.
6. return response.

It should not contain domain decisions.

---

# Middleware Order

Recommended conceptual order:

```text
Request ID
    |
    v
Host and Origin Validation
    |
    v
Session or Local Authentication
    |
    v
CSRF Validation
    |
    v
Request Size Limit
    |
    v
Structured Logging
    |
    v
Route Handler
    |
    v
Error Translation
```

---

# Event Stream Organization

Frontend event contracts should be generated from versioned schemas.

Event transport code belongs in API infrastructure.

Domain event creation belongs in the owning module.

---

# Feature Flags

Feature-flag definitions should live in Configuration.

Modules may consume typed feature decisions.

They should not read feature-flag files directly.

---

# Experimental Code

Experimental features should be isolated.

Examples:

```text
ats/adapters/workday_experimental/
```

or guarded through explicit feature flags.

Experimental code must not silently replace stable implementations.

---

# Deprecated Code

Deprecated modules should include:

* Replacement path.
* planned removal version.
* compatibility tests.
* migration guidance.

Dead code should not remain indefinitely behind undocumented flags.

---

# Code Ownership

A conceptual ownership file may identify responsibility.

Example:

```text
candidate/        Candidate Data
jobs/             Job Intelligence
documents/        Document Generation
browser/          Browser Automation
ats/              ATS Integration
submission/       Submission Safety
security/         Security and Privacy
```

In a solo project, ownership still helps organize reviews and test responsibility.

---

# Change Review by Boundary

Changes require focused review when they affect:

* Canonical schema.
* candidate source precedence.
* work authorization.
* review approval.
* readiness.
* browser upload.
* ATS submission control.
* submission attempt.
* history status.
* sensitive-data policy.
* secret handling.

---

# Pull Request Organization

A change should ideally remain within one capability plus required contract updates.

Large changes spanning many modules should explain:

* Why the boundary change is necessary.
* which contracts changed.
* compatibility impact.
* migration impact.
* security impact.
* tests added.

---

# Repository Documentation

Recommended architecture documentation:

```text
docs/
    architecture/
        overview.md
        dependency_rules.md
        module_catalog.md
        data_flow.md
        security_boundaries.md

    development/
        setup.md
        testing.md
        adding_module.md
        adding_adapter.md
        schema_changes.md
        prompt_changes.md

    operations/
    user/
    api/
```

---

# Module README

Each major module should include a README or documentation page describing:

* Responsibility.
* owned entities.
* public interface.
* allowed dependencies.
* prohibited dependencies.
* persistence.
* events.
* errors.
* tests.
* known limitations.

---

# Module Catalog

The project should maintain a concise module catalog.

Example:

| Module     | Owns                            | Main Consumers                   |
| ---------- | ------------------------------- | -------------------------------- |
| Candidate  | Candidate facts and snapshots   | Jobs, Documents, Answers, Review |
| Packages   | Application Package aggregate   | Review, Readiness, Orchestration |
| Browser    | Browser sessions and actions    | ATS, Orchestration, Submission   |
| Submission | Final attempt and verification  | Orchestration, History           |
| History    | Application records and exports | UI, Operations                   |

---

# Build Outputs

Build outputs should use dedicated ignored directories.

Examples:

```text
dist/
build/
frontend/dist/
test-results/
coverage/
```

They should not be mixed with production source.

---

# Release Packaging

The release package should include:

* Backend source or executable.
* frontend build.
* canonical schemas.
* prompt templates.
* migrations.
* adapter metadata.
* version manifest.
* required static assets.

It should exclude:

* Tests unless needed.
* synthetic fixtures unless used for smoke tests.
* developer tools.
* real runtime data.
* secrets.
* browser profiles.

---

# Version Manifest

Recommended generated file:

```json
{
  "application_version": "1.0.0",
  "schema_registry_version": "1.0",
  "prompt_registry_version": "1.0",
  "frontend_version": "1.0.0",
  "adapter_versions": {
    "greenhouse": "1.0.0"
  }
}
```

---

# Import-Time Side Effects

Modules should avoid side effects during import.

Prohibited import-time behavior:

* Reading candidate data.
* starting a browser.
* loading secrets.
* opening network connections.
* running migrations.
* creating runtime directories.
* registering global routes unpredictably.

Initialization belongs in bootstrap.

---

# Global State

Global mutable state should be avoided.

Permitted limited globals may include:

* Immutable schema constants.
* enum definitions.
* stateless registries created during bootstrap.
* logger interface configuration.

---

# Thread and Process Safety

Even with sequential browser execution, file repositories and locks should assume that:

* Multiple UI tabs may issue commands.
* Maintenance tools may run.
* A previous process may have crashed.
* Another application instance may start accidentally.

State changes should use locks and version checks.

---

# Concurrency Boundary

Concurrency policy belongs in Orchestration and repository infrastructure.

Domain entities should not contain process-lock implementation.

---

# Example End-to-End Call Flow

## Package Preparation

```text
Frontend
    |
    v
Packages API
    |
    v
PrepareApplication Coordinator
    |
    +--> Candidate Snapshot Reader
    +--> Job Reader
    +--> Documents Service
    +--> Answers Service
    +--> Review Service
    +--> Readiness Service
    |
    v
Packages Repository
```

---

# Example Browser Execution Flow

```text
Orchestration
    |
    v
Readiness Public Interface
    |
    v
ATS Detection
    |
    v
ATS Adapter
    |
    v
Browser Public Interface
    |
    v
Playwright Infrastructure
```

---

# Example Submission Flow

```text
Orchestration
    |
    v
Submission Service
    |
    +--> Validate Review Approval
    +--> Validate Readiness
    +--> Acquire Submission Lock
    +--> Create Attempt
    +--> Request Browser Final Click
    +--> Request ATS Verification
    +--> Persist Result
    +--> Notify History
```

No ATS adapter or browser driver should skip the Submission Service.

---

# Forbidden Dependency Examples

## Browser Importing Candidate

Prohibited:

```text
browser -> candidate
```

Reason:

The browser should execute resolved values, not access candidate truth directly.

---

## ATS Importing History

Prohibited:

```text
ats -> history
```

Reason:

ATS adapters should interpret application pages, not determine duplicate history or tracker state.

---

## Frontend Reading Package Files

Prohibited:

```text
frontend -> filesystem package directory
```

Reason:

The backend must enforce authorization, versioning, and redaction.

---

## Documents Mutating Candidate Data

Prohibited:

```text
documents -> candidate repository write
```

Reason:

Generated content must not silently alter candidate truth.

---

## History Marking Submission Truth

Prohibited:

```text
history decides submitted
```

Reason:

Only Submission verification determines submission truth.

---

## Provider Output Triggering Browser Directly

Prohibited:

```text
reasoning provider -> browser action
```

Reason:

Provider output must be validated and converted through domain contracts.

---

# Allowed Dependency Examples

```text
documents -> candidate public read contract
documents -> jobs public read contract

review -> packages read model
review -> documents validation result
review -> answers answer set

ats -> browser public contract
orchestration -> readiness public contract
orchestration -> submission public contract
submission -> history public sync contract
```

---

# Architectural Tests

The test suite should include architecture tests that verify:

* Domain layers do not import infrastructure.
* Browser does not import Candidate.
* ATS adapters do not import History.
* Frontend cannot import backend file adapters.
* Submission click function exists only behind Submission public interface.
* Provider SDK imports are restricted.
* Playwright imports are restricted.
* spreadsheet-library imports are restricted.
* secret-store implementations are restricted.

---

# Static Dependency Report

CI should generate or validate a dependency graph.

Unexpected new edges should fail or require explicit review.

---

# Module Health Metrics

Useful internal maintenance metrics:

* Number of public exports.
* Number of cross-module dependencies.
* Circular dependencies.
* shared-kernel size.
* adapter-specific branching outside ATS.
* provider-specific branching outside infrastructure.
* browser-specific branching outside Browser.
* unowned schemas.
* untested public services.

These are maintainability indicators, not release metrics by themselves.

---

# Refactoring Rules

Refactoring should preserve:

* Public contracts.
* schema compatibility.
* domain ownership.
* audit behavior.
* security policy.
* submission state behavior.

Internal implementations may change freely when contracts remain valid.

---

# Extracting a Future Service

A module may become a separate service later when:

* It has a stable public contract.
* Its data ownership is clear.
* It has independent scaling or security needs.
* Network boundaries add real value.
* Distributed failure handling is designed.

The repository structure should make such extraction possible but should not optimize prematurely for it.

---

# Candidate Module Completion Criteria

The Candidate module is structurally complete when:

* It owns all candidate master entities.
* It exposes purpose-specific read interfaces.
* Source parsers are infrastructure adapters.
* Sensitive-value access is controlled.
* Other modules do not read candidate files directly.

---

# Job Module Completion Criteria

The Jobs module is structurally complete when:

* It owns Job, Job Source, Job Analysis, and Job Match.
* External-page readers are infrastructure adapters.
* Ranking is testable without browser or provider network calls.
* Job selection does not create Application Packages directly without the Package public interface.

---

# Package Module Completion Criteria

The Packages module is structurally complete when:

* It owns package identity, manifest, artifacts, status, and staleness.
* Other modules return results instead of editing package files.
* Package writes use version checks and atomic persistence.
* Package locks are abstracted.

---

# Browser and ATS Completion Criteria

The Browser and ATS boundaries are structurally complete when:

* Playwright remains inside Browser infrastructure.
* Browser actions are ATS-neutral.
* ATS adapters consume browser abstractions.
* candidate facts do not enter ATS adapters directly.
* final submission remains centralized in Submission.

---

# Submission Completion Criteria

The Submission module is structurally complete when:

* It is the only module authorized to create a final attempt.
* Click initiation is recorded before execution.
* ATS and browser implementations are ports.
* History synchronization uses a public History contract.
* Unknown outcomes cannot be converted to retries by other modules.

---

# Frontend Completion Criteria

The frontend structure is complete when:

* Features align with domain capabilities.
* Backend state remains authoritative.
* API types are generated.
* sensitive values use protected display components.
* external content is sanitized.
* no filesystem or Secret Store access exists.

---

# Repository Completion Criteria

The repository organization phase is complete when:

* Top-level directories are defined.
* Runtime data is excluded from source control.
* Domain modules have clear ownership.
* Public interfaces exist.
* dependency direction is documented.
* domain and infrastructure layers are separated.
* shared code remains minimal.
* composition occurs in one bootstrap area.
* schemas have one source of truth.
* prompts are versioned and owned.
* migrations are organized by domain.
* ATS adapters are isolated.
* Playwright is isolated.
* provider SDKs are isolated.
* spreadsheet libraries are isolated.
* frontend types are generated.
* tests mirror module ownership.
* architecture tests enforce import boundaries.
* scripts call public application services.
* final submission is structurally centralized.
* candidate facts cannot be silently mutated by generation modules.
* package files cannot be edited by unrelated modules.
* dependency cycles are prevented.
* module documentation exists.

---

# Definition of Boundary Safety

Module boundaries are safe when:

* Candidate truth has one owner.
* Job truth has one owner.
* Package state has one owner.
* Queue state has one owner.
* Submission truth has one owner.
* History status has one owner.
* Browser mechanics do not decide candidate answers.
* ATS adapters do not authorize submission.
* Reasoning-provider output does not execute directly.
* UI state does not override backend state.
* security policies apply consistently.
* file paths do not cross boundaries unchecked.
* infrastructure frameworks remain at the edges.

---

# Required Structural Test Scenarios

## Domain Imports Infrastructure

A domain file imports Playwright.

Expected:

* Architecture test fails.
* change cannot merge.

---

## Browser Reads Candidate Profile

Browser module imports Candidate repository.

Expected:

* Dependency rule fails.
* browser must receive a resolved interaction value instead.

---

## ATS Adapter Writes History

Adapter attempts to update CSV after confirmation.

Expected:

* Dependency rule fails.
* Submission or History public interface must be used.

---

## Documents Update Candidate Facts

Resume generation attempts to save a newly inferred skill.

Expected:

* Direct write is blocked.
* explicit Candidate update workflow is required.

---

## UI Sends Absolute File Path

Frontend sends `/Users/.../resume.pdf`.

Expected:

* API contract rejects arbitrary path.
* UI must use Artifact or File Reference ID.

---

## Provider Response Calls Browser

Provider output includes an action list with a direct selector.

Expected:

* Output cannot bypass Answer or ATS validation.
* Browser executes only a validated Interaction Plan.

---

## Second Submission Entry Point

An ATS adapter adds a direct `click_submit()` call outside Submission orchestration.

Expected:

* Architecture or code-search rule fails.
* final click must pass through Submission.

---

## Circular Module Dependency

Review imports Packages internals and Packages imports Review internals.

Expected:

* Cycle detector fails.
* a public read contract or coordinator is introduced.

---

## Shared Module Growth

Sponsorship-resolution logic is added to `shared/utils.py`.

Expected:

* Review rejects placement.
* logic moves to Candidate or Answers domain.

---

## Generated-Type Drift

Schema changes without regenerating TypeScript types.

Expected:

* CI generation-drift check fails.

---

# Definition of Phase Completion

The Repository Structure, Module Boundaries, and Code Organization phase is complete when the codebase can answer:

```text
Which module owns this entity?

Which module may mutate it?

Which public interface exposes it?

Which dependencies are allowed?

Where is the infrastructure implementation?

Where is the schema defined?

Where are its tests?

Which layer contains the business rule?

Can this component be tested without the full platform?

Can a framework or provider be replaced without rewriting domain policy?
```

The answers should be visible from the repository layout, module documentation, public contracts, and automated dependency checks.

---

# Summary

The repository should be organized as a modular local application rather than a monolithic automation script or prematurely distributed system.

The recommended structure uses:

* Domain-oriented backend modules.
* Explicit public interfaces.
* application services.
* abstract ports.
* infrastructure adapters.
* a single composition root.
* a local frontend.
* one canonical schema registry.
* versioned prompts.
* controlled ATS adapters.
* synthetic test fixtures.
* strict runtime-data separation.

The most important ownership rules are:

```text
Candidate owns candidate truth.
Jobs owns job truth.
Packages owns Application Package state.
Documents owns generated document logic.
Answers owns question and answer resolution.
Review owns findings and approval.
Readiness owns stage eligibility.
Browser owns browser mechanics.
ATS owns application-site interpretation.
Orchestration owns workflow progression.
Submission owns the irreversible action and its truth.
History owns tracking and recruitment status.
Security owns access and sensitive-data policy.
Observability owns logs, audit records, and health reporting.
```

The most important dependency rule is:

```text
High-level policy must not depend directly on low-level frameworks.
```

The most important submission rule is:

```text
No code outside the Submission boundary may authorize or record a final application submission.
```

A well-organized repository will make the platform easier to test, safer to change, simpler to maintain, and more resistant to the architectural drift that could compromise candidate accuracy, privacy, or submission safety.
