# 09 - ATS Adapters and Generic Form Engine

## LLM-Powered Autonomous Job Search & Application Platform

Version: 1.0

---

# Purpose

This document defines the Applicant Tracking System adapter framework and Generic Form Engine responsible for translating diverse job-application websites into a common application workflow.

Applicant Tracking Systems vary significantly in:

* Page structure.
* Authentication requirements.
* Field naming.
* Form controls.
* Resume parsing.
* Multi-page navigation.
* Validation behavior.
* Document-upload handling.
* Review-page structure.
* Submission controls.
* Confirmation signals.
* Application-status dashboards.

The platform should not implement one large collection of website-specific browser scripts.

Instead, it should use:

* A shared ATS adapter contract.
* Dedicated adapters for supported ATS platforms.
* A Generic Form Engine for standard and unknown application forms.
* Capability detection.
* Structured page and field models.
* Deterministic browser actions.
* Verified fallback behavior.
* Clear unsupported-state handling.

The browser engine performs low-level browser actions.

ATS adapters and the Generic Form Engine interpret application structure and convert it into browser-executable plans.

---

# Core Principle

ATS-specific knowledge should be isolated behind a common interface.

```text
Application URL
        |
        v
ATS Detection
        |
        v
Adapter Selection
        |
        +------> Dedicated ATS Adapter
        |
        +------> Generic Form Engine
        |
        +------> Manual Completion
        |
        v
Structured Application Workflow
        |
        v
Browser Automation Engine
```

The rest of the application should not depend on Workday-specific, Greenhouse-specific, Lever-specific, or other ATS-specific browser details.

---

# Objectives

The ATS adapter framework should:

* Identify the ATS serving an application.
* Route the application to the best available adapter.
* Normalize ATS pages into common page types.
* Normalize fields into canonical field models.
* Support ATS-specific controls.
* Handle ATS-specific account and login workflows.
* Handle resume uploads and parsing.
* Handle repeating employment and education sections.
* Navigate multi-page applications.
* Detect review and submission pages.
* Verify submission success.
* Fall back safely to a generic form engine.
* Detect unsupported workflows.
* Avoid brittle selectors.
* Recover when ATS markup changes.
* Preserve application state.
* Expose structured capabilities to the orchestrator.
* Keep candidate facts outside adapter implementations.

---

# Scope

This document covers:

* ATS detection.
* Adapter registry.
* Adapter selection.
* Adapter contracts.
* Capability declarations.
* Page-type detection.
* Form extraction.
* Field normalization.
* Generic form handling.
* ATS-specific custom controls.
* Authentication flows.
* File uploads.
* Resume parsing.
* Repeating sections.
* Review pages.
* Submission.
* Confirmation detection.
* Fallback strategy.
* Adapter health.
* Versioning.
* Testing.
* Security.
* Observability.

This document does not define:

* Candidate facts.
* Resume tailoring.
* Cover-letter generation.
* Answer generation.
* Application ranking.
* Workflow queue ordering.
* Low-level Playwright implementation.
* CAPTCHA bypass.
* Anti-bot evasion.

---

# Architectural Responsibilities

```text
ATS Integration Layer
    |
    +-- ATS Detector
    +-- Adapter Registry
    +-- Adapter Router
    +-- Capability Resolver
    +-- Dedicated ATS Adapters
    +-- Generic Form Engine
    +-- Page Classifier
    +-- Form Normalizer
    +-- Widget Handler Registry
    +-- Submission Signal Resolver
    +-- Adapter Health Monitor
    +-- Adapter Fixture Library
```

---

# Separation of Responsibilities

## Browser Automation Engine

Responsible for:

* Opening pages.
* Locating elements.
* Clicking.
* Typing.
* Selecting.
* Uploading files.
* Waiting for page changes.
* Capturing screenshots.
* Reading browser-visible values.
* Verifying low-level actions.

## ATS Adapter

Responsible for:

* Recognizing ATS-specific page structures.
* Classifying ATS pages.
* Extracting ATS-specific fields.
* Interpreting custom controls.
* Building browser action plans.
* Navigating ATS-specific steps.
* Detecting ATS review pages.
* Identifying ATS submission controls.
* Verifying ATS-specific confirmation signals.

## Generic Form Engine

Responsible for:

* Inspecting unknown or standard forms.
* Normalizing accessible controls.
* Classifying fields.
* Resolving standard widgets.
* Executing generic multi-page form workflows.
* Falling back when no dedicated adapter exists.

## Application Answer Service

Responsible for:

* Determining what answer should be used.
* Mapping questions to canonical families.
* Validating answer truthfulness.
* Returning browser-ready values.

Adapters must not invent answers.

---

# ATS Adapter Contract

Every dedicated ATS adapter should implement a shared conceptual interface.

```text
ATSAdapter

    get_adapter_metadata()
    detect(context)
    get_capabilities(context)

    classify_page(page_snapshot)
    inspect_page(page_snapshot)
    extract_job_identity(page_snapshot)
    extract_form(page_snapshot)

    build_page_plan(form_model, answer_set)
    validate_page(page_snapshot, expected_state)
    determine_next_action(page_snapshot)

    handle_authentication(page_snapshot)
    handle_account_creation(page_snapshot)
    handle_resume_upload(page_snapshot, file_reference)
    inspect_resume_parsing(page_snapshot)

    add_repeating_entry(section_type)
    inspect_repeating_entries(section_type)

    detect_review_page(page_snapshot)
    extract_review_snapshot(page_snapshot)

    identify_submission_control(page_snapshot)
    submit(page_snapshot, submission_plan)
    verify_submission(page_snapshot, submission_attempt)

    create_checkpoint_context(page_snapshot)
    restore_checkpoint(checkpoint)
```

The implementation may use the Browser Automation Engine internally through approved high-level browser operations.

---

# Adapter Metadata

Each adapter should expose metadata.

Example:

```json
{
  "adapter_id": "greenhouse",
  "display_name": "Greenhouse",
  "adapter_version": "1.0.0",
  "schema_version": "1.0",
  "enabled": true,
  "status": "stable",
  "supported_domains": [],
  "supported_page_signatures": [],
  "minimum_browser_engine_version": "1.0",
  "capabilities": {}
}
```

---

# Adapter Status

Supported adapter statuses:

```text
experimental
beta
stable
degraded
disabled
unsupported
```

---

## Experimental

Initial support with limited testing.

Automatic submission should be disabled by default.

---

## Beta

Major flows work, but broader testing is still required.

Review mode should be recommended.

---

## Stable

Supported test workflows pass consistently.

Automatic mode may be permitted.

---

## Degraded

The ATS appears to have changed or an important capability is failing.

Generic fallback or manual mode should be preferred.

---

## Disabled

The adapter is intentionally unavailable.

---

## Unsupported

The ATS or workflow cannot currently be handled safely.

---

# Adapter Registry

## Responsibility

Maintain all available adapters and their capabilities.

Conceptual interface:

```text
ATSAdapterRegistry

    register(adapter)
    unregister(adapter_id)
    get_adapter(adapter_id)
    list_adapters()
    find_candidates(url, page_snapshot)
    get_adapter_status(adapter_id)
    update_adapter_health(adapter_id, result)
```

---

# Adapter Registration

An adapter registration should include:

* Adapter ID.
* Version.
* Supported domains.
* URL patterns.
* Page signatures.
* Capabilities.
* Priority.
* Health status.
* Test status.
* Generic-fallback compatibility.

---

# Adapter Priority

When multiple adapters match:

