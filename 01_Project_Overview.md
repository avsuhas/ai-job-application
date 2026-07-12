# LLM-Powered Autonomous Job Search & Application Platform
## Product Requirements Document (PRD)

Version: 1.0

Status: Draft

Author: ChatGPT

Target Development Model:
Claude (Sonnet / Opus / Claude Code Compatible)

Target Platform:
Desktop Application (Local First)

---

# Table of Contents

1. Executive Summary
2. Product Vision
3. Problem Statement
4. Existing Solutions
5. Why This Product Exists
6. Product Philosophy
7. High Level Goals
8. Design Principles
9. User Personas
10. Scope
11. Out of Scope
12. Product Workflow
13. Success Metrics
14. MVP Definition
15. Long Term Vision

---

# Executive Summary

The purpose of this project is to build an intelligent desktop application that extends the capabilities of Large Language Models—specifically Claude—by enabling them to perform end-to-end job discovery and job application automation on real company career websites.

Current LLMs are excellent at reasoning, understanding resumes, tailoring content, and answering application questions. However, they cannot independently browse arbitrary career portals, navigate applicant tracking systems (ATS), interact with dynamic web forms, upload resumes, or complete online job applications in a reliable and repeatable manner.

This application fills that gap.

Rather than replacing Claude or building another language model, this software acts as an orchestration and automation layer around Claude. Claude remains responsible for understanding, reasoning, and decision-making, while the application performs browser automation, workflow orchestration, local file management, application tracking, and interaction with external systems.

The result is an AI-assisted job search platform capable of discovering relevant opportunities, ranking them intelligently, tailoring application materials, completing online applications, and maintaining a complete history of submitted jobs—all while keeping the user's data local and under their control.

---

# Product Vision

Create the world's most capable AI-powered job search and application assistant that combines the reasoning abilities of Claude with deterministic browser automation.

The application should feel like an experienced executive recruiter and personal career assistant working alongside the user.

The platform should allow a user to:

- Discover jobs across multiple company career websites.
- Find opportunities that best match their skills and preferences.
- Tailor resumes and application materials for each role.
- Automatically complete application forms.
- Track submitted applications.
- Reuse applicant information intelligently.
- Eliminate repetitive manual data entry.
- Allow the user to remain in control of every submission.

The application should dramatically reduce the time required to apply for high-quality positions while improving application quality and consistency.

---

# Problem Statement

Job applications today involve a significant amount of repetitive manual work.

A candidate typically performs the following tasks repeatedly:

- Searching company websites
- Filtering jobs manually
- Reading job descriptions
- Comparing qualifications
- Uploading resumes
- Entering identical personal information
- Re-entering employment history
- Re-entering education history
- Completing questionnaires
- Answering screening questions
- Uploading resumes again
- Uploading cover letters
- Checking boxes
- Selecting dropdown values
- Confirming work authorization
- Providing sponsorship information
- Reviewing before submission

For active job seekers applying to dozens or hundreds of positions, this process becomes tedious, inconsistent, and time-consuming.

Existing language models can assist with writing and reasoning but cannot reliably complete the end-to-end workflow.

This creates a gap between AI capabilities and real-world job application processes.

This project aims to bridge that gap.

---

# Existing Solutions

Several tools attempt to automate portions of the hiring process.

These include:

- LinkedIn Easy Apply
- Simplify
- LazyApply
- Sonara
- Massive
- Teal
- Huntr
- Autofill browser extensions
- Browser password managers

These tools primarily rely on static field mapping, keyword matching, or simple form autofill.

While useful, they generally lack:

- Deep semantic understanding of resumes
- Intelligent job ranking
- Dynamic form reasoning
- Resume tailoring
- Company-specific adaptation
- Multi-step decision making
- Context-aware screening question generation

Large Language Models solve the reasoning problem.

Browser automation solves the interaction problem.

This application combines both.

---

# Why This Product Exists

Claude is already exceptional at:

- Understanding resumes
- Understanding job descriptions
- Comparing qualifications
- Tailoring resumes
- Writing cover letters
- Answering application questions
- Explaining reasoning

However, Claude cannot directly:

- Visit arbitrary career websites
- Browse job listings
- Navigate ATS systems
- Click buttons
- Upload files
- Submit applications
- Maintain application history
- Track browser state
- Manage browser sessions

The purpose of this application is to provide these missing capabilities.

Claude remains the intelligence.

The application becomes the execution engine.

---

# Product Philosophy

This project follows one simple philosophy:

> "Never reinvent Claude."

The application should never attempt to duplicate reasoning already performed exceptionally well by Claude.

Instead, it should focus exclusively on capabilities outside the scope of an LLM.

Claude should answer questions.

Claude should analyze resumes.

Claude should rank jobs.

Claude should determine the best response.

The application should:

- Browse websites
- Manage browser sessions
- Interact with forms
- Store local files
- Coordinate workflows
- Upload resumes
- Track applications
- Handle retries
- Recover from failures

