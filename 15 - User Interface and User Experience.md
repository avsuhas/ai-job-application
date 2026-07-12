# 15 - User Interface and User Experience

## LLM-Powered Autonomous Job Search & Application Platform

Version: 1.0

---

# Purpose

This document defines the user interface and user experience requirements for the LLM-Powered Autonomous Job Search and Application Platform.

The interface should allow a user to:

* Configure their candidate profile.
* Add job sources and company career pages.
* Discover and review jobs.
* Understand job-match results.
* Select jobs for preparation.
* Inspect prepared resumes, cover letters, and application answers.
* Review application readiness.
* Create and manage an application queue.
* Observe browser execution.
* Respond to login, CAPTCHA, MFA, and missing-information requests.
* Review applications before submission when configured.
* Confirm submission results.
* Track application history.
* Inspect errors, audit trails, and operational health.
* Control privacy, automation, and retention settings.
* Safely recover interrupted workflows.

The interface should make a complex automation system understandable without exposing unnecessary internal complexity.

The platform may use sophisticated reasoning, browser automation, ATS adapters, package state machines, and review services internally.

The user experience should present these capabilities through clear actions, explicit statuses, actionable explanations, and safe defaults.

---

# Core Principle

The user should always be able to answer:

```text
What is happening?

Why is it happening?

What information is being used?

What action will happen next?

Is my input required?

Has anything irreversible happened?

Was the application actually submitted?
```

The interface should never obscure uncertainty or imply completion without evidence.

---

# UX Objectives

The user interface should:

* Make job discovery and application progress easy to understand.
* Separate preparation from submission.
* Clearly distinguish automatic, review, and manual modes.
* Show the active candidate profile.
* Show which resume and answer set will be used.
* Explain why a job is recommended or skipped.
* Explain why an application is blocked.
* Minimize unnecessary user intervention.
* Request user input only when required.
* Preserve context when user intervention is needed.
* Clearly identify irreversible actions.
* Protect sensitive information from casual exposure.
* Make Submission Unknown visually distinct from Failed or Submitted.
* Support keyboard and screen-reader navigation.
* Remain usable on normal desktop and laptop displays.
* Provide recovery paths after errors.
* Avoid overwhelming the user with technical logs.
* Keep advanced operational details available when needed.

---

# UX Principles

The platform should follow these principles.

---

## Show State, Not Assumptions

Display actual workflow state.

Preferred:

```text
Waiting for CAPTCHA completion
```

Avoid:

```text
Still working
```

---

## Distinguish Preparation from Submission

Preparing documents does not mean an application was submitted.

The interface should use distinct states and actions for:

* Prepared.
* Ready.
* Queued.
* In Progress.
* Ready for Review.
* Submitting.
* Submitted.
* Submission Unknown.

---

## Make Irreversible Actions Explicit

The final submission action should be visually and semantically distinct.

The interface should clearly identify:

* Whether automatic submission is enabled.
* Whether user approval is required.
* Whether Submit has been clicked.
* Whether submission has been verified.

---

## Explain Blocking Conditions

A blocked package should display:

* What is blocking it.
* Why the condition matters.
* Whether the system can fix it.
* What the user needs to do.
* What happens after resolution.

---

## Use Progressive Disclosure

The default view should show:

* Current status.
* Key warnings.
* Required actions.
* Main artifacts.
* Next step.

Advanced views may show:

* Detailed validation results.
* Source references.
* adapter diagnostics.
* workflow traces.
* logs.
* audit events.

---

## Minimize Sensitive Exposure

Sensitive information should be:

* Hidden by default.
* revealed only on user action.
* excluded from general dashboards.
* redacted in screenshots and logs when practical.
* grouped into protected sections.

---

## Preserve User Control

The user should be able to:

* Pause automation.
* switch to Review mode.
* switch to Manual mode.
* skip an application.
* cancel pending applications.
* correct answers.
* replace documents.
* approve or reject changes.
* inspect submission evidence.
* delete local data.

---

## Prefer Safe Failure

When the system cannot continue safely, the interface should stop and explain the situation rather than continue with guesses.

---

# Primary User

The initial platform is designed for:

```text
One candidate
One local installation
One primary browser profile
One or more application queues
```

Future multi-user or enterprise experiences are outside the MVP scope.

---

# User Roles

The MVP may use one user role:

```text
Local Candidate
```

This user may:

* Manage candidate data.
* manage jobs.
* prepare packages.
* control queues.
* review applications.
* approve submissions.
* view history.
* manage configuration.
* manage privacy and security.

A future version may distinguish administrator, candidate, or reviewer roles.

---

# Interface Surfaces

The platform may expose:

* A local web interface.
* Visible Playwright-controlled browser windows.
* System notifications.
* Local file exports.
* Optional command-line maintenance tools.

The local web interface should be the primary user-facing surface.

---

# Information Architecture

Recommended primary navigation:

```text
Dashboard
Jobs
Applications
Queue
History
Candidate Profile
Settings
System Health
```

A compact navigation may group items as:

```text
Home
Jobs
Applications
History
Settings
```

with Queue, Candidate Profile, and Health available through subnavigation.

---

# Main Navigation Requirements

The primary navigation should:

* Remain visible on desktop.
* Show the active section.
* display pending-action badges.
* display queue activity.
* display critical alerts.
* support keyboard navigation.
* avoid showing sensitive details.

---

# Global Header

The global header may include:

* Application name.
* Active candidate profile.
* Global search.
* Queue status.
* User-action notification count.
* System health indicator.
* Settings access.

---

# Global Status Indicators

Recommended indicators:

```text
Queue running
Queue paused
User action required
Submission Unknown
System degraded
Offline
Safe mode
Maintenance mode
```

Indicators should include text or accessible labels, not color alone.

---

# Global Actions

Possible global actions:

```text
Add jobs
Run discovery
Prepare selected jobs
Start queue
Pause queue
Run health check
Create backup
```

Actions should appear only when relevant.

---

# Page Layout

Desktop pages should generally use:

```text
Page Header
Summary or Status Area
Primary Content
Contextual Action Panel
Optional Details Panel
```

The most important action should be easy to identify.

---

# Responsive Design

The local UI should primarily target desktop and laptop use.

Minimum supported layout:

```text
1280 x 720
```

The UI should remain usable at narrower widths, but complex review and queue workflows may use stacked panels.

Mobile support is optional for the MVP.

---

# Visual Hierarchy

Use visual hierarchy to distinguish:

* Page title.
* application status.
* blocking issue.
* warning.
* primary action.
* secondary action.
* technical detail.

Critical warnings should not be visually confused with informational messages.

---

# Status Design

Every major entity should have a visible status.

Entities include:

* Job.
* Application Package.
* Queue item.
* Workflow.
* Browser session.
* Review.
* Readiness.
* Submission.
* History synchronization.
* System component.

---

# Common Status Presentation

Each status should include:

* Status label.
* concise explanation.
* timestamp when useful.
* next allowed action.
* related warnings.

Example:

```text
Ready for Review

The application form is complete and has passed automated validation.
Review the final answers before submission.
```

---

# Status Color Guidance

Color may support status but must not be the only signal.

Suggested semantic categories:

* Neutral: Draft, Pending, Not Started.
* Informational: Preparing, In Progress.
* Positive: Ready, Approved, Submitted.
* Warning: Ready with Warnings, Waiting for User.
* Critical: Blocked, Failed, Security Alert.
* Uncertain: Submission Unknown.

Submission Unknown should have its own icon and wording rather than reuse the normal error style.

---

# Status Icons

Possible semantic icons:

```text
Check:
Passed or Submitted

Clock:
Pending or Waiting

Pause:
Paused

Person:
User action required

Shield:
Security or privacy

Warning triangle:
Warning

Stop:
Blocked

Question mark:
Unknown outcome

Refresh:
Refresh required
```

Icons must have accessible labels.

---

# Dashboard

## Purpose

The Dashboard provides an overview of current job-search activity and directs attention to items requiring action.

---

# Dashboard Sections

Recommended sections:

* Current Queue.
* Required Actions.
* Recent Applications.
* Job Discovery Summary.
* Application Pipeline.
* System Health.
* Recent Alerts.
* Suggested Next Action.

---

# Dashboard Summary Cards

Possible summary cards:

```text
Jobs discovered
Jobs selected
Applications prepared
Ready to apply
Submitted this week
Waiting for action
Submission Unknown
```

Clicking a card should open the corresponding filtered view.

---

# Current Queue Card

Display:

* Queue status.
* Current company and role.
* Current stage.
* Overall progress.
* Pause or resume action.
* Number remaining.
* Number completed.
* Number requiring attention.

---

