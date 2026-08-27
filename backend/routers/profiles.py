from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from dependencies import get_db
from dependencies.auth import get_current_user
from dependencies.roles import require_role
from models.profile import Profile
from models.user import User
from schemas.profile import (
    ProfileCreate,
    ProfileResponse,
    ProfileUpdate,
)


router = APIRouter(
    prefix="/profiles",
    tags=["Profiles"],
)


@router.post(
    "",
    response_model=ProfileResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_profile(
    profile_data: ProfileCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("CANDIDATE")
    ),
):
    existing_profile = (
        db.query(Profile)
        .filter(
            Profile.user_id == current_user.id
        )
        .first()
    )

    if existing_profile:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Profile already exists",
        )

    profile = Profile(
        user_id=current_user.id,
        **profile_data.model_dump(),
    )

    db.add(profile)
    db.commit()
    db.refresh(profile)

    return profile


@router.get(
    "/me",
    response_model=ProfileResponse,
)
def get_my_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("CANDIDATE")
    ),
):
    profile = (
        db.query(Profile)
        .filter(
            Profile.user_id == current_user.id
        )
        .first()
    )

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found",
        )

    return profile


@router.put(
    "/me",
    response_model=ProfileResponse,
)
def update_my_profile(
    profile_data: ProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("CANDIDATE")
    ),
):
    profile = (
        db.query(Profile)
        .filter(
            Profile.user_id == current_user.id
        )
        .first()
    )

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found",
        )

    update_data = profile_data.model_dump(
        exclude_unset=True
    )

    for field, value in update_data.items():
        setattr(profile, field, value)

    db.commit()
    db.refresh(profile)

    return profile