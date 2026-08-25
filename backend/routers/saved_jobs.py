from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from dependencies import get_db
from dependencies.auth import get_current_user
from models.job import Job
from models.saved_job import SavedJob
from models.user import User
from schemas.saved_job import SavedJobResponse

router = APIRouter(
    prefix="/saved-jobs",
    tags=["Saved Jobs"],
)


@router.post(
    "/{job_id}",
    response_model=SavedJobResponse,
    status_code=status.HTTP_201_CREATED,
)
def save_job(
    job_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Check that the job exists
    job = (
        db.query(Job)
        .filter(Job.id == job_id)
        .first()
    )

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )

    # Check if already saved
    existing = (
        db.query(SavedJob)
        .filter(
            SavedJob.user_id == current_user.id,
            SavedJob.job_id == job_id,
        )
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Job already saved",
        )

    saved_job = SavedJob(
        user_id=current_user.id,
        job_id=job_id,
    )

    db.add(saved_job)
    db.commit()
    db.refresh(saved_job)

    return saved_job


@router.get(
    "",
    response_model=list[SavedJobResponse],
)
def get_saved_jobs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return (
        db.query(SavedJob)
        .filter(SavedJob.user_id == current_user.id)
        .order_by(SavedJob.created_at.desc())
        .all()
    )


@router.delete(
    "/{job_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def unsave_job(
    job_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    saved_job = (
        db.query(SavedJob)
        .filter(
            SavedJob.user_id == current_user.id,
            SavedJob.job_id == job_id,
        )
        .first()
    )

    if not saved_job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Saved job not found",
        )

    db.delete(saved_job)
    db.commit()

    return None