1. Explicit package override.
2. Exact domain and page-signature match.
3. Exact embedded-ATS signature.
4. High-confidence page-signature match.
5. Domain-only match.
6. Generic Form Engine.
7. Manual mode.

---

# ATS Detection

The ATS Detector should identify which platform controls the application.

Detection may occur:

* From the original job URL.
* After following the Apply link.
* After an external redirect.
* After an embedded application form loads.
* After login.
* On every major domain or page-signature change.

---

# Detection Signals

The detector may inspect:

* Hostname.
* URL path.
* Page title.
* HTML metadata.
* Script sources.
* Form action.
* Accessibility structure.
* DOM attributes.
* Known element IDs.
* Known data attributes.
* Known API endpoints.
* Page headings.
* Embedded iframe domains.
* ATS-specific asset names.

No single signal should be considered authoritative when false matches are possible.

---

# ATS Detection Result

```json
{
  "detected_ats": "workday",
  "confidence": 98,
  "detection_method": [
    "domain_pattern",
    "page_signature",
    "script_source"
  ],
  "matched_adapter": "workday",
  "generic_fallback_allowed": true,
  "warnings": []
}
```

---

# Detection Confidence

Suggested interpretation:

```text
95–100:
Exact, verified adapter match.

80–94:
Strong multi-signal match.

60–79:
Probable match requiring page verification.

Below 60:
Use generic inspection or manual confirmation.
```

---

# Domain Detection

Domain matching may include:

* Primary ATS domains.
* Company-specific ATS subdomains.
* White-labeled ATS domains.
* Embedded ATS iframes.
* Regional ATS domains.

Domain matching should not assume that all pages on a domain use the same workflow version.

---

# Page Signature

A page signature is a stable set of characteristics used to identify an ATS page or workflow version.

Example signature fields:

```json
{
  "adapter_id": "example_ats",
  "page_type": "personal_information",
  "required_roles": [
    "textbox",
    "button"
  ],
  "required_labels": [
    "First Name",
    "Last Name"
  ],
  "known_attributes": [],
  "known_heading_patterns": [],
  "url_patterns": []
}
```

Page signatures should favor stable semantic characteristics over CSS class names.

---

# Signature Matching

Signature matching may use:

* Exact required signal matches.
* Weighted optional signals.
* Negative signals.
* Page-type-specific thresholds.
* Adapter-version compatibility.

Example:

```text
Required signals passed: 5 of 5
Optional signals passed: 7 of 9
Negative signals found: 0
Confidence: 96
```

---

# Negative Detection Signals

Negative signals reduce confidence.

Examples:

* Page matches another ATS more strongly.
* Expected ATS form root is absent.
* Application is embedded in a third-party assessment tool.
* URL changed to an unrelated domain.
* Page is a corporate login gateway rather than the ATS.
* Page is a job aggregator redirect.

---

# Re-Detection

ATS detection should rerun when:

* Domain changes.
* New tab opens.
* Iframe changes.
* Login completes.
* Application redirects.
* Dedicated adapter reports an incompatible page.
* Page signature changes materially.
* The application moves into an assessment platform.

---

# Application Identity Preservation

ATS redetection must preserve application identity.

Compare:

* Company.
* Job title.
* Job ID.
* Requisition ID.
* Location.
* Original application URL.

If the ATS redirect leads to another job, the workflow should stop.

---

# Adapter Capability Model

Adapters should declare supported capabilities.

Example:

```json
{
  "authentication": true,
  "account_creation": true,
  "guest_application": false,
  "resume_upload": true,
  "resume_parsing": true,
  "cover_letter_upload": true,
  "repeating_employment": true,
  "repeating_education": true,
  "searchable_dropdowns": true,
  "multi_select": true,
  "custom_date_picker": true,
  "review_page": true,
  "submission_verification": true,
  "application_dashboard": true,
  "generic_fallback": true
}
```

---

# Capability Levels

A capability may be:

```text
supported
partially_supported
manual_only
unsupported
unknown
```

---

# Capability Resolution

The router should evaluate both:

* Adapter-level capabilities.
* Current workflow capabilities.

An ATS may generally support guest applications, while one employer requires account creation.

---

# Capability Readiness Result

```json
{
  "adapter_id": "example_ats",
  "workflow_capabilities": {
    "resume_upload": "supported",
    "repeating_employment": "supported",
    "assessment_redirect": "manual_only"
  },
  "automatic_execution_allowed": false,
  "recommended_mode": "review"
}
```

---

# Common Page Types

Adapters and the Generic Form Engine should normalize pages into common types.

```text
job_detail
application_start
login
account_creation
email_verification
candidate_dashboard
personal_information
contact_information
resume_upload
work_history
education
skills
questionnaire
work_authorization
demographic_disclosure
legal_disclosure
supporting_documents
review
submission
confirmation
application_closed
captcha
error
unknown
```

---

# Page Classification Result

```json
{
  "page_type": "work_history",
  "confidence": 94,
  "adapter_id": "workday",
  "page_number": 3,
  "step_label": "Experience",
  "application_identity": {},
  "warnings": []
}
```

---

# Common Form Model

Every adapter should normalize forms into the same form model.

```json
{
  "form_id": "work_authorization",
  "page_type": "work_authorization",
  "page_number": 5,
  "title": "Work Authorization",
  "sections": [],
  "fields": [],
  "actions": [],
  "validation_messages": [],
  "adapter_metadata": {}
}
```

---

# Common Field Model

```json
{
  "field_id": "future_sponsorship",
  "adapter_field_id": "",
  "label": "Will you now or in the future require sponsorship?",
  "help_text": "",
  "field_type": "radio",
  "semantic_type": "work_authorization.sponsorship_future",
  "required": true,
  "visible": true,
  "enabled": true,
  "read_only": false,
  "current_value": null,
  "options": [],
  "constraints": {},
  "selector_candidates": [],
  "container_context": {},
  "confidence": 97
}
```

---

# Field Constraints

Constraints may include:

```json
{
  "minimum_length": null,
  "maximum_length": 1000,
  "minimum_value": null,
  "maximum_value": null,
  "pattern": null,
  "allowed_file_types": [],
  "maximum_file_size_bytes": null,
  "maximum_selections": null,
  "date_format": null
}
```

---

# Common Action Model

```json
{
  "action_id": "continue",
  "action_type": "next",
  "label": "Save and Continue",
  "enabled": true,
  "final_submission": false,
  "selector_candidates": []
}
```

Supported action types:

```text
start_application
save
next
previous
add_entry
remove_entry
edit_entry
upload
review
submit
cancel
return_to_dashboard
```

---

# Adapter Context

The adapter should receive structured context rather than unrestricted application access.

Example:

```json
{
  "package_id": "",
  "application_url": "",
  "job_identity": {},
  "browser_profile": "",
  "automation_mode": "review",
  "candidate_rules": {},
  "execution_state": {},
  "active_documents": {}
}
```

---

# Dedicated Adapter Design

A dedicated adapter should contain:

* ATS detection rules.
* Page signatures.
* Page classifiers.
* ATS field extraction logic.
* Custom widget handlers.
* ATS navigation logic.
* ATS validation parsing.
* Review-page extraction.
* Submission-control detection.
* Confirmation detection.
* ATS-specific recovery logic.

It should not contain:

* Candidate-specific values.
* Hardcoded personal answers.
* Resume text.
* Company-specific candidate rules.
* Credentials.
* User passwords.
* Demographic assumptions.

---

# Dedicated Adapter Directory Structure

Conceptual structure:

```text
ats/
    adapters/
        base/
        workday/
            metadata
            detection
            page_classifier
            form_extractor
            widget_handlers
            navigation
            submission
            fixtures
        greenhouse/
        lever/
        smartrecruiters/
        ashby/
        icims/
        taleo/
```