# Required Actions

Show highest-priority actions first.

Priority order:

1. Submission Unknown.
2. Security or privacy alert.
3. CAPTCHA or MFA.
4. Missing required legal or factual answer.
5. Manual review ready.
6. Failed history synchronization.
7. Stale package requiring refresh.
8. Optional warnings.

---

# Required Action Card

Each card should display:

* Company.
* Role.
* Action category.
* concise explanation.
* time created.
* primary action.
* safe secondary action.

Example:

```text
Microsoft — Senior Backend Engineer

A required conflict-of-interest question has no saved answer.

[Answer Question] [Skip Application]
```

---

# Application Pipeline

A pipeline view may group applications into:

```text
Selected
Preparing
Ready
Queued
In Progress
Review
Submitted
Needs Attention
Closed
```

Counts should be clickable filters.

---

# Recent Activity

Show user-relevant events, not raw logs.

Examples:

```text
Resume prepared for Google.
Application review completed for Microsoft.
Submission verified for Stripe.
CAPTCHA required for Amazon.
```

---

# System Health Summary

Display:

* Overall status.
* browser status.
* provider status.
* history status.
* disk status.
* outstanding critical issues.

A detailed Health page should be available.

---

# First-Time Onboarding

## Purpose

Guide the user through minimum setup without requiring advanced configuration.

---

# Onboarding Steps

Recommended sequence:

```text
Welcome
Candidate Profile
Resume and Career Data
Application Preferences
Work Authorization
Sensitive Answer Preferences
Reasoning Provider
Browser Setup
History and Storage
Safety Review
Synthetic Test
Complete
```

---

# Onboarding Progress

Display:

* Current step.
* completed steps.
* remaining steps.
* ability to save and resume.
* ability to revisit prior steps.

Do not force the user to complete optional advanced settings.

---

# Welcome Screen

Explain:

* What the platform does.
* what remains local.
* when candidate data may be sent to the reasoning provider.
* that browser automation may submit applications.
* that CAPTCHA and MFA require manual action.
* that automatic submission can remain disabled.

Primary actions:

```text
Start setup
Use safe defaults
Import existing profile
```

---

# Candidate Profile Setup

Collect:

* Legal name.
* preferred name.
* email.
* phone.
* location.
* country.
* optional address.

Sensitive fields should explain why they may be needed.

---

# Resume and Career Data Setup

Allow:

* Upload resume.
* add additional resume versions.
* review extracted employment.
* review extracted education.
* correct parsing.
* add skills.
* add certifications.
* select default resume.

The system should not silently accept extracted information as authoritative.

---

# Candidate Data Review

After import, show a structured review:

```text
Personal Information
Employment
Education
Skills
Certifications
```

Highlight:

* Missing fields.
* conflicting fields.
* low-confidence parsing.
* dates requiring confirmation.

---

# Application Preference Setup

Collect:

* Target roles.
* target countries.
* target locations.
* remote preference.
* salary preferences.
* employment types.
* relocation preference.
* travel preference.
* notice period.
* job exclusions.

---

# Work Authorization Setup

This step should separately ask:

* Authorized to work in target country now.
* Requires sponsorship now.
* May require sponsorship in the future.
* Current status.
* transfer or petition requirements when applicable.

The UI should explain that these questions are distinct.

---

# Work Authorization Confirmation

Show a summary such as:

```text
Authorized to work in the United States now: Yes
Requires employer sponsorship now: No
May require sponsorship in the future: Yes
```

Require confirmation before saving.

---

# Sensitive Answer Preferences

Configure:

* Demographic response policy.
* disability response policy.
* veteran-status response policy.
* salary-history policy.
* legal-question handling.
* government-ID policy.
* automatic attestation policy.

Values should be hidden by default after setup.

---

# Provider Setup

Allow the user to:

* Select provider.
* select model.
* add secret reference.
* test connection.
* choose fallback model.
* configure cost limits.
* review privacy policy.

Do not display the API key after entry.

---

# Browser Setup

Guide the user through:

* Browser installation check.
* creation of dedicated browser profile.
* launch test.
* visible browser confirmation.
* optional ATS login.
* profile identity check.

---

# Synthetic Test

Before real use, run a controlled synthetic workflow.

Test:

* Candidate profile loading.
* provider request.
* document generation.
* browser form filling.
* review.
* simulated submission.
* history update.

Show a clear pass or failure report.

---

# Onboarding Completion

Display:

* Setup summary.
* automation mode.
* active browser profile.
* provider status.
* history location.
* security settings.
* next recommended action.

Primary action:

```text
Add job sources
```

---

# Jobs Section

## Purpose

Discover, review, filter, rank, and select jobs.

---

# Jobs Page Views

Possible views:

```text
Discovered
Recommended
Selected
Skipped
Closed
All Jobs
```

---

# Job Discovery Controls

Allow users to:

* Add company career URL.
* add direct job URL.
* add a company list.
* run discovery.
* rerun discovery.
* select target country.
* set posting-age filter.
* import job links.
* stop discovery.

---

# Discovery Source Card

Display:

* Source name.
* source URL.
* source type.
* country scope.
* last checked.
* jobs found.
* health status.
* next action.

---

# Job List

Recommended columns or card fields:

* Select checkbox.
* company.
* job title.
* location.
* date posted.
* match score.
* recommendation.
* salary when known.
* work-authorization note.
* source.
* status.

---

# Job List Controls

Support:

* Sort.
* filter.
* search.
* group.
* multi-select.
* pagination or virtual scrolling.
* saved filters.
* export.

---

# Recommended Filters

```text
Country
Location
Remote status
Company
Job family
Seniority
Match score
Date posted
Salary
Employment type
Sponsorship compatibility
Application status
Source
```

---

# Match Score Display

Show:

* Overall score.
* recommendation category.
* confidence.
* major strengths.
* major gaps.
* hard-rule status.

Avoid showing a score without explanation.

---

# Job Match Categories

Recommended labels:

```text
Strong Match
Good Match
Possible Match
Low Match
Skip
Blocked by Rule
```

---

# Match Explanation

A job detail page should explain:

```text
Matched:
Distributed systems
Python
REST APIs
Cloud infrastructure

Gaps:
No direct Kafka experience
Preferred Kubernetes experience not explicit

Rules:
Location accepted
Salary range accepted
Future sponsorship compatibility unknown
```

---

# Job Detail Page

Display:

* Company.
* job title.
* location.
* country.
* remote status.
* date posted.
* job ID.
* source URL.
* application URL.
* salary.
* employment type.
* job description.
* match score.
* requirement analysis.
* candidate-rule result.
* duplicate status.
* preparation status.

---

# Job Detail Actions

Possible actions:

```text
Select for Preparation
Prepare Now
Skip
Open Original Job
Add Note
Change Priority
Mark Closed
Refresh Job
```

---

# Job Description Safety

External job content should be visually marked as:

```text
Content from employer website
```

The UI need not alarm the user, but advanced details may show that external content is treated as untrusted.

---

# Duplicate Job Warning

When a similar application exists, display:

* Matched prior job.
* job ID.
* date applied.
* location.
* duplicate confidence.
* reason for match.
* override action when allowed.

---

# Job Selection

Users should be able to:

* Select individual jobs.
* select all visible jobs.
* select top N.
* select by score.
* select by company.
* clear selection.
* reorder selected jobs.

---

# Bulk Preparation Action

Before preparing multiple jobs, show:

* Number selected.
* expected resume generation count.
* expected cover letters.
* likely missing information.
* automation mode.
* estimated provider usage category.
* duplicate exclusions.

Do not promise execution duration.

---

# Applications Section

## Purpose

Manage Application Packages from preparation through completion.

---

# Application Views

Recommended tabs:

```text
All
Preparing
Ready
Queued
In Progress
Review
Needs Attention
Submitted
Failed
Archived
```

---

# Application List

Display:

* Company.
* role.
* package status.
* current stage.
* match score.
* automation mode.
* active resume.
* last updated.
* next action.

---

# Application Package Card

Example:

```text
Google
Senior Software Engineer

Status: Ready for Browser Execution
Match: 91
Resume: Google_Backend_Resume.pdf
Cover Letter: Not Required
Warnings: 1
```

Actions:

```text
Open Package
Queue
Review
Refresh
Skip
```

---

# Package Detail Page

Recommended sections:

```text
Overview
Job
Resume
Cover Letter
Answers
Review
Readiness
Execution
Submission
History
Audit
```

---

# Package Overview

Display:

* Company.
* job title.
* job identity.
* package status.
* current workflow stage.
* match score.
* automation mode.
* candidate profile.
* active artifact versions.
* warnings.
* blocking issues.
* next action.

