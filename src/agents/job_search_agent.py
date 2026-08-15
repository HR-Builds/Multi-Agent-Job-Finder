from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_tavily import TavilySearch
from langgraph.prebuilt import create_react_agent

from src.config import settings


# ---------------------------------------------------------
# LLM - Google Gemini
# ---------------------------------------------------------

llm = ChatGoogleGenerativeAI(
    model=settings.MODEL_NAME,
    google_api_key=settings.GOOGLE_API_KEY,
    temperature=settings.TEMPERATURE,
)


# ---------------------------------------------------------
# Tavily Search Tool
# ---------------------------------------------------------

tavily_search = TavilySearch(
   #  max_results = user_selected_results,
    max_results = settings.MAX_SEARCH_RESULTS,
    topic="general",
    search_depth="basic",
    tavily_api_key=settings.TAVILY_API_KEY,
)


# ---------------------------------------------------------
# Agent Instructions
# ---------------------------------------------------------

SYSTEM_PROMPT = """
You are a job search specialist.

Your ONLY task is to find relevant and real job posting URLs
using the Tavily web search tool.

The user will provide:
- candidate role
- experience level
- skills
- location
- optimized search queries

Use the provided search queries as your primary search strategy.

IMPORTANT RULES:

1. Use Tavily to search the web.

2. Search for REAL job openings only.

3. Prefer:
   - company career pages
   - legitimate job boards
   - recruitment platforms

4. Avoid:
   - tutorials
   - blogs
   - courses
   - documentation
   - GitHub repositories
   - news articles
   - generic career advice

5. Use the provided search queries without unnecessarily
   changing them.

6. Only modify a query if the search produces poor results.

7. Focus on jobs matching the candidate's:
   - role
   - experience level
   - skills
   - technologies
   - location

8. Remove duplicate URLs.

9. Do not invent job information.

10. Do not guess or fabricate posting dates.

11. At this stage, DO NOT deeply analyze job descriptions.

12. Return concise search results containing only:
   - job title if available
   - company if available
   - URL
   - short Tavily snippet

13. The URLs will be passed to a separate Job Scraper Agent
    for detailed extraction.

Keep your final response concise.
"""


# ---------------------------------------------------------
# ReAct Agent
# ---------------------------------------------------------

job_search_agent = create_react_agent(
    model=llm,
    tools=[tavily_search],
    prompt=SYSTEM_PROMPT,
)