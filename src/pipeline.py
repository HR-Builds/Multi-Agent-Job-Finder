from pathlib import Path

from src.tools.resume_reader import read_resume
from src.chains.analyzer import analyzer_chain
from src.agents.job_search_agent import job_search_agent
from src.agents.job_scraper_agent import job_scraper_agent
from src.chains.writer import writer_chain


def run_pipeline(resume_path: str) -> str:
    """
    Run the complete Resume → Job Matcher pipeline.

    Flow:
        Resume
        → Resume Reader
        → Analyzer
        → Job Search Agent
        → Job Scraper Agent
        → Writer
        → Final Report
    """

    # -----------------------------------------------------
    # Stage 1: Resume Reader
    # -----------------------------------------------------

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

    print("Resume extracted successfully.")


    # -----------------------------------------------------
    # Stage 2: Resume Analyzer
    # -----------------------------------------------------

    print("\n[2/5] Analyzing resume...")

    analyzer_result = analyzer_chain.invoke(
        {
            "resume": resume_text
        }
    )

    print("Resume analysis completed.")


    # -----------------------------------------------------
    # Stage 3: Job Search Agent
    # -----------------------------------------------------

    print("\n[3/5] Searching for relevant jobs...")

    candidate_profile = analyzer_result.get(
        "candidate_profile",
        {}
    )

    skills = analyzer_result.get(
        "skills",
        []
    )

    technologies = analyzer_result.get(
        "technologies",
        []
    )

    search_queries = analyzer_result.get(
        "search_queries",
        []
    )

    search_input = f"""
Find relevant job openings for this candidate.

Candidate Profile:
{candidate_profile}

Skills:
{skills}

Technologies:
{technologies}

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
- generic career pages

Return relevant job posting URLs and useful search result
information for further scraping.
"""

    search_result = job_search_agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": search_input
                }
            ]
        }
    )

    print("Job search completed.")


    # -----------------------------------------------------
    # Stage 4: Job Scraper Agent
    # -----------------------------------------------------

    print("\n[4/5] Scraping job pages...")

    scraper_input = f"""
Scrape and analyze the job posting URLs discovered by the
Job Search Agent.

Candidate Profile:
{candidate_profile}

Skills:
{skills}

Technologies:
{technologies}

Search Results:
{search_result["messages"][-1].content}

Use the scrape_url tool.

For every valid job posting, extract:

- job title
- company
- job description
- location
- employment type
- posting date
- URL

Do not fabricate any information.

If the actual posting date cannot be reliably determined,
return:

date not available
"""

    scraped_result = job_scraper_agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": scraper_input
                }
            ]
        }
    )

    print("Job scraping completed.")


    # -----------------------------------------------------
    # Stage 5: Writer
    # -----------------------------------------------------

    print("\n[5/5] Generating final job report...")

    final_report = writer_chain.invoke(
        {
            "candidate_profile": candidate_profile,
            "skills": skills,
            "technologies": technologies,
            "jobs": scraped_result["messages"][-1].content,
        }
    )

    print("Final report generated.")

    return final_report


if __name__ == "__main__":

    resume_path = "data/sample_resumes/resume.pdf"

    report = run_pipeline(resume_path)

    print("\n")
    print("=" * 70)
    print("FINAL JOB MATCHING REPORT")
    print("=" * 70)
    print("\n")

    print(report)