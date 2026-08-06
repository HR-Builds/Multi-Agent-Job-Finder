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
You are an expert technical recruiter.

Analyze the following resume.

Resume:
{resume}

Extract the following information.

Return ONLY valid JSON.

{{
    "role": "",
    "experience": "",
    "skills": [],
    "technologies": [],
    "keywords": []
}}

Rules:

- Infer the most suitable job role.
- Estimate experience if mentioned.
- Include technical skills only.
- Generate 8–12 search keywords suitable for searching jobs.
- Do not explain.
"""
)

parser = JsonOutputParser()

analyzer_chain = prompt | llm | parser