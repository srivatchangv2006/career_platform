from pydantic import BaseModel, Field


class AICareerRecommendation(BaseModel):
    recommendation_type: str = Field(
        description=(
            "Type of recommendation, such as SKILL, JOB, "
            "PROJECT, CERTIFICATION, NETWORKING, or CAREER_PATH."
        )
    )

    title: str = Field(
        description="Short title of the recommendation."
    )

    description: str = Field(
        description="Detailed and actionable explanation."
    )

    priority: str = Field(
        description=(
            "Priority level such as HIGH, MEDIUM, or LOW."
        )
    )

    is_completed: bool = Field(
        default=False,
        description="Whether the recommendation is already completed."
    )