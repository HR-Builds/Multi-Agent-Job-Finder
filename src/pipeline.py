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


# =========================================================
# AGENT OUTPUT HELPER
# =========================================================

def _extract_agent_content(
    agent_result: dict,
) -> str:

    messages = agent_result.get(
        "messages",
        []
    )

    if not messages:
        return ""

    content = messages[-1].content

    if isinstance(
        content,
        str,
    ):
        return content

    if isinstance(
        content,
        list,
    ):

        parts = []

        for item in content:

            if (
                isinstance(item, dict)
                and item.get("type") == "text"
            ):

                parts.append(
                    item.get(
                        "text",
                        ""
                    )
                )

        return "\n".join(
            parts
        )

    return str(content)


# =========================================================
# SCRAPER JSON PARSER
# =========================================================

def _parse_scraped_jobs(
    content,
) -> list[dict]:

    if isinstance(
        content,
        list,
    ):

        if all(
            isinstance(
                item,
                dict,
            )
            for item in content
        ):

            return content

        text_parts = []

        for item in content:

            if (
                isinstance(item, dict)
                and item.get("type") == "text"
            ):

                text_parts.append(
                    item.get(
                        "text",
                        ""
                    )
                )

        content = "\n".join(
            text_parts
        )

    if not isinstance(
        content,
        str,
    ):

        raise ValueError(
            "Unsupported scraper output type: "
            f"{type(content).__name__}"
        )

    content = content.strip()

    if not content:
        return []

    # -----------------------------------------------------
    # Remove markdown code fences
    # -----------------------------------------------------

    if content.startswith(
        "```"
    ):

        lines = content.splitlines()

        if lines:
            lines = lines[1:]

        if (
            lines
            and lines[-1].strip()
            == "```"
        ):

            lines = lines[:-1]

        content = "\n".join(
            lines
        ).strip()

    # -----------------------------------------------------
    # Parse JSON
    # -----------------------------------------------------

    try:

        jobs = json.loads(
            content
        )

    except json.JSONDecodeError as exc:

        print(
            "\nSCRAPER RAW OUTPUT:"
        )

        print(
            content
        )

        raise ValueError(
            "Job Scraper Agent did not "
            "return valid JSON."
        ) from exc

    if not isinstance(
        jobs,
        list,
    ):

        raise ValueError(
            "Scraper output must be "
            "a JSON array."
        )

    return jobs


# =========================================================
# MANUAL CANDIDATE
# =========================================================

def _build_manual_candidate(
    role: str,
    skills: list[str],
    location: str = "",
    experience_level: str = "",
    employment_type: str = "",
) -> dict:

    clean_skills = [
        str(skill).strip()
        for skill in skills
        if str(skill).strip()
    ]

    return {
        "role": role.strip(),
        "experience_level": (
            experience_level.strip()
        ),
        "location": location.strip(),
        "skills": clean_skills[:5],
        "search_queries": [],
        "employment_type": (
            employment_type.strip()
        ),
    }


# =========================================================
# SEARCH QUERY BUILDER
# =========================================================

