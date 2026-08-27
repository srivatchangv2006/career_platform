from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from dependencies import get_db
from dependencies.roles import require_role

from models.application import Application
from models.job import Job
from models.resume import Resume
from models.user import User

from schemas.application import (
    ApplicationCreate,
    ApplicationResponse,
    ApplicationUpdate,
)


router = APIRouter(
    prefix="/applications",
    tags=["Applications"],
    dependencies=[
        Depends(require_role("CANDIDATE"))
    ],
)


@router.post(
    "",
    response_model=ApplicationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_application(
    application_data: ApplicationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("CANDIDATE")
    ),
):
    job = (
        db.query(Job)
        .filter(
            Job.id == application_data.job_id
        )
        .first()
    )

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )

    if application_data.resume_id:
        resume = (
            db.query(Resume)
            .filter(
                Resume.id
                == application_data.resume_id,
                Resume.user_id
                == current_user.id,
            )
            .first()
        )

        if not resume:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resume not found",
            )

    existing_application = (
        db.query(Application)
        .filter(
            Application.job_id
            == application_data.job_id,
            Application.user_id
            == current_user.id,
        )
        .first()
    )

    if existing_application:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You have already applied to this job",
        )

    application = Application(
        job_id=application_data.job_id,
        user_id=current_user.id,
        resume_id=application_data.resume_id,
        cover_letter=application_data.cover_letter,
    )

    db.add(application)
    db.commit()
    db.refresh(application)

    return application


@router.get(
    "/me",
    response_model=list[ApplicationResponse],
)
def get_my_applications(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("CANDIDATE")
    ),
):
    return (
        db.query(Application)
        .filter(
            Application.user_id
            == current_user.id
        )
        .order_by(
            Application.applied_at.desc()
        )
        .all()
    )


@router.get(
    "/{application_id}",
    response_model=ApplicationResponse,
)
def get_application(
    application_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("CANDIDATE")
    ),
):
    application = (
        db.query(Application)
        .filter(
            Application.id == application_id,
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

    return application


@router.put(
    "/{application_id}",
    response_model=ApplicationResponse,
)
def update_application(
    application_id: UUID,
    application_data: ApplicationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("CANDIDATE")
    ),
):
    application = (
        db.query(Application)
        .filter(
            Application.id == application_id,
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

    if application_data.resume_id:
        resume = (
            db.query(Resume)
            .filter(
                Resume.id
                == application_data.resume_id,
                Resume.user_id
                == current_user.id,
            )
            .first()
        )

        if not resume:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resume not found",
            )

    update_data = application_data.model_dump(
        exclude_unset=True
    )

    for field, value in update_data.items():
        setattr(
            application,
            field,
            value,
        )

    db.commit()
    db.refresh(application)

    return application