---

# Package Timeline

Show major lifecycle events:

```text
Job selected
Package created
Resume prepared
Answers prepared
Readiness passed
Queued
Browser execution started
Review completed
Submitted
```

---

# Resume Tab

Display:

* Active resume preview.
* filename.
* version.
* generation source.
* validation result.
* change summary.
* factual findings.
* page count.
* file type.
* download or open action.
* replace action.
* restore prior version.

---

# Resume Change Review

Show changes grouped as:

```text
Added emphasis
Removed or reduced emphasis
Reordered skills
Rewritten bullets
Formatting changes
```

Do not describe supported rewording as newly acquired experience.

---

# Resume Validation Panel

Show:

* Candidate-name validation.
* employer and date validation.
* unsupported-claim check.
* job-identity check.
* layout validation.
* upload readiness.

---

# Resume Version History

Allow:

* Preview prior version.
* compare versions.
* activate prior version.
* delete unsubmitted draft version.
* retain submitted version permanently unless user deletes the package.

---

# Cover Letter Tab

Display:

* Requirement status.
* active document.
* preview.
* company and role validation.
* source references.
* length.
* version history.
* replace or regenerate actions.

---

# Application Answers Tab

Display answers grouped by category:

```text
Personal Information
Employment
Education
Work Authorization
Salary and Availability
Legal
Demographic
Narrative
Other
```

---

# Answer Row

Each answer row may show:

* Question.
* normalized category.
* answer preview.
* source.
* confidence.
* status.
* edit action.

Sensitive answers should display:

```text
Stored answer available
```

with a Reveal action.

---

# Answer Statuses

```text
Resolved
Resolved with Review
Missing
Ambiguous
Optional and Blank
Declined
Manual Only
Blocked by Policy
```

---

# Answer Editing

When editing:

* Show original application question.
* show available options.
* show current answer.
* show source.
* show related answers.
* show whether change may be saved for reuse.
* explain affected packages.

---

# Save Answer for Reuse

After a user edits an answer, offer:

```text
Use only for this application
Save for this company
Save for similar questions
Save as global standard answer
```

Changes to trusted candidate sources should require explicit approval.

---

# Sensitive Answer Editing

Sensitive-answer screens should:

* Hide value until revealed.
* use clear privacy warning.
* avoid retaining value in browser autocomplete.
* avoid copying into logs.
* explain where it will be used.
* allow Manual Only policy.

---

# Review Tab

Display the latest Application Review result.

Summary:

* Status.
* reviewed stage.
* blocking findings.
* warnings.
* corrections applied.
* approval state.
* artifact versions reviewed.

---

# Review Finding Card

Display:

* Severity.
* category.
* affected artifact.
* explanation.
* evidence summary.
* recommended action.
* automatic correction status.

---

# Review Actions

Possible actions:

```text
Apply Safe Corrections
Edit Answer
Replace Document
Rerun Review
Approve with Warnings
Return to Preparation
Block Application
```

---

# Readiness Tab

Display stage-specific readiness.

Sections:

```text
Package Integrity
Candidate Data
Documents
Answers
Browser
ATS Adapter
Review Approval
Duplicate Check
Submission Safety
```

---

# Readiness Check Row

Show:

* Check name.
* status.
* requirement type.
* explanation.
* evidence.
* fix action.

---

# Next Allowed Action

The Readiness page should prominently display:

```text
Next allowed action: Queue Application
```

or:

```text
Next allowed action: Provide Missing Information
```

---

# Refresh Required Experience

When a package is stale, show:

* What changed.
* which artifacts are affected.
* what will be regenerated.
* which user edits will be preserved.
* whether approval will be invalidated.

---

# Execution Tab

Display:

* Queue.
* workflow status.
* browser profile.
* ATS adapter.
* current page.
* completed pages.
* current stage.
* interventions.
* retries.
* screenshots.
* recovery state.

---

# Submission Tab

Display:

* Submission readiness.
* submission attempt.
* final-click status.
* verification status.
* confirmation evidence.
* confirmation number.
* ATS application ID.
* date submitted.
* history-sync status.

---

# Submission Evidence View

Show:

* Confirmation message.
* confirmation screenshot.
* confirmation URL.
* dashboard status.
* evidence strength.
* verification source.

---

# Audit Tab

The Audit tab should show a user-friendly event timeline.

Advanced details may include:

* Event IDs.
* artifact versions.
* actors.
* source references.
* integrity status.

Raw technical events should be hidden behind an Advanced toggle.

---

# Preparation Workflow

## Purpose

Guide the user from selected job to prepared package.

---

# Preparation Progress

Display stages:

```text
Analyzing Job
Selecting Resume
Tailoring Resume
Preparing Cover Letter
Preparing Answers
Running Review
Checking Readiness
```

---

# Preparation State

Each stage may show:

```text
Pending
Running
Complete
Warning
Needs Input
Failed
```

---

# Preparation Results Screen

When complete, show:

* Package readiness.
* active resume.
* cover-letter status.
* answer completeness.
* warnings.
* user input required.
* primary next action.

Example:

```text
Application package prepared

Resume: Ready
Cover Letter: Not Required
Answers: 14 of 14 required questions resolved
Readiness: Ready with 1 warning
```

---

# Preparation Failure

Display:

* Failed stage.
* impact.
* whether prior artifacts remain valid.
* safe retry action.
* Manual mode option.
* diagnostic reference.

---

# Application Queue

## Purpose

Manage ordered execution of multiple Application Packages.

---

# Queue Page Layout

Recommended areas:

```text
Queue Header
Current Application
Queue Items
Required Actions
Completed Results
Queue Controls
```

---

# Queue Header

Display:

* Queue name or ID.
* queue status.
* total items.
* current position.
* completed count.
* waiting count.
* failed count.
* automation mode.
* browser profile.

---

# Queue Controls

```text
Start
Pause
Resume
Cancel Queue
Skip Current
Reorder Pending
Add Applications
```

Potentially destructive controls should require confirmation.

---

# Current Application Panel

Display:

* Company and role.
* current workflow stage.
* current browser page.
* page progress.
* active resume.
* ATS.
* browser status.
* latest progress message.
* required action.

---

# Queue Item Row

Show:

* Position.
* company.
* role.
* status.
* match score.
* automation mode.
* warnings.
* next action.

---

# Queue Reordering

Allow dragging or keyboard-based reorder for pending items.

Do not allow reordering:

* Current executing item.
* submitted items.
* blocked terminal items.

---

# Queue Skip-Ahead

When a package requires user action, show whether the queue can continue.

Example:

```text
This application is waiting for a legal answer.

The current browser session cannot be safely reused until this page is resolved.

[Answer Now] [Pause Queue] [Switch to Manual Mode]
```

---

# Queue Completion Summary

Display:

```text
Selected: 10
Submitted: 6
Already Applied: 1
Waiting for User: 1
Blocked: 1
Failed: 1
```

Provide links to each filtered group.

---

# Browser Execution Experience

## Purpose

Allow the user to understand and intervene in visible browser automation.

---

# Browser Window Relationship

The local UI should make clear that:

* A separate browser window is controlled by the platform.
* The user may be asked to interact with it.
* Closing it may interrupt execution.
* Manual interaction should be limited to requested steps during automatic execution.

---

# Browser Status Panel

Display:

* Running.
* paused.
* waiting for login.
* waiting for CAPTCHA.
* recovering.
* crashed.
* closed.

---

# Browser Progress Messages

Examples:

```text
Opening the application.
Uploading the approved resume.
Completing work history.
Reviewing ATS-parsed employment data.
Waiting for the next page.
```

Do not expose sensitive values.

---

# Browser Action Visibility

The interface may display high-level actions.

Avoid exposing:

* Low-level selectors.
* full DOM.
* cookies.
* detailed technical retries.

Advanced diagnostics may show these in sanitized form.

---

# User Interaction Boundary

When user action is needed:

1. Browser automation pauses.
2. Local UI displays clear instructions.
3. Browser window remains visible.
4. User completes the action.
5. User returns to the local UI or the system detects completion.
6. Workflow reinspects the page.
7. Execution resumes.

---

# CAPTCHA Experience

Display:

```text
Verification required

Complete the CAPTCHA in the application browser.
The platform will not attempt to bypass it.

[Open Browser] [I Completed It] [Cancel Application]
```

The system may detect completion automatically but should still provide a manual Resume action.

---

# MFA Experience

Display:

* Which ATS or account is requesting verification.
* generic instruction to complete the verification.
* no request to paste security codes into the local UI unless explicitly designed and secured.
* Resume action.

---

# Login Required

Display:

