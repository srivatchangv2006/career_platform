from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from dependencies import get_db
from dependencies.auth import get_current_user
from models.agent_task import AgentTask
from models.agent_task_step import AgentTaskStep
from models.user import User
from schemas.agent_task_step import (
    AgentTaskStepCreate,
    AgentTaskStepResponse,
    AgentTaskStepUpdate,
)

router = APIRouter(
    prefix="/agent/tasks",
    tags=["Agent Task Steps"],
)


@router.post(
    "/{task_id}/steps",
    response_model=AgentTaskStepResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_task_step(
    task_id: UUID,
    step_data: AgentTaskStepCreate,
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

    step = AgentTaskStep(
        task_id=task_id,
        **step_data.model_dump(),
    )

    db.add(step)
    db.commit()
    db.refresh(step)

    return step


@router.get(
    "/{task_id}/steps",
    response_model=list[AgentTaskStepResponse],
)
def get_task_steps(
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
        db.query(AgentTaskStep)
        .filter(
            AgentTaskStep.task_id == task_id
        )
        .order_by(
            AgentTaskStep.step_order.asc()
        )
        .all()
    )


@router.put(
    "/{task_id}/steps/{step_id}",
    response_model=AgentTaskStepResponse,
)
def update_task_step(
    task_id: UUID,
    step_id: UUID,
    step_data: AgentTaskStepUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    step = (
        db.query(AgentTaskStep)
        .join(
            AgentTask,
            AgentTask.id == AgentTaskStep.task_id,
        )
        .filter(
            AgentTaskStep.id == step_id,
            AgentTaskStep.task_id == task_id,
            AgentTask.user_id == current_user.id,
        )
        .first()
    )

    if not step:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent task step not found",
        )

    update_data = step_data.model_dump(
        exclude_unset=True
    )

    for field, value in update_data.items():
        setattr(step, field, value)

    if step.status == "RUNNING" and step.started_at is None:
        step.started_at = datetime.now(timezone.utc)

    if step.status in {"COMPLETED", "FAILED"}:
        step.completed_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(step)

    return step