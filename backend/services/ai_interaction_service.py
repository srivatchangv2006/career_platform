from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import insert, select
from sqlalchemy.orm import Session

from models.ai_interaction import AIInteraction


def log_ai_interaction(
    db: Session,
    user_id: UUID,
    interaction_type: str,
    input_text: str | None = None,
    output_text: str | None = None,
    model_name: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> UUID:
    """
    Store an AI interaction in the ai_interactions table.

    Uses SQLAlchemy Core so the PostgreSQL column named
    `metadata` does not conflict with SQLAlchemy's
    Declarative `metadata` attribute.
    """

    interaction_id = uuid4()

    values = {
        "id": interaction_id,
        "user_id": user_id,
        "interaction_type": interaction_type,
        "input_text": input_text,
        "output_text": output_text,
        "model_name": model_name,
        "metadata": metadata or {},
    }

    statement = insert(
        AIInteraction.__table__
    ).values(**values)

    db.execute(statement)
    db.commit()

    return interaction_id


def get_user_ai_interactions(
    db: Session,
    user_id: UUID,
    limit: int = 50,
) -> list[dict]:
    """
    Return recent AI interactions for a user.
    """

    if limit < 1:
        limit = 1

    if limit > 100:
        limit = 100

    statement = (
        select(
            AIInteraction.__table__.c.id,
            AIInteraction.__table__.c.user_id,
            AIInteraction.__table__.c.interaction_type,
            AIInteraction.__table__.c.input_text,
            AIInteraction.__table__.c.output_text,
            AIInteraction.__table__.c.model_name,
            AIInteraction.__table__.c["metadata"],
            AIInteraction.__table__.c.created_at,
        )
        .where(
            AIInteraction.__table__.c.user_id == user_id
        )
        .order_by(
            AIInteraction.__table__.c.created_at.desc()
        )
        .limit(limit)
    )

    rows = db.execute(statement).mappings().all()

    return [
        {
            "id": row["id"],
            "user_id": row["user_id"],
            "interaction_type": row[
                "interaction_type"
            ],
            "input_text": row["input_text"],
            "output_text": row["output_text"],
            "model_name": row["model_name"],
            "metadata": row["metadata"],
            "created_at": row["created_at"],
        }
        for row in rows
    ]