```text
Sign in required

The application has opened the employer's ATS login page.
Sign in using the correct candidate account, then continue.
```

Show masked expected account identity where available.

---

# Wrong Account Warning

Display prominently:

```text
Different candidate account detected

The ATS session appears to be signed in with:
a***@example.com

Expected candidate:
s***@gmail.com

No application data has been changed.
```

Actions:

```text
Switch Account
Choose Another Browser Profile
Cancel Application
```

---

# Missing Information Experience

Display:

* Complete application question.
* why it cannot be answered.
* available options.
* related candidate information.
* whether answer is sensitive.
* reuse options.

---

# Ambiguous Question Experience

Explain:

```text
This question combines current work authorization and future sponsorship.
The available Yes/No options do not clearly map to your stored answers.
```

Require user selection.

---

# External Assessment Experience

Display:

```text
External assessment required

The employer has opened a coding or candidate assessment.
The platform will not complete this assessment automatically.

[Open Assessment] [Mark Complete] [Return Later] [Skip Application]
```

---

# Application Review Experience

## Purpose

Allow the user to inspect the final application before submission when Review mode is enabled.

---

# Review Page Layout

Recommended two-column layout:

```text
Application Summary
Final Answers and Documents

Review Findings
Approval Actions
```

At narrow widths, stack sections.

---

# Review Header

Display:

* Company.
* role.
* job ID.
* ATS.
* review status.
* automation mode.
* final-submit state.

---

# Review Sections

```text
Job Identity
Personal Information
Documents
Employment
Education
Work Authorization
Salary and Availability
Legal and Demographic
Narrative Answers
Browser Validation
Warnings
```

---

# Sensitive Review Sections

Legal and demographic sections should be collapsed by default.

Display:

```text
Sensitive responses completed
```

with a Reveal control.

---

# Document Verification

Show:

* Resume filename.
* resume version.
* upload status.
* cover-letter filename.
* supporting documents.
* file hashes only in advanced details.

---

# Final Browser Comparison

Highlight mismatches between:

* Expected answer.
* browser value.
* package source.

---

# Review Approval Actions

Primary actions:

```text
Approve and Submit
Approve for Automatic Submission
Save Changes and Rerun Review
Return to Preparation
Cancel Application
```

The available actions depend on configuration.

---

# Approval Confirmation

Before approving final submission, show:

```text
You are approving the current application form and these artifact versions:

Resume version 2
Cover letter version 1
Answer set version 3
```

The confirmation should explain that material changes invalidate approval.

---

# Final Submission Experience

## Automatic Mode

The UI should show:

```text
Application review passed.
Submission readiness passed.
Submitting application.
```

No additional user click is required unless policy changes.

---

## Review Mode

The final user action should be clearly labeled:

```text
Approve and Submit Application
```

Avoid ambiguous labels such as:

```text
Continue
Complete
Proceed
```

---

## Manual Mode

The UI should not imply the platform will submit.

Display:

```text
Prepared for manual completion
```

and provide:

* Application URL.
* resume.
* cover letter.
* answer checklist.
* remaining fields.

---

# Submission In Progress

During final submission:

* Disable repeated Submit actions.
* show that an irreversible action has started.
* display verification status.
* prevent queue duplicate actions.

Example:

```text
Submission action initiated

Verifying whether the employer received the application.
Do not submit the application again.
```

---

# Submission Success

Display:

```text
Application Submitted
```

Include:

* Company.
* role.
* date and time.
* confirmation number.
* ATS application ID when available.
* confirmation link.
* resume used.
* history-sync result.

---

# Submission Success Actions

```text
View Application Record
Open Confirmation
Continue Queue
Add Follow-Up Date
```

---

# Submission Failed

Display:

* Whether the final click occurred.
* whether an application was created.
* failure reason.
* retry safety.
* next action.

Example:

```text
Submission did not occur

The final page rejected the application because a required field was incomplete.
It is safe to correct the field and retry.
```

---

# Submission Unknown

Submission Unknown requires a unique high-visibility experience.

Display:

```text
Submission Status Unknown

The final submission action was initiated, but the platform could not verify whether the employer received the application.

Do not submit again yet.
```

---

# Submission Unknown Actions

```text
Check ATS Dashboard
Open Application
Mark as Submitted
Mark as Not Submitted
Keep Unresolved
View Evidence
```

Marking as Submitted or Not Submitted should require an explanation or evidence note.

---

# Submission Unknown Queue Behavior

The UI should explain whether the queue is paused.

Example:

```text
The queue is paused to prevent a possible duplicate application.
```

Allow continuing the rest of the queue only after explicit acknowledgment.

---

# Application History

## Purpose

Provide a reliable local record of application activity and outcomes.

---

# History Page Views

Recommended views:

```text
All Applications
Submitted
Under Review
Interviews
Offers
Rejected
Needs Follow-Up
Submission Unknown
Manual Applications
Archived
```

---

# History Table

Recommended columns:

* Company.
* job title.
* location.
* date applied.
* application status.
* recruitment status.
* match score.
* ATS.
* resume.
* follow-up date.
* notes.

---

# History Filters

```text
Date range
Company
Status
Location
Country
Job family
ATS
Automation mode
Match score
Follow-up state
```

---

# History Record Detail

Display:

* Job information.
* application timeline.
* submission evidence.
* resume and cover-letter versions.
* confirmation number.
* status changes.
* follow-up information.
* notes.
* package link.
* audit summary.

---

# Add Manual Application

Allow users to add externally completed applications.

Fields:

* Company.
* job title.
* job URL.
* date applied.
* status.
* resume used.
* notes.
* optional confirmation.

Clearly label:

```text
Verification source: User
```

---

# Update Recruitment Status

Allow:

```text
Under Review
Assessment
Recruiter Contact
Interview
Final Interview
Offer
Rejected
Withdrawn
Position Closed
```

Preserve the submission status separately.

---

# Status Timeline

Display chronological events:

```text
July 12 — Submitted
July 18 — Recruiter Contact
July 22 — Interview
July 30 — Rejected
```

---

# Follow-Up Experience

Allow the user to:

* Set follow-up date.
* set follow-up type.
* add contact.
* add note.
* mark complete.
* reschedule.

The MVP does not require automated email sending.

---

# History Export

Provide:

```text
Export CSV
Export XLSX
Export Filtered Results
```

Explain that exports exclude highly sensitive application answers.

---

# Candidate Profile

## Purpose

Manage trusted candidate information used across applications.

---

# Candidate Profile Sections

```text
Personal Information
Professional Summary
Employment
Education
Skills
Certifications
Projects
Work Authorization
Preferences
Standard Answers
Sensitive Answers
Source Files
Version History
```

---

# Active Candidate Profile Indicator

The active profile should be visible globally.

For future multi-profile support, switching profiles should require confirmation when workflows are active.

---

# Personal Information

Display editable structured fields.

Sensitive values such as full address should be collapsed or partially masked.

---

# Employment Editor

Support:

* Add role.
* edit role.
* reorder roles.
* mark current role.
* add responsibilities.
* add achievements.
* attach source reference.
* validate dates.

---

# Education Editor

Support:

* Institution.
* degree.
* field.
* dates.
* GPA policy.
* current-enrollment state.
* source reference.

---

# Skills Editor

Allow:

* Skill name.
* proficiency description when explicitly provided.
* years of experience when supported.
* source.
* category.
* preferred resume inclusion.

Do not auto-convert keyword mentions into verified skills without review.

---

# Work Authorization Editor

Keep distinct fields clearly separated.

Display a warning when values are logically inconsistent.

---

# Standard Answers

Group reusable answers by category.

Examples:

* Relocation.
* travel.
* notice period.
* salary.
* work authorization.
* legal.
* demographic.
* company-interest templates.

---

# Source Files

Display imported files:

* Filename.
* file type.
* date added.
* status.
* hash in advanced view.
* parsing result.
* data categories extracted.

---

# Candidate Data Conflict UI

When sources conflict, show:

```text
Current title differs between candidate.json and resume.pdf.
```

Actions:

```text
Use Structured Profile
Use Resume Value
Enter Correct Value
Keep Both with Context
```

---

# Candidate Profile Changes

Before saving a material change, show impacted packages.

Example:

```text
Changing future sponsorship from No to Yes will require refreshing 6 prepared applications.
```

---

# Settings

## Purpose

Configure platform behavior without editing raw files.

---

# Settings Categories

```text
General
Automation
Job Discovery
Documents
Application Answers
Review
Browser
ATS Adapters
Reasoning Provider
Privacy
Security
History
Logging
Retention
Backups
Advanced
```

---

# General Settings

Possible settings:

* Active candidate profile.
* local data directory.
* time zone.
* date format.
* interface density.
* default country.
* default automation mode.

