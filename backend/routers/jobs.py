from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from dependencies import get_db
from dependencies.auth import get_current_user
from dependencies.roles import require_role

from models.job import Job
from models.user import User

from schemas.job import (
    JobCreate,
    JobResponse,
    JobUpdate,
)


router = APIRouter(
    prefix="/jobs",
    tags=["Jobs"],
)


# ==================================================
# Recruiter/Admin: Create Job
# ==================================================

@router.post(
    "",
    response_model=JobResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_job(
    job_data: JobCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("RECRUITER", "ADMIN")
    ),
):
    job = Job(
        posted_by=current_user.id,
        **job_data.model_dump(),
    )

    db.add(job)
    db.commit()
    db.refresh(job)

    return job


# ==================================================
# Shared: Browse Jobs
# ==================================================

@router.get(
    "",
    response_model=list[JobResponse],
)
def get_jobs(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    return (
        db.query(Job)
        .order_by(
            Job.created_at.desc()
        )
        .all()
    )


# ==================================================
# Shared: Get Job
# ==================================================

@router.get(
    "/{job_id}",
    response_model=JobResponse,
)
def get_job(
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

    return job


# ==================================================
# Recruiter/Admin: Update Own Job
# ==================================================

@router.put(
    "/{job_id}",
    response_model=JobResponse,
)
def update_job(
    job_id: UUID,
    job_data: JobUpdate,
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

    update_data = job_data.model_dump(
        exclude_unset=True
    )

    for field, value in update_data.items():
        setattr(
            job,
            field,
            value,
        )

    db.commit()
    db.refresh(job)

    return job