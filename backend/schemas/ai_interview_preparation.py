from pydantic import BaseModel, Field


class AIInterviewPreparation(BaseModel):
    questions: list[str] = Field(
        description=(
            "Likely interview questions based on the candidate, "
            "job, resume, and skills."
        )
    )

    suggested_answers: list[str] = Field(
        description=(
            "Suggested answer guidance corresponding to the questions. "
            "Do not invent candidate experience."
        )
    )

    strengths: list[str] = Field(
        description=(
            "Candidate strengths relevant to the interview."
        )
    )

    improvement_areas: list[str] = Field(
        description=(
            "Areas the candidate should improve before the interview."
        )
    )

    recommendations: list[str] = Field(
        description=(
            "Practical recommendations for interview preparation."
        )
    )