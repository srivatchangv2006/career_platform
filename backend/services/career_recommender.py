import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

from schemas.ai_career_recommendation import (
    AICareerRecommendation,
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


def generate_career_recommendations(
    goal: dict,
    candidate_context: dict,
) -> list[dict]:

    prompt = f"""
You are an expert career-planning assistant.

Create actionable recommendations for the candidate
based on their career goal and current profile.

Career goal:
{goal}

Candidate context:
{candidate_context}

Consider:
- Current skills
- Resume experience
- Education
- Skill gaps
- Job preferences
- Relevant job opportunities
- Previous recommendations
- Previous user feedback
- Target role
- Target industry
- Target location
- Target company
- Target timeline

Rules:
- Recommendations must be realistic and actionable.
- Do not invent candidate experience.
- Do not claim the candidate has a skill unless supported
  by the candidate context.
- Prioritize recommendations that directly move the
  candidate toward the stated goal.
- Return several useful recommendations.
"""

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=list[AICareerRecommendation],
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

    return [
        item.model_dump()
        for item in response.parsed
    ]