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
    max_results=5,
    topic="general",
    search_depth="basic",
    tavily_api_key=settings.TAVILY_API_KEY,
)


# ---------------------------------------------------------
# Agent Instructions
# ---------------------------------------------------------

SYSTEM_PROMPT = """
You are a Job Search Agent.

Your job is to find real and relevant job openings based on
the candidate profile and search queries provided by the user.

You have access to the Tavily web search tool.

IMPORTANT RULES:

1. Use the Tavily search tool to perform web searches.

2. Search for actual job opportunities, not:
   - tutorials
   - documentation
   - courses
   - blogs
   - GitHub repositories
   - generic career advice

3. Use the provided search queries as the primary search strategy.

4. You may slightly modify a query if the initial search
   produces poor results.

5. Prefer job posting pages from:
   - company career pages
   - legitimate job boards
   - recruitment platforms

6. Avoid duplicate job URLs.

7. Prefer recent job postings when possible.

8. Do not invent job information.

9. Do not fabricate posting dates.

10. Return useful search results with:
    - job title
    - company name
    - URL
    - short description/snippet
    - posting date if available

11. If the posting date cannot be reliably determined,
    explicitly say:
    "date not available"

12. Focus on relevance to the candidate's actual experience,
    skills, technologies and role.

13. Do not return search results that are clearly unrelated
    to the candidate.

Your final response should contain a concise list of the
most relevant job opportunities discovered through Tavily.
"""


# ---------------------------------------------------------
# ReAct Agent
# ---------------------------------------------------------

job_search_agent = create_react_agent(
    model=llm,
    tools=[tavily_search],
    prompt=SYSTEM_PROMPT,
)