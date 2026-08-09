from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

from src.config import settings


# ---------------------------------------------------------
# LLM
# ---------------------------------------------------------

llm = ChatGoogleGenerativeAI(
    model=settings.MODEL_NAME,
    google_api_key=settings.GOOGLE_API_KEY,
    temperature=0.1,
)


# ---------------------------------------------------------
# Writer Prompt
# ---------------------------------------------------------

writer_prompt = ChatPromptTemplate.from_template(
    """
You are an expert technical recruiter.

Your task is to create a clean and useful job report from
the scraped job information provided below.

Candidate Profile:
{candidate_profile}

Candidate Skills:
{skills}

Candidate Technologies:
{technologies}

Scraped Jobs:
{jobs}


IMPORTANT RULES:

1. Include only jobs that are reasonably relevant to the
   candidate's profile.

2. Sort jobs by reliable posting date:
   newest first.

3. Jobs with a reliable posting date should appear before
   jobs where the date is unavailable.

4. If a reliable posting date is not available, write exactly:

   "date not available"

5. NEVER fabricate, estimate, or guess a posting date.

6. Do not treat "last updated", "modified", "deadline",
   or "published" dates as the posting date unless the
   source clearly identifies them as the actual job
   posting date.

7. Do not invent:
   - job titles
   - companies
   - descriptions
   - locations
   - dates
   - URLs

8. Remove duplicate jobs.

9. Prefer jobs with direct job posting URLs.

10. Keep descriptions concise but useful.

11. Highlight the technologies or skills that match the
    candidate.

12. If no reliable posting date exists, do not try to
    calculate or infer one.

13. Do not include irrelevant search results such as:
    - blogs
    - tutorials
    - courses
    - documentation
    - GitHub repositories
    - generic career pages


OUTPUT FORMAT:

# Job Matches

For each job use this format:

## {Job Title}

**Company:** {Company}

**Location:** {Location}

**Employment Type:** {Employment Type}

**Posting Date:** {Posting Date}

**Match:** {Short explanation of why this job matches
the candidate}

**Description:** {Concise job description}

**URL:** {URL}


At the end, provide:

## Summary

- Total relevant jobs: X
- Jobs with reliable posting dates: X
- Jobs with date not available: X

Do not add unnecessary explanations.
"""
)


# ---------------------------------------------------------
# Writer Chain
# ---------------------------------------------------------

writer_chain = writer_prompt | llm | StrOutputParser()