This is a conceptual module organization, not an implementation requirement.

---

# ATS Examples

Initial adapter targets may include:

* Workday.
* Greenhouse.
* Lever.
* SmartRecruiters.
* Ashby.
* iCIMS.
* Taleo.
* Company-hosted custom forms.

The MVP should support a limited number deeply rather than claiming broad unreliable coverage.

---

# Workday Adapter Considerations

A Workday adapter may need to handle:

* Candidate account login.
* Account creation.
* Multiple workflow steps.
* Custom modal dropdowns.
* Searchable location fields.
* Repeating work-experience sections.
* Repeating education sections.
* Resume parsing.
* Review-and-submit pages.
* Candidate dashboard.
* Session expiration.
* Employer-specific custom questions.

The adapter should not assume every employer uses identical Workday configuration.

---

# Greenhouse Adapter Considerations

A Greenhouse adapter may need to handle:

* One-page or short multi-section forms.
* Standard personal fields.
* Resume and cover-letter uploads.
* Employer-defined custom questions.
* Searchable dropdowns.
* Voluntary demographic sections.
* Submission confirmation.
* Embedded forms.
* Hosted forms and company-branded wrappers.

---

# Lever Adapter Considerations

A Lever adapter may need to handle:

* Compact application forms.
* Resume upload.
* Personal details.
* Links.
* Additional information.
* Employer-specific custom questions.
* Location and work-authorization fields.
* Confirmation pages.

---

# SmartRecruiters Adapter Considerations

A SmartRecruiters adapter may need to handle:

* Account or profile flows.
* Resume parsing.
* Profile information.
* Experience and education.
* Questionnaire sections.
* Consent and privacy fields.
* Review and submission.
* Regional privacy differences.

---

# Ashby Adapter Considerations

An Ashby adapter may need to handle:

* Hosted job pages.
* Structured application forms.
* Custom questions.
* Resume and supporting-document uploads.
* Form validation.
* Voluntary demographic sections.
* Confirmation pages.

---

# iCIMS Adapter Considerations

An iCIMS adapter may need to handle:

* Branded career portals.
* Candidate login.
* Profile creation.
* Multi-page workflows.
* Resume parsing.
* Repeating sections.
* Legacy and modern UI variants.
* Privacy and consent pages.
* Application dashboard.

---

# Taleo Adapter Considerations

A Taleo adapter may need to handle:

* Candidate accounts.
* Multi-step application processes.
* Older control structures.
* Repeating employment and education forms.
* Prescreening questions.
* Save-and-continue behavior.
* Session timeouts.
* Application status pages.

---

# Employer-Specific Customization

An ATS adapter should support employer-specific configuration without forking the entire adapter.

Example:

```json
{
  "adapter_id": "workday",
  "employer_profile": "example_company",
  "overrides": {
    "account_creation_required": true,
    "custom_question_mappings": {},
    "known_page_signatures": [],
    "submission_confirmation_patterns": []
  }
}
```

---

# Employer Override Rules

Employer-specific overrides may define:

* Known workflow sequence.
* Stable custom field mappings.
* Required documents.
* Review-page behavior.
* Confirmation patterns.
* Login requirements.
* Known problematic widgets.
* Country-specific workflow differences.

Overrides must not contain candidate-specific answers.

---

# Generic Form Engine

## Responsibility

Handle standard and unknown application forms when no dedicated adapter is available or when a dedicated adapter partially fails.

The Generic Form Engine should favor semantic browser information over site-specific markup.

---

# Generic Form Engine Components

```text
Generic Form Engine
    |
    +-- Page Discovery
    +-- Form Boundary Detector
    +-- Field Extractor
    +-- Label Resolver
    +-- Field Type Classifier
    +-- Semantic Field Classifier
    +-- Widget Detector
    +-- Action Detector
    +-- Form Plan Builder
    +-- Validation Interpreter
    +-- Page Progression Detector
    +-- Submission Signal Detector
```

---

# Generic Engine Entry Conditions

Use the Generic Form Engine when:

* No dedicated adapter matches.
* Detection confidence is below threshold.
* Dedicated adapter supports only part of the workflow.
* Employer uses a custom application page.
* ATS markup changed but standard accessible controls remain usable.
* Package settings permit generic fallback.

---

# Generic Engine Restrictions

The Generic Form Engine should not continue automatically when:

* Final submission control cannot be distinguished from navigation.
* Job identity cannot be confirmed.
* Required field meaning remains ambiguous.
* A control cannot be manipulated or verified.
* An unsupported security challenge appears.
* An unknown domain requests sensitive information.
* The page requires arbitrary local-file access.
* Submission success cannot be verified and automatic mode would be unsafe.

---

# Form Boundary Detection

The engine should identify application forms using:

* `<form>` elements.
* ARIA form roles.
* Headings.
* Field grouping.
* Required-field patterns.
* Buttons such as Apply, Continue, Review, or Submit.
* Page URL and job identity.
* Visible section boundaries.
* ATS-specific root containers when recognized.

A page may contain multiple unrelated forms.

Examples:

* Search form.
* Newsletter form.
* Login form.
* Job application form.

The engine must select the correct one.

---

# Form Boundary Result

```json
{
  "form_candidates": [
    {
      "form_id": "candidate_application",
      "confidence": 96,
      "field_count": 18,
      "application_related": true
    },
    {
      "form_id": "job_search",
      "confidence": 20,
      "field_count": 2,
      "application_related": false
    }
  ],
  "selected_form_id": "candidate_application"
}
```

---

# Field Extraction

The engine should extract:

* Text inputs.
* Text areas.
* Select elements.
* Comboboxes.
* Listboxes.
* Radio groups.
* Checkboxes.
* Switches.
* Date inputs.
* File inputs.
* Content-editable fields.
* Buttons.
* Repeating-section controls.
* Hidden validation inputs when relevant.

Only visible or conditionally relevant fields should normally be included.

---

# Label Resolution

Field labels may be resolved through:

1. Explicit `<label for>`.
2. Wrapping label.
3. Accessible name.
4. ARIA label.
5. ARIA-labelledby.
6. Nearby text.
7. Placeholder.
8. Table or grid header.
9. Group heading.
10. Parent section heading.

The engine should retain all label evidence.

---

# Label Resolution Result

```json
{
  "primary_label": "Phone Number",
  "label_sources": [
    {
      "type": "associated_label",
      "value": "Phone Number"
    },
    {
      "type": "placeholder",
      "value": "(555) 555-5555"
    }
  ],
  "confidence": 99
}
```

---

# Generic Field Type Classification

Field types should be classified through deterministic signals first.

Examples:

```text
input[type=text] -> text
input[type=email] -> email
input[type=tel] -> phone
input[type=url] -> url
input[type=number] -> number
input[type=date] -> date
input[type=file] -> upload
textarea -> textarea
select -> dropdown
role=combobox -> searchable_dropdown or dropdown
role=radio -> radio
role=checkbox -> checkbox
contenteditable=true -> rich_text
```

---

# Semantic Field Classification

Semantic classification maps a visible field to a canonical candidate concept.

Examples:

```text
“Given Name” -> personal.first_name

“Are you legally eligible to work in this country?”
    -> work_authorization.authorized_now

“Will sponsorship ever be required?”
    -> work_authorization.sponsorship_future
```

---

# Semantic Classification Priority

1. Exact known label mapping.
2. Employer-specific mapping.
3. ATS-specific mapping.
4. Canonical synonym mapping.
5. Input attributes.
6. Section context.
7. Available options.
8. Reusable semantic cache.
9. Reasoning-provider classification.
10. User input.

