from uuid import UUID

from sqlalchemy import text
from sqlalchemy.orm import Session

from models.agent_memory import AgentMemory
from models.agent_memory_embedding import AgentMemoryEmbedding
from services.embedding_service import generate_embedding


def build_memory_text(
    memory_type: str,
    memory_key: str | None,
    memory_value: dict,
    source: str | None,
) -> str:
    parts = [
        f"Memory type: {memory_type}",
    ]

    if memory_key:
        parts.append(
            f"Memory key: {memory_key}"
        )

    parts.append(
        f"Memory value: {memory_value}"
    )

    if source:
        parts.append(
            f"Source: {source}"
        )

    return "\n".join(parts)


def create_memory(
    db: Session,
    user_id: UUID,
    memory_type: str,
    memory_value: dict,
    memory_key: str | None = None,
    source: str | None = None,
    confidence_score: float | None = None,
) -> AgentMemory:

    memory = AgentMemory(
        user_id=user_id,
        memory_type=memory_type,
        memory_key=memory_key,
        memory_value=memory_value,
        source=source,
        confidence_score=confidence_score,
    )

    db.add(memory)
    db.flush()

    memory_text = build_memory_text(
        memory_type=memory_type,
        memory_key=memory_key,
        memory_value=memory_value,
        source=source,
    )

    embedding_values = generate_embedding(
        memory_text
    )

    embedding = AgentMemoryEmbedding(
        memory_id=memory.id,
        embedding=embedding_values,
    )

    db.add(embedding)
    db.commit()
    db.refresh(memory)

    return memory


def create_or_update_memory(
    db: Session,
    user_id: UUID,
    memory_type: str,
    memory_value: dict,
    memory_key: str | None = None,
    source: str | None = None,
    confidence_score: float | None = None,
) -> AgentMemory:

    existing = (
        db.query(AgentMemory)
        .filter(
            AgentMemory.user_id == user_id,
            AgentMemory.memory_type == memory_type,
            AgentMemory.memory_key == memory_key,
        )
        .first()
    )

    if existing:
        existing.memory_value = memory_value
        existing.source = source
        existing.confidence_score = (
            confidence_score
        )

        memory_text = build_memory_text(
            memory_type=memory_type,
            memory_key=memory_key,
            memory_value=memory_value,
            source=source,
        )

        embedding_values = generate_embedding(
            memory_text
        )

        existing_embedding = (
            db.query(AgentMemoryEmbedding)
            .filter(
                AgentMemoryEmbedding.memory_id
                == existing.id
            )
            .first()
        )

        if existing_embedding:
            existing_embedding.embedding = (
                embedding_values
            )
        else:
            db.add(
                AgentMemoryEmbedding(
                    memory_id=existing.id,
                    embedding=embedding_values,
                )
            )

        db.commit()
        db.refresh(existing)

        return existing

    return create_memory(
        db=db,
        user_id=user_id,
        memory_type=memory_type,
        memory_key=memory_key,
        memory_value=memory_value,
        source=source,
        confidence_score=confidence_score,
    )


def search_user_memories(
    db: Session,
    user_id: UUID,
    query: str,
    limit: int = 5,
) -> list[dict]:

    if not query.strip():
        return []

    query_embedding = generate_embedding(query)

    similarity_query = text(
        """
        SELECT
            am.id,
            am.memory_type,
            am.memory_key,
            am.memory_value,
            am.source,
            am.confidence_score,
            am.created_at,
            1 - (
                ame.embedding <=>
                CAST(:embedding AS vector)
            ) AS similarity
        FROM agent_memory am
        JOIN agent_memory_embeddings ame
            ON ame.memory_id = am.id
        WHERE am.user_id = :user_id
        ORDER BY
            ame.embedding <=>
            CAST(:embedding AS vector)
        LIMIT :limit
        """
    )

    rows = db.execute(
        similarity_query,
        {
            "embedding": str(query_embedding),
            "user_id": str(user_id),
            "limit": limit,
        },
    ).mappings().all()

    return [
        {
            "id": str(row["id"]),
            "memory_type": row["memory_type"],
            "memory_key": row["memory_key"],
            "memory_value": row["memory_value"],
            "source": row["source"],
            "confidence_score": (
                float(row["confidence_score"])
                if row["confidence_score"] is not None
                else None
            ),
            "similarity": float(
                row["similarity"]
            ),
            "created_at": (
                row["created_at"].isoformat()
            ),
        }
        for row in rows
    ]