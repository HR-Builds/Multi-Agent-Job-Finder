from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent

from src.config import settings

# IMPORTANT:
# Replace this import with the actual location of your
# existing scrape_url tool from the original research system.
from src.tools.scrape_url import scrape_url


# ---------------------------------------------------------
# LLM
# ---------------------------------------------------------

llm = ChatGoogleGenerativeAI(
    model=settings.MODEL_NAME,
    google_api_key=settings.GOOGLE_API_KEY,
    temperature=0.1,
)


# ---------------------------------------------------------
# Scraper Agent Instructions
# ---------------------------------------------------------

SYSTEM_PROMPT = """
You are a Job Scraper Agent.

Your job is to visit job posting URLs provided by the user
and extract accurate information from the actual job pages.

You have access to the scrape_url tool.

IMPORTANT RULES:

1. Use scrape_url to inspect the provided job URLs.

2. Extract information only from the scraped page content.

3. Do NOT invent or guess missing information.

4. Extract these fields whenever available:

   - job title
   - company name
   - job description
   - location
   - employment type
   - posting date
   - URL

5. Posting date is extremely important.

6. Only report a posting date when the page provides
   reasonable evidence that it is the actual posting date.

7. Do NOT treat these as the posting date unless the page
   clearly identifies them as the original posting date:

   - last modified date
   - updated date
   - page publication date
   - application deadline
   - crawling/indexing date

8. If a reliable posting date cannot be found, return:

   "date not available"

9. Do not fabricate dates.

10. Ignore pages that are clearly not job postings.

11. If a job URL redirects to another job page, use the
    final job page information.

12. Preserve the original job description as accurately as
    possible, but remove obvious navigation, advertisements,
    cookie notices and unrelated page content.

13. Return structured information for every valid job URL.

14. If scraping fails for a URL, report the URL and mark
    unavailable fields appropriately.

Your output should contain the scraped job information only.
"""


# ---------------------------------------------------------
# Job Scraper Agent
# ---------------------------------------------------------

job_scraper_agent = create_react_agent(
    model=llm,
    tools=[scrape_url],
    prompt=SYSTEM_PROMPT,
)