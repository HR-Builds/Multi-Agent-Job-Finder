from datetime import datetime
from typing import Any
from datetime import datetime, timedelta
from urllib.parse import urlsplit, urlunsplit
import re


# =========================================================
# Constants
# =========================================================

UNKNOWN_VALUES = {
    "",
    "date not available",
    "not available",
    "unknown",
    "n/a",
    "na",
    "none",
    "null",
}

JOB_SOURCE_DOMAINS = {
    "linkedin.com": "LinkedIn",
    "indeed.com": "Indeed",
    "glassdoor.com": "Glassdoor",
    "wellfound.com": "Wellfound",
    "greenhouse.io": "Greenhouse",
    "lever.co": "Lever",
}

NON_JOB_TERMS = {
    "blog",
    "blogs",
    "article",
    "articles",
    "tutorial",
    "course",
    "courses",
    "news",
    "documentation",
    "docs",
    "github",
    "salary guide",
    "career advice",
}


# =========================================================
# Basic Helpers
# =========================================================

def _clean_text(value: Any) -> str:
    if value is None:
        return ""

    return str(value).strip()


def _normalize_text(value: Any) -> str:
    """
    Normalize text for deterministic matching.
    """

    value = _clean_text(value).lower()

    value = re.sub(
        r"[^a-z0-9+#.\- ]+",
        " ",
        value,
    )

    value = re.sub(
        r"\s+",
        " ",
        value,
    )

    return value.strip()


def _tokenize(value: Any) -> set[str]:
    text = _normalize_text(value)

    if not text:
        return set()

    return set(text.split())


# =========================================================
# Date Parser
# =========================================================

def parse_date(date_value: Any):
    """
    Convert a verified job posting date into datetime.

    Returns None if the date is unavailable or unreliable.

    IMPORTANT:
    No dates are guessed.
    """

    if not isinstance(date_value, str):
        return None

    value = date_value.strip().lower()

    if value in UNKNOWN_VALUES:
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
                value,
                date_format,
            )
        except ValueError:
            continue

    return None


# =========================================================
# URL Normalization
# =========================================================

def normalize_url(url: Any) -> str:
    """
    Normalize URLs so tracking parameters and trailing
    differences do not create duplicate jobs.
    """

    url = _clean_text(url)

    if not url:
        return ""

    try:
        parsed = urlsplit(url)

        clean_path = parsed.path.rstrip("/")

        normalized = urlunsplit(
            (
                parsed.scheme.lower(),
                parsed.netloc.lower(),
                clean_path,
                "",
                "",
            )
        )

        return normalized

    except Exception:
        return url.lower().rstrip("/")


# =========================================================
# Source Detection
# =========================================================

def detect_source(url: str) -> str:
    """
    Detect major job platform from URL.
    """

    normalized_url = normalize_url(url).lower()

    for domain, source in JOB_SOURCE_DOMAINS.items():

        if domain in normalized_url:
            return source

    return "Company / Other"


# =========================================================
# Normalize Job
# =========================================================

def normalize_job(job: dict) -> dict:
    """
    Convert any scraped job into a consistent structure.
    """

    url = normalize_url(
        job.get("url", "")
    )

    normalized = {
        "title": _clean_text(
            job.get("title")
        ) or "Title not available",

        "company": _clean_text(
            job.get("company")
        ) or "Company not available",

        "location": _clean_text(
            job.get("location")
        ) or "Location not available",

        "employment_type": _clean_text(
            job.get("employment_type")
        ) or "Not available",

        "description": _clean_text(
            job.get("description")
        ) or "Description not available",

        "posting_date": _clean_text(
            job.get("posting_date")
        ) or "date not available",

        "url": url,

        "source": detect_source(url),

        # Default score
        "match_score": 0,
    }

    return normalized


# =========================================================
# Actual Job Validation
# =========================================================

def is_actual_job(job: dict) -> bool:
    """
    Deterministic quality filter.

    Removes obvious blogs, tutorials, news, GitHub pages,
    generic pages and invalid results.
    """

    title = _normalize_text(
        job.get("title")
    )

    company = _normalize_text(
        job.get("company")
    )

    description = _normalize_text(
        job.get("description")
    )

    url = _normalize_text(
        job.get("url")
    )

    if not url:
        return False

    # Obviously invalid title
    if title in {
        "",
        "title not available",
    }:
        return False

    combined = " ".join(
        [
            title,
            company,
            description[:1000],
            url,
        ]
    )

    for bad_term in NON_JOB_TERMS:

        if bad_term in combined:
            return False

    # Generic career pages without a real role
    generic_titles = {
        "careers",
        "career",
        "jobs",
        "job opportunities",
        "work with us",
        "join us",
        "open positions",
    }

    if title in generic_titles:
        return False

    return True


# =========================================================
# Duplicate Removal
# =========================================================

