import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

from schemas.job_recommendation import JobRecommendationAI


load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-3.6-flash",
)

if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY is not set")

client = genai.Client(api_key=GEMINI_API_KEY)


def generate_job_recommendations(
    candidate_profile: dict,
    jobs: list[dict],
) -> list[dict]:
    prompt = f"""
You are a career recommendation assistant.

Candidate profile:
{candidate_profile}

Available jobs:
{jobs}

Rank the most suitable jobs for this candidate.

Rules:
- Only recommend jobs from the provided list.
- Consider skills, preferred roles, locations,
  employment types, experience levels, salary,
  and remote preference.
- Give each recommendation a score from 0 to 100.
- Explain briefly why the job is recommended.
- Do not invent job information.
"""

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=list[JobRecommendationAI],
        ),
    )

    if not response.text:
        raise RuntimeError("Gemini returned an empty response")

    return [
        item.model_dump()
        for item in response.parsed
    ]