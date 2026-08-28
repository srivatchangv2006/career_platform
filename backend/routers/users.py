from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_

from models.profile import Profile
from models.recruiter_profile import RecruiterProfile

from schemas.user_search import UserSearchResult
from auth import authenticate_user, create_access_token
from dependencies import get_db
from dependencies.auth import get_current_user
from dependencies.roles import require_role
from models.user import User
from schemas.auth import LoginRequest, TokenResponse
from schemas.user import UserCreate, UserResponse
from security import hash_password


router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


# ============================================================
# REGISTER USER
#
# Public registration endpoint.
#
# Allowed roles:
#   - CANDIDATE
#   - RECRUITER
#
# ADMIN cannot be created through public registration.
# ============================================================

@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
):
    # --------------------------------------------------------
    # Check whether the email already exists.
    # --------------------------------------------------------

    existing_user = (
        db.query(User)
        .filter(
            User.email == user_data.email
        )
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    # --------------------------------------------------------
    # Create the user.
    #
    # UserCreate only permits:
    #   CANDIDATE
    #   RECRUITER
    #
    # ADMIN cannot be created through this endpoint.
    # --------------------------------------------------------

    new_user = User(
        email=user_data.email,
        password_hash=hash_password(
            user_data.password
        ),
        role=user_data.role.value,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # --------------------------------------------------------
    # Return all fields required by UserResponse.
    #
    # The previous implementation omitted "status",
    # which caused FastAPI to return 500 after successfully
    # inserting the user into PostgreSQL.
    # --------------------------------------------------------

    return {
        "id": str(new_user.id),
        "email": new_user.email,
        "role": (
            new_user.role.value
            if hasattr(
                new_user.role,
                "value",
            )
            else str(new_user.role)
        ),
        "status": (
            new_user.status.value
            if hasattr(
                new_user.status,
                "value",
            )
            else str(new_user.status)
        ),
    }


# ============================================================
# LOGIN
# ============================================================

@router.post(
    "/login",
    response_model=TokenResponse,
)
def login_user(
    login_data: LoginRequest,
    db: Session = Depends(get_db),
):
    user = (
        db.query(User)
        .filter(
            User.email == login_data.email
        )
        .first()
    )

    authenticated_user = authenticate_user(
        user,
        login_data.password,
    )

    if authenticated_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    access_token = create_access_token(
        str(authenticated_user.id)
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


# ============================================================
# GET CURRENT USER
# ============================================================

@router.get("/me")
def get_my_profile(
    current_user: User = Depends(
        get_current_user
    ),
):
    role = (
        current_user.role.value
        if hasattr(
            current_user.role,
            "value",
        )
        else str(current_user.role)
    )

    user_status = (
        current_user.status.value
        if hasattr(
            current_user.status,
            "value",
        )
        else str(current_user.status)
    )

    return {
        "id": str(current_user.id),
        "email": current_user.email,
        "role": role,
        "status": user_status,
    }

@router.get(
    "/search",
    response_model=list[UserSearchResult],
)
def search_users(
    q: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    search_term = q.strip()

    if len(search_term) < 2:
        return []

    pattern = f"%{search_term}%"

    rows = (
        db.query(
            User,
            Profile,
            RecruiterProfile,
        )
        .outerjoin(
            Profile,
            Profile.user_id == User.id,
        )
        .outerjoin(
            RecruiterProfile,
            RecruiterProfile.user_id == User.id,
        )
        .filter(
            User.id != current_user.id,
            User.status == "ACTIVE",
            or_(
                User.email.ilike(pattern),
                Profile.full_name.ilike(pattern),
                Profile.headline.ilike(pattern),
                RecruiterProfile.designation.ilike(
                    pattern
                ),
            ),
        )
        .order_by(
            User.created_at.desc()
        )
        .limit(20)
        .all()
    )

    results = []

    for (
        user,
        profile,
        recruiter_profile,
    ) in rows:
        role = (
            user.role.value
            if hasattr(user.role, "value")
            else str(user.role)
        )

        email_prefix = (
            str(user.email)
            .split("@")[0]
            .strip()
        )

        # Candidate display information
        if profile:
            display_name = (
                profile.full_name
            )

            headline = (
                profile.headline
            )

            location = (
                profile.location
            )

            profile_image = (
                profile.profile_image_blob_path
            )

        # Recruiter / fallback information
        elif recruiter_profile:
            display_name = email_prefix

            headline = (
                recruiter_profile.designation
            )

            location = None
            profile_image = None

        else:
            display_name = email_prefix
            headline = None
            location = None
            profile_image = None

        results.append(
            UserSearchResult(
                id=user.id,
                display_name=display_name,
                handle=f"@{email_prefix}",
                role=role,
                headline=headline,
                location=location,
                profile_image_blob_path=profile_image,
            )
        )

    return results
# ============================================================
# CANDIDATE-ONLY TEST ENDPOINT
# ============================================================

@router.get("/candidate-only")
def candidate_only(
    current_user: User = Depends(
        require_role("CANDIDATE")
    ),
):
    role = (
        current_user.role.value
        if hasattr(
            current_user.role,
            "value",
        )
        else str(current_user.role)
    )

    return {
        "message": "Candidate access granted",
        "user_id": str(current_user.id),
        "role": role,
    }
