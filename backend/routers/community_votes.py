from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from dependencies import get_db
from dependencies.auth import get_current_user

from models.community_comments import CommunityComment
from models.community_posts import CommunityPost
from models.user import User
from models.community_votes import (
    CommunityVote,
    VoteType,
)
from schemas.community_vote import (
    CommunityVoteCreate,
    CommunityVoteResponse,
)


router = APIRouter(
    prefix="/community",
    tags=["Community Votes"],
)
ALLOWED_VOTES = {
    VoteType.UP.value,
    VoteType.DOWN.value,
}

# ============================================================
# VOTE ON A POST
#
# If a vote already exists:
#   same vote  -> 409
#   different  -> update existing vote
# ============================================================

@router.post(
    "/posts/{post_id}/vote",
    response_model=CommunityVoteResponse,
)
def vote_on_post(
    post_id: UUID,
    vote_data: CommunityVoteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    vote_value = vote_data.vote.upper()

    if vote_value not in ALLOWED_VOTES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vote must be UP or DOWN",
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

    existing_vote = (
        db.query(CommunityVote)
        .filter(
            CommunityVote.user_id == current_user.id,
            CommunityVote.post_id == post_id,
        )
        .first()
    )

    if existing_vote:
        if existing_vote.vote == vote_value:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="You already have this vote on the post",
            )

        existing_vote.vote = VoteType(vote_value)

        db.commit()
        db.refresh(existing_vote)

        return existing_vote

    vote = CommunityVote(
        user_id=current_user.id,
        post_id=post_id,
        comment_id=None,
        vote=VoteType(vote_value),
    )

    db.add(vote)
    db.commit()
    db.refresh(vote)

    return vote


# ============================================================
# REMOVE VOTE FROM POST
# ============================================================

@router.delete(
    "/posts/{post_id}/vote",
    status_code=status.HTTP_204_NO_CONTENT,
)
def remove_post_vote(
    post_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    vote = (
        db.query(CommunityVote)
        .filter(
            CommunityVote.user_id == current_user.id,
            CommunityVote.post_id == post_id,
        )
        .first()
    )

    if not vote:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="You have not voted on this post",
        )

    db.delete(vote)
    db.commit()

    return None


# ============================================================
# VOTE ON A COMMENT
# ============================================================

@router.post(
    "/comments/{comment_id}/vote",
    response_model=CommunityVoteResponse,
)
def vote_on_comment(
    comment_id: UUID,
    vote_data: CommunityVoteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    vote_value = vote_data.vote.upper()

    if vote_value not in ALLOWED_VOTES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vote must be UP or DOWN",
        )

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

    existing_vote = (
        db.query(CommunityVote)
        .filter(
            CommunityVote.user_id == current_user.id,
            CommunityVote.comment_id == comment_id,
        )
        .first()
    )

    if existing_vote:
        if existing_vote.vote == vote_value:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="You already have this vote on the comment",
            )

        existing_vote.vote = VoteType(vote_value)

        db.commit()
        db.refresh(existing_vote)

        return existing_vote

    vote = CommunityVote(
        user_id=current_user.id,
        post_id=None,
        comment_id=comment_id,
        vote=VoteType(vote_value),
    )

    db.add(vote)
    db.commit()
    db.refresh(vote)

    return vote


# ============================================================
# REMOVE VOTE FROM COMMENT
# ============================================================

@router.delete(
    "/comments/{comment_id}/vote",
    status_code=status.HTTP_204_NO_CONTENT,
)
def remove_comment_vote(
    comment_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    vote = (
        db.query(CommunityVote)
        .filter(
            CommunityVote.user_id == current_user.id,
            CommunityVote.comment_id == comment_id,
        )
        .first()
    )

    if not vote:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="You have not voted on this comment",
        )

    db.delete(vote)
    db.commit()

    return None
