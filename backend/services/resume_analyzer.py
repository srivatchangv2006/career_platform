import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

from schemas.ai_resume_analysis import ResumeAnalysisAI


load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-3.6-flash",
)

if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY is not set")


client = genai.Client(api_key=GEMINI_API_KEY)


def analyze_resume_text(resume_text: str) -> dict:
    if not resume_text.strip():
        raise ValueError("Resume text is empty")

    prompt = f"""
You are an expert career and resume analysis assistant.

Analyze the resume below.

Rules:
- Only use information supported by the resume.
- Do not invent experience, skills, education, achievements, or dates.
- Keep the summary concise and professional.
- List specific strengths and weaknesses.
- Extract skills explicitly present in the resume.
- Summarize work experience and education separately.
- Give practical, actionable recommendations.

Resume:
--------------------
{resume_text}
--------------------
"""

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=ResumeAnalysisAI,
        ),
    )

    if not response.text:
        raise RuntimeError("Gemini returned an empty response")

    analysis = ResumeAnalysisAI.model_validate_json(
        response.text
    )

    return analysis.model_dump()