This separation keeps the system modular, maintainable, and future-proof.

---

# High-Level Goals

The application should:

1. Discover jobs from company career websites.
2. Analyze each job using Claude.
3. Rank jobs by suitability.
4. Allow filtering and sorting.
5. Tailor resumes for each application.
6. Generate job-specific responses.
7. Fill online application forms.
8. Upload required documents.
9. Submit applications.
10. Maintain a complete application history.
11. Avoid duplicate applications.
12. Operate entirely on the user's local machine by default.
13. Support multiple Claude models.
14. Remain modular enough to support additional LLM providers in the future.

---

# Design Principles

## 1. Local First

The user's personal information belongs to the user.

Applicant data should remain on the local computer whenever possible.

The application should not require cloud storage.

---

## 2. Claude First

Claude performs all reasoning.

The application performs all execution.

---

## 3. User Control

The user should always control:

- Search criteria
- Resume selection
- Applicant information
- Submission preferences
- Automation settings
- Review mode

---

## 4. Reusable Knowledge

Rather than asking users to repeatedly enter identical information, the application should maintain a **Local Applicant Knowledge Base** on the user's computer.

This repository serves as the authoritative source for completing applications and may consist of JSON, Markdown, plain text, YAML, or other supported file formats. It should contain all information commonly requested during job applications, including personal details, employment history, education, work authorization, salary expectations, screening responses, demographic information (if the user chooses to store it), and any other reusable information.

Claude should consult this repository first, followed by the uploaded resume and any user-provided instructions, when determining answers to application questions.

---

## 5. Transparency

Every automated decision should be explainable.

The application should show:

- Why a job was recommended.
- Why an answer was selected.
- Where the information came from.
- Whether Claude inferred anything.

---

## 6. Extensibility

Every subsystem should be replaceable.

For example:

Resume Parser

↓

Different implementation

Browser Automation

↓

Different framework

LLM

↓

Different provider

Storage

↓

Different backend

without affecting the remainder of the application.

---

# User Personas

## Persona 1

Senior Software Engineer

Applies to:

- Google
- Microsoft
- Meta
- Amazon

Needs:

- Resume tailoring
- High-quality applications
- Workday automation

---

## Persona 2

New Graduate

Applies to:

100+

Entry-level jobs

Needs:

- Large-scale automation

---

## Persona 3

Experienced Professional

Applies selectively.

Needs:

- High application quality.

---

## Persona 4

International Applicant

Needs:

- Visa-aware filtering
- Sponsorship detection
- Country filtering

---

# Product Workflow

The application should guide users through the following high-level workflow:

1. Configure a Local Applicant Knowledge Base that contains reusable information for completing applications.
2. Upload one or more resumes.
3. Specify job search preferences such as companies, roles, countries, locations, keywords, and other filters.
4. Discover jobs from company career websites.
5. Analyze and rank jobs using Claude.
6. Present a sortable and filterable list of matching jobs.
7. Allow the user to select one or more jobs.
8. Prepare application materials, including resume tailoring when appropriate.
9. Open the selected application in the browser and complete the required forms.
10. Submit applications automatically or pause for optional user review, depending on the configured automation mode.
11. Record every submitted application in a local Excel (or CSV) tracker to prevent duplicate submissions and maintain a complete application history.

---

# Success Metrics

The platform should aim to achieve:

- Significant reduction in manual application time.
- High accuracy when mapping applicant information to application forms.
- Consistent use of stored applicant information across applications.
- Intelligent job ranking aligned with user preferences and qualifications.
- Reliable browser automation with graceful recovery from common failures.
- Clear auditability of submitted applications.

---

# MVP Definition

The first release should focus on a practical, local-first workflow.

The MVP should include:

- Local Applicant Knowledge Base.
- Resume upload and parsing.
- Company career website search.
- Job extraction.
- Claude-based job ranking.
- Country and keyword filtering.
- Batch job selection.
- Resume tailoring.
- Browser automation using Playwright.
- Automated form completion.
- Optional review before submission.
- Local Excel/CSV application tracker.

The MVP should intentionally avoid unnecessary infrastructure such as cloud databases, user authentication, distributed services, or remote storage.

---

# Long-Term Vision

The long-term vision is to evolve this application into a modular AI career platform capable of supporting additional workflows beyond job applications.

Future capabilities may include:

- Multi-provider LLM support.
- Additional ATS adapters.
- Resume optimization analytics.
- Interview preparation.
- Referral tracking.
- Recruiter outreach assistance.
- Cover letter libraries.
- Networking automation.
- Application analytics and dashboards.
- Plugin ecosystem.
- Model Context Protocol (MCP) integrations for external tools and services.

The guiding principle should remain unchanged:

Claude provides the intelligence.

The application provides the execution.

Together, they create an efficient, transparent, and extensible AI-powered job application assistant.