def _build_search_queries(
    role: str,
    skills: list[str],
    location: str = "",
    employment_type: str = "",
) -> list[str]:

    queries = []

    role = role.strip()
    location = location.strip()
    employment_type = (
        employment_type.strip()
    )

    if not role:
        return []

    # -----------------------------------------------------
    # Primary role
    # -----------------------------------------------------

    query = f'"{role}" jobs'

    if location:
        query += f' "{location}"'

    if employment_type:
        query += f' "{employment_type}"'

    queries.append(
        query
    )

    # -----------------------------------------------------
    # Role + important skills
    # -----------------------------------------------------

    skill_query = ""

    if skills:

        selected_skills = [
            str(skill).strip()
            for skill in skills[:3]
            if str(skill).strip()
        ]

        if selected_skills:

            skill_query = (
                " ".join(
                    selected_skills
                )
            )

    if skill_query:

        query = (
            f'"{role}" '
            f'{skill_query} jobs'
        )

        if location:
            query += f' "{location}"'

        queries.append(
            query
        )

    # -----------------------------------------------------
    # Pakistan / location search
    # -----------------------------------------------------

    if location:

        queries.append(
            f'"{role}" jobs '
            f'in {location}'
        )

    else:

        queries.append(
            f'"{role}" jobs Pakistan'
        )

    # -----------------------------------------------------
    # Job platforms
    # -----------------------------------------------------

    platform_query = (
        f'"{role}" jobs '
        f'(site:linkedin.com/jobs '
        f'OR site:indeed.com '
        f'OR site:wellfound.com '
        f'OR site:greenhouse.io '
        f'OR site:lever.co)'
    )

    if location:
        platform_query += (
            f' "{location}"'
        )

    queries.append(
        platform_query
    )

    # -----------------------------------------------------
    # Remove duplicates
    # -----------------------------------------------------

    unique_queries = []

    seen = set()

    for query in queries:

        query = query.strip()

        normalized = query.lower()

        if not query:
            continue

        if normalized in seen:
            continue

        seen.add(
            normalized
        )

        unique_queries.append(
            query
        )

    # Maximum 4
    return unique_queries[:4]


# =========================================================
# MAIN PIPELINE
# =========================================================

