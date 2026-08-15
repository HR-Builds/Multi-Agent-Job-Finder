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
You are a technical recruiter and job-search query specialist.

Analyze the resume and generate highly relevant search queries
for finding REAL job postings on the web using Tavily.

Resume:
{resume}

Return ONLY valid JSON in this exact format:

{{
    "role": "",
    "experience_level": "",
    "location": "",
    "skills": [],
    "search_queries": []
}}

Rules:

- Identify the candidate's most suitable job role.
- Identify experience level from the resume.
- Extract only the most important technical skills.
- Generate 5-7 highly targeted job-search queries.
- Queries must be suitable for Tavily web search.
- Include job titles, important technologies, experience level,
  and location when relevant.
- Prefer queries containing "jobs", "careers", "hiring",
  "vacancy", or "openings".
- Focus on finding actual job postings.
- Avoid queries for tutorials, courses, documentation,
  blogs, GitHub repositories, or general information.
- Do not invent skills, experience, location, or technologies.
- Do not explain your answer.
- Keep all output concise.
"""
)


parser = JsonOutputParser()

analyzer_chain = prompt | llm | parser