---

# Automation Settings

Configure:

* Automatic mode.
* Review mode.
* Manual mode.
* continue after package failure.
* pause on user action.
* pause on Submission Unknown.
* maximum queue size.
* maximum retries.
* automatic account creation.
* automatic legal attestation.

Dangerous settings should have explanations and confirmation.

---

# Automatic Submission Toggle

The automatic-submission control should:

* Be off by default for initial setup.
* require confirmation to enable.
* explain required quality gates.
* display supported ATS limitations.
* remain disabled in Safe mode.
* remain disabled for degraded adapters.

---

# Job Discovery Settings

Configure:

* Target countries.
* target companies.
* posting age.
* job families.
* seniority.
* remote preference.
* excluded keywords.
* salary threshold.
* source refresh behavior.

---

# Document Settings

Configure:

* Resume-tailoring enabled.
* default resume.
* page-count preference.
* output format.
* cover-letter default.
* filename format.
* document storage location.

---

# Answer Settings

Configure:

* Reusable-answer behavior.
* optional-question policy.
* salary policy.
* relocation policy.
* narrative-answer length.
* user approval before saving global answers.

---

# Review Settings

Configure:

* Preparation review.
* pre-submission review.
* manual-review mode.
* warning policy.
* high-severity blocking.
* maximum correction rounds.
* selected-company review rules.

---

# Browser Settings

Configure:

* Browser profile.
* visible browser.
* profile creation.
* profile reset.
* browser health check.
* download directory.
* maximum pages.
* page timeout.

---

# ATS Adapter Settings

Display adapter cards with:

* Name.
* version.
* stability.
* enabled state.
* capabilities.
* last regression result.
* automatic-mode eligibility.
* fallback policy.

---

# Reasoning Provider Settings

Configure:

* Provider.
* model.
* fallback.
* secret reference.
* timeout.
* token limits.
* request budget.
* privacy policy.
* connection test.

---

# Privacy Settings

Configure:

* Provider-context minimization.
* demographic policy.
* disability policy.
* veteran policy.
* salary logging.
* screenshot retention.
* raw HTML retention.
* diagnostic export policy.
* external telemetry.

---

# Security Settings

Configure:

* Government-ID policy.
* unknown-domain behavior.
* HTTPS requirement.
* browser-profile backup.
* local-interface authentication.
* audit-integrity blocking.
* automatic attestation.
* file-upload roots.

---

# History Settings

Configure:

* CSV enabled.
* XLSX enabled.
* workbook location.
* follow-up defaults.
* manual-record behavior.
* archive behavior.

---

# Logging Settings

Configure:

* Log level.
* debug logging.
* screenshot logging.
* retention.
* diagnostic bundles.
* local metrics.
* sensitive-value policy.

---

# Backup Settings

Configure:

* Backup location.
* encryption.
* retention.
* included categories.
* scheduled local backup when supported.
* browser-profile exclusion.

---

# Advanced Settings

Advanced settings should be clearly separated.

Examples:

* Schema details.
* cache settings.
* adapter overrides.
* custom prompt versions.
* experimental features.
* developer diagnostics.
* raw configuration editor.

Changes should include validation and rollback.

---

# System Health

## Purpose

Show operational condition and provide maintenance actions.

---

# Health Overview

Display component cards:

```text
Storage
Candidate Profile
Reasoning Provider
Browser
Browser Profile
ATS Adapters
History CSV
History XLSX
Logging
Audit Integrity
Disk Space
```

---

# Health Card

Show:

* Status.
* last checked.
* concise result.
* recommended action.
* Run Check action.
* Advanced details.

---

# Overall Health States

```text
Healthy
Degraded
Unavailable
Blocked
```

---

# Health Alerts

Examples:

* Provider key expired.
* browser profile locked.
* XLSX tracker corrupt.
* low disk space.
* degraded ATS adapter.
* stale execution lock.
* audit integrity failure.
* pending history sync.

---

# Maintenance Actions

```text
Run Full Health Check
Create Backup
Verify Backup
Clean Cache
Clean Expired Logs
Rebuild History
Validate Packages
Repair Stale Locks
Create Diagnostic Bundle
Enter Safe Mode
```

---

# Safe Mode UI

When Safe mode is active:

* Display persistent banner.
* disable queue execution.
* disable submission.
* disable candidate-data mutation when configured.
* allow health checks and diagnostics.
* explain why Safe mode is active.

---

# Maintenance Mode UI

Display:

```text
Maintenance mode active

New application workflows cannot start while maintenance is running.
```

Show current maintenance task and progress.

---

# Notifications

## Purpose

Notify the user about important events without overwhelming them.

---

# Notification Categories

```text
Action Required
Submission Result
Queue Status
System Health
Security
History
Informational
```

---

# Notification Priority

High-priority notifications:

* Submission Unknown.
* security incident.
* CAPTCHA.
* MFA.
* manual approval.
* required missing answer.
* browser crash.
* failed history sync after submission.

---

# Notification Center

Display:

* Unread count.
* priority.
* package or component.
* message.
* timestamp.
* primary action.
* dismiss or acknowledge.

Critical unresolved notifications should not be dismissible without acknowledgment.

---

# Desktop Notifications

Optional local desktop notifications may be used for:

* CAPTCHA.
* MFA.
* manual review ready.
* submission verified.
* Submission Unknown.
* queue complete.

Notifications should not contain sensitive values.

---

# Search

Global search may include:

* Companies.
* job titles.
* job IDs.
* packages.
* history.
* confirmation numbers.
* notes.

Do not index sensitive answer values by default.

---

# Command Palette

A keyboard-accessible command palette may provide:

```text
Add Job URL
Start Queue
Pause Queue
Open Candidate Profile
Run Health Check
Create Backup
Open Submission Unknown Items
```

This is optional for the MVP.

---

# Confirmation Dialogs

Confirmation dialogs should be used for:

* Final user-approved submission.
* enabling automatic submission.
* queue cancellation.
* package deletion.
* duplicate override.
* candidate-profile deletion.
* history correction.
* browser-profile deletion.
* data restore.
* upgrade.
* decommissioning.

---

# Confirmation Dialog Requirements

A confirmation dialog should state:

* Exact action.
* affected item.
* whether reversible.
* consequences.
* primary confirm label.
* cancel action.

Avoid generic buttons such as:

```text
Yes
No
```

Prefer:

```text
Delete Package
Keep Package
```

---

# Destructive Action Design

Destructive actions should:

* Use explicit labels.
* avoid placement beside primary positive actions.
* require confirmation.
* preserve audit records where applicable.
* allow undo when feasible.
* explain irreversible effects.

---

# Empty States

Empty states should guide the user.

Examples:

## No Jobs

```text
No jobs have been discovered yet.

Add a company career page or direct job URL to begin.
```

## No Applications

```text
No Application Packages exist.

Select jobs and prepare application materials.
```

## No History

```text
No application history yet.

Submitted and manually recorded applications will appear here.
```

---

# Loading States

Loading indicators should show the operation.

Preferred:

```text
Analyzing job requirements
```

Avoid:

```text
Loading
```

For long multi-stage operations, show completed stages.

---

# Background Operation Language

The interface should not promise asynchronous completion unless an actual background task system exists.

For active local workflows, display current progress and allow pause or cancellation.

---

# Error Messages

Error messages should contain:

* What failed.
* impact.
* whether data is safe.
* whether submission may have occurred.
* what the user can do.
* diagnostic reference.

---

# Error Message Example

```text
The browser closed before the final application page was completed.

No submission attempt was made.
The application can be resumed from the last completed page.
```

---

# Submission Error Language

Always distinguish:

```text
No submission attempt occurred
```

from:

```text
A submission attempt occurred, but the outcome is unknown
```

---

# Technical Details

Error dialogs may include:

```text
Show Technical Details
```

Advanced information may show:

* Error code.
* component.
* stage.
* retry count.
* adapter.
* diagnostic ID.

Do not expose secrets or sensitive values.

---

# Retry Actions

Use specific actions:

```text
Retry Page
Restart Browser and Resume
Rerun Review
Rebuild XLSX
Check ATS Dashboard
```

Avoid generic Retry when the scope is unclear.

---

# Undo

Undo may be supported for:

* Job skip.
* queue reorder.
* note deletion.
* status update.
* optional answer edit before submission.

Undo should not be offered for:

* Final submission.
* external ATS account creation.
* deletion after secure cleanup.
* withdrawal already sent to employer.

---

# Accessibility

The UI should target WCAG 2.1 AA principles where practical.

---

# Keyboard Navigation

All primary workflows should be keyboard accessible.