def remove_duplicates(
    jobs: list[dict],
) -> list[dict]:
    """
    Remove duplicates using normalized URLs.

    Fallback:
    company + title + location.
    """

    unique_jobs = []

    seen_urls = set()
    seen_fingerprints = set()

    for job in jobs:

        url = normalize_url(
            job.get("url", "")
        )

        title = _normalize_text(
            job.get("title")
        )

        company = _normalize_text(
            job.get("company")
        )

        location = _normalize_text(
            job.get("location")
        )

        if url:

            if url in seen_urls:
                continue

            seen_urls.add(url)

        fingerprint = (
            company,
            title,
            location,
        )

        if fingerprint in seen_fingerprints:
            continue

        seen_fingerprints.add(
            fingerprint
        )

        unique_jobs.append(job)

    return unique_jobs


# =========================================================
# Candidate Matching Helpers
# =========================================================

def _candidate_skills(
    candidate: dict,
) -> list[str]:

    skills = candidate.get(
        "skills",
        [],
    )

    if not isinstance(skills, list):
        skills = [skills]

    return [
        _normalize_text(skill)
        for skill in skills
        if _normalize_text(skill)
    ]


def _skill_match_count(
    job_text: str,
    skills: list[str],
) -> int:

    count = 0

    for skill in skills:

        if not skill:
            continue

        # Phrase match for skills like:
        # machine learning
        # node.js
        # power bi
        if skill in job_text:
            count += 1

    return count


# =========================================================
# Relevance Scoring
# =========================================================

def calculate_match_score(
    job: dict,
    candidate: dict,
) -> dict:
    """
    Calculate deterministic job relevance.

    Base scoring follows the BRD direction:

        Title        30
        Technology   20
        Skills       10
        Location     10
        Experience   10
        Employment    5

    Maximum base score = 85.

    Final score is normalized to 100.
    """

    title = _normalize_text(
        job.get("title")
    )

    description = _normalize_text(
        job.get("description")
    )

    job_location = _normalize_text(
        job.get("location")
    )

    job_employment = _normalize_text(
        job.get("employment_type")
    )

    company = _normalize_text(
        job.get("company")
    )

    role = _normalize_text(
        candidate.get("role")
    )

    candidate_location = _normalize_text(
        candidate.get("location")
    )

    experience = _normalize_text(
        candidate.get(
            "experience_level"
        )
    )

    employment = _normalize_text(
        candidate.get(
            "employment_type"
        )
    )

    skills = _candidate_skills(
        candidate
    )

    full_job_text = " ".join(
        [
            title,
            description,
            company,
            job_location,
            job_employment,
        ]
    )

    # -----------------------------------------------------
    # 1. Job Title — 30
    # -----------------------------------------------------

    title_score = 0

    if role:

        if role in title:
            title_score = 30

        else:

            role_tokens = _tokenize(role)
            title_tokens = _tokenize(title)

            if role_tokens:

                overlap = (
                    role_tokens
                    & title_tokens
                )

                ratio = (
                    len(overlap)
                    / len(role_tokens)
                )

                title_score = round(
                    30 * ratio
                )

    # -----------------------------------------------------
    # 2. Technology — 20
    # -----------------------------------------------------

    technology_score = 0

    if skills:

        matched_skills = (
            _skill_match_count(
                full_job_text,
                skills,
            )
        )

        ratio = (
            matched_skills
            / len(skills)
        )

        technology_score = round(
            20 * ratio
        )

    # -----------------------------------------------------
    # 3. Skills — 10
    # -----------------------------------------------------

    skill_score = 0

    if skills:

        matched_skills = (
            _skill_match_count(
                description,
                skills,
            )
        )

        ratio = (
            matched_skills
            / len(skills)
        )

        skill_score = round(
            10 * ratio
        )

    # -----------------------------------------------------
    # 4. Location — 10
    # -----------------------------------------------------

    location_score = 0

    if candidate_location:

        candidate_location_tokens = (
            _tokenize(candidate_location)
        )

        job_location_tokens = (
            _tokenize(job_location)
        )

        if (
            candidate_location
            in job_location
        ):

            location_score = 10

        elif (
            "remote" in candidate_location
            and "remote" in job_location
        ):

            location_score = 10

        elif (
            candidate_location_tokens
            & job_location_tokens
        ):

            location_score = 7

    # -----------------------------------------------------
    # 5. Experience — 10
    # -----------------------------------------------------

    experience_score = 0

    experience_map = {
        "internship": {
            "intern": 10,
            "internship": 10,
            "entry": 8,
            "junior": 7,
        },

        "entry": {
            "entry": 10,
            "junior": 10,
            "intern": 8,
            "associate": 8,
        },

        "junior": {
            "junior": 10,
            "entry": 9,
            "associate": 8,
        },

        "mid": {
            "mid": 10,
            "middle": 10,
            "senior": 5,
        },

        "senior": {
            "senior": 10,
            "lead": 8,
            "principal": 7,
        },
    }

    experience_key = experience.lower()

    for level, score in (
        experience_map
        .get(experience_key, {})
        .items()
    ):

        if level in title or level in description:
            experience_score = max(
                experience_score,
                score,
            )

    # If no specific experience info exists,
    # don't invent a match.
    if not experience:
        experience_score = 0

    # -----------------------------------------------------
    # 6. Employment Type — 5
    # -----------------------------------------------------

    employment_score = 0

    if employment:

        if employment in job_employment:
            employment_score = 5

    # -----------------------------------------------------
    # Final Score
    # -----------------------------------------------------

    raw_score = (
        title_score
        + technology_score
        + skill_score
        + location_score
        + experience_score
        + employment_score
    )

    # Maximum = 85
    final_score = round(
        (raw_score / 85) * 100
    )

    return {
        "match_score": min(
            max(final_score, 0),
            100,
        ),

        "score_breakdown": {
            "title": title_score,
            "technology": technology_score,
            "skills": skill_score,
            "location": location_score,
            "experience": experience_score,
            "employment": employment_score,
            "raw_score": raw_score,
            "maximum_score": 85,
        },
    }


