from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from dependencies import get_db
from dependencies.auth import get_current_user
from dependencies.roles import require_role
from models.application import Application
from models.interview import Interview
from models.interview_preparation import InterviewPreparation
from models.job import Job
from models.skill import Skill
from models.user import User
from models.user_skill import UserSkill

from schemas.interview_preparation import (
    InterviewPreparationResponse,
)

from services.ai_interaction_service import (
    log_ai_interaction,
)

from services.interview_preparer import (
    generate_interview_preparation,
)

from services.memory_service import (
    create_or_update_memory,
    search_user_memories,
)


router = APIRouter(
    prefix="/interviews",
    tags=["Interview Preparation"],
    dependencies=[
        Depends(require_role("CANDIDATE"))
    ],
)


@router.post(
    "/{interview_id}/prepare",
    response_model=InterviewPreparationResponse,
    status_code=status.HTTP_201_CREATED,
)
def prepare_interview(
    interview_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # -------------------------------------------------
    # 1. Find interview belonging to current user
    # -------------------------------------------------

    interview = (
        db.query(Interview)
        .join(
            Application,
            Application.id
            == Interview.application_id,
        )
        .filter(
            Interview.id == interview_id,
            Application.user_id
            == current_user.id,
        )
        .first()
    )

    if not interview:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview not found",
        )

    # -------------------------------------------------
    # 2. Find application
    # -------------------------------------------------

    application = (
        db.query(Application)
        .filter(
            Application.id
            == interview.application_id,
            Application.user_id
            == current_user.id,
        )
        .first()
    )

    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found",
        )

    # -------------------------------------------------
    # 3. Find job
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
    # 4. Get candidate skills
    # -------------------------------------------------

    candidate_skills = (
        db.query(Skill.name)
        .join(
            UserSkill,
            UserSkill.skill_id
            == Skill.id,
        )
        .filter(
            UserSkill.user_id
            == current_user.id
        )
        .all()
    )

    candidate_skill_names = [
        skill[0]
        for skill in candidate_skills
    ]

    # -------------------------------------------------
    # 5. Get relevant agent memories
    # -------------------------------------------------

    memory_context = search_user_memories(
        db=db,
        user_id=current_user.id,
        query=(
            "candidate resume, experience, education, "
            "skills, skill gaps, career preferences, "
            "job recommendations, career goals, "
            "previous interview preparation, and "
            "agent feedback"
        ),
        limit=10,
    )

    # -------------------------------------------------
    # 6. Build AI context
    # -------------------------------------------------

    interview_context = {
        "interview": {
            "id": str(interview.id),
            "interview_type": (
                interview.interview_type
            ),
            "scheduled_at": (
                interview.scheduled_at.isoformat()
                if interview.scheduled_at
                else None
            ),
            "duration_minutes": (
                interview.duration_minutes
            ),
            "meeting_url": (
                interview.meeting_url
            ),
            "location": interview.location,
            "notes": interview.notes,
        },
        "application": {
            "id": str(application.id),
            "status": application.status,
            "cover_letter": (
                application.cover_letter
            ),
        },
        "job": {
            "id": str(job.id),
            "title": job.title,
            "description": job.description,
            "location": job.location,
            "employment_type": (
                job.employment_type
            ),
            "experience_level": (
                job.experience_level
            ),
        },
        "candidate_skills": (
            candidate_skill_names
        ),
        "memory_context": memory_context,
    }

    # -------------------------------------------------
    # 7. Call Gemini
    # -------------------------------------------------

    try:
        preparation_data = (
            generate_interview_preparation(
                interview_context
            )
        )

        # -------------------------------------------------
        # 8. Log Gemini interaction
        # -------------------------------------------------

        log_ai_interaction(
            db=db,
            user_id=current_user.id,
            interaction_type=(
                "INTERVIEW_PREPARATION"
            ),
            input_text=str(
                interview_context
            ),
            output_text=str(
                preparation_data
            ),
            model_name="gemini-3.6-flash",
            metadata={
                "agent": (
                    "interview_preparation_agent"
                ),
                "interview_id": (
                    str(interview_id)
                ),
                "application_id": (
                    str(
                        application.id
                    )
                ),
                "job_id": (
                    str(job.id)
                ),
            },
        )

        # -------------------------------------------------
        # 9. Store/update preparation
        # -------------------------------------------------

        existing = (
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

        if existing:

            existing.preparation_type = (
                interview.interview_type
            )

            existing.questions = (
                preparation_data[
                    "questions"
                ]
            )

            existing.suggested_answers = (
                preparation_data[
                    "suggested_answers"
                ]
            )

            existing.strengths = (
                preparation_data[
                    "strengths"
                ]
            )

            existing.improvement_areas = (
                preparation_data[
                    "improvement_areas"
                ]
            )

            existing.recommendations = (
                preparation_data[
                    "recommendations"
                ]
            )

            db.commit()
            db.refresh(existing)

            preparation = existing

        else:

            preparation = InterviewPreparation(
                application_id=application.id,
                user_id=current_user.id,
                preparation_type=(
                    interview.interview_type
                ),
                questions=(
                    preparation_data[
                        "questions"
                    ]
                ),
                suggested_answers=(
                    preparation_data[
                        "suggested_answers"
                    ]
                ),
                strengths=(
                    preparation_data[
                        "strengths"
                    ]
                ),
                improvement_areas=(
                    preparation_data[
                        "improvement_areas"
                    ]
                ),
                recommendations=(
                    preparation_data[
                        "recommendations"
                    ]
                ),
            )

            db.add(preparation)
            db.commit()
            db.refresh(preparation)

        # -------------------------------------------------
        # 10. Store interview-preparation memory
        # -------------------------------------------------

        create_or_update_memory(
            db=db,
            user_id=current_user.id,
            memory_type="INTERVIEW_PREPARATION",
            memory_key=(
                f"application_{application.id}_"
                "interview_preparation"
            ),
            memory_value={
                "interview_id": (
                    str(interview_id)
                ),
                "application_id": (
                    str(application.id)
                ),
                "job_id": str(job.id),
                "questions": (
                    preparation_data[
                        "questions"
                    ]
                ),
                "strengths": (
                    preparation_data[
                        "strengths"
                    ]
                ),
                "improvement_areas": (
                    preparation_data[
                        "improvement_areas"
                    ]
                ),
                "recommendations": (
                    preparation_data[
                        "recommendations"
                    ]
                ),
            },
            source=(
                "interview_preparation_agent"
            ),
            confidence_score=90,
        )

        return preparation

    except Exception as exc:
        db.rollback()

        raise HTTPException(
            status_code=(
                status.HTTP_500_INTERNAL_SERVER_ERROR
            ),
            detail=(
                "Failed to generate interview preparation"
            ),
        ) from exc


@router.get(
    "/{interview_id}/preparation",
    response_model=InterviewPreparationResponse,
)
def get_interview_preparation(
    interview_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    interview = (
        db.query(Interview)
        .join(
            Application,
            Application.id
            == Interview.application_id,
        )
        .filter(
            Interview.id == interview_id,
            Application.user_id
            == current_user.id,
        )
        .first()
    )

    if not interview:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview not found",
        )

    preparation = (
        db.query(InterviewPreparation)
        .filter(
            InterviewPreparation.application_id
            == interview.application_id,
            InterviewPreparation.user_id
            == current_user.id,
        )
        .first()
    )

    if not preparation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                "Interview preparation not found"
            ),
        )

    return preparation