from datetime import datetime
from typing import Any


# ---------------------------------------------------------
# Date Parser
# ---------------------------------------------------------

def parse_date(date_value: Any):
    """
    Convert a job posting date into a datetime object.

    Returns None when the date is unavailable or unreliable.
    """

    if not date_value:
        return None

    if not isinstance(date_value, str):
        return None

    date_value = date_value.strip().lower()

    if date_value in {
        "",
        "date not available",
        "not available",
        "unknown",
        "n/a",
        "na",
        "none",
    }:
        return None

    date_formats = [
        "%Y-%m-%d",
        "%d-%m-%Y",
        "%m-%d-%Y",
        "%Y/%m/%d",
        "%d/%m/%Y",
        "%m/%d/%Y",
        "%B %d, %Y",
        "%b %d, %Y",
        "%d %B %Y",
        "%d %b %Y",
    ]

    for date_format in date_formats:
        try:
            return datetime.strptime(
                date_value,
                date_format,
            )
        except ValueError:
            continue

    return None


# ---------------------------------------------------------
# Normalize Job
# ---------------------------------------------------------

def normalize_job(job: dict) -> dict:
    """
    Normalize a scraped job into a consistent structure.
    """

    return {
        "title": str(
            job.get("title") or "Title not available"
        ).strip(),

        "company": str(
            job.get("company") or "Company not available"
        ).strip(),

        "location": str(
            job.get("location") or "Location not available"
        ).strip(),

        "employment_type": str(
            job.get("employment_type")
            or "Not available"
        ).strip(),

        "description": str(
            job.get("description")
            or "Description not available"
        ).strip(),

        "posting_date": str(
            job.get("posting_date")
            or "date not available"
        ).strip(),

        "url": str(
            job.get("url") or ""
        ).strip(),
    }


# ---------------------------------------------------------
# Remove Duplicate Jobs
# ---------------------------------------------------------

def remove_duplicates(jobs: list[dict]) -> list[dict]:
    """
    Remove duplicate jobs using their URL.
    """

    unique_jobs = []
    seen_urls = set()

    for job in jobs:

        url = job.get("url", "").strip().lower()

        if not url:
            continue

        if url in seen_urls:
            continue

        seen_urls.add(url)
        unique_jobs.append(job)

    return unique_jobs


# ---------------------------------------------------------
# Sort Jobs
# ---------------------------------------------------------

def sort_jobs(jobs: list[dict]) -> list[dict]:
    """
    Sort jobs by reliable posting date.

    Jobs with dates come first, newest first.
    Jobs without dates come afterward.
    """

    dated_jobs = []
    undated_jobs = []

    for job in jobs:

        parsed_date = parse_date(
            job.get("posting_date")
        )

        if parsed_date:
            job["_parsed_date"] = parsed_date
            dated_jobs.append(job)

        else:
            job["posting_date"] = "date not available"
            undated_jobs.append(job)

    # Newest first
    dated_jobs.sort(
        key=lambda job: job["_parsed_date"],
        reverse=True,
    )

    # Remove internal field
    for job in dated_jobs:
        job.pop("_parsed_date", None)

    return dated_jobs + undated_jobs


# ---------------------------------------------------------
# Limit Results
# ---------------------------------------------------------

def limit_jobs(
    jobs: list[dict],
    max_jobs: int | None = None,
) -> list[dict]:
    """
    Limit the number of jobs returned.
    """

    if not max_jobs:
        return jobs

    return jobs[:max_jobs]


# ---------------------------------------------------------
# Main Processor
# ---------------------------------------------------------

def process_jobs(
    jobs: list[dict],
    max_jobs: int | None = None,
) -> list[dict]:
    """
    Complete Stage 5 processing.

    Pipeline:

        Normalize
        ↓
        Remove duplicates
        ↓
        Sort by posting date
        ↓
        Limit results
    """

    if not jobs:
        return []

    # 1. Normalize
    normalized_jobs = [
        normalize_job(job)
        for job in jobs
    ]

    # 2. Remove duplicate URLs
    unique_jobs = remove_duplicates(
        normalized_jobs
    )

    # 3. Sort newest → oldest
    sorted_jobs = sort_jobs(
        unique_jobs
    )

    # 4. Limit final results
    final_jobs = limit_jobs(
        sorted_jobs,
        max_jobs,
    )

    return final_jobs


# ---------------------------------------------------------
# Statistics
# ---------------------------------------------------------

def get_job_statistics(
    jobs: list[dict],
) -> dict:
    """
    Generate simple statistics for the UI.
    """

    total = len(jobs)

    with_date = sum(
        1
        for job in jobs
        if parse_date(
            job.get("posting_date")
        )
    )

    without_date = total - with_date

    companies = {
        job.get("company")
        for job in jobs
        if job.get("company")
    }

    return {
        "total_jobs": total,
        "jobs_with_date": with_date,
        "jobs_without_date": without_date,
        "unique_companies": len(companies),
    }