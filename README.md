    # Project Spec: Resume → Job Matcher (Multi-agent)

    ## Overview
    An extension of the existing Multi-Agent Research System pattern. The user uploads
    their resume, and the system autonomously analyzes it, searches the web for matching
    job openings, and returns a sorted list of relevant, recent postings.

    ## Input
    - A single resume file (PDF or DOCX)
    - No separate job description is required — keywords are derived entirely from the resume

    ## Pipeline

    | Stage | Component | Type | Purpose |
    |---|---|---|---|
    | 1 | Resume Reader | New tool | Extracts plain text from the uploaded PDF/DOCX resume |
    | 2 | Analyzer | LCEL chain (no tool) | Reads resume text, identifies skills/experience/role, generates search keywords |
    | 3 | Job Search Agent | ReAct agent (Tavily `web_search` tool) | Searches the web for job listings using the generated keywords |
    | 4 | Job Scraper Agent | ReAct agent (`scrape_url` tool, reused) | Scrapes job pages for title, company, description, and posting date |
    | 5 | Writer | LCEL chain | Compiles all found jobs into a report, sorted by posting date (newest first) |

    **Full flow:**
    Resume upload → text extraction → keyword generation → job search → job page scraping →
    sorted job list with dates → presented to user

    ## Component Count
    - **1 new tool:** Resume reader (PDF/DOCX parser)
    - **2 reused tools:** `web_search`, `scrape_url`
    - **2 agents:** Job Search Agent, Job Scraper Agent
    - **2 LCEL chains:** Analyzer chain, Writer chain

    ## Design Decisions (confirmed)
    - **Input scope:** Resume only — no target job description input from the user
    - **Search source:** General web search (Tavily), not a dedicated jobs API (e.g. LinkedIn/Indeed)

    ## Known Limitation
    Because job search relies on general web search rather than a dedicated jobs API,
    **posting dates will not always be reliable**. Many job pages don't clearly state a
    posting date, or show a "last modified" date instead of the actual post date.

    **Mitigation:** The writer chain must be explicitly instructed to output "date not
    available" or "recently posted" when no reliable date is found — it must never
    fabricate a date.

    ## Next Steps
    Build stage-by-stage, in this order:
    1. Resume reader tool
    2. Analyzer chain
    3. Job search agent
    4. Job scraper agent
    5. Writer chain
    6. Wire the full pipeline together (mirroring `pipeline.py` from the original research system)


    resume-job-matcher/
    ├── README.md
    ├── requirements.txt
    ├── requirements-dev.txt
    ├── .env.example
    ├── .gitignore
    ├── src/
    │   └── resume_job_matcher/
    │       ├── __init__.py
    │       ├── config.py
    │       ├── tools/
    │       │   ├── __init__.py
    │       │   └── resume_reader.py      ← Stage 1 (ready)
    │       ├── chains/
    │       │   └── __init__.py            ← Stage 2 & 5 yahan aayengi
    │       └── agents/
    │           └── __init__.py            ← Stage 3 & 4 yahan aayengi
    ├── tests/
    │   ├── __init__.py
    │   └── tools/
    │       ├── __init__.py
    │       └── test_resume_reader.py
    └── data/
        └── sample_resumes/
