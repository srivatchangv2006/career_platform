from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from dependencies import get_db
from dependencies.auth import get_current_user

from models.community_comments import CommunityComment
from models.community_posts import CommunityPost
from models.user import User

from schemas.community_comment import (
    CommunityCommentCreate,
    CommunityCommentResponse,
    CommunityCommentUpdate,
)


router = APIRouter(
    prefix="/community",
    tags=["Community Comments"],
)


# ============================================================
# CREATE COMMENT / REPLY
# ============================================================

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

    # --------------------------------------------------------
    # Verify post exists.
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # If this is a reply, verify the parent comment exists
    # AND belongs to the same post.
    # --------------------------------------------------------

    if comment_data.parent_comment_id is not None:
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

    # --------------------------------------------------------
    # Create comment/reply.
    # --------------------------------------------------------

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

    return comment


# ============================================================
# GET COMMENTS FOR A POST
# ============================================================

@router.get(
    "/posts/{post_id}/comments",
    response_model=list[CommunityCommentResponse],
)
def get_post_comments(
    post_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # --------------------------------------------------------
    # Verify post exists.
    # --------------------------------------------------------

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

    return (
        db.query(CommunityComment)
        .filter(
            CommunityComment.post_id == post_id
        )
        .order_by(
            CommunityComment.created_at.asc()
        )
        .all()
    )


# ============================================================
# UPDATE OWN COMMENT
# ============================================================

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

    return comment


# ============================================================
# DELETE OWN COMMENT
# ============================================================

@router.delete(
    "/comments/{comment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_comment(
    comment_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
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

    if comment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own comments",
        )

    db.delete(comment)
    db.commit()

    return None
