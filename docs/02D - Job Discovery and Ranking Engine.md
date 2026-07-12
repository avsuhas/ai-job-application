# 02D - Job Discovery and Ranking Engine

## LLM-Powered Autonomous Job Search & Application Platform

Version: 1.0

---

# Purpose

The Job Discovery and Ranking Engine is responsible for finding, analyzing, and prioritizing job opportunities before any application begins.

Its responsibilities include:

- Discovering jobs from company career websites.
- Extracting structured job information.
- Normalizing job data.
- Removing duplicates.
- Understanding each job description.
- Ranking jobs against the candidate.
- Producing a prioritized list of opportunities.

The engine should function independently of browser automation used later during applications.

---

# Design Goals

The engine should:

- Support hundreds of companies.
- Support multiple Applicant Tracking Systems (ATS).
- Support custom company websites.
- Produce consistent structured job objects.
- Avoid duplicate jobs.
- Rank jobs using semantic reasoning.
- Allow future plugin support.

---

# Two Discovery Modes

The engine supports two primary modes of operation.

---

# Mode 1 – User-Specified Career Websites

The user explicitly provides one or more company career websites.

Example:

Google Careers

Microsoft Careers

Amazon Jobs

NVIDIA Careers

Qualcomm Careers

Apple Careers

The engine searches only these websites.

---

## Inputs

Career URLs

Keywords

Countries

Locations

Departments

Remote Preference

Maximum Jobs

Date Filter

---

## Advantages

Precise.

Fast.

Predictable.

Ideal for users targeting specific companies.

---

# Mode 2 – Smart Company Discovery (Recommended)

The user provides:

Target Role

↓

Preferred Countries

↓

Optional Filters

The engine automatically searches every enabled company.

Example:

Target Role

Senior Backend Engineer

Countries

USA

The engine may search:

Google

Microsoft

Meta

Amazon

Netflix

Snowflake

Databricks

NVIDIA

Qualcomm

Apple

OpenAI

Anthropic

Stripe

Cloudflare

MongoDB

Uber

Airbnb

...

The user does not need to manually specify every company.

---

## Company Lists

Users may maintain reusable company lists.

Example:

FAANG.txt

AI.txt

Semiconductor.txt

Startups.txt

Fortune500.txt

The engine loads enabled lists automatically.

---

# Discovery Pipeline

The complete pipeline is:

Career Sources

↓

Crawler

↓

ATS Detection

↓

Job Extraction

↓

Normalization

↓

Deduplication

↓

Job Analysis

↓

Ranking

↓

Filtering

↓

Recommendations

↓

Final Results

---

# Supported Sources

The engine should support:

Company Career Websites

ATS Platforms

Saved Company Lists

Future plugins

---

# ATS Detection

Before extracting jobs, determine the platform.

Possible systems include:

Workday

Greenhouse

Lever

SmartRecruiters

Ashby

Oracle Recruiting

iCIMS

SuccessFactors

Taleo

Custom Websites

If detection fails,

use Generic Mode.

---

# Generic Mode

Generic Mode should operate using browser inspection.

Capabilities:

Extract job cards

Extract links

Extract metadata

Handle pagination

Handle infinite scroll

Handle search boxes

Handle filters

Handle lazy loading

This ensures unsupported websites remain usable.

---

# Job Extraction

Every discovered job should be normalized into a standard object.

Required fields:

Company

Job Title

Job ID

Location

Country

Department

Employment Type

Remote Status

Date Posted

Application URL

Job Description

Source Website

ATS Platform

---

Optional:

Salary

Recruiter

Travel %

Security Clearance

Visa Notes

---

# Job Object

Every discovered job becomes:

```json
{
  "company": "",

  "title": "",

  "job_id": "",

  "location": "",

  "country": "",

  "url": "",

  "description": "",

  "date_posted": "",

  "ats": "",

  "raw": {}

}
```

---

# Deduplication

Jobs should be compared using:

Job ID

↓

URL

↓

Company + Title + Location

↓

Description Similarity

↓

Semantic Similarity

Duplicate jobs should never appear twice.

---

# Date Handling

Every job should record:

Date Posted

Date Discovered

Date Updated

These values should remain separate.

---

# Job Analysis

Every discovered job should be analyzed by Claude.

Claude should identify:

Required Skills

Preferred Skills

Technologies

Programming Languages

Frameworks

Cloud Platforms

Education

Years of Experience

Leadership Requirements

Management Experience

Visa Requirements

