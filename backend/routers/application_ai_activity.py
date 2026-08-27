from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from dependencies import get_db
from dependencies.auth import get_current_user

from models.agent_message import AgentMessage
from models.agent_task import AgentTask
from models.agent_task_step import AgentTaskStep
from models.ai_interaction import AIInteraction
from models.application import Application
from models.interview import Interview
from models.user import User

from schemas.application_ai_activity import (
    AIActivityInteraction,
    AIActivityMessage,
    AIActivityStep,
    AIActivityTask,
    ApplicationAIActivityResponse,
)


router = APIRouter(
    prefix="/applications",
    tags=["Application AI Activity"],
)


def contains_application_id(
    data: dict[str, Any] | None,
    application_id: UUID,
) -> bool:
    if not data:
        return False

    target = str(application_id)

    if str(data.get("application_id")) == target:
        return True

    for value in data.values():
        if isinstance(value, dict):
            if contains_application_id(
                value,
                application_id,
            ):
                return True

        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    if contains_application_id(
                        item,
                        application_id,
                    ):
                        return True

    return False


def task_belongs_to_application(
    task: AgentTask,
    application: Application,
) -> bool:
    application_id = application.id
    job_id = application.job_id

    task_input = task.input_data or {}
    task_output = task.output_data or {}

    # Direct application ID
    if contains_application_id(
        task_input,
        application_id,
    ):
        return True

    if contains_application_id(
        task_output,
        application_id,
    ):
        return True

    # Career-analysis tasks are associated with
    # the application's job.
    if (
        task.task_type == "CAREER_ANALYSIS"
        and str(task_input.get("job_id"))
        == str(job_id)
    ):
        return True

    return False


def interaction_matches_application(
    metadata: dict[str, Any] | None,
    application: Application,
    db: Session,
) -> bool:
    if not metadata:
        return False

    application_id = str(application.id)
    job_id = str(application.job_id)

    # ---------------------------------------------
    # Direct application match
    # ---------------------------------------------

    if str(
        metadata.get("application_id")
    ) == application_id:
        return True

    # ---------------------------------------------
    # Resume match
    # ---------------------------------------------

    resume_id = metadata.get("resume_id")

    if (
        resume_id
        and application.resume_id
        and str(resume_id)
        == str(application.resume_id)
    ):
        return True

    # ---------------------------------------------
    # Job match
    # ---------------------------------------------

    metadata_job_id = metadata.get(
        "job_id"
    )

    if (
        metadata_job_id
        and str(metadata_job_id)
        == job_id
    ):
        return True

    # ---------------------------------------------
    # Interview match
    # ---------------------------------------------

    interview_id = metadata.get(
        "interview_id"
    )

    if interview_id:
        interview = (
            db.query(Interview.id)
            .filter(
                Interview.id == interview_id,
                Interview.application_id
                == application.id,
            )
            .first()
        )

        if interview:
            return True

    return False


