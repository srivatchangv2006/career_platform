from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from dependencies import get_db
from dependencies.auth import get_current_user
from dependencies.roles import require_role
from models.agent_message import AgentMessage
from models.agent_task import AgentTask
from models.user import User
from schemas.agent_message import (
    AgentMessageCreate,
    AgentMessageResponse,
)


router = APIRouter(
    prefix="/agent/messages",
    tags=["Agent Messages"],
    dependencies=[Depends(require_role("CANDIDATE"))],
)


@router.post(
    "",
    response_model=AgentMessageResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_agent_message(
    message_data: AgentMessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if message_data.task_id:
        task = (
            db.query(AgentTask)
            .filter(
                AgentTask.id == message_data.task_id,
                AgentTask.user_id == current_user.id,
            )
            .first()
        )

        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Agent task not found",
            )

    message = AgentMessage(
        **message_data.model_dump()
    )

    db.add(message)
    db.commit()
    db.refresh(message)

    return message


@router.get(
    "/task/{task_id}",
    response_model=list[AgentMessageResponse],
)
def get_task_messages(
    task_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = (
        db.query(AgentTask)
        .filter(
            AgentTask.id == task_id,
            AgentTask.user_id == current_user.id,
        )
        .first()
    )

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent task not found",
        )

    return (
        db.query(AgentMessage)
        .filter(
            AgentMessage.task_id == task_id
        )
        .order_by(
            AgentMessage.created_at.asc()
        )
        .all()
    )


@router.post(
    "/{message_id}/process",
    response_model=AgentMessageResponse,
)
def process_agent_message(
    message_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    message = (
        db.query(AgentMessage)
        .join(
            AgentTask,
            AgentTask.id == AgentMessage.task_id,
        )
        .filter(
            AgentMessage.id == message_id,
            AgentTask.user_id == current_user.id,
        )
        .first()
    )

    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent message not found",
        )

    if message.status == "PROCESSED":
        return message

    message.status = "PROCESSED"
    message.processed_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(message)

    return message