---

# Semantic Classification Result

```json
{
  "semantic_type": "preferences.relocation",
  "confidence": 93,
  "classification_method": "canonical_synonym_mapping",
  "requires_review": false
}
```

---

# Unknown Fields

When a field cannot be classified:

1. Extract structured field context.
2. Inspect help text and options.
3. Search known mappings.
4. Search semantic cache.
5. Ask the reasoning provider for classification.
6. Validate the result.
7. Request user input when material ambiguity remains.

The engine should not fill an unknown required field with a placeholder.

---

# Widget Handler Registry

Custom controls should use reusable widget handlers.

```text
Widget Handler Registry
    |
    +-- Native Text Handler
    +-- Native Select Handler
    +-- Searchable Combobox Handler
    +-- Multi-Select Handler
    +-- Date Picker Handler
    +-- Radio Group Handler
    +-- Checkbox Group Handler
    +-- File Upload Handler
    +-- Rich Text Handler
    +-- Repeating Section Handler
    +-- Address Autocomplete Handler
    +-- Signature Handler
```

---

# Widget Handler Contract

```text
WidgetHandler

    detect(field_context)
    extract_state(field_context)
    build_interaction(field_context, answer)
    execute(interaction)
    verify(expected_value)
    clear()
    recover(error_context)
```

---

# Widget Handler Selection

Selection should use:

* Native element type.
* ARIA role.
* DOM structure.
* Known library signature.
* ATS adapter hint.
* Interaction behavior.
* Available options.

---

# Native Text Fields

The handler should:

* Confirm visibility.
* Confirm enabled state.
* Clear when appropriate.
* Enter value.
* Trigger required input events.
* Read value back.
* Detect validation messages.

---

# Native Dropdowns

The handler should:

* Extract all available options.
* Resolve exact portal option.
* Select by label when possible.
* Verify selected value.
* Detect disabled or placeholder options.

---

# Searchable Dropdowns

The handler should:

1. Open the control.
2. Detect the dropdown panel.
3. Enter search text.
4. Wait for matching options.
5. Select the intended result.
6. Verify the displayed selected value.
7. Confirm the dropdown closed.

---

# Searchable Dropdown Risks

Common risks:

* Selecting the first result without exact match.
* Pressing Enter before options load.
* Matching the wrong city with the same name.
* Selecting a placeholder.
* Selecting a disabled option.
* Selecting a value from a previous search.

The handler should verify option identity.

---

# Multi-Select Controls

The handler should:

* Extract available options.
* Select each approved value.
* Verify selected tokens.
* Respect maximum-selection limits.
* Remove unintended values.
* Preserve order only when meaningful.

---

# Radio Groups

The handler should:

* Identify group label.
* Extract all choices.
* Resolve intended option.
* Select one option.
* Verify checked state.
* Confirm no conflicting option remains.

---

# Checkbox Groups

The handler should distinguish:

* Single acknowledgment checkbox.
* Boolean answer.
* Multi-select option group.
* Consent.
* Legal attestation.
* Optional marketing permission.

It must not automatically select all required-looking checkboxes.

---

# Date Picker Controls

The handler should support:

* Native date inputs.
* Text date fields.
* Calendar popups.
* Month and year selectors.
* Separate month, day, and year fields.
* Current-employer end-date exceptions.

It should prefer direct deterministic entry when supported.

---

# Date Verification

Verify:

* Final displayed date.
* Underlying input value.
* Required date format.
* No locale reversal.
* Date falls within allowed range.
* Start and end dates remain logically consistent.

---

# Address Autocomplete

Address widgets may provide suggestions.

The handler should:

* Enter candidate address text.
* Wait for suggestions.
* Select the correct address when exact.
* Verify address components.
* Avoid selecting similarly named locations.
* Fall back to manual component fields when supported.

Sensitive address handling should remain local.

---

# Rich Text Editors

The handler should detect:

* Content-editable elements.
* Embedded editor iframes.
* Hidden backing text areas.
* Editor-specific controls.

Plain text should be used unless formatting is required.

The handler should verify visible content and backing value when possible.

---

# File Upload Widgets

The handler should support:

* Native file input.
* Drag-and-drop upload zones backed by file input.
* Upload buttons that expose file inputs.
* Multiple-file upload.
* File replacement.
* Upload progress.
* Upload failure messages.

It should not interact with native operating-system file dialogs when direct input assignment is available.

---

# Upload Verification

Verify:

* Correct file name.
* Correct document type.
* Upload progress completed.
* No failure message.
* Replace or remove control appears.
* ATS shows uploaded-file token.
* Correct file remains active.

---

# Resume Parsing

After resume upload, an ATS may automatically populate fields.

The adapter or Generic Form Engine should:

1. Wait for parsing to finish.
2. Reinspect the page.
3. Detect changed fields.
4. Compare parsed values with candidate facts.
5. Correct errors.
6. Record the parsing result.
7. Avoid treating parsed data as authoritative.

---

# Resume Parsing Result

```json
{
  "status": "completed",
  "fields_populated": 14,
  "correct_values": 10,
  "corrected_values": 4,
  "unresolved_values": 0,
  "warnings": []
}
```

---

# Repeating Section Engine

Applications frequently require repeated entries for:

* Employment.
* Education.
* Certifications.
* Languages.
* References.
* Projects.

The Generic Form Engine should support a reusable repeating-section model.

---

# Repeating Section Model

```json
{
  "section_id": "employment_history",
  "semantic_type": "employment",
  "existing_entries": [],
  "add_action": {},
  "maximum_entries": null,
  "minimum_entries": 1
}
```

---

# Repeating Entry Workflow

```text
Inspect Existing Entries
        |
        v
Match Entries to Candidate Records
        |
        v
Determine Required Entry Count
        |
        v
Add or Remove Entries
        |
        v
Fill Each Entry
        |
        v
Save Each Entry
        |
        v
Verify Entry Summary
```

---

# Existing Entry Matching

ATS resume parsing may create existing entries.

The engine should match them using:

* Employer.
* Job title.
* Start date.
* End date.
* Institution.
* Degree.
* Graduation date.

It should not duplicate entries already parsed correctly.

---

# Entry Matching Result

```json
{
  "candidate_record_id": "employment_1",
  "ats_entry_id": "entry_3",
  "match_confidence": 97,
  "action": "update_existing"
}
```

---

# Repeating Entry Actions

Supported actions:

```text
add
edit
remove
save
cancel_edit
expand
collapse
reorder
```

---

# Employment Entry Handling

Fields may include:

* Company.
* Title.
* Location.
* Start date.
* End date.
* Current-employer checkbox.
* Responsibilities.
* Reason for leaving.
* Employment type.

The adapter should preserve exact candidate records.

---

# Education Entry Handling

Fields may include:

* Institution.
* Degree.
* Field of study.
* Start date.
* Graduation date.
* GPA.
* Country.
* Current-student indicator.

Institution and degree option mappings should be verified.

---

# Entry Save Verification

After saving a repeated entry, verify:

* Entry summary appears.
* Key values match.
* Edit control becomes available.
* No validation error remains.
* Draft editor closed.
* Correct entry count exists.

---

# Multi-Page Workflow Engine

The adapter should normalize ATS navigation into common stages.

```text
Start
Personal Information
Experience
Education
Questions
Disclosures
Review
Submit
Confirmation
```

Actual labels may vary.

---

# Workflow Map

An adapter may provide a known workflow map.