Requirements:

* Logical tab order.
* visible focus.
* skip navigation.
* keyboard-operable dialogs.
* keyboard-operable tables.
* keyboard queue reorder alternative.
* Escape closes non-critical modal where safe.
* no keyboard trap.

---

# Screen Readers

Use:

* Semantic headings.
* landmarks.
* accessible names.
* descriptive button labels.
* status announcements.
* table headers.
* form-error associations.
* live regions for progress.

---

# Live Status Announcements

Screen readers should announce:

* Queue paused.
* user action required.
* review ready.
* submission initiated.
* submission verified.
* Submission Unknown.
* critical health alert.

Announcements should be concise.

---

# Color and Contrast

Requirements:

* Sufficient contrast.
* status not conveyed by color alone.
* visible focus.
* high-contrast support where possible.
* avoid pale warning text.

---

# Motion

Animations should be limited.

Respect reduced-motion preferences.

Do not use motion that distracts during long queue workflows.

---

# Text Scaling

The interface should remain usable at increased browser zoom.

Critical controls should not become inaccessible at 200% zoom.

---

# Accessible Documents

Generated resume and cover-letter previews should not replace downloadable accessible document files.

Where possible:

* Preserve selectable text.
* use semantic DOCX structure.
* avoid image-only PDFs.

---

# Table Accessibility

Tables should include:

* Header cells.
* sortable-column labels.
* filter descriptions.
* row action labels.
* selected-row state.
* keyboard access.

---

# Forms

Forms should include:

* Visible labels.
* required indicators.
* inline errors.
* error summary.
* help text.
* valid autocomplete attributes when safe.
* clear Save and Cancel actions.

---

# Sensitive Fields and Accessibility

Masking should not make sensitive information impossible to review.

Reveal controls should have labels such as:

```text
Reveal work-authorization answer
```

rather than:

```text
Show
```

---

# Content Style

The interface should use plain, direct language.

Preferred:

```text
A required answer is missing.
```

Avoid:

```text
Answer-resolution workflow dependency failure.
```

---

# Status Wording

Use stable terms consistently.

Do not use:

```text
Complete
```

to refer to both:

* form completion.
* workflow completion.
* verified submission.

---

# Recommended Terminology

```text
Prepared:
Documents and expected answers exist.

Ready:
All requirements for the next stage passed.

In Progress:
Browser execution is active.

Ready for Review:
Form is filled and awaiting approval.

Submitting:
Final action initiated and verification underway.

Submitted:
Submission verified.

Submission Unknown:
Final action may have occurred, but outcome is not verified.
```

---

# Help and Guidance

Provide contextual help for:

* Work authorization.
* future sponsorship.
* salary types.
* demographic questions.
* legal questions.
* automatic submission.
* Submission Unknown.
* duplicate applications.
* browser profiles.
* ATS adapters.

---

# Help Content Rules

Help content should:

* Explain platform behavior.
* distinguish facts from user choices.
* avoid legal or immigration guarantees.
* avoid implying the system can bypass security controls.
* link to settings when appropriate.

---

# Tooltips

Use tooltips only for concise supplemental information.

Do not hide critical instructions exclusively in tooltips.

---

# Inline Documentation

Examples:

```text
Future sponsorship is separate from whether you are currently authorized to work.
```

```text
The platform will not automatically retry a submission when the outcome is unknown.
```

---

# Privacy UX

Privacy controls should be understandable without reading technical documentation.

---

# Data Use Indicators

For candidate fields, the UI may show:

```text
Used in resumes
Used in application forms
Never sent to the reasoning provider
Stored locally
```

---

# Provider Context Preview

An advanced option may show categories sent to the provider.

Example:

```text
Included:
Relevant employment
Relevant skills
Job description

Excluded:
Demographic information
Government identifiers
Credentials
```

---

# Sensitive Data Badge

Use a badge such as:

```text
Sensitive
```

for:

* Government ID.
* legal disclosures.
* demographics.
* disability.
* veteran status.
* immigration-document information.

The badge should not reveal the value.

---

# Screenshot Privacy Controls

Users should be able to:

* View stored screenshots.
* delete eligible screenshots.
* change retention.
* understand why a screenshot was captured.
* see whether it is redacted.

---

# Export Privacy

Before export, show:

* Included categories.
* excluded categories.
* encryption option.
* destination.
* number of records.
* whether sensitive data is included.

---

# Deletion UX

Deletion should distinguish:

```text
Delete draft package
Delete submitted package
Delete browser profile
Delete candidate profile
Delete application history
Delete all local data
```

Each action should explain scope.

---

# Browser Profile UX

The Browser Profiles page should show:

* Profile ID.
* candidate identity.
* active status.
* last used.
* known ATS sessions.
* health.
* storage size.
* lock status.

Actions:

```text
Launch Profile
Run Health Check
Create New Profile
Rename
Delete
Reauthenticate
```

---

# Browser Profile Warning

Display:

```text
Browser profiles contain login sessions and should not be shared or exported.
```

---

# ATS Adapter UX

The Adapter page should display:

* ATS name.
* stability.
* version.
* automatic mode allowed.
* generic fallback.
* recent health.
* known limitations.

---

# Degraded Adapter Warning

Example:

```text
Workday adapter is currently degraded.

Review mode is required.
Automatic submission is disabled until regression tests pass.
```

---

# Reasoning Provider UX

The Provider page should show:

* Provider.
* model.
* connection status.
* fallback status.
* recent request failures.
* local privacy policy.
* usage summary when available.

---

# Provider Failure Experience

Display:

```text
The reasoning provider is unavailable.

Prepared applications remain safe.
Tasks requiring new narrative generation are paused.
```

Offer:

```text
Retry Connection
Use Tested Fallback
Continue in Manual Mode
```

---

# Cost Awareness

When token or usage information is available, show:

* Approximate request count.
* token usage.
* model used.
* configured limits.

Do not present estimated provider cost as exact unless supported by current provider pricing and verified calculation.

---

# Audit UX

Audit information should answer user questions rather than present raw events first.

Suggested actions:

```text
Why was this application blocked?
Which resume was submitted?
Why was this answer selected?
Was Submit clicked?
How was submission verified?
```

---

# Explainability Panel

Example:

```text
Why was this answer selected?

Question:
Will you now or in the future require sponsorship?

Answer:
Yes

Source:
Candidate Profile > Work Authorization > Future Sponsorship

Last confirmed:
July 12, 2026
```

Sensitive answers should remain hidden unless revealed.

---

# Recovery UX

## Purpose

Help the user safely resume interrupted workflows.

---

# Startup Recovery Screen

If incomplete workflows exist, display:

* Company and role.
* previous state.
* last checkpoint.
* whether submission was attempted.
* recommended action.
* recovery risk.

---

# Recovery Categories

```text
Safe to Resume
User Action Required
Submission Verification Required
Manual Recovery Required
Cannot Resume
```

---

# Safe Resume Example

```text
Google — Senior Software Engineer

Last completed stage:
Page 2 of 5

No submission attempt occurred.

[Resume Application] [Open Package] [Cancel]
```

---

# Submission Recovery Example

```text
Stripe — Backend Engineer

The final submission action may have occurred.
The outcome must be verified before any retry.

[Check ATS Dashboard] [View Evidence]
```

---

# Stale Lock Recovery

The UI should not expose raw lock files as the primary workflow.

Display:

```text
An interrupted workflow lock was found.
The owning process is no longer running.
```

Actions:

```text
Inspect Workflow
Recover Safely
Keep Locked
```

---

# Maintenance and Upgrade UX

## Update Available

Display:

* Current version.
* available version.
* release channel.
* security fixes.
* migrations required.
* backup requirement.
* known limitations.

---

# Upgrade Action

Before upgrade:

```text
Pause active workflows.
Create verified backup.
Review migration details.
```

The UI should block upgrade during final submission.

---

# Migration Progress

Display:

* Migration ID.
* current stage.
* records processed.
* warnings.
* backup ID.
* rollback availability.

---

# Failed Migration

Display:

```text
Upgrade could not complete.

Your pre-upgrade backup is intact.
The platform has entered Safe mode.
```

Actions:

```text
Rollback
View Migration Report
Export Diagnostics
```

---

# Backup UX

## Create Backup

Allow selection of:

* Candidate profile.
* Application Packages.
* history.
* configuration.
* audit records.
* generated documents.

Browser profiles and secrets should be excluded by default.

---

# Backup Result

Display:

* Backup ID.
* path.
* encrypted status.
* file count.
* size.
* verification status.
* created date.

---

# Restore UX

Show:

* Backup contents.
* version.
* schema compatibility.
* conflicts.
* categories to restore.
* current-data backup action.

