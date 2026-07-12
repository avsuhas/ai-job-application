# 02A - Functional Requirements

## LLM-Powered Autonomous Job Search & Application Platform

Version: 1.0

This document defines the functional requirements of the application.

These requirements describe **what** the application must do. They intentionally avoid implementation details, which are covered in later architecture documents.

---

# Table of Contents

1. Functional Overview
2. Primary Actors
3. Functional Modules
4. User Stories
5. Functional Requirements
6. Functional Priorities
7. MVP Requirements
8. Future Enhancements

---

# Functional Overview

The application shall provide an end-to-end AI-assisted workflow for searching, evaluating, and applying to jobs on company career websites.

Rather than functioning as a simple browser automation tool, the application acts as an intelligent orchestration layer that combines:

- Claude's reasoning capabilities
- Browser automation
- Resume intelligence
- Candidate knowledge management
- Workflow automation
- Local persistence

The application shall minimize repetitive manual work while preserving user control and maintaining factual accuracy.

---

# Primary Actors

## Candidate

The primary user of the application.

Responsible for:

- Configuring preferences
- Providing resumes
- Maintaining Candidate Knowledge Base
- Selecting jobs
- Reviewing applications (optional)
- Monitoring progress

---

## Claude

Claude acts as the reasoning engine.

Claude is responsible for:

- Resume understanding
- Job understanding
- Resume tailoring
- Screening question generation
- Form reasoning
- Decision making
- Semantic matching

Claude is NOT responsible for:

- Clicking buttons
- Opening browsers
- Uploading files
- Tracking browser state
- Managing workflows

---

## Browser Automation Engine

Responsible for:

- Navigation
- Clicking
- Typing
- Uploading documents
- Waiting for page changes
- Reading DOM
- Extracting form information

---

# Functional Modules

The system consists of the following logical modules.

1. Candidate Knowledge Base
2. Resume Manager
3. Job Discovery Engine
4. Job Ranking Engine
5. Resume Tailoring Engine
6. Application Preparation Engine
7. Browser Automation Engine
8. Form Understanding Engine
9. Application Submission Engine
10. Application History Manager
11. Local Storage Manager
12. Configuration Manager

Each module should be independently replaceable.

---

# User Stories

## Epic 1

As a candidate,

I want to upload my resume,

so that Claude understands my professional background.

---

## Epic 2

As a candidate,

I want to maintain reusable application information,

so that I never need to repeatedly enter identical data.

---

## Epic 3

As a candidate,

I want to search multiple company websites,

so that I can discover relevant opportunities.

---

## Epic 4

As a candidate,

I want Claude to rank jobs,

so that I spend my time applying only to strong matches.

---

## Epic 5

As a candidate,

I want Claude to tailor my resume,

so that every application is optimized.

---

## Epic 6

As a candidate,

I want the application to complete online forms,

so that I avoid repetitive manual work.

---

## Epic 7

As a candidate,

I want every submitted application recorded,

so that duplicate submissions never occur.

---

# Functional Requirements

Each requirement below is assigned a unique identifier.

---

# Candidate Knowledge Base

## FR-001

The application shall maintain a reusable Candidate Knowledge Base (CKB) on the user's local computer.

---

## FR-002

The CKB shall support multiple files rather than requiring a single monolithic JSON document.

---

## FR-003

Supported formats shall include:

- JSON
- Markdown
- Plain Text
- YAML

---

## FR-004

Claude shall treat the Candidate Knowledge Base as the primary source of truth when answering application questions.

---

## FR-005

Users shall be able to edit the CKB using any text editor.

No proprietary editor shall be required.

---

## FR-006

The application shall reload updated CKB files without requiring schema migration.

---

## Resume Management

---

## FR-007

Users shall be able to upload multiple resumes.

Example:

Backend.pdf

ML.pdf

Infrastructure.pdf

General.pdf

---

## FR-008

The application shall preserve original resumes.

---

## FR-009

Claude shall analyze uploaded resumes.

---

## FR-010

Resume parsing shall identify:

- Skills
- Employers
- Titles
- Technologies
- Education
- Certifications
- Projects

---

## FR-011

Resume analysis results shall be cached locally.

---

## Job Discovery

---

## FR-012

Users shall provide one or more company career websites.

Examples:

Google Careers

Microsoft Careers

Amazon Jobs

NVIDIA Careers

Apple Jobs

Qualcomm Careers

Netflix Careers

etc.

---

## FR-013

The application shall crawl company career portals.

---

## FR-014

Supported navigation shall include:

Search

Pagination

Infinite scrolling

Dynamic content

Lazy loading

---

## FR-015

Users shall specify:

- Keywords
- Countries
- Locations
- Remote preference
- Seniority
- Departments

---

## FR-016

Users may omit filters.

Claude should infer preferences from:

- Resume
- CKB
- Previous searches

---

