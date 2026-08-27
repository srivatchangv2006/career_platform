from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from dependencies import get_db
from dependencies.auth import get_current_user
from dependencies.roles import require_role
from models.user import User
from schemas.agent_feedback import (
    AgentFeedbackCreate,
    AgentFeedbackResponse,
)
from services.agent_feedback_service import (
    create_feedback,
    get_user_feedback,
)


router = APIRouter(
    prefix="/agent/feedback",
    tags=["Agent Feedback"],
    dependencies=[Depends(require_role("CANDIDATE"))],
)


@router.post(
    "",
    response_model=AgentFeedbackResponse,
    status_code=201,
)
def submit_feedback(
    feedback_data: AgentFeedbackCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return create_feedback(
            db=db,
            user_id=current_user.id,
            interaction_id=(
                feedback_data.interaction_id
            ),
            task_id=feedback_data.task_id,
            rating=feedback_data.rating,
            feedback=feedback_data.feedback,
            is_helpful=feedback_data.is_helpful,
            metadata=feedback_data.metadata,
        )

    except ValueError as exc:
        db.rollback()

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Failed to store agent feedback",
        ) from exc


@router.get(
    "/me",
    response_model=list[AgentFeedbackResponse],
)
def get_my_feedback(
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_user_feedback(
        db=db,
        user_id=current_user.id,
        limit=limit,
    )


@router.get(
    "/{feedback_id}",
    response_model=AgentFeedbackResponse,
)
def get_feedback(
    feedback_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    rows = get_user_feedback(
        db=db,
        user_id=current_user.id,
        limit=100,
    )

    for row in rows:
        if row["id"] == feedback_id:
            return row

    raise HTTPException(
        status_code=404,
        detail="Agent feedback not found",
    )