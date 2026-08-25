from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.orm import Session

from models.agent_message import AgentMessage
from models.agent_task import AgentTask
from models.agent_task_step import AgentTaskStep

from services.agents import (
    run_job_recommendation_agent,
    run_resume_agent,
    run_skill_gap_agent,
)


def create_agent_message(
    db: Session,
    task_id: UUID,
    sender_agent: str,
    receiver_agent: str,
    message_type: str,
    payload: dict,
):
    message = AgentMessage(
        task_id=task_id,
        sender_agent=sender_agent,
        receiver_agent=receiver_agent,
        message_type=message_type,
        payload=payload,
        status="PENDING",
    )

    db.add(message)
    db.commit()
    db.refresh(message)

    return message


def execute_career_analysis(
    db: Session,
    task: AgentTask,
) -> AgentTask:

    task.status = "RUNNING"
    task.started_at = datetime.now(timezone.utc)

    db.commit()

    steps = (
        db.query(AgentTaskStep)
        .filter(
            AgentTaskStep.task_id == task.id
        )
        .order_by(
            AgentTaskStep.step_order.asc()
        )
        .all()
    )

    results = []

    try:

        previous_result = None

        for step in steps:

            step.status = "RUNNING"
            step.started_at = datetime.now(timezone.utc)

            db.commit()

            result = execute_step(
                db=db,
                task=task,
                step=step,
            )

            step.output_data = result
            step.status = "COMPLETED"
            step.completed_at = datetime.now(timezone.utc)

            results.append(
                {
                    "step_id": str(step.id),
                    "step_name": step.step_name,
                    "agent_name": step.agent_name,
                    "result": result,
                }
            )

            db.commit()

            # ------------------------------------------
            # Send result to the next agent
            # ------------------------------------------

            next_step = (
                db.query(AgentTaskStep)
                .filter(
                    AgentTaskStep.task_id == task.id,
                    AgentTaskStep.step_order
                    == step.step_order + 1,
                )
                .first()
            )

            if next_step:

                create_agent_message(
                    db=db,
                    task_id=task.id,
                    sender_agent=step.agent_name
                    or "unknown_agent",
                    receiver_agent=next_step.agent_name
                    or "unknown_agent",
                    message_type=(
                        f"{step.agent_name.upper()}_COMPLETED"
                    ),
                    payload={
                        "step_id": str(step.id),
                        "step_name": step.step_name,
                        "result": result,
                    },
                )

            previous_result = result

        task.status = "COMPLETED"

        task.output_data = {
            "steps": results,
            "final_result": previous_result,
        }

        task.completed_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(task)

        return task

    except Exception as exc:

        db.rollback()

        task.status = "FAILED"
        task.error_message = str(exc)
        task.completed_at = datetime.now(timezone.utc)

        db.add(task)
        db.commit()

        raise


def execute_step(
    db: Session,
    task: AgentTask,
    step: AgentTaskStep,
) -> dict:

    # ------------------------------------------
    # Resume Agent
    # ------------------------------------------

    if step.agent_name == "resume_agent":

        resume_id = (
            step.input_data.get("resume_id")
            if step.input_data
            else None
        )

        if not resume_id:
            raise ValueError(
                "resume_id is required for resume_agent"
            )

        return run_resume_agent(
            db=db,
            user_id=task.user_id,
            resume_id=UUID(str(resume_id)),
        )

    # ------------------------------------------
    # Skill Gap Agent
    # ------------------------------------------

    if step.agent_name == "skill_gap_agent":

        job_id = (
            step.input_data.get("job_id")
            if step.input_data
            else None
        )

        if not job_id:
            raise ValueError(
                "job_id is required for skill_gap_agent"
            )

        return run_skill_gap_agent(
            db=db,
            user_id=task.user_id,
            job_id=UUID(str(job_id)),
        )

    # ------------------------------------------
    # Job Recommendation Agent
    # ------------------------------------------

    if step.agent_name == "job_recommendation_agent":

        return run_job_recommendation_agent(
            db=db,
            user_id=task.user_id,
        )

    return {
        "agent": step.agent_name,
        "status": "SKIPPED",
        "message": (
            "No implementation registered "
            "for this agent."
        ),
    }