```json
{
  "adapter_id": "example_ats",
  "steps": [
    {
      "step_id": "personal",
      "required": true
    },
    {
      "step_id": "experience",
      "required": true
    },
    {
      "step_id": "review",
      "required": true
    }
  ]
}
```

The real page sequence should still be verified dynamically.

---

# Dynamic Workflow Variants

Workflow steps may change based on:

* Country.
* Job.
* Employer.
* Candidate answers.
* Resume parsing.
* Account state.
* Required documents.
* Legal disclosures.

Adapters should not rely exclusively on a fixed page count.

---

# Step Indicator Extraction

The engine may inspect:

* Progress bars.
* Breadcrumbs.
* Step labels.
* Numbered navigation.
* Headings.
* Current section markers.

Example:

```json
{
  "current_step": 3,
  "total_steps": 6,
  "current_label": "Experience",
  "completed_steps": [
    "Personal Information",
    "Documents"
  ]
}
```

---

# Page Progression

After clicking Next or Save and Continue, verify:

* Step changed.
* URL changed.
* Page signature changed.
* Form fields changed.
* Validation errors did not block progression.

The adapter should not assume button clicks advance the workflow.

---

# Save and Continue

Some ATS platforms save data before advancing.

The adapter should distinguish:

* Save only.
* Save and continue.
* Continue without save.
* Review.
* Submit.

Incorrect action classification may lose data or submit prematurely.

---

# Back Navigation

When returning to a previous step:

* Preserve current data.
* Verify earlier values remain.
* Avoid triggering duplicate parsing.
* Update checkpoint state.
* Rerun review when material values change.

---

# Account and Authentication Flows

Some ATS platforms require:

* Existing account login.
* Account creation.
* Email verification.
* Password setup.
* Multifactor authentication.
* Privacy consent.
* Candidate-profile acceptance.

---

# Authentication Capability Model

```json
{
  "login_supported": true,
  "account_creation_supported": true,
  "email_verification": "manual_only",
  "mfa": "manual_only",
  "persistent_session": true
}
```

---

# Existing Session Detection

The adapter should determine whether the user is:

* Logged in.
* Logged out.
* On the wrong account.
* In an expired session.
* In a partially created account.
* At a verification screen.

---

# Wrong Account Detection

When possible, compare:

* Logged-in email.
* Candidate email.
* Candidate profile name.

If a different candidate account is active:

* Pause.
* Do not overwrite profile data.
* Request user action.
* Allow profile switching.

---

# Account Creation Rules

Account creation may proceed only when:

* Application requires it.
* Candidate rules permit it.
* Approved email is available.
* Password handling follows secure policy.
* User verification is available.
* Existing-account checks have been performed.

---

# Password Handling

Adapters must not:

* Store plaintext passwords in package files.
* Send passwords to Claude.
* Write passwords to logs.
* Capture passwords in screenshots when avoidable.

Preferred options:

* Existing browser session.
* Runtime user entry.
* Operating-system credential manager.
* Secure local secret store.

---

# Email Verification

When verification is required:

* Pause workflow.
* Preserve page state.
* Request user verification.
* Detect completion.
* Resume at a safe checkpoint.

---

# MFA

MFA is manual unless a secure authorized integration exists.

The adapter must not attempt to bypass MFA.

---

# Privacy and Consent Pages

ATS platforms may require:

* Privacy notice acknowledgment.
* Data-processing consent.
* Regional disclosure consent.
* Terms of use.
* Marketing preferences.

The adapter should distinguish mandatory application consent from optional marketing consent.

---

# Consent Handling

Mandatory consent may be selected when:

* Candidate rules permit it.
* The full statement is captured.
* The statement is required to apply.
* The action is recorded.

Optional marketing consent should follow user preferences and should default to not selected unless configured otherwise.

---

# Job Identity Extraction

Every adapter should attempt to extract:

* Company.
* Job title.
* Job ID.
* Requisition ID.
* Location.
* Country.
* Department.
* Application URL.

---

# Job Identity Result

```json
{
  "company": "",
  "job_title": "",
  "job_id": "",
  "requisition_id": "",
  "location": "",
  "confidence": 98
}
```

---

# Identity Verification

Compare extracted identity with the Application Package.

Possible outcomes:

```text
match
normalized_match
partial_match
mismatch
unverifiable
```

Mismatch blocks execution.

---

# Review Page Detection

The adapter should identify pages where the application can be reviewed before submission.

Signals:

* Heading such as Review Application.
* Summary sections.
* Edit links.
* Attached-file summaries.
* Submit button.
* Step indicator showing final step.

---

# Review Snapshot

```json
{
  "job_identity": {},
  "sections": [
    {
      "section_type": "personal_information",
      "values": []
    }
  ],
  "uploaded_files": [],
  "attestations": [],
  "submit_control": {}
}
```

---

# Review Extraction Requirements

Extract when available:

* Personal information.
* Work history.
* Education.
* Questionnaire answers.
* Work authorization.
* Legal responses.
* Demographic responses.
* Uploaded documents.
* Signature.
* Attestations.

Sensitive values may be masked in routine logs.

---

# Review Page Editing

When the review page contains Edit controls:

* Map each Edit control to its section.
* Allow corrections.
* Preserve checkpoint state.
* Return to review page.
* Rerun Application Review.

---

# Submission Control Detection

The adapter must distinguish final submission controls from:

* Next.
* Continue.
* Save.
* Review.
* Complete Profile.
* Add Information.
* Return to Dashboard.

---

# Final Submission Signals

A control may be considered final submission when:

* Label explicitly indicates submission.
* Page is classified as review or submission.
* No later application step is visible.
* Employer instructions identify it as final.
* Adapter signature confirms the control.

Ambiguous controls require manual review.

---

# Submission Control Result

```json
{
  "action_id": "submit_application",
  "label": "Submit Application",
  "final_submission": true,
  "confidence": 99,
  "selector_candidates": []
}
```

---

# Submission Execution

Submission should occur through the Browser Automation Engine after:

* Application Review passes.
* Submission Readiness passes.
* Submission lock is acquired.
* Final control is verified.

The adapter should provide the submission plan and expected confirmation signals.

---

# Confirmation Detection

Dedicated adapters should define strong confirmation signals.

Possible signals:

* Confirmation heading.
* Success message.
* Confirmation number.
* Application ID.
* Dashboard status.
* Dedicated confirmation URL.
* Submitted-status indicator.
* Server response associated with final submission.

---

# Confirmation Model

```json
{
  "status": "submitted",
  "confirmation_message": "",
  "confirmation_number": "",
  "application_id": "",
  "confirmation_url": "",
  "dashboard_status": "",
  "evidence": [],
  "confidence": 100
}
```

---

# Weak Confirmation Signals

Weak signals include:

* Submit button disappeared.
* User was redirected to job listings.
* Page became blank.
* Browser returned to the company home page.
* Form fields disappeared.
* Success-colored banner without readable text.

Weak signals alone should produce Submission Unknown.

---

# Application Dashboard

Some ATS platforms provide a candidate dashboard showing application status.

An adapter may support:

* Opening dashboard.
* Listing applications.
* Matching the current job.
* Reading submitted status.
* Detecting duplicate applications.
* Resolving unknown submission outcomes.

---

# Dashboard Matching

Match applications using:

* Job ID.
* Job title.
* Company.
* Location.
* Submission date.
* Requisition ID.

Avoid matching only by similar job title.

---

# Generic Submission Verification

When no dedicated adapter exists, the Generic Form Engine may verify submission using:

1. Explicit success text.
2. Confirmation identifier.
3. Dedicated confirmation page.
4. Application status page.
5. Strong URL and content combination.