Travel Requirements

Remote Status

Security Clearance

Domain

---

# Job Classification

Every job should receive categories.

Examples:

Backend

Frontend

Full Stack

Platform

Infrastructure

Cloud

ML

AI

Security

Networking

Embedded

Firmware

Data

DevOps

SRE

Management

Product

Research

Hardware

Semiconductor

These categories improve filtering.

---

# Skill Extraction

Claude should extract skills.

Example:

Python

FastAPI

Kafka

Redis

AWS

Docker

Kubernetes

Terraform

C++

Java

Go

Spark

PyTorch

CUDA

etc.

Required and Preferred skills should remain separate.

---

# Eligibility Analysis

Claude should identify hard requirements.

Examples:

US Citizen

Security Clearance

Bachelor's Degree

10+ Years

PhD

Visa Sponsorship Required

These affect ranking significantly.

---

# Job Ranking

Claude should compare:

Candidate Resume

↓

Candidate Knowledge Base

↓

Job Description

↓

User Preferences

↓

Rules

↓

Generate Match

---

# Ranking Factors

Suggested weights:

Required Skills

35%

Relevant Experience

20%

Preferred Skills

10%

Industry Experience

10%

Location Match

5%

User Preferences

10%

Growth Opportunity

5%

Resume Fit

5%

Weights should remain configurable.

---

# Match Score

Range

0–100

Suggested meanings:

95+

Apply Immediately

90+

Excellent Match

80+

Strong Match

70+

Good Match

60+

Possible Match

Below 60

Low Priority

Below 40

Ignore

---

# Recommendation

Every job should include:

Match Score

Recommendation

Summary

Reasons

Concerns

Missing Skills

Suggested Resume

Suggested Cover Letter

---

Example:

Match

92%

Recommendation

Strong Match

Reasons

Python

Distributed Systems

AWS

Backend

Leadership

Concerns

No Kafka experience

Suggested Resume

Backend.pdf

---

# Explainability

Every recommendation should explain itself.

Example:

This role is recommended because your backend distributed systems experience strongly matches the required qualifications. The only notable gap is Kafka, which is listed as preferred rather than required.

---

# Filtering

The user may filter results using:

Country

State

City

Remote

Hybrid

Company

Department

Salary

Date Posted

Date Discovered

ATS

Employment Type

Match Score

Visa

Keywords

Excluded Keywords

---

# Sorting

Supported sorting:

Match Score

Date Posted

Company

Country

Location

Title

Salary

Newest

Oldest

Alphabetical

---

# Smart Recommendations

The engine should identify opportunities beyond exact keyword matches.

Example:

Candidate searches:

Backend Engineer

The engine may also recommend:

Platform Engineer

Infrastructure Engineer

Distributed Systems Engineer

Cloud Engineer

Storage Engineer

because Claude understands semantic similarity.

---

# Job Collections

Users should be able to save collections.

Examples:

Favorites

Apply Later

Dream Companies

High Match

Needs Review

Already Applied

Rejected

Hidden

Collections should not affect ranking.

---

# Continuous Discovery (Future)

Optionally, the engine should periodically re-scan enabled companies.

Example:

Every 6 hours

Every 12 hours

Daily

Weekly

Only new jobs should be presented.

---

# Duplicate Prevention

Before recommending a job:

Check local application tracker.

If already applied:

Mark:

Already Applied

Hide by default.

Allow user override.

---

# Output

The engine returns:

RankedJob[]

Each RankedJob contains:

Job

Analysis

Match

Recommendation

Suggested Resume

Suggested Cover Letter

Reasoning

---

# Success Criteria

The Job Discovery and Ranking Engine is successful when:

- Relevant jobs are discovered reliably.
- Unsupported career websites still work using Generic Mode.
- Duplicate jobs are eliminated.
- Ranking reflects semantic understanding rather than keywords.
- Users spend time applying only to the highest-value opportunities.

---

# Future Enhancements

Future versions may include:

- Live job alerts
- Saved searches
- AI-powered company recommendations
- Salary benchmarking
- Recruiter likelihood scoring
- Referral availability detection
- Hiring trend analysis
- Historical posting frequency
- Company response rate analytics
- Integration with email notifications

---

# Summary

The Job Discovery and Ranking Engine is the intelligence layer responsible for transforming thousands of raw job postings into a concise, prioritized list of opportunities tailored to the candidate.

Its purpose is not merely to find jobs, but to help the candidate focus their effort on the opportunities with the highest probability of success.