from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from dependencies import get_db
from dependencies.auth import get_current_user
from dependencies.roles import require_role

from models.job import Job
from models.job_screening_question import (
    JobScreeningQuestion,
)
from models.user import User

from schemas.job_screening_question import (
    JobScreeningQuestionCreate,
    JobScreeningQuestionResponse,
    JobScreeningQuestionUpdate,
)


router = APIRouter(
    prefix="/jobs",
    tags=["Job Screening Questions"],
)


# ==================================================
# Recruiter/Admin: Create Screening Question
# ==================================================

@router.post(
    "/{job_id}/screening-questions",
    response_model=JobScreeningQuestionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_screening_question(
    job_id: UUID,
    question_data: JobScreeningQuestionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("RECRUITER", "ADMIN")
    ),
):
    job = (
        db.query(Job)
        .filter(
            Job.id == job_id,
            Job.posted_by == current_user.id,
        )
        .first()
    )

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )

    question = JobScreeningQuestion(
        job_id=job_id,
        **question_data.model_dump(),
    )

    db.add(question)
    db.commit()
    db.refresh(question)

    return question


# ==================================================
# Shared: Get Screening Questions
# ==================================================

@router.get(
    "/{job_id}/screening-questions",
    response_model=list[
        JobScreeningQuestionResponse
    ],
)
def get_screening_questions(
    job_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    job = (
        db.query(Job)
        .filter(
            Job.id == job_id
        )
        .first()
    )

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )

    return (
        db.query(JobScreeningQuestion)
        .filter(
            JobScreeningQuestion.job_id
            == job_id
        )
        .order_by(
            JobScreeningQuestion.display_order.asc()
        )
        .all()
    )


# ==================================================
# Recruiter/Admin: Update Own Job Question
# ==================================================

@router.put(
    "/{job_id}/screening-questions/{question_id}",
    response_model=JobScreeningQuestionResponse,
)
def update_screening_question(
    job_id: UUID,
    question_id: UUID,
    question_data: JobScreeningQuestionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("RECRUITER", "ADMIN")
    ),
):
    question = (
        db.query(JobScreeningQuestion)
        .join(
            Job,
            Job.id
            == JobScreeningQuestion.job_id,
        )
        .filter(
            JobScreeningQuestion.id
            == question_id,
            JobScreeningQuestion.job_id
            == job_id,
            Job.posted_by
            == current_user.id,
        )
        .first()
    )

    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Screening question not found",
        )

    update_data = question_data.model_dump(
        exclude_unset=True
    )

    for field, value in update_data.items():
        setattr(
            question,
            field,
            value,
        )

    db.commit()
    db.refresh(question)

    return question


# ==================================================
# Recruiter/Admin: Delete Own Job Question
# ==================================================

@router.delete(
    "/{job_id}/screening-questions/{question_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_screening_question(
    job_id: UUID,
    question_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("RECRUITER", "ADMIN")
    ),
):
    question = (
        db.query(JobScreeningQuestion)
        .join(
            Job,
            Job.id
            == JobScreeningQuestion.job_id,
        )
        .filter(
            JobScreeningQuestion.id
            == question_id,
            JobScreeningQuestion.job_id
            == job_id,
            Job.posted_by
            == current_user.id,
        )
        .first()
    )

    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Screening question not found",
        )

    db.delete(question)
    db.commit()

    return None