@router.get(
    "/{application_id}/ai-activity",
    response_model=ApplicationAIActivityResponse,
)
def get_application_ai_activity(
    application_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # =================================================
    # 1. Verify application ownership
    # =================================================

    application = (
        db.query(Application)
        .filter(
            Application.id == application_id,
            Application.user_id == current_user.id,
        )
        .first()
    )

    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found",
        )

    # =================================================
    # 2. Agent Tasks
    # =================================================

    all_tasks = (
        db.query(AgentTask)
        .filter(
            AgentTask.user_id
            == current_user.id
        )
        .order_by(
            AgentTask.created_at.asc()
        )
        .all()
    )

    matching_tasks = [
        task
        for task in all_tasks
        if task_belongs_to_application(
            task,
            application,
        )
    ]

    task_ids = {
        task.id
        for task in matching_tasks
    }

    # =================================================
    # 3. Agent Task Steps
    # =================================================

    steps = []

    if task_ids:
        steps = (
            db.query(AgentTaskStep)
            .filter(
                AgentTaskStep.task_id.in_(
                    task_ids
                )
            )
            .order_by(
                AgentTaskStep.created_at.asc()
            )
            .all()
        )

    # =================================================
    # 4. Agent Messages
    # =================================================

    messages = []

    if task_ids:
        messages = (
            db.query(AgentMessage)
            .filter(
                AgentMessage.task_id.in_(
                    task_ids
                )
            )
            .order_by(
                AgentMessage.created_at.asc()
            )
            .all()
        )

    # =================================================
    # 5. AI Interactions
    #
    # Read the `metadata` database column directly
    # through SQLAlchemy Core. This avoids the
    # SQLAlchemy Declarative `metadata` name collision.
    # =================================================

    interaction_table = (
        AIInteraction.__table__
    )

    interaction_statement = (
        select(
            interaction_table.c.id,
            interaction_table.c.interaction_type,
            interaction_table.c.model_name,
            interaction_table.c.input_text,
            interaction_table.c.output_text,
            interaction_table.c["metadata"],
            interaction_table.c.created_at,
        )
        .where(
            interaction_table.c.user_id
            == current_user.id
        )
        .order_by(
            interaction_table.c.created_at.asc()
        )
    )

    interaction_rows = (
        db.execute(
            interaction_statement
        )
        .mappings()
        .all()
    )

    matching_interactions = []

    for row in interaction_rows:

        metadata = row["metadata"]

        if not isinstance(
            metadata,
            dict,
        ):
            metadata = {}

        if interaction_matches_application(
            metadata,
            application,
            db,
        ):
            matching_interactions.append(
                {
                    "id": row["id"],
                    "interaction_type": (
                        row["interaction_type"]
                    ),
                    "model_name": (
                        row["model_name"]
                    ),
                    "input_text": (
                        row["input_text"]
                    ),
                    "output_text": (
                        row["output_text"]
                    ),
                    "metadata": metadata,
                    "created_at": (
                        row["created_at"]
                    ),
                }
            )

    # =================================================
    # 6. Build response
    # =================================================

    task_response = [
        AIActivityTask(
            id=task.id,
            task_type=task.task_type,
            status=task.status,
            input_data=task.input_data,
            output_data=task.output_data,
            error_message=task.error_message,
            started_at=task.started_at,
            completed_at=task.completed_at,
            created_at=task.created_at,
        )
        for task in matching_tasks
    ]

    step_response = [
        AIActivityStep(
            id=step.id,
            task_id=step.task_id,
            step_name=step.step_name,
            step_order=step.step_order,
            agent_name=step.agent_name,
            status=step.status,
            input_data=step.input_data,
            output_data=step.output_data,
            error_message=step.error_message,
            started_at=step.started_at,
            completed_at=step.completed_at,
            created_at=step.created_at,
        )
        for step in steps
    ]

    message_response = [
        AIActivityMessage(
            id=message.id,
            task_id=message.task_id,
            sender_agent=message.sender_agent,
            receiver_agent=message.receiver_agent,
            message_type=message.message_type,
            payload=message.payload,
            status=message.status,
            created_at=message.created_at,
            processed_at=message.processed_at,
        )
        for message in messages
    ]

    interaction_response = [
        AIActivityInteraction(
            id=interaction["id"],
            interaction_type=(
                interaction[
                    "interaction_type"
                ]
            ),
            model_name=(
                interaction["model_name"]
            ),
            input_text=(
                interaction["input_text"]
            ),
            output_text=(
                interaction["output_text"]
            ),
            metadata=(
                interaction["metadata"]
            ),
            created_at=(
                interaction["created_at"]
            ),
        )
        for interaction in matching_interactions
    ]

    return ApplicationAIActivityResponse(
        application_id=application_id,
        tasks=task_response,
        steps=step_response,
        messages=message_response,
        interactions=interaction_response,
    )