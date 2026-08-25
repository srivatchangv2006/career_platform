import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

from schemas.ai_skill_gap import SkillGapAI


load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-3.6-flash",
)

if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY is not set")

client = genai.Client(api_key=GEMINI_API_KEY)


def analyze_skill_gap(
    candidate_skills: list[str],
    required_skills: list[str],
) -> dict:
    prompt = f"""
You are a career skill-gap analysis assistant.

Compare the candidate's skills against the skills required for the job.

Candidate skills:
{candidate_skills}

Required job skills:
{required_skills}

Rules:
- Only consider a skill matched when the candidate clearly has it.
- Do not invent skills.
- Identify missing required skills.
- Give practical recommendations for closing the gaps.
- Calculate an overall skill match score from 0 to 100.
"""

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=SkillGapAI,
        ),
    )

    if not response.text:
        raise RuntimeError("Gemini returned an empty response")

    result = SkillGapAI.model_validate_json(response.text)

    score = max(
        0,
        min(100, result.overall_match_score),
    )

    output = result.model_dump()
    output["overall_match_score"] = score

    return output