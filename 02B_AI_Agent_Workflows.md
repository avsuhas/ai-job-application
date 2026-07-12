# 02B - AI Agent Workflows

## LLM-Powered Autonomous Job Search & Application Platform

Version: 1.0

---

# Purpose

This document defines the logical AI agents that make up the application.

These agents are **not separate language models**. They are logical software components that use the configured reasoning provider (Claude by default) together with deterministic browser automation and local data.

Each agent has a clearly defined responsibility.

The purpose of this separation is to:

- Keep the codebase modular.
- Minimize duplicated logic.
- Make testing easier.
- Allow future replacement or enhancement of individual agents.
- Prevent browser logic from being mixed with reasoning logic.

---

# Design Principles

Every AI Agent should follow these rules.

## Single Responsibility

Each agent should perform exactly one major task.

Example:

Resume Tailoring Agent

↓

Only tailors resumes.

It should not search jobs.

It should not submit applications.

---

## Stateless

Agents should not permanently store information internally.

All persistent information should be stored in:

- Candidate Knowledge Base
- Application Tracker
- Local Cache

---

## Idempotent

Running the same agent multiple times with identical inputs should produce equivalent results.

---

## Explainable

Every agent should provide reasoning for its decisions whenever applicable.

---

## Recoverable

If an agent fails, the orchestration engine should be able to retry the agent without restarting the entire workflow.

---

# AI Workflow

The complete workflow is:

Candidate

↓

Job Discovery Agent

↓

Job Analysis Agent

↓

Job Ranking Agent

↓

Resume Tailoring Agent

↓

Application Preparation Agent

↓

Browser Automation Agent

↓

Form Understanding Agent

↓

Answer Generation Agent

↓

Application Review Agent

↓

Submission Agent

↓

Application History Agent

---

# Job Discovery Agent

## Responsibility

Discover jobs from one or more company career websites.

---

## Inputs

- Career URLs
- Search Keywords
- Preferred Countries
- Preferred Locations
- Remote Preference
- Maximum Jobs
- Date Filter

---

## Outputs

Normalized Job List

---

## Responsibilities

Visit career websites.

Navigate search pages.

Apply search filters.

Handle pagination.

Handle infinite scrolling.

Extract job URLs.

Extract job descriptions.

Extract metadata.

Normalize data.

Remove duplicates.

Return discovered jobs.

---

## Must NOT

Analyze resumes.

Rank jobs.

Fill applications.

Submit forms.

---

# Job Analysis Agent

## Responsibility

Understand each job posting.

---

## Inputs

Job Description

---

## Outputs

Structured Job Analysis

---

## Responsibilities

Extract:

- Required Skills
- Preferred Skills
- Experience
- Education
- Seniority
- Technologies
- Domain
- Visa Requirements
- Remote Status
- Employment Type

Identify:

Required vs Preferred qualifications.

Hard eligibility requirements.

Potential concerns.

---

# Job Ranking Agent

## Responsibility

Determine how well the candidate matches a job.

---

## Inputs

Resume

Candidate Knowledge Base

Job Analysis

User Preferences

---

## Outputs

Match Score

Recommendation

Strengths

Weaknesses

Missing Qualifications

Reasoning

---

## Ranking Rules

Ranking must use semantic understanding.

Keyword counting alone is prohibited.

Required qualifications should receive greater weight than preferred qualifications.

Transferable skills should be recognized where appropriate.

The agent must distinguish between:

- Missing required skills.
- Missing preferred skills.
- Skills that are clearly transferable.

---

## Score

Range:

0–100

Suggested interpretation:

90–100

Exceptional Match

80–89

Strong Match

70–79

Good Match

60–69

Possible Match

Below 60

Low Match

---

# Resume Tailoring Agent

## Responsibility

Generate a tailored version of the resume for a specific job.

---

## Inputs

Original Resume

Candidate Knowledge Base

Job Description

---

## Outputs

Tailored Resume

Resume Change Summary

---

## Allowed Changes

Reorder bullet points.

Highlight relevant projects.

Reword accomplishments.

Adjust summary.

Use terminology from the job description when truthful.

---

## Forbidden Changes

Invent skills.

Invent employment.

Invent education.

Invent certifications.

Invent accomplishments.

Modify employment dates.