Use Maintenance mode during restore.

---

# Performance UX

The interface should remain responsive while:

* Jobs are being analyzed.
* documents are generated.
* browser automation runs.
* history exports are created.

Long operations should not block navigation where safe.

---

# Optimistic Updates

Avoid optimistic status changes for consequential actions.

Do not show Submitted before verification.

Optimistic UI may be used for low-risk actions such as:

* Adding a note.
* changing a filter.
* reordering pending queue items.

---

# Refresh Behavior

The UI should update active workflow state automatically.

Potential approaches:

* Local event stream.
* polling.
* WebSocket or server-sent events.

Connection loss should not alter workflow truth.

---

# Stale UI Detection

If the interface loses connection to the local backend:

```text
Connection to the local application was interrupted.
```

The UI should:

* stop showing stale progress as current.
* reconnect.
* reload authoritative state.
* avoid repeating actions.

---

# Multi-Tab Behavior

If the local UI is open in multiple tabs:

* State-changing actions should use version checks.
* only one tab should control modal review when practical.
* duplicate final actions should be prevented by backend locks.
* stale views should refresh.

---

# Concurrency Conflicts

When another tab or process changes a package, display:

```text
This package changed after you opened it.

Reload the current version before editing.
```

---

# Unsaved Changes

Warn before leaving pages with:

* Edited answers.
* modified candidate profile.
* review changes.
* settings changes.

Do not warn for read-only browsing.

---

# Draft Saving

Candidate-profile and answer edits may autosave as drafts.

Final trusted-source updates should require explicit Save.

---

# User Preferences

The interface may remember:

* Table sort.
* filters.
* density.
* expanded sections.
* last visited page.
* dashboard layout.
* preferred queue view.

Do not store sensitive revealed values as UI preferences.

---

# Themes

The UI may support:

* Light.
* dark.
* system default.

Theme support should preserve contrast and status clarity.

---

# Localization

The MVP may use English.

The architecture should avoid hardcoding interface strings into workflow logic.

Future localization may require:

* Date formatting.
* number formatting.
* field-label translation.
* right-to-left support.
* local ATS question handling.

---

# Date and Time Presentation

Display user-friendly local times while preserving exact timestamps in details.

Example:

```text
July 12, 2026 at 2:30 PM
```

Advanced details may show ISO timestamps.

---

# File Names

The UI should show human-readable filenames.

Long paths should not be exposed by default.

Package-relative or logical locations may be shown in Advanced details.

---

# Downloads and Open Actions

Use clear labels:

```text
Open Resume
Download Resume
Open Application URL
Open Confirmation
Export History
```

Do not use generic file icons without labels.

---

# User Interface State Model

Each page should derive its actions from authoritative backend state.

Example:

```json
{
  "package_status": "ready",
  "next_allowed_actions": [
    "queue",
    "review",
    "refresh",
    "skip"
  ]
}
```

The UI should not infer workflow transitions independently.

---

# Frontend Action Validation

The backend must validate every state-changing action.

Disabled buttons are not a security or workflow-control boundary.

---

# UI Error Codes

Advanced error details may include stable codes.

Example:

```text
BROWSER_NAV_TIMEOUT
```

The user-facing message should remain understandable.

---

# Event-Driven UI

Important backend events should update:

* Dashboard.
* queue.
* application detail.
* notifications.
* history.
* health.

---

# Event Deduplication

The frontend should avoid showing duplicate notifications when:

* It reconnects.
* events are replayed.
* the same status is synchronized twice.

---

# User Action Request Model

The interface should render a common user-action model.

```json
{
  "request_id": "",
  "category": "missing_answer",
  "title": "Required answer needed",
  "message": "",
  "package_id": "",
  "sensitive": true,
  "actions": [],
  "resume_stage": ""
}
```

---

# User Action Categories

```text
Login
MFA
CAPTCHA
Missing Answer
Ambiguous Answer
Sensitive Field
Manual Review
Unknown Submission
External Assessment
Browser Interaction
Security Confirmation
```

---

# Action Request Expiration

If a user-action request becomes stale because:

* Browser session expired.
* package changed.
* application closed.
* another action resolved it.

The UI should mark it:

```text
No longer active
```

and explain why.

---

# UI Security

The local UI should:

* Bind to localhost.
* use secure session handling.
* use CSRF protection.
* validate origins.
* escape external content.
* sanitize Markdown.
* restrict downloads.
* prevent arbitrary path access.
* avoid exposing secrets in HTML.
* use a restrictive Content Security Policy.

---

# External Content Rendering

Job descriptions and application questions should be sanitized.

Do not render employer-provided scripts or unsafe HTML.

---

# Link Handling

External links should:

* Display destination domain when helpful.
* open safely.
* use expected protocols.
* warn for unknown domains.
* not expose local referrer data unnecessarily.

---

# Clipboard

Copy actions may be offered for:

* Narrative answers.
* confirmation numbers.
* job IDs.

Sensitive values should require explicit reveal before copy.

---

# Browser Autocomplete

Sensitive local UI fields such as API keys or government identifiers should disable normal browser autocomplete where appropriate.

---

# Session Timeout

If local UI authentication is enabled, support:

* Inactivity timeout.
* lock screen.
* reauthentication.
* preservation of active backend workflows.

Locking the UI should not cancel a queue.

---

# Accessibility Acceptance Criteria

The UI is accessible when:

* All main actions are keyboard operable.
* focus is visible.
* dialogs announce titles.
* status changes are announced.
* color is not the only status indicator.
* form errors are associated with fields.
* tables are navigable.
* text can be enlarged.
* screen-reader labels are meaningful.
* critical workflows can be completed without a mouse.

---

# Usability Testing

User testing should cover:

* First-time setup.
* adding job sources.
* selecting jobs.
* reviewing match scores.
* preparing packages.
* understanding readiness.
* starting a queue.
* responding to CAPTCHA.
* reviewing final application.
* understanding submission outcome.
* resolving Submission Unknown.
* finding an application in history.
* changing privacy settings.
* creating a backup.
* recovering an interrupted workflow.

---

# UX Test Questions

Tests should determine whether users can answer:

```text
Which application is currently running?

Which resume will be uploaded?

Why is this job recommended?

Why is this application blocked?

Has Submit been clicked?

Was submission verified?

What information is waiting for me?

Where can I change sponsorship answers?

How do I pause automation?

How do I delete local data?
```

---

# Critical UX Errors

Examples:

* Submitted shown before verification.
* Submission Unknown visually presented as Failed.
* Wrong package displayed during approval.
* sensitive values exposed on dashboard.
* final Submit action mislabeled.
* automatic submission enabled without clear confirmation.
* user cannot identify active browser profile.
* blocking issue hidden in technical details.
* queue continues after unknown submission without notice.
* destructive deletion lacks scope explanation.

---

# UI Testing Strategy

Test categories:

* Component tests.
* page tests.
* interaction tests.
* accessibility tests.
* visual regression.
* state-transition tests.
* error tests.
* security tests.
* responsive tests.
* recovery tests.

---

# Component Tests

Test:

* Status badge.
* finding card.
* answer row.
* sensitive-value reveal.
* confirmation dialog.
* queue item.
* health card.
* notification.
* timeline.
* document preview.

---

# Page Tests

Test:

* Dashboard.
* Jobs list.
* job detail.
* application list.
* package detail.
* queue.
* review.
* history.
* profile.
* settings.
* health.
* onboarding.
* recovery.

---

# Interaction Tests

Test:

* Select jobs.
* bulk prepare.
* queue reorder.
* pause and resume.
* edit answer.
* replace resume.
* approve review.
* cancel application.
* resolve intervention.
* update status.
* create backup.

---

# Accessibility Tests

Use automated and manual checks for:

* Labels.
* keyboard.
* focus.
* contrast.
* live regions.
* tables.
* dialogs.
* zoom.
* screen readers.

Automated accessibility tools are not sufficient alone.

---

# Visual Regression

Use visual snapshots for:

* Dashboard.
* queue status.
* review page.
* Submission Unknown screen.
* health alerts.
* document preview.
* responsive layout.

---

# State Matrix Testing

Each package state should have a UI fixture.

```text
Preparing
Ready
Ready with Warnings
Queued
Executing
Waiting for User
Waiting for Review
Submitting
Submitted
Submission Unknown
Blocked
Failed
Cancelled
Already Applied
Closed
```

---

# Empty and Error State Testing

Test:

* No jobs.
* no applications.
* no history.
* provider unavailable.
* browser unavailable.
* corrupt history.
* stale package.
* unsupported ATS.
* invalid candidate profile.
* low disk.
* audit failure.

---

