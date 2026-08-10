# Resume → Job Matcher

An AI-powered multi-agent job discovery system that analyzes a
candidate's resume, generates optimized job-search queries, discovers
relevant job openings through Tavily, extracts job information from
public job pages, and presents the results in a structured format.

The system is designed around a resume-first workflow, meaning the user
does not need to provide a separate job description. Candidate skills,
experience, role, and search criteria are derived directly from the
uploaded resume.

---

## Overview

The Resume → Job Matcher follows a multi-stage pipeline:

Resume Upload
→ Resume Text Extraction
→ Resume Analysis
→ Search Query Generation
→ Web Job Search
→ Job Page Scraping
→ Job Data Processing
→ Final Job Results

The project uses Google Gemini for intelligent analysis and extraction,
Tavily for web search, and deterministic Python processing for result
normalization, deduplication, sorting, and filtering.

---

## Key Features

- Upload resumes in PDF or DOCX format
- Extract resume text automatically
- Analyze candidate experience and technical skills
- Identify the most suitable job role
- Generate optimized job-search queries
- Search the web using Tavily
- Discover real job posting URLs
- Scrape publicly accessible job pages
- Extract:
  - Job title
  - Company
  - Location
  - Employment type
  - Short job description
  - Posting date
  - Job URL
- Remove duplicate job postings
- Sort jobs by reliable posting date
- Handle unavailable posting dates safely
- Limit the number of jobs processed
- Prepare structured results for Streamlit
- Minimize unnecessary LLM token usage

---

## Architecture

```text
                         Resume
                           │
                           ▼
                 ┌──────────────────┐
                 │ Resume Reader    │
                 │ PDF / DOCX       │
                 └────────┬─────────┘
                          │
                          ▼
                 ┌──────────────────┐
                 │ Analyzer Chain   │
                 │ Google Gemini    │
                 └────────┬─────────┘
                          │
                  Candidate Profile
                  + Search Queries
                          │
                          ▼
                 ┌──────────────────┐
                 │ Job Search Agent │
                 │ Gemini + Tavily  │
                 └────────┬─────────┘
                          │
                       Job URLs
                          │
                          ▼
                 ┌──────────────────┐
                 │ Job Scraper      │
                 │ Agent            │
                 │ Gemini + Tool    │
                 └────────┬─────────┘
                          │
                   Structured Jobs
                          │
                          ▼
               ┌──────────────────────┐
               │ Job Result Processor │
               │ Python               │
               └──────────┬───────────┘
                          │
             ┌────────────┼────────────┐
             │            │            │
          Normalize   Deduplicate    Sort
             │            │            │
             └────────────┼────────────┘
                          │
                          ▼
                    Final Results
                          │
                          ▼
                    Streamlit UI



Project Structure


resume-job-matcher/
│
├── README.md
├── requirements.txt
├── requirements-dev.txt
├── .env
├── .env.example
├── .gitignore
│
├── data/
│   └── sample_resumes/
│
├── src/
│   └── resume_job_matcher/
│       │
│       ├── __init__.py
│       ├── config.py
│       ├── pipeline.py
│       │
│       ├── tools/
│       │   ├── __init__.py
│       │   ├── resume_reader.py
│       │   └── scrape_url.py
│       │
│       ├── chains/
│       │   ├── __init__.py
│       │   └── analyzer.py
│       │
│       ├── agents/
│       │   ├── __init__.py
│       │   ├── job_search_agent.py
│       │   └── job_scraper_agent.py
│       │
│       └── processors/
│           ├── __init__.py
│           └── job_result_processor.py
│
├── app.py
│
└── tests/
    ├── __init__.py
    └── tools/
        ├── __init__.py
        └── test_resume_reader.py