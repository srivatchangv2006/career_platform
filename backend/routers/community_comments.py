from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from dependencies import get_db
from dependencies.auth import get_current_user

from models.community_comments import CommunityComment
from models.community_posts import CommunityPost
from models.company import Company
from models.profile import Profile
from models.recruiter_profile import RecruiterProfile
from models.user import User

from schemas.community_comment import (
    CommunityCommentAuthorResponse,
    CommunityCommentCreate,
    CommunityCommentResponse,
    CommunityCommentUpdate,
)


router = APIRouter(
    prefix="/community",
    tags=["Community Comments"],
)


def get_comment_or_404(
    db: Session,
    comment_id: UUID,
) -> CommunityComment:
    comment = (
        db.query(CommunityComment)
        .filter(
            CommunityComment.id == comment_id
        )
        .first()
    )

    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Community comment not found",
        )

    return comment


def get_comment_author(
    db: Session,
    user_id: UUID,
) -> CommunityCommentAuthorResponse:
    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment author not found",
        )

    role = (
        user.role.value
        if hasattr(user.role, "value")
        else str(user.role)
    )

    profile = (
        db.query(Profile)
        .filter(Profile.user_id == user.id)
        .first()
    )

    if profile:
        return CommunityCommentAuthorResponse(
            user_id=user.id,
            role=role,
            display_name=profile.full_name,
            headline=profile.headline,
            designation=None,
            company_name=None,
            profile_image_blob_path=(
                profile.profile_image_blob_path
            ),
        )

    recruiter_profile = (
        db.query(RecruiterProfile)
        .filter(
            RecruiterProfile.user_id == user.id
        )
        .first()
    )

    if recruiter_profile:
        company = (
            db.query(Company)
            .filter(
                Company.id
                == recruiter_profile.company_id
            )
            .first()
        )

        return CommunityCommentAuthorResponse(
            user_id=user.id,
            role=role,
            display_name=user.email,
            headline=None,
            designation=(
                recruiter_profile.designation
            ),
            company_name=(
                company.name
                if company
                else None
            ),
            profile_image_blob_path=None,
        )

    return CommunityCommentAuthorResponse(
        user_id=user.id,
        role=role,
        display_name=user.email,
    )


def build_comment_response(
    db: Session,
    comment: CommunityComment,
) -> CommunityCommentResponse:
    return CommunityCommentResponse(
        id=comment.id,
        post_id=comment.post_id,
        user_id=comment.user_id,
        parent_comment_id=(
            comment.parent_comment_id
        ),
        author=get_comment_author(
            db,
            comment.user_id,
        ),
        content=comment.content,
        created_at=comment.created_at,
        updated_at=comment.updated_at,
    )


@router.post(
    "/posts/{post_id}/comments",
    response_model=CommunityCommentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_comment(
    post_id: UUID,
    comment_data: CommunityCommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    content = comment_data.content.strip()

    if not content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Comment content cannot be empty",
        )

    post = (
        db.query(CommunityPost)
        .filter(
            CommunityPost.id == post_id
        )
        .first()
    )

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Community post not found",
        )

    if comment_data.parent_comment_id:
        parent_comment = (
            db.query(CommunityComment)
            .filter(
                CommunityComment.id
                == comment_data.parent_comment_id,
                CommunityComment.post_id
                == post_id,
            )
            .first()
        )

        if not parent_comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(
                    "Parent comment not found for this post"
                ),
            )

    comment = CommunityComment(
        post_id=post_id,
        user_id=current_user.id,
        parent_comment_id=(
            comment_data.parent_comment_id
        ),
        content=content,
    )

    db.add(comment)
    db.commit()
    db.refresh(comment)

    return build_comment_response(
        db,
        comment,
    )


@router.get(
    "/posts/{post_id}/comments",
    response_model=list[CommunityCommentResponse],
)
def get_post_comments(
    post_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    post = (
        db.query(CommunityPost)
        .filter(
            CommunityPost.id == post_id
        )
        .first()
    )

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Community post not found",
        )

    comments = (
        db.query(CommunityComment)
        .filter(
            CommunityComment.post_id == post_id
        )
        .order_by(
            CommunityComment.created_at.asc()
        )
        .all()
    )

    return [
        build_comment_response(
            db,
            comment,
        )
        for comment in comments
    ]


@router.put(
    "/comments/{comment_id}",
    response_model=CommunityCommentResponse,
)
def update_comment(
    comment_id: UUID,
    comment_data: CommunityCommentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    comment = get_comment_or_404(
        db,
        comment_id,
    )

    if comment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only edit your own comments",
        )

    content = comment_data.content.strip()

    if not content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Comment content cannot be empty",
        )

    comment.content = content
    comment.updated_at = datetime.now(
        timezone.utc
    )

    db.commit()
    db.refresh(comment)

    return build_comment_response(
        db,
        comment,
    )


@router.delete(
    "/comments/{comment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_comment(
    comment_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    comment = get_comment_or_404(
        db,
        comment_id,
    )

    if comment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own comments",
        )

    db.delete(comment)
    db.commit()

    return None
