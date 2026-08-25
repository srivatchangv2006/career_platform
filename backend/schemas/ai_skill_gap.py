from pydantic import BaseModel, Field


class SkillGapAI(BaseModel):
    matched_skills: list[str] = Field(
        description="Skills from the user's profile that match the job requirements."
    )

    missing_skills: list[str] = Field(
        description="Required job skills that are missing from the user's profile."
    )

    recommendations: list[str] = Field(
        description="Specific recommendations for closing the skill gaps."
    )

    overall_match_score: float = Field(
        description="Overall candidate-to-job skill match score from 0 to 100."
    )