# Security UI Tests

Test:

* XSS in job description.
* malicious Markdown.
* unsafe external URL.
* unauthorized package download.
* CSRF attempt.
* sensitive value in DOM.
* API key reveal.
* path traversal.
* stale-session action.

---

# Recovery UI Tests

Test:

* Restart during preparation.
* restart during browser execution.
* restart after final click.
* stale lock.
* failed migration.
* browser-profile corruption.
* pending history sync.

---

# Performance UI Tests

Test with:

* 1,000 jobs.
* 100 packages.
* 1,000 history rows.
* long audit timelines.
* many notifications.
* large answer sets.
* multiple document versions.

The interface should remain responsive through pagination, virtualization, or incremental loading.

---

# Browser Support

The local UI should define supported browser versions.

Since Playwright controls a separate application browser, the local UI browser and automation browser may be different.

The project may initially support:

```text
Latest stable Chromium-based desktop browsers
```

Specific support should be tested and documented.

---

# Frontend Technology Requirements

The UI technology should support:

* Accessible components.
* local API integration.
* event-driven updates.
* document previews.
* large tables.
* secure Markdown rendering.
* state persistence.
* typed API contracts.
* test automation.

This document does not mandate a specific frontend framework.

---

# API Requirements for UI

The backend should provide structured APIs for:

* Jobs.
* packages.
* queue.
* workflow state.
* user actions.
* review.
* readiness.
* submission.
* history.
* candidate profile.
* settings.
* health.
* maintenance.
* audit explanations.

---

# API Error Response

UI-facing errors should include:

```json
{
  "error_code": "READINESS_REQUIRED_ARTIFACT_MISSING",
  "message": "The active resume file is missing.",
  "action": "regenerate_resume",
  "package_id": "",
  "details_available": true
}
```

---

# Optimistic Concurrency

Updates should include version identifiers.

Example:

```json
{
  "package_id": "",
  "expected_version": 4,
  "changes": {}
}
```

If the package changed, the UI should reload rather than overwrite newer data.

---

# UI Audit Actions

State-changing UI actions should record:

* Actor.
* action.
* target.
* prior version.
* new version.
* timestamp.
* reason when required.

---

# User Experience Completion Criteria

The UI and UX phase is complete when the user can:

* Complete onboarding.
* configure candidate data.
* add job sources.
* run job discovery.
* understand job-match scores.
* select jobs.
* prepare Application Packages.
* inspect resumes and cover letters.
* inspect and edit answers.
* understand readiness.
* create and manage a queue.
* observe browser execution.
* complete CAPTCHA, MFA, and login interventions.
* provide missing answers.
* review final applications.
* approve submission.
* understand verified submission.
* understand Submission Unknown.
* inspect confirmation evidence.
* manage application history.
* update recruitment status.
* configure privacy and security.
* manage browser profiles.
* inspect system health.
* create and restore backups.
* recover interrupted workflows.
* delete local data deliberately.

---

# Definition of UI Completion

The user interface is complete when it accurately represents the underlying workflow state and never implies that an action occurred without backend evidence.

The interface should reliably distinguish:

```text
Selected
Prepared
Ready
Queued
In Progress
Ready for Review
Submitting
Submitted
Failed
Submission Unknown
```

It should clearly expose:

* Required user actions.
* blocking conditions.
* active artifacts.
* automation mode.
* browser state.
* review status.
* submission evidence.
* history synchronization.
* security and privacy controls.

---

# Definition of UX Safety

The UX is safe when:

* Automatic submission cannot be enabled accidentally.
* Final submission is clearly identified.
* repeated submission actions are prevented.
* Submission Unknown blocks unsafe retry.
* sensitive values are hidden by default.
* wrong-account detection is visible.
* wrong-job and wrong-document findings are prominent.
* security warnings cannot be mistaken for informational notices.
* destructive actions explain scope.
* user intervention preserves application context.
* technical failures do not obscure whether submission may have occurred.

---

# Definition of Accessibility Completion

Accessibility is complete when:

* Primary workflows are keyboard accessible.
* status changes are announced.
* dialogs are accessible.
* tables are navigable.
* focus is managed.
* color is supplemental.
* text scales correctly.
* error messages are associated with fields.
* screen-reader users can distinguish submission states.
* no critical action requires pointer-only interaction.

---

# Required UX Scenarios

## First-Time Setup

Expected:

* User creates a candidate profile.
* imports a resume.
* confirms extracted facts.
* configures work authorization.
* adds a provider secret.
* creates a browser profile.
* runs a synthetic test.
* reaches the Dashboard.

---

## Job Discovery and Selection

Expected:

* User adds career sources.
* sees discovered jobs.
* filters by country and score.
* understands match reasons.
* selects jobs.
* starts preparation.

---

## Prepared Application

Expected:

* User sees active resume.
* cover-letter requirement.
* prepared answers.
* warnings.
* readiness status.
* queue action.

---

## CAPTCHA Intervention

Expected:

* Queue pauses.
* browser window remains available.
* clear CAPTCHA instruction appears.
* user completes challenge.
* workflow resumes.
* no bypass claim appears.

---

## Missing Legal Answer

Expected:

* Complete question shown.
* no default guess.
* sensitive status shown.
* user selects answer.
* reuse choice offered.
* application review reruns.

---

## Manual Review

Expected:

* Final browser values shown.
* sensitive sections collapsed.
* uploaded documents verified.
* warnings shown.
* user approves exact artifact versions.
* submission begins only after approval.

---

## Submission Success

Expected:

* Submitted appears only after verification.
* confirmation evidence visible.
* history synchronization shown.
* queue continues according to policy.

---

## Submission Unknown

Expected:

* Unique unknown state.
* warning not to resubmit.
* evidence available.
* queue pause explained.
* ATS dashboard action available.
* later resolution supported.

---

## Browser Crash Before Submit

Expected:

* User sees that no submission attempt occurred.
* package can safely resume.
* checkpoint is displayed.

---

## Browser Crash After Submit

Expected:

* User sees that a submission attempt occurred.
* no Retry Submit button appears.
* verification workflow offered.

---

## Wrong Resume

Expected:

* Review highlights incorrect upload.
* correct file shown.
* replacement action available.
* approval invalidated.
* rereview required.

---

## Duplicate Application

Expected:

* Existing application record shown.
* reason for duplicate match shown.
* automatic execution blocked.
* override requires explicit reason.

---

## Provider Outage

Expected:

* Provider status degraded.
* deterministic tasks remain available.
* affected packages explain what is paused.
* Manual mode is available.

---

## Low Disk Space

Expected:

* Global alert.
* final submission blocked when durability is at risk.
* cleanup options shown.
* audit and submission evidence protected.

---

## History Correction

Expected:

* Current value and corrected value shown.
* reason requested.
* audit event created.
* package evidence not silently overwritten.

---

## Data Deletion

Expected:

* User selects exact data categories.
* consequences displayed.
* submitted-package deletion requires stronger confirmation.
* secrets and browser profiles are separate choices.

---

# Completion Criteria

The User Interface and User Experience specification is complete when:

* Information architecture is defined.
* onboarding is defined.
* dashboard behavior is defined.
* job discovery and selection are defined.
* package preparation is defined.
* document and answer review are defined.
* readiness presentation is defined.
* queue management is defined.
* browser intervention flows are defined.
* application review is defined.
* submission states are defined.
* Submission Unknown has a dedicated experience.
* application history is defined.
* candidate-profile management is defined.
* settings are defined.
* system-health and maintenance interfaces are defined.
* privacy and security controls are defined.
* recovery workflows are defined.
* accessibility requirements are defined.
* responsive behavior is defined.
* UI testing requirements are defined.
* backend state remains authoritative.
* irreversible actions require explicit and accurate presentation.

---

# Summary

The User Interface and User Experience layer turns a complex local automation system into a controlled and understandable workflow.

The interface should help the user move through:

```text
Discover Jobs
    |
    v
Review Matches
    |
    v
Select Jobs
    |
    v
Prepare Applications
    |
    v
Review Readiness
    |
    v
Run Queue
    |
    v
Resolve Interventions
    |
    v
Review Application
    |
    v
Submit
    |
    v
Verify
    |
    v
Track History
```

The UI must always distinguish preparation from execution and submission from verification.

It should provide:

* Clear statuses.
* actionable warnings.
* protected sensitive information.
* visible automation controls.
* reviewable artifacts.
* recoverable workflows.
* accurate history.
* explicit security and privacy settings.
* accessible interaction.

The most important UX rule is:

```text
Never make the user guess whether an application was submitted.
```

The interface should display verified truth, clearly label uncertainty, and preserve user control over every consequential stage.