def run_pipeline(
    resume_path: str | None = None,
    max_jobs: int = 10,

    role: str | None = None,
    skills: list[str] | None = None,
    location: str = "",
    experience_level: str = "",
    employment_type: str = "",

    search_mode: str = "resume",
) -> dict[str, Any]:

    search_mode = (
        search_mode.lower().strip()
    )

    if search_mode not in {
        "resume",
        "manual",
    }:

        raise ValueError(
            "search_mode must be "
            "'resume' or 'manual'."
        )

    # =====================================================
    # 1. CANDIDATE PROFILE
    # =====================================================

    if search_mode == "resume":

        if not resume_path:

            raise ValueError(
                "Resume file is required."
            )

        print(
            "\n[1/5] Reading resume..."
        )

        resume_text = read_resume.invoke(
            {
                "file_path": resume_path
            }
        )

        if not isinstance(
            resume_text,
            str,
        ):

            resume_text = str(
                resume_text
            )

        if not resume_text.strip():

            raise ValueError(
                "Resume reader returned "
                "empty text."
            )

        print(
            "✓ Resume extracted."
        )

        # -------------------------------------------------
        # Resume analysis
        # -------------------------------------------------

        print(
            "\n[2/5] Analyzing resume..."
        )

        analyzer_result = (
            analyzer_chain.invoke(
                {
                    "resume": resume_text
                }
            )
        )

        if not isinstance(
            analyzer_result,
            dict,
        ):

            raise ValueError(
                "Analyzer returned "
                "invalid data."
            )

        candidate = {
            "role": str(
                analyzer_result.get(
                    "role",
                    ""
                )
            ).strip(),

            "experience_level": str(
                analyzer_result.get(
                    "experience_level",
                    ""
                )
            ).strip(),

            "location": str(
                analyzer_result.get(
                    "location",
                    ""
                )
            ).strip(),

            "skills": analyzer_result.get(
                "skills",
                []
            ),

            "search_queries": analyzer_result.get(
                "search_queries",
                []
            ),

            "employment_type": "",
        }

        print(
            "✓ Resume analysis completed."
        )

    else:

        print(
            "\n[1/5] Building manual profile..."
        )

        if not role:

            raise ValueError(
                "Target role is required."
            )

        candidate = (
            _build_manual_candidate(
                role=role,
                skills=skills or [],
                location=location,
                experience_level=(
                    experience_level
                ),
                employment_type=(
                    employment_type
                ),
            )
        )

        print(
            "✓ Manual profile created."
        )

        print(
            "✓ AI resume analysis skipped."
        )

    # =====================================================
    # NORMALIZE CANDIDATE
    # =====================================================

    candidate_role = str(
        candidate.get(
            "role",
            ""
        )
    ).strip()

    candidate_skills = candidate.get(
        "skills",
        []
    )

    if not isinstance(
        candidate_skills,
        list,
    ):

        candidate_skills = [
            str(candidate_skills)
        ]

    candidate_skills = [
        str(skill).strip()
        for skill in candidate_skills
        if str(skill).strip()
    ][:5]

    candidate_location = str(
        candidate.get(
            "location",
            ""
        )
    ).strip()

    candidate_experience = str(
        candidate.get(
            "experience_level",
            ""
        )
    ).strip()

    candidate_employment = str(
        candidate.get(
            "employment_type",
            ""
        )
    ).strip()

    # =====================================================
    # BUILD SEARCH QUERIES
    # =====================================================

    search_queries = (
        _build_search_queries(
            role=candidate_role,
            skills=candidate_skills,
            location=candidate_location,
            employment_type=(
                candidate_employment
            ),
        )
    )

    candidate[
        "search_queries"
    ] = search_queries

    print(
        "\nCandidate:"
    )

    print(
        f"Role: {candidate_role}"
    )

    print(
        f"Skills: {candidate_skills}"
    )

    print(
        f"Location: {candidate_location}"
    )

    print(
        f"Experience: {candidate_experience}"
    )

    print(
        f"Queries: {len(search_queries)}"
    )

    for index, query in enumerate(
        search_queries,
        start=1,
    ):

        print(
            f"  {index}. {query}"
        )

    # =====================================================
    # 3. JOB SEARCH
    # =====================================================

    print(
        "\n[3/5] Searching job sources..."
    )

    search_input = f"""
Find real current job postings.

Candidate role:
{candidate_role}

Location:
{candidate_location}

Experience:
{candidate_experience}

Employment:
{candidate_employment}

Skills:
{", ".join(candidate_skills)}

Search queries:

{chr(10).join(search_queries)}

Use Tavily.

Search multiple related opportunities.

Return concise search results containing:

- job title
- URL
- short snippet

Prefer actual job posting pages from:

LinkedIn Jobs
Indeed
Wellfound
Greenhouse
Lever
Official company job pages

Exclude:

blogs
courses
tutorials
news
GitHub
documentation
salary articles
career advice
generic company pages

Do not fabricate jobs.

Do not invent dates.

Do not deeply analyze descriptions.

Return concise results only.
"""

    search_result = (
        job_search_agent.invoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": search_input,
                    }
                ]
            }
        )
    )

    search_content = (
        _extract_agent_content(
            search_result
        )
    )

    if not search_content:

        raise ValueError(
            "Job Search Agent returned "
            "no results."
        )

    print(
        "✓ Job search completed."
    )

    print(
        f"✓ Search output size: "
        f"{len(search_content)} characters"
    )

    # =====================================================
    # TOKEN PROTECTION
    # =====================================================

    # IMPORTANT:
    #
    # Groq GPT-OSS has an 8K TPM limit on the
    # current service tier.
    #
    # Therefore we NEVER send a huge Tavily result
    # directly to the scraper.
    #
    # Keep search context around 4,500 chars.

    MAX_SEARCH_CONTENT_CHARS = 4500

    if len(search_content) > (
        MAX_SEARCH_CONTENT_CHARS
    ):

        print(
            f"⚠ Search output too large: "
            f"{len(search_content)} chars"
        )

        search_content = (
            search_content[
                :MAX_SEARCH_CONTENT_CHARS
            ]
        )

        print(
            f"✓ Search output reduced to "
            f"{MAX_SEARCH_CONTENT_CHARS} chars."
        )

    # =====================================================
    # 4. JOB SCRAPING
    # =====================================================

    print(
        "\n[4/5] Inspecting job pages..."
    )

    scraper_input = f"""
Extract valid job postings from the search
results below.

SEARCH RESULTS:

{search_content}

Return ONLY a JSON array.

Format:

[
  {{
    "title": "",
    "company": "",
    "location": "",
    "employment_type": "",
    "description": "",
    "posting_date": "",
    "url": ""
  }}
]

Rules:

1. Keep only real job postings.

2. Preserve the actual job URL.

3. Never fabricate information.

4. Never guess dates.

5. Unknown date must be:
"date not available"

6. Ignore blogs.

7. Ignore articles.

8. Ignore tutorials.

9. Ignore courses.

10. Ignore generic company pages.

11. Remove duplicate URLs.

12. Keep descriptions SHORT.

13. Only return jobs that actually appear
in the supplied search results.
"""

    scraped_result = (
        job_scraper_agent.invoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": scraper_input,
                    }
                ]
            }
        )
    )

    scraped_content = (
        _extract_agent_content(
            scraped_result
        )
    )

    scraped_jobs = (
        _parse_scraped_jobs(
            scraped_content
        )
    )

    print(
        f"✓ Job inspection completed."
    )

    print(
        f"✓ Jobs extracted: "
        f"{len(scraped_jobs)}"
    )

    # =====================================================
    # REMOVE DUPLICATES AGAIN
    # =====================================================

    unique_jobs = []

    seen_urls = set()

    for job in scraped_jobs:

        if not isinstance(
            job,
            dict,
        ):
            continue

        url = str(
            job.get(
                "url",
                ""
            )
        ).strip()

        if not url:
            continue

        normalized_url = (
            url.rstrip("/")
            .lower()
        )

        if normalized_url in seen_urls:
            continue

        seen_urls.add(
            normalized_url
        )

        unique_jobs.append(
            job
        )

    scraped_jobs = unique_jobs

    print(
        f"✓ Unique jobs: "
        f"{len(scraped_jobs)}"
    )

    # =====================================================
    # 5. PYTHON MATCHING
    # =====================================================

    print(
        "\n[5/5] Running matching engine..."
    )

    final_jobs = process_jobs(
        scraped_jobs,
        candidate=candidate,
        max_jobs=max_jobs,
    )

    statistics = (
        get_job_statistics(
            final_jobs
        )
    )

    print(
        "✓ Matching completed."
    )

    print(
        f"Final jobs: "
        f"{statistics.get('total_jobs', 0)}"
    )

    print(
        f"Unique companies: "
        f"{statistics.get('unique_companies', 0)}"
    )

    # =====================================================
    # FINAL RESULT
    # =====================================================

    return {
        "candidate": candidate,
        "search_mode": search_mode,
        "jobs": final_jobs,
        "statistics": statistics,
    }


