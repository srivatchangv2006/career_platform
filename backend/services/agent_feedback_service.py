from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import insert, select
from sqlalchemy.orm import Session

from models.agent_feedback import AgentFeedback
from models.agent_task import AgentTask
from models.ai_interaction import AIInteraction
from services.memory_service import create_memory


def create_feedback(
    db: Session,
    user_id: UUID,
    interaction_id: UUID | None = None,
    task_id: UUID | None = None,
    rating: int | None = None,
    feedback: str | None = None,
    is_helpful: bool | None = None,
    metadata: dict[str, Any] | None = None,
) -> dict:

    # -----------------------------------------
    # Validate rating
    # -----------------------------------------

    if rating is not None and (
        rating < 1 or rating > 5
    ):
        raise ValueError(
            "Rating must be between 1 and 5"
        )

    # -----------------------------------------
    # Verify interaction belongs to user
    # -----------------------------------------

    if interaction_id is not None:

        interaction_exists = db.execute(
            select(AIInteraction.__table__.c.id)
            .where(
                AIInteraction.__table__.c.id
                == interaction_id
            )
            .where(
                AIInteraction.__table__.c.user_id
                == user_id
            )
        ).first()

        if not interaction_exists:
            raise ValueError(
                "AI interaction not found"
            )

    # -----------------------------------------
    # Verify task belongs to user
    # -----------------------------------------

    if task_id is not None:

        task_exists = db.execute(
            select(AgentTask.__table__.c.id)
            .where(
                AgentTask.__table__.c.id
                == task_id
            )
            .where(
                AgentTask.__table__.c.user_id
                == user_id
            )
        ).first()

        if not task_exists:
            raise ValueError(
                "Agent task not found"
            )

    # -----------------------------------------
    # Create feedback row
    # -----------------------------------------

    feedback_id = uuid4()

    values = {
        "id": feedback_id,
        "user_id": user_id,
        "interaction_id": interaction_id,
        "task_id": task_id,
        "rating": rating,
        "feedback": feedback,
        "is_helpful": is_helpful,
        "metadata": metadata or {},
    }

    statement = insert(
        AgentFeedback.__table__
    ).values(**values)

    db.execute(statement)
    db.commit()

    # -----------------------------------------
    # Store feedback in agent memory
    # -----------------------------------------

    memory_value = {
        "feedback_id": str(feedback_id),
        "interaction_id": (
            str(interaction_id)
            if interaction_id
            else None
        ),
        "task_id": (
            str(task_id)
            if task_id
            else None
        ),
        "rating": rating,
        "feedback": feedback,
        "is_helpful": is_helpful,
        "metadata": metadata or {},
    }

    # Use rating to estimate confidence.
    if rating is not None:
        confidence = float(
            rating / 5 * 100
        )
    elif is_helpful is not None:
        confidence = 100.0 if is_helpful else 30.0
    else:
        confidence = 70.0

    try:
        create_memory(
            db=db,
            user_id=user_id,
            memory_type="AGENT_FEEDBACK",
            memory_key=f"feedback_{feedback_id}",
            memory_value=memory_value,
            source="agent_feedback",
            confidence_score=confidence,
        )

    except Exception:
        # Feedback itself should remain useful even if
        # memory/embedding generation fails.
        db.rollback()

    # -----------------------------------------
    # Return stored feedback
    # -----------------------------------------

    row = db.execute(
        select(
            AgentFeedback.__table__.c.id,
            AgentFeedback.__table__.c.user_id,
            AgentFeedback.__table__.c.interaction_id,
            AgentFeedback.__table__.c.task_id,
            AgentFeedback.__table__.c.rating,
            AgentFeedback.__table__.c.feedback,
            AgentFeedback.__table__.c.is_helpful,
            AgentFeedback.__table__.c["metadata"],
            AgentFeedback.__table__.c.created_at,
        )
        .where(
            AgentFeedback.__table__.c.id
            == feedback_id
        )
    ).mappings().first()

    if not row:
        raise RuntimeError(
            "Feedback was stored but could not be retrieved"
        )

    return dict(row)


def get_user_feedback(
    db: Session,
    user_id: UUID,
    limit: int = 50,
) -> list[dict]:

    if limit < 1:
        limit = 1

    if limit > 100:
        limit = 100

    statement = (
        select(
            AgentFeedback.__table__.c.id,
            AgentFeedback.__table__.c.user_id,
            AgentFeedback.__table__.c.interaction_id,
            AgentFeedback.__table__.c.task_id,
            AgentFeedback.__table__.c.rating,
            AgentFeedback.__table__.c.feedback,
            AgentFeedback.__table__.c.is_helpful,
            AgentFeedback.__table__.c["metadata"],
            AgentFeedback.__table__.c.created_at,
        )
        .where(
            AgentFeedback.__table__.c.user_id
            == user_id
        )
        .order_by(
            AgentFeedback.__table__.c.created_at.desc()
        )
        .limit(limit)
    )

    rows = db.execute(
        statement
    ).mappings().all()

    return [dict(row) for row in rows]