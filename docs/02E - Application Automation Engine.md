# 02E - Application Automation Engine

## LLM-Powered Autonomous Job Search & Application Platform

Version: 1.0

---

# Purpose

The Application Automation Engine is responsible for transforming a selected job into a completed online application.

Unlike traditional browser automation tools, this engine separates **reasoning** from **execution**.

Claude performs all reasoning before the browser begins interacting with the website.

The browser then executes a deterministic application plan.

This dramatically improves:

- Reliability
- Speed
- Repeatability
- Debugging
- Error Recovery

---

# High Level Workflow

Selected Jobs

↓

Preparation Phase

↓

Application Queue

↓

Browser Execution

↓

Submission

↓

Verification

↓

Application Tracker

---

# Two Phase Architecture

The application process consists of two completely independent phases.

## Phase 1

Preparation

Claude performs all reasoning.

No browser actions occur.

---

## Phase 2

Execution

Browser automation performs all interactions.

Claude is only consulted if unexpected situations occur.

---

# Why Separate These Phases?

Many AI browser agents attempt to think while interacting with websites.

Example:

Open page

↓

Read question

↓

Ask Claude

↓

Wait

↓

Generate answer

↓

Fill field

↓

Repeat

This is slow.

Expensive.

Fragile.

Instead we perform:

Understand Job

↓

Prepare Everything

↓

Execute Everything

---

# Phase 1 - Application Preparation

The browser remains closed.

Claude prepares every artifact required for the application.

---

## Inputs

Selected Job

Candidate Knowledge Base

Selected Resume

User Preferences

Rules

Application History

---

## Outputs

Prepared Application Package

---

# Application Package

Every selected job generates a package.

Example

```text
Google_Senior_Backend_Engineer/

    job.json

    analysis.json

    tailored_resume.pdf

    cover_letter.pdf

    answers.json

    metadata.json

    screenshots/

```

Nothing has been submitted yet.

---

# Resume Selection

Determine:

Best resume.

Example

Backend.pdf

↓

Backend_Google.pdf

The tailored resume becomes part of the package.

---

# Cover Letter

Generate only if:

Required

or

User Enabled

Otherwise skip.

---

# Question Prediction

Claude should predict likely questions before opening the browser.

Examples

Tell us about yourself.

Why Google?

Salary Expectations.

Visa Status.

Relocation.

Leadership.

Conflict of Interest.

Security Clearance.

Notice Period.

Expected Start Date.

Strengths.

Weaknesses.

Generate reusable answers.

---

# Answer Generation

Every predicted answer should contain:

Question

Answer

Confidence

Source

Example

```json
{

 "question":"Why do you want to work here?",

 "answer":"...",

 "confidence":96,

 "source":"answers.md"

}
```

---

# Source Priority

Candidate JSON

↓

Rules

↓

Answers

↓

Resume

↓

Preferences

↓

Notes

↓

Claude Reasoning

Claude must never invent factual information.

---

# Validation

Before browser execution:

Validate:

Resume exists.

Generated files exist.

Candidate data loaded.

Required fields available.

Application package complete.

If validation fails,

the package is marked

Needs User Attention.

---

# Application Queue

Prepared packages enter a queue.

Example

1

Google

Ready

2

Microsoft

Ready

3

Meta

Needs Attention

4

Apple

Ready

The browser only processes

Ready

packages.

---

# Queue Benefits

Resume generation happens once.

Questions generated once.

Claude invoked once.

Execution becomes deterministic.

Failures become resumable.

---

# Browser Execution Phase

Only prepared packages enter execution.

No resume generation.

No ranking.

No tailoring.

No reasoning.

Execution only.

---

# Browser Responsibilities

Open Browser.

Restore Session.

Navigate.

Upload Files.

Fill Fields.

Click Buttons.

Submit.

Verify.

Record.

---

# Browser Rules

Every interaction must be verified.

Never assume.

Always confirm.

---

# Form Inspection

Before filling anything:

Read every field.

Determine:

Label

Type

Required

Validation

Allowed Values

Grouping

Accessibility

Return structured form.

---

# Field Types

Textbox

Textarea

Dropdown

Searchable Dropdown

Checkbox

Radio Button

Date Picker

File Upload

Phone

Email

URL

Autocomplete

Hidden

Custom Widgets

---

# Mapping

Each form field should map to one prepared answer.

Example

Label

Visa Status

↓

answers.json

↓

H1B

No Claude call required.

---

# Unknown Fields

If a field is unknown:

Pause.

Send field context to Claude.

Generate answer.

Store answer.

Continue.

Unknown fields should be rare.

---

# File Upload

Supported uploads:

Resume

Cover Letter

Transcript

Certificates

Portfolio

Other Attachments

Verify upload completed successfully.

---

# Multi Page Applications

Supported.

Workflow:

Page 1

↓

Validate

↓

Save Progress

↓

Next

↓

Page 2

↓

Validate

↓

Next

↓

...

↓

Final Review

↓

Submit

---

# Save Progress

After every successful page:

Persist state.

Example

Current Page

Completed Fields

Uploaded Files

Screenshots

If interrupted,

resume later.

---

# Review Modes

Two execution modes.

---

## Automatic Mode

Default.

Browser proceeds immediately.

No pause.

---

## Review Mode

Optional.

Pause before submission.

Display:

Resume

Cover Letter

Generated Answers

Screenshots

Summary

User chooses:

Submit

Skip

Edit

Cancel

---

# Submission

After clicking Submit:

Verify success.

Verification methods:

Confirmation Page

Confirmation Message

Application ID

URL Change

Success Banner

Email Confirmation (future)

---

# Failure Recovery

Failures should be categorized.

Retryable

Network Timeout

Temporary Server Error

Slow Page

Non Retryable

Authentication Failure

Invalid Resume

Missing Required Information

CAPTCHA

User Action Required

---

# Retry Policy

Recoverable failures:

Retry

3

times.

Exponential Backoff.

Capture screenshots.

---

# CAPTCHA

Never attempt bypass.

Pause.

Notify user.

Resume after completion.

---

# Login Sessions

Reuse browser profile.

Do not repeatedly login.

Persistent sessions preferred.

---

# Screenshots

Capture:

Before Submit

After Submit

Errors

Warnings

Unexpected Pages

Store locally.

---

# Logging

Every action should record:

Timestamp

Action

Target

Result

Duration

Error

Recovery

---

# Application History

After successful submission:

Append to local tracker.

Fields:

Company

Job Title

Job ID

Application URL

Date Applied

Resume Version

Status

Notes

---

# Duplicate Check

Before execution:

Search tracker.

If already applied:

Skip.

Unless user overrides.

---

# Application Status

States

Prepared

Queued

Executing

Waiting

Needs Attention

Submitted

Failed

Skipped

Already Applied

Cancelled

---

# Performance Goals

Preparing

50

applications should happen faster than browser execution.

Browser should spend minimal time idle.

Claude should not be repeatedly called.

---

# Security

Sensitive information remains local.

Only required context is sent to Claude.

Logs should never expose secrets.

---

# Future Improvements

Adaptive ATS plugins.

Learning from previous applications.

Application replay.

Bulk resume optimization.

Automatic answer improvement.

Application analytics.

Email verification.

Interview scheduling.

Offer tracking.

---

# Summary

The Application Automation Engine separates planning from execution.

Claude performs all reasoning before the browser begins.

The browser executes a prepared plan with deterministic actions, validation, recovery, and tracking.

This architecture minimizes browser idle time, reduces LLM calls, improves reliability, and makes failures recoverable without repeating expensive reasoning steps.