# =========================================================
# Apply Match Scores
# =========================================================

def score_jobs(
    jobs: list[dict],
    candidate: dict | None,
) -> list[dict]:

    if not candidate:
        return jobs

    scored_jobs = []

    for job in jobs:

        score_data = calculate_match_score(
            job,
            candidate,
        )

        job.update(
            score_data
        )

        scored_jobs.append(job)

    return scored_jobs


# =========================================================
# Sort Jobs
# =========================================================

def sort_jobs(
    jobs: list[dict],
) -> list[dict]:
    """
    Sort primarily by match score and secondarily
    by verified posting date.

    Undated jobs remain at the bottom.
    """

    def sort_key(job):

        score = job.get(
            "match_score",
            0,
        )

        parsed_date = parse_date(
            job.get("posting_date")
        )

        if parsed_date:
            timestamp = (
                parsed_date.timestamp()
            )
        else:
            timestamp = 0

        return (
            score,
            timestamp,
        )

    return sorted(
        jobs,
        key=sort_key,
        reverse=True,
    )


# =========================================================
# Limit Results
# =========================================================

def limit_jobs(
    jobs: list[dict],
    max_jobs: int | None = None,
) -> list[dict]:

    if not max_jobs:
        return jobs

    return jobs[:max_jobs]


# =========================================================
# Main Processor
# =========================================================

def process_jobs(
    jobs: list[dict],
    candidate: dict | None = None,
    max_jobs: int | None = None,
) -> list[dict]:
    """
    Complete deterministic Python job-processing engine.

    Pipeline:

        Normalize
        ↓
        Validate
        ↓
        Remove duplicates
        ↓
        Calculate relevance
        ↓
        Sort by relevance/date
        ↓
        Limit
    """

    if not jobs:
        return []

    # -----------------------------------------------------
    # 1. Normalize
    # -----------------------------------------------------

    normalized_jobs = [
        normalize_job(job)
        for job in jobs
    ]

    # -----------------------------------------------------
    # 2. Remove invalid/non-job results
    # -----------------------------------------------------

    valid_jobs = [
        job
        for job in normalized_jobs
        if is_actual_job(job)
    ]

    # -----------------------------------------------------
    # 3. Remove duplicates
    # -----------------------------------------------------

    unique_jobs = remove_duplicates(
        valid_jobs
    )

    # -----------------------------------------------------
    # 4. Score
    # -----------------------------------------------------

    scored_jobs = score_jobs(
        unique_jobs,
        candidate,
    )

    # -----------------------------------------------------
    # 5. Sort
    # -----------------------------------------------------

    sorted_jobs = sort_jobs(
        scored_jobs
    )

    # -----------------------------------------------------
    # 6. Limit
    # -----------------------------------------------------

    final_jobs = limit_jobs(
        sorted_jobs,
        max_jobs,
    )

    return final_jobs


# =========================================================
# Statistics
# =========================================================

def get_job_statistics(
    jobs: list[dict],
) -> dict:

    total = len(jobs)

    with_date = sum(
        1
        for job in jobs
        if parse_date(
            job.get("posting_date")
        )
    )

    without_date = (
        total - with_date
    )

    companies = {
        _normalize_text(
            job.get("company")
        )
        for job in jobs
        if job.get("company")
    }

    sources = {}

    for job in jobs:

        source = job.get(
            "source",
            "Company / Other",
        )

        sources[source] = (
            sources.get(source, 0)
            + 1
        )

    scores = [
        job.get(
            "match_score",
            0,
        )
        for job in jobs
        if isinstance(
            job.get(
                "match_score",
                0,
            ),
            (int, float),
        )
    ]

    average_match = (
        round(
            sum(scores)
            / len(scores)
        )
        if scores
        else 0
    )

    high_match_jobs = sum(
        1
        for score in scores
        if score >= 80
    )

    return {
        "total_jobs": total,

        "jobs_with_date": with_date,

        "jobs_without_date": without_date,

        "unique_companies": len(
            companies
        ),

        "average_match_score":
            average_match,

        "high_match_jobs":
            high_match_jobs,

        "sources":
            sources,
    }