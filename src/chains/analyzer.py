from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

from src.config import settings


llm = ChatGoogleGenerativeAI(
    model=settings.MODEL_NAME,
    google_api_key=settings.GOOGLE_API_KEY,
    temperature=settings.TEMPERATURE,
)


prompt = ChatPromptTemplate.from_template(
    """
You are an expert technical recruiter and search optimization specialist.

Your job is NOT only to summarize the resume.

Your main objective is to analyze the candidate's resume and generate
highly effective web search queries that will maximize the quality and
relevance of job search results.

The generated search queries will be sent to the Tavily web search engine
to find real and relevant job openings.

Resume:
{resume}

Analyze the resume and return ONLY valid JSON.

Use exactly this structure:

{{
    "candidate_profile": {{
        "primary_role": "",
        "experience_level": "",
        "years_of_experience": "",
        "location": "",
        "employment_type": ""
    }},

    "skills": [],

    "technologies": [],

    "search_queries": []
}}

Search query rules:

- Match the candidate's actual experience and background.
- Identify the most suitable primary job role.
- Consider closely related job titles that match the candidate.
- Include important technologies and skills in the search queries.
- Include experience level such as Junior, Mid-Level, or Senior when appropriate.
- Include Remote, Full-time, On-site, or Hybrid when appropriate.
- Include the candidate's location when it is available in the resume.
- Do NOT create queries using skills that are not present in the resume.
- Avoid overly generic queries such as "software engineer jobs".
- Prefer specific job-search phrases such as:
  "Python Backend Developer jobs"
  "FastAPI Developer jobs"
  "Junior Python Developer remote jobs"
- Generate 6-10 high-quality search queries.
- Each query should have a clear job-search intent.
- Queries should be suitable for web search and should help find actual job
  postings rather than tutorials, documentation, courses, or general articles.
- Prefer queries containing terms such as:
  jobs, careers, vacancies, hiring, openings, position
  when appropriate.
- Do not include unnecessary explanations.
- Do not fabricate candidate information.
"""
)


parser = JsonOutputParser()

analyzer_chain = prompt | llm | parser