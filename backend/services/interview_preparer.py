import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

from schemas.ai_interview_preparation import (
    AIInterviewPreparation,
)


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


def generate_interview_preparation(
    interview_context: dict,
) -> dict:

    prompt = f"""
You are an expert interview preparation assistant.

Prepare the candidate for the interview using the
information below.

Interview context:
{interview_context}

Generate:
1. Likely interview questions.
2. Suggested answer guidance.
3. Candidate strengths.
4. Improvement areas.
5. Practical preparation recommendations.

Rules:
- Use only information supported by the provided context.
- Do not invent work experience, projects, achievements,
  education, or skills.
- Suggested answers must be guidance, not fabricated
  claims about the candidate.
- Make the preparation specific to the job and candidate.
- Include both technical and behavioral preparation
  where relevant.
"""

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=AIInterviewPreparation,
        ),
    )

    if not response.text:
        raise RuntimeError(
            "Gemini returned an empty response"
        )

    if not response.parsed:
        raise RuntimeError(
            "Gemini response could not be parsed"
        )

    return response.parsed.model_dump()