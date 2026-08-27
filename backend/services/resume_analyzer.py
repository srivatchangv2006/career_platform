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
    raise RuntimeError(
        "GEMINI_API_KEY is not set"
    )


client = genai.Client(
    api_key=GEMINI_API_KEY
)


def analyze_resume_text(
    resume_text: str,
    memory_context: list[dict] | None = None,
) -> dict:

    if not resume_text.strip():
        raise ValueError(
            "Resume text is empty"
        )

    memory_context = memory_context or []

    prompt = f"""
You are an expert career and resume analysis assistant.

Analyze the resume below.

Rules:
- Only use information supported by the resume.
- Do not invent experience, skills, education,
  achievements, or dates.
- Keep the summary concise and professional.
- Identify specific strengths and weaknesses.
- Extract skills explicitly present in the resume.
- Summarize work experience and education separately.
- Give practical and actionable recommendations.
- Use memory context only when it is relevant.
- Do not treat memory context as proof of facts
  that are not present in the resume.

Resume:
--------------------
{resume_text}
--------------------

Relevant candidate memory:
--------------------
{memory_context}
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
        raise RuntimeError(
            "Gemini returned an empty response"
        )

    analysis = ResumeAnalysisAI.model_validate_json(
        response.text
    )

    return analysis.model_dump()