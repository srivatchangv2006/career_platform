from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from dependencies import get_db
from dependencies.auth import get_current_user

from models.user import User
from models.user_follows import UserFollow

from schemas.user_follow import UserFollowResponse


router = APIRouter(
    prefix="/user-follows",
    tags=["User Follows"],
)


@router.post(
    "/{user_id}",
    response_model=UserFollowResponse,
    status_code=status.HTTP_201_CREATED,
)
def follow_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot follow yourself",
        )

    target_user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    existing_follow = (
        db.query(UserFollow)
        .filter(
            UserFollow.follower_id == current_user.id,
            UserFollow.following_id == user_id,
        )
        .first()
    )

    if existing_follow:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You are already following this user",
        )

    follow = UserFollow(
        follower_id=current_user.id,
        following_id=user_id,
    )

    db.add(follow)
    db.commit()
    db.refresh(follow)

    return follow


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def unfollow_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    follow = (
        db.query(UserFollow)
        .filter(
            UserFollow.follower_id == current_user.id,
            UserFollow.following_id == user_id,
        )
        .first()
    )

    if not follow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Follow relationship not found",
        )

    db.delete(follow)
    db.commit()

    return None


@router.get(
    "/me",
    response_model=list[UserFollowResponse],
)
def get_my_following(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return (
        db.query(UserFollow)
        .filter(
            UserFollow.follower_id == current_user.id
        )
        .order_by(
            UserFollow.created_at.desc()
        )
        .all()
    )


@router.get(
    "/{user_id}",
    response_model=list[UserFollowResponse],
)
def get_user_followers(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    target_user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return (
        db.query(UserFollow)
        .filter(
            UserFollow.following_id == user_id
        )
        .order_by(
            UserFollow.created_at.desc()
        )
        .all()
    )
