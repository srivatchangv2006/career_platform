from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from dependencies import get_db
from dependencies.auth import get_current_user
from models.application import Application
from models.application_answer import ApplicationAnswer
from models.job_screening_question import JobScreeningQuestion
from models.user import User
from schemas.application_answer import (
    ApplicationAnswerCreate,
    ApplicationAnswerResponse,
    ApplicationAnswerUpdate,
)

router = APIRouter(
    prefix="/applications",
    tags=["Application Answers"],
)


@router.post(
    "/{application_id}/answers",
    response_model=ApplicationAnswerResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_application_answer(
    application_id: UUID,
    answer_data: ApplicationAnswerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
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

    question = (
        db.query(JobScreeningQuestion)
        .filter(
            JobScreeningQuestion.id == answer_data.question_id,
            JobScreeningQuestion.job_id == application.job_id,
        )
        .first()
    )

    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Screening question not found for this job",
        )

    existing_answer = (
        db.query(ApplicationAnswer)
        .filter(
            ApplicationAnswer.application_id == application_id,
            ApplicationAnswer.question_id == answer_data.question_id,
        )
        .first()
    )

    if existing_answer:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Answer already exists for this question",
        )

    answer = ApplicationAnswer(
        application_id=application_id,
        question_id=answer_data.question_id,
        answer=answer_data.answer,
    )

    db.add(answer)
    db.commit()
    db.refresh(answer)

    return answer


@router.get(
    "/{application_id}/answers",
    response_model=list[ApplicationAnswerResponse],
)
def get_application_answers(
    application_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
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

    return (
        db.query(ApplicationAnswer)
        .filter(ApplicationAnswer.application_id == application_id)
        .order_by(ApplicationAnswer.created_at.asc())
        .all()
    )


@router.put(
    "/{application_id}/answers/{question_id}",
    response_model=ApplicationAnswerResponse,
)
def update_application_answer(
    application_id: UUID,
    question_id: UUID,
    answer_data: ApplicationAnswerUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
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

    answer = (
        db.query(ApplicationAnswer)
        .filter(
            ApplicationAnswer.application_id == application_id,
            ApplicationAnswer.question_id == question_id,
        )
        .first()
    )

    if not answer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application answer not found",
        )

    answer.answer = answer_data.answer

    db.commit()
    db.refresh(answer)

    return answer