## FR-017

Duplicate jobs shall be detected.

---

## FR-018

Job IDs shall be normalized.

---

## FR-019

The application shall extract:

Company

Title

Job ID

Description

Location

Country

Date Posted

Application URL

Employment Type

Remote Status

---

## FR-020

The application shall preserve raw job descriptions.

---

# Job Ranking

---

## FR-021

Claude shall analyze every discovered job.

---

## FR-022

Ranking shall consider:

Resume

CKB

Preferences

Keywords

Experience

Skills

Education

---

## FR-023

Keyword matching alone shall never determine ranking.

Semantic understanding is required.

---

## FR-024

Every job shall receive:

Match Score

Recommendation

Strengths

Weaknesses

Missing Skills

Reasoning

---

## FR-025

Scores shall range from:

0

to

100.

---

## FR-026

Users shall sort jobs by:

Match

Date

Company

Country

Title

---

## FR-027

Users shall filter jobs by:

Country

Remote

Company

Date

Score

---

# Resume Tailoring

---

## FR-028

Claude shall generate tailored resumes.

---

## FR-029

Tailoring shall never invent qualifications.

---

## FR-030

Employment dates shall never be modified.

---

## FR-031

Skills shall never be fabricated.

---

## FR-032

Resume bullets may be reordered.

---

## FR-033

Relevant accomplishments may be emphasized.

---

## FR-034

Job terminology may be incorporated only when factually accurate.

---

## FR-035

Original resumes shall remain unchanged.

---

## Application Preparation

---

## FR-036

Before beginning any application,

the system shall prepare:

Tailored Resume

Job Description

Candidate Context

CKB

Previous Answers

---

## FR-037

Claude shall determine which resume version is most appropriate.

---

## FR-038

Cover letters shall be generated only when requested.

---

## FR-039

Application packages shall be reusable.

---

# Browser Automation

---

## FR-040

The application shall launch a persistent browser.

---

## FR-041

Existing login sessions shall be reused.

---

## FR-042

The application shall support Chromium.

Additional browsers may be supported in future releases.

---

## FR-043

Navigation shall tolerate slow websites.

---

## FR-044

Retries shall occur after recoverable failures.

---

## FR-045

Browser screenshots shall be captured upon failure.

---

# Form Understanding

---

## FR-046

The application shall inspect:

Labels

Placeholder

ARIA labels

Nearby text

Validation

Required fields

---

## FR-047

Claude shall receive structured form context.

Claude shall not receive raw HTML alone.

---

## FR-048

Each field shall be classified before answering.

Examples:

Textbox

Dropdown

Checkbox

Radio

Autocomplete

Upload

Date Picker

Phone

Email

---

## FR-049

The application shall determine whether answers exist within:

CKB

Resume

Previous Answers

---

## FR-050

Claude shall answer only after all relevant context has been collected.

---

# Application Completion

---

## FR-051

The browser shall complete all supported form fields.

---

## FR-052

Resume uploads shall be automatic.

---

## FR-053

Cover letter uploads shall be automatic.

---

## FR-054

Multi-page workflows shall be supported.

---

## FR-055

Progress shall be saved after every page.

---

## FR-056

Recoverable failures shall resume from the last completed page.

---

# Submission

---

## FR-057

Users shall choose between:

Review Mode

Automatic Mode

---

## FR-058

In Automatic Mode,

the application shall submit immediately after successful validation.

---

## FR-059

In Review Mode,

the application shall pause before final submission.

---

## FR-060

Users may edit any generated answer before submission.

---

# Application History

---

## FR-061

The application shall maintain a local Excel or CSV file containing all submitted applications.

---

## FR-062

The tracker shall include:

Company

Job Title

Job ID

Application URL

Date Posted

Date Applied

Country

Resume Used

Status

Notes

---

## FR-063

Duplicate applications shall be prevented by checking:

Job ID

Application URL

Company + Title + Location

---

## FR-064

Users shall be able to open the tracker using Microsoft Excel, Google Sheets, or LibreOffice without requiring the application.

---

# Configuration

---

## FR-065

The user shall be able to configure:

Claude Model

Browser Mode

Automation Mode

Search Preferences

Resume Folder

CKB Folder

Tracker Location

---

## FR-066

All configuration shall be stored locally.

---

# Logging

---

## FR-067

Every significant action shall be logged.

---

## FR-068

Errors shall include screenshots whenever possible.

---

## FR-069

Logs shall never contain sensitive information unless explicitly enabled by the user.

---

# MVP Functional Requirements

The MVP must implement:

✓ Candidate Knowledge Base

✓ Resume Upload

✓ Job Discovery

✓ Job Ranking

✓ Resume Tailoring

✓ Browser Automation

✓ Form Completion

✓ Automatic Submission

✓ Review Mode

✓ Excel Tracker

Everything else should be considered future enhancement.
