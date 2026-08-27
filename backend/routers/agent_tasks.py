from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from services.agent_orchestrator import execute_career_analysis
from dependencies import get_db
from dependencies.auth import get_current_user
from dependencies.roles import require_role
from models.agent_task import AgentTask
from models.user import User
from schemas.agent_task import (
    AgentTaskCreate,
    AgentTaskResponse,
)


router = APIRouter(
    prefix="/agent/tasks",
    tags=["Agent Tasks"],
    dependencies=[Depends(require_role("CANDIDATE"))],
)


@router.post(
    "",
    response_model=AgentTaskResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_agent_task(
    task_data: AgentTaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = AgentTask(
        user_id=current_user.id,
        task_type=task_data.task_type,
        status="PENDING",
        input_data=task_data.input_data,
    )

    db.add(task)
    db.commit()
    db.refresh(task)

    return task


@router.get(
    "/me",
    response_model=list[AgentTaskResponse],
)
def get_my_agent_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return (
        db.query(AgentTask)
        .filter(
            AgentTask.user_id == current_user.id
        )
        .order_by(
            AgentTask.created_at.desc()
        )
        .all()
    )


@router.get(
    "/{task_id}",
    response_model=AgentTaskResponse,
)
def get_agent_task(
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

    return task


@router.post(
    "/{task_id}/start",
    response_model=AgentTaskResponse,
)
def start_agent_task(
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

    if task.status != "PENDING":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Only pending tasks can be started",
        )

    task.status = "RUNNING"
    task.started_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(task)

    return task

@router.post(
    "/{task_id}/execute",
    response_model=AgentTaskResponse,
)
def execute_agent_task(
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

    if task.status not in {"PENDING", "RUNNING"}:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Task cannot be executed in its current state",
        )

    if task.task_type != "CAREER_ANALYSIS":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported task type",
        )

    try:
        return execute_career_analysis(
            db=db,
            task=task,
        )

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Agent task execution failed",
        ) from exc