from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from dependencies import get_db
from dependencies.auth import get_current_user

from models.user import User
from models.user_follows import UserFollow

from schemas.network import NetworkUserResponse
from schemas.user_follow import UserFollowResponse

from services.public_user import (
    get_public_user,
)


router = APIRouter(
    prefix="/user-follows",
    tags=["User Follows"],
)


def build_follow_response(
    db: Session,
    follow: UserFollow,
) -> UserFollowResponse:
    return UserFollowResponse(
        follower_id=follow.follower_id,
        following_id=follow.following_id,
        created_at=follow.created_at,
        follower=get_public_user(
            db,
            follow.follower_id,
        ),
        following=get_public_user(
            db,
            follow.following_id,
        ),
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
        .filter(
            User.id == user_id,
        )
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
            UserFollow.follower_id
            == current_user.id,
            UserFollow.following_id
            == user_id,
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

    return build_follow_response(
        db,
        follow,
    )


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
            UserFollow.follower_id
            == current_user.id,
            UserFollow.following_id
            == user_id,
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
    q: str | None = Query(
        default=None,
        min_length=2,
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = (
        db.query(UserFollow)
        .filter(
            UserFollow.follower_id
            == current_user.id
        )
    )

    follows = (
        query
        .order_by(
            UserFollow.created_at.desc()
        )
        .all()
    )

    results = []

    for follow in follows:
        following = get_public_user(
            db,
            follow.following_id,
        )

        if not following:
            continue

        if q:
            search = q.strip().lower()

            searchable = " ".join(
                [
                    following["display_name"],
                    following["handle"],
                    following["role"],
                    following["headline"] or "",
                    following["location"] or "",
                    following["company_name"] or "",
                ]
            ).lower()

            if search not in searchable:
                continue

        results.append(
            UserFollowResponse(
                follower_id=follow.follower_id,
                following_id=follow.following_id,
                created_at=follow.created_at,
                follower=get_public_user(
                    db,
                    follow.follower_id,
                ),
                following=following,
            )
        )

    return results


@router.get(
    "/{user_id}",
    response_model=list[UserFollowResponse],
)
def get_user_followers(
    user_id: UUID,
    q: str | None = Query(
        default=None,
        min_length=2,
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    target_user = (
        db.query(User)
        .filter(
            User.id == user_id,
        )
        .first()
    )

    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    follows = (
        db.query(UserFollow)
        .filter(
            UserFollow.following_id
            == user_id
        )
        .order_by(
            UserFollow.created_at.desc()
        )
        .all()
    )

    results = []

    for follow in follows:
        follower = get_public_user(
            db,
            follow.follower_id,
        )

        following = get_public_user(
            db,
            follow.following_id,
        )

        if not follower:
            continue

        if q:
            search = q.strip().lower()

            searchable = " ".join(
                [
                    follower["display_name"],
                    follower["handle"],
                    follower["role"],
                    follower["headline"] or "",
                    follower["location"] or "",
                    follower["company_name"] or "",
                ]
            ).lower()

            if search not in searchable:
                continue

        results.append(
            UserFollowResponse(
                follower_id=follow.follower_id,
                following_id=follow.following_id,
                created_at=follow.created_at,
                follower=follower,
                following=following,
            )
        )

    return results
