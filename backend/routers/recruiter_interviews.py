from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from dependencies import get_db
from dependencies.roles import require_role

from models.application import Application
from models.interview import Interview
from models.job import Job
from models.user import User

from schemas.interview import InterviewResponse
from schemas.recruiter_interview import (
    RecruiterInterviewCreate,
    RecruiterInterviewUpdate,
)


router = APIRouter(
    prefix="/recruiter/interviews",
    tags=["Recruiter Interviews"],
)


# ============================================================
# Allowed recruiter-managed interview statuses
# ============================================================

ALLOWED_INTERVIEW_STATUSES = {
    "SCHEDULED",
    "CONFIRMED",
    "COMPLETED",
    "CANCELLED",
    "RESCHEDULED",
}


# ============================================================
# Helper: get an application that belongs to a job owned
# by the current recruiter.
# ============================================================

def get_owned_application(
    db: Session,
    application_id: UUID,
    recruiter_id: UUID,
) -> Application | None:
    return (
        db.query(Application)
        .join(
            Job,
            Job.id == Application.job_id,
        )
        .filter(
            Application.id == application_id,
            Job.posted_by == recruiter_id,
        )
        .first()
    )


# ============================================================
# Helper: get an interview through an application whose job
# belongs to the current recruiter.
# ============================================================

def get_owned_interview(
    db: Session,
    interview_id: UUID,
    recruiter_id: UUID,
) -> Interview | None:
    return (
        db.query(Interview)
        .join(
            Application,
            Application.id == Interview.application_id,
        )
        .join(
            Job,
            Job.id == Application.job_id,
        )
        .filter(
            Interview.id == interview_id,
            Job.posted_by == recruiter_id,
        )
        .first()
    )


# ============================================================
# CREATE INTERVIEW
# ============================================================

@router.post(
    "",
    response_model=InterviewResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_recruiter_interview(
    interview_data: RecruiterInterviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("RECRUITER")
    ),
):
    # --------------------------------------------------------
    # 1. Verify recruiter owns the application's job.
    # --------------------------------------------------------

    application = get_owned_application(
        db=db,
        application_id=interview_data.application_id,
        recruiter_id=current_user.id,
    )

    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found",
        )

    # --------------------------------------------------------
    # 2. Validate duration.
    # --------------------------------------------------------

    if (
        interview_data.duration_minutes is not None
        and interview_data.duration_minutes <= 0
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Duration must be greater than 0 minutes",
        )

    # --------------------------------------------------------
    # 3. Validate interview status.
    # --------------------------------------------------------

    if (
        interview_data.status
        not in ALLOWED_INTERVIEW_STATUSES
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Invalid interview status. "
                f"Allowed values: "
                f"{sorted(ALLOWED_INTERVIEW_STATUSES)}"
            ),
        )

    # --------------------------------------------------------
    # 4. Create interview.
    #
    # application_id is intentionally taken from the verified
    # application and cannot point outside recruiter scope.
    # --------------------------------------------------------

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


# ============================================================
# GET ALL INTERVIEWS FOR RECRUITER-OWNED JOBS
# ============================================================

@router.get(
    "",
    response_model=list[InterviewResponse],
)
def get_recruiter_interviews(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("RECRUITER")
    ),
):
    return (
        db.query(Interview)
        .join(
            Application,
            Application.id == Interview.application_id,
        )
        .join(
            Job,
            Job.id == Application.job_id,
        )
        .filter(
            Job.posted_by == current_user.id
        )
        .order_by(
            Interview.scheduled_at.asc().nullslast(),
            Interview.created_at.desc(),
        )
        .all()
    )


# ============================================================
# GET ONE INTERVIEW
# ============================================================

@router.get(
    "/{interview_id}",
    response_model=InterviewResponse,
)
def get_recruiter_interview(
    interview_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("RECRUITER")
    ),
):
    interview = get_owned_interview(
        db=db,
        interview_id=interview_id,
        recruiter_id=current_user.id,
    )

    if not interview:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview not found",
        )

    return interview


# ============================================================
# UPDATE INTERVIEW
#
# application_id is intentionally NOT part of the update
# schema, preventing a recruiter from moving an interview
# from one application to another.
# ============================================================

@router.put(
    "/{interview_id}",
    response_model=InterviewResponse,
)
def update_recruiter_interview(
    interview_id: UUID,
    interview_data: RecruiterInterviewUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("RECRUITER")
    ),
):
    interview = get_owned_interview(
        db=db,
        interview_id=interview_id,
        recruiter_id=current_user.id,
    )

    if not interview:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview not found",
        )

    update_data = interview_data.model_dump(
        exclude_unset=True
    )

    # --------------------------------------------------------
    # Validate duration if supplied.
    # --------------------------------------------------------

    if (
        "duration_minutes" in update_data
        and update_data["duration_minutes"] is not None
        and update_data["duration_minutes"] <= 0
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Duration must be greater than 0 minutes",
        )

    # --------------------------------------------------------
    # Validate status if supplied.
    # --------------------------------------------------------

    if "status" in update_data:
        if (
            update_data["status"]
            not in ALLOWED_INTERVIEW_STATUSES
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Invalid interview status. "
                    f"Allowed values: "
                    f"{sorted(ALLOWED_INTERVIEW_STATUSES)}"
                ),
            )

    # --------------------------------------------------------
    # Apply update.
    # --------------------------------------------------------

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


# ============================================================
# DELETE INTERVIEW
# ============================================================

@router.delete(
    "/{interview_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_recruiter_interview(
    interview_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("RECRUITER")
    ),
):
    interview = get_owned_interview(
        db=db,
        interview_id=interview_id,
        recruiter_id=current_user.id,
    )

    if not interview:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview not found",
        )

    db.delete(interview)
    db.commit()

    return None