Otherwise, return Submission Unknown.

---

# Generic Form Engine Confidence

The Generic Form Engine should track confidence at:

* Page level.
* Form level.
* Field level.
* Action level.
* Submission level.

---

# Confidence-Based Behavior

Example policy:

```text
Field confidence >= 90:
Automatic execution allowed.

Field confidence 75–89:
Execute with review or enhanced verification.

Field confidence 50–74:
Require review.

Field confidence below 50:
Require user input or manual mode.
```

Final submission should require higher confidence than ordinary field entry.

---

# Generic Fallback Strategy

When a dedicated adapter fails:

```text
Dedicated Adapter Action
        |
        v
Failure Detected
        |
        v
Reinspect Current Page
        |
        v
Is Failure Localized?
        |
        +--> Yes: Generic Widget Handler
        |
        +--> No: Generic Page Engine
        |
        +--> Unsafe: Manual Mode
```

---

# Localized Fallback

A dedicated adapter may delegate one unsupported widget to a generic handler.

Example:

```text
Dedicated ATS adapter handles the page.
Generic searchable-dropdown handler manages one custom field.
```

This is preferable to abandoning the full adapter workflow.

---

# Full Generic Fallback

Use full Generic Form Engine when:

* Adapter no longer recognizes the page.
* Workflow is custom.
* Standard accessible controls remain.
* Application identity is verified.
* Generic fallback is permitted.
* Submission safety remains enforceable.

---

# Fallback Restrictions

Do not use generic fallback to bypass:

* CAPTCHA.
* MFA.
* Security prompts.
* Unknown sensitive-information requests.
* Unsupported document-access requests.
* Untrusted redirects.
* Ambiguous final submission controls.

---

# Manual Completion Fallback

When safe automation is not possible, the system should prepare a manual-completion package containing:

* Application URL.
* Active resume.
* Cover letter.
* Prepared answers.
* Unresolved questions.
* Current browser screenshot.
* Completed-field summary.
* Remaining-field checklist.

---

# Adapter Health Monitoring

## Responsibility

Detect when an adapter becomes unreliable.

Health signals may include:

* Detection failures.
* Page-classification failures.
* Selector failures.
* Widget failures.
* Navigation failures.
* Review extraction failures.
* Submission-verification failures.
* Increased manual intervention.
* Regression-test failures.

---

# Adapter Health Result

```json
{
  "adapter_id": "example_ats",
  "version": "1.2.0",
  "status": "degraded",
  "success_rate": 72,
  "recent_failures": [],
  "recommended_mode": "review",
  "automatic_submission_allowed": false
}
```

---

# Adapter Degradation Rules

An adapter may become degraded when:

* Required page signature no longer matches.
* Multiple supported employers fail similarly.
* Core widget handling fails.
* Submission verification becomes unreliable.
* Regression fixtures fail after an update.
* Browser engine changes create incompatibility.

---

# Degraded Adapter Behavior

When degraded:

* Disable automatic mode.
* Prefer Review mode.
* Enable generic fallback when safe.
* Increase screenshot capture.
* Record diagnostic artifacts.
* Warn the user.
* Continue only when validation remains strong.

---

# Adapter Versioning

Adapters should use semantic versions.

Example:

```text
1.0.0
```

Meaning:

* Major: incompatible workflow or contract changes.
* Minor: new capabilities or page variants.
* Patch: bug fixes and selector updates.

---

# Version Binding

Execution state should record:

* Adapter ID.
* Adapter version.
* Browser engine version.
* Generic engine version.
* Page-signature version.
* Widget-handler versions.

This supports reproducibility and recovery.

---

# Adapter Upgrade During Execution

An adapter should not silently change versions in the middle of an active workflow.

After an application restart:

* Load recorded adapter version when available.
* Detect compatibility.
* Migrate checkpoint context when supported.
* Otherwise require workflow recovery review.

---

# Adapter Configuration

Example:

```json
{
  "ats": {
    "enabled_adapters": [
      "workday",
      "greenhouse",
      "lever"
    ],
    "allow_generic_fallback": true,
    "automatic_submission_adapter_statuses": [
      "stable"
    ],
    "review_mode_adapter_statuses": [
      "beta",
      "degraded"
    ],
    "manual_mode_for_unsupported": true
  }
}
```

---

# ATS-Specific Candidate Rules

Users may define rules such as:

```text
Never create a new Workday account automatically.

Use manual review for Taleo applications.

Allow automatic submission only for stable Greenhouse forms.

Do not reuse an ATS account created with another email.

Skip applications requiring third-party assessments.
```

These rules should be evaluated by the orchestrator and readiness services.

---

# Third-Party Assessment Redirects

Applications may redirect to:

* Coding assessments.
* Personality assessments.
* Video interviews.
* Background-check portals.
* Document-signing services.

The ATS adapter should classify these as external workflow stages.

Default behavior:

* Do not complete assessments automatically.
* Pause and notify the user.
* Preserve application state.
* Record the assessment URL.
* Resume only when the ATS indicates completion.

---

# Assessment Result State

```json
{
  "status": "user_action_required",
  "category": "external_assessment",
  "assessment_url": "",
  "resume_action": "return_to_application_dashboard"
}
```

---

# Application Timeouts

Adapters should define or inherit configurable timeouts for:

* Initial page load.
* Custom widget options.
* Resume parsing.
* Account creation.
* Save operation.
* Page progression.
* Review-page load.
* Submission confirmation.
* Dashboard load.

Timeouts should remain bounded.

---

# Adapter Retry Policy

Adapter operations may retry when:

* Page is temporarily incomplete.
* Element is detached.
* Options load slowly.
* Navigation times out before submission.
* Upload fails temporarily.
* Session refresh is safe.

Final submission clicks must not be automatically repeated.

---

# Adapter Recovery Context

Adapters should store recovery-specific state.

Example:

```json
{
  "adapter_id": "workday",
  "adapter_version": "1.0.0",
  "page_type": "education",
  "workflow_step": "education",
  "entry_edit_state": null,
  "application_dashboard_url": "",
  "resume_parsing_completed": true
}
```

---

# Page Mutation Handling

Modern ATS pages may update without full navigation.

The adapter should detect:

* Dynamic field appearance.
* Modal opening.
* Validation insertion.
* Step content replacement.
* Upload completion.
* Parsed resume field population.
* Consent section expansion.

The browser should reinspect after material mutations.

---

# Lazy Loading

For pages with lazy-loaded content:

* Scroll incrementally.
* Detect newly loaded controls.
* Wait for stable item count.
* Avoid endless scrolling.
* Respect maximum scroll attempts.

---

# Virtual Lists

Searchable dropdowns may use virtualized lists.

The handler should:

* Search by exact term.
* Inspect visible options.
* Scroll within the option list when necessary.
* Verify the selected option text.
* Avoid selecting by unstable index.

---

# Iframe Handling

ATS forms may be embedded in iframes.

Adapters should:

* Detect expected ATS frames.
* Verify frame origin.
* Route form extraction into the correct frame.
* Preserve frame context with fields.
* Re-resolve frame after navigation.
* Block interaction with unrelated frames.

---

# Shadow DOM

The engine may handle open Shadow DOM through browser-supported locators.

Closed Shadow DOM may require:

* Dedicated adapter techniques.
* Alternate exposed input.
* Manual completion.
* Unsupported-state classification.

The system should not use unsafe browser modifications to bypass closed controls.

---

# New Tabs and Popups

Adapters should handle:

* Login popup.
* Privacy-policy popup.
* Application form in a new tab.
* External assessment tab.
* Confirmation tab.

