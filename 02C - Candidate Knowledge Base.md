# 02C - Candidate Knowledge Base (CKB)

## LLM-Powered Autonomous Job Search & Application Platform

Version: 1.0

---

# Purpose

The Candidate Knowledge Base (CKB) is the central repository of all reusable information about the candidate.

Rather than repeatedly asking the user for information during every application, the system maintains a local collection of files containing everything Claude needs to complete job applications accurately.

The Candidate Knowledge Base serves as the single source of truth for all candidate-specific information.

The browser automation layer should never hardcode answers.

Instead, every answer should originate from:

1. Candidate Knowledge Base
2. Resume
3. User Instructions

Claude should use reasoning to determine the best answer, but it must never invent factual information.

---

# Design Principles

The CKB should satisfy the following principles.

## Local First

All files remain on the user's computer.

No cloud storage is required.

---

## Human Readable

Users should be able to open and edit every file using any text editor.

Avoid proprietary formats whenever possible.

---

## Flexible

The system should not require one rigid JSON schema.

Claude is capable of understanding multiple document types.

The CKB should support:

- JSON
- Markdown
- Plain Text
- YAML
- PDF
- DOCX

---

## Modular

Separate information into logical files.

Do not create one enormous JSON file.

Smaller files are easier to maintain.

---

## User Owned

The application never owns the data.

The user owns the files.

The application simply reads them.

---

# Folder Structure

Recommended layout:

```text
candidate/

    resume/

        Backend.pdf

        Platform.pdf

        ML.pdf

        General.pdf

    profile/

        candidate.json

        preferences.md

        rules.md

        answers.md

        notes.md

    documents/

        cover_letter_template.md

        certifications.pdf

        transcript.pdf

        portfolio.pdf

    generated/

        resumes/

        cover_letters/

        answers/

```

Everything inside this folder is considered part of the Candidate Knowledge Base.

---

# Candidate JSON

candidate.json stores structured information that is commonly requested in online applications.

Example:

```json
{
  "personal": {
    "first_name": "",
    "last_name": "",
    "email": "",
    "phone": "",
    "address": "",
    "city": "",
    "state": "",
    "country": "",
    "postal_code": ""
  },

  "employment": {

    "current_company": "",

    "current_title": "",

    "years_of_experience": 0

  },

  "work_authorization": {

    "authorized_to_work": true,

    "requires_sponsorship": false,

    "visa_status": "H1B"

  },

  "education": {

    "highest_degree": "",

    "university": ""

  }

}
```

This file should contain only structured facts.

Do not store long explanations.

---

# preferences.md

Contains search preferences.

Example:

```text
Preferred Countries

United States

Canada

Preferred Roles

Backend Engineer

Platform Engineer

Infrastructure Engineer

Distributed Systems Engineer

Preferred Industries

Cloud

AI

Semiconductor

Remote

Yes

Maximum Travel

15%

Preferred Salary

220000+

```

Claude should use this file while ranking jobs.

---

# rules.md

Defines permanent behavioral rules.

Example:

```text
Never apply to contract jobs.

Never apply outside North America.

Always prefer Backend roles.

Always use Backend.pdf unless another resume scores significantly better.

Never answer salary questions with "Negotiable."

Always answer sponsorship truthfully.

Do not apply to internships.

Skip jobs requiring more than 30% travel.
```

This file overrides preferences.

---

# answers.md

Contains reusable answers.

Example:

```text
## Why do you want to work here?

I enjoy building highly scalable distributed systems...

---

## Tell us about yourself

Software Engineer with eight years...

---

## Why are you leaving your current company?

...

---

## Strengths

...

---

## Weaknesses

...

```

Claude may adapt these answers.

Claude should preserve factual accuracy.

---

# notes.md

Optional.

Contains free-form notes.

Example:

```text
I recently completed Kubernetes certification.

I have significant mentoring experience.

I enjoy platform engineering.

Interested in AI infrastructure.
```

Claude may use these notes if relevant.

---

# Resume Folder

Users may maintain multiple resumes.

Example:

```text
resume/

Backend.pdf

Platform.pdf

Infrastructure.pdf

General.pdf

```

Claude should choose the most appropriate resume.

---

# Resume Selection

Resume selection occurs before tailoring.

Example logic:

Backend Job

↓

Backend.pdf

Platform Job

↓

Platform.pdf

ML Job

↓

ML.pdf

Unknown

↓

General.pdf

The chosen resume becomes the base resume.

---

# Resume Tailoring

Claude may generate a tailored version.

Example:

Backend.pdf

↓

Backend_Google.pdf

↓

Backend_Microsoft.pdf

↓

Backend_Amazon.pdf

Original resumes must never be modified.

Generated resumes belong under

generated/resumes/

---

# Cover Letters

Generated cover letters belong under

generated/cover_letters/

The original template remains unchanged.

---

# Generated Answers

Application-specific answers belong under

generated/answers/

Example:

Google_2026-07-01.md

Microsoft_2026-07-04.md

---

# Answer Priority

Whenever Claude answers an application question it should follow this order.

Priority 1

candidate.json

↓

Priority 2

rules.md

↓

Priority 3

answers.md

↓

Priority 4

preferences.md

↓

Priority 5

resume

↓

Priority 6

notes.md

↓

Priority 7

Reasoning

Claude should never skip higher-priority sources.

---

# Candidate Knowledge Loading

Before any reasoning begins:

Load candidate.json

↓

Load rules.md

↓

Load preferences.md

↓

Load answers.md

↓

Load notes.md

↓

Load selected resume

↓

Create unified context

↓

Send to Claude

The browser automation layer never decides answers.

Claude always reasons over the unified context.

---

# Updating the Knowledge Base

The application may suggest updates.

Example:

A new answer performed well.

↓

Prompt the user

↓

"Would you like to save this answer for future applications?"

↓

If approved

↓

Append to answers.md

The application should never modify user files automatically.

User approval is required.

---

# Version History

Generated files should include timestamps.

Example:

generated/

resume/

Backend_Google_20260701.pdf

Backend_Meta_20260705.pdf

This allows users to inspect historical resumes.

---

# Sensitive Information

The CKB may contain:

Address

Phone

Email

Visa Status

Salary

Demographic Responses

Social Links

These files remain local.

The application should never transmit unrelated information to Claude.

Only information necessary for the current task should be included in the prompt context.

---

# Validation

The application should verify:

Required files exist.

JSON syntax is valid.

Resume files exist.

Generated folders exist.

Missing information should produce warnings rather than failures.

---

# User Editing

Users should never need to edit code.

Everything should be editable through:

VS Code

Notepad

TextEdit

Any Markdown editor

Any JSON editor

---

# Future Expansion

The CKB should support additional documents without code changes.

Examples:

languages.md

publications.md

patents.md

security_clearance.md

immigration.md

conference_talks.md

awards.md

recommendations.md

The loading engine should automatically include supported files.

---

# Summary

The Candidate Knowledge Base is the authoritative source of truth for all reusable candidate information.

It is:

- Local
- Human-readable
- Flexible
- Extensible
- User-controlled

Claude should always reason from the Candidate Knowledge Base before generating answers, ensuring consistency, accuracy, and reuse across every job application.