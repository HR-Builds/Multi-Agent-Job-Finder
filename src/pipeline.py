import json
from typing import Any

from src.tools.resume_reader import read_resume
from src.chains.analyzer import analyzer_chain
from src.agents.job_search_agent import job_search_agent
from src.agents.job_scraper_agent import job_scraper_agent
from src.processors.job_result_processor import (
    process_jobs,
    get_job_statistics,
)


def _extract_agent_content(agent_result: dict) -> str:
    """
    Extract the final text response from a LangGraph agent result.
    """

    messages = agent_result.get("messages", [])

    if not messages:
        return ""

    return messages[-1].content

def _parse_scraped_jobs(content) -> list[dict]:
    """
    Normalize the scraper agent output into a list of job dictionaries.

    The scraper may return:
    - a Python list
    - a JSON string
    - a Markdown JSON code block
    - a LangChain structured content list
    """

    # -------------------------------------------------
    # Case 1: Already a Python list
    # -------------------------------------------------

    if isinstance(content, list):

        # Some LangChain/Gemini responses may return
        # structured content like:
        #
        # [{"type": "text", "text": "..."}]

        if all(isinstance(item, dict) for item in content):

            # Normal job list
            if all(
                "title" in item
                or "company" in item
                or "url" in item
                for item in content
            ):
                return content

            # LangChain structured text content
            text_parts = []

            for item in content:

                if item.get("type") == "text":
                    text_parts.append(
                        item.get("text", "")
                    )

            if text_parts:
                content = "\n".join(text_parts)

            else:
                raise ValueError(
                    "Scraper returned an unsupported list structure."
                )

        else:
            raise ValueError(
                "Scraper returned an unsupported list format."
            )

    # -------------------------------------------------
    # Case 2: Convert content to string
    # -------------------------------------------------

    if not isinstance(content, str):

        raise ValueError(
            f"Unsupported scraper output type: "
            f"{type(content).__name__}"
        )

    content = content.strip()

    if not content:
        return []

    # -------------------------------------------------
    # Remove Markdown JSON code fences
    # -------------------------------------------------

    if content.startswith("```"):

        lines = content.splitlines()

        # Remove ```json / ```
        if lines:
            lines = lines[1:]

        # Remove closing ```
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]

        content = "\n".join(lines).strip()

    # -------------------------------------------------
    # Parse JSON
    # -------------------------------------------------

    try:

        jobs = json.loads(content)

    except json.JSONDecodeError as exc:

        print("\nSCRAPER RAW OUTPUT:")
        print(content)

        raise ValueError(
            "Job Scraper Agent did not return valid JSON."
        ) from exc

    # -------------------------------------------------
    # Validate final structure
    # -------------------------------------------------

    if not isinstance(jobs, list):

        raise ValueError(
            "Job Scraper Agent output must be a JSON list."
        )

    return jobs


