from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from dependencies import get_db
from dependencies.auth import get_current_user
from dependencies.roles import require_role
from models.user import User
from schemas.ai_interaction import (
    AIInteractionCreate,
    AIInteractionResponse,
)
from services.ai_interaction_service import (
    get_user_ai_interactions,
    log_ai_interaction,
)


router = APIRouter(
    prefix="/ai/interactions",
    tags=["AI Interactions"],
    dependencies=[Depends(require_role("CANDIDATE"))],
)


@router.post(
    "",
    response_model=AIInteractionResponse,
    status_code=201,
)
def create_ai_interaction(
    interaction_data: AIInteractionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        interaction_id = log_ai_interaction(
            db=db,
            user_id=current_user.id,
            interaction_type=(
                interaction_data.interaction_type
            ),
            input_text=interaction_data.input_text,
            output_text=interaction_data.output_text,
            model_name=interaction_data.model_name,
            metadata=interaction_data.metadata,
        )

    except Exception as exc:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Failed to store AI interaction",
        ) from exc

    interactions = get_user_ai_interactions(
        db=db,
        user_id=current_user.id,
        limit=100,
    )

    for interaction in interactions:
        if interaction["id"] == interaction_id:
            return interaction

    raise HTTPException(
        status_code=500,
        detail="AI interaction was stored but could not be retrieved",
    )


@router.get(
    "/me",
    response_model=list[AIInteractionResponse],
)
def get_my_ai_interactions(
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_user_ai_interactions(
        db=db,
        user_id=current_user.id,
        limit=limit,
    )