# =========================================================
# LOCAL TEST
# =========================================================

if __name__ == "__main__":

    result = run_pipeline(
        resume_path=(
            "data/sample_resumes/"
            "resume.pdf"
        ),
        max_jobs=10,
        search_mode="resume",
    )

    print(
        "\n"
    )

    print(
        "=" * 70
    )

    print(
        "CAREERLENS AI — JOB MATCHING RESULTS"
    )

    print(
        "=" * 70
    )

    print(
        "\nCandidate:"
    )

    print(
        result["candidate"]
    )

    print(
        "\nStatistics:"
    )

    print(
        result["statistics"]
    )

    print(
        "\nJobs:"
    )

    for index, job in enumerate(
        result["jobs"],
        start=1,
    ):

        print(
            "\n"
            + "-" * 70
        )

        print(
            f"{index}. "
            f"{job.get('title', 'Unknown')}"
        )

        print(
            f"Company: "
            f"{job.get('company', 'Unknown')}"
        )

        print(
            f"Location: "
            f"{job.get('location', 'Unknown')}"
        )

        print(
            f"Employment: "
            f"{job.get('employment_type', 'Unknown')}"
        )

        print(
            f"Posting Date: "
            f"{job.get('posting_date', 'Unknown')}"
        )

        print(
            f"Match Score: "
            f"{job.get('match_score', 'N/A')}%"
        )

        print(
            f"URL: "
            f"{job.get('url', '')}"
        )