Modify company names.

Claim technologies never used.

---

# Application Preparation Agent

## Responsibility

Prepare everything needed before opening the browser.

---

## Responsibilities

Determine:

Resume version.

Cover letter requirement.

Supporting documents.

Expected application flow.

Known ATS platform.

Expected questions.

Collect candidate context.

Prepare answer cache.

---

# Browser Automation Agent

## Responsibility

Control the browser.

---

## Responsibilities

Launch browser.

Reuse login session.

Navigate pages.

Click buttons.

Type text.

Upload files.

Take screenshots.

Wait for page transitions.

Handle navigation.

Handle popups.

Handle new tabs.

Handle iframes.

Handle dialogs.

---

## Browser Rules

Never guess whether an action succeeded.

Verify every interaction.

Wait for expected page state.

Retry recoverable failures.

Capture screenshots when failures occur.

---

# Form Understanding Agent

## Responsibility

Understand application forms before they are filled.

---

## Responsibilities

Identify every field.

Determine field type.

Identify:

- Label
- Placeholder
- Required state
- Validation
- Allowed values

Associate nearby explanatory text.

Extract accessibility information.

Return structured form data.

---

## Supported Field Types

Textbox

Textarea

Dropdown

Searchable Dropdown

Checkbox

Radio Button

Date Picker

Phone Number

Email

URL

Resume Upload

Cover Letter Upload

Multi-select

Auto-complete

Hidden Fields

---

# Answer Generation Agent

## Responsibility

Generate accurate answers for every application question.

---

## Inputs

Candidate Knowledge Base

Resume

Question

Job Description

User Preferences

---

## Output

Final Answer

Confidence Score

Source Reference

---

## Source Priority

1. Candidate Knowledge Base

2. Resume

3. Previous Answers

4. Claude Reasoning

---

## Rules

Never invent qualifications.

Never contradict stored information.

Never modify legal facts.

Clearly distinguish inferred answers.

---

# Application Review Agent

## Responsibility

Validate the completed application.

---

## Responsibilities

Verify:

Required fields completed.

Resume uploaded.

Correct resume version.

Expected files uploaded.

No empty required fields.

No obvious inconsistencies.

Review screenshots.

Prepare summary.

---

## Review Modes

Automatic

↓

Continue automatically.

Manual

↓

Pause for user review.

---

# Submission Agent

## Responsibility

Submit completed applications.

---

## Responsibilities

Click final submit.

Verify success.

Capture confirmation page.

Capture confirmation number.

Capture submission timestamp.

Capture screenshots.

Handle failures.

---

## Success Criteria

Application successfully submitted.

Confirmation page reached.

Confirmation recorded.

Tracker updated.

---

# Application History Agent

## Responsibility

Maintain application history.

---

## Storage

Local Excel or CSV.

---

## Responsibilities

Prevent duplicate applications.

Record:

Company

Job Title

Job ID

Application URL

Date Applied

Resume Version

Status

Notes

Allow manual edits.

---

# Agent Communication

Agents communicate only through structured models.

Agents must never exchange raw browser objects.

Example:

Job Discovery Agent

↓

NormalizedJob

↓

Job Ranking Agent

↓

RankedJob

↓

Resume Agent

↓

PreparedApplication

↓

Browser Agent

---

# Failure Handling

Every agent returns one of:

SUCCESS

FAILED

RETRYABLE

USER_ACTION_REQUIRED

SKIPPED

---

# Logging

Every agent should log:

Start Time

End Time

Duration

Inputs

Outputs

Warnings

Errors

Recovery Actions

---

# Future Agents

The architecture should support additional agents without redesign.

Examples:

Interview Preparation Agent

Referral Finder Agent

LinkedIn Networking Agent

Recruiter Outreach Agent

Offer Comparison Agent

Salary Negotiation Agent

Career Analytics Agent

Resume Optimization Agent

Conference Discovery Agent

Visa Tracking Agent

These agents should integrate with the orchestration engine using the same communication model defined above.

---

# Summary

The application is built as a collection of specialized AI agents coordinated by an orchestration layer.

Each agent has one clearly defined responsibility.

Claude provides reasoning.

The application provides execution.

This separation creates a modular, testable, extensible architecture that can evolve without major redesign.