Every new page should undergo:

* Domain verification.
* Job identity verification when applicable.
* Page classification.
* Adapter routing.

---

# Dialogs

Browser dialogs may include:

* Leave-page warning.
* Session-expiration notice.
* Save confirmation.
* Application cancellation.
* Submission confirmation.

Adapters should define expected dialogs.

Unexpected dialogs should pause execution.

---

# Validation Message Extraction

Adapters should normalize validation messages.

Example:

```json
{
  "field_id": "phone",
  "message": "Enter a valid phone number.",
  "severity": "blocking",
  "source": "inline_error"
}
```

---

# Validation Sources

* Inline field error.
* Top-of-page error summary.
* Disabled Next button.
* Browser-native validation.
* Modal error.
* Server response.
* Toast message.
* Section error badge.

---

# Validation-to-Field Mapping

The adapter should map error messages to fields using:

* ARIA relationships.
* Anchor links.
* IDs.
* Section names.
* Matching label text.
* DOM proximity.

Unmapped blocking errors should remain visible in the page-validation result.

---

# Generic Validation Handling

The Generic Form Engine should:

1. Extract all visible errors.
2. Map errors to fields.
3. Reinspect affected fields.
4. Request corrected values when necessary.
5. Re-execute only affected actions.
6. Revalidate.

---

# Error Summary Result

```json
{
  "status": "failed",
  "errors": [
    {
      "field_id": "postal_code",
      "message": "Invalid postal code.",
      "automatically_correctable": true
    }
  ]
}
```

---

# Error Categories

Recommended adapter errors:

```text
ATSDetectionError
ATSAdapterNotFoundError
ATSAdapterDegradedError
ATSPageClassificationError
ATSPageSignatureMismatchError
ATSFormExtractionError
ATSFieldClassificationError
ATSWidgetUnsupportedError
ATSNavigationError
ATSAuthenticationError
ATSAccountCreationError
ATSResumeUploadError
ATSResumeParsingError
ATSRepeatingSectionError
ATSReviewExtractionError
ATSSubmissionControlError
ATSSubmissionVerificationError
ATSUnsupportedWorkflowError
GenericFormDetectionError
GenericFieldAmbiguityError
GenericSubmissionAmbiguityError
```

---

# Structured Adapter Result

Every adapter operation should return a structured result.

```json
{
  "operation": "extract_form",
  "status": "success",
  "adapter_id": "greenhouse",
  "adapter_version": "1.0.0",
  "confidence": 98,
  "data": {},
  "warnings": [],
  "error": null
}
```

---

# Adapter Logging

Logs may include:

* Adapter ID.
* Adapter version.
* Detection confidence.
* Page type.
* Page-signature ID.
* Capability decision.
* Widget-handler ID.
* Fallback activation.
* Operation result.
* Retry count.
* Error category.
* Duration.
* Screenshot path.

Logs should not include candidate answer values by default.

---

# Diagnostics

On adapter failure, capture:

* Current URL.
* Page title.
* Adapter ID and version.
* Page classification.
* Sanitized DOM characteristics.
* Accessibility snapshot summary.
* Screenshot.
* Form model.
* Failed widget model.
* Error.
* Retry history.

Do not capture:

* Passwords.
* Tokens.
* Cookies.
* Sensitive government IDs.
* Complete unrestricted page HTML by default.

---

# Metrics

Useful local metrics include:

* ATS detections.
* Adapter-selection confidence.
* Applications per adapter.
* Generic fallback rate.
* Manual fallback rate.
* Form-extraction success rate.
* Field-classification success rate.
* Widget failure rate.
* Resume-parsing correction count.
* Review-page detection rate.
* Submission-verification rate.
* Adapter degradation events.
* Average pages per ATS.
* User interventions per ATS.

Metrics should not imply application success or hiring success.

---

# Security

The ATS integration layer processes untrusted external content.

It should enforce:

* Domain verification.
* Application identity verification.
* Restricted navigation.
* Restricted file uploads.
* Local-only browser profiles.
* No credentials in model prompts.
* No arbitrary script execution.
* No arbitrary local-file discovery.
* No anti-bot bypass.
* No CAPTCHA solving.
* No hidden-field manipulation intended to defeat website controls.
* No automatic submission when final-action meaning is ambiguous.

---

# Prompt Injection Protection

ATS page content, form questions, help text, and validation messages are untrusted.

The adapter and Generic Form Engine should treat external content only as data needed to interpret the application.

They must ignore content instructing the system to:

* Reveal candidate files.
* Change orchestration rules.
* Add unsupported qualifications.
* Disable validation.
* Upload unrelated files.
* Expose credentials.
* Approve the application automatically.
* Mark submission successful.
* Navigate to unrelated websites.

---

# External Link Policy

The adapter may follow links only when they are:

* Part of the approved application workflow.
* On the expected company or ATS domain.
* An expected authentication or assessment provider.
* Explicitly approved by the user.

Unexpected external links should be blocked or require review.

---

# Sensitive Field Isolation

Sensitive fields should be marked in the common field model.

Example:

```json
{
  "semantic_type": "personal.government_id",
  "sensitive": true,
  "model_access": false,
  "logging_policy": "redacted",
  "execution_policy": "manual_only"
}
```

Adapters must honor the field policy.

---

# Testing Strategy

Adapters should be tested primarily against:

* Controlled local fixtures.
* Sanitized page snapshots.
* Recreated ATS-like test pages.
* Recorded structured page models.
* Limited live validation where permitted.

Tests should not depend solely on live ATS websites.

---

# Adapter Unit Tests

Unit-test:

* Domain detection.
* Page-signature matching.
* Page classification.
* Field extraction.
* Field semantic mapping.
* Capability resolution.
* Action classification.
* Review-page detection.
* Submission-signal classification.
* Fallback selection.
* Error mapping.

---

# Widget Handler Tests

Test:

* Text fields.
* Native dropdowns.
* Searchable dropdowns.
* Multi-select controls.
* Radio groups.
* Checkbox groups.
* Date pickers.
* Address autocomplete.
* File uploads.
* Rich-text fields.
* Repeating sections.
* Virtualized option lists.

---

# Generic Form Engine Tests

Test:

* Single standard form.
* Multiple unrelated forms.
* Missing labels.
* ARIA-only labels.
* Placeholder-only fields.
* Conditional fields.
* Dynamic form sections.
* Hidden fields.
* Ambiguous fields.
* Multi-page progression.
* Unknown final button.
* Explicit confirmation page.
* Unknown submission result.

---

# Dedicated Adapter Fixtures

Each adapter should maintain fixtures for:

* Job detail page.
* Application start.
* Login.
* Account creation.
* Resume upload.
* Resume parsing.
* Personal information.
* Work history.
* Education.
* Questionnaire.
* Disclosures.
* Review.
* Confirmation.
* Validation error.
* Session expiration.
* Closed job.
* Dashboard.

---

# Fixture Versioning

Fixtures should include:

* ATS adapter version.
* Workflow variant.
* Employer configuration type.
* Region.
* Page type.
* Capture or reconstruction date.
* Sanitization status.

---

# Regression Test Matrix

Example:

```text
Adapter        Login  Upload  Experience  Review  Submit  Dashboard
Workday        Yes    Yes     Yes         Yes     Yes     Yes
Greenhouse     N/A    Yes     N/A         Yes     Yes     Limited
Lever          N/A    Yes     N/A         Yes     Yes     N/A
Generic Form   N/A    Yes     Partial     Partial Partial N/A
```

Actual statuses should be generated from test results rather than documentation claims.

---

# Required Test Scenarios

