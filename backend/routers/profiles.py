from decimal import Decimal
from uuid import UUID
from dependencies.auth import get_current_user
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from dependencies import get_db
from dependencies.roles import require_role

from models.community_posts import CommunityPost
from models.company import Company
from models.profile import Profile
from models.recruiter_profile import RecruiterProfile
from models.user import User

from schemas.profile import (
    ProfileCreate,
    ProfileResponse,
    ProfileUpdate,
)
from schemas.public_profile import (
    PublicCompany,
    PublicPost,
    PublicProfileResponse,
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


@router.get(
    "/{user_id}",
    response_model=PublicProfileResponse,
)
def get_public_profile(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    user = (
        db.query(User)
        .filter(
            User.id == user_id
        )
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # --------------------------------------------------------
    # Candidate profile
    # --------------------------------------------------------

    candidate_profile = (
        db.query(Profile)
        .filter(
            Profile.user_id == user.id
        )
        .first()
    )

    # --------------------------------------------------------
    # Recruiter profile
    # --------------------------------------------------------

    recruiter_profile = (
        db.query(RecruiterProfile)
        .filter(
            RecruiterProfile.user_id == user.id
        )
        .first()
    )

    # --------------------------------------------------------
    # Company for recruiter
    # --------------------------------------------------------

    company_data = None

    if recruiter_profile:
        company = (
            db.query(Company)
            .filter(
                Company.id
                == recruiter_profile.company_id
            )
            .first()
        )

        if company:
            company_data = PublicCompany(
                id=company.id,
                name=company.name,
                slug=company.slug,
                description=company.description,
                website_url=company.website_url,
                logo_blob_path=company.logo_blob_path,
                industry=company.industry,
                company_size=company.company_size,
                location=company.location,
            )

    # --------------------------------------------------------
    # Community posts
    # --------------------------------------------------------

    posts = (
        db.query(CommunityPost)
        .filter(
            CommunityPost.user_id == user.id
        )
        .order_by(
            CommunityPost.created_at.desc()
        )
        .all()
    )

    public_posts = [
        PublicPost(
            id=post.id,
            user_id=post.user_id,
            title=post.title,
            content=post.content,
        )
        for post in posts
    ]

    # --------------------------------------------------------
    # Build public profile
    # --------------------------------------------------------

    return PublicProfileResponse(
        user_id=user.id,
        email=user.email,
        role=user.role.value
        if hasattr(user.role, "value")
        else str(user.role),

        full_name=(
            candidate_profile.full_name
            if candidate_profile
            else None
        ),
        headline=(
            candidate_profile.headline
            if candidate_profile
            else None
        ),
        bio=(
            candidate_profile.bio
            if candidate_profile
            else (
                recruiter_profile.bio
                if recruiter_profile
                else None
            )
        ),
        location=(
            candidate_profile.location
            if candidate_profile
            else None
        ),
        years_of_experience=(
            float(candidate_profile.years_of_experience)
            if (
                candidate_profile
                and candidate_profile.years_of_experience
                is not None
            )
            else None
        ),
        profile_image_blob_path=(
            candidate_profile.profile_image_blob_path
            if candidate_profile
            else None
        ),
        designation=(
            recruiter_profile.designation
            if recruiter_profile
            else None
        ),
        company=company_data,
        posts=public_posts,
    )
