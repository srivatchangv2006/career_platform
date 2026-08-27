from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from dependencies import get_db
from dependencies.roles import require_role
from models.job_preference import JobPreference
from models.user import User
from schemas.job_preference import (
    JobPreferenceCreate,
    JobPreferenceResponse,
    JobPreferenceUpdate,
)


router = APIRouter(
    prefix="/job-preferences",
    tags=["Job Preferences"],
    dependencies=[Depends(require_role("CANDIDATE"))],
)


@router.post(
    "",
    response_model=JobPreferenceResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_job_preferences(
    preference_data: JobPreferenceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("CANDIDATE")
    ),
):
    existing = (
        db.query(JobPreference)
        .filter(
            JobPreference.user_id
            == current_user.id
        )
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Job preferences already exist",
        )

    preferences = JobPreference(
        user_id=current_user.id,
        **preference_data.model_dump(),
    )

    db.add(preferences)
    db.commit()
    db.refresh(preferences)

    return preferences


@router.get(
    "",
    response_model=JobPreferenceResponse,
)
def get_job_preferences(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("CANDIDATE")
    ),
):
    preferences = (
        db.query(JobPreference)
        .filter(
            JobPreference.user_id
            == current_user.id
        )
        .first()
    )

    if not preferences:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job preferences not found",
        )

    return preferences


@router.put(
    "",
    response_model=JobPreferenceResponse,
)
def update_job_preferences(
    preference_data: JobPreferenceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("CANDIDATE")
    ),
):
    preferences = (
        db.query(JobPreference)
        .filter(
            JobPreference.user_id
            == current_user.id
        )
        .first()
    )

    if not preferences:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job preferences not found",
        )

    update_data = preference_data.model_dump(
        exclude_unset=True
    )

    for field, value in update_data.items():
        setattr(preferences, field, value)

    db.commit()
    db.refresh(preferences)

    return preferences