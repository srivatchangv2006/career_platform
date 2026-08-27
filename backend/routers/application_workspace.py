from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from dependencies import get_db
from dependencies.auth import get_current_user

from models.application import Application
from dependencies.roles import require_role
from models.interview import Interview
from models.interview_preparation import InterviewPreparation
from models.job import Job
from models.resume import Resume
from models.skill_gap_analysis import SkillGapAnalysis
from models.user import User

from schemas.application_workspace import (
    ApplicationWorkspaceResponse,
    WorkspaceApplication,
    WorkspaceInterview,
    WorkspaceInterviewPreparation,
    WorkspaceJob,
    WorkspaceResume,
    WorkspaceSkillGap,
)

router = APIRouter(
    prefix="/applications",
    tags=["Application Workspace"],
    dependencies=[
        Depends(require_role("CANDIDATE"))
    ],
)

@router.get(
    "/{application_id}/workspace",
    response_model=ApplicationWorkspaceResponse,
)
def get_application_workspace(
    application_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # -------------------------------------------------
    # 1. Application
    # -------------------------------------------------

    application = (
        db.query(Application)
        .filter(
            Application.id == application_id,
            Application.user_id == current_user.id,
        )
        .first()
    )

    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found",
        )

    # -------------------------------------------------
    # 2. Job
    # -------------------------------------------------

    job = (
        db.query(Job)
        .filter(
            Job.id == application.job_id
        )
        .first()
    )

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )

    # -------------------------------------------------
    # 3. Resume
    # -------------------------------------------------

    resume_data = None

    if application.resume_id:
        resume = (
            db.query(Resume)
            .filter(
                Resume.id == application.resume_id,
                Resume.user_id == current_user.id,
            )
            .first()
        )

        if resume:
            resume_data = WorkspaceResume(
                id=resume.id,
                file_name=resume.file_name,
                content_type=resume.content_type,
                file_size_bytes=resume.file_size_bytes,
                is_primary=resume.is_primary,
            )

    # -------------------------------------------------
    # 4. Skill Gap
    # -------------------------------------------------

    skill_gap = (
        db.query(SkillGapAnalysis)
        .filter(
            SkillGapAnalysis.user_id
            == current_user.id,
            SkillGapAnalysis.job_id
            == application.job_id,
        )
        .first()
    )

    skill_gap_data = None

    if skill_gap:
        skill_gap_data = WorkspaceSkillGap(
            id=skill_gap.id,
            job_id=skill_gap.job_id,
            matched_skills=(
                skill_gap.matched_skills
            ),
            missing_skills=(
                skill_gap.missing_skills
            ),
            recommendations=(
                skill_gap.recommendations
            ),
            overall_match_score=(
                float(
                    skill_gap.overall_match_score
                )
                if skill_gap.overall_match_score
                is not None
                else None
            ),
        )

    # -------------------------------------------------
    # 5. Interviews + Preparation
    # -------------------------------------------------

    interviews = (
        db.query(Interview)
        .filter(
            Interview.application_id
            == application.id
        )
        .order_by(
            Interview.scheduled_at.asc().nullslast()
        )
        .all()
    )

    interview_data = []

    for interview in interviews:

        preparation = (
            db.query(
                InterviewPreparation
            )
            .filter(
                InterviewPreparation.application_id
                == application.id,
                InterviewPreparation.user_id
                == current_user.id,
            )
            .first()
        )

        preparation_data = None

        if preparation:
            preparation_data = (
                WorkspaceInterviewPreparation(
                    id=preparation.id,
                    preparation_type=(
                        preparation.preparation_type
                    ),
                    questions=(
                        preparation.questions
                    ),
                    suggested_answers=(
                        preparation.suggested_answers
                    ),
                    strengths=(
                        preparation.strengths
                    ),
                    improvement_areas=(
                        preparation.improvement_areas
                    ),
                    recommendations=(
                        preparation.recommendations
                    ),
                )
            )

        interview_data.append(
            WorkspaceInterview(
                id=interview.id,
                interview_type=(
                    interview.interview_type
                ),
                scheduled_at=(
                    interview.scheduled_at
                ),
                duration_minutes=(
                    interview.duration_minutes
                ),
                meeting_url=(
                    interview.meeting_url
                ),
                location=(
                    interview.location
                ),
                notes=interview.notes,
                status=interview.status,
                preparation=preparation_data,
            )
        )

    # -------------------------------------------------
    # 6. Build application response
    # -------------------------------------------------

    application_data = WorkspaceApplication(
        id=application.id,
        user_id=application.user_id,
        job_id=application.job_id,
        resume_id=application.resume_id,
        status=application.status,
        cover_letter=application.cover_letter,
        applied_at=application.applied_at,
        updated_at=application.updated_at,
    )

    job_data = WorkspaceJob(
        id=job.id,
        title=job.title,
        description=job.description,
        location=job.location,
        employment_type=job.employment_type,
        experience_level=job.experience_level,
        salary_min=(
            float(job.salary_min)
            if job.salary_min is not None
            else None
        ),
        salary_max=(
            float(job.salary_max)
            if job.salary_max is not None
            else None
        ),
        currency=job.currency,
    )

    return ApplicationWorkspaceResponse(
        application=application_data,
        job=job_data,
        resume=resume_data,
        skill_gap=skill_gap_data,
        interviews=interview_data,
    )