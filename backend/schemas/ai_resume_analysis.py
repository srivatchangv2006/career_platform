from pydantic import BaseModel, Field


class ResumeAnalysisAI(BaseModel):
    summary: str = Field(
        description="A concise professional summary of the candidate's resume."
    )

    strengths: list[str] = Field(
        description="The strongest aspects of the candidate's resume."
    )

    weaknesses: list[str] = Field(
        description="Areas where the resume or candidate profile could be improved."
    )

    extracted_skills: list[str] = Field(
        description="Technical and professional skills explicitly identified from the resume."
    )

    experience_summary: list[str] = Field(
        description="Important work experience details extracted from the resume."
    )

    education_summary: list[str] = Field(
        description="Important education details extracted from the resume."
    )

    recommendations: list[str] = Field(
        description="Specific actionable recommendations for improving the candidate's career profile or resume."
    )