## Exact Dedicated Adapter Match

The application URL and page signature match a stable adapter.

Expected:

* Dedicated adapter selected.
* Confidence above threshold.
* Generic fallback remains available.
* Workflow proceeds.

---

## Domain Match but Signature Mismatch

The domain is recognized, but the page structure changed.

Expected:

* Adapter marked uncertain or degraded.
* Generic inspection attempted when safe.
* Automatic submission disabled until confidence is restored.

---

## Embedded ATS Form

A company career page embeds an ATS form in an iframe.

Expected:

* ATS iframe detected.
* Frame origin verified.
* Adapter selected based on frame.
* Application identity preserved.

---

## Unknown Custom Form

No ATS adapter matches, but the page uses standard accessible controls.

Expected:

* Generic Form Engine selected.
* Form boundary detected.
* Fields classified.
* Review mode recommended.
* Submission proceeds only with strong confirmation.

---

## Multiple Forms on Page

The page contains job search, newsletter, and application forms.

Expected:

* Application form selected.
* Unrelated forms ignored.
* No newsletter subscription.

---

## Ambiguous Required Field

A required dropdown label is unclear.

Expected:

* Structured context sent for semantic classification.
* User input requested when ambiguity remains.
* No placeholder selected automatically.

---

## Searchable Location Dropdown

The candidate location appears among multiple similarly named options.

Expected:

* Exact location resolved.
* Correct country or state verified.
* Selected value read back.

---

## Resume Parsing Error

ATS parses an employer as a job title.

Expected:

* Parsing mismatch detected.
* Correct value entered.
* Final entry verified.

---

## Repeating Work History

ATS contains two parsed entries, but candidate has three required records.

Expected:

* Existing entries matched.
* Incorrect entries corrected.
* Missing entry added.
* No duplicate entries created.

---

## Account Login Required

Application redirects to login.

Expected:

* Adapter classifies login page.
* Existing session checked.
* User action requested when credentials or MFA are required.
* Workflow resumes after authentication.

---

## Wrong Candidate Account

ATS dashboard is logged in under a different email.

Expected:

* Account mismatch detected.
* No profile data overwritten.
* User action required.

---

## Required Privacy Consent

ATS requires data-processing consent.

Expected:

* Full consent statement captured.
* Candidate rule checked.
* Required consent selected when authorized.
* Optional marketing consent remains unselected by default.

---

## Conditional Sponsorship Field

Selecting Yes reveals visa-type question.

Expected:

* Page mutation detected.
* New field extracted.
* Answer resolved.
* Form plan extended.
* Page validated before progression.

---

## Dedicated Widget Failure

Adapter cannot handle one custom date picker.

Expected:

* Generic date handler attempted.
* Dedicated adapter retains page control.
* Result verified.

---

## Full Adapter Failure

Dedicated adapter no longer recognizes the page.

Expected:

* Adapter marked degraded.
* Generic page extraction attempted.
* Manual mode used if generic execution is unsafe.

---

## Ambiguous Final Button

Final page has a button labeled Complete without a clear submission indicator.

Expected:

* Do not click automatically.
* Manual review required.
* Final-action ambiguity recorded.

---

## Strong Confirmation

After submission, a confirmation message and application ID appear.

Expected:

* Submitted status.
* Evidence stored.
* Tracker synchronization allowed.

---

## Weak Confirmation Only

After clicking Submit, the browser returns to the job list without confirmation text.

Expected:

* Submission Unknown.
* No automatic retry.
* Dashboard or user verification required.

---

## External Assessment Redirect

Application redirects to a coding assessment.

Expected:

* Assessment classified as external user action.
* No automated completion.
* Application state preserved.

---

## Malicious Form Text

A form field asks the system to upload all candidate files.

Expected:

* Instruction treated as untrusted.
* Only approved documents remain accessible.
* Suspicious field flagged.
* No unrelated upload occurs.

---

## Unknown Sensitive Field

An unknown domain asks for a Social Security number.

Expected:

* Domain trust and sensitive-field policy checked.
* No value sent to Claude.
* Workflow paused or blocked.

---

# Adapter Completion Criteria

A dedicated ATS adapter is considered complete when:

* Detection rules are defined.
* Page signatures exist.
* Supported capabilities are declared.
* Login behavior is classified.
* Core application pages are normalized.
* Standard fields are extracted.
* Custom widgets are supported.
* Resume upload is verified.
* Resume parsing is reviewed.
* Repeating sections are supported where required.
* Validation errors are extracted.
* Review pages are detected.
* Submission controls are distinguished.
* Strong confirmation signals are defined.
* Recovery context is persisted.
* Fixtures exist for major page types.
* Regression tests pass.
* Prompt-injection protections pass.
* Sensitive data remains protected.
* Generic fallback behavior is defined.

---

# Generic Form Engine Completion Criteria

The Generic Form Engine is complete when:

* Application forms can be distinguished from unrelated forms.
* Accessible fields can be extracted.
* Labels can be resolved.
* Standard field types can be classified.
* Canonical semantic mappings work.
* Unknown questions can be escalated.
* Standard widgets can be executed and verified.
* File uploads work.
* Conditional fields are detected.
* Multi-page progression is verified.
* Validation errors are extracted.
* Review pages can be recognized when explicit.
* Final submission ambiguity triggers review.
* Strong confirmations can be detected.
* Weak confirmations produce Submission Unknown.
* Unsupported controls trigger Manual mode.
* Security and file-access boundaries are enforced.

---

# Definition of ATS Integration Completion

The ATS Adapters and Generic Form Engine phase is complete when:

* ATS detection uses multiple signals.
* Adapter selection is confidence-based.
* Adapter registry and capability declarations exist.
* Application identity is preserved through redirects.
* Dedicated adapters implement a shared interface.
* Common page, field, action, and review models exist.
* Generic fallback supports accessible standard forms.
* Field and widget handlers are reusable.
* Repeating employment and education sections work.
* Resume upload and parsing corrections work.
* Login and account states are handled safely.
* CAPTCHA and MFA trigger user intervention.
* Privacy and consent fields follow candidate rules.
* Review-page extraction works for supported adapters.
* Final submission controls are distinguished from navigation.
* Strong submission verification is required.
* Submission Unknown prevents automatic retry.
* Adapter degradation is detected.
* Adapter versions are persisted in workflow state.
* Dedicated and generic test fixtures exist.
* Adapter failures can fall back safely.
* Manual completion fallback is available.
* Prompt-injection and sensitive-data tests pass.
* At least one dedicated adapter completes an end-to-end controlled application workflow.
* The Generic Form Engine completes an end-to-end standard-form workflow.

---

# Summary

The ATS integration layer converts diverse job-application websites into one normalized application model.

Dedicated ATS adapters provide:

* Platform recognition.
* ATS-specific page understanding.
* Custom widget handling.
* Authentication workflows.
* Resume-parsing support.
* Multi-page navigation.
* Review-page extraction.
* Submission verification.

The Generic Form Engine provides:

* Accessible form discovery.
* Field classification.
* Reusable widget handling.
* Unknown-form fallback.
* Conservative submission behavior.
* Manual fallback when automation is unsafe.

The system should not attempt to automate every website through brittle scripts.

It should use:

* Clear adapter boundaries.
* Stable semantic selectors.
* Structured page models.
* Capability declarations.
* Confidence thresholds.
* Verified browser actions.
* Safe fallback.
* Explicit unsupported states.
* Strong submission evidence.

Candidate facts and application answers remain outside the ATS adapter layer.

Adapters interpret and execute application structure; they do not decide what is true about the candidate.