def run_pipeline(
    resume_path: str,
    max_jobs: int = 20,
) -> dict[str, Any]:
    """
    Run the complete Resume → Job Matcher pipeline.

    Pipeline:

        Resume
        ↓
        Resume Reader
        ↓
        Analyzer Chain
        ↓
        Job Search Agent
        ↓
        Job Scraper Agent
        ↓
        Python Result Processor
        ↓
        Final Job Results
    """

    # =====================================================
    # Stage 1: Resume Reader
    # =====================================================

    print("\n[1/5] Reading resume...")

    resume_text = read_resume.invoke(
        {
            "file_path": resume_path
        }
    )

    if not resume_text.strip():
        raise ValueError(
            "Resume reader returned empty text."
        )

    print("✓ Resume extracted successfully.")


    # =====================================================
    # Stage 2: Resume Analyzer
    # =====================================================

    print("\n[2/5] Analyzing resume...")

    analyzer_result = analyzer_chain.invoke(
        {
            "resume": resume_text
        }
    )

    if not isinstance(analyzer_result, dict):
        raise ValueError(
            "Analyzer did not return a valid JSON object."
        )

    role = analyzer_result.get(
        "role",
        "",
    )

    experience_level = analyzer_result.get(
        "experience_level",
        "",
    )

    location = analyzer_result.get(
        "location",
        "",
    )

    skills = analyzer_result.get(
        "skills",
        [],
    )

    search_queries = analyzer_result.get(
        "search_queries",
        [],
    )

    print("✓ Resume analysis completed.")

    print(f"  Role: {role}")
    print(f"  Experience: {experience_level}")
    print(f"  Location: {location}")
    print(f"  Search queries: {len(search_queries)}")


    # =====================================================
    # Stage 3: Job Search Agent
    # =====================================================

    print("\n[3/5] Searching for relevant jobs...")

    search_input = f"""
Find real and relevant job openings for this candidate.

Candidate Role:
{role}

Experience Level:
{experience_level}

Location:
{location}

Skills:
{skills}

Recommended Search Queries:
{search_queries}

Use Tavily to search the web.

Find actual job postings only.

Avoid:
- blogs
- tutorials
- courses
- documentation
- GitHub repositories
- news articles
- generic career pages

Return unique job posting URLs and short search-result
snippets.

Do not fabricate job information.
"""

    search_result = job_search_agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": search_input,
                }
            ]
        }
    )

    search_content = _extract_agent_content(
        search_result
    )

    if not search_content:
        raise ValueError(
            "Job Search Agent returned no results."
        )

    print("✓ Job search completed.")


    # =====================================================
    # Stage 4: Job Scraper Agent
    # =====================================================

    print("\n[4/5] Scraping job pages...")

    scraper_input = f"""
Extract structured information from the job posting
results below.

Search Results:
{search_content}

Use the scrape_url tool to inspect the actual job pages.

Return ONLY a valid JSON array.

For every valid job posting return:

{{
    "title": "",
    "company": "",
    "location": "",
    "employment_type": "",
    "description": "",
    "posting_date": "",
    "url": ""
}}

Rules:

- Extract information only from the actual job page.
- Keep description between 50 and 100 words.
- Do not copy the entire job description.
- Do not invent information.
- Do not guess dates.
- If the actual posting date cannot be verified, use:
  "date not available"
- Remove duplicate URLs.
- Ignore pages that are not actual job postings.
- Preserve the actual job URL.
"""

    scraped_result = job_scraper_agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": scraper_input,
                }
            ]
        }
    )

    scraped_content = _extract_agent_content(
        scraped_result
    )

    scraped_jobs = _parse_scraped_jobs(
        scraped_content
    )

    print(
        f"✓ Scraping completed. "
        f"Jobs extracted: {len(scraped_jobs)}"
    )


    # =====================================================
    # Stage 5: Python Result Processor
    # =====================================================

    print("\n[5/5] Processing job results...")

    final_jobs = process_jobs(
        scraped_jobs,
        max_jobs=max_jobs,
    )

    statistics = get_job_statistics(
        final_jobs
    )

    print("✓ Job processing completed.")

    print(
        f"  Final jobs: "
        f"{statistics['total_jobs']}"
    )

    print(
        f"  Jobs with dates: "
        f"{statistics['jobs_with_date']}"
    )

    print(
        f"  Jobs without dates: "
        f"{statistics['jobs_without_date']}"
    )

    print(
        f"  Unique companies: "
        f"{statistics['unique_companies']}"
    )


    # =====================================================
    # Final Result
    # =====================================================

    return {
        "candidate": {
            "role": role,
            "experience_level": experience_level,
            "location": location,
            "skills": skills,
            "search_queries": search_queries,
        },
        "jobs": final_jobs,
        "statistics": statistics,
    }




if __name__ == "__main__":

    resume_path = "data/sample_resumes/resume.pdf"

    result = run_pipeline(
        resume_path=resume_path,
        max_jobs=10,
    )

    print("\n")
    print("=" * 70)
    print("FINAL JOB MATCHING RESULTS")
    print("=" * 70)

    print("\nCandidate:")
    print(result["candidate"])

    print("\nStatistics:")
    print(result["statistics"])

    print("\nJobs:")

    for index, job in enumerate(
        result["jobs"],
        start=1,
    ):

        print("\n" + "-" * 70)

        print(
            f"{index}. {job['title']}"
        )

        print(
            f"Company: {job['company']}"
        )

        print(
            f"Location: {job['location']}"
        )

        print(
            f"Employment: {job['employment_type']}"
        )

        print(
            f"Posting Date: {job['posting_date']}"
        )

        print(
            f"Description: {job['description']}"
        )

        print(
            f"URL: {job['url']}"
        )