from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from dependencies import get_db
from dependencies.roles import require_role

from models.company import Company
from models.recruiter_profile import RecruiterProfile
from models.user import User

from schemas.recruiter_profile import (
    RecruiterProfileCreate,
    RecruiterProfileResponse,
    RecruiterProfileUpdate,
)


router = APIRouter(
    prefix="/recruiter-profiles",
    tags=["Recruiter Profiles"],
)


@router.post(
    "/me",
    response_model=RecruiterProfileResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_recruiter_profile(
    profile_data: RecruiterProfileCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("RECRUITER")
    ),
):
    existing = (
        db.query(RecruiterProfile)
        .filter(
            RecruiterProfile.user_id == current_user.id
        )
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Recruiter profile already exists",
        )

    company = (
        db.query(Company)
        .filter(
            Company.id == profile_data.company_id
        )
        .first()
    )

    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found",
        )

    profile = RecruiterProfile(
        user_id=current_user.id,
        company_id=profile_data.company_id,
        designation=profile_data.designation,
        bio=profile_data.bio,
    )

    db.add(profile)
    db.commit()
    db.refresh(profile)

    return profile


@router.get(
    "/me",
    response_model=RecruiterProfileResponse,
)
def get_my_recruiter_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("RECRUITER")
    ),
):
    profile = (
        db.query(RecruiterProfile)
        .filter(
            RecruiterProfile.user_id == current_user.id
        )
        .first()
    )

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recruiter profile not found",
        )

    return profile


@router.put(
    "/me",
    response_model=RecruiterProfileResponse,
)
def update_my_recruiter_profile(
    profile_data: RecruiterProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("RECRUITER")
    ),
):
    profile = (
        db.query(RecruiterProfile)
        .filter(
            RecruiterProfile.user_id == current_user.id
        )
        .first()
    )

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recruiter profile not found",
        )

    update_data = profile_data.model_dump(
        exclude_unset=True
    )

    if "company_id" in update_data:
        company = (
            db.query(Company)
            .filter(
                Company.id == update_data["company_id"]
            )
            .first()
        )

        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Company not found",
            )

    for field, value in update_data.items():
        setattr(profile, field, value)

    profile.updated_at = datetime.now(
        timezone.utc
    )

    db.commit()
    db.refresh(profile)

    return profile
