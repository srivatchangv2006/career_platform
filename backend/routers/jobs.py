from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from dependencies import get_db
from dependencies.auth import get_current_user
from dependencies.roles import require_role

from models.company import Company
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


def build_job_response(job, company):
    return JobResponse(
        id=job.id,
        company_id=job.company_id,
        company_name=(
            company.name
            if company
            else None
        ),
        posted_by=job.posted_by,
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
        status=job.status,
        application_deadline=(
            job.application_deadline
        ),
        created_at=job.created_at,
        updated_at=job.updated_at,
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
    company = (
        db.query(Company)
        .filter(
            Company.id
            == job_data.company_id
        )
        .first()
    )

    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found",
        )

    job = Job(
        posted_by=current_user.id,
        **job_data.model_dump(),
    )

    db.add(job)
    db.commit()
    db.refresh(job)

    return build_job_response(
        job,
        company,
    )


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
    rows = (
        db.query(Job, Company)
        .outerjoin(
            Company,
            Company.id == Job.company_id,
        )
        .order_by(
            Job.created_at.desc()
        )
        .all()
    )

    return [
        build_job_response(
            job,
            company,
        )
        for job, company in rows
    ]


# ==================================================
# Recruiter/Admin: Get Own Jobs
# ==================================================

@router.get(
    "/mine",
    response_model=list[JobResponse],
)
def get_my_jobs(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("RECRUITER", "ADMIN")
    ),
):
    rows = (
        db.query(Job, Company)
        .outerjoin(
            Company,
            Company.id == Job.company_id,
        )
        .filter(
            Job.posted_by == current_user.id
        )
        .order_by(
            Job.created_at.desc()
        )
        .all()
    )

    return [
        build_job_response(
            job,
            company,
        )
        for job, company in rows
    ]


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
    row = (
        db.query(Job, Company)
        .outerjoin(
            Company,
            Company.id == Job.company_id,
        )
        .filter(
            Job.id == job_id
        )
        .first()
    )

    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )

    job, company = row

    return build_job_response(
        job,
        company,
    )


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

    if "company_id" in update_data:
        company = (
            db.query(Company)
            .filter(
                Company.id
                == update_data["company_id"]
            )
            .first()
        )

        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Company not found",
            )

    for field, value in update_data.items():
        setattr(
            job,
            field,
            value,
        )

    db.commit()
    db.refresh(job)

    company = (
        db.query(Company)
        .filter(
            Company.id == job.company_id
        )
        .first()
    )

    return build_job_response(
        job,
        company,
    )
