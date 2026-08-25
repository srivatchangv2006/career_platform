from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from auth import authenticate_user, create_access_token
from dependencies import get_db
from models.user import User
from schemas.auth import LoginRequest, TokenResponse
from schemas.user import UserCreate, UserResponse
from security import hash_password
from dependencies.auth import get_current_user
from dependencies.roles import require_role


router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
):
    existing_user = db.query(User).filter(
        User.email == user_data.email
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    new_user = User(
        email=user_data.email,
        password_hash=hash_password(user_data.password),
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "id": str(new_user.id),
        "email": new_user.email,
        "role": new_user.role,
        "status": new_user.status,
    }


@router.post(
    "/login",
    response_model=TokenResponse,
)
def login_user(
    login_data: LoginRequest,
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(
        User.email == login_data.email
    ).first()

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

@router.get("/me")
def get_my_profile(
    current_user: User = Depends(get_current_user),
):
    return {
        "id": str(current_user.id),
        "email": current_user.email,
        "role": current_user.role,
        "status": current_user.status,
    }

@router.get("/candidate-only")
def candidate_only(
    current_user: User = Depends(
        require_role("CANDIDATE")
    ),
):
    return {
        "message": "Candidate access granted",
        "user_id": str(current_user.id),
        "role": current_user.role,
    }