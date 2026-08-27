from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from dependencies import get_db
from dependencies.auth import get_current_user
from dependencies.roles import require_role
from models.agent_memory import AgentMemory
from models.agent_memory_embedding import AgentMemoryEmbedding
from models.user import User
from schemas.agent_memory import (
    AgentMemoryCreate,
    AgentMemoryResponse,
    AgentMemorySearchResult,
    AgentMemoryUpdate,
)
from services.embedding_service import generate_embedding


router = APIRouter(
    prefix="/agent/memory",
    tags=["Agent Memory"],
    dependencies=[Depends(require_role("CANDIDATE"))],
)


def build_memory_text(memory: AgentMemory) -> str:
    parts = [
        f"Memory type: {memory.memory_type}",
    ]

    if memory.memory_key:
        parts.append(
            f"Memory key: {memory.memory_key}"
        )

    parts.append(
        f"Memory value: {memory.memory_value}"
    )

    if memory.source:
        parts.append(
            f"Source: {memory.source}"
        )

    return "\n".join(parts)


@router.post(
    "",
    response_model=AgentMemoryResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_memory(
    memory_data: AgentMemoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    memory = AgentMemory(
        user_id=current_user.id,
        **memory_data.model_dump(),
    )

    db.add(memory)
    db.flush()

    memory_text = build_memory_text(memory)

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


@router.get(
    "",
    response_model=list[AgentMemoryResponse],
)
def get_my_memories(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return (
        db.query(AgentMemory)
        .filter(
            AgentMemory.user_id == current_user.id
        )
        .order_by(
            AgentMemory.created_at.desc()
        )
        .all()
    )


@router.get(
    "/{memory_id}",
    response_model=AgentMemoryResponse,
)
def get_memory(
    memory_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    memory = (
        db.query(AgentMemory)
        .filter(
            AgentMemory.id == memory_id,
            AgentMemory.user_id == current_user.id,
        )
        .first()
    )

    if not memory:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Memory not found",
        )

    return memory


@router.put(
    "/{memory_id}",
    response_model=AgentMemoryResponse,
)
def update_memory(
    memory_id: UUID,
    memory_data: AgentMemoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    memory = (
        db.query(AgentMemory)
        .filter(
            AgentMemory.id == memory_id,
            AgentMemory.user_id == current_user.id,
        )
        .first()
    )

    if not memory:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Memory not found",
        )

    update_data = memory_data.model_dump(
        exclude_unset=True
    )

    for field, value in update_data.items():
        setattr(memory, field, value)

    # Regenerate embedding because the memory content may have changed.
    embedding_text = build_memory_text(memory)
    embedding_values = generate_embedding(
        embedding_text
    )

    existing_embedding = (
        db.query(AgentMemoryEmbedding)
        .filter(
            AgentMemoryEmbedding.memory_id == memory.id
        )
        .first()
    )

    if existing_embedding:
        existing_embedding.embedding = embedding_values
    else:
        db.add(
            AgentMemoryEmbedding(
                memory_id=memory.id,
                embedding=embedding_values,
            )
        )

    db.commit()
    db.refresh(memory)

    return memory


@router.delete(
    "/{memory_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_memory(
    memory_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    memory = (
        db.query(AgentMemory)
        .filter(
            AgentMemory.id == memory_id,
            AgentMemory.user_id == current_user.id,
        )
        .first()
    )

    if not memory:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Memory not found",
        )

    db.delete(memory)
    db.commit()

    return None

@router.get(
    "/search/query",
    response_model=list[AgentMemorySearchResult],
)
def search_memories(
    q: str,
    limit: int = 5,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not q.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Search query cannot be empty",
        )

    if limit < 1 or limit > 20:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Limit must be between 1 and 20",
        )

    query_embedding = generate_embedding(q)

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
            1 - (ame.embedding <=> CAST(:embedding AS vector)) AS similarity
        FROM agent_memory am
        JOIN agent_memory_embeddings ame
            ON ame.memory_id = am.id
        WHERE am.user_id = :user_id
        ORDER BY ame.embedding <=> CAST(:embedding AS vector)
        LIMIT :limit
        """
    )

    rows = db.execute(
        similarity_query,
        {
            "embedding": str(query_embedding),
            "user_id": str(current_user.id),
            "limit": limit,
        },
    ).mappings().all()

    return [
        AgentMemorySearchResult(
            id=row["id"],
            memory_type=row["memory_type"],
            memory_key=row["memory_key"],
            memory_value=row["memory_value"],
            source=row["source"],
            confidence_score=row["confidence_score"],
            similarity=float(row["similarity"]),
            created_at=row["created_at"],
        )
        for row in rows
    ]