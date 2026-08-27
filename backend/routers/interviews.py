from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from dependencies import get_db
from dependencies.roles import require_role

from models.application import Application
from models.interview import Interview
from models.user import User

from schemas.interview import (
    InterviewCreate,
    InterviewResponse,
    InterviewUpdate,
)


router = APIRouter(
    prefix="/interviews",
    tags=["Interviews"],
    dependencies=[
        Depends(require_role("CANDIDATE"))
    ],
)


@router.post(
    "",
    response_model=InterviewResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_interview(
    interview_data: InterviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("CANDIDATE")
    ),
):
    application = (
        db.query(Application)
        .filter(
            Application.id
            == interview_data.application_id,
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

    if (
        interview_data.duration_minutes is not None
        and interview_data.duration_minutes <= 0
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Duration must be greater than 0 minutes",
        )

    interview = Interview(
        application_id=application.id,
        interviewer_id=interview_data.interviewer_id,
        interview_type=interview_data.interview_type,
        scheduled_at=interview_data.scheduled_at,
        duration_minutes=(
            interview_data.duration_minutes
        ),
        meeting_url=interview_data.meeting_url,
        location=interview_data.location,
        notes=interview_data.notes,
        status=interview_data.status,
    )

    db.add(interview)
    db.commit()
    db.refresh(interview)

    return interview


@router.get(
    "/me",
    response_model=list[InterviewResponse],
)
def get_my_interviews(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("CANDIDATE")
    ),
):
    return (
        db.query(Interview)
        .join(
            Application,
            Application.id
            == Interview.application_id,
        )
        .filter(
            Application.user_id
            == current_user.id
        )
        .order_by(
            Interview.scheduled_at.asc().nullslast(),
            Interview.created_at.desc(),
        )
        .all()
    )


@router.get(
    "/{interview_id}",
    response_model=InterviewResponse,
)
def get_interview(
    interview_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("CANDIDATE")
    ),
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

    return interview


@router.put(
    "/{interview_id}",
    response_model=InterviewResponse,
)
def update_interview(
    interview_id: UUID,
    interview_data: InterviewUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("CANDIDATE")
    ),
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

    update_data = interview_data.model_dump(
        exclude_unset=True
    )

    if (
        "duration_minutes" in update_data
        and update_data["duration_minutes"] is not None
        and update_data["duration_minutes"] <= 0
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Duration must be greater than 0 minutes",
        )

    for field, value in update_data.items():
        setattr(
            interview,
            field,
            value,
        )

    interview.updated_at = datetime.now(
        timezone.utc
    )

    db.commit()
    db.refresh(interview)

    return interview


@router.delete(
    "/{interview_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_interview(
    interview_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("CANDIDATE")
    ),
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

    db.delete